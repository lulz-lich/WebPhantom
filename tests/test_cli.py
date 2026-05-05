import pytest

from webphantom.cli.app import parse_viewport


def test_parse_viewport_accepts_width_and_height() -> None:
    assert parse_viewport("1440x900") == (1440, 900)


def test_parse_viewport_rejects_small_values() -> None:
    with pytest.raises(Exception):
        parse_viewport("200x100")
