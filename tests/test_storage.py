import json

from webphantom.models import PageSnapshot, ScanResult
from webphantom.storage.project import build_evidence_manifest, write_json


def test_write_json_creates_structured_result(tmp_path) -> None:
    result = ScanResult.create(
        target_url="https://example.com",
        output_dir=str(tmp_path),
        pages=[
            PageSnapshot(
                url="https://example.com",
                title="Example",
                status=200,
                screenshot="screenshots/example.png",
                headers={"content-type": "text/html"},
                cookies=[],
                forms=[],
                links=[],
                technologies=[],
            )
        ],
        navigation_graph={"https://example.com": []},
        warnings=["authorized use only"],
    )

    path = write_json(result, tmp_path)

    payload = json.loads(path.read_text(encoding="utf-8"))
    assert payload["target_url"] == "https://example.com"
    assert payload["pages"][0]["title"] == "Example"


def test_build_evidence_manifest_hashes_stable_artifacts(tmp_path) -> None:
    screenshots = tmp_path / "screenshots"
    screenshots.mkdir()
    screenshot = screenshots / "page.png"
    screenshot.write_bytes(b"fake image")
    (tmp_path / "README.md").write_text("report", encoding="utf-8")
    (tmp_path / "webphantom-results.json").write_text("{}", encoding="utf-8")
    (tmp_path / "evidence-manifest.json").write_text("[]", encoding="utf-8")

    records = build_evidence_manifest(tmp_path)

    assert len(records) == 1
    assert records[0].path == "screenshots\\page.png" or records[0].path == "screenshots/page.png"
    assert records[0].size_bytes == len(b"fake image")
