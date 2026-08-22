"""
反检测策略测试
"""

import sys
sys.path.insert(0, '.')

import pytest
from src.crawler.anti_detect import (
    check_risk_control, get_safe_page_count, random_delay, batch_sleep,
)
from src.config import settings


class TestAntiDetect:
    """反检测策略测试"""

    def test_check_risk_control_code_31(self):
        """测试风控码 31 检测"""
        assert check_risk_control({"code": 31, "message": "环境异常"}) is True

    def test_check_risk_control_code_37(self):
        """测试风控码 37 检测"""
        assert check_risk_control({"code": 37, "message": "访问频繁"}) is True

    def test_check_risk_control_normal(self):
        """测试正常响应"""
        assert check_risk_control({"code": 0, "message": "ok"}) is False

    def test_check_risk_control_empty(self):
        """测试空响应"""
        assert check_risk_control(None) is False
        assert check_risk_control({}) is False

    def test_check_risk_control_message_keyword(self):
        """测试消息关键字兜底识别"""
        assert check_risk_control(
            {"code": 99, "message": "检测到环境存在异常"}
        ) is True
        assert check_risk_control(
            {"code": 99, "message": "请进行安全校验"}
        ) is True

    def test_get_safe_page_count_within_limit(self):
        """测试页数在限制内"""
        assert get_safe_page_count(5) == 5
        assert get_safe_page_count(10) == 10

    def test_get_safe_page_count_over_limit(self):
        """测试页数超过限制"""
        assert get_safe_page_count(15) == settings.MAX_PAGES
        assert get_safe_page_count(100) == settings.MAX_PAGES

    def test_random_delay(self):
        """测试随机延时（极短延时）"""
        delay = random_delay((0.01, 0.02), label="test")
        assert 0.01 <= delay <= 0.02

    def test_batch_sleep_triggers(self):
        """测试批量休眠触发"""
        # 75 的倍数应该触发
        result = batch_sleep(75, batch_size=75, batch_delay_range=(0.01, 0.02))
        assert result is True

    def test_batch_sleep_not_triggers(self):
        """测试批量休眠不触发"""
        result = batch_sleep(30, batch_size=75, batch_delay_range=(0.01, 0.02))
        assert result is False


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
