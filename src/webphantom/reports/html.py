from __future__ import annotations

from html import escape
from pathlib import Path

from webphantom.models import ScanResult


def render_html(result: ScanResult) -> str:
    pages = "\n".join(_render_page(page) for page in result.pages)
    observations = "\n".join(
        f"<li><strong>{escape(obs.severity.title())}</strong> {escape(obs.title)} "
        f"<span>{escape(obs.category)}</span><p>{escape(obs.recommendation)}</p></li>"
        for page in result.pages
        for obs in page.observations
    )
    network = "\n".join(
        f"<tr><td>{escape(str(record.status))}</td><td>{escape(record.method)}</td>"
        f"<td>{escape(record.resource_type)}</td><td>{escape('internal' if record.internal else 'external')}</td>"
        f"<td>{escape(record.url)}</td></tr>"
        for record in result.network[:50]
    )
    evidence = "\n".join(
        f"<li><code>{escape(item.path)}</code> <code>{escape(item.sha256)}</code> {item.size_bytes} bytes</li>"
        for item in result.evidence
    )
    style = """
    :root {
      color-scheme: dark;
      --bg:#070b0d; --panel:#10171c; --line:#24313a; --text:#e8f1f2;
      --muted:#9ab0b7; --accent:#63f7a4; --warn:#ffd166;
    }
    body {
      margin:0;
      font:14px/1.55 ui-monospace, SFMono-Regular, Consolas, monospace;
      background:var(--bg);
      color:var(--text);
    }
    header {
      padding:32px;
      border-bottom:1px solid var(--line);
      background:linear-gradient(135deg,#08110d,#10171c);
    }
    h1 { margin:0 0 8px; color:var(--accent); font-size:32px; letter-spacing:0; }
    h2 { margin-top:32px; color:var(--accent); }
    main { max-width:1180px; margin:0 auto; padding:24px; }
    .grid {
      display:grid;
      grid-template-columns:repeat(auto-fit,minmax(160px,1fr));
      gap:12px;
    }
    .card, section {
      background:var(--panel);
      border:1px solid var(--line);
      border-radius:8px;
      padding:16px;
    }
    .metric { color:var(--muted); }
    .metric strong { display:block; color:var(--text); font-size:24px; }
    code { color:var(--accent); word-break:break-all; }
    img { max-width:100%; border:1px solid var(--line); border-radius:6px; }
    table { width:100%; border-collapse:collapse; }
    th, td {
      border-bottom:1px solid var(--line);
      padding:8px;
      text-align:left;
      vertical-align:top;
    }
    p, li, td { color:var(--muted); }
    strong { color:var(--text); }
    """
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>WebPhantom Report</title>
  <style>{style}</style>
</head>
<body>
  <header>
    <h1>WebPhantom</h1>
    <div>authorized browser reconnaissance // evidence-first // no exploit path</div>
    <p>Target: <code>{escape(result.target_url)}</code><br>Generated: <code>{escape(result.created_at)}</code></p>
  </header>
  <main>
    <div class="grid">
      {_metric("Pages", result.stats.get("pages", 0))}
      {_metric("Forms", result.stats.get("forms", 0))}
      {_metric("Network", result.stats.get("network_requests", 0))}
      {_metric("Observations", result.stats.get("observations", 0))}
      {_metric("Risk Score", result.stats.get("risk_score", 0))}
    </div>
    <h2>Executive Observations</h2>
    <section><ul>{observations or "<li>No passive observations recorded.</li>"}</ul></section>
    <h2>Pages</h2>
    {pages}
    <h2>Network Inventory</h2>
    <section><table><thead><tr><th>Status</th><th>Method</th><th>Type</th><th>Scope</th><th>URL</th></tr></thead><tbody>{network}</tbody></table></section>
    <h2>Evidence</h2>
    <section><ul>{evidence or "<li>No screenshot evidence recorded.</li>"}</ul></section>
  </main>
</body>
</html>
"""


def _metric(label: str, value: int) -> str:
    return f'<div class="card metric">{escape(label)}<strong>{value}</strong></div>'


def _render_page(page) -> str:
    if page.screenshot:
        screenshot = (
            f'<img src="{escape(page.screenshot)}" '
            f'alt="Screenshot for {escape(page.title or page.url)}">'
        )
    else:
        screenshot = ""
    return f"""
    <section>
      <h3>{escape(page.title or page.url)}</h3>
      <p><code>{escape(page.url)}</code> status <strong>{escape(str(page.status))}</strong></p>
      {screenshot}
    </section>
    """


def write_html(result: ScanResult, output_dir: Path) -> Path:
    path = output_dir / "report.html"
    path.write_text(render_html(result), encoding="utf-8")
    return path
