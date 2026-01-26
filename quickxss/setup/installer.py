"""Installer helpers for setup."""

from __future__ import annotations

import shutil
import tempfile
from pathlib import Path
from typing import Iterable

from quickxss.constants.platform import APT_CMD, BREW_CMD, OS_DARWIN, OS_LINUX
from quickxss.constants.tools import GF_PATTERNS_REPO_URL, GF_REPO_URL, GO_TOOLS
from quickxss.scan.errors import ToolError
from quickxss.utils.exec import run_command
from quickxss.utils.fs import copy_tree
from quickxss.utils.log import Logger


def install_system_packages(os_name: str, packages: Iterable[str], logger: Logger) -> None:
    """Install system packages via brew or apt-get."""

    if not packages:
        return

    if os_name == OS_DARWIN:
        run_command([BREW_CMD, "install", *packages], logger)
        return

    if os_name == OS_LINUX:
        run_command([APT_CMD, "update"], logger)
        run_command([APT_CMD, "install", "-y", *packages], logger)
        return

    raise ToolError("Auto-install is not supported on this OS.")


def install_go_tools(missing_tools: Iterable[str], logger: Logger) -> None:
    """Install missing Go-based tools via go install."""

    for tool in missing_tools:
        module = GO_TOOLS.get(tool)
        if not module:
            continue
        run_command(["go", "install", module], logger)


def install_gf_patterns(logger: Logger) -> None:
    """Install gf patterns into ~/.gf."""

    gf_dir = Path.home() / ".gf"
    gf_dir.mkdir(parents=True, exist_ok=True)

    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        gf_repo = temp_path / "gf"
        patterns_repo = temp_path / "Gf-Patterns"

        run_command(
            [
                "git",
                "clone",
                "--depth",
                "1",
                GF_REPO_URL,
                str(gf_repo),
            ],
            logger,
        )
        run_command(
            [
                "git",
                "clone",
                "--depth",
                "1",
                GF_PATTERNS_REPO_URL,
                str(patterns_repo),
            ],
            logger,
        )

        copy_tree(gf_repo / "examples", gf_dir)
        for pattern in patterns_repo.glob("*.json"):
            shutil.copy2(pattern, gf_dir / pattern.name)
