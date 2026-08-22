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
from typing import Dict, List, Optional, Generator, Any

from sqlalchemy.orm import Session
from sqlalchemy import desc, func, and_

from src.models.job import Job, CrawlLog
from src.services.crawl_service import CrawlService
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
                    result = self._do_crawl(
                        keyword, city, filters, db,
                        log_callback=lambda msg, level='info': log_queue.put((msg, level))
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
        检查今天是否有匹配的爬取记录（筛选词完全相同，不多不少）。

        匹配条件：
        - CrawlLog.timestamp 是今天
        - CrawlLog.keyword == keyword
        - CrawlLog.city == city（都为空时也算匹配）
        - CrawlLog.filters_json 与 filters 完全相同
        - CrawlLog.status == 'success'
        """
        today = date.today()
        today_start = datetime.combine(today, datetime.min.time())
        today_end = datetime.combine(today, datetime.max.time())

        query = db.query(CrawlLog).filter(
            and_(
                CrawlLog.keyword == keyword,
                CrawlLog.timestamp >= today_start,
                CrawlLog.timestamp <= today_end,
                CrawlLog.status == "success",
            )
        )

        if city:
            query = query.filter(CrawlLog.city == city)
        else:
            query = query.filter((CrawlLog.city.is_(None)) | (CrawlLog.city == ""))

        logs = query.all()

        if not logs:
            return False

        # 检查筛选条件是否完全匹配
        for log in logs:
            if KeywordParser.filters_match(log.filters_json, filters):
                return True

        return False

    def _do_crawl(
        self, keyword: str, city: str, filters: Optional[Dict], db: Session,
        log_callback=None,
    ) -> Dict:
        """调用爬虫服务采集岗位数据。

        如果关键词包含空格（如 "python java"），拆分为多个子关键词
        分别采集，合并结果（与采集任务模块的行为一致）。

        参数:
            log_callback: 日志回调函数 (message, level) -> None
        """
        # 如果没有指定城市，使用默认城市"上海"
        crawl_city = city if city else "上海"

        # 拆分复合关键词（如 "python java" -> ["python", "java"]）
        keywords = [kw.strip() for kw in keyword.split() if kw.strip()]
        if not keywords:
            keywords = [keyword]

        total_jobs = 0
        errors = []

        for i, kw in enumerate(keywords):
            if len(keywords) > 1:
                if log_callback:
                    log_callback(f"  [CRAWL] 子关键词 {i+1}/{len(keywords)}: {kw}", "info")

            service = CrawlService()
            # 设置日志回调，将爬虫日志实时推送给调用方
            if log_callback:
                service.log_callback = log_callback

            result = service.crawl(
                keyword=kw,
                city=crawl_city,
                pages=2,
                fetch_detail=False,  # AI助手模式不需要详情页，列表数据足够
                filters=filters,
                output_format="json",
                db_session=db,
            )

            if result.get("success"):
                total_jobs += result.get("total_jobs", 0)
            else:
                errors.append(result.get("error", "未知错误"))
                # 环境检查失败时直接返回，不继续采集
                if result.get("env_check_failed"):
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

        # 经验匹配
        experience = keywords.get("experience", "").strip()
        if experience and experience != "不限":
            query = query.filter(Job.experience == experience)

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
