"""Test API layer with FastAPI TestClient and SQLite file-based database."""
import sys
sys.path.insert(0, '.')

import os
import tempfile

# Use a temp file-based SQLite for testing (in-memory is per-connection)
_db_file = os.path.join(tempfile.gettempdir(), "boss_test.db")
if os.path.exists(_db_file):
    os.remove(_db_file)
os.environ["DB_URL"] = f"sqlite:///{_db_file}"

from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.models.job import Base, Job
from src.models import database
from src.api.routes import router

# Create tables
Base.metadata.create_all(database.engine)

# Insert test data
db = database.SessionLocal()
db.add(Job(job_id="j1", job_name="AI Engineer", salary_desc="30-60K",
           city="Shanghai", company_name="ByteDance"))
db.add(Job(job_id="j2", job_name="Frontend Dev", salary_desc="20-40K",
           city="Beijing", company_name="Alibaba"))
db.commit()
db.close()

# Create app
app = FastAPI()
app.include_router(router)
client = TestClient(app)

# Test 1: GET /api/jobs
print("=== Test GET /api/jobs ===")
resp = client.get("/api/jobs")
print(f"Status: {resp.status_code}")
data = resp.json()
print(f"Total: {data['total']}, Data count: {len(data['data'])}")
assert resp.status_code == 200
assert data["total"] == 2

# Test 2: GET /api/jobs with keyword filter
print("\n=== Test GET /api/jobs?keyword=AI ===")
resp = client.get("/api/jobs", params={"keyword": "AI"})
data = resp.json()
print(f"Total: {data['total']}")
assert resp.status_code == 200
assert data["total"] == 1

# Test 3: GET /api/jobs/{job_id}
print("\n=== Test GET /api/jobs/j1 ===")
resp = client.get("/api/jobs/j1")
print(f"Status: {resp.status_code}")
data = resp.json()
print(f"Job: {data['job_name']} - {data['salary_desc']}")
assert resp.status_code == 200
assert data["job_name"] == "AI Engineer"

# Test 4: GET /api/jobs/{job_id} - not found
print("\n=== Test GET /api/jobs/notexist ===")
resp = client.get("/api/jobs/notexist")
print(f"Status: {resp.status_code}")
assert resp.status_code == 404

# Test 5: GET /api/stats
print("\n=== Test GET /api/stats ===")
resp = client.get("/api/stats")
data = resp.json()
print(f"Total jobs: {data['total_jobs']}")
print(f"City dist: {data['city_distribution']}")
assert resp.status_code == 200
assert data["total_jobs"] == 2

# Test 6: GET /api/cities
print("\n=== Test GET /api/cities ===")
resp = client.get("/api/cities")
data = resp.json()
print(f"Cities: {data['cities']}")
assert resp.status_code == 200
assert "Shanghai" in data["cities"]

# Test 7: GET /api/cities/all
print("\n=== Test GET /api/cities/all ===")
resp = client.get("/api/cities/all")
data = resp.json()
print(f"Total cities: {len(data['cities'])}")
assert resp.status_code == 200
assert len(data["cities"]) > 0

# Test 8: GET /api/crawl/status
print("\n=== Test GET /api/crawl/status ===")
resp = client.get("/api/crawl/status")
data = resp.json()
print(f"Logs count: {len(data['recent_logs'])}")
assert resp.status_code == 200

# Cleanup (ignore errors on Windows due to file locking)
try:
    os.remove(_db_file)
except PermissionError:
    pass

print("\n=== All API tests passed! ===")
