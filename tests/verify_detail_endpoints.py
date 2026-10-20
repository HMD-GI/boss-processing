# -*- coding: utf-8 -*-
"""端到端验证 detail-url / refresh-url 端点行为（使用真实 MySQL 数据）。"""
import sys
import pymysql
from fastapi.testclient import TestClient

sys.path.insert(0, r"e:\BaiduNetdiskDownload\job_review\boss_processing")
from src.main import app  # noqa: E402

conn = pymysql.connect(host="localhost", user="root", password="root",
                       database="boss_db", charset="utf8mb4")
cur = conn.cursor()
cur.execute("SELECT job_id FROM job WHERE detail_url != '' LIMIT 1")
row = cur.fetchone()
conn.close()

if not row:
    print("数据库无数据")
    sys.exit(1)
job_id = row[0]
print("测试 job_id:", job_id)

with TestClient(app) as client:
    # 1. 获取 detail-url
    r1 = client.get(f"/api/jobs/{job_id}/detail-url")
    print("\n[GET detail-url]", r1.status_code)
    d1 = r1.json()
    print("  detail_url :", d1.get("detail_url"))
    print("  need_refresh:", d1.get("need_refresh"))
    print("  message    :", d1.get("message"))
    assert d1.get("need_refresh") is False, "need_refresh 必须为 False"
    assert "/job_detail/" in (d1.get("detail_url") or ""), \
        "detail_url 必须是 /job_detail/ 新格式"
    print("  [PASS] detail-url 返回新格式且无需刷新")

    # 2. 刷新 refresh-url
    r2 = client.post(f"/api/jobs/{job_id}/refresh-url")
    print("\n[POST refresh-url]", r2.status_code)
    d2 = r2.json()
    print("  detail_url :", d2.get("detail_url"))
    print("  fresh      :", d2.get("fresh"))
    assert d2.get("fresh") is True, "fresh 必须为 True"
    assert "/job_detail/" in (d2.get("detail_url") or ""), \
        "刷新后必须是新格式"
    print("  [PASS] refresh-url 返回新格式")

    # 3. 列表接口 detail_url 展示验证
    r3 = client.get("/api/jobs", params={"page": 1, "page_size": 3})
    d3 = r3.json()
    print("\n[GET jobs] 列表前3条 detail_url:")
    for j in (d3.get("data") or [])[:3]:
        print("  ", j.get("detail_url"))
        assert "/job_detail/" in (j.get("detail_url") or ""), \
            "列表返回的 detail_url 必须是新格式"
    print("  [PASS] 列表接口 detail_url 均为新格式")

print("\n===== 全部通过 =====")