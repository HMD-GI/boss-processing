"""
职位详情页 JD 抓取器

核心功能：
- 进入职位详情页，抓取完整职位描述（JD）
- 带上列表API返回的 securityId / lid 上下文
- 只从"职位描述"区域提取JD，不抓取推荐职位等无关内容
- 检测登录墙，避免保存截断数据

关键设计：
- 优先通过 BOSS 内部 API 获取 JD（最可靠）
- 回退到 DOM 提取：从包含"职位描述"的详情区提取
- 若页面出现"登录查看完整内容"，报错并跳过
"""

import time
import random
from typing import Dict, Optional

from src.config import settings


class JobDetailFetcher:
    """
    职位详情页 JD 抓取器

    通过 CDP 导航到详情页，提取职位描述文本和技能标签。
    """

    def __init__(self, cdp_connector):
        """
        参数:
            cdp_connector: CDPConnector 实例（已连接）
        """
        self.cdp = cdp_connector
        self.log_callback = None  # 日志回调: (message, level) -> None

    def _log(self, message: str, level: str = "info"):
        """输出日志到控制台和回调函数。"""
        print(message)
        if self.log_callback:
            try:
                self.log_callback(message, level)
            except Exception:
                pass

    def fetch_detail(self, job: Dict) -> Optional[Dict]:
        """
        抓取单个职位的完整 JD。

        流程：
        1. 构造详情页URL（带上 securityId / lid 上下文）
        2. 导航到详情页
        3. 等待页面加载
        4. 检测登录墙
        5. 优先通过内部 API 获取 JD，回退到 DOM 提取

        参数:
            job: 职位数据字典，需包含 job_id, security_id, lid

        返回:
            更新后的职位字典（增加了 job_desc 字段），失败返回 None
        """
        job_id = job.get("job_id", "")
        security_id = job.get("security_id", "")
        lid = job.get("lid", "")

        if not job_id:
            return None

        # 构造详情页URL
        detail_url = settings.BOSS_DETAIL_URL_TEMPLATE.format(
            job_id=job_id,
            lid=lid,
            security_id=security_id,
        )

        # 导航到详情页
        self.cdp.navigate(detail_url)

        # 等待页面加载（使用动态等待代替固定延时）
        load_delay = random.uniform(*settings.PAGE_LOAD_DELAY)
        time.sleep(max(load_delay, 2))  # 至少等待2秒

        # 额外等待页面 JS 框架初始化
        try:
            for _ in range(10):
                ready = self.cdp.evaluate(
                    "document.readyState", await_promise=False
                )
                if ready == "complete":
                    break
                time.sleep(0.5)
        except Exception:
            time.sleep(2)

        # 优先方案：通过内部 API 获取 JD（最可靠）
        jd = self._fetch_jd_via_api(job_id, lid, security_id)

        if not jd:
            # 回退方案：从 DOM 提取
            jd = self._extract_jd_from_dom()

        if not jd:
            print(f"  [WARN] Job {job_id}: JD extraction failed (both API and DOM)")
            job["job_desc"] = ""
            return job

        # 提取技能标签
        skills = self._extract_skills_from_dom()

        # 更新职位数据
        job["job_desc"] = jd
        if skills:
            existing = set(job.get("skills", []))
            for s in skills:
                if s and s not in existing:
                    job.setdefault("skills", []).append(s)

        return job

    def _fetch_jd_via_api(self, job_id: str, lid: str, security_id: str) -> str:
        """
        通过 BOSS 内部 API 获取职位详情（含 JD）。

        BOSS直聘详情页内部会调用 /wapi/zpgeek/job/card.json 接口，
        返回包含 postDescription（职位描述）的 JSON 数据。
        """
        js_code = """
            (function() {
                try {
                    var xhr = new XMLHttpRequest();
                    var url = '/wapi/zpgeek/job/card.json?jobId=' + encodeURIComponent(arguments[0]) +
                              '&lid=' + encodeURIComponent(arguments[1]) +
                              '&securityId=' + encodeURIComponent(arguments[2]);
                    xhr.open('GET', url, false);
                    xhr.setRequestHeader('x-requested-with', 'XMLHttpRequest');
                    xhr.send();
                    if (xhr.status !== 200) return '';
                    var data = JSON.parse(xhr.responseText);
                    if (data.code !== 0) return '';
                    var jd = data.zpData?.jobInfo?.postDescription ||
                             data.zpData?.jobCard?.postDescription ||
                             data.zpData?.postDescription ||
                             '';
                    return jd;
                } catch(e) {
                    return '';
                }
            })
        """

        try:
            result = self.cdp.evaluate(
                f"{js_code}({repr(job_id)}, {repr(lid)}, {repr(security_id)})",
                await_promise=False,
            )
            if result and isinstance(result, str) and result.strip():
                # 清理 HTML 标签（API 可能返回带标签的文本）
                return self._strip_html(result).strip()
        except Exception as e:
            print(f"  [DEBUG] API JD fetch error: {e}")

        return ""

    def _extract_jd_from_dom(self) -> str:
        """
        从详情页 DOM 提取职位描述文本。

        尝试多种选择器和文本定位策略。
        """
        js_code = """
            (function() {
                // 检测登录墙
                var bodyText = document.body ? document.body.innerText : '';
                if (bodyText.indexOf('登录查看完整内容') !== -1) {
                    return { error: 'login_wall' };
                }

                var jd = '';

                // 方案1：从 .job-detail-body 提取"职位描述"之后的全部文本
                var bodyEl = document.querySelector('.job-detail-body') ||
                             document.querySelector('.job-detail-box') ||
                             document.querySelector('.job-detail-container') ||
                             document.querySelector('[class*="job-detail"]') ||
                             document.querySelector('.job-sec-text') ||
                             document.querySelector('.text-fold');
                if (bodyEl) {
                    var fullText = bodyEl.innerText;
                    var idx = fullText.indexOf('职位描述');
                    if (idx !== -1) {
                        jd = fullText.substring(idx + 4).trim();
                    } else {
                        // 如果没有"职位描述"标记，直接取全部文本
                        jd = fullText.trim();
                    }
                }

                // 方案2：直接查找 .job-sec-text 或 .job-detail-section 内容
                if (!jd) {
                    var secEl = document.querySelector('.job-sec-text') ||
                                document.querySelector('.job-detail-section') ||
                                document.querySelector('[class*="job-sec"]') ||
                                document.querySelector('[class*="postDescription"]');
                    if (secEl) {
                        jd = secEl.innerText.trim();
                    }
                }

                // 方案3：从整页提取
                if (!jd) {
                    var pageText = document.body ? document.body.innerText : '';
                    var idx2 = pageText.indexOf('职位描述');
                    if (idx2 !== -1) {
                        var after = pageText.substring(idx2 + 4);
                        // 去掉末尾的推荐职位等无关内容
                        var cutKeywords = ['相似职位', '看了该职位的人还看了', '猜你喜欢',
                                           '工作地址', '点击查看地图', 'BOSS直聘',
                                           '去App', '前往App', '与BOSS随时沟通',
                                           '查看更多信息', '活跃状态'];
                        for (var ci = 0; ci < cutKeywords.length; ci++) {
                            var cutIdx = after.indexOf(cutKeywords[ci]);
                            if (cutIdx !== -1) {
                                after = after.substring(0, cutIdx);
                            }
                        }
                        jd = after.trim();
                    }
                }

                return { jd: jd };
            })()
        """

        result = self.cdp.evaluate(js_code, await_promise=False)

        if not result:
            return ""

        if isinstance(result, dict):
            if result.get("error") == "login_wall":
                print(f"  [WARN] Login wall detected, skipping")
                return ""
            return result.get("jd", "")

        return ""

    def _extract_skills_from_dom(self) -> list:
        """从详情页 DOM 提取技能标签。"""
        js_code = """
            (function() {
                var skillTags = [];
                var tagSelectors = '.job-detail-body .tag-list li, ' +
                    '.job-tags .tag-item, .job-keyword-list li, ' +
                    '.job-detail-container .tag-list li, ' +
                    '.job-sec-tags .tag-list li, ' +
                    '[class*="skill"] li, [class*="tag-list"] li';
                document.querySelectorAll(tagSelectors).forEach(function(el) {
                    var text = el.innerText.trim();
                    if (text && text.length < 30) skillTags.push(text);
                });
                return skillTags;
            })()
        """

        try:
            result = self.cdp.evaluate(js_code, await_promise=False)
            if result and isinstance(result, list):
                return result
        except Exception:
            pass

        return []

    @staticmethod
    def _strip_html(text: str) -> str:
        """去除字符串中的 HTML 标签。"""
        import re
        # 替换 <br> 和 <p> 为换行
        text = re.sub(r'<br\s*/?>', '\n', text, flags=re.IGNORECASE)
        text = re.sub(r'</p>', '\n', text, flags=re.IGNORECASE)
        # 去除所有 HTML 标签
        text = re.sub(r'<[^>]+>', '', text)
        # 去除多余空行
        text = re.sub(r'\n{3,}', '\n\n', text)
        return text

    def fetch_details_batch(
        self,
        jobs: list,
        delay_range: Optional[tuple] = None,
    ) -> list:
        """
        批量抓取多个职位的详情页 JD。

        参数:
            jobs: 职位列表
            delay_range: 详情页间延时范围（秒）

        返回:
            更新后的职位列表
        """
        if delay_range is None:
            delay_range = settings.DETAIL_DELAY_RANGE

        total = len(jobs)
        for i, job in enumerate(jobs):
            self._log(f"抓取详情 {i+1}/{total}: {job.get('job_name', '?')}")

            self.fetch_detail(job)

            # 详情页间延时
            if i < total - 1:
                delay = random.uniform(*delay_range)
                time.sleep(delay)

        self._log(f"详情页抓取完成，共 {total} 条")
        return jobs
