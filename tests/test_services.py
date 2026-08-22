"""Test service layer with SQLite in-memory database."""
import sys
sys.path.insert(0, '.')

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.models.job import Base, Job, CrawlLog
from src.services.job_service import JobService
from src.services.crawl_service import CrawlService

# Use SQLite for testing
engine = create_engine("sqlite:///:memory:", echo=False)
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)
db = Session()

# Insert test data
test_jobs = [
    Job(job_id="j1", job_name="AI Engineer", salary_desc="30-60K", city="Shanghai",
        company_name="ByteDance", experience="3-5 years", education="Master"),
    Job(job_id="j2", job_name="Frontend Dev", salary_desc="20-40K", city="Beijing",
        company_name="Alibaba", experience="1-3 years", education="Bachelor"),
    Job(job_id="j3", job_name="AI Researcher", salary_desc="40-80K", city="Shanghai",
        company_name="ByteDance", experience="5+ years", education="PhD"),
    Job(job_id="j4", job_name="Backend Dev", salary_desc="25-45K", city="Shenzhen",
        company_name="Tencent", experience="3-5 years", education="Bachelor"),
]
for j in test_jobs:
    db.add(j)
db.commit()

# Test list_jobs
result = JobService.list_jobs(db, page=1, page_size=10)
print(f"Total jobs: {result['total']}")
print(f"Data count: {len(result['data'])}")

# Test list_jobs with keyword filter
result = JobService.list_jobs(db, keyword="AI")
print(f"AI jobs: {result['total']}")

# Test list_jobs with city filter
result = JobService.list_jobs(db, city="Shanghai")
print(f"Shanghai jobs: {result['total']}")

# Test get_job_detail
detail = JobService.get_job_detail(db, "j1")
print(f"Detail: {detail['job_name']} - {detail['salary_desc']}")

# Test get_stats
stats = JobService.get_stats(db)
print(f"Stats - total: {stats['total_jobs']}")
print(f"Stats - cities: {stats['city_distribution']}")
print(f"Stats - companies: {stats['top_companies']}")

# Test get_cities
cities = JobService.get_cities(db)
print(f"Cities: {cities}")

# Test CrawlService._save_to_db (static method)
new_jobs = [
    {"job_id": "j5", "job_name": "Data Scientist", "salary_desc": "35-70K",
     "city": "Hangzhou", "company_name": "Alibaba", "experience": "3-5 years"}
]
CrawlService._save_to_db(db, new_jobs)
count = db.query(Job).count()
print(f"After save: {count} jobs in DB")

# Test duplicate (update existing)
update_jobs = [
    {"job_id": "j1", "job_name": "Senior AI Engineer", "salary_desc": "50-100K",
     "city": "Shanghai", "company_name": "ByteDance"}
]
CrawlService._save_to_db(db, update_jobs)
j1 = db.query(Job).filter(Job.job_id == "j1").first()
print(f"Updated j1: {j1.job_name} - {j1.salary_desc}")

db.close()
print("Services OK")
