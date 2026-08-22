"""Test ORM models with SQLite in-memory database."""
import sys
sys.path.insert(0, '.')

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.models.job import Base, Job, CrawlLog

# Use SQLite for testing
engine = create_engine("sqlite:///:memory:", echo=False)
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)
db = Session()

# Test Job model
job = Job(
    job_id="test_001",
    job_name="AI Engineer",
    salary_desc="30-60K",
    city="Shanghai",
    experience="3-5 years",
    education="Bachelor",
    skills=["Python", "PyTorch"],
    welfare=["Free lunch"],
)
db.add(job)
db.commit()

# Query
result = db.query(Job).filter(Job.job_id == "test_001").first()
print("Job:", result)
print("to_dict:", result.to_dict(full=True))

# Test CrawlLog
log = CrawlLog(keyword="AI", city="Shanghai", page=1, fetched_count=30)
db.add(log)
db.commit()

logs = db.query(CrawlLog).all()
print("Logs:", logs)
print("Log dict:", logs[0].to_dict())

# Test duplicate job_id (should update)
job2 = Job(
    job_id="test_001",
    job_name="Updated Title",
    salary_desc="40-80K",
    city="Beijing",
)
existing = db.query(Job).filter(Job.job_id == "test_001").first()
if existing:
    for key, value in job2.__dict__.items():
        if key != "_sa_instance_state" and value is not None:
            setattr(existing, key, value)
    db.commit()

updated = db.query(Job).filter(Job.job_id == "test_001").first()
print("Updated job_name:", updated.job_name)
print("Updated city:", updated.city)

db.close()
print("Models OK")
