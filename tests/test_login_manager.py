"""
LoginManager 单元测试

验证登录状态管理器的核心功能：
- 创建会话
- 等待登录（阻塞/超时）
- 确认登录
- 取消登录
"""

import time
import threading
import pytest

from src.services.login_manager import LoginManager, LoginSession


class TestLoginSession:
    """LoginSession 测试"""

    def test_create_session(self):
        session = LoginSession("test-1", "登录失效")
        assert session.session_id == "test-1"
        assert session.reason == "登录失效"
        assert not session.is_confirmed
        assert not session.is_cancelled
        assert not session.is_done

    def test_confirm_session(self):
        session = LoginSession("test-2")
        session.confirm()
        assert session.is_confirmed
        assert session.is_done
        assert not session.is_cancelled

    def test_cancel_session(self):
        session = LoginSession("test-3")
        session.cancel()
        assert session.is_cancelled
        assert session.is_done
        assert not session.is_confirmed

    def test_wait_timeout(self):
        session = LoginSession("test-4")
        # 0.1 秒超时
        result = session.wait(timeout=0.1)
        assert result is False
        assert not session.is_done

    def test_wait_confirmed(self):
        session = LoginSession("test-5")

        def _confirm_after_delay():
            time.sleep(0.1)
            session.confirm()

        t = threading.Thread(target=_confirm_after_delay)
        t.start()
        result = session.wait(timeout=2)
        t.join()
        assert result is True
        assert session.is_confirmed


class TestLoginManager:
    """LoginManager 单例测试"""

    def test_singleton(self):
        m1 = LoginManager()
        m2 = LoginManager()
        assert m1 is m2

    def test_create_and_confirm(self):
        manager = LoginManager()
        session_id = manager.create_session(reason="测试登录")
        assert session_id is not None

        # 在另一个线程中确认
        def _confirm():
            time.sleep(0.1)
            manager.confirm_login(session_id)

        t = threading.Thread(target=_confirm)
        t.start()
        result = manager.wait_for_login(session_id, timeout=2)
        t.join()
        assert result is True

    def test_create_and_cancel(self):
        manager = LoginManager()
        session_id = manager.create_session(reason="测试取消")

        def _cancel():
            time.sleep(0.1)
            manager.cancel_login(session_id)

        t = threading.Thread(target=_cancel)
        t.start()
        result = manager.wait_for_login(session_id, timeout=2)
        t.join()
        assert result is False  # 取消不算成功

    def test_wait_timeout_no_confirm(self):
        manager = LoginManager()
        session_id = manager.create_session(reason="测试超时")
        result = manager.wait_for_login(session_id, timeout=0.2)
        assert result is False

    def test_confirm_nonexistent_session(self):
        manager = LoginManager()
        result = manager.confirm_login("nonexistent-id")
        assert result is False

    def test_cancel_nonexistent_session(self):
        manager = LoginManager()
        result = manager.cancel_login("nonexistent-id")
        assert result is False

    def test_get_session(self):
        manager = LoginManager()
        session_id = manager.create_session(reason="测试获取")
        session = manager.get_session(session_id)
        assert session is not None
        assert session.reason == "测试获取"

    def test_cleanup_after_wait(self):
        manager = LoginManager()
        session_id = manager.create_session(reason="测试清理")
        manager.confirm_login(session_id)
        manager.wait_for_login(session_id, timeout=1)
        # 等待完成后会话应被清理
        session = manager.get_session(session_id)
        assert session is None
