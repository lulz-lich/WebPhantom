import pytest

from webphantom.safety import same_origin, validate_target_url


def test_validate_target_url_accepts_http_urls() -> None:
    assert validate_target_url("https://example.com/app") == "https://example.com/app"


def test_validate_target_url_rejects_non_http_urls() -> None:
    with pytest.raises(ValueError):
        validate_target_url("file:///etc/passwd")


def test_same_origin_accounts_for_scheme_host_and_port() -> None:
    assert same_origin("https://example.com/a", "https://example.com/b")
    assert not same_origin("https://example.com/a", "http://example.com/a")
    assert not same_origin("https://example.com/a", "https://other.example/a")
