# -*- coding: utf-8 -*-
"""
从 BOSS 直聘官方接口抓取全量城市码表，生成 data/city_codes.json。

用法: python -m tools.generate_city_codes
输出: data/city_codes.json  (格式: {"城市名": "城市代码", ...})
"""
import json
import sys
import urllib.request
from collections import Counter
from pathlib import Path

sys.path.insert(0, r"e:\BaiduNetdiskDownload\job_review\boss_processing")

URL = "https://www.zhipin.com/wapi/zpgeek/common/data/city.json"
OUT_PATH = Path(r"e:\BaiduNetdiskDownload\job_review\boss_processing\data\city_codes.json")

# 需要修正的内置表城市（保持原有 51 城，对齐官方正确码）
TARGET_CITIES = [
    "北京", "上海", "广州", "深圳", "杭州", "成都", "南京", "武汉", "西安", "苏州",
    "厦门", "长沙", "重庆", "青岛", "大连", "宁波", "济南", "哈尔滨", "沈阳", "石家庄",
    "太原", "兰州", "昆明", "贵阳", "南昌", "福州", "合肥", "郑州", "南宁", "海口",
    "三亚", "拉萨", "银川", "西宁", "乌鲁木齐", "呼和浩特", "天津", "无锡", "温州",
    "佛山", "东莞", "珠海", "中山", "惠州", "嘉兴", "常州", "绍兴", "烟台", "潍坊",
    "保定", "洛阳",
]


def fetch_official():
    req = urllib.request.Request(
        URL,
        headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                               "AppleWebKit/537.36 Chrome/120.0 Safari/537.36"},
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        data = json.loads(resp.read().decode("utf-8"))
    if data.get("code") != 0:
        raise RuntimeError(f"官方接口返回异常: {data.get('message')}")
    return data["zpData"]


def main():
    provinces = fetch_official()
    mapping = {}
    for prov in provinces:
        for city in prov.get("subLevelModelList") or []:
            name = city.get("name")
            code = str(city.get("code"))
            if name and code:
                mapping[name] = code

    print(f"官方共 {len(mapping)} 个城市（去重后）")

    # 检查重名冲突
    dup = {k: v for k, v in Counter(mapping.keys()).items() if v > 1}
    if dup:
        print(f"[WARN] 存在同名城市: {dup}")

    # 校验内置表城市都能匹配
    missing = [c for c in TARGET_CITIES if c not in mapping]
    if missing:
        print(f"[ERROR] 内置表城市在官方数据中缺失: {missing}")
        sys.exit(1)

    # 输出内置表所需城市码（用于更新 city_codes.py）
    print("\n内置表 51 城官方正确码：")
    for c in TARGET_CITIES:
        print(f'    "{c}": "{mapping[c]}",')

    # 写入 data/city_codes.json
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(
        json.dumps(mapping, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print(f"\n✅ 已生成 {OUT_PATH}（{len(mapping)} 个城市）")


if __name__ == "__main__":
    main()