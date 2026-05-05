from __future__ import annotations

import time

from rich.console import Console
from rich.text import Text

BANNER = r"""
__        __   _     ____  _                 _
\ \      / /__| |__ |  _ \| |__   __ _ _ __ | |_ ___  _ __ ___
 \ \ /\ / / _ \ '_ \| |_) | '_ \ / _` | '_ \| __/ _ \| '_ ` _ \
  \ V  V /  __/ |_) |  __/| | | | (_| | | | | || (_) | | | | | |
   \_/\_/ \___|_.__/|_|   |_| |_|\__,_|_| |_|\__\___/|_| |_| |_|
""".strip("\n")

TAGLINE = "authorized browser reconnaissance // evidence-first // no exploit path"

STARTUP_PULSE = [
    "[scope] seed URL accepted",
    "[browser] launching isolated headless context",
    "[capture] screenshots, forms, links, headers, cookies",
    "[evidence] local JSON, Markdown, SHA-256 manifest",
]

PHANTOM_FRAMES = [
    r"[    ]   _.-.      acquiring visual context",
    r"[=   ]  (o o)     acquiring visual context",
    r"[==  ]   |=|      mapping browser-observable state",
    r"[=== ]  __|__     preserving local evidence",
    r"[====] /_____\    ready",
]


def render_banner(console: Console, *, compact: bool = False) -> None:
    style = "bold bright_green"
    if compact:
        console.print(Text("WebPhantom", style=style), Text(f"  {TAGLINE}", style="dim"))
        return
    console.print(Text(BANNER, style=style))
    console.print(Text(TAGLINE, style="dim"))


def render_startup_pulse(console: Console) -> None:
    for line in STARTUP_PULSE:
        console.print(f"[dim]{line}[/dim]")


def render_boot_animation(console: Console, *, delay: float = 0.05) -> None:
    for frame in PHANTOM_FRAMES:
        console.print(f"[green]{frame}[/green]")
        if delay > 0:
            time.sleep(delay)
