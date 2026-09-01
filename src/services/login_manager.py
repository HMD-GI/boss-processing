"""
登录状态管理器

用于爬虫线程与 API 路由之间的线程间通信：
- 爬虫线程检测到未登录/风控时，通过 LoginManager 通知前端需要登录
- 前端用户完成登录后，通过 API 调用通知 LoginManager 解除阻塞
- 爬虫线程继续执行

线程安全设计：
- 使用 threading.Event 实现阻塞等待
- 使用 threading.Lock 保护共享状态
- 每个会话（session_id）独立管理，互不干扰
"""

import threading
import time
from typing import Optional, Dict


class LoginSession:
    """单个登录会话"""

    def __init__(self, session_id: str, reason: str = ""):
        self.session_id = session_id
        self.reason = reason
        self._event = threading.Event()
        self._confirmed = False
        self._cancelled = False
        self._created_at = time.time()

    def wait(self, timeout: float = 300) -> bool:
        """阻塞等待用户完成登录，返回 True 表示已确认"""
        return self._event.wait(timeout=timeout)

    def confirm(self):
        """用户已完成登录"""
        self._confirmed = True
        self._event.set()

    def cancel(self):
        """用户取消登录"""
        self._cancelled = True
        self._event.set()

    @property
    def is_confirmed(self) -> bool:
        return self._confirmed

    @property
    def is_cancelled(self) -> bool:
        return self._cancelled

    @property
    def is_done(self) -> bool:
        return self._confirmed or self._cancelled

    @property
    def elapsed(self) -> float:
        return time.time() - self._created_at


class LoginManager:
    """
    全局登录状态管理器（单例模式）

    管理所有活跃的登录会话，协调爬虫线程与 API 请求。
    """

    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._sessions: Dict[str, LoginSession] = {}
                    cls._instance._sessions_lock = threading.Lock()
        return cls._instance

    def create_session(self, reason: str = "") -> str:
        """创建一个新的登录会话，返回 session_id"""
        import uuid
        session_id = str(uuid.uuid4())[:8]
        session = LoginSession(session_id, reason)
        with self._sessions_lock:
            self._sessions[session_id] = session
        return session_id

    def wait_for_login(self, session_id: str, timeout: float = 300) -> bool:
        """
        阻塞等待用户完成登录。

        返回:
            True 表示用户已确认登录
            False 表示超时或取消
        """
        with self._sessions_lock:
            session = self._sessions.get(session_id)
        if session is None:
            return False
        result = session.wait(timeout=timeout)
        # 清理会话
        with self._sessions_lock:
            self._sessions.pop(session_id, None)
        return result and session.is_confirmed

    def confirm_login(self, session_id: str) -> bool:
        """用户确认已完成登录"""
        with self._sessions_lock:
            session = self._sessions.get(session_id)
        if session is None:
            return False
        session.confirm()
        return True

    def cancel_login(self, session_id: str) -> bool:
        """用户取消登录"""
        with self._sessions_lock:
            session = self._sessions.get(session_id)
        if session is None:
            return False
        session.cancel()
        return True

    def get_session(self, session_id: str) -> Optional[LoginSession]:
        """获取会话信息"""
        with self._sessions_lock:
            return self._sessions.get(session_id)

    def cleanup_expired(self, max_age: float = 600):
        """清理过期的会话"""
        with self._sessions_lock:
            expired = [
                sid for sid, session in self._sessions.items()
                if session.elapsed > max_age and not session.is_done
            ]
            for sid in expired:
                self._sessions.pop(sid, None)
