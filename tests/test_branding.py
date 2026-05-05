from webphantom.cli.branding import BANNER, PHANTOM_FRAMES, STARTUP_PULSE, TAGLINE


def test_banner_has_project_name_and_no_control_sequences() -> None:
    assert "____" in BANNER
    assert r"\___" in BANNER
    assert "\x1b" not in BANNER


def test_branding_text_is_professional_and_compact() -> None:
    assert "authorized" in TAGLINE
    assert "exploit" in TAGLINE
    assert len(STARTUP_PULSE) <= 5


def test_animation_frames_are_short_ascii_lines() -> None:
    assert len(PHANTOM_FRAMES) <= 6
    assert all(len(frame) < 80 for frame in PHANTOM_FRAMES)
    assert all(ord(char) < 128 for frame in PHANTOM_FRAMES for char in frame)
