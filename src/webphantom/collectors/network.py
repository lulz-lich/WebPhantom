from __future__ import annotations

from webphantom.collectors.headers import sanitize_headers
from webphantom.models import NetworkRecord
from webphantom.safety import same_origin


def register_network_collector(page, seed_url: str, records: list[NetworkRecord]) -> None:
    async def on_response(response) -> None:
        request = response.request
        headers = sanitize_headers(await response.all_headers())
        records.append(
            NetworkRecord(
                url=response.url,
                method=request.method,
                resource_type=request.resource_type,
                status=response.status,
                content_type=headers.get("content-type", ""),
                internal=same_origin(seed_url, response.url),
            )
        )

    page.on("response", on_response)
