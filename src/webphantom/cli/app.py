from __future__ import annotations

import asyncio
import json
from pathlib import Path

try:
    import typer
    from rich.console import Console
    from rich.panel import Panel
    from rich.table import Table
except ImportError:  # pragma: no cover
    typer = None
    Console = None
    Panel = None
    Table = None

from webphantom import __version__
from webphantom.browser.runner import run_scan
from webphantom.cli.branding import render_banner, render_boot_animation, render_startup_pulse
from webphantom.config import load_scan_profile, resolve_profile_value, write_sample_profile
from webphantom.models import ScopePolicy
from webphantom.reports.html import write_html
from webphantom.reports.markdown import write_markdown
from webphantom.safety import AUTHORIZED_USE_NOTICE, validate_target_url
from webphantom.storage.project import build_evidence_manifest, create_project_dir, write_evidence_manifest, write_json

if typer is None:  # pragma: no cover
    raise RuntimeError("Typer and Rich are required. Install with `python -m pip install -e .`.")

app = typer.Typer(help="WebPhantom: safe headless browser documentation for authorized web assessments.")
console = Console()


def version_callback(value: bool) -> None:
    if value:
        console.print(f"WebPhantom {__version__}")
        raise typer.Exit()


@app.callback()
def main(
    version: bool = typer.Option(False, "--version", callback=version_callback, help="Show version and exit."),
) -> None:
    """Authorized browser reconnaissance and documentation toolkit."""


@app.command()
def scan(
    url: str = typer.Argument(..., help="Explicit target URL to visit."),
    output: Path = typer.Option(Path("runs"), "--output", "-o", help="Base directory for scan results."),
    profile: Path | None = typer.Option(None, "--profile", help="Optional JSON scan profile."),
    max_pages: int | None = typer.Option(None, "--max-pages", min=1, max=25, help="Maximum in-scope pages to visit."),
    allow_external: bool | None = typer.Option(
        None,
        "--allow-external/--same-origin-only",
        help="Allow or block navigation to external origins.",
    ),
    timeout: int | None = typer.Option(None, "--timeout", help="Navigation timeout in milliseconds."),
    viewport: str | None = typer.Option(None, "--viewport", help="Browser viewport as WIDTHxHEIGHT."),
    user_agent: str | None = typer.Option(None, "--user-agent", help="Optional assessment user agent."),
    wait_until: str | None = typer.Option(
        None,
        "--wait-until",
        help="Playwright wait condition: load, domcontentloaded, commit, or networkidle.",
    ),
    full_page: bool | None = typer.Option(None, "--full-page/--viewport-only", help="Capture full-page screenshots."),
    capture_har: bool | None = typer.Option(
        None,
        "--har/--no-har",
        help="Opt-in HAR capture. Sensitive values are redacted locally.",
    ),
    ascii_art: bool = typer.Option(True, "--ascii/--no-ascii", help="Show subtle WebPhantom ASCII branding."),
    pulse: bool = typer.Option(False, "--pulse", help="Show brief terminal-style startup lines."),
) -> None:
    """Visit an explicit target URL and save screenshots, metadata, JSON, and Markdown."""
    if ascii_art:
        render_banner(console, compact=False)
    if pulse:
        render_boot_animation(console)
        render_startup_pulse(console)
    console.print(Panel(AUTHORIZED_USE_NOTICE, title="Authorized Use Only", border_style="yellow"))
    validate_target_url(url)
    scan_profile = load_scan_profile(profile) if profile else None
    max_pages = resolve_profile_value(scan_profile, "max_pages", max_pages, 5)
    allow_external = resolve_profile_value(scan_profile, "allow_external", allow_external, False)
    timeout = resolve_profile_value(scan_profile, "timeout", timeout, 15000)
    viewport = resolve_profile_value(scan_profile, "viewport", viewport, "1365x768")
    user_agent = resolve_profile_value(scan_profile, "user_agent", user_agent, None)
    wait_until = resolve_profile_value(scan_profile, "wait_until", wait_until, "networkidle")
    full_page = resolve_profile_value(scan_profile, "full_page", full_page, True)
    capture_har = resolve_profile_value(scan_profile, "capture_har", capture_har, False)

    width, height = parse_viewport(viewport)
    if max_pages < 1 or max_pages > 25:
        raise typer.BadParameter("max_pages must be between 1 and 25")
    if wait_until not in {"load", "domcontentloaded", "commit", "networkidle"}:
        raise typer.BadParameter("wait_until must be one of: load, domcontentloaded, commit, networkidle")

    output_dir = create_project_dir(output, url)
    policy = ScopePolicy(
        seed_url=url,
        allow_external=allow_external,
        max_pages=max_pages,
        timeout_ms=timeout,
        viewport_width=width,
        viewport_height=height,
        user_agent=user_agent,
        wait_until=wait_until,
        full_page=full_page,
        capture_har=capture_har,
    )

    with console.status("[bold green]Running headless browser assessment..."):
        result = asyncio.run(run_scan(policy, output_dir))
        result = result.__class__.create(
            target_url=result.target_url,
            output_dir=result.output_dir,
            pages=result.pages,
            navigation_graph=result.navigation_graph,
            warnings=result.warnings,
            network=result.network,
            evidence=build_evidence_manifest(output_dir),
        )
        json_path = write_json(result, output_dir)
        manifest_path = write_evidence_manifest(result.evidence, output_dir)
        markdown_path = write_markdown(result, output_dir)
        html_path = write_html(result, output_dir)

    console.print("[bold green]Scan complete[/bold green]")
    render_scan_table(result)
    console.print(f"Project folder: [cyan]{output_dir}[/cyan]")
    console.print(f"JSON: [cyan]{json_path}[/cyan]")
    console.print(f"Markdown: [cyan]{markdown_path}[/cyan]")
    console.print(f"HTML: [cyan]{html_path}[/cyan]")
    console.print(f"Evidence manifest: [cyan]{manifest_path}[/cyan]")


@app.command()
def show(
    result_file: Path = typer.Argument(..., help="Path to webphantom-results.json."),
    ascii_art: bool = typer.Option(False, "--ascii/--no-ascii", help="Show compact WebPhantom branding."),
) -> None:
    """Summarize a previously generated WebPhantom JSON result."""
    if ascii_art:
        render_banner(console, compact=True)
    payload = json.loads(result_file.read_text(encoding="utf-8"))
    table = Table(title="Stored Scan Summary")
    table.add_column("Metric")
    table.add_column("Value", justify="right")
    table.add_row("Target", payload.get("target_url", "unknown"))
    table.add_row("Created", payload.get("created_at", "unknown"))
    for key, label in [
        ("pages", "Pages"),
        ("forms", "Forms"),
        ("links", "Links"),
        ("network_requests", "Network"),
        ("external_requests", "External"),
        ("observations", "Observations"),
        ("high_observations", "High"),
        ("medium_observations", "Medium"),
        ("low_observations", "Low"),
        ("risk_score", "Risk Score"),
    ]:
        table.add_row(label, str(payload.get("stats", {}).get(key, 0)))
    console.print(table)


@app.command("init-profile")
def init_profile(
    path: Path = typer.Option(Path("examples/scan-profile.json"), "--path", "-p", help="Profile path to create."),
    force: bool = typer.Option(False, "--force", help="Overwrite an existing profile."),
) -> None:
    """Create a sample JSON scan profile."""
    if path.exists() and not force:
        raise typer.BadParameter(f"{path} already exists. Use --force to overwrite.")
    created = write_sample_profile(path)
    console.print(f"Scan profile written to [cyan]{created}[/cyan]")


@app.command()
def doctor() -> None:
    """Check local runtime dependencies and browser availability."""
    table = Table(title="WebPhantom Doctor")
    table.add_column("Check")
    table.add_column("Status")
    table.add_row("WebPhantom", __version__)
    try:
        import playwright  # noqa: F401

        table.add_row("Playwright package", "ok")
    except ImportError:
        table.add_row("Playwright package", "missing")
    try:
        from playwright.sync_api import sync_playwright

        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(headless=True)
            browser.close()
        table.add_row("Chromium browser", "ok")
    except Exception as exc:  # pragma: no cover - environment dependent
        table.add_row("Chromium browser", f"check failed: {exc}")
    console.print(table)


@app.command()
def banner(
    compact: bool = typer.Option(False, "--compact", help="Print compact banner."),
    animate: bool = typer.Option(False, "--animate", help="Print the optional terminal boot animation."),
) -> None:
    """Print the WebPhantom terminal banner."""
    render_banner(console, compact=compact)
    if animate:
        render_boot_animation(console)


def parse_viewport(value: str) -> tuple[int, int]:
    try:
        width_text, height_text = value.lower().split("x", maxsplit=1)
        width = int(width_text)
        height = int(height_text)
    except ValueError as exc:
        raise typer.BadParameter("Viewport must use WIDTHxHEIGHT format, for example 1365x768.") from exc
    if width < 320 or height < 240:
        raise typer.BadParameter("Viewport must be at least 320x240.")
    return width, height


def render_scan_table(result) -> None:
    table = Table(title="Scan Summary")
    table.add_column("Metric")
    table.add_column("Value", justify="right")
    table.add_row("Pages", str(result.stats.get("pages", 0)))
    table.add_row("Forms", str(result.stats.get("forms", 0)))
    table.add_row("Links", str(result.stats.get("links", 0)))
    table.add_row("Cookies", str(result.stats.get("cookies", 0)))
    table.add_row("Observations", str(result.stats.get("observations", 0)))
    table.add_row("High", str(result.stats.get("high_observations", 0)))
    table.add_row("Medium", str(result.stats.get("medium_observations", 0)))
    table.add_row("Low", str(result.stats.get("low_observations", 0)))
    table.add_row("Network", str(result.stats.get("network_requests", 0)))
    table.add_row("External", str(result.stats.get("external_requests", 0)))
    table.add_row("Risk Score", str(result.stats.get("risk_score", 0)))
    console.print(table)


@app.command("demo-server")
def demo_server(
    host: str = typer.Option("127.0.0.1", "--host", help="Demo server host."),
    port: int = typer.Option(8765, "--port", help="Demo server port."),
) -> None:
    """Run a local intentionally harmless demo target for WebPhantom scans."""
    from http.server import ThreadingHTTPServer

    from webphantom.examples.demo_server import DemoHandler

    server = ThreadingHTTPServer((host, port), DemoHandler)
    console.print(f"Demo target running at [cyan]http://{host}:{port}[/cyan]")
    console.print("Press Ctrl+C to stop.")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        console.print("Stopping demo server.")
    finally:
        server.server_close()


if __name__ == "__main__":
    app()
