"""
CDP 连接器测试

测试 CDPConnector 类的初始化和路径检测逻辑。
不测试实际 Chrome 连接（需要 Chrome 运行）。
"""

import sys
sys.path.insert(0, '.')

import pytest
from src.crawler.cdp_connector import CDPConnector


class TestCDPConnector:
    """CDPConnector 单元测试"""

    def test_init_default_port(self):
        """测试默认端口初始化"""
        conn = CDPConnector()
        assert conn.port == 9222
        assert conn.ws is None
        assert conn.target_id is None
        assert conn.msg_id == 0

    def test_init_custom_port(self):
        """测试自定义端口初始化"""
        conn = CDPConnector(port=9333)
        assert conn.port == 9333

    def test_detect_chrome_path(self):
        """测试 Chrome 路径自动检测"""
        # _detect_chrome_path 是静态方法，应返回一个路径或抛出异常
        try:
            path = CDPConnector._detect_chrome_path()
            assert isinstance(path, str)
            assert len(path) > 0
        except FileNotFoundError:
            # 如果没有 Chrome 也算正常（测试环境可能没有）
            pass

    def test_is_chrome_running_no_chrome(self):
        """测试未启动 Chrome 时的状态检查"""
        conn = CDPConnector(port=19999)  # 使用一个不太可能被占用的端口
        assert conn.is_chrome_running() is False


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
