from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlparse

from webphantom.models import EvidenceRecord, ScanResult, to_jsonable


def create_project_dir(base_dir: Path, target_url: str) -> Path:
    parsed = urlparse(target_url)
    host = parsed.netloc.replace(":", "-") or "target"
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    output_dir = base_dir / f"{host}-{timestamp}"
    output_dir.mkdir(parents=True, exist_ok=True)
    return output_dir


def write_json(result: ScanResult, output_dir: Path) -> Path:
    path = output_dir / "webphantom-results.json"
    path.write_text(json.dumps(to_jsonable(result), indent=2) + "\n", encoding="utf-8")
    return path


def build_evidence_manifest(output_dir: Path) -> list[EvidenceRecord]:
    records: list[EvidenceRecord] = []
    for path in sorted(output_dir.rglob("*")):
        if not path.is_file() or path.name in {"README.md", "evidence-manifest.json", "webphantom-results.json"}:
            continue
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        records.append(
            EvidenceRecord(
                path=str(path.relative_to(output_dir)),
                sha256=digest,
                size_bytes=path.stat().st_size,
            )
        )
    return records


def write_evidence_manifest(records: list[EvidenceRecord], output_dir: Path) -> Path:
    path = output_dir / "evidence-manifest.json"
    path.write_text(json.dumps(to_jsonable(records), indent=2) + "\n", encoding="utf-8")
    return path
