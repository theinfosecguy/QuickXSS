"""Custom error types for QuickXSS."""

from __future__ import annotations


class QuickXSSError(Exception):
    """Base error for QuickXSS failures."""


class ValidationError(QuickXSSError):
    """Raised when user input is invalid."""


class DependencyError(QuickXSSError):
    """Raised when required external tools or patterns are missing."""


class ToolError(QuickXSSError):
    """Raised when an external tool returns a non-zero exit code."""

    def __init__(self, message: str, command: list[str] | None = None) -> None:
        super().__init__(message)
        self.command = command or []
