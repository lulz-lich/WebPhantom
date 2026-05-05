from webphantom.collectors.headers import sanitize_headers


def test_sanitize_headers_redacts_sensitive_values() -> None:
    headers = {
        "content-type": "text/html",
        "set-cookie": "session=secret",
        "Authorization": "Bearer token",
    }

    sanitized = sanitize_headers(headers)

    assert sanitized["content-type"] == "text/html"
    assert sanitized["set-cookie"] == "[redacted]"
    assert sanitized["Authorization"] == "[redacted]"
