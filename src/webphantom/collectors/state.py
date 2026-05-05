from __future__ import annotations


async def collect_interesting_states(page) -> list[str]:
    notes: list[str] = []
    title = await page.title()
    if title:
        notes.append(f"Page title observed: {title}")

    password_fields = await page.locator("input[type='password']").count()
    if password_fields:
        notes.append("Authentication-like form detected.")

    file_inputs = await page.locator("input[type='file']").count()
    if file_inputs:
        notes.append("File upload input detected.")

    admin_words = await page.locator("text=/admin|dashboard|settings|profile/i").count()
    if admin_words:
        notes.append("Administrative or account-management wording observed.")

    return notes
