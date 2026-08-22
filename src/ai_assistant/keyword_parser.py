"""
关键词解析模块

将用户的自然语言需求解析为结构化关键词组，
与爬虫的筛选参数（keyword, city, scale, salary, experience, degree）对齐。

BOSS直聘爬虫支持的筛选条件（对应 api_fetcher.py 中的 filters）：
- scale:      公司规模 (如 "100-499人")
- salary:     薪资范围 (如 "406" 表示 15-30K)
- experience: 经验要求 (如 "3" 表示 3-5年)
- degree:     学历要求 (如 "4" 表示本科)

同时也支持 BOSS直聘 API 的筛选值映射。
"""

import json
import os
from typing import Dict, Optional

from src.config import settings


# BOSS直聘筛选条件编码映射表
# 来源：BOSS直聘搜索页面的 URL 参数编码
BOSS_FILTER_MAP = {
    # 经验要求 experience
    "experience": {
        "应届毕业生": "1",
        "1年以内": "2",
        "1-3年": "3",
        "3-5年": "4",
        "5-10年": "5",
        "10年以上": "6",
        "不限": "",
    },
    # 学历要求 degree
    "degree": {
        "初中及以下": "1",
        "中专/中技": "2",
        "高中": "3",
        "大专": "4",
        "本科": "5",
        "硕士": "6",
        "博士": "7",
        "不限": "",
    },
    # 公司规模 scale
    "scale": {
        "0-20人": "1",
        "20-99人": "2",
        "100-499人": "3",
        "500-999人": "4",
        "1000-9999人": "5",
        "10000人以上": "6",
        "不限": "",
    },
    # 薪资范围 salary（BOSS编码）
    "salary": {
        "3K以下": "401",
        "3-5K": "402",
        "5-10K": "403",
        "10-15K": "404",
        "15-20K": "405",
        "20-30K": "406",
        "30-50K": "407",
        "50K以上": "408",
        "不限": "",
    },
}


# 反向映射：编码 -> 中文描述
def _build_reverse_map():
    reverse = {}
    for category, mapping in BOSS_FILTER_MAP.items():
        reverse[category] = {v: k for k, v in mapping.items() if v}
    return reverse

BOSS_FILTER_REVERSE = _build_reverse_map()


# LLM 系统提示词：解析用户需求为结构化关键词组
KEYWORD_PARSE_PROMPT = """你是一个求职需求解析助手。用户会用自然语言描述求职需求，你需要将其解析为结构化的JSON数据。

请严格按照以下JSON格式输出：

{
  "keyword": "搜索关键词，如 Python开发、AI Agent、前端工程师",
  "city": "城市名（中文），如 上海、北京、深圳。如果用户未指定城市，留空字符串",
  "experience": "经验要求（中文），可选值：应届毕业生/1年以内/1-3年/3-5年/5-10年/10年以上/不限。如果用户未指定，留空字符串",
  "degree": "学历要求（中文），可选值：初中及以下/中专中技/高中/大专/本科/硕士/博士/不限。如果用户未指定，留空字符串",
  "scale": "公司规模（中文），可选值：0-20人/20-99人/100-499人/500-999人/1000-9999人/10000人以上/不限。如果用户未指定，留空字符串",
  "salary": "薪资范围（中文），可选值：3K以下/3-5K/5-10K/10-15K/15-20K/20-30K/30-50K/50K以上/不限。如果用户未指定，留空字符串"
}

【解析规则】：
1. keyword 是用户求职意向的核心搜索词，从用户描述中提取最关键的职业/技术/岗位名称。
2. 所有字段值必须使用上面列出的标准可选值，不要使用其他表述。
3. 如果用户描述中某个维度没有明确要求，对应字段留空字符串""。
4. 只输出JSON，不要包含任何其他文字或解释。

【示例】：
用户输入："我想找上海的Python开发岗位，3-5年经验，本科以上学历，薪资20-30K，公司规模500人以上"
输出：
{"keyword":"Python开发","city":"上海","experience":"3-5年","degree":"本科","scale":"500-999人","salary":"20-30K"}

用户输入："帮我看看杭州的前端岗位"
输出：
{"keyword":"前端","city":"杭州","experience":"","degree":"","scale":"","salary":""}"""


class KeywordParser:
    """用户需求关键词解析器"""

    def __init__(self):
        self.api_key = settings.LLM_API_KEY
        self.base_url = settings.LLM_BASE_URL
        self.model = settings.LLM_MODEL

    def parse(self, user_input: str, context_messages: Optional[list] = None) -> Dict:
        """
        解析用户自然语言需求为结构化关键词组。

        参数:
            user_input: 用户的自然语言输入
            context_messages: 上下文消息列表（用于多轮对话修正解析）

        返回:
            {
                "keyword": "Python开发",
                "city": "上海",
                "experience": "3-5年",      # 中文描述
                "degree": "本科",            # 中文描述
                "scale": "500-999人",        # 中文描述
                "salary": "20-30K",          # 中文描述
                # 以下为对应的BOSS API编码
                "filters": {
                    "experience": "4",
                    "degree": "5",
                    "scale": "4",
                    "salary": "406",
                }
            }
        """
        if not self.api_key:
            # 未配置API Key时使用简单正则解析
            return self._parse_with_regex(user_input)

        try:
            from openai import OpenAI
            client = OpenAI(api_key=self.api_key, base_url=self.base_url)

            messages = [{"role": "system", "content": KEYWORD_PARSE_PROMPT}]

            # 加入上下文（最近2轮对话）
            if context_messages:
                for msg in context_messages[-4:]:
                    messages.append({
                        "role": msg.get("role", "user"),
                        "content": msg.get("content", "")[:500],
                    })

            messages.append({"role": "user", "content": f"请解析以下求职需求：\n{user_input}"})

            response = client.chat.completions.create(
                model=self.model,
                messages=messages,
                response_format={"type": "json_object"},
                max_tokens=1024,
                temperature=0.1,
            )

            content = response.choices[0].message.content
            if not content or not content.strip():
                raise ValueError("LLM 返回空内容")

            parsed = json.loads(content)
            # 补充BOSS API编码
            parsed = self._enrich_with_codes(parsed)
            return parsed

        except Exception as e:
            print(f"[KeywordParser] LLM parse failed, using regex: {e}")
            return self._parse_with_regex(user_input)

    def _enrich_with_codes(self, parsed: Dict) -> Dict:
        """将中文描述转换为BOSS API编码，补充到 filters 字段。"""
        filters = {}
        for field in ["experience", "degree", "scale", "salary"]:
            value = parsed.get(field, "").strip()
            if value and value in BOSS_FILTER_MAP.get(field, {}):
                code = BOSS_FILTER_MAP[field][value]
                if code:
                    filters[field] = code
        parsed["filters"] = filters
        return parsed

    def _parse_with_regex(self, text: str) -> Dict:
        """正则兜底解析（未配置API Key时使用）。"""
        import re

        result = {
            "keyword": "",
            "city": "",
            "experience": "",
            "degree": "",
            "scale": "",
            "salary": "",
        }

        # 城市匹配
        cities = [
            "北京", "上海", "深圳", "广州", "杭州", "成都", "南京",
            "武汉", "西安", "苏州", "厦门", "长沙", "重庆", "青岛",
            "大连", "宁波", "济南", "天津", "无锡", "温州", "佛山",
            "东莞", "珠海", "中山", "惠州", "嘉兴", "常州", "绍兴",
        ]
        for city in cities:
            if city in text:
                result["city"] = city
                break

        # 经验匹配
        exp_patterns = [
            (r"应届", "应届毕业生"),
            (r"1年以内|一年以内", "1年以内"),
            (r"1-3年|1~3年|一到三年", "1-3年"),
            (r"3-5年|3~5年|三到五年", "3-5年"),
            (r"5-10年|5~10年|五到十年", "5-10年"),
            (r"10年以上|十年以上", "10年以上"),
        ]
        for pattern, value in exp_patterns:
            if re.search(pattern, text):
                result["experience"] = value
                break

        # 学历匹配
        degree_patterns = [
            (r"大专", "大专"),
            (r"本科", "本科"),
            (r"硕士", "硕士"),
            (r"博士", "博士"),
        ]
        for pattern, value in degree_patterns:
            if re.search(pattern, text):
                result["degree"] = value
                break

        # 薪资匹配
        salary_patterns = [
            (r"3K以下|3k以下", "3K以下"),
            (r"3-5K|3~5K", "3-5K"),
            (r"5-10K|5~10K", "5-10K"),
            (r"10-15K|10~15K", "10-15K"),
            (r"15-20K|15~20K", "15-20K"),
            (r"20-30K|20~30K", "20-30K"),
            (r"30-50K|30~50K", "30-50K"),
            (r"50K以上|50k以上", "50K以上"),
        ]
        for pattern, value in salary_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                result["salary"] = value
                break

        # 公司规模匹配
        scale_patterns = [
            (r"20人以下|0-20人", "0-20人"),
            (r"20-99人|20~99人", "20-99人"),
            (r"100-499人|100~499人", "100-499人"),
            (r"500-999人|500~999人|500人以上", "500-999人"),
            (r"1000-9999人|1000~9999人|1000人以上|千人以上", "1000-9999人"),
            (r"10000人以上|万人以上", "10000人以上"),
        ]
        for pattern, value in scale_patterns:
            if re.search(pattern, text):
                result["scale"] = value
                break

        # 关键词提取：去掉已识别的城市/经验/学历等词后的剩余部分
        keyword_text = text
        remove_patterns = [
            r"我想找", r"帮我找", r"看看", r"的", r"岗位", r"工作",
            r"职位", r"经验", r"学历", r"以上", r"以下", r"不限",
            r"薪资", r"公司", r"规模", r"城市",
        ]
        for p in remove_patterns:
            keyword_text = re.sub(p, " ", keyword_text)
        # 去掉已识别的具体值
        for v in list(result.values()):
            if v:
                keyword_text = keyword_text.replace(v, " ")
        # 清理
        words = keyword_text.strip().split()
        if words:
            result["keyword"] = words[0] if words else text.strip()[:20]
        else:
            result["keyword"] = text.strip()[:20]

        # 补充编码
        result = self._enrich_with_codes(result)
        return result

    @staticmethod
    def normalize_filters(parsed: Dict) -> Optional[Dict]:
        """
        从解析结果中提取标准化的 filters 字典（用于爬虫和数据库匹配）。
        只包含非空的筛选条件。
        """
        filters = parsed.get("filters", {})
        if not filters:
            return None
        # 只保留有值的字段
        return {k: v for k, v in filters.items() if v}

    @staticmethod
    def filters_to_dict(filters_json) -> Dict:
        """将 filters_json（可能来自数据库JSON列）转为普通字典。"""
        if not filters_json:
            return {}
        if isinstance(filters_json, dict):
            return filters_json
        if isinstance(filters_json, str):
            try:
                return json.loads(filters_json)
            except (json.JSONDecodeError, TypeError):
                return {}
        return {}

    @staticmethod
    def filters_match(log_filters, target_filters) -> bool:
        """
        比较两组筛选条件是否完全相同（不多不少）。

        参数:
            log_filters: CrawlLog 中的 filters_json
            target_filters: 目标筛选条件字典

        返回:
            True 表示完全相同
        """
        log_dict = KeywordParser.filters_to_dict(log_filters)
        target_dict = KeywordParser.filters_to_dict(target_filters)

        # 完全相同：键集合相同且值相同
        if set(log_dict.keys()) != set(target_dict.keys()):
            return False
        for key in log_dict:
            if str(log_dict[key]) != str(target_dict[key]):
                return False
        return True
