"""
AI 助手服务模块

核心流程编排：
1. 解析用户需求 → 结构化关键词组
2. 查询数据库当天是否有匹配的爬取记录（筛选词完全相同）
3. 如无则调用爬虫采集
4. 查询数据库筛选出与关键词组完全符合的岗位列表
5. 将岗位完整数据和关键词发送LLM进行分析
6. 返回分析结果

通过生成器模式实现逐步输出，前端可同步展示处理过程。
"""

import time
import json
import queue
import threading
from datetime import datetime, date
from typing import Dict, List, Optional, Generator, Any, Callable

from sqlalchemy.orm import Session
from sqlalchemy import desc, func, and_

from src.models.job import Job, CrawlLog
from src.services.crawl_service import CrawlService
from src.services.login_manager import LoginManager
from src.ai_assistant.keyword_parser import KeywordParser
from src.ai_assistant.job_analyzer import JobAnalyzer
from src.ai_assistant.mongo_manager import MongoManager


class AssistantService:
    """AI 助手主服务"""

    def __init__(self):
        self.keyword_parser = KeywordParser()
        self.job_analyzer = JobAnalyzer()

    def chat(
        self,
        user_input: str,
        db: Session,
        conversation_id: Optional[str] = None,
        user_id: str = "default_user",
    ) -> Generator[Dict, None, None]:
        """
        处理用户对话，逐步输出处理过程和最终结果。

        通过生成器模式逐步yield：
        - {"type": "step", "step": N, "status": "running/completed", "title": "...", "detail": "..."}
        - {"type": "content", "content": "部分内容"}  (LLM流式输出)
        - {"type": "done", "conversation_id": "...", "keywords": {...}}
        - {"type": "error", "message": "..."}

        参数:
            user_input: 用户的自然语言输入
            db: 数据库会话
            conversation_id: 对话ID（如为None则创建新对话）
            user_id: 用户标识
        """
        # ========== 步骤1: 创建/获取对话 ==========
        if not conversation_id:
            # 创建新对话
            try:
                conversation_id = MongoManager.create_conversation(
                    user_id=user_id,
                    title=user_input[:30]
                )
            except Exception as e:
                yield {"type": "error", "message": f"创建对话失败: {e}"}
                return
        else:
            # 验证对话存在
            conv = MongoManager.get_conversation(conversation_id)
            if not conv:
                try:
                    conversation_id = MongoManager.create_conversation(
                        user_id=user_id,
                        title=user_input[:30]
                    )
                except Exception as e:
                    yield {"type": "error", "message": f"创建对话失败: {e}"}
                    return

        # 保存用户消息
        try:
            MongoManager.add_message(conversation_id, "user", user_input)
        except Exception as e:
            yield {"type": "error", "message": f"保存用户消息失败: {e}"}
            return

        # 获取上下文消息（排除刚添加的用户消息）
        context_messages = MongoManager.get_context_messages(conversation_id, max_messages=6)

        process_steps = []
        crawl_logs = []  # 收集爬虫日志用于持久化保存

        # ========== 步骤1: 解析用户需求 ==========
        step1 = {"step": 1, "status": "running", "title": "解析用户需求", "detail": "正在使用AI解析您的求职需求..."}
        yield {"type": "step", **step1}
        process_steps.append(step1)

        try:
            keywords = self.keyword_parser.parse(user_input, context_messages)
        except Exception as e:
            step1["status"] = "error"
            step1["detail"] = f"解析失败: {e}"
            yield {"type": "step", **step1}
            yield {"type": "error", "message": f"解析用户需求失败: {e}"}
            return

        kw_desc = self._format_keywords(keywords)
        step1["status"] = "completed"
        step1["detail"] = kw_desc
        yield {"type": "step", **step1}

        # 更新用户消息中的关键词
        try:
            MongoManager.add_message(
                conversation_id, "system",
                f"[已解析关键词] {kw_desc}",
                parsed_keywords=keywords
            )
        except Exception:
            pass

        keyword = keywords.get("keyword", "").strip()
        city = keywords.get("city", "").strip()
        filters = KeywordParser.normalize_filters(keywords)

        if not keyword:
            yield {"type": "error", "message": "无法从您的需求中解析出搜索关键词，请更具体地描述您的求职需求。"}
            return

        # ========== 步骤2: 检查数据库当天爬取记录 ==========
        step2 = {
            "step": 2,
            "status": "running",
            "title": "检查数据库爬取记录",
            "detail": f"查询当天是否有匹配的爬取记录（关键词={keyword}，城市={city or '不限'}）..."
        }
        yield {"type": "step", **step2}
        process_steps.append(step2)

        has_today_record = self._check_today_crawl_log(db, keyword, city, filters)

        if has_today_record:
            step2["status"] = "completed"
            step2["detail"] = f"找到当天匹配的爬取记录，跳过爬取步骤"
            yield {"type": "step", **step2}
        else:
            step2["status"] = "completed"
            step2["detail"] = f"未找到当天匹配的爬取记录，需要执行爬取"
            yield {"type": "step", **step2}

            # ========== 步骤3: 调用爬虫采集 ==========
            step3 = {
                "step": 3,
                "status": "running",
                "title": "启动爬虫采集岗位数据",
                "detail": f"正在爬取关键词「{keyword}」，城市「{city or '不限'}」..."
            }
            yield {"type": "step", **step3}
            process_steps.append(step3)

            # 使用线程 + 队列实现爬虫日志实时推送
            log_queue = queue.Queue()
            crawl_result_box = {}

            def _run_crawl():
                """在线程中执行爬取，日志通过队列推送。"""
                try:
                    # 登录事件回调：创建会话并推送到队列
                    def _login_event_cb(reason: str, code: int) -> str:
                        """
                        当爬虫检测到未登录/风控时调用。
                        通过队列推送 login_required 事件到 SSE 流，
                        返回 session_id 供调用方等待。
                        """
                        login_manager = LoginManager()
                        session_id = login_manager.create_session(reason=reason)
                        # 推送 login_required 事件到队列（SSE 流会消费）
                        log_queue.put(("__login_required__", session_id, reason, code))
                        return session_id

                    result = self._do_crawl(
                        keyword, city, filters, db,
                        log_callback=lambda msg, level='info': log_queue.put((msg, level)),
                        login_event_callback=_login_event_cb,
                        event_queue=log_queue,
                    )
                    crawl_result_box["result"] = result
                except Exception as e:
                    crawl_result_box["error"] = e
                finally:
                    log_queue.put(None)  # 哨兵值，表示爬取结束

            crawl_thread = threading.Thread(target=_run_crawl, daemon=True)
            crawl_thread.start()

            # 实时消费日志队列，通过 SSE 推送给前端
            while True:
                try:
                    item = log_queue.get(timeout=0.5)
                except queue.Empty:
                    if not crawl_thread.is_alive():
                        break
                    continue

                if item is None:
                    break

                # 区分日志事件和登录要求事件
                if isinstance(item, tuple) and len(item) == 4 and item[0] == "__login_required__":
                    _, session_id, reason, code = item
                    # 通过 SSE 推送 login_required 事件给前端
                    yield {
                        "type": "login_required",
                        "session_id": session_id,
                        "reason": reason,
                        "code": code,
                    }
                    continue

                # 登录成功事件
                if isinstance(item, tuple) and len(item) == 2 and item[0] == "__login_success__":
                    _, session_id = item
                    yield {"type": "login_success", "session_id": session_id}
                    continue

                # 登录取消事件
                if isinstance(item, tuple) and len(item) == 2 and item[0] == "__login_cancelled__":
                    _, session_id = item
                    yield {"type": "login_cancelled", "session_id": session_id}
                    continue

                msg, level = item
                crawl_logs.append({"message": msg, "level": level, "time": datetime.now().strftime("%H:%M:%S")})
                yield {"type": "log", "step": 3, "message": msg, "level": level}

            crawl_thread.join(timeout=5)

            # 获取爬取结果
            if "error" in crawl_result_box:
                crawl_result = {"success": False, "error": str(crawl_result_box["error"])}
            else:
                crawl_result = crawl_result_box.get("result", {"success": False, "error": "未知结果"})

            if crawl_result.get("success"):
                total = crawl_result.get("total_jobs", 0)
                step3["status"] = "completed"
                step3["detail"] = f"爬取完成，共获取 {total} 条岗位数据"
                yield {"type": "step", **step3}
            elif crawl_result.get("env_check_failed"):
                # 环境检查失败，将原因返回给用户
                env_errors = crawl_result.get("env_errors", [])
                error_detail = "；".join(env_errors) if env_errors else "环境检查未通过"
                step3["status"] = "error"
                step3["detail"] = f"环境检查未通过: {error_detail}"
                yield {"type": "step", **step3}

                # 保存错误消息并返回给用户
                error_reply = (
                    f"## 爬取环境检查未通过\n\n"
                    f"很抱歉，爬取任务无法执行。原因如下：\n\n"
                    f"{error_detail}\n\n"
                    f"**建议操作：**\n"
                    f"1. 如果是登录过期，请在「采集任务」页面点击「环境检查」完成登录\n"
                    f"2. 如果是 Chrome 未启动，请确保 Chrome 浏览器已安装并关闭所有 Chrome 窗口后重试\n"
                    f"3. 如果是风控限制，请稍后再试\n"
                )
                try:
                    MongoManager.add_message(
                        conversation_id, "assistant",
                        error_reply,
                        process_steps=process_steps,
                        logs=crawl_logs
                    )
                except Exception:
                    pass
                yield {"type": "content", "content": error_reply}
                yield {"type": "done", "conversation_id": conversation_id, "keywords": keywords}
                return
            else:
                error = crawl_result.get("error", "未知错误")
                step3["status"] = "error"
                step3["detail"] = f"爬取失败: {error}，将尝试使用数据库已有数据"
                yield {"type": "step", **step3}

        # ========== 步骤4: 查询数据库匹配岗位 ==========
        step4 = {
            "step": 4,
            "status": "running",
            "title": "查询数据库筛选匹配岗位",
            "detail": "正在从数据库筛选符合关键词组的岗位..."
        }
        yield {"type": "step", **step4}
        process_steps.append(step4)

        jobs = self._query_matching_jobs(db, keyword, city, keywords, limit=50)

        if not jobs:
            step4["status"] = "completed"
            step4["detail"] = "未找到匹配的岗位数据"
            yield {"type": "step", **step4}
            # 保存空结果
            try:
                MongoManager.add_message(
                    conversation_id, "assistant",
                    "未找到匹配的岗位数据。请尝试调整搜索条件，如更换关键词或放宽筛选范围。",
                    process_steps=process_steps,
                    logs=crawl_logs
                )
            except Exception:
                pass
            yield {"type": "content", "content": "未找到匹配的岗位数据。请尝试调整搜索条件，如更换关键词或放宽筛选范围。"}
            yield {"type": "done", "conversation_id": conversation_id, "keywords": keywords}
            return

        step4["status"] = "completed"
        step4["detail"] = f"筛选出 {len(jobs)} 条匹配岗位"
        yield {"type": "step", **step4}

        # ========== 步骤5: LLM 分析岗位 ==========
        step5 = {
            "step": 5,
            "status": "running",
            "title": "AI分析岗位推荐",
            "detail": "正在将岗位数据发送给AI进行分析..."
        }
        yield {"type": "step", **step5}
        process_steps.append(step5)

        # 获取上下文消息（包含用户和assistant的历史对话）
        context_for_llm = MongoManager.get_context_messages(conversation_id, max_messages=6)

        full_result = ""
        try:
            for chunk in self.job_analyzer.analyze_stream(
                jobs, keywords, context_for_llm, user_input
            ):
                full_result += chunk
                yield {"type": "content", "content": chunk}
        except Exception as e:
            step5["status"] = "error"
            step5["detail"] = f"AI分析失败: {e}"
            yield {"type": "step", **step5}
            yield {"type": "error", "message": f"AI分析失败: {e}"}
            return

        step5["status"] = "completed"
        step5["detail"] = "AI分析完成"
        yield {"type": "step", **step5}

        # ========== 保存AI回复到MongoDB ==========
        try:
            MongoManager.add_message(
                conversation_id, "assistant",
                full_result,
                process_steps=process_steps,
                logs=crawl_logs
            )
        except Exception as e:
            print(f"[AssistantService] Failed to save assistant message: {e}")

        # ========== 完成 ==========
        yield {
            "type": "done",
            "conversation_id": conversation_id,
            "keywords": keywords,
        }

    # ========== 内部方法 ==========

    def _check_today_crawl_log(
        self, db: Session, keyword: str, city: str, filters: Optional[Dict]
    ) -> bool:
        """
        检查今天是否有匹配的爬取记录（且采集到了数据）。

        匹配条件：
        - CrawlLog.timestamp 是今天
        - CrawlLog.keyword == keyword（或 keyword 的子关键词有记录）
        - CrawlLog.city == city（都为空时也算匹配）
        - CrawlLog.status == 'success'
        - CrawlLog.fetched_count > 0（确保采集到了数据，不是空结果）

        满足以上条件时，直接在数据库中查询分析，不需要重新爬取。
        """
        today = date.today()
        today_start = datetime.combine(today, datetime.min.time())
        today_end = datetime.combine(today, datetime.max.time())

        # 拆分复合关键词，所有子关键词都需要有当天的成功记录
        keywords = [kw.strip() for kw in keyword.split() if kw.strip()]
        if not keywords:
            keywords = [keyword]

        for kw in keywords:
            query = db.query(CrawlLog).filter(
                and_(
                    CrawlLog.keyword == kw,
                    CrawlLog.timestamp >= today_start,
                    CrawlLog.timestamp <= today_end,
                    CrawlLog.status == "success",
                    CrawlLog.fetched_count > 0,
                )
            )

            if city:
                query = query.filter(CrawlLog.city == city)
            else:
                query = query.filter((CrawlLog.city.is_(None)) | (CrawlLog.city == ""))

            logs = query.all()
            if not logs:
                # 任一子关键词没有当天成功记录，需要重新爬取
                return False

        # 所有子关键词都有当天成功记录，跳过爬取
        return True

    def _do_crawl(
        self, keyword: str, city: str, filters: Optional[Dict], db: Session,
        log_callback=None,
        login_event_callback=None,
        event_queue=None,
    ) -> Dict:
        """调用爬虫服务采集岗位数据。

        如果关键词包含空格（如 "python java"），拆分为多个子关键词
        分别采集，合并结果（与采集任务模块的行为一致）。

        关键设计：
        - 所有关键词共用同一个 CrawlService 实例和 Chrome 连接
        - 第一个关键词执行环境检查并启动 Chrome（有头模式）
        - 后续关键词用 skip_env_check=True 复用已有连接
        - 所有关键词采集完成后才关闭 Chrome
        - 检测到未登录/风控时通过 SSE 通知前端，等待用户完成登录后继续

        参数:
            log_callback: 日志回调函数 (message, level) -> None
            login_event_callback: 登录事件回调 (reason, code) -> session_id
                用于通过 SSE 向前端推送 login_required 事件，并等待用户完成登录。
            event_queue: 事件队列，用于向 SSE 流推送登录成功/取消事件
        """
        # 如果没有指定城市，使用默认城市"上海"
        crawl_city = city if city else "上海"

        # 拆分复合关键词（如 "python java" -> ["python", "java"]）
        keywords = [kw.strip() for kw in keyword.split() if kw.strip()]
        if not keywords:
            keywords = [keyword]

        total_jobs = 0
        errors = []

        # 创建一个共用的 CrawlService 实例
        service = CrawlService()
        if log_callback:
            service.log_callback = log_callback

        # 设置登录要求回调
        # 当爬虫检测到未登录/风控时，通过 SSE 通知前端并等待用户登录
        if login_event_callback:
            def _auth_callback(reason: str, code: int) -> bool:
                """登录要求回调：通过 SSE 通知前端，等待用户完成登录。"""
                try:
                    # 通过回调向 SSE 流推送 login_required 事件
                    # login_event_callback 返回 session_id，用于等待用户完成登录
                    login_session_id = login_event_callback(reason, code)
                    if login_session_id:
                        # 等待用户完成登录
                        login_manager = LoginManager()
                        success = login_manager.wait_for_login(
                            login_session_id,
                            timeout=300,
                        )
                        if success:
                            if log_callback:
                                log_callback("  [OK] 用户已完成登录，继续采集...", "info")
                            # 通过队列推送 login_success 事件给 SSE 流
                            if event_queue:
                                event_queue.put(("__login_success__", login_session_id))
                            # 用户已在 Chrome 中完成登录，只需重新连接 WebSocket
                            # 不关闭 Chrome 页面，不重启 Chrome 进程
                            try:
                                if service.connector:
                                    # 关闭旧 WebSocket（不关闭 Chrome）
                                    if service.connector.ws:
                                        service.connector.close()
                                    # 重新连接到已有 Chrome 页面
                                    service.connector.connect()
                            except Exception as e:
                                if log_callback:
                                    log_callback(f"  [WARN] 重新连接 Chrome: {e}", "warn")
                            return True
                        else:
                            if log_callback:
                                log_callback("  [WARN] 用户未完成登录，取消采集", "warn")
                            # 通过队列推送 login_cancelled 事件给 SSE 流
                            if event_queue:
                                event_queue.put(("__login_cancelled__", login_session_id))
                            return False
                    return False
                except Exception as e:
                    if log_callback:
                        log_callback(f"  [ERROR] 登录回调异常: {e}", "error")
                    return False

            service.auth_required_callback = _auth_callback

        for i, kw in enumerate(keywords):
            if len(keywords) > 1:
                if log_callback:
                    log_callback(f"  [CRAWL] 子关键词 {i+1}/{len(keywords)}: {kw}", "info")

            # 第一个关键词：执行环境检查（启动 Chrome）
            # 后续关键词：跳过环境检查，复用已有 Chrome 连接
            # 最后一个关键词：采集完成后关闭 Chrome
            is_last = (i == len(keywords) - 1)

            result = service.crawl(
                keyword=kw,
                city=crawl_city,
                pages=2,
                fetch_detail=False,  # AI助手模式不需要详情页，列表数据足够
                filters=None,  # 爬虫采集时不传筛选条件，采集所有数据；筛选条件在数据库查询阶段应用
                output_format="json",
                db_session=db,
                skip_env_check=(i > 0),  # 第一个关键词不跳过，后续跳过
                keep_chrome_alive=(not is_last),  # 最后一个关键词采集完才关闭 Chrome
            )

            if result.get("success"):
                total_jobs += result.get("total_jobs", 0)
            else:
                errors.append(result.get("error", "未知错误"))
                # 环境检查失败时直接返回，不继续采集
                if result.get("env_check_failed"):
                    return result
                # 用户取消登录时，关闭 Chrome 并停止采集
                if "取消" in result.get("error", "") or "取消采集" in result.get("error", ""):
                    # 确保 Chrome 被关闭
                    try:
                        if service.connector:
                            service.connector.close()
                            service.connector.stop_chrome()
                            service.connector = None
                    except Exception:
                        pass
                    return result

        if total_jobs > 0:
            return {
                "success": True,
                "total_jobs": total_jobs,
                "keyword": keyword,
                "city": crawl_city,
            }
        else:
            return {
                "success": False,
                "error": "; ".join(errors) if errors else "采集到0条数据",
                "total_jobs": 0,
            }

    def _query_matching_jobs(
        self, db: Session, keyword: str, city: str, keywords: Dict, limit: int = 50
    ) -> List[Dict]:
        """
        查询数据库中与关键词组完全符合的岗位列表。

        筛选逻辑：
        - keyword: 模糊匹配 job_name（拆分关键词，任一匹配即可）
        - city: 精确匹配
        - experience: 精确匹配（中文描述）
        - degree(education): 精确匹配（中文描述）
        - scale(company_scale): 精确匹配
        - salary: 通过薪资范围描述匹配（包含相邻范围）
        """
        from sqlalchemy import or_

        query = db.query(Job)

        # 关键词匹配：拆分关键词，任一部分匹配即可
        # 例如 "Java开发" -> 匹配 job_name 包含 "Java" 或 "开发"
        import re as _re
        # 提取关键词中的有意义子串（英文单词、中文词组）
        keyword_parts = []
        # 提取英文字母序列（如 Java, Python, AI）
        en_parts = _re.findall(r'[a-zA-Z]+', keyword)
        keyword_parts.extend(en_parts)
        # 提取中文字符序列，每2个字为一组
        cn_str = _re.sub(r'[^\u4e00-\u9fa5]', '', keyword)
        for i in range(len(cn_str) - 1):
            keyword_parts.append(cn_str[i:i+2])
        if cn_str:
            keyword_parts.append(cn_str)
        # 整体关键词也加入
        keyword_parts.append(keyword)
        keyword_parts.append(keyword.replace(' ', ''))
        # 去重
        seen = set()
        unique_parts = []
        for p in keyword_parts:
            if p and p not in seen and len(p) >= 2:
                seen.add(p)
                unique_parts.append(p)
        keyword_conditions = [Job.job_name.contains(p) for p in unique_parts]
        query = query.filter(or_(*keyword_conditions))

        # 城市匹配
        if city:
            query = query.filter(Job.city == city)

        # 经验匹配（智能匹配）
        experience = keywords.get("experience", "").strip()
        if experience and experience != "不限":
            # 构建经验匹配条件列表
            exp_conditions = [Job.experience == experience]
            # 经验不限的岗位始终匹配（不限经验意味着任何经验都可以）
            exp_conditions.append(Job.experience == "经验不限")
            # 用户没有经验/应届/1年以内时，也匹配这些低门槛选项
            if experience in ("应届毕业生", "1年以内"):
                # 无经验的用户也可以看应届和1年以内的岗位
                exp_conditions.append(Job.experience == "应届毕业生")
                exp_conditions.append(Job.experience == "1年以内")
            query = query.filter(or_(*exp_conditions))

        # 学历匹配
        degree = keywords.get("degree", "").strip()
        if degree and degree != "不限":
            query = query.filter(Job.education == degree)

        # 公司规模匹配
        scale = keywords.get("scale", "").strip()
        if scale and scale != "不限":
            query = query.filter(Job.company_scale == scale)

        # 薪资匹配（匹配薪资范围及相邻范围）
        salary = keywords.get("salary", "").strip()
        if salary and salary != "不限":
            salary_map = {
                "3K以下": ["3K", "2K", "1K"],
                "3-5K": ["3-", "4-", "3-5K", "4-5K"],
                "5-10K": ["5-", "6-", "7-", "8-", "9-", "5-10K", "6-7K", "7-8K", "8-9K", "8-13K"],
                "10-15K": ["10-", "11-", "12-", "13-", "14-", "10-15K", "10-13K", "10-14K", "11-12K", "12-13K", "13-14K", "14-15K", "14-17K"],
                "15-20K": ["15-", "16-", "17-", "18-", "19-", "15-20K", "15-16K", "16-17K", "17-18K", "18-19K", "19-20K"],
                "20-30K": ["20-", "25-", "20-30K", "20-25K", "25-30K"],
                "30-50K": ["30-", "35-", "40-", "45-", "30-50K", "30-35K", "35-40K"],
                "50K以上": ["50-", "60-", "50K以上"],
            }
            salary_patterns = salary_map.get(salary, [salary])
            salary_conditions = []
            for pattern in salary_patterns:
                salary_conditions.append(Job.salary_desc.contains(pattern))
            if salary_conditions:
                query = query.filter(or_(*salary_conditions))

        # 优先查当天数据，如果没有则查全部数据
        today = date.today()
        today_start = datetime.combine(today, datetime.min.time())
        # 先构建当天查询
        today_query = query.filter(Job.fetch_time >= today_start)
        today_jobs = today_query.order_by(desc(Job.fetch_time)).limit(limit).all()
        if today_jobs:
            return [job.to_dict(full=True) for job in today_jobs]

        # 当天无数据，查全部数据
        jobs = query.order_by(desc(Job.fetch_time)).limit(limit).all()
        return [job.to_dict(full=True) for job in jobs]

    def _format_keywords(self, keywords: Dict) -> str:
        """格式化关键词组为可读描述。"""
        parts = []
        if keywords.get("keyword"):
            parts.append(f"关键词: {keywords['keyword']}")
        if keywords.get("city"):
            parts.append(f"城市: {keywords['city']}")
        if keywords.get("experience"):
            parts.append(f"经验: {keywords['experience']}")
        if keywords.get("degree"):
            parts.append(f"学历: {keywords['degree']}")
        if keywords.get("salary"):
            parts.append(f"薪资: {keywords['salary']}")
        if keywords.get("scale"):
            parts.append(f"规模: {keywords['scale']}")
        return " | ".join(parts) if parts else "无"
