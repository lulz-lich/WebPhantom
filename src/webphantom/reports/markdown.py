from __future__ import annotations

from pathlib import Path

from webphantom.models import ScanResult

SEVERITY_ORDER = {"high": 0, "medium": 1, "low": 2, "informational": 3}


def render_markdown(result: ScanResult) -> str:
    observations = sorted(
        [observation for page in result.pages for observation in page.observations],
        key=lambda item: (SEVERITY_ORDER.get(item.severity, 99), item.category, item.title),
    )
    lines = [
        "# WebPhantom Assessment Summary",
        "",
        f"Target: `{result.target_url}`",
        f"Generated: `{result.created_at}`",
        "",
        "## Safety Notice",
        "",
        "This report documents browser-observable metadata from an explicitly provided target URL. "
        "It does not contain exploitation, brute forcing, authentication bypass, credential collection, "
        "or destructive testing.",
        "",
        "## Overview",
        "",
        f"- Pages visited: {len(result.pages)}",
        f"- Forms discovered: {result.stats.get('forms', 0)}",
        f"- Links discovered: {result.stats.get('links', 0)}",
        f"- Network responses observed: {result.stats.get('network_requests', 0)}",
        f"- External responses observed: {result.stats.get('external_requests', 0)}",
        f"- Passive observations: {result.stats.get('observations', 0)}",
        "- High / Medium / Low: "
        f"{result.stats.get('high_observations', 0)} / "
        f"{result.stats.get('medium_observations', 0)} / "
        f"{result.stats.get('low_observations', 0)}",
        f"- Passive risk score: {result.stats.get('risk_score', 0)}",
        f"- Output directory: `{result.output_dir}`",
        f"- Warnings: {len(result.warnings)}",
        "",
    ]

    if observations:
        lines.extend(["## Executive Observation Summary", ""])
        for observation in observations[:12]:
            lines.append(
                f"- {observation.severity.title()}: {observation.title} "
                f"({observation.category}) - {observation.recommendation}"
            )
        if len(observations) > 12:
            lines.append(f"- Additional observations omitted from this summary: {len(observations) - 12}")
        lines.append("")

    if result.warnings:
        lines.extend(["## Warnings", ""])
        for warning in result.warnings:
            lines.append(f"- {warning}")
        lines.append("")

    lines.extend(["## Pages", ""])
    for page in result.pages:
        lines.extend(
            [
                f"### {page.title or page.url}",
                "",
                f"- URL: `{page.url}`",
                f"- Status: `{page.status}`",
                f"- Screenshot: `{page.screenshot}`",
                f"- Cookies observed: {len(page.cookies)}",
                f"- Forms: {len(page.forms)}",
                f"- Links: {len(page.links)}",
                f"- Technologies: {', '.join(page.technologies) if page.technologies else 'None identified'}",
                "",
            ]
        )
        if page.observations:
            lines.append("Passive observations:")
            for observation in page.observations:
                lines.append(
                    f"- {observation.severity.title()} / {observation.category}: "
                    f"{observation.title} - {observation.detail}"
                )
            lines.append("")

        if page.notes:
            lines.append("Observed states:")
            for note in page.notes:
                lines.append(f"- {note}")
            lines.append("")

        if page.forms:
            lines.append("Forms:")
            for form in page.forms:
                field_names = ", ".join(field.name or field.field_type for field in form.fields) or "no named fields"
                lines.append(f"- `{form.method}` `{form.action}` fields: {field_names}")
            lines.append("")

    lines.extend(["## Navigation Graph", ""])
    for source, targets in result.navigation_graph.items():
        if targets:
            for target in targets:
                lines.append(f"- `{source}` -> `{target}`")
        else:
            lines.append(f"- `{source}` -> no in-scope links found")
    lines.append("")

    if result.network:
        lines.extend(["## Network Inventory", ""])
        for record in result.network[:30]:
            scope = "internal" if record.internal else "external"
            lines.append(
                f"- `{record.status}` `{record.method}` `{record.resource_type}` {scope}: `{record.url}`"
            )
        if len(result.network) > 30:
            lines.append(f"- Additional responses omitted from Markdown: {len(result.network) - 30}")
        lines.append("")

    if result.evidence:
        lines.extend(["## Evidence Manifest", ""])
        for evidence in result.evidence:
            lines.append(f"- `{evidence.path}` `{evidence.sha256}` {evidence.size_bytes} bytes")
        lines.append("")
    return "\n".join(lines)


def write_markdown(result: ScanResult, output_dir: Path) -> Path:
    path = output_dir / "README.md"
    path.write_text(render_markdown(result) + "\n", encoding="utf-8")
    return path
