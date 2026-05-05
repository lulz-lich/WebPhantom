from __future__ import annotations

import json
from pathlib import Path

SENSITIVE_HAR_HEADERS = {"authorization", "cookie", "set-cookie", "proxy-authorization"}
SENSITIVE_COOKIE_FIELDS = {"value"}


def sanitize_har_file(path: Path) -> None:
    """Redact sensitive header and cookie values from an opt-in HAR artifact."""
    if not path.exists():
        return
    payload = json.loads(path.read_text(encoding="utf-8"))
    for entry in payload.get("log", {}).get("entries", []):
        _redact_headers(entry.get("request", {}).get("headers", []))
        _redact_headers(entry.get("response", {}).get("headers", []))
        _redact_cookies(entry.get("request", {}).get("cookies", []))
        _redact_cookies(entry.get("response", {}).get("cookies", []))
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def _redact_headers(headers: list[dict]) -> None:
    for header in headers:
        if str(header.get("name", "")).lower() in SENSITIVE_HAR_HEADERS:
            header["value"] = "[redacted]"


def _redact_cookies(cookies: list[dict]) -> None:
    for cookie in cookies:
        for field in SENSITIVE_COOKIE_FIELDS:
            if field in cookie:
                cookie[field] = "[redacted]"
