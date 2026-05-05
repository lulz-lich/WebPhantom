# WebPhantom

WebPhantom is a headless browser security automation toolkit for authorized web assessments. It visits an explicitly provided URL, captures screenshots, records browser-observable metadata, extracts forms and links, builds a small navigation graph, and exports local JSON and Markdown reports.

It is designed for reconnaissance documentation, assessment evidence, and detection-aware reporting. It is not an exploitation framework.

## What It Captures

- Full-page screenshots.
- Response headers.
- Cookies visible to the browser context, stored locally for documentation only.
- Forms, methods, actions, and input fields.
- Links and a basic in-scope navigation graph.
- Page titles and simple application-state notes.
- Lightweight technology hints from headers and DOM signals.
- Passive network response inventory.
- SHA-256 evidence manifest for generated screenshots.
- JSON, Markdown, and HTML summaries in a local project folder.
- Optional HAR capture with local redaction.
- JSON scan profiles for repeatable assessment settings.

## Safety Model

WebPhantom is intentionally scoped and passive:

- It starts only from a URL explicitly supplied by the user.
- External origins are blocked by default.
- Page visits are capped with `--max-pages`.
- It does not brute force, fuzz, exploit, bypass authentication, submit credentials, collect passwords, persist, hide activity, or exfiltrate data.
- Cookie names and security attributes are written only to the local output folder; cookie values and sensitive header values are redacted.

Use WebPhantom only on systems you own or have explicit written permission to assess.

## Project Structure

```text
webphantom/
  src/webphantom/
    cli/
      app.py
    browser/
      runner.py
    collectors/
      dom.py
      state.py
      technology.py
    storage/
      project.py
    reports/
      markdown.py
    examples/
      demo_server.py
    models.py
    safety.py
  examples/
    README.md
  tests/
  docs/
    safety.md
  README.md
  pyproject.toml
```

## Installation

Create a virtual environment, install the project with browser extras, and install Chromium for Playwright:

```bash
python -m venv .venv
.venv\Scripts\activate
python -m pip install -e .[dev]
playwright install chromium
```

On macOS/Linux, activate with:

```bash
source .venv/bin/activate
```

## Quick Start With Local Demo Target

Run the harmless local demo server:

```bash
webphantom demo-server
```

In another terminal:

```bash
webphantom scan http://127.0.0.1:8765 --max-pages 4 --output runs
```

WebPhantom creates a timestamped folder under `runs/` containing:

```text
screenshots/
artifacts/
webphantom-results.json
evidence-manifest.json
README.md
report.html
```

## CLI Usage

Scan one explicit URL:

```bash
webphantom scan https://example.com --max-pages 3 --output runs
```

Run quietly for automation:

```bash
webphantom scan https://example.com --no-ascii --max-pages 3 --output runs
```

Show the terminal banner:

```bash
webphantom banner
```

Show the optional ASCII boot animation:

```bash
webphantom banner --animate
```

Tune browser behavior:

```bash
webphantom scan https://example.com --viewport 1440x900 --wait-until domcontentloaded --user-agent "WebPhantom-AuthorizedAssessment/0.1"
```

Use a repeatable profile:

```bash
webphantom init-profile --path examples/scan-profile.json
webphantom scan https://example.com --profile examples/scan-profile.json
```

Capture a redacted HAR artifact when authorized:

```bash
webphantom scan https://example.com --har --max-pages 3
```

Allow external-origin links when you have authorization for the broader scope:

```bash
webphantom scan https://example.com --allow-external --max-pages 5
```

Adjust timeout:

```bash
webphantom scan https://example.com --timeout 30000
```

Show version:

```bash
webphantom --version
```

Summarize an existing scan result:

```bash
webphantom show runs/example.com-20260505T194500Z/webphantom-results.json
```

Check local runtime health:

```bash
webphantom doctor
```

## Output Example

```text
runs/example.com-20260505T194500Z/
  screenshots/
    01-https-example-com.png
  evidence-manifest.json
  webphantom-results.json
  report.html
  README.md
```

The Markdown report is designed for quick review and portfolio screenshots. The JSON report is designed for automation, evidence handling, or future integrations.

## Evidence Handling

Each scan writes a local `evidence-manifest.json` containing SHA-256 hashes and file sizes for screenshot artifacts. This helps preserve assessment evidence integrity without sending files anywhere.

The JSON result also includes a passive network inventory with URL, method, resource type, status, content type, and whether the response was in scope.

HAR capture is available with `--har`. It is opt-in because HAR files can contain sensitive browser metadata. WebPhantom redacts sensitive header and cookie values locally before writing the artifact.

## Passive Security Observations

WebPhantom includes safe, non-exploitative checks that help document defensive posture:

- Missing common security headers.
- Cookie attributes such as `Secure`, `HttpOnly`, and `SameSite`.
- Password fields over HTTP.
- Password fields submitted through GET forms.

These observations are documentation aids, not vulnerability proof. Validate them manually before including them in a formal report.

## Development

Run tests:

```bash
python -m pytest
```

Run without installing the console script:

```bash
PYTHONPATH=src python -m webphantom.cli.app scan http://127.0.0.1:8765
```

PowerShell equivalent:

```powershell
$env:PYTHONPATH="src"; python -m webphantom.cli.app scan http://127.0.0.1:8765
```

## Portfolio Highlights

WebPhantom demonstrates:

- Safe browser automation for authorized assessments.
- Practical reconnaissance documentation.
- Clean Python package architecture.
- Modular collectors and report generation.
- Evidence integrity via SHA-256 manifests.
- Passive network inventory without exploit behavior.
- Subtle terminal identity with optional ASCII branding.
- Local evidence storage with screenshots and structured JSON.
- Clear ethical scope and guardrails.

## Roadmap

- Optional PDF report export.
- Screenshot diffing between runs.
- Additional passive technology fingerprints.
- Integration tests against the bundled local demo server.

## License

MIT License. Use responsibly and only for authorized, ethical security work.
