"""Platform and package manager constants."""

from __future__ import annotations

from typing import List

OS_DARWIN: str = "darwin"
OS_LINUX: str = "linux"
OS_WINDOWS: str = "windows"

INSTALL_OS: List[str] = [OS_DARWIN, OS_LINUX]

BREW_CMD: str = "brew"
APT_CMD: str = "apt-get"

GO_PKG_DARWIN: str = "go"
GO_PKG_LINUX: str = "golang-go"
