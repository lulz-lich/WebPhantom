from __future__ import annotations

SENSITIVE_HEADER_NAMES = {"authorization", "cookie", "set-cookie", "proxy-authorization"}


def sanitize_headers(headers: dict[str, str]) -> dict[str, str]:
    """Keep header names visible while redacting values that may contain secrets."""
    sanitized: dict[str, str] = {}
    for name, value in headers.items():
        if name.lower() in SENSITIVE_HEADER_NAMES:
            sanitized[name] = "[redacted]"
        else:
            sanitized[name] = value
    return sanitized
