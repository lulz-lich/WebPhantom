import json

import pytest

from webphantom.config import load_scan_profile, write_sample_profile


def test_load_scan_profile_reads_supported_keys(tmp_path) -> None:
    profile = tmp_path / "profile.json"
    profile.write_text(json.dumps({"max_pages": 3, "viewport": "1280x720"}), encoding="utf-8")

    loaded = load_scan_profile(profile)

    assert loaded.max_pages == 3
    assert loaded.viewport == "1280x720"


def test_load_scan_profile_rejects_unknown_keys(tmp_path) -> None:
    profile = tmp_path / "profile.json"
    profile.write_text(json.dumps({"danger": True}), encoding="utf-8")

    with pytest.raises(ValueError):
        load_scan_profile(profile)


def test_write_sample_profile_creates_json(tmp_path) -> None:
    path = write_sample_profile(tmp_path / "profile.json")

    assert json.loads(path.read_text(encoding="utf-8"))["max_pages"] == 4
