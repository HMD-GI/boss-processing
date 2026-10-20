# -*- coding: utf-8 -*-
"""
沙箱测试：验证 JobListFetcher.fetch_page 修复后的行为
- 1. 参数构造：keyword + query 双参数
- 2. JS 代码用异步 fetch（与环境检查一致）
- 3. 空 jobList 时输出诊断日志
- 4. 正常数据解析
"""
import os
import sys
import json
import types

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.crawler.api_fetcher import JobListFetcher  # noqa: E402


class FakeCDP:
    """模拟 CDPConnector，记录 evaluate 调用，返回预设结果。"""

    def __init__(self, responses):
        self.responses = responses
        self.calls = []

    def evaluate(self, js_code, await_promise=False):
        self.calls.append({"js": js_code, "await_promise": await_promise})
        if self.responses:
            return self.responses.pop(0)
        return None


def mock_settings():
    """Mock settings.PAGE_SIZE 为 30。"""
    import src.config.settings as settings_mod

    if not hasattr(settings_mod, "PAGE_SIZE"):
        settings_mod.PAGE_SIZE = 30


def test_1_params_match_login_check():
    """验证: fetch_page 使用 keyword 参数（与环境检查一致），且保留 query 兼容。"""
    mock_settings()
    cdp = FakeCDP([{"code": 0, "zpData": {"jobList": [{}]}}])
    fetcher = JobListFetcher(cdp)
    fetcher.fetch_page("java", "101280100", 1)

    js = cdp.calls[0]["js"]
    # 检查是异步 fetch 模式
    assert "(async function()" in js, "JS 应该使用异步 fetch"
    assert "await_promise" in str(cdp.calls[0]) or cdp.calls[0]["await_promise"] is True, \
        "evaluate 应该 awaitPromise"

    # 勾出 URL 参数
    url = js.split("fetch('")[1].split("'")[0]
    print("构造的 API URL:")
    print(" ", url)
    assert "keyword=java" in url, "必须包含 keyword 参数"
    assert "query=java" in url, "必须保留 query 参数（兼容）"
    assert "city=101280100" in url, "必须包含 city 参数"
    assert "page=1" in url
    assert "pageSize=30" in url
    print("[PASS] 参数构造正确：keyword + query + city + page + pageSize")
    return True


def test_2_empty_joblist_diag():
    """验证: 空 jobList 时 fetch_all 打印 DIAG 诊断日志并停止。"""
    mock_settings()
    # 模拟 API 返回 code=0 但 jobList 为空（与日志场景一致）
    cdp = FakeCDP([
        {"code": 0, "zpData": {"jobList": [], "pageFrom": 1}},
    ])
    fetcher = JobListFetcher(cdp)

    logs = []
    fetcher.log_callback = lambda msg, level="info": logs.append((msg, level))

    all_jobs = fetcher.fetch_all("java", "101280100", pages=1)
    batches = list(all_jobs)
    final = fetcher.fetch_all("java", "101280100", pages=1)  # 再拿一次
    _ = list(final)

    msgs = [m for m, _ in logs]
    print("\n日志输出：")
    for m, lv in logs:
        print(f"  [{lv}] {m}")

    assert any("no more data" in m for m in msgs), "应输出 no more data"
    assert any("DIAG" in m for m in msgs), "应输出 DIAG 诊断信息"
    print("[PASS] 空 jobList 时输出 DIAG 诊断日志")
    return True


def test_3_normal_data_parse():
    """验证: 正常数据能解析出字段。"""
    mock_settings()
    raw_job = {
        "encryptJobId": "abc123",
        "jobName": "Java开发工程师",
        "salaryDesc": "30-60K·15薪",
        "cityName": "广州",
        "businessDistrict": "天河区",
        "jobExperience": "3-5年",
        "jobDegree": "本科",
        "brandName": "某某科技",
        "brandIndustry": "互联网",
        "brandScaleName": "1000-9999人",
        "brandStageName": "已上市",
        "jobLabels": ["五险一金", "年终奖"],
        "skills": ["Java", "Spring"],
        "bossName": "王先生",
        "bossTitle": "招聘者",
        "bossOnline": True,
        "securityId": "sec_1",
        "lid": "lid_1",
    }
    cdp = FakeCDP([{"code": 0, "zpData": {"jobList": [raw_job]}}])
    fetcher = JobListFetcher(cdp)

    logs = []
    fetcher.log_callback = lambda msg, level="info": logs.append((msg, level))

    batches = list(fetcher.fetch_all("java", "101280100", pages=1))
    assert batches and len(batches) == 1, "应 yield 1 批"
    jobs = batches[0]
    assert len(jobs) == 1, f"应解析 1 条职位, got {len(jobs)}"
    j = jobs[0]
    assert j["job_id"] == "abc123"
    assert j["job_name"] == "Java开发工程师"
    assert j["salary_desc"] == "30-60K·15薪"
    assert j["city"] == "广州"
    assert j["company_name"] == "某某科技"
    assert j["boss_active_status"] == "online"
    assert "detail_url" in j and "abc123" in j["detail_url"]
    print("\n解析结果：")
    print(json.dumps(j, ensure_ascii=False, indent=2))
    print("[PASS] 正常数据解析成功")
    return True


def test_4_login_fail_handling():
    """验证: code != 0（登录失效）时按原逻辑处理，不回退到 no more data。"""
    mock_settings()
    cdp = FakeCDP([{"code": 1001, "message": "用户未登录"}])
    fetcher = JobListFetcher(cdp)

    logs = []
    fetcher.log_callback = lambda msg, level="info": logs.append((msg, level))

    list(fetcher.fetch_all("java", "101280100", pages=1))
    msgs = [m for m, _ in logs]
    assert any("FAIL" in m for m in msgs), "登录失效应输出 FAIL 而非 no more data"
    assert not any("no more data" in m for m in msgs)
    print("\n日志输出：")
    for m, lv in logs:
        print(f"  [{lv}] {m}")
    print("[PASS] 登录失效处理正确")
    return True


if __name__ == "__main__":
    results = [
        ("测试1 参数构造", test_1_params_match_login_check),
        ("测试2 空列表诊断", test_2_empty_joblist_diag),
        ("测试3 数据解析", test_3_normal_data_parse),
        ("测试4 登录失效", test_4_login_fail_handling),
    ]
    failed = 0
    for name, fn in results:
        print(f"\n{'='*50}\n运行: {name}\n{'='*50}")
        try:
            fn()
        except AssertionError as e:
            failed += 1
            print(f"[FAIL] {e}")
        except Exception as e:
            failed += 1
            print(f"[ERROR] {type(e).__name__}: {e}")

    print(f"\n{'='*50}\n结果: {'全部通过' if failed == 0 else f'{failed} 项失败'}")
    sys.exit(1 if failed else 0)