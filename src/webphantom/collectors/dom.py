from __future__ import annotations

from urllib.parse import urljoin

from webphantom.models import FormField, FormRecord, LinkRecord
from webphantom.safety import same_origin


async def collect_forms(page) -> list[FormRecord]:
    raw_forms = await page.locator("form").evaluate_all(
        """
        forms => forms.map(form => ({
          action: form.getAttribute('action') || '',
          method: (form.getAttribute('method') || 'GET').toUpperCase(),
          fields: Array.from(form.querySelectorAll('input, textarea, select')).map(field => ({
            name: field.getAttribute('name') || field.getAttribute('id') || '',
            field_type: field.getAttribute('type') || field.tagName.toLowerCase(),
            required: field.hasAttribute('required'),
            placeholder: field.getAttribute('placeholder') || ''
          }))
        }))
        """
    )
    base_url = page.url
    return [
        FormRecord(
            action=urljoin(base_url, item["action"]),
            method=item["method"],
            fields=[
                FormField(
                    name=field["name"],
                    field_type=field["field_type"],
                    required=bool(field["required"]),
                    placeholder=field["placeholder"],
                )
                for field in item["fields"]
            ],
        )
        for item in raw_forms
    ]


async def collect_links(page, seed_url: str, allow_external: bool) -> list[LinkRecord]:
    raw_links = await page.locator("a[href]").evaluate_all(
        """
        links => links.map(link => ({
          text: (link.innerText || link.getAttribute('aria-label') || '').trim(),
          href: link.getAttribute('href') || ''
        }))
        """
    )
    records: list[LinkRecord] = []
    seen: set[str] = set()
    for item in raw_links:
        raw_href = item["href"].strip()
        if raw_href.startswith(("mailto:", "tel:", "javascript:")):
            continue
        href = urljoin(page.url, raw_href)
        if href in seen:
            continue
        internal = same_origin(seed_url, href)
        if internal or allow_external:
            records.append(LinkRecord(text=item["text"][:120], href=href, internal=internal))
            seen.add(href)
    return records
