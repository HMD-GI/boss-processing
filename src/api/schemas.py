"""
Pydantic 数据模型（请求/响应 Schema）

定义 API 接口的请求参数和响应数据结构。
"""

from typing import Optional, List, Any
from pydantic import BaseModel, Field


class CrawlRequest(BaseModel):
    """采集任务请求"""
    keywords: List[str] = Field(..., description="搜索关键词列表")
    city: str = Field(default="上海", description="城市名（中文）")
    pages: int = Field(default=3, ge=1, le=10, description="采集页数（1-10）")
    fetch_detail: bool = Field(default=True, description="是否抓取详情页JD")
    filters: Optional[dict] = Field(default=None, description="筛选条件")


class CrawlResponse(BaseModel):
    """采集任务响应"""
    status: str
    message: str
    task_id: Optional[str] = None


class JobListItem(BaseModel):
    """职位列表项"""
    job_id: str
    job_name: str
    salary_desc: Optional[str] = None
    city: Optional[str] = None
    company_name: Optional[str] = None
    experience: Optional[str] = None
    education: Optional[str] = None


class JobListResponse(BaseModel):
    """职位列表响应"""
    total: int
    page: int
    page_size: int
    data: List[dict]


class JobDetailResponse(BaseModel):
    """职位详情响应"""
    job_id: str
    job_name: str
    salary_desc: Optional[str] = None
    city: Optional[str] = None
    area: Optional[str] = None
    experience: Optional[str] = None
    education: Optional[str] = None
    job_desc: Optional[str] = None
    company_name: Optional[str] = None
    company_industry: Optional[str] = None
    company_scale: Optional[str] = None
    company_stage: Optional[str] = None
    skills: Optional[List[str]] = None
    welfare: Optional[List[str]] = None
    boss_name: Optional[str] = None
    boss_title: Optional[str] = None
    boss_active_status: Optional[str] = None
    fetch_time: Optional[str] = None


class StatsResponse(BaseModel):
    """统计响应"""
    total_jobs: int
    city_distribution: List[dict]
    top_companies: List[dict]
    experience_distribution: List[dict]


class CrawlLogItem(BaseModel):
    """采集日志项"""
    id: Optional[int] = None
    keyword: Optional[str] = None
    city: Optional[str] = None
    page: Optional[int] = None
    fetched_count: Optional[int] = None
    status: Optional[str] = None
    error_msg: Optional[str] = None
    timestamp: Optional[str] = None


class EnvironmentCheckResponse(BaseModel):
    """环境检查响应"""
    chrome_cdp: bool
    websocket: bool
    login_status: bool
    errors: List[str]
