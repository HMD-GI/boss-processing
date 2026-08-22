"""Test FastAPI app startup and endpoints."""
import sys
sys.path.insert(0, '.')

import os
import tempfile

_db_file = os.path.join(tempfile.gettempdir(), "boss_app_test.db")
if os.path.exists(_db_file):
    os.remove(_db_file)
os.environ["DB_URL"] = f"sqlite:///{_db_file}"

from fastapi.testclient import TestClient
from src.main import create_app
from src.models.database import init_db

app = create_app()

# Manually init DB (simulates startup event)
init_db()

# Use TestClient with context manager to trigger startup/shutdown
with TestClient(app) as client:
    # Test root
    print("=== Root ===")
    r = client.get("/")
    print(f"Status: {r.status_code}")
    print(f"Name: {r.json()['name']}")

    # Test jobs (empty)
    print("\n=== Jobs (empty) ===")
    r = client.get("/api/jobs")
    print(f"Status: {r.status_code}")
    print(f"Total: {r.json()['total']}")

    # Test stats (empty)
    print("\n=== Stats (empty) ===")
    r = client.get("/api/stats")
    print(f"Status: {r.status_code}")
    print(f"Total: {r.json()['total_jobs']}")

    # Test cities/all
    print("\n=== Cities All ===")
    r = client.get("/api/cities/all")
    print(f"Status: {r.status_code}")
    print(f"Count: {len(r.json()['cities'])}")

    # Test crawl/status
    print("\n=== Crawl Status ===")
    r = client.get("/api/crawl/status")
    print(f"Status: {r.status_code}")
    print(f"Logs: {len(r.json()['recent_logs'])}")

    # Test docs
    print("\n=== Docs ===")
    r = client.get("/docs")
    print(f"Status: {r.status_code}")

print("\n=== FastAPI App Test Passed! ===")

# Cleanup
try:
    os.remove(_db_file)
except PermissionError:
    pass
