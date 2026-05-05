from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any


@dataclass(frozen=True)
class ScopePolicy:
    """Scope controls for safe, explicit assessment boundaries."""

    seed_url: str
    allow_external: bool = False
    max_pages: int = 5
    timeout_ms: int = 15000
    viewport_width: int = 1365
    viewport_height: int = 768
    user_agent: str | None = None
    wait_until: str = "networkidle"
    full_page: bool = True
    capture_har: bool = False


@dataclass(frozen=True)
class CookieRecord:
    name: str
    domain: str
    path: str
    secure: bool
    http_only: bool
    same_site: str | None
    expires: float | None


@dataclass(frozen=True)
class FormField:
    name: str
    field_type: str
    required: bool
    placeholder: str


@dataclass(frozen=True)
class FormRecord:
    action: str
    method: str
    fields: list[FormField]


@dataclass(frozen=True)
class LinkRecord:
    text: str
    href: str
    internal: bool


@dataclass(frozen=True)
class Observation:
    category: str
    severity: str
    title: str
    detail: str
    recommendation: str


@dataclass(frozen=True)
class NetworkRecord:
    url: str
    method: str
    resource_type: str
    status: int | None
    content_type: str
    internal: bool


@dataclass(frozen=True)
class EvidenceRecord:
    path: str
    sha256: str
    size_bytes: int


@dataclass(frozen=True)
class PageSnapshot:
    url: str
    title: str
    status: int | None
    screenshot: str | None
    headers: dict[str, str]
    cookies: list[CookieRecord]
    forms: list[FormRecord]
    links: list[LinkRecord]
    technologies: list[str]
    observations: list[Observation] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class ScanResult:
    target_url: str
    created_at: str
    output_dir: str
    pages: list[PageSnapshot]
    navigation_graph: dict[str, list[str]]
    warnings: list[str]
    stats: dict[str, int]
    network: list[NetworkRecord] = field(default_factory=list)
    evidence: list[EvidenceRecord] = field(default_factory=list)

    @classmethod
    def create(
        cls,
        target_url: str,
        output_dir: str,
        pages: list[PageSnapshot],
        navigation_graph: dict[str, list[str]],
        warnings: list[str],
        stats: dict[str, int] | None = None,
        network: list[NetworkRecord] | None = None,
        evidence: list[EvidenceRecord] | None = None,
    ) -> ScanResult:
        network_records = network or []
        return cls(
            target_url=target_url,
            created_at=datetime.now(timezone.utc).isoformat(),
            output_dir=output_dir,
            pages=pages,
            navigation_graph=navigation_graph,
            warnings=warnings,
            stats=stats or build_stats(pages, network_records),
            network=network_records,
            evidence=evidence or [],
        )


def build_stats(pages: list[PageSnapshot], network: list[NetworkRecord] | None = None) -> dict[str, int]:
    network_records = network or []
    external_requests = sum(1 for record in network_records if not record.internal)
    return {
        "pages": len(pages),
        "forms": sum(len(page.forms) for page in pages),
        "links": sum(len(page.links) for page in pages),
        "cookies": sum(len(page.cookies) for page in pages),
        "network_requests": len(network_records),
        "external_requests": external_requests,
        "observations": sum(len(page.observations) for page in pages),
        "high_observations": sum(
            1 for page in pages for observation in page.observations if observation.severity == "high"
        ),
        "medium_observations": sum(
            1 for page in pages for observation in page.observations if observation.severity == "medium"
        ),
        "low_observations": sum(
            1 for page in pages for observation in page.observations if observation.severity == "low"
        ),
        "risk_score": sum(
            {"high": 5, "medium": 3, "low": 1}.get(observation.severity, 0)
            for page in pages
            for observation in page.observations
        ),
    }


def to_jsonable(value: Any) -> Any:
    if hasattr(value, "__dataclass_fields__"):
        return {key: to_jsonable(getattr(value, key)) for key in value.__dataclass_fields__}
    if isinstance(value, list):
        return [to_jsonable(item) for item in value]
    if isinstance(value, dict):
        return {str(key): to_jsonable(item) for key, item in value.items()}
    return value
