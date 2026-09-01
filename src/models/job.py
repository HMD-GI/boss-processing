"""
ORM 数据模型

定义职位表和采集日志表的 SQLAlchemy 模型。
对应 MySQL 表结构：
- job: 职位信息表（job_id 唯一索引，city/salary_desc/fetch_time 普通索引）
- crawl_log: 采集日志表
"""

from sqlalchemy import (
    Column, BigInteger, String, Text, DateTime, Integer, JSON,
    Enum as SAEnum, Index,
)
from sqlalchemy.orm import declarative_base
from datetime import datetime

Base = declarative_base()


class Job(Base):
    """
    职位信息表

    存储从 BOSS直聘 采集的职位数据，按 job_id 去重。
    salary_desc 为明文薪资（如 "30-60K·15薪"），绕过字体反爬。
    """
    __tablename__ = "job"

    # BigInteger for MySQL, auto-degrade to Integer for SQLite (testing)
    id = Column(BigInteger().with_variant(Integer, "sqlite"), primary_key=True, autoincrement=True)
    job_id = Column(String(128), unique=True, nullable=False, index=True, comment="BOSS职位加密ID")
    job_name = Column(String(256), nullable=False, comment="职位名称")
    salary_desc = Column(String(64), index=True, comment="明文薪资，如 30-60K·15薪")
    city = Column(String(32), index=True, comment="工作城市")
    area = Column(String(64), comment="商区")
    experience = Column(String(32), comment="经验要求")
    education = Column(String(32), comment="学历要求")
    job_desc = Column(Text, comment="职位描述")
    company_name = Column(String(128), comment="公司名称")
    company_industry = Column(String(128), comment="公司行业")
    company_scale = Column(String(64), comment="公司规模")
    company_stage = Column(String(64), comment="融资阶段")
    skills = Column(JSON, comment="技能标签")
    welfare = Column(JSON, comment="福利标签")
    boss_name = Column(String(32), comment="招聘者姓名")
    boss_title = Column(String(64), comment="招聘者职位")
    boss_active_status = Column(String(16), comment="招聘者在线状态")
    detail_url = Column(String(512), comment="BOSS直聘岗位详情页网址")
    keyword = Column(String(64), index=True, comment="搜索关键词（用于按关键词+城市清理旧数据）")
    fetch_time = Column(DateTime, default=datetime.utcnow, index=True, comment="采集时间")

    __table_args__ = (
        Index("idx_company", "company_name"),
        {"mysql_charset": "utf8mb4", "mysql_engine": "InnoDB"},
    )

    def __repr__(self):
        return f"<Job(id={self.id}, job_name='{self.job_name}', salary='{self.salary_desc}')>"

    def to_dict(self, full: bool = False) -> dict:
        """
        转换为字典。

        参数:
            full: True 返回所有字段，False 只返回列表展示字段
        """
        d = {
            "job_id": self.job_id,
            "job_name": self.job_name,
            "salary_desc": self.salary_desc,
            "city": self.city,
            "company_name": self.company_name,
            "experience": self.experience,
            "education": self.education,
            "detail_url": self.detail_url,
            "keyword": self.keyword,
            "fetch_time": self.fetch_time.strftime("%Y-%m-%d %H:%M:%S") if self.fetch_time else None,
        }
        if full:
            d.update({
                "job_desc": self.job_desc,
                "area": self.area,
                "company_industry": self.company_industry,
                "company_scale": self.company_scale,
                "company_stage": self.company_stage,
                "skills": self.skills,
                "welfare": self.welfare,
                "boss_name": self.boss_name,
                "boss_title": self.boss_title,
                "boss_active_status": self.boss_active_status,
                "fetch_time": self.fetch_time.strftime("%Y-%m-%d %H:%M:%S") if self.fetch_time else None,
            })
        return d


class CrawlLog(Base):
    """
    采集日志表

    记录每次采集任务的关键信息，用于监控和排查。
    """
    __tablename__ = "crawl_log"

    id = Column(BigInteger().with_variant(Integer, "sqlite"), primary_key=True, autoincrement=True)
    keyword = Column(String(64), comment="搜索关键词")
    city = Column(String(32), comment="搜索城市")
    page = Column(Integer, comment="页码")
    fetched_count = Column(Integer, default=0, comment="本次获取数量")
    status = Column(
        SAEnum("success", "failed", "partial"),
        default="success",
        comment="采集状态",
    )
    error_msg = Column(Text, comment="错误信息")
    timestamp = Column(DateTime, default=datetime.utcnow, comment="记录时间")
    # 存储筛选条件 JSON，用于 AI 助手精确匹配当天爬取记录
    filters_json = Column(JSON, comment="筛选条件JSON(scale/salary/experience/degree)")

    __table_args__ = (
        {"mysql_charset": "utf8mb4", "mysql_engine": "InnoDB"},
    )

    def __repr__(self):
        return f"<CrawlLog(id={self.id}, keyword='{self.keyword}', status='{self.status}')>"

    def to_dict(self) -> dict:
        """转换为字典。"""
        return {
            "id": self.id,
            "keyword": self.keyword,
            "city": self.city,
            "page": self.page,
            "fetched_count": self.fetched_count,
            "status": self.status,
            "error_msg": self.error_msg,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
            "filters_json": self.filters_json,
        }
