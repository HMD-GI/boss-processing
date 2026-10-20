"""
BOSS直聘职位列表采集器

核心功能：
- 通过 CDP 在页面上下文中调用 BOSS内部搜索 API
- 获取明文薪资数据（salaryDesc），绕过字体反爬
- 多页采集，含反爬限流策略
- 数据解析与字段映射

反爬策略：
- 翻页间隔 12~22 秒随机延时
- 每采集 75 条后休眠 30~60 秒
- 单次最多 10 页（300条）上限保护
- API 请求从页面内发起，与正常浏览行为一致
"""

import time
import random
import urllib.parse
from typing import List, Dict, Optional, Generator

from src.config import settings


class JobListFetcher:
    """
    BOSS直聘职位列表采集器

    通过 CDP 在页面 JavaScript 上下文中调用搜索 API，
    获取包含明文薪资的 JSON 数据。
    """

    def __init__(self, cdp_connector):
        """
        参数:
            cdp_connector: CDPConnector 实例（已连接）
        """
        self.cdp = cdp_connector
        self.log_callback = None  # 日志回调函数: (message, level) -> None
        self.auth_required_callback = None  # 登录/验证要求回调: (reason, code) -> bool
        # 返回 True 表示用户已完成登录，可重试；False 表示放弃

    def _log(self, message: str, level: str = "info"):
        """输出日志到控制台和回调函数。"""
        print(message)
        if self.log_callback:
            try:
                self.log_callback(message, level)
            except Exception:
                pass

    def fetch_page(
        self,
        keyword: str,
        city_code: str,
        page: int,
        filters: Optional[Dict[str, str]] = None,
    ) -> Optional[Dict]:
        """
        获取单页职位列表（明文薪资）。

        参数:
            keyword: 搜索关键词，如 "AI Agent"
            city_code: 城市代码，如 "101020100"
            page: 页码，从1开始
            filters: 筛选条件字典（可选），支持的key:
                     scale(公司规模), salary(薪资范围),
                     experience(经验), degree(学历)

        返回:
            API 返回的完整 JSON 数据（dict），失败返回 None
        """
        params = {
            "scene": "1",
            "keyword": keyword,  # BOSS API 使用 keyword 参数（与登录检查一致）
            "query": keyword,  # 兼容旧版参数名，双参数保证标题关键词生效
            "city": city_code,
            "experience": "",
            "payType": "",
            "partTime": "",
            "degree": "",
            "industry": "",
            "scale": "",
            "position": "",
            "jobType": "",
            "salary": "",
            "multiBusinessDistrict": "",
            "multiSubway": "",
            "page": str(page),
            "pageSize": str(settings.PAGE_SIZE),
        }

        # 应用筛选条件
        if filters:
            for key, value in filters.items():
                if key in params:
                    params[key] = value

        query_string = urllib.parse.urlencode(params)

        # 在页面上下文中用 fetch 调用 API（与环境检查一致，已验证可行）
        # 使用异步 fetch + awaitPromise，避免同步 XHR 在新版 Chrome 中的兼容问题
        js_code = (
            "(async function() {\n"
            "    try {\n"
            f"        const resp = await fetch('/wapi/zpgeek/search/joblist.json?{query_string}',\n"
            "            { headers: {'x-requested-with': 'XMLHttpRequest'} }\n"
            "        );\n"
            "        if (resp.status !== 200) {\n"
            "            return { error: 'HTTP ' + resp.status, status: resp.status };\n"
            "        }\n"
            "        const respText = await resp.text();\n"
            "        if (!respText || respText.charAt(0) !== '{') {\n"
            "            return { error: 'Non-JSON response', preview: String(respText).substring(0, 200) };\n"
            "        }\n"
            "        return JSON.parse(respText);\n"
            "    } catch(e) {\n"
            "        return { error: e.message };\n"
            "    }\n"
            "})()"
        )

        result = self.cdp.evaluate(js_code, await_promise=True)

        # 类型安全检查：确保返回的是 dict
        if isinstance(result, str):
            # JSON.parse 可能返回字符串（如 responseText 是 "null" 或纯数字）
            print(f"  [WARN] API returned string instead of dict: {result[:100]}")
            return {"error": f"Unexpected string response: {result[:100]}", "code": -1}

        return result

    def fetch_all(
        self,
        keyword: str,
        city_code: str,
        pages: int = 3,
        filters: Optional[Dict[str, str]] = None,
        delay_range: Optional[tuple] = None,
        batch_size: Optional[int] = None,
        batch_delay_range: Optional[tuple] = None,
    ) -> Generator[List[Dict], None, List[Dict]]:
        """
        多页采集，含反爬限流策略。生成器模式，每页 yield 一次。

        反爬策略：
        - 每次请求间隔 delay_range 秒随机延时（默认 12~22 秒）
        - 每采集 batch_size 条后休眠 batch_delay_range 秒（默认 75条/30~60秒）
        - 单次最多 MAX_PAGES 页（默认10页）上限保护

        参数:
            keyword: 搜索关键词
            city_code: 城市代码
            pages: 采集页数
            filters: 筛选条件
            delay_range: 页间延时范围
            batch_size: 批量休眠阈值
            batch_delay_range: 批量休眠时间范围

        Yields:
            每页采集完成后 yield 当前累计的所有职位列表
        """
        if delay_range is None:
            delay_range = settings.DELAY_RANGE
        if batch_size is None:
            batch_size = settings.BATCH_SIZE
        if batch_delay_range is None:
            batch_delay_range = settings.BATCH_DELAY_RANGE

        all_jobs: List[Dict] = []
        pages = min(pages, settings.MAX_PAGES)  # 上限保护

        for page in range(1, pages + 1):
            self._log(f"  [CRAWL] Page {page}/{pages}...")

            data = self.fetch_page(keyword, city_code, page, filters)

            if not data:
                self._log(f"  [FAIL] Page {page}: no response", "error")
                continue

            # 类型安全检查：确保 data 是 dict
            if not isinstance(data, dict):
                self._log(f"  [FAIL] Page {page}: unexpected response type {type(data).__name__}: {str(data)[:100]}", "error")
                continue

            # 检查是否有错误
            if data.get("error"):
                error_msg = data.get("error", "unknown error")
                self._log(f"  [FAIL] Page {page}: {error_msg}", "error")
                continue

            if data.get("code") != 0:
                error_msg = data.get("message", "unknown error")
                code = data.get("code")
                self._log(f"  [FAIL] Page {page}: {error_msg}", "error")

                # 风控码检测
                if code in settings.RISK_CONTROL_CODES:
                    self._log(f"  [WARN] Risk control triggered (code={code}), stopping.", "warn")
                    # 尝试通知上层需要验证
                    if self.auth_required_callback:
                        retry = self.auth_required_callback(
                            f"触发风控限制 (code={code}: {error_msg})",
                            code,
                        )
                        if retry:
                            # 用户已完成验证，重试当前页
                            self._log(f"  [RETRY] 用户已完成验证，重试 Page {page}...")
                            data = self.fetch_page(keyword, city_code, page, filters)
                            if data and isinstance(data, dict) and data.get("code") == 0:
                                # 重试成功，继续处理当前页数据（不 continue）
                                pass
                            else:
                                continue
                        else:
                            break
                    else:
                        break
                    # 如果走到这里说明重试成功了，继续往下处理数据

                # 检测未登录情况（code 非 0 且非风控码）
                # BOSS 可能返回 message="用户未登录" 或其他登录失效提示
                is_login_issue = (
                    "登录" in error_msg
                    or "login" in error_msg.lower()
                    or code in {-1, -2, 1001, 1002}
                )
                if is_login_issue and self.auth_required_callback:
                    self._log(f"  [WARN] 检测到登录失效 (code={code}: {error_msg})，通知前端...", "warn")
                    retry = self.auth_required_callback(
                        f"登录失效 (code={code}: {error_msg})",
                        code,
                    )
                    if retry:
                        # 用户已完成登录，重试当前页
                        self._log(f"  [RETRY] 用户已完成登录，重试 Page {page}...")
                        data = self.fetch_page(keyword, city_code, page, filters)
                        if data and isinstance(data, dict) and data.get("code") == 0:
                            # 重试成功，继续正常流程
                            pass
                        else:
                            # 重试后仍失败
                            retry_msg = data.get("message", "unknown") if isinstance(data, dict) else "no data"
                            self._log(f"  [FAIL] 重试后仍失败: {retry_msg}", "error")
                            continue
                    else:
                        # 用户放弃登录
                        self._log(f"  [WARN] 用户取消登录，停止采集", "warn")
                        break
                else:
                    # 非登录问题或无回调，原逻辑
                    if code in settings.RISK_CONTROL_CODES:
                        break
                    continue

            job_list = data.get("zpData", {}).get("jobList", [])
            if not job_list:
                # 打印诊断信息：帮助判断是 API 结构变化、参数问题还是真的没有数据
                zp_data = data.get("zpData") or {}
                diag_keys = list(zp_data.keys())[:15] if isinstance(zp_data, dict) else type(zp_data).__name__
                preview = str(data)[:300]
                self._log(f"  [INFO] Page {page}: no more data")
                self._log(
                    f"  [DIAG] zpData keys={diag_keys} | code={data.get('code')} "
                    f"| raw preview={preview}",
                    "warn",
                )
                break

            for job in job_list:
                parsed = self._parse_job(job)
                if parsed:
                    all_jobs.append(parsed)

            self._log(
                f"  [OK] Page {page}: got {len(job_list)} jobs, "
                f"total {len(all_jobs)}"
            )

            # 每页抓完立即 yield（增量写入）
            yield all_jobs

            # 限流：页间随机延时
            if page < pages:
                delay = random.uniform(*delay_range)
                self._log(f"  [WAIT] Sleeping {delay:.1f}s...")
                time.sleep(delay)

                # 批量休眠
                if (
                    len(all_jobs) >= batch_size
                    and len(all_jobs) % batch_size == 0
                ):
                    batch_delay_sec = random.uniform(*batch_delay_range)
                    self._log(
                        f"  [BATCH] {len(all_jobs)} jobs collected, "
                        f"sleeping {batch_delay_sec:.1f}s..."
                    )
                    time.sleep(batch_delay_sec)

        return all_jobs

    @staticmethod
    def _parse_job(raw: Dict) -> Optional[Dict]:
        """
        解析单条职位数据，提取关键字段。

        参数:
            raw: API 返回的原始职位数据

        返回:
            解析后的职位字典
        """
        if not raw:
            return None

        return {
            # 职位信息
            "job_id": raw.get("encryptJobId", ""),
            "job_name": raw.get("jobName", ""),
            "salary_desc": raw.get("salaryDesc", ""),  # 明文薪资
            "city": raw.get("cityName", ""),
            "area": raw.get("businessDistrict", ""),
            "experience": raw.get("jobExperience", ""),
            "education": raw.get("jobDegree", ""),
            # 公司信息
            "company_name": raw.get("brandName", ""),
            "company_industry": raw.get("brandIndustry", ""),
            "company_scale": raw.get("brandScaleName", ""),
            "company_stage": raw.get("brandStageName", ""),
            # 标签
            "welfare": raw.get("jobLabels", []),
            "skills": raw.get("skills", []),
            # BOSS信息
            "boss_name": raw.get("bossName", ""),
            "boss_title": raw.get("bossTitle", ""),
            "boss_active_status": (
                "online" if raw.get("bossOnline") else "offline"
            ),
            # 详情页所需上下文
            "security_id": raw.get("securityId", ""),
            "lid": raw.get("lid", ""),
            # 详情页网址（/job_detail/{jobId}.html 静态SEO格式，无需 lid/securityId）
            "detail_url": (
                settings.BOSS_DETAIL_URL_TEMPLATE.format(
                    job_id=raw.get("encryptJobId", ""),
                )
                if raw.get("encryptJobId") else ""
            ),
            # 采集时间
            "fetch_time": time.strftime("%Y-%m-%d %H:%M:%S"),
        }
