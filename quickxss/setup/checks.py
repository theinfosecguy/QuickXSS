"""Setup checks for external dependencies."""

from __future__ import annotations

import platform
import subprocess
from pathlib import Path
from shutil import which
from typing import Dict, Iterable, Set

from quickxss.constants.platform import APT_CMD, BREW_CMD, OS_DARWIN, OS_LINUX


def detect_tools(tools: Iterable[str]) -> Dict[str, bool]:
    """Return a tool availability map."""

    return {tool: which(tool) is not None for tool in tools}


def detect_os() -> str:
    """Return a normalized OS identifier."""

    return platform.system().lower()


def has_brew() -> bool:
    """Return True when Homebrew is available."""

    return which(BREW_CMD) is not None


def has_apt() -> bool:
    """Return True when apt-get is available."""

    return which(APT_CMD) is not None


def install_supported(os_name: str) -> bool:
    """Return True when auto-install is supported for the OS."""

    if os_name == OS_DARWIN:
        return has_brew()
    if os_name == OS_LINUX:
        return has_apt()
    return False


def has_gf_pattern(pattern: str, gf_available: bool) -> bool:
    """Check whether the requested gf pattern exists."""

    if not gf_available:
        return False

    gf_dir = Path.home() / ".gf"
    pattern_file = gf_dir / f"{pattern}.json"
    if pattern_file.exists():
        return True

    try:
        result = subprocess.run(
            ["gf", "-list"],
            capture_output=True,
            text=True,
            check=False,
        )
    except FileNotFoundError:
        return False

    patterns: Set[str] = {line.strip() for line in result.stdout.splitlines() if line.strip()}
    return pattern in patterns
