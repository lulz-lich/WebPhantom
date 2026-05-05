# Architecture

WebPhantom is intentionally modular so collectors can evolve without turning the project into an exploitation framework.

## Main Flow

1. The CLI validates an explicitly provided URL and builds a `ScopePolicy`.
2. The browser runner launches an isolated Playwright Chromium context.
3. Collectors extract passive browser-observable data from each visited page.
4. Storage helpers write JSON, Markdown, HTML, screenshots, optional HAR, and evidence hashes.
5. Reports summarize evidence and passive observations.

## Packages

- `cli`: Typer/Rich user interface, banner, doctor, profiles, and reporting commands.
- `browser`: Playwright orchestration and same-origin crawl loop.
- `collectors`: DOM, headers, technology, state, network, and passive security observations.
- `storage`: project folders, JSON output, HAR redaction, and evidence manifests.
- `reports`: Markdown and HTML renderers.
- `examples`: local harmless demo target.

## Safety Invariants

- Only a user-provided seed URL starts a scan.
- External links are blocked unless `--allow-external` is used.
- Page visits are capped.
- No form submission, payload injection, authentication bypass, credential capture, brute forcing, or exploit execution is implemented.
- Sensitive header and cookie values are redacted or omitted from standard artifacts.
