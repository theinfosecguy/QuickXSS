"""Banner rendering for the CLI."""

from __future__ import annotations

import pyfiglet


def render_banner() -> str:
    """Render the QuickXSS banner using pyfiglet."""

    return pyfiglet.figlet_format("QuickXSS", font="standard")
