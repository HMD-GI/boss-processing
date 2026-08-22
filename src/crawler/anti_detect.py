"""
反检测策略模块

提供随机延时、行为模拟等反爬策略工具函数。
反爬策略：
- 翻页间隔 12~22 秒随机延时
- 每采集 75 条后休眠 30~60 秒
- 单次最多 10 页（300条）上限保护
- 随机化行为，模拟真人浏览节奏
"""

import random
import time
from typing import Tuple

from src.config import settings


def random_delay(
    delay_range: Tuple[float, float] = None,
    label: str = "",
) -> float:
    """
    随机延时，模拟真人浏览节奏。

    参数:
        delay_range: 延时范围（最小, 最大），默认使用配置中的 DELAY_RANGE
        label: 日志标签（用于输出提示信息）

    返回:
        实际休眠的秒数
    """
    if delay_range is None:
        delay_range = settings.DELAY_RANGE

    delay = random.uniform(*delay_range)
    if label:
        print(f"  [WAIT] {label}: sleeping {delay:.1f}s...")
    time.sleep(delay)
    return delay


def batch_sleep(
    current_count: int,
    batch_size: int = None,
    batch_delay_range: Tuple[float, float] = None,
) -> bool:
    """
    批量休眠检查：当采集量达到阈值时执行长休眠。

    参数:
        current_count: 当前已采集总数
        batch_size: 批量阈值，默认使用配置
        batch_delay_range: 休眠时间范围，默认使用配置

    返回:
        True 表示执行了休眠，False 表示未触发
    """
    if batch_size is None:
        batch_size = settings.BATCH_SIZE
    if batch_delay_range is None:
        batch_delay_range = settings.BATCH_DELAY_RANGE

    if current_count >= batch_size and current_count % batch_size == 0:
        delay = random.uniform(*batch_delay_range)
        print(
            f"  [BATCH] {current_count} jobs collected, "
            f"sleeping {delay:.1f}s..."
        )
        time.sleep(delay)
        return True
    return False


def check_risk_control(api_response: dict) -> bool:
    """
    检测API响应是否触发风控。

    BOSS直聘的风控码：
    - code 31: 环境异常
    - code 37: 访问频繁
    - 其他风控相关消息也会被识别

    参数:
        api_response: API 返回的 JSON 数据

    返回:
        True 表示触发了风控，应停止采集
    """
    if not api_response:
        return False

    code = api_response.get("code")
    if code in settings.RISK_CONTROL_CODES:
        return True

    # 按 message 关键字兜底识别
    message = api_response.get("message", "")
    risk_keywords = ["环境存在异常", "访问频繁", "安全校验", "请求异常"]
    for keyword in risk_keywords:
        if keyword in message:
            return True

    return False


def get_safe_page_count(requested_pages: int) -> int:
    """
    安全页数检查：限制单次最大采集页数。

    参数:
        requested_pages: 用户请求的页数

    返回:
        安全的页数（不超过 MAX_PAGES）
    """
    return min(requested_pages, settings.MAX_PAGES)
