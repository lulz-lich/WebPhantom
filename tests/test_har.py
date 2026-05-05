import json

from webphantom.storage.har import sanitize_har_file


def test_sanitize_har_file_redacts_sensitive_values(tmp_path) -> None:
    har = tmp_path / "network.har"
    har.write_text(
        json.dumps(
            {
                "log": {
                    "entries": [
                        {
                            "request": {
                                "headers": [{"name": "Cookie", "value": "session=secret"}],
                                "cookies": [{"name": "session", "value": "secret"}],
                            },
                            "response": {
                                "headers": [{"name": "Set-Cookie", "value": "session=secret"}],
                                "cookies": [{"name": "session", "value": "secret"}],
                            },
                        }
                    ]
                }
            }
        ),
        encoding="utf-8",
    )

    sanitize_har_file(har)
    payload = json.loads(har.read_text(encoding="utf-8"))
    entry = payload["log"]["entries"][0]

    assert entry["request"]["headers"][0]["value"] == "[redacted]"
    assert entry["response"]["headers"][0]["value"] == "[redacted]"
    assert entry["request"]["cookies"][0]["value"] == "[redacted]"
    assert entry["response"]["cookies"][0]["value"] == "[redacted]"
