from webphantom.collectors.security import evaluate_security_posture
from webphantom.models import CookieRecord, FormField, FormRecord


def test_evaluate_security_posture_reports_missing_https_headers() -> None:
    observations = evaluate_security_posture(
        url="https://example.com",
        headers={"content-type": "text/html"},
        cookies=[],
        forms=[],
    )

    titles = {observation.title for observation in observations}
    assert "Missing HSTS Header" in titles
    assert "Missing Content Security Policy" in titles


def test_evaluate_security_posture_reports_password_get_form() -> None:
    observations = evaluate_security_posture(
        url="http://example.com/login",
        headers={},
        cookies=[],
        forms=[
            FormRecord(
                action="http://example.com/login",
                method="GET",
                fields=[FormField(name="password", field_type="password", required=True, placeholder="")],
            )
        ],
    )

    titles = {observation.title for observation in observations}
    assert "Password Field Uses GET Form" in titles
    assert "Password Field Observed Over HTTP" in titles


def test_evaluate_security_posture_reports_cookie_attribute_gaps() -> None:
    observations = evaluate_security_posture(
        url="https://example.com",
        headers={},
        cookies=[
            CookieRecord(
                name="session",
                domain="example.com",
                path="/",
                secure=False,
                http_only=False,
                same_site=None,
                expires=None,
            )
        ],
        forms=[],
    )

    titles = {observation.title for observation in observations}
    assert "Cookie Missing Secure Attribute" in titles
    assert "Cookie Missing HttpOnly Attribute" in titles
    assert "Cookie SameSite Review Recommended" in titles
