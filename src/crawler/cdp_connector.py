"""
Chrome DevTools Protocol (CDP) 连接管理器

核心原理：
BOSS直聘前端使用字体反爬，薪资数字通过自定义字体渲染，解析HTML会得到乱码。
但其前端代码通过内部 API /wapi/zpgeek/search/joblist.json 获取明文数据。
通过 CDP 连接已登录的 Chrome，在页面上下文中执行 JS 直接调用此 API，
复用真实浏览器的 Cookie、指纹和登录态，绕过字体反爬。

关键设计：
- 使用隔离 profile（~/.boss-zhipin-scraper/chrome-profile），不碰主 Chrome
- 登录态持久化：首次手动登录，后续自动复用
- 风控码检测：识别 code:31/37 等，立即停止
"""

import subprocess
import os
import sys
import time
import json
import platform
from typing import Optional

import requests
import websocket


class CDPConnector:
    """
    Chrome CDP 连接管理器

    负责启动 Chrome、建立 WebSocket 连接、在页面上下文中执行 JavaScript。
    """

    def __init__(self, chrome_path: Optional[str] = None, port: Optional[int] = None):
        """
        初始化 CDP 连接器。

        参数:
            chrome_path: Chrome 可执行文件路径，留空自动检测
            port: CDP 调试端口，默认使用配置值
        """
        from src.config import settings

        self.port = port or settings.CDP_PORT
        self.chrome_path = chrome_path or settings.CHROME_PATH or self._detect_chrome_path()
        self.profile_dir = settings.CHROME_PROFILE_DIR
        self.ws: Optional[websocket.WebSocket] = None
        self.target_id: Optional[str] = None
        self.msg_id = 0

    @staticmethod
    def _detect_chrome_path() -> str:
        """自动检测系统上的 Chrome 可执行文件路径。"""
        system = platform.system().lower()
        paths = {
            "windows": [
                r"C:\Program Files\Google\Chrome\Application\chrome.exe",
                r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
                os.path.expandvars(r"%LOCALAPPDATA%\Google\Chrome\Application\chrome.exe"),
            ],
            "darwin": [
                "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
            ],
            "linux": [
                "/usr/bin/google-chrome",
                "/usr/bin/google-chrome-stable",
                "/usr/bin/chromium-browser",
                "/usr/bin/chromium",
            ],
        }
        for p in paths.get(system, []):
            if os.path.exists(p):
                return p
        raise FileNotFoundError(
            "未找到 Chrome 浏览器，请手动指定 chrome_path 或设置 CHROME_PATH 环境变量"
        )

    def _kill_stale_chrome(self) -> None:
        """
        关闭占用 CDP 端口的旧 Chrome 进程（避免 403 WebSocket 握手错误）。

        新版 Chrome 要求 --remote-allow-origins 参数，
        如果之前启动的 Chrome 没有该参数，需要先关闭再重启。
        通过 profile 目录路径匹配，只关闭用隔离 profile 启动的 Chrome，
        不影响用户的主 Chrome。
        """
        try:
            resp = requests.get(
                f"http://127.0.0.1:{self.port}/json/version", timeout=2
            )
            if resp.status_code != 200:
                return  # 端口无 Chrome，无需处理
        except Exception:
            return  # 端口无 Chrome，无需处理

        # 端口上有 Chrome，需要关闭它（只关闭使用隔离 profile 的）
        system = platform.system().lower()
        if system == "windows":
            # Windows: 用 wmic 查找并关闭使用该 profile 的 chrome 进程
            # 用 taskkill 精准匹配 profile 路径
            try:
                # 用 PowerShell 精准匹配 profile 路径
                ps_cmd = (
                    f'Get-WmiObject Win32_Process -Filter '
                    f'"Name=\'chrome.exe\'" | '
                    f'Where-Object {{ $_.CommandLine -like "*{self.profile_dir}*" }} | '
                    f'ForEach-Object {{ Stop-Process -Id $_.ProcessId -Force }}'
                )
                subprocess.run(
                    ["powershell", "-Command", ps_cmd],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                    timeout=10,
                )
            except Exception:
                pass
        elif system == "linux":
            try:
                subprocess.run(
                    ["pkill", "-f", str(self.profile_dir)],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                    timeout=10,
                )
            except Exception:
                pass
        elif system == "darwin":
            try:
                subprocess.run(
                    ["pkill", "-f", str(self.profile_dir)],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                    timeout=10,
                )
            except Exception:
                pass

        # 等待端口释放
        time.sleep(3)

    def _start_chrome_process(self, headless: bool = False) -> None:
        """
        启动 Chrome 进程并等待 CDP 端口就绪（不关闭已有实例）。

        参数:
            headless: 是否使用无头模式（不弹出浏览器窗口）

        内部方法，供 start_chrome 和 ensure_chrome 复用。
        """
        os.makedirs(self.profile_dir, exist_ok=True)
        cmd = [
            self.chrome_path,
            f"--remote-debugging-port={self.port}",
            f"--user-data-dir={self.profile_dir}",
            "--no-first-run",
            "--no-default-browser-check",
            "--remote-allow-origins=*",
            "--disable-blink-features=AutomationControlled",
        ]
        if headless:
            cmd.append("--headless=new")
            cmd.append("--disable-gpu")
            cmd.append("--window-size=1920,1080")
        subprocess.Popen(
            cmd,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        # 等待 CDP 端口就绪
        for _ in range(30):
            try:
                resp = requests.get(
                    f"http://127.0.0.1:{self.port}/json", timeout=2
                )
                if resp.status_code == 200:
                    return
            except requests.ConnectionError:
                pass
            time.sleep(1)
        raise RuntimeError(
            f"Chrome CDP 端口 {self.port} 未就绪，请检查 Chrome 是否正确启动"
        )

    def start_chrome(self, headless: bool = False) -> None:
        """
        强制重启 Chrome（先关闭旧实例再启动）。

        参数:
            headless: 是否使用无头模式（默认 False，弹出浏览器窗口）

        仅用于 setup 命令（首次登录场景）。
        对于 check / crawl，应使用 ensure_chrome()。
        """
        self._kill_stale_chrome()
        self._start_chrome_process(headless=headless)

    def ensure_chrome(self, headless: bool = False) -> "CDPConnector":
        """
        确保 Chrome 已启动并连接。

        - 如果 Chrome CDP 已在运行，直接 connect()；
        - 如果未运行，使用已保存的 profile 启动 Chrome（复用登录态），
          然后连接。

        参数:
            headless: 是否使用无头模式（默认 False，弹出浏览器窗口）。
                      如果登录态失效，需调用 setup_chrome() 重新登录。

        与 start_chrome() 的区别：
        - 不会关闭已有 Chrome 实例
        - 不会等待用户登录（假定 profile 中已有登录态）

        返回:
            self（已连接状态）

        异常:
            如果 profile 中无登录态，connect 后的 API 调用会失败，
            此时需要先运行 setup 命令登录。
        """
        if not self.is_chrome_running():
            mode = "无头模式" if headless else "有头模式"
            print(f"[INFO] Chrome 未运行，正在启动（{mode}，复用已保存的登录态）...")
            self._start_chrome_process(headless=headless)
        return self.connect()

    def is_chrome_running(self) -> bool:
        """检查 Chrome CDP 是否已在运行。"""
        try:
            resp = requests.get(
                f"http://127.0.0.1:{self.port}/json", timeout=3
            )
            return resp.status_code == 200
        except requests.ConnectionError:
            return False

    def connect(self) -> "CDPConnector":
        """
        连接到 CDP，获取或创建 BOSS直聘页面标签。

        优先复用已有的 zhipin.com 标签页；
        如果没有，则复用任意空白标签页或创建新标签页，
        然后通过 CDP Page.navigate 导航到 BOSS直聘。
        """
        from src.config import settings

        tabs = requests.get(
            f"http://127.0.0.1:{self.port}/json"
        ).json()

        boss_tab = None
        blank_tab = None

        for tab in tabs:
            if tab.get("type") != "page":
                continue
            url = tab.get("url", "")
            if "zhipin.com" in url:
                boss_tab = tab
                break
            # 记录第一个可用的空白页（about:blank 或 chrome://newtab）
            if blank_tab is None and (
                "about:blank" in url
                or "chrome://newtab" in url
                or "chrome://new-tab-page" in url
            ):
                blank_tab = tab

        if not boss_tab:
            # 优先复用空白标签页，否则创建新标签页
            target_tab = blank_tab or self._create_tab()
            self.target_id = target_tab["id"]
            ws_url = target_tab["webSocketDebuggerUrl"]
            self.ws = websocket.create_connection(ws_url)

            # 注入反检测脚本（在页面加载前注入，确保生效）
            self._inject_anti_detect_scripts()

            # 用 CDP Page.navigate 导航到 BOSS直聘
            self._cdp_navigate(settings.BOSS_HOME_URL)

            # 等待页面完全加载（包括 JS 初始化安全令牌）
            self._wait_for_page_ready()
        else:
            self.target_id = boss_tab["id"]
            ws_url = boss_tab["webSocketDebuggerUrl"]
            self.ws = websocket.create_connection(ws_url)

            # 检查已有页面是否需要重新加载（如登录过期）
            self._ensure_page_active()

        return self

    def _create_tab(self) -> dict:
        """
        创建一个空白新标签页。

        注意：新版 Chrome 的 /json/new 接口不再自动导航到指定 URL，
        只会创建 about:blank 页面。导航需通过 CDP Page.navigate 完成。
        """
        resp = requests.put(
            f"http://127.0.0.1:{self.port}/json/new",
        )
        return resp.json()

    def evaluate(
        self, expression: str, await_promise: bool = True
    ) -> Optional[object]:
        """
        在页面上下文中执行 JavaScript，返回结果。

        参数:
            expression: JavaScript 代码字符串
            await_promise: 是否等待 Promise 完成

        返回:
            JavaScript 执行结果的 Python 对象
        """
        if not self.ws:
            raise RuntimeError("WebSocket 未连接，请先调用 connect()")

        self.msg_id += 1
        msg_id = self.msg_id
        msg = {
            "id": msg_id,
            "method": "Runtime.evaluate",
            "params": {
                "expression": expression,
                "returnByValue": True,
                "awaitPromise": await_promise,
            },
        }
        self.ws.send(json.dumps(msg))

        # 循环接收消息，直到收到匹配 id 的响应
        # CDP WebSocket 会推送各种事件（Page.frameNavigated 等），
        # 必须按 id 过滤才能拿到正确的响应
        timeout = 30  # 30 秒超时
        start_time = time.time()
        while time.time() - start_time < timeout:
            raw = self.ws.recv()
            if not raw:
                continue
            result = json.loads(raw)

            # 只处理与当前 msg_id 匹配的响应
            if result.get("id") == msg_id:
                if "error" in result:
                    raise RuntimeError(
                        f"CDP evaluate error: {result['error']}"
                    )
                return (
                    result.get("result", {})
                    .get("result", {})
                    .get("value")
                )
            # 非 matching id 的消息（事件推送）跳过

        raise RuntimeError(
            f"CDP evaluate 超时（id={msg_id}），未收到响应"
        )

    def _cdp_navigate(self, url: str) -> None:
        """
        通过 CDP Page.navigate 命令导航当前标签页到指定 URL。

        比 JS window.location.href 更可靠，能触发 Page.frameStoppedLoading 事件。
        """
        if not self.ws:
            raise RuntimeError("WebSocket 未连接，请先调用 connect()")

        # 先启用 Page 域，确保能收到页面事件
        self.msg_id += 1
        enable_id = self.msg_id
        self.ws.send(json.dumps({
            "id": enable_id,
            "method": "Page.enable",
        }))
        # 等待匹配 id 的响应
        self._recv_matching(enable_id)

        self.msg_id += 1
        nav_id = self.msg_id
        msg = {
            "id": nav_id,
            "method": "Page.navigate",
            "params": {"url": url},
        }
        self.ws.send(json.dumps(msg))
        result = self._recv_matching(nav_id)
        if result and "error" in result:
            raise RuntimeError(f"CDP navigate error: {result['error']}")

    def _recv_matching(self, expected_id: int, timeout: int = 15) -> Optional[dict]:
        """
        接收 WebSocket 消息，直到收到匹配 expected_id 的响应。

        CDP 会推送各种事件消息，必须按 id 过滤。
        """
        start_time = time.time()
        while time.time() - start_time < timeout:
            raw = self.ws.recv()
            if not raw:
                continue
            msg = json.loads(raw)
            if msg.get("id") == expected_id:
                return msg
        return None

    def _inject_anti_detect_scripts(self) -> None:
        """
        注入反检测脚本，隐藏 headless 浏览器特征。

        BOSS直聘会检测 navigator.webdriver、navigator.plugins 等指纹
        来识别自动化工具。此方法通过 CDP 的 Page.addScriptToEvaluateOnNewDocument
        在页面加载前注入脚本，覆盖这些检测点。
        """
        if not self.ws:
            return

        stealth_js = """
            // 覆盖 navigator.webdriver = false
            Object.defineProperty(navigator, 'webdriver', {
                get: () => false,
            });

            // 模拟 navigator.plugins（headless 默认为空数组）
            Object.defineProperty(navigator, 'plugins', {
                get: () => [1, 2, 3, 4, 5],
            });

            // 模拟 navigator.languages
            Object.defineProperty(navigator, 'languages', {
                get: () => ['zh-CN', 'zh', 'en'],
            });

            // 确保 window.chrome 存在
            if (!window.chrome) {
                window.chrome = {
                    runtime: {},
                    loadTimes: function() {},
                    csi: function() { return {}; },
                };
            }

            // 覆盖 navigator.permissions.query 检测
            const originalQuery = window.navigator.permissions.query;
            window.navigator.permissions.query = (parameters) =>
                parameters.name === 'notifications'
                    ? Promise.resolve({ state: Notification.permission })
                    : originalQuery(parameters);

            // 覆盖 navigator.userAgent（移除 HeadlessChrome 标记）
            if (navigator.userAgent.indexOf('HeadlessChrome') !== -1) {
                Object.defineProperty(navigator, 'userAgent', {
                    get: () => navigator.userAgent.replace('HeadlessChrome', 'Chrome'),
                });
            }
        """

        self.msg_id += 1
        msg = {
            "id": self.msg_id,
            "method": "Page.addScriptToEvaluateOnNewDocument",
            "params": {"source": stealth_js},
        }
        self.ws.send(json.dumps(msg))
        self._recv_matching(self.msg_id)  # 读取匹配的响应

    def _wait_for_page_ready(self, max_wait: int = 20) -> None:
        """
        等待页面完全加载，包括 JavaScript 初始化安全令牌。

        不再使用固定的 3 秒等待，而是轮询检测：
        1. document.readyState === 'complete'
        2. 页面 URL 已导航到 zhipin.com
        3. 额外等待 JS 框架初始化（安全令牌设置）

        参数:
            max_wait: 最大等待秒数
        """
        print("[INFO] 等待页面加载...")

        # 阶段1：等待 document.readyState === 'complete'
        start = time.time()
        while time.time() - start < max_wait:
            try:
                ready = self.evaluate(
                    "document.readyState", await_promise=False
                )
                if ready == "complete":
                    break
            except Exception:
                pass
            time.sleep(0.5)

        # 阶段2：额外等待 JS 框架初始化安全令牌
        # BOSS 页面的 JS 需要额外时间设置 __zp_stoken__ 等安全 cookie
        time.sleep(3)

        # 阶段3：验证页面 URL 已正确导航
        # 重试多次，避免 CDP WebSocket 消息错位导致返回错误值
        url_ok = False
        for retry in range(3):
            try:
                current_url = self.evaluate(
                    "window.location.href", await_promise=False
                )
                if current_url and isinstance(current_url, str) and "zhipin.com" in current_url:
                    print(f"[OK] 页面加载完成: {current_url}")
                    url_ok = True
                    break
                else:
                    print(f"[WARN] 页面 URL 异常: {current_url}，重试 ({retry+1}/3)...")
                    time.sleep(3)
            except Exception:
                time.sleep(3)

        if not url_ok:
            # 尝试重新导航
            print("[WARN] 页面 URL 仍然异常，尝试重新导航...")
            try:
                from src.config import settings
                self._cdp_navigate(settings.BOSS_HOME_URL)
                time.sleep(5)
                # 再次检查
                current_url = self.evaluate(
                    "window.location.href", await_promise=False
                )
                if current_url and isinstance(current_url, str) and "zhipin.com" in current_url:
                    print(f"[OK] 重新导航成功: {current_url}")
                else:
                    print(f"[WARN] 重新导航后 URL 仍异常: {current_url}")
            except Exception as e:
                print(f"[WARN] 重新导航失败: {e}")

    def _ensure_page_active(self) -> None:
        """
        检查已有 BOSS 页面标签是否仍然有效。

        如果页面被关闭或导航到了非 BOSS 页面，则重新导航。
        """
        from src.config import settings

        try:
            current_url = self.evaluate(
                "window.location.href", await_promise=False
            )
            if current_url and "zhipin.com" in str(current_url):
                # 页面仍在 BOSS 上，检查是否需要刷新
                ready = self.evaluate(
                    "document.readyState", await_promise=False
                )
                if ready != "complete":
                    print("[INFO] 页面未完全加载，等待...")
                    self._wait_for_page_ready()
                return
        except Exception:
            pass

        # 页面无效，重新导航
        print("[INFO] 页面标签无效，重新导航到 BOSS直聘...")
        self._inject_anti_detect_scripts()
        self._cdp_navigate(settings.BOSS_HOME_URL)
        self._wait_for_page_ready()

    def navigate(self, url: str) -> None:
        """在当前标签页导航到指定 URL。"""
        self._cdp_navigate(url)

    def setup_chrome(self, login_timeout: Optional[int] = None) -> bool:
        """
        一键启动 Chrome 并等待用户手动登录 BOSS直聘。

        登录态保存在隔离 profile 中，重启后仍保留。
        后续使用无需重复登录，直接 connect() 即可。

        参数:
            login_timeout: 登录等待超时秒数

        返回:
            True 表示登录成功且接口可用
        """
        from src.config import settings

        if login_timeout is None:
            login_timeout = settings.LOGIN_TIMEOUT

        # 始终先关闭旧 Chrome 再重新启动（确保带有 --remote-allow-origins 参数）
        print("正在启动 Chrome（隔离 profile）...")
        self.start_chrome(headless=False)

        self.connect()

        # 注入反检测脚本（connect 中已注入，但 setup 场景额外确保）
        self._inject_anti_detect_scripts()

        # 注入关闭拦截脚本：防止用户误关闭页面
        self._inject_beforeunload_handler()

        print("请在弹出的 Chrome 窗口中登录 BOSS直聘...")
        print(f"等待登录完成（超时 {login_timeout} 秒）...")

        # 轮询检测登录状态
        start = time.time()
        while time.time() - start < login_timeout:
            result = self.evaluate("""
                (async () => {
                    try {
                        const resp = await fetch(
                            '/wapi/zpgeek/search/joblist.json?keyword=test&page=1',
                            { headers: {'x-requested-with': 'XMLHttpRequest'} }
                        );
                        const data = await resp.json();
                        if (data.code === 0 && data.zpData && data.zpData.jobList) {
                            return {
                                logged_in: true,
                                has_salary: !!data.zpData.jobList[0]?.salaryDesc
                            };
                        }
                        return {
                            logged_in: false,
                            code: data.code,
                            message: data.message
                        };
                    } catch(e) {
                        return { logged_in: false, error: e.message };
                    }
                })()
            """)

            if result and isinstance(result, dict) and result.get("logged_in"):
                print("[OK] 登录成功！搜索接口可返回明文薪资数据。")
                # 登录成功后不关闭浏览器，保持有头模式运行
                # 仅关闭 WebSocket 连接，Chrome 进程保持运行
                self.close()
                return True

            # 检测风控码
            if result and isinstance(result, dict) and result.get("code") in settings.RISK_CONTROL_CODES:
                print(f"[WARN] 检测到风控限制: {result.get('message')}")
                print("  请稍后再试或更换网络环境。")
                return False

            time.sleep(5)

        print("[FAIL] 登录超时。")
        return False

    def _inject_beforeunload_handler(self) -> None:
        """
        注入 beforeunload 事件处理器，在用户关闭页面时弹出提示。

        当用户尝试关闭 BOSS直聘页面时，Chrome 会弹出确认对话框：
        "关闭该网页会导致数据获取功能出现故障"
        用户可以选择「取消关闭」或「依然关闭」。
        """
        if not self.ws:
            return

        beforeunload_js = """
            window.addEventListener('beforeunload', function(e) {
                e.preventDefault();
                e.returnValue = '关闭该网页会导致数据获取功能出现故障';
                return '关闭该网页会导致数据获取功能出现故障';
            });
        """

        self.msg_id += 1
        msg = {
            "id": self.msg_id,
            "method": "Runtime.evaluate",
            "params": {
                "expression": beforeunload_js,
                "returnByValue": True,
                "awaitPromise": False,
            },
        }
        self.ws.send(json.dumps(msg))
        self._recv_matching(self.msg_id)

    def stop_chrome(self) -> None:
        """
        关闭 BOSS 专用 CDP Chrome。
        按隔离 profile 精准匹配，不影响主 Chrome。
        """
        if self.is_chrome_running():
            try:
                requests.get(
                    f"http://127.0.0.1:{self.port}/json/close/{self.target_id}"
                )
            except Exception:
                pass
            # 也关闭整个 Chrome 进程
            self._kill_stale_chrome()
        self.close()

    def close(self) -> None:
        """关闭 WebSocket 连接（不关闭 Chrome）。"""
        if self.ws:
            self.ws.close()
            self.ws = None
