# -*- coding: utf-8 -*-
"""精确验证：项目内置城市码在 BOSS 官方码表中是否存在。"""
import json
import urllib.request
import sys

sys.path.insert(0, r"e:\BaiduNetdiskDownload\job_review\boss_processing")
from src.utils.city_codes import _DEFAULT_CITY_CODES  # noqa: E402

URL = "https://www.zhipin.com/wapi/zpgeek/common/data/city.json"
req = urllib.request.Request(
    URL,
    headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                           "AppleWebKit/537.36 Chrome/120.0 Safari/537.36"},
)
data = json.loads(urllib.request.urlopen(req, timeout=20).read().decode("utf-8"))

official_codes = {}
official_reverse = {}
for prov in data.get("zpData", []):
    for city in prov.get("subLevelModelList") or []:
        name = city.get("name")
        code = str(city.get("code"))
        if name:
            official_codes[name] = code
            official_reverse[code] = name

print("=" * 70)
print("项目内置城市码在官方表中的命中情况")
print("=" * 70)
wrong = 0
total = 0
for name, code in sorted(_DEFAULT_CITY_CODES.items()):
    total += 1
    if code in official_reverse and official_reverse[code] == name:
        status = f"✅ 正确 ({official_reverse[code]})"
    elif code in official_reverse:
        status = f"❌ 代码指向别的城市: {official_reverse[code]}"
        wrong += 1
    else:
        status = "❌ 官方表中不存在此代码"
        wrong += 1
    print(f"  {name:6s} {code:10s} {status}")

print(f"\n汇总: 共 {total} 个城市, 错误 {wrong} 个, 错误率 {wrong/total*100:.0f}%")

print("\n关键结论:")
print(f"  环境检查 city=101280100 -> 官方城市: {official_reverse.get('101280100')}")
print(f"  实际采集 city=101280101 -> 官方城市: {official_reverse.get('101280101', '!!! 不存在 !!!')}")