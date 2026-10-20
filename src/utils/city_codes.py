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
# 注意：以下均为 BOSS 直聘官方城市代码（来自 /wapi/zpgeek/common/data/city.json），
# 全量码表见 data/city_codes.json。请勿手写"推测码"，否则会导致搜索返回空列表。
_DEFAULT_CITY_CODES = {
    "北京": "101010100",
    "上海": "101020100",
    "广州": "101280100",
    "深圳": "101280600",
    "杭州": "101210100",
    "成都": "101270100",
    "南京": "101190100",
    "武汉": "101200100",
    "西安": "101110100",
    "苏州": "101190400",
    "厦门": "101230200",
    "长沙": "101250100",
    "重庆": "101040100",
    "青岛": "101120200",
    "大连": "101070200",
    "宁波": "101210400",
    "济南": "101120100",
    "哈尔滨": "101050100",
    "沈阳": "101070100",
    "石家庄": "101090100",
    "太原": "101100100",
    "兰州": "101160100",
    "昆明": "101290100",
    "贵阳": "101260100",
    "南昌": "101240100",
    "福州": "101230100",
    "合肥": "101220100",
    "郑州": "101180100",
    "南宁": "101300100",
    "海口": "101310100",
    "三亚": "101310200",
    "拉萨": "101140100",
    "银川": "101170100",
    "西宁": "101150100",
    "乌鲁木齐": "101130100",
    "呼和浩特": "101080100",
    "天津": "101030100",
    "无锡": "101190200",
    "温州": "101210700",
    "佛山": "101280800",
    "东莞": "101281600",
    "珠海": "101280700",
    "中山": "101281700",
    "惠州": "101280300",
    "嘉兴": "101210300",
    "常州": "101191100",
    "绍兴": "101210500",
    "烟台": "101120500",
    "潍坊": "101120600",
    "保定": "101090200",
    "洛阳": "101180900",
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
