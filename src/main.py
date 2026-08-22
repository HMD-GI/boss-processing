"""
BOSS直聘数据采集系统 - 应用入口

提供两种使用方式：
1. FastAPI Web服务：提供RESTful API接口
2. CLI命令行工具：直接执行采集任务

使用方式：
  # 启动API服务
  python -m src.main serve

  # CLI采集
  python -m src.main crawl --keyword "AI Agent" --city 上海 --pages 3

  # 启动Chrome并登录
  python -m src.main setup

  # 环境检查
  python -m src.main check

  # 列出城市
  python -m src.main cities --keyword 江
"""

import sys
import argparse

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


# uvicorn 直接引用的 app 实例（支持 python -m uvicorn src.main:app）
app = create_app()


# ========== CLI 命令 ==========

def cmd_serve(args):
    """启动 FastAPI API 服务。"""
    import uvicorn

    app = create_app()
    print(f"[SERVE] Starting API server on {settings.API_HOST}:{settings.API_PORT}")
    print(f"[SERVE] Docs: http://localhost:{settings.API_PORT}/docs")
    uvicorn.run(
        app,
        host=settings.API_HOST,
        port=settings.API_PORT,
    )


def cmd_setup(args):
    """启动 Chrome 并等待登录。"""
    from src.services.crawl_service import CrawlService

    service = CrawlService()
    success = service.setup_chrome(args.login_timeout)
    if success:
        print("\n[OK] Environment ready! You can start crawling now.")
    else:
        print("\n[FAIL] Setup failed. Please check login or network.")


def cmd_check(args):
    """环境检查。"""
    from src.services.crawl_service import CrawlService

    print("=== Environment Check ===")
    service = CrawlService()
    result = service.check_environment()

    print(f"  Chrome CDP:     {'OK' if result['chrome_cdp'] else 'FAIL'}")
    print(f"  WebSocket:      {'OK' if result['websocket'] else 'FAIL'}")
    print(f"  Login Status:   {'OK' if result['login_status'] else 'FAIL'}")

    if result["errors"]:
        print("\n  Errors:")
        for err in result["errors"]:
            print(f"    - {err}")

    if all([result["chrome_cdp"], result["websocket"], result["login_status"]]):
        print("\n[OK] All checks passed!")
    else:
        print("\n[FAIL] Some checks failed. Run 'setup' to fix.")


def cmd_crawl(args):
    """执行采集任务。"""
    from src.services.crawl_service import CrawlService
    from src.models.database import SessionLocal
    from src.utils.city_codes import get_city_code

    # 验证城市
    city_code = get_city_code(args.city)
    if not city_code:
        print(f"[FAIL] Unknown city: {args.city}")
        print("Use 'cities' command to see supported cities.")
        return

    # 构建筛选条件
    filters = {}
    if args.scale:
        filters["scale"] = args.scale
    if args.salary:
        filters["salary"] = args.salary
    if args.experience:
        filters["experience"] = args.experience
    if args.degree:
        filters["degree"] = args.degree

    service = CrawlService()

    # 尝试连接数据库（可选）
    db = None
    try:
        # 先确保表已创建
        init_db()
        db = SessionLocal()
        # 测试连接
        from sqlalchemy import text
        db.execute(text("SELECT 1"))
        print("[DB] Database connected.")
    except Exception as e:
        print(f"[DB] Database not available: {e}")
        print("[DB] Data will be saved to files only.")
        db = None

    result = service.crawl(
        keyword=args.keyword,
        city=args.city,
        pages=args.pages,
        fetch_detail=not args.no_detail,
        filters=filters if filters else None,
        output_format=args.format,
        db_session=db,
    )

    if result.get("success"):
        print(f"\n[OK] Crawl complete! Total: {result['total_jobs']} jobs")
    else:
        print(f"\n[FAIL] Crawl failed: {result.get('error')}")

    if db:
        db.close()


def cmd_cities(args):
    """列出支持的城市。"""
    from src.utils.city_codes import list_cities_with_codes

    cities = list_cities_with_codes(args.keyword)
    if not cities:
        print("No cities found.")
        return

    print(f"Found {len(cities)} cities:")
    for c in cities:
        print(f"  {c['city']:8s}  (code: {c['code']})")


def main():
    """CLI 入口。"""
    parser = argparse.ArgumentParser(
        description="BOSS直聘数据采集系统",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python -m src.main serve                          # Start API server
  python -m src.main setup                          # Setup Chrome and login
  python -m src.main check                          # Check environment
  python -m src.main crawl --keyword "AI Agent" --city 上海 --pages 3
  python -m src.main cities --keyword 江
        """,
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # serve
    p_serve = subparsers.add_parser("serve", help="Start API server")

    # setup
    p_setup = subparsers.add_parser("setup", help="Setup Chrome and login")
    p_setup.add_argument(
        "--login-timeout", type=int, default=300,
        help="Login timeout in seconds (default: 300)",
    )

    # check
    p_check = subparsers.add_parser("check", help="Check environment")

    # crawl
    p_crawl = subparsers.add_parser("crawl", help="Execute crawl task")
    p_crawl.add_argument("--keyword", default="AI Agent", help="Search keyword")
    p_crawl.add_argument("--city", default="上海", help="City name (Chinese)")
    p_crawl.add_argument("--pages", type=int, default=3, help="Pages to crawl (max 10)")
    p_crawl.add_argument("--format", choices=["json", "csv"], default="json")
    p_crawl.add_argument("--no-detail", action="store_true", help="Skip detail page")
    p_crawl.add_argument("--scale", help="Company scale filter")
    p_crawl.add_argument("--salary", help="Salary range filter")
    p_crawl.add_argument("--experience", help="Experience filter")
    p_crawl.add_argument("--degree", help="Degree filter")

    # cities
    p_cities = subparsers.add_parser("cities", help="List supported cities")
    p_cities.add_argument("--keyword", default="", help="Filter by keyword")

    args = parser.parse_args()

    if args.command == "serve":
        cmd_serve(args)
    elif args.command == "setup":
        cmd_setup(args)
    elif args.command == "check":
        cmd_check(args)
    elif args.command == "crawl":
        cmd_crawl(args)
    elif args.command == "cities":
        cmd_cities(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
