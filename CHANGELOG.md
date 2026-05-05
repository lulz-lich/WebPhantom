# Changelog

## 1.0.0 - 2026-05-05

Initial professional release of WebPhantom.

### Added

- Headless browser scan workflow for explicitly provided URLs.
- Full-page screenshots, response headers, cookie metadata, forms, links, navigation graph, and technology hints.
- Passive security observations for common headers, cookie attributes, and unsafe password-form patterns.
- Passive network inventory with internal/external classification.
- JSON, Markdown, and HTML reports.
- SHA-256 evidence manifest for screenshots and opt-in artifacts.
- Optional HAR capture with local redaction of sensitive header and cookie values.
- JSON scan profiles and `init-profile` helper.
- `doctor`, `show`, `banner`, and `demo-server` CLI commands.
- Local harmless demo target.
- GitHub-ready documentation, CI workflow, issue templates, and release checklist.

### Safety

- Same-origin navigation by default.
- Page cap with `--max-pages`.
- No exploitation, brute forcing, credential collection, persistence, stealth, or exfiltration features.
- Sensitive headers and cookie values are redacted or omitted from standard outputs.
