from __future__ import annotations

from urllib.parse import urlparse

from webphantom.models import CookieRecord, FormRecord, Observation

SECURITY_HEADERS = {
    "strict-transport-security": (
        "medium",
        "Missing HSTS Header",
        "Strict-Transport-Security was not observed on an HTTPS response.",
        "Enable HSTS on HTTPS applications after validating subdomain and preload requirements.",
    ),
    "content-security-policy": (
        "medium",
        "Missing Content Security Policy",
        "Content-Security-Policy was not observed.",
        "Define a CSP that reflects the application's script, style, image, and framing requirements.",
    ),
    "x-frame-options": (
        "low",
        "Missing Clickjacking Protection Header",
        "X-Frame-Options was not observed. A CSP frame-ancestors directive can also satisfy this control.",
        "Use CSP frame-ancestors or X-Frame-Options to restrict unexpected framing.",
    ),
    "x-content-type-options": (
        "low",
        "Missing MIME Sniffing Protection Header",
        "X-Content-Type-Options was not observed.",
        "Set X-Content-Type-Options: nosniff on applicable responses.",
    ),
    "referrer-policy": (
        "low",
        "Missing Referrer Policy",
        "Referrer-Policy was not observed.",
        "Set a Referrer-Policy aligned with privacy and analytics needs.",
    ),
}


def evaluate_security_posture(
    url: str,
    headers: dict[str, str],
    cookies: list[CookieRecord],
    forms: list[FormRecord],
) -> list[Observation]:
    observations: list[Observation] = []
    normalized_headers = {name.lower(): value for name, value in headers.items()}
    parsed = urlparse(url)

    for header_name, (severity, title, detail, recommendation) in SECURITY_HEADERS.items():
        if header_name == "strict-transport-security" and parsed.scheme != "https":
            continue
        if header_name not in normalized_headers:
            observations.append(
                Observation(
                    category="headers",
                    severity=severity,
                    title=title,
                    detail=detail,
                    recommendation=recommendation,
                )
            )

    for cookie in cookies:
        if parsed.scheme == "https" and not cookie.secure:
            observations.append(
                Observation(
                    category="cookies",
                    severity="medium",
                    title="Cookie Missing Secure Attribute",
                    detail=f"Cookie `{cookie.name}` was observed without the Secure attribute.",
                    recommendation="Set Secure on session and sensitive cookies served over HTTPS.",
                )
            )
        if not cookie.http_only:
            observations.append(
                Observation(
                    category="cookies",
                    severity="low",
                    title="Cookie Missing HttpOnly Attribute",
                    detail=f"Cookie `{cookie.name}` was observed without the HttpOnly attribute.",
                    recommendation="Set HttpOnly on cookies that do not need client-side JavaScript access.",
                )
            )
        if not cookie.same_site or cookie.same_site.lower() == "none":
            observations.append(
                Observation(
                    category="cookies",
                    severity="low",
                    title="Cookie SameSite Review Recommended",
                    detail=f"Cookie `{cookie.name}` has SameSite `{cookie.same_site}`.",
                    recommendation="Use Lax or Strict where compatible with the application flow.",
                )
            )

    for form in forms:
        if form.method.upper() == "GET" and any(field.field_type.lower() == "password" for field in form.fields):
            observations.append(
                Observation(
                    category="forms",
                    severity="high",
                    title="Password Field Uses GET Form",
                    detail=f"Form `{form.action}` contains a password field and uses GET.",
                    recommendation="Submit credential forms with POST over HTTPS and avoid placing secrets in URLs.",
                )
            )
        if parsed.scheme != "https" and any(field.field_type.lower() == "password" for field in form.fields):
            observations.append(
                Observation(
                    category="forms",
                    severity="high",
                    title="Password Field Observed Over HTTP",
                    detail=f"Page `{url}` contains a password field over an unencrypted scheme.",
                    recommendation="Serve authentication flows exclusively over HTTPS.",
                )
            )

    return observations
