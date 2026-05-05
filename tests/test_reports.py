from webphantom.models import PageSnapshot, ScanResult
from webphantom.reports.markdown import render_markdown


def test_render_markdown_includes_core_sections() -> None:
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
                technologies=["Server: demo"],
            )
        ],
        navigation_graph={"https://example.com": []},
        warnings=[],
        network=[],
    )

    markdown = render_markdown(result)

    assert "# WebPhantom Assessment Summary" in markdown
    assert "https://example.com" in markdown
    assert "Server: demo" in markdown
