from __future__ import annotations

from webphantom.models import PageSnapshot, ScanResult
from webphantom.reports.html import render_html


def test_render_html_contains_target_and_metrics() -> None:
    result = ScanResult.create(
        target_url="https://example.com",
        output_dir="runs/example",
        pages=[
            PageSnapshot(
                url="https://example.com",
                title="Example",
                status=200,
                screenshot="screenshots/example.png",
                headers={},
                cookies=[],
                forms=[],
                links=[],
                technologies=[],
            )
        ],
        navigation_graph={"https://example.com": []},
        warnings=[],
    )

    html = render_html(result)

    assert "WebPhantom" in html
    assert "https://example.com" in html
    assert "Risk Score" in html
