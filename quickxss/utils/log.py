"""Logging helpers for QuickXSS."""

from __future__ import annotations

import sys
from dataclasses import dataclass


@dataclass(slots=True)
class Logger:
    """Minimal logger with quiet/verbose controls."""

    verbose: bool
    quiet: bool

    def info(self, message: str) -> None:
        """Write an informational message."""

        if self.quiet:
            return
        print(message)

    def warn(self, message: str) -> None:
        """Write a warning message."""

        if self.quiet:
            return
        print(message, file=sys.stderr)

    def error(self, message: str) -> None:
        """Write an error message."""

        print(message, file=sys.stderr)

    def debug(self, message: str) -> None:
        """Write a debug message when verbose is enabled."""

        if not self.verbose or self.quiet:
            return
        print(message, file=sys.stderr)
