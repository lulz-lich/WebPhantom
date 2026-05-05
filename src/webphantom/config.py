from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class ScanProfile:
    max_pages: int | None = None
    allow_external: bool | None = None
    timeout: int | None = None
    viewport: str | None = None
    user_agent: str | None = None
    wait_until: str | None = None
    full_page: bool | None = None
    capture_har: bool | None = None


PROFILE_KEYS = set(ScanProfile.__dataclass_fields__)


def load_scan_profile(path: Path) -> ScanProfile:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError("Scan profile must be a JSON object.")
    unknown_keys = sorted(set(payload) - PROFILE_KEYS)
    if unknown_keys:
        raise ValueError(f"Unsupported scan profile keys: {', '.join(unknown_keys)}")
    return ScanProfile(**payload)


def write_sample_profile(path: Path) -> Path:
    sample: dict[str, Any] = {
        "max_pages": 4,
        "allow_external": False,
        "timeout": 15000,
        "viewport": "1440x900",
        "user_agent": "WebPhantom-AuthorizedAssessment/0.1",
        "wait_until": "networkidle",
        "full_page": True,
        "capture_har": False,
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(sample, indent=2) + "\n", encoding="utf-8")
    return path


def profile_value(profile: ScanProfile | None, key: str, fallback):
    if profile is None:
        return fallback
    value = getattr(profile, key)
    return fallback if value is None else value


def resolve_profile_value(profile: ScanProfile | None, key: str, cli_value, default):
    if cli_value is not None:
        return cli_value
    return profile_value(profile, key, default)
