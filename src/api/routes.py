"""
FastAPI 路由定义

提供 RESTful API 接口：
- GET  /api/jobs         - 分页查询职位列表
- GET  /api/jobs/{id}    - 获取单条职位详情
- POST /api/crawl/start  - 触发爬取任务
- GET  /api/crawl/status - 查询采集日志
- GET  /api/stats        - 数据统计
- GET  /api/cities       - 获取有数据的城市列表
- GET  /api/cities/all   - 获取所有支持的城市
- POST /api/env/check    - 环境检查
- POST /api/chrome/setup - 启动Chrome并等待登录
"""

import uuid
import os
import tempfile
import time
from typing import Optional
from collections import deque

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, UploadFile, File
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from src.models.database import get_db
from src.services.job_service import JobService
from src.services.crawl_service import CrawlService
from src.utils.city_codes import list_cities_with_codes, list_cities
from src.api.schemas import (
    CrawlRequest,
    CrawlResponse,
    JobListResponse,
    StatsResponse,
    EnvironmentCheckResponse,
)

router = APIRouter(prefix="/api", tags=["boss-zhipin"])

# 全局任务状态存储（简单实现，生产环境可用 Redis）
_task_status = {}

# 实时日志缓冲区：task_id -> deque of log lines
# 每个任务的日志保存在内存中，前端通过 SSE 实时拉取
_task_logs = {}  # task_id -> deque(maxlen=200)


# ========== 职位查询 ==========

@router.get("/jobs")
def list_jobs(
    keyword: Optional[str] = None,
    city: Optional[str] = None,
    company: Optional[str] = None,
    page: int = 1,
    page_size: int = 20,
    sort_by: str = "fetch_time",
    sort_order: str = "desc",
    db: Session = Depends(get_db),
):
    """分页查询职位列表，支持按关键词、城市、公司筛选。"""
    result = JobService.list_jobs(
        db,
        keyword=keyword,
        city=city,
        company=company,
        page=page,
        page_size=page_size,
        sort_by=sort_by,
        sort_order=sort_order,
    )
    return result


@router.get("/jobs/{job_id}")
def get_job_detail(job_id: str, db: Session = Depends(get_db)):
    """获取单条职位详情。"""
    result = JobService.get_job_detail(db, job_id)
    if not result:
        raise HTTPException(status_code=404, detail="Job not found")
    return result


@router.get("/jobs/{job_id}/detail-url")
def get_job_detail_url(job_id: str, db: Session = Depends(get_db)):
    """
    获取岗位详情页的 URL，并检查是否过期。

    BOSS直聘的 securityId 有时效性（通常30分钟左右过期）。
    本接口检查采集时间是否超过30分钟：
    - 未超时：直接返回数据库中保存的 URL
    - 超时：返回 need_refresh=True，提示前端需要刷新链接
    """
    from datetime import datetime, timedelta

    # 从数据库查询岗位信息
    result = JobService.get_job_detail(db, job_id)
    if not result:
        raise HTTPException(status_code=404, detail="Job not found")

    stored_url = result.get("detail_url", "")
    fetch_time_str = result.get("fetch_time", "")

    # 解析采集时间，判断是否超过30分钟
    need_refresh = False
    fetch_time = None
    if fetch_time_str:
        try:
            fetch_time = datetime.strptime(fetch_time_str, "%Y-%m-%d %H:%M:%S")
            elapsed = datetime.now() - fetch_time
            if elapsed > timedelta(minutes=30):
                need_refresh = True
        except (ValueError, TypeError):
            need_refresh = True
    else:
        need_refresh = True

    if need_refresh:
        return {
            "detail_url": stored_url,
            "need_refresh": True,
            "fetch_time": fetch_time_str,
            "message": "链接可能已过期，需要刷新获取最新详情链接",
        }
    else:
        return {
            "detail_url": stored_url,
            "need_refresh": False,
            "fetch_time": fetch_time_str,
            "message": "链接有效",
        }


@router.post("/jobs/{job_id}/refresh-url")
def refresh_job_detail_url(job_id: str, db: Session = Depends(get_db)):
    """
    刷新岗位详情页 URL（获取最新 securityId 并更新数据库）。

    流程：
    1. 查询岗位信息（keyword, city）
    2. 启动 Chrome（如未运行）或连接已有 Chrome
    3. 通过 BOSS 搜索 API 获取该岗位最新的 securityId
    4. 构造新的详情页 URL
    5. 更新数据库中的 detail_url 和 fetch_time
    """
    import urllib.parse
    from datetime import datetime
    from src.crawler.cdp_connector import CDPConnector
    from src.config import settings
    from src.utils.city_codes import get_city_code
    from src.models.job import Job

    # 从数据库查询岗位信息
    result = JobService.get_job_detail(db, job_id)
    if not result:
        raise HTTPException(status_code=404, detail="Job not found")

    stored_url = result.get("detail_url", "")
    keyword = result.get("keyword", "")
    city = result.get("city", "")
    job_name = result.get("job_name", "")

    try:
        connector = CDPConnector()

        # 复用已有 Chrome 实例（不杀旧进程，避免多设备登录冲突）
        # 如果 Chrome 未运行，用已有 profile 启动（复用登录态）
        # 如果 Chrome 已运行，直接连接
        connector.ensure_chrome(headless=False)

        # 等待页面就绪
        import time
        time.sleep(2)

        city_code = get_city_code(city) if city else ""
        search_keyword = keyword or job_name.split(" ")[0] or "python"

        # 通过搜索 API 获取该岗位最新的 securityId
        js_code = f"""
            (function() {{
                try {{
                    var xhr = new XMLHttpRequest();
                    var params = 'scene=1&query=' + encodeURIComponent('{search_keyword}') +
                                '&city=' + encodeURIComponent('{city_code}') +
                                '&page=1&pageSize=30';
                    xhr.open('GET', '/wapi/zpgeek/search/joblist.json?' + params, false);
                    xhr.setRequestHeader('x-requested-with', 'XMLHttpRequest');
                    xhr.send();
                    if (xhr.status !== 200) return null;
                    var data = JSON.parse(xhr.responseText);
                    if (data.code !== 0) return null;
                    var jobList = data.zpData && data.zpData.jobList || [];
                    // 查找匹配的岗位
                    for (var i = 0; i < jobList.length; i++) {{
                        if (jobList[i].encryptJobId === '{job_id}') {{
                            return {{
                                securityId: jobList[i].securityId,
                                lid: jobList[i].lid,
                            }};
                        }}
                    }}
                    return null;
                }} catch(e) {{
                    return null;
                }}
            }})()
        """

        api_result = connector.evaluate(js_code, await_promise=False)
        connector.close()  # 只关闭 WebSocket，不关闭 Chrome

        if api_result and isinstance(api_result, dict) and api_result.get("securityId"):
            # 构造最新的详情页 URL
            fresh_url = settings.BOSS_DETAIL_URL_TEMPLATE.format(
                job_id=job_id,
                lid=api_result.get("lid", ""),
                security_id=urllib.parse.quote(api_result["securityId"], safe=""),
            )

            # 更新数据库中的 detail_url 和 fetch_time
            now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            now_dt = datetime.now()
            job_obj = db.query(Job).filter(Job.job_id == job_id).first()
            if job_obj:
                job_obj.detail_url = fresh_url
                job_obj.fetch_time = now_dt
                db.commit()

            return {
                "detail_url": fresh_url,
                "fresh": True,
                "fetch_time": now_str,
                "message": "已获取最新详情页链接并更新数据库",
            }
        else:
            return {
                "detail_url": stored_url,
                "fresh": False,
                "message": "未能从搜索结果中找到该岗位，请稍后重试或手动在 BOSS 直聘中搜索",
            }
    except Exception as e:
        return {
            "detail_url": stored_url,
            "fresh": False,
            "message": f"刷新链接失败: {str(e)}",
        }


# ========== 采集任务 ==========

@router.post("/crawl/start")
def start_crawl(
    req: CrawlRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
):
    """触发爬取任务（异步执行）。"""
    task_id = str(uuid.uuid4())[:8]
    _task_status[task_id] = {
        "status": "pending",
        "keywords": req.keywords,
        "city": req.city,
        "total_jobs": 0,
    }

    background_tasks.add_task(_run_crawl_task, task_id, req, db)

    return CrawlResponse(
        status="started",
        message=f"Crawl task started: {req.keywords}",
        task_id=task_id,
    )


@router.get("/crawl/status")
def crawl_status(
    task_id: Optional[str] = None,
    limit: int = 20,
    db: Session = Depends(get_db),
):
    """查询采集任务状态和日志。"""
    result = {"task_status": None, "recent_logs": [], "live_logs": []}

    if task_id and task_id in _task_status:
        result["task_status"] = _task_status[task_id]
        # 同时返回该任务的实时日志
        if task_id in _task_logs:
            result["live_logs"] = list(_task_logs[task_id])

    result["recent_logs"] = JobService.get_crawl_logs(db, limit)
    return result


@router.get("/crawl/stream/{task_id}")
def crawl_stream(task_id: str):
    """SSE 端点：实时推送采集日志到前端。"""
    import json as _json

    def event_generator():
        sent_count = 0
        max_idle = 300  # 最长 5 分钟无新日志后自动关闭
        idle = 0

        while True:
            # 检查任务是否存在
            if task_id not in _task_status:
                yield f"data: {_json.dumps({'type': 'error', 'message': '任务不存在'})}\n\n"
                break

            # 发送新日志
            if task_id in _task_logs:
                all_logs = list(_task_logs[task_id])
                new_logs = all_logs[sent_count:]
                for log_entry in new_logs:
                    sent_count = len(all_logs)
                    yield f"data: {_json.dumps(log_entry)}\n\n"

            # 检查任务是否结束
            status = _task_status[task_id].get("status", "")
            if status in ("completed", "error"):
                # 发送结束信号
                end_data = {
                    "type": "end",
                    "status": status,
                    "total_jobs": _task_status[task_id].get("total_jobs", 0),
                    "error": _task_status[task_id].get("error", ""),
                }
                yield f"data: {_json.dumps(end_data)}\n\n"
                break

            time.sleep(0.5)
            idle += 0.5
            if idle > max_idle:
                yield f"data: {_json.dumps({'type': 'timeout', 'message': '超时自动关闭'})}\n\n"
                break

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


@router.get("/stats")
def get_stats(db: Session = Depends(get_db)):
    """获取数据统计（总数、城市分布、热门公司等）。"""
    return JobService.get_stats(db)


# ========== 城市列表 ==========

@router.get("/cities")
def get_cities_with_data(db: Session = Depends(get_db)):
    """获取数据库中有职位数据的城市列表。"""
    return {"cities": JobService.get_cities(db)}


@router.get("/cities/all")
def get_all_cities(keyword: str = ""):
    """获取所有支持的城市列表（含城市码），可选关键词过滤。"""
    return {"cities": list_cities_with_codes(keyword)}


# ========== 环境管理 ==========

@router.post("/env/check")
def check_environment():
    """环境检查：Chrome CDP、依赖、登录态。"""
    service = CrawlService()
    result = service.check_environment()
    return result


@router.post("/chrome/setup")
def setup_chrome(login_timeout: int = 300):
    """启动Chrome并等待登录（同步执行，可能需要较长时间）。"""
    service = CrawlService()
    success = service.setup_chrome(login_timeout)
    if success:
        return {"status": "success", "message": "Chrome setup complete, logged in."}
    else:
        return {
            "status": "failed",
            "message": "Chrome setup failed. Check login or network.",
        }


# ========== 简历解析 ==========

@router.post("/resume/parse")
async def parse_resume(file: UploadFile = File(...)):
    """
    上传 PDF 简历文件，后端解析提取结构化数据。

    - 接收 PDF 文件
    - 优先使用 DeepSeek AI 大模型解析（需配置 DEEPSEEK_API_KEY）
    - 未配置 API Key 时回退到正则+模式匹配解析
    - 同时提取 PDF 中的图片作为头像
    - AI 模式下还会推荐最匹配的简历模板
    - 返回标准化 JSON 数据（与前端 store 结构一致）
    """
    if not file.filename:
        raise HTTPException(status_code=400, detail="未提供文件")

    if not file.filename.lower().endswith('.pdf'):
        raise HTTPException(status_code=400, detail="仅支持 PDF 格式文件")

    try:
        content = await file.read()
        if not content:
            raise HTTPException(status_code=400, detail="文件内容为空")

        from src.services.resume_parser import ResumeParser
        parser = ResumeParser()
        result = parser.parse(content)

        parse_method = result.pop('parseMethod', 'regex')
        suggested_template = result.pop('suggestedTemplate', None)

        method_label = "AI大模型" if parse_method == 'ai' else "正则规则"

        message = f"解析完成（{method_label}），提取了 {len(result.get('education', []))} 条教育经历、"
        message += f"{len(result.get('workExperience', []))} 条工作经历、"
        message += f"{len(result.get('projects', []))} 条项目经历"
        if suggested_template:
            template_names = {
                'simple': '经典简约', 'modern': '现代简约', 'sidebar': '侧边栏风格',
                'professional': '商务专业', 'creative': '创意风格', 'elegant': '雅致风格',
                'classic': '经典横幅', 'darksidebar': '深色侧栏', 'minimal': '极简留白',
            }
            message += f"，推荐模板：{template_names.get(suggested_template, suggested_template)}"

        return {
            "status": "success",
            "message": message,
            "data": result,
            "parseMethod": parse_method,
            "suggestedTemplate": suggested_template,
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"解析失败: {str(e)}")


# ========== 后台任务 ==========

def _log_to_task(task_id: str, message: str, level: str = "info"):
    """向任务日志缓冲区追加一条日志（供前端实时显示）。"""
    if task_id not in _task_logs:
        _task_logs[task_id] = deque(maxlen=200)
    _task_logs[task_id].append({
        "type": "log",
        "level": level,
        "message": message,
        "timestamp": time.strftime("%H:%M:%S"),
    })


def _run_crawl_task(task_id: str, req: CrawlRequest, db: Session):
    """后台执行采集任务。"""
    _task_status[task_id]["status"] = "running"
    _log_to_task(task_id, f"采集任务启动：关键词={req.keywords}，城市={req.city}，页数={req.pages}")

    service = CrawlService()
    # 注入日志回调
    service.log_callback = lambda msg, level="info": _log_to_task(task_id, msg, level)

    total = 0

    for keyword in req.keywords:
        _task_status[task_id]["current_keyword"] = keyword
        _log_to_task(task_id, f"开始采集关键词: {keyword}")

        result = service.crawl(
            keyword=keyword,
            city=req.city,
            pages=req.pages,
            fetch_detail=req.fetch_detail,
            filters=req.filters,
            db_session=db,
        )

        if result.get("success"):
            total += result["total_jobs"]
            _log_to_task(task_id, f"关键词 '{keyword}' 采集完成，共 {result['total_jobs']} 条", "success")
        else:
            _task_status[task_id]["status"] = "error"
            _task_status[task_id]["error"] = result.get("error")
            _log_to_task(task_id, f"采集失败: {result.get('error')}", "error")
            return

    _task_status[task_id]["status"] = "completed"
    _task_status[task_id]["total_jobs"] = total
    _log_to_task(task_id, f"全部采集完成！共 {total} 条职位数据", "success")
