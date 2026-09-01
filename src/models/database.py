"""
数据库连接管理模块

使用 SQLAlchemy ORM 管理 MySQL 连接。
支持连接池、自动建表、会话管理。
"""

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session

from src.config import settings


# 创建数据库引擎
# SQLite 不支持连接池参数，需要区分处理
_engine_kwargs = {
    "pool_pre_ping": True,  # 连接前检查是否存活
}
if not settings.DB_URL.startswith("sqlite"):
    _engine_kwargs["pool_size"] = settings.DB_POOL_SIZE
    _engine_kwargs["max_overflow"] = settings.DB_MAX_OVERFLOW
    _engine_kwargs["pool_recycle"] = 3600  # 连接回收时间（秒）

engine = create_engine(settings.DB_URL, **_engine_kwargs)

# 会话工厂
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)


def get_db() -> Session:
    """
    获取数据库会话（用于 FastAPI 依赖注入）。

    用法:
        @app.get("/")
        def index(db: Session = Depends(get_db)):
            ...
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db() -> None:
    """
    初始化数据库：创建所有表，并自动迁移新增列。

    在应用启动时调用。
    """
    from src.models.job import Base
    Base.metadata.create_all(bind=engine)
    _auto_migrate()


def _auto_migrate() -> None:
    """
    自动迁移：检查并添加缺失的列。

    用于在 ORM 模型新增列后，自动向已有表中添加对应列。
    """
    migrations = [
        # (表名, 列名, 列定义SQL)
        ("crawl_log", "filters_json", "JSON"),
        ("job", "detail_url", "VARCHAR(512)"),
        ("job", "keyword", "VARCHAR(64)"),
    ]

    for table_name, column_name, column_def in migrations:
        try:
            # 检查列是否已存在
            with engine.connect() as conn:
                if not settings.DB_URL.startswith("sqlite"):
                    # MySQL: 查 information_schema
                    result = conn.execute(text(
                        f"SELECT COUNT(*) FROM information_schema.columns "
                        f"WHERE table_schema = DATABASE() "
                        f"AND table_name = '{table_name}' "
                        f"AND column_name = '{column_name}'"
                    ))
                    exists = result.scalar() > 0
                else:
                    # SQLite: 用 PRAGMA table_info
                    result = conn.execute(text(f"PRAGMA table_info({table_name})"))
                    exists = any(row[1] == column_name for row in result)

                if not exists:
                    conn.execute(text(
                        f"ALTER TABLE {table_name} ADD COLUMN {column_name} {column_def}"
                    ))
                    conn.commit()
                    print(f"[MIGRATE] Added column {table_name}.{column_name}")
        except Exception as e:
            print(f"[MIGRATE] Failed to add {table_name}.{column_name}: {e}")


def check_db_connection() -> bool:
    """
    检查数据库连接是否正常。

    返回:
        True 表示连接正常
    """
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return True
    except Exception:
        return False
