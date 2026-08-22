"""
BOSS直聘数据采集系统 - 全局配置

通过环境变量或默认值管理所有配置项。
支持 .env 文件加载。
"""

import os
from pathlib import Path

# 尝试加载 .env 文件
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass


# ========== 路径配置 ==========

# 项目根目录
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# 数据目录
DATA_DIR = BASE_DIR / "data"

# 城市码表文件
CITY_CODES_FILE = DATA_DIR / "city_codes.json"

# Chrome 隔离 profile 目录（持久化登录态）
CHROME_PROFILE_DIR = Path(
    os.getenv("CHROME_PROFILE_DIR", "~/.boss-zhipin-scraper/chrome-profile")
).expanduser()

# 采集结果输出目录
JOB_RESULT_DIR = Path(
    os.getenv("JOB_RESULT_DIR", "~/.boss-zhipin-scraper/job-result")
).expanduser()


# ========== Chrome CDP 配置 ==========

# CDP 调试端口
CDP_PORT = int(os.getenv("CDP_PORT", "9222"))

# Chrome 可执行文件路径（留空则自动检测）
CHROME_PATH = os.getenv("CHROME_PATH", "")

# 登录等待超时（秒）
LOGIN_TIMEOUT = int(os.getenv("LOGIN_TIMEOUT", "300"))


# ========== 数据库配置 ==========

# MySQL 8.0 连接URL
# 格式: mysql+pymysql://user:password@host:port/database?charset=utf8mb4
# 优先读取 MYSQL_URL，兼容旧版 DB_URL
DB_URL = os.getenv(
    "MYSQL_URL",
    os.getenv(
        "DB_URL",
        "mysql+pymysql://root:root@localhost:3306/boss_db?charset=utf8mb4",
    ),
)

# 数据库连接池大小
DB_POOL_SIZE = int(os.getenv("DB_POOL_SIZE", "10"))
DB_MAX_OVERFLOW = int(os.getenv("DB_MAX_OVERFLOW", "20"))

# Redis 连接URL
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")

# MongoDB 连接URL（AI助手对话记录存储）
MONGO_URL = os.getenv("MONGO_URL", "mongodb://localhost:27017")
MONGO_DB = os.getenv("MONGO_DB", "boss_assistant")

# ========== AI 大模型配置 ==========
# 支持任何兼容 OpenAI API 格式的大模型（DeepSeek、OpenAI等）
LLM_API_KEY = os.getenv("LLM_API_KEY", "")
LLM_BASE_URL = os.getenv("LLM_BASE_URL", "https://api.deepseek.com")
LLM_MODEL = os.getenv("LLM_MODEL", "deepseek-chat")


# ========== 采集策略配置 ==========

# 单次最大采集页数（上限保护）
MAX_PAGES = 10

# 每页条数（BOSS直聘固定30）
PAGE_SIZE = 30

# 翻页随机延时范围（秒）
DELAY_RANGE = (12, 22)

# 批量休眠阈值（条数）
BATCH_SIZE = 75

# 批量休眠时间范围（秒）
BATCH_DELAY_RANGE = (30, 60)

# 详情页间延时范围（秒）
DETAIL_DELAY_RANGE = (3, 6)

# 详情页加载等待时间范围（秒）
PAGE_LOAD_DELAY = (2, 4)

# 风控码列表（遇到这些code立即停止采集）
RISK_CONTROL_CODES = {31, 37}


# ========== API 配置 ==========

# FastAPI 服务配置
API_HOST = os.getenv("API_HOST", "0.0.0.0")
API_PORT = int(os.getenv("API_PORT", "8000"))

# CORS 允许的源
CORS_ORIGINS = [
    "http://localhost",
    "http://localhost:80",
    "http://localhost:5173",  # Vite dev server
    "http://127.0.0.1:5173",
]


# ========== BOSS直聘 API 端点 ==========

# 搜索API（返回明文薪资）
SEARCH_API_PATH = "/wapi/zpgeek/search/joblist.json"

# BOSS直聘首页URL
BOSS_HOME_URL = "https://www.zhipin.com/web/geek/job-recommend"

# BOSS直聘详情页URL模板
BOSS_DETAIL_URL_TEMPLATE = (
    "https://www.zhipin.com/web/geek/job?jobId={job_id}"
    "&lid={lid}&securityId={security_id}"
)
