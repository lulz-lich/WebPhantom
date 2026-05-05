from __future__ import annotations

from urllib.parse import urlparse

AUTHORIZED_USE_NOTICE = (
    "WebPhantom is for authorized assessments only. It passively visits URLs "
    "you explicitly provide, records browser-observable metadata, and does not "
    "perform exploitation, brute forcing, credential collection, or bypasses."
)


def validate_target_url(url: str) -> str:
    parsed = urlparse(url)
    if parsed.scheme not in {"http", "https"}:
        raise ValueError("Target URL must start with http:// or https://.")
    if not parsed.netloc:
        raise ValueError("Target URL must include a host.")
    return url


def same_origin(seed_url: str, candidate_url: str) -> bool:
    seed = urlparse(seed_url)
    candidate = urlparse(candidate_url)
    seed_port = seed.port or (443 if seed.scheme == "https" else 80)
    candidate_port = candidate.port or (443 if candidate.scheme == "https" else 80)
    return (
        seed.scheme == candidate.scheme
        and seed.hostname == candidate.hostname
        and seed_port == candidate_port
    )
