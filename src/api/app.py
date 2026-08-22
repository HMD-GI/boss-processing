"""
FastAPI 应用入口模块

通过 uvicorn 启动：
    python -m uvicorn src.api.app:app --host 0.0.0.0 --port 8000
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.config import settings
from src.models.database import init_db
from src.api.routes import router
from src.api.assistant_routes import router as assistant_router


def create_app() -> FastAPI:
    """
    创建并配置 FastAPI 应用。

    - 注册路由
    - 配置 CORS
    - 启动时初始化数据库
    """
    app = FastAPI(
        title="BOSS直聘数据采集系统",
        description="基于 Chrome CDP 的 BOSS直聘职位数据采集与查询系统",
        version="1.0.0",
    )

    # CORS 配置
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # 注册路由
    app.include_router(router)
    app.include_router(assistant_router)

    # 启动事件：初始化数据库
    @app.on_event("startup")
    def on_startup():
        try:
            init_db()
            print("[STARTUP] Database initialized successfully.")
        except Exception as e:
            print(f"[STARTUP] Database init failed: {e}")
            print("[STARTUP] API will start, but database features may not work.")

    # 根路由
    @app.get("/")
    def root():
        return {
            "name": "BOSS直聘数据采集系统",
            "version": "1.0.0",
            "docs": "/docs",
            "endpoints": {
                "jobs": "/api/jobs",
                "job_detail": "/api/jobs/{job_id}",
                "crawl_start": "/api/crawl/start",
                "crawl_status": "/api/crawl/status",
                "stats": "/api/stats",
                "cities": "/api/cities",
                "env_check": "/api/env/check",
                "assistant_chat": "/api/assistant/chat",
                "assistant_conversations": "/api/assistant/conversations",
            },
        }

    return app


# uvicorn 直接引用的 app 实例
app = create_app()
