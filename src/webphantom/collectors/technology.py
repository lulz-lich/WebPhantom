from __future__ import annotations


async def detect_technologies(page, headers: dict[str, str]) -> list[str]:
    technologies: set[str] = set()
    normalized_headers = {key.lower(): value for key, value in headers.items()}

    server = normalized_headers.get("server")
    powered_by = normalized_headers.get("x-powered-by")
    if server:
        technologies.add(f"Server: {server}")
    if powered_by:
        technologies.add(f"X-Powered-By: {powered_by}")

    dom_signals = await page.evaluate(
        """
        () => ({
          react: Boolean(window.React || document.querySelector('[data-reactroot], [data-reactid]')),
          vue: Boolean(window.Vue || document.querySelector('[data-v-app]')),
          angular: Boolean(window.angular || document.querySelector('[ng-app], [ng-version]')),
          next: Boolean(window.__NEXT_DATA__),
          wordpress: Boolean(document.querySelector(
            'meta[name="generator"][content*="WordPress"], link[href*="wp-content"]'
          )),
          jquery: Boolean(window.jQuery)
        })
        """
    )
    for name, present in dom_signals.items():
        if present:
            technologies.add(name.title())
    return sorted(technologies)
