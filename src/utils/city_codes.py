"""
城市码管理模块

管理BOSS直聘的城市代码映射表。
首次使用时会从 data/city_codes.json 加载，支持按中文名或代码查询。
"""

import json
from pathlib import Path
from typing import Optional

from src.config import settings


# 预置常用城市码（主城市）
_DEFAULT_CITY_CODES = {
    "北京": "101010100",
    "上海": "101020100",
    "深圳": "101280100",
    "广州": "101280101",
    "杭州": "101210101",
    "成都": "101270101",
    "南京": "101190101",
    "武汉": "101200101",
    "西安": "101110101",
    "苏州": "101190401",
    "厦门": "101230201",
    "长沙": "101250101",
    "重庆": "101040100",
    "青岛": "101120201",
    "大连": "101070201",
    "宁波": "101210401",
    "济南": "101120101",
    "哈尔滨": "101050101",
    "沈阳": "101070101",
    "石家庄": "101090101",
    "太原": "101100101",
    "兰州": "101160101",
    "昆明": "101290101",
    "贵阳": "101260101",
    "南昌": "101240101",
    "福州": "101230101",
    "合肥": "101220101",
    "郑州": "101180101",
    "南宁": "101300101",
    "海口": "101310101",
    "三亚": "101310201",
    "拉萨": "101140101",
    "银川": "101170101",
    "西宁": "101150101",
    "乌鲁木齐": "101130101",
    "呼和浩特": "101080101",
    "天津": "101030100",
    "无锡": "101190201",
    "温州": "101210701",
    "佛山": "101280800",
    "东莞": "101281600",
    "珠海": "101280701",
    "中山": "101281701",
    "惠州": "101280301",
    "嘉兴": "101210301",
    "常州": "101191101",
    "绍兴": "101210501",
    "烟台": "101120501",
    "潍坊": "101120601",
    "保定": "101090201",
    "洛阳": "101180901",
}

# 代码 -> 城市名 的反向映射
_DEFAULT_CODE_TO_CITY = {v: k for k, v in _DEFAULT_CITY_CODES.items()}


def _load_city_codes() -> dict:
    """
    从 data/city_codes.json 加载城市码表。
    如果文件不存在，使用内置的预置码表。
    """
    filepath = settings.CITY_CODES_FILE
    if filepath.exists():
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            pass
    return _DEFAULT_CITY_CODES


def get_city_code(city_name: str) -> Optional[str]:
    """
    根据城市中文名获取城市代码。

    参数:
        city_name: 城市中文名，如 "上海"

    返回:
        城市代码字符串，如 "101020100"；未找到返回 None
    """
    codes = _load_city_codes()
    return codes.get(city_name)


def get_city_name(code: str) -> Optional[str]:
    """
    根据城市代码获取城市中文名。
    """
    codes = _load_city_codes()
    reverse = {v: k for k, v in codes.items()}
    return reverse.get(code)


def list_cities(keyword: str = "") -> list:
    """
    列出所有支持的城市，可选按关键词过滤。

    参数:
        keyword: 过滤关键词，如 "江" 会返回含"江"的城市

    返回:
        城市名列表
    """
    codes = _load_city_codes()
    cities = sorted(codes.keys())
    if keyword:
        cities = [c for c in cities if keyword in c]
    return cities


def list_cities_with_codes(keyword: str = "") -> list:
    """
    列出所有支持的城市及对应代码，可选按关键词过滤。

    返回:
        [{"city": "上海", "code": "101020100"}, ...]
    """
    codes = _load_city_codes()
    result = [{"city": c, "code": codes[c]} for c in sorted(codes.keys())]
    if keyword:
        result = [r for r in result if keyword in r["city"]]
    return result
