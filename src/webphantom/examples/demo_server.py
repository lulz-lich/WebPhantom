from __future__ import annotations

from http.server import BaseHTTPRequestHandler


class DemoHandler(BaseHTTPRequestHandler):
    def do_GET(self) -> None:
        if self.path == "/":
            body = """
            <!doctype html>
            <html>
              <head>
                <title>WebPhantom Demo Portal</title>
                <meta name="generator" content="DemoApp">
              </head>
              <body>
                <h1>WebPhantom Demo Portal</h1>
                <nav>
                  <a href="/login">Login</a>
                  <a href="/profile">Profile</a>
                  <a href="/upload">Upload</a>
                </nav>
                <form action="/search" method="GET">
                  <input name="q" placeholder="Search documentation">
                  <button type="submit">Search</button>
                </form>
              </body>
            </html>
            """
            self._send(body)
            return
        if self.path == "/login":
            self._send(
                """
                <!doctype html><html><head><title>Login</title></head><body>
                <h1>Login</h1>
                <form action="/session" method="POST">
                  <input name="email" type="email" required>
                  <input name="password" type="password" required>
                  <button type="submit">Sign in</button>
                </form>
                </body></html>
                """,
                cookie="demo_session=local-documentation-only; HttpOnly; SameSite=Lax",
            )
            return
        if self.path == "/profile":
            self._send(
                """
                <!doctype html><html><head><title>Profile Settings</title></head><body>
                <h1>Profile Settings</h1>
                <a href='/'>Home</a>
                </body></html>
                """
            )
            return
        if self.path == "/upload":
            self._send(
                """
                <!doctype html><html><head><title>Upload</title></head><body>
                <h1>Upload Center</h1>
                <form action="/upload" method="POST">
                  <input type="file" name="attachment">
                  <button type="submit">Upload</button>
                </form>
                </body></html>
                """
            )
            return
        self.send_response(404)
        self.end_headers()

    def log_message(self, format: str, *args: object) -> None:
        return

    def _send(self, body: str, cookie: str | None = None) -> None:
        payload = body.encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(payload)))
        self.send_header("Server", "WebPhantomDemo/0.1")
        if cookie:
            self.send_header("Set-Cookie", cookie)
        self.end_headers()
        self.wfile.write(payload)
