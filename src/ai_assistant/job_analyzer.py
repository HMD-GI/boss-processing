"""
岗位分析模块

将数据库中查到的岗位完整数据 + 用户关键词组发送给 LLM，
让 LLM 分析哪些岗位最符合用户需求，并给出推荐理由。
"""

import json
from typing import List, Dict, Optional

from src.config import settings


# LLM 系统提示词：岗位分析
JOB_ANALYSIS_PROMPT = """你是一个专业的求职顾问AI助手。用户会提供一批从BOSS直聘采集的岗位数据，以及用户的求职需求关键词。

请根据用户的需求关键词，分析这批岗位数据，筛选出最符合用户要求的岗位，并给出详细的推荐分析。

【输出格式要求】
请用Markdown格式输出，结构如下：

## 岗位推荐分析

### 匹配岗位推荐

针对每个推荐岗位，按以下格式输出：

**第N名：[岗位名称] - [公司名称]**
- 📍 工作地点：[城市] [商区]
- 💰 薪资范围：[薪资描述]
- 📋 经验/学历：[经验要求] / [学历要求]
- 🏢 公司信息：[公司行业] | [公司规模] | [融资阶段]
- 🛠️ 核心技能：[技能标签]
- 🎁 福利待遇：[福利标签]
- 👤 招聘者：[招聘者姓名] - [招聘者职位]（[在线状态]）

**推荐理由：**
[详细分析该岗位为何匹配用户需求，包括技能匹配度、薪资合理性、公司发展前景等]

---

### 总结建议

[对整体匹配情况的总结，给出求职建议]

【分析规则】：
1. 最多推荐5个最匹配的岗位，按匹配度从高到低排序。
2. 如果没有完全匹配的岗位，也要推荐最接近的岗位并说明差异。
3. 推荐理由要具体，结合岗位描述(job_desc)和技能要求(skills)进行分析。
4. 如果用户有薪资要求，分析岗位薪资是否满足。
5. 如果用户有经验/学历要求，分析是否匹配。
6. 如果用户有公司规模要求，分析公司是否符合。
7. 如果岗位数据中没有完全符合用户筛选条件的，也要给出说明。"""


class JobAnalyzer:
    """岗位分析器：将岗位数据发送给LLM进行智能分析"""

    def __init__(self):
        self.api_key = settings.LLM_API_KEY
        self.base_url = settings.LLM_BASE_URL
        self.model = settings.LLM_MODEL

    def analyze(
        self,
        jobs: List[Dict],
        keywords: Dict,
        context_messages: Optional[List[Dict]] = None,
        user_input: str = "",
    ) -> str:
        """
        将岗位数据和关键词发送给LLM进行分析。

        参数:
            jobs: 岗位数据列表（完整数据，含job_desc等）
            keywords: 解析出的关键词组
            context_messages: 上下文消息列表
            user_input: 用户原始输入

        返回:
            LLM 分析结果的 Markdown 文本
        """
        if not self.api_key:
            return self._fallback_analysis(jobs, keywords)

        try:
            from openai import OpenAI
            client = OpenAI(api_key=self.api_key, base_url=self.base_url)

            # 构建用户消息：关键词 + 岗位数据
            user_message = self._build_user_message(jobs, keywords, user_input)

            messages = [{"role": "system", "content": JOB_ANALYSIS_PROMPT}]

            # 加入上下文（最近2轮对话，排除当前消息）
            if context_messages:
                for msg in context_messages[-4:]:
                    role = msg.get("role", "user")
                    content = msg.get("content", "")[:2000]
                    messages.append({"role": role, "content": content})

            messages.append({"role": "user", "content": user_message})

            response = client.chat.completions.create(
                model=self.model,
                messages=messages,
                max_tokens=4096,
                temperature=0.7,
                stream=True,
            )

            # 流式输出
            result_text = ""
            for chunk in response:
                if chunk.choices and chunk.choices[0].delta.content:
                    result_text += chunk.choices[0].delta.content

            if not result_text.strip():
                raise ValueError("LLM 返回空内容")

            return result_text

        except Exception as e:
            print(f"[JobAnalyzer] LLM analysis failed: {e}")
            return self._fallback_analysis(jobs, keywords)

    def analyze_stream(
        self,
        jobs: List[Dict],
        keywords: Dict,
        context_messages: Optional[List[Dict]] = None,
        user_input: str = "",
    ):
        """
        流式分析岗位数据，逐块生成结果。

        Yields:
            str: 每次生成的文本片段
        """
        if not self.api_key:
            yield self._fallback_analysis(jobs, keywords)
            return

        try:
            from openai import OpenAI
            client = OpenAI(api_key=self.api_key, base_url=self.base_url)

            user_message = self._build_user_message(jobs, keywords, user_input)

            messages = [{"role": "system", "content": JOB_ANALYSIS_PROMPT}]

            if context_messages:
                for msg in context_messages[-4:]:
                    role = msg.get("role", "user")
                    content = msg.get("content", "")[:2000]
                    messages.append({"role": role, "content": content})

            messages.append({"role": "user", "content": user_message})

            response = client.chat.completions.create(
                model=self.model,
                messages=messages,
                max_tokens=4096,
                temperature=0.7,
                stream=True,
            )

            for chunk in response:
                if chunk.choices and chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content

        except Exception as e:
            print(f"[JobAnalyzer] LLM stream failed: {e}")
            yield f"\n\n⚠️ 分析过程中出现错误: {e}"
            yield self._fallback_analysis(jobs, keywords)

    def _build_user_message(
        self, jobs: List[Dict], keywords: Dict, user_input: str
    ) -> str:
        """构建发送给LLM的用户消息。"""
        # 关键词描述
        kw_lines = []
        kw_lines.append(f"用户原始需求：{user_input}")
        kw_lines.append(f"搜索关键词：{keywords.get('keyword', '')}")
        if keywords.get("city"):
            kw_lines.append(f"城市：{keywords['city']}")
        if keywords.get("experience"):
            kw_lines.append(f"经验要求：{keywords['experience']}")
        if keywords.get("degree"):
            kw_lines.append(f"学历要求：{keywords['degree']}")
        if keywords.get("salary"):
            kw_lines.append(f"薪资要求：{keywords['salary']}")
        if keywords.get("scale"):
            kw_lines.append(f"公司规模要求：{keywords['scale']}")

        kw_text = "\n".join(kw_lines)

        # 岗位数据（精简，避免超出token限制）
        job_summaries = []
        for i, job in enumerate(jobs[:50], 1):  # 最多50条
            summary = {
                "序号": i,
                "岗位名称": job.get("job_name", ""),
                "公司名称": job.get("company_name", ""),
                "薪资": job.get("salary_desc", ""),
                "城市": job.get("city", ""),
                "商区": job.get("area", ""),
                "经验要求": job.get("experience", ""),
                "学历要求": job.get("education", ""),
                "公司行业": job.get("company_industry", ""),
                "公司规模": job.get("company_scale", ""),
                "融资阶段": job.get("company_stage", ""),
                "技能标签": job.get("skills", []),
                "福利标签": job.get("welfare", []),
                "招聘者": job.get("boss_name", ""),
                "招聘者职位": job.get("boss_title", ""),
                "在线状态": job.get("boss_active_status", ""),
                "职位描述": (job.get("job_desc", "") or "")[:500],
            }
            job_summaries.append(summary)

        jobs_json = json.dumps(job_summaries, ensure_ascii=False, indent=2)

        return f"""{kw_text}

以下是数据库中匹配到的 {len(jobs)} 条岗位数据：

{jobs_json}

请根据用户需求分析并推荐最合适的岗位。"""

    def _fallback_analysis(self, jobs: List[Dict], keywords: Dict) -> str:
        """LLM不可用时的简单分析（基于规则的匹配排序）。"""
        if not jobs:
            return "## 岗位推荐分析\n\n未找到匹配的岗位数据。请尝试调整搜索条件。"

        lines = ["## 岗位推荐分析\n"]
        lines.append(f"共找到 {len(jobs)} 条岗位数据。\n")

        kw = keywords.get("keyword", "")
        lines.append(f"### 匹配岗位推荐\n")

        for i, job in enumerate(jobs[:10], 1):
            lines.append(f"**第{i}名：{job.get('job_name', '')} - {job.get('company_name', '')}**")
            lines.append(f"- 📍 工作地点：{job.get('city', '')} {job.get('area', '')}")
            lines.append(f"- 💰 薪资范围：{job.get('salary_desc', '')}")
            lines.append(f"- 📋 经验/学历：{job.get('experience', '')} / {job.get('education', '')}")
            lines.append(f"- 🏢 公司信息：{job.get('company_industry', '')} | {job.get('company_scale', '')}")
            lines.append(f"- 🛠️ 核心技能：{', '.join(job.get('skills', []) or [])}")
            lines.append("")

        lines.append("### 总结建议\n")
        lines.append(f"以上岗位均包含关键词「{kw}」，建议根据个人情况进一步筛选。")
        return "\n".join(lines)
