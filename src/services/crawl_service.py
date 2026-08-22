"""
采集服务模块

负责协调爬虫引擎和数据库存储：
- 启动 Chrome CDP 连接
- 调用搜索 API 采集职位列表
- 抓取详情页 JD
- 数据写入数据库（去重：job_id 存在则更新）
- 同时写入文件（JSON/CSV，增量保存）
- 记录采集日志
"""

import time
from typing import List, Dict, Optional
from datetime import datetime

from src.config import settings
from src.crawler.cdp_connector import CDPConnector
from src.crawler.api_fetcher import JobListFetcher
from src.crawler.detail_fetcher import JobDetailFetcher
from src.crawler.anti_detect import check_risk_control
from src.utils.city_codes import get_city_code
from src.utils.file_io import DataWriter


class CrawlService:
    """
    采集服务

    协调爬虫引擎、数据库存储和文件输出。
    可被 CLI 和 API 层调用。
    """

    def __init__(self):
        self.connector: Optional[CDPConnector] = None
        self.writer = DataWriter()
        self.log_callback = None  # 日志回调函数: (message, level) -> None

    def _log(self, message: str, level: str = "info"):
        """输出日志到控制台和回调函数。"""
        print(message)
        if self.log_callback:
            try:
                self.log_callback(message, level)
            except Exception:
                pass

    def setup_chrome(self, login_timeout: Optional[int] = None) -> bool:
        """
        启动 Chrome 并等待登录。

        参数:
            login_timeout: 登录超时秒数

        返回:
            True 表示成功
        """
        self.connector = CDPConnector()
        success = self.connector.setup_chrome(login_timeout)
        if not success:
            return False
        self.connector.close()
        return True

    def check_environment(self) -> Dict:
        """
        环境检查：CDP 可用性、依赖完整性、登录态。

        策略：
        1. 直接用有头模式启动 Chrome（弹出浏览器窗口）
        2. 检查登录态，如果已登录则直接返回成功
        3. 如果未登录，在弹出的浏览器窗口中等待用户手动登录
        4. 登录成功后保持 Chrome 运行和 WebSocket 连接，
           后续 crawl() 直接复用该连接
        5. 不再使用无头模式

        返回:
            检查结果字典。成功时 self.connector 保持已连接状态。
        """
        result = {
            "chrome_cdp": False,
            "websocket": False,
            "login_status": False,
            "errors": [],
        }

        # 1. 检查 websocket-client 依赖
        try:
            import websocket  # noqa: F401
            result["websocket"] = True
        except ImportError:
            result["errors"].append("websocket-client 未安装")
            return result

        # 2. 有头模式启动 Chrome CDP
        # 如果 Chrome 已在运行（如之前已启动），直接连接
        self._log("[CHECK] 正在以有头模式启动 Chrome...")
        try:
            self.connector = CDPConnector()
            # 如果 Chrome 未运行，先启动有头模式进程
            if not self.connector.is_chrome_running():
                self._log("[INFO] Chrome 未运行，正在启动（有头模式）...")
                self.connector.start_chrome(headless=False)
            # 连接到 Chrome（导航到 BOSS直聘）
            self.connector.connect()
            result["chrome_cdp"] = True
        except Exception as e:
            result["errors"].append(f"无法启动 Chrome CDP: {e}")
            return result

        # 3. 注入关闭拦截脚本（反检测脚本已在 connect() 中注入）
        try:
            self.connector._inject_beforeunload_handler()
        except Exception:
            pass

        # 4. 检查登录态
        login_ok = False
        login_error_detail = ""
        try:
            api_result = self.connector.evaluate("""
                (async () => {
                    try {
                        const resp = await fetch(
                            '/wapi/zpgeek/search/joblist.json?keyword=test&page=1',
                            { headers: {'x-requested-with': 'XMLHttpRequest'} }
                        );
                        const data = await resp.json();
                        return { code: data.code, has_jobs: !!(data.zpData?.jobList?.length) };
                    } catch(e) { return { error: e.message }; }
                })()
            """)
            if api_result and isinstance(api_result, dict) and api_result.get("code") == 0:
                result["login_status"] = True
                login_ok = True
                self._log("[OK] 登录态正常")
            else:
                # 所有非成功情况都视为需要重新登录
                if api_result and isinstance(api_result, dict):
                    code = api_result.get("code")
                    if code in settings.RISK_CONTROL_CODES:
                        login_error_detail = f"触发风控限制 (code={code})"
                    elif api_result.get("error"):
                        login_error_detail = f"API 请求失败: {api_result.get('error')}"
                    else:
                        login_error_detail = f"登录态过期 (code={code})"
                elif api_result is None:
                    login_error_detail = "登录检查返回 None，页面可能未正确加载"
                else:
                    login_error_detail = f"登录检查返回异常类型: {type(api_result).__name__} = {str(api_result)[:100]}"
                result["errors"].append(login_error_detail)
        except Exception as e:
            login_error_detail = f"登录检查异常: {e}"
            result["errors"].append(login_error_detail)

        # 5. 登录失败时，在已打开的浏览器窗口中等待用户登录
        if not login_ok:
            self._log(f"[INFO] 登录态失效（{login_error_detail}），请在弹出的 Chrome 窗口中登录 BOSS直聘...")
            try:
                # 在当前已打开的 Chrome 窗口中等待登录
                # 使用 setup_chrome 的轮询逻辑，但复用已有的 Chrome 连接
                from src.config import settings as _settings
                login_timeout = _settings.LOGIN_TIMEOUT
                self._log(f"等待登录完成（超时 {login_timeout} 秒）...")

                start = time.time()
                while time.time() - start < login_timeout:
                    result_check = self.connector.evaluate("""
                        (async () => {
                            try {
                                const resp = await fetch(
                                    '/wapi/zpgeek/search/joblist.json?keyword=test&page=1',
                                    { headers: {'x-requested-with': 'XMLHttpRequest'} }
                                );
                                const data = await resp.json();
                                if (data.code === 0 && data.zpData && data.zpData.jobList) {
                                    return { logged_in: true };
                                }
                                return { logged_in: false, code: data.code };
                            } catch(e) { return { logged_in: false, error: e.message }; }
                        })()
                    """)

                    if result_check and isinstance(result_check, dict) and result_check.get("logged_in"):
                        result["login_status"] = True
                        # 清除之前的错误信息
                        result["errors"] = [
                            e for e in result["errors"]
                            if not e.startswith(login_error_detail)
                        ]
                        self._log("[OK] 登录成功！")
                        login_ok = True
                        break

                    # 检测风控码
                    if result_check and isinstance(result_check, dict) and result_check.get("code") in settings.RISK_CONTROL_CODES:
                        self._log(f"[WARN] 检测到风控限制: {result_check.get('code')}")
                        break

                    time.sleep(5)

                if not login_ok:
                    result["errors"].append("登录超时或失败。请在弹出的浏览器窗口中完成登录后重试。")
            except Exception as e:
                result["errors"].append(f"等待登录失败: {e}")

        # 6. 登录成功后保持 Chrome 运行和 WebSocket 连接
        # 不关闭 Chrome，不关闭 WebSocket，让 crawl() 直接复用
        if result["login_status"]:
            self._log("[OK] 环境检查通过，Chrome 保持运行状态")
        else:
            # 检查失败时关闭 Chrome
            if self.connector:
                self.connector.close()
                self.connector.stop_chrome()
                self.connector = None

        return result

    def crawl(
        self,
        keyword: str,
        city: str,
        pages: int = 3,
        fetch_detail: bool = True,
        filters: Optional[Dict[str, str]] = None,
        output_format: str = "json",
        db_session=None,
        skip_env_check: bool = False,
    ) -> Dict:
        """
        执行采集任务。

        流程：
        0. 自动环境检查（有头模式启动 Chrome，保持连接）
        1. 复用环境检查建立的 Chrome 连接
        2. 调用搜索 API 采集职位列表（多页，含限流）
        3. 每页抓完立即保存到文件和数据库
        4. 可选：抓取详情页 JD
        5. 记录采集日志
        6. 爬取完成后关闭 Chrome

        参数:
            keyword: 搜索关键词
            city: 城市名（中文）
            pages: 采集页数
            fetch_detail: 是否抓取详情页
            filters: 筛选条件
            output_format: 输出格式 json/csv
            db_session: 数据库会话（可选，传入则写入数据库）
            skip_env_check: 是否跳过环境检查（跳过则直接启动 Chrome）

        返回:
            采集结果摘要字典
        """
        city_code = get_city_code(city)
        if not city_code:
            self._log(f"错误：未知城市 '{city}'", "error")
            return {
                "success": False,
                "error": f"Unknown city: {city}",
                "total_jobs": 0,
            }

        # 步骤0: 自动环境检查（有头模式启动 Chrome）
        if not skip_env_check:
            self._log("[CHECK] 正在执行环境检查...")
            env_result = self.check_environment()
            if not env_result.get("login_status"):
                errors = env_result.get("errors", ["未知错误"])
                error_msg = "; ".join(errors)
                self._log(f"[CHECK] 环境检查未通过: {error_msg}", "error")
                return {
                    "success": False,
                    "error": f"环境检查未通过: {error_msg}",
                    "total_jobs": 0,
                    "env_check_failed": True,
                    "env_errors": errors,
                }
            self._log("[CHECK] 环境检查通过，开始爬取...")
            # check_environment 成功后 self.connector 已连接到有头 Chrome
            # 直接复用该连接
        else:
            # skip_env_check=True 时，自行启动 Chrome
            self._log("正在启动 Chrome（有头模式）...")
            try:
                self.connector = CDPConnector()
                if not self.connector.is_chrome_running():
                    self.connector.start_chrome(headless=False)
                self.connector.connect()
                self.connector._inject_beforeunload_handler()
            except Exception as e:
                self._log(f"Chrome 连接失败: {e}", "error")
                return {
                    "success": False,
                    "error": f"Cannot start Chrome CDP: {e}.",
                    "total_jobs": 0,
                }

        self._log("Chrome 连接成功，页面就绪")

        fetcher = JobListFetcher(self.connector)
        # 注入日志回调到列表采集器
        fetcher.log_callback = self.log_callback
        all_jobs: List[Dict] = []

        self._log(f"开始采集：关键词='{keyword}'，城市={city}，页数={pages}")

        # 采集列表
        page_num = 0
        for batch in fetcher.fetch_all(keyword, city_code, pages, filters):
            all_jobs = batch
            page_num += 1
            self._log(f"第 {page_num}/{pages} 页采集完成，累计 {len(all_jobs)} 条")
            # 每页抓完立即保存文件（增量写入）
            self.writer.save_json(all_jobs)

            # 写入数据库
            if db_session:
                self._save_to_db(db_session, all_jobs)

        self._log(f"列表采集完成，共 {len(all_jobs)} 条职位")

        # 详情页抓取
        if fetch_detail and all_jobs:
            self._log(f"开始抓取 {len(all_jobs)} 条职位的详情页 JD...")
            detail_fetcher = JobDetailFetcher(self.connector)
            # 注入日志回调到详情抓取器
            detail_fetcher.log_callback = self.log_callback
            detail_fetcher.fetch_details_batch(all_jobs)
            self._log("详情页 JD 抓取完成")

            # 保存带详情的数据
            self.writer.save_json(all_jobs)
            if db_session:
                self._save_to_db(db_session, all_jobs)

        # CSV 输出
        if output_format == "csv" and all_jobs:
            self.writer.save_csv(all_jobs)

        # 记录日志
        if db_session:
            self._log_crawl(
                db_session, keyword, city, pages,
                len(all_jobs), "success",
                filters=filters,
            )

        # 爬取完成后关闭 Chrome
        self._log("[INFO] 采集完成，正在关闭 Chrome...")
        if self.connector:
            self.connector.close()
            self.connector.stop_chrome()
            self.connector = None

        return {
            "success": True,
            "total_jobs": len(all_jobs),
            "keyword": keyword,
            "city": city,
            "pages": pages,
        }

    @staticmethod
    def _save_to_db(db_session, jobs: List[Dict]) -> None:
        """
        将职位数据写入数据库（去重：job_id 存在则更新）。
        只写入 Job 模型中定义的字段，忽略多余字段（如 security_id, lid）。
        """
        from src.models.job import Job
        from datetime import datetime

        # 获取 Job 模型所有合法字段名
        valid_columns = {c.name for c in Job.__table__.columns}

        for job_data in jobs:
            job_id = job_data.get("job_id")
            if not job_id:
                continue

            # 过滤掉模型中没有的字段
            filtered = {
                k: v for k, v in job_data.items()
                if k in valid_columns
            }

            # fetch_time 字符串转 datetime 对象（SQLite 兼容）
            ft = filtered.get("fetch_time")
            if isinstance(ft, str):
                try:
                    filtered["fetch_time"] = datetime.strptime(
                        ft, "%Y-%m-%d %H:%M:%S"
                    )
                except ValueError:
                    filtered["fetch_time"] = datetime.utcnow()

            existing = (
                db_session.query(Job)
                .filter(Job.job_id == job_id)
                .first()
            )
            if existing:
                # 更新已有记录
                for key, value in filtered.items():
                    setattr(existing, key, value)
            else:
                # 新增记录
                db_session.add(Job(**filtered))

        db_session.commit()

    @staticmethod
    def _log_crawl(
        db_session,
        keyword: str,
        city: str,
        pages: int,
        fetched_count: int,
        status: str,
        error_msg: str = None,
        filters: Optional[Dict] = None,
    ) -> None:
        """记录采集日志。"""
        from src.models.job import CrawlLog

        log = CrawlLog(
            keyword=keyword,
            city=city,
            page=pages,
            fetched_count=fetched_count,
            status=status,
            error_msg=error_msg,
            filters_json=filters,
        )
        db_session.add(log)
        db_session.commit()
