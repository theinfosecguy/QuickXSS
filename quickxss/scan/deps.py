"""Dependency checks for QuickXSS."""

from __future__ import annotations

import subprocess
from pathlib import Path
from shutil import which
from typing import Iterable

from quickxss.scan.errors import DependencyError


def missing_binaries(names: Iterable[str]) -> list[str]:
    """Return a list of missing binaries from PATH."""

    return [name for name in names if which(name) is None]


def check_binaries(required: Iterable[str]) -> None:
    """Raise DependencyError if any required binaries are missing."""

    missing = missing_binaries(required)
    if missing:
        joined = ", ".join(missing)
        raise DependencyError(f"Missing required tools: {joined}.")


def check_gf_pattern(pattern: str) -> None:
    """Ensure the requested gf pattern exists."""

    gf_dir = Path.home() / ".gf"
    pattern_file = gf_dir / f"{pattern}.json"
    if pattern_file.exists():
        return

    # Fall back to `gf -list` when pattern files are managed elsewhere.
    try:
        result = subprocess.run(
            ["gf", "-list"],
            capture_output=True,
            text=True,
            check=False,
        )
    except FileNotFoundError as exc:
        raise DependencyError("gf is not installed or not on PATH.") from exc

    patterns = {line.strip() for line in result.stdout.splitlines() if line.strip()}
    if pattern in patterns:
        return

    raise DependencyError(
        f"gf pattern '{pattern}' not found. Install gf patterns in ~/.gf."
    )
