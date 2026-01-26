"""Project-wide constants."""

from __future__ import annotations

from quickxss.constants.platform import (
    APT_CMD,
    BREW_CMD,
    GO_PKG_DARWIN,
    GO_PKG_LINUX,
    INSTALL_OS,
    OS_DARWIN,
    OS_LINUX,
    OS_WINDOWS,
)
from quickxss.constants.tools import GF_PATTERNS_REPO_URL, GF_REPO_URL, GO_TOOLS, REQUIRED_TOOLS

CREDIT = "** Developed by theinfosecguy <3 **"

__all__ = [
    "APT_CMD",
    "BREW_CMD",
    "CREDIT",
    "GO_PKG_DARWIN",
    "GO_PKG_LINUX",
    "GF_PATTERNS_REPO_URL",
    "GF_REPO_URL",
    "GO_TOOLS",
    "INSTALL_OS",
    "OS_DARWIN",
    "OS_LINUX",
    "OS_WINDOWS",
    "REQUIRED_TOOLS",
]
