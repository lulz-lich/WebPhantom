# Safety and Scope

WebPhantom is designed for authorized assessment documentation. It is passive browser automation, not an exploitation framework.

## Guardrails

- The scanner starts only from a URL explicitly provided by the user.
- External navigation is disabled by default.
- Page visits are capped with `--max-pages`.
- No brute forcing, fuzzing, bypassing authentication, or exploit execution is implemented.
- Cookies are recorded as local metadata only and are never transmitted anywhere.
- Cookie values and sensitive response-header values are not written to reports.
- Network inventory is passive and records responses observed during normal browser navigation.
- Evidence hashes are generated locally and do not transmit artifacts.
- No credentials are collected, submitted, replayed, or exfiltrated.

## Recommended Use

- Use local demo targets during development.
- Obtain written authorization before scanning any third-party system.
- Keep output folders private if they contain internal URLs, headers, or cookies.
- Treat screenshots as assessment evidence.
- Manually validate passive observations before classifying them as reportable findings.
