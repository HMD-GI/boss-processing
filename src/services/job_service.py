"""
职位查询服务模块

提供职位数据的查询、统计功能：
- 分页查询职位列表（支持多条件筛选和排序）
- 获取单条职位详情
- 数据统计（总数、城市分布、薪资分布等）
- 获取采集日志
"""

from typing import Optional, List, Dict
from sqlalchemy import desc, asc, func
from sqlalchemy.orm import Session

from src.models.job import Job, CrawlLog


class JobService:
    """
    职位查询服务

    封装所有与职位数据查询相关的数据库操作。
    """

    @staticmethod
    def list_jobs(
        db: Session,
        keyword: Optional[str] = None,
        city: Optional[str] = None,
        company: Optional[str] = None,
        page: int = 1,
        page_size: int = 20,
        sort_by: str = "fetch_time",
        sort_order: str = "desc",
    ) -> Dict:
        """
        分页查询职位列表，支持多条件筛选和排序。

        参数:
            db: 数据库会话
            keyword: 职位名称关键词（模糊匹配）
            city: 城市名（精确匹配）
            company: 公司名（模糊匹配）
            page: 页码（从1开始）
            page_size: 每页条数
            sort_by: 排序字段
            sort_order: 排序方向 asc/desc

        返回:
            {"total": int, "page": int, "page_size": int, "data": [...]}
        """
        query = db.query(Job)

        # 筛选条件
        if keyword:
            query = query.filter(Job.job_name.contains(keyword))
        if city:
            query = query.filter(Job.city == city)
        if company:
            query = query.filter(Job.company_name.contains(company))

        # 排序
        sort_column = getattr(Job, sort_by, Job.fetch_time)
        if sort_order == "desc":
            query = query.order_by(desc(sort_column))
        else:
            query = query.order_by(asc(sort_column))

        # 分页
        total = query.count()
        offset = (page - 1) * page_size
        jobs = query.offset(offset).limit(page_size).all()

        return {
            "total": total,
            "page": page,
            "page_size": page_size,
            "data": [j.to_dict() for j in jobs],
        }

    @staticmethod
    def get_job_detail(db: Session, job_id: str) -> Optional[Dict]:
        """
        获取单条职位详情。

        参数:
            db: 数据库会话
            job_id: BOSS职位加密ID

        返回:
            职位详情字典，不存在返回 None
        """
        job = db.query(Job).filter(Job.job_id == job_id).first()
        if not job:
            return None
        return job.to_dict(full=True)

    @staticmethod
    def get_stats(db: Session) -> Dict:
        """
        获取数据统计信息。

        返回:
            {
                "total_jobs": int,
                "city_distribution": [{"city": str, "count": int}],
                "top_companies": [{"company": str, "count": int}],
                "experience_distribution": [...],
            }
        """
        # 总数
        total = db.query(func.count(Job.id)).scalar() or 0

        # 城市分布
        city_dist = (
            db.query(Job.city, func.count(Job.id).label("count"))
            .filter(Job.city.isnot(None))
            .group_by(Job.city)
            .order_by(desc("count"))
            .limit(20)
            .all()
        )

        # 热门公司
        top_companies = (
            db.query(Job.company_name, func.count(Job.id).label("count"))
            .filter(Job.company_name.isnot(None))
            .group_by(Job.company_name)
            .order_by(desc("count"))
            .limit(10)
            .all()
        )

        # 经验要求分布
        exp_dist = (
            db.query(Job.experience, func.count(Job.id).label("count"))
            .filter(Job.experience.isnot(None))
            .group_by(Job.experience)
            .order_by(desc("count"))
            .all()
        )

        return {
            "total_jobs": total,
            "city_distribution": [
                {"city": c, "count": n} for c, n in city_dist if c
            ],
            "top_companies": [
                {"company": c, "count": n} for c, n in top_companies if c
            ],
            "experience_distribution": [
                {"experience": e, "count": n} for e, n in exp_dist if e
            ],
        }

    @staticmethod
    def get_crawl_logs(
        db: Session, limit: int = 20
    ) -> List[Dict]:
        """
        获取最近的采集日志。

        参数:
            db: 数据库会话
            limit: 返回条数

        返回:
            日志字典列表
        """
        logs = (
            db.query(CrawlLog)
            .order_by(desc(CrawlLog.timestamp))
            .limit(limit)
            .all()
        )
        return [log.to_dict() for log in logs]

    @staticmethod
    def get_cities(db: Session) -> List[str]:
        """
        获取数据库中有职位数据的所有城市列表。

        返回:
            城市名列表
        """
        results = (
            db.query(Job.city)
            .filter(Job.city.isnot(None), Job.city != "")
            .distinct()
            .order_by(Job.city)
            .all()
        )
        return [r[0] for r in results]
