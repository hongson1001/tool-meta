"""Local OAuth callback server — bắt code/token từ FB redirect khi user cấp quyền.

Flow:
1. Tool gọi start_oauth_flow(app_id, scopes) trong UI
2. Function start HTTP server localhost:PORT
3. Mở browser tới URL OAuth của Facebook (response_type=code)
4. User login + cấp quyền → FB redirect tới http://localhost:PORT/callback?code=...
5. Server bắt code, return về caller
6. Server tự shutdown
"""
import http.server
import secrets
import socketserver
import threading
import time
import webbrowser
from typing import Optional
from urllib.parse import parse_qs, urlparse

from src.config import OAUTH_REDIRECT_PORT


class OAuthError(Exception):
    pass


class _State:
    code: Optional[str] = None
    error: Optional[str] = None
    error_desc: Optional[str] = None
    state: Optional[str] = None


def _redirect_uri() -> str:
    return f"http://localhost:{OAUTH_REDIRECT_PORT}/callback"


def _build_authorize_url(app_id: str, scopes: list[str], state: str, api_version: str = "v19.0") -> str:
    scope_str = ",".join(scopes)
    return (
        f"https://www.facebook.com/{api_version}/dialog/oauth"
        f"?client_id={app_id}"
        f"&redirect_uri={_redirect_uri()}"
        f"&response_type=code"
        f"&scope={scope_str}"
        f"&state={state}"
        f"&auth_type=rerequest"
    )


_SUCCESS_HTML = """<!DOCTYPE html>
<html lang="vi">
<head>
<meta charset="utf-8">
<title>Đã đăng nhập</title>
<style>
body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
       background: #f0f2f5; margin: 0; min-height: 100vh;
       display: flex; align-items: center; justify-content: center; }
.card { background: white; padding: 48px 64px; border-radius: 12px;
        box-shadow: 0 4px 16px rgba(0,0,0,0.08); text-align: center; max-width: 480px; }
h1 { color: #1877f2; margin: 0 0 12px; font-size: 28px; }
p { color: #65676b; margin: 8px 0; }
.icon { font-size: 64px; margin-bottom: 16px; }
</style>
</head>
<body>
<div class="card">
  <div class="icon">✅</div>
  <h1>Đã đăng nhập thành công!</h1>
  <p>Bạn có thể đóng tab này và quay lại tool FB Auto Post.</p>
  <p style="font-size: 13px; color: #8a8d91;">Tool đang tự động xử lý token...</p>
</div>
<script>setTimeout(() => window.close(), 3000);</script>
</body>
</html>"""

_ERROR_HTML = """<!DOCTYPE html>
<html lang="vi">
<head>
<meta charset="utf-8">
<title>Lỗi đăng nhập</title>
<style>
body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
       background: #f0f2f5; margin: 0; min-height: 100vh;
       display: flex; align-items: center; justify-content: center; }
.card { background: white; padding: 48px 64px; border-radius: 12px;
        box-shadow: 0 4px 16px rgba(0,0,0,0.08); text-align: center; max-width: 480px; }
h1 { color: #d93025; margin: 0 0 12px; font-size: 28px; }
p { color: #65676b; margin: 8px 0; }
.icon { font-size: 64px; margin-bottom: 16px; }
.error { background: #fde8e8; padding: 12px; border-radius: 6px; color: #b91c1c;
         font-family: monospace; font-size: 13px; margin-top: 16px; word-break: break-word; }
</style>
</head>
<body>
<div class="card">
  <div class="icon">❌</div>
  <h1>Đăng nhập thất bại</h1>
  <p>Vui lòng quay lại tool và thử lại.</p>
  <div class="error">{error}</div>
</div>
</body>
</html>"""


class _Handler(http.server.BaseHTTPRequestHandler):
    def log_message(self, *args, **kwargs):
        pass

    def do_GET(self):
        parsed = urlparse(self.path)
        if parsed.path != "/callback":
            self.send_response(404)
            self.end_headers()
            return

        params = parse_qs(parsed.query)
        code = params.get("code", [None])[0]
        error = params.get("error", [None])[0]
        error_desc = params.get("error_description", [None])[0]
        state = params.get("state", [None])[0]

        if code:
            _State.code = code
            _State.state = state
            html = _SUCCESS_HTML
        else:
            _State.error = error or "unknown"
            _State.error_desc = error_desc
            html = _ERROR_HTML.replace("{error}", f"{error}: {error_desc or ''}")

        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(html.encode("utf-8"))


def start_oauth_flow(app_id: str, scopes: list[str], api_version: str = "v19.0", timeout: int = 300) -> dict:
    """Mở browser cho user OAuth, đợi callback, trả về {code, redirect_uri}.

    Throws OAuthError nếu user từ chối, timeout, hoặc state mismatch.
    """
    if not app_id:
        raise OAuthError("FB_APP_ID chưa được cấu hình trong .env")

    _State.code = None
    _State.error = None
    _State.error_desc = None
    _State.state = None

    state = secrets.token_urlsafe(16)
    expected_state = state

    try:
        server = socketserver.TCPServer(("127.0.0.1", OAUTH_REDIRECT_PORT), _Handler)
    except OSError as e:
        raise OAuthError(
            f"Không khởi tạo được local server cổng {OAUTH_REDIRECT_PORT}: {e}. "
            f"Có thể cổng này đang bị app khác dùng — đổi OAUTH_REDIRECT_PORT trong .env"
        ) from e

    server.allow_reuse_address = True
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()

    try:
        url = _build_authorize_url(app_id, scopes, state, api_version)
        opened = webbrowser.open(url)
        if not opened:
            raise OAuthError(f"Không mở được browser tự động. Mở thủ công URL: {url}")

        elapsed = 0.0
        interval = 0.3
        while elapsed < timeout:
            if _State.code or _State.error:
                break
            time.sleep(interval)
            elapsed += interval

        if _State.error:
            raise OAuthError(f"FB từ chối: {_State.error} — {_State.error_desc or ''}")
        if not _State.code:
            raise OAuthError(f"Timeout {timeout}s — không nhận được callback từ Facebook")
        if _State.state != expected_state:
            raise OAuthError("State mismatch (CSRF protection) — bỏ flow OAuth này")

        return {"code": _State.code, "redirect_uri": _redirect_uri()}

    finally:
        server.shutdown()
        server.server_close()
