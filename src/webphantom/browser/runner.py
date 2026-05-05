from __future__ import annotations

import re
from collections import deque
from pathlib import Path
from urllib.parse import urldefrag

from webphantom.collectors.dom import collect_forms, collect_links
from webphantom.collectors.headers import sanitize_headers
from webphantom.collectors.network import register_network_collector
from webphantom.collectors.security import evaluate_security_posture
from webphantom.collectors.state import collect_interesting_states
from webphantom.collectors.technology import detect_technologies
from webphantom.models import CookieRecord, NetworkRecord, PageSnapshot, ScanResult, ScopePolicy
from webphantom.safety import same_origin, validate_target_url
from webphantom.storage.har import sanitize_har_file


def slugify_url(url: str) -> str:
    slug = re.sub(r"[^a-zA-Z0-9]+", "-", url).strip("-").lower()
    return slug[:80] or "page"


def normalize_url(url: str) -> str:
    return urldefrag(url)[0].rstrip("/") or url


async def run_scan(policy: ScopePolicy, output_dir: Path) -> ScanResult:
    validate_target_url(policy.seed_url)
    try:
        from playwright.async_api import TimeoutError as PlaywrightTimeoutError
        from playwright.async_api import async_playwright
    except ImportError as exc:
        raise RuntimeError(
            "Playwright is required for browser scans. Install with "
            "`python -m pip install -e .` and then run `playwright install chromium`."
        ) from exc

    screenshots_dir = output_dir / "screenshots"
    screenshots_dir.mkdir(parents=True, exist_ok=True)
    artifacts_dir = output_dir / "artifacts"
    har_path = artifacts_dir / "network.har"
    if policy.capture_har:
        artifacts_dir.mkdir(parents=True, exist_ok=True)

    pages: list[PageSnapshot] = []
    navigation_graph: dict[str, list[str]] = {}
    warnings = [
        "Only URLs explicitly provided by the user and in-scope discovered links were visited.",
        "Cookies are listed for documentation only and are not exported anywhere.",
    ]

    queue: deque[str] = deque([normalize_url(policy.seed_url)])
    visited: set[str] = set()
    network_records: list[NetworkRecord] = []

    async with async_playwright() as playwright:
        browser = await playwright.chromium.launch(headless=True)
        context_kwargs = {
            "ignore_https_errors": False,
            "viewport": {"width": policy.viewport_width, "height": policy.viewport_height},
        }
        if policy.capture_har:
            context_kwargs["record_har_path"] = str(har_path)
            context_kwargs["record_har_content"] = "omit"
        if policy.user_agent:
            context_kwargs["user_agent"] = policy.user_agent
        context = await browser.new_context(**context_kwargs)
        page = await context.new_page()
        register_network_collector(page, policy.seed_url, network_records)

        while queue and len(visited) < policy.max_pages:
            url = queue.popleft()
            if url in visited:
                continue
            if not policy.allow_external and not same_origin(policy.seed_url, url):
                continue

            normalized_url = normalize_url(url)
            if normalized_url in visited:
                continue
            visited.add(normalized_url)

            try:
                response = await page.goto(url, wait_until=policy.wait_until, timeout=policy.timeout_ms)
            except PlaywrightTimeoutError:
                warnings.append(f"Timed out while loading {url}. Partial page evidence may be unavailable.")
                continue

            status = response.status if response else None
            headers = sanitize_headers(await response.all_headers()) if response else {}

            screenshot_name = f"{len(pages) + 1:02d}-{slugify_url(url)}.png"
            screenshot_path = screenshots_dir / screenshot_name
            await page.screenshot(path=str(screenshot_path), full_page=policy.full_page)

            cookies = [
                CookieRecord(
                    name=item.get("name", ""),
                    domain=item.get("domain", ""),
                    path=item.get("path", ""),
                    secure=bool(item.get("secure", False)),
                    http_only=bool(item.get("httpOnly", False)),
                    same_site=item.get("sameSite"),
                    expires=item.get("expires"),
                )
                for item in await context.cookies(url)
            ]
            forms = await collect_forms(page)
            links = await collect_links(page, policy.seed_url, policy.allow_external)
            technologies = await detect_technologies(page, headers)
            notes = await collect_interesting_states(page)
            observations = evaluate_security_posture(url=page.url, headers=headers, cookies=cookies, forms=forms)

            navigation_graph[normalized_url] = [
                normalize_url(link.href) for link in links if link.internal or policy.allow_external
            ]
            for link in links:
                normalized_link = normalize_url(link.href)
                has_capacity = len(visited) + len(queue) < policy.max_pages
                if normalized_link not in visited and normalized_link not in queue and has_capacity:
                    if link.internal or policy.allow_external:
                        queue.append(normalized_link)

            pages.append(
                PageSnapshot(
                    url=url,
                    title=await page.title(),
                    status=status,
                    screenshot=str(screenshot_path.relative_to(output_dir)),
                    headers=dict(headers),
                    cookies=cookies,
                    forms=forms,
                    links=links,
                    technologies=technologies,
                    observations=observations,
                    notes=notes,
                )
            )

        await context.close()
        await browser.close()

    if policy.capture_har:
        sanitize_har_file(har_path)
        warnings.append("HAR capture was enabled; sensitive HAR header and cookie values were redacted locally.")

    return ScanResult.create(
        target_url=policy.seed_url,
        output_dir=str(output_dir),
        pages=pages,
        navigation_graph=navigation_graph,
        warnings=warnings,
        network=network_records,
    )
