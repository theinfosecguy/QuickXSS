"""Unit tests for quickxss.scan.errors module."""

from __future__ import annotations

import pytest

from quickxss.scan.errors import (
    DependencyError,
    OperationError,
    QuickXSSError,
    ToolError,
    ValidationError,
)


def test_quickxss_error_is_exception() -> None:
    """QuickXSSError should be an Exception."""
    error = QuickXSSError("test error")
    assert isinstance(error, Exception)


def test_quickxss_error_message() -> None:
    """QuickXSSError should store message."""
    error = QuickXSSError("test message")
    assert str(error) == "test message"


def test_validation_error_inherits_from_base() -> None:
    """ValidationError should inherit from QuickXSSError."""
    error = ValidationError("invalid input")
    assert isinstance(error, QuickXSSError)
    assert isinstance(error, Exception)


def test_validation_error_message() -> None:
    """ValidationError should store message."""
    error = ValidationError("domain is required")
    assert str(error) == "domain is required"


def test_dependency_error_inherits_from_base() -> None:
    """DependencyError should inherit from QuickXSSError."""
    error = DependencyError("missing tool")
    assert isinstance(error, QuickXSSError)


def test_dependency_error_message() -> None:
    """DependencyError should store message."""
    error = DependencyError("gf not found")
    assert str(error) == "gf not found"


def test_tool_error_inherits_from_base() -> None:
    """ToolError should inherit from QuickXSSError."""
    error = ToolError("command failed")
    assert isinstance(error, QuickXSSError)


def test_tool_error_message() -> None:
    """ToolError should store message."""
    error = ToolError("dalfox failed")
    assert str(error) == "dalfox failed"


def test_tool_error_stores_command() -> None:
    """ToolError should store command list."""
    error = ToolError("command failed", command=["gf", "xss"])
    assert error.command == ["gf", "xss"]


def test_tool_error_command_default_empty() -> None:
    """ToolError command should default to empty list."""
    error = ToolError("command failed")
    assert error.command == []


def test_tool_error_with_none_command() -> None:
    """ToolError with None command should use empty list."""
    error = ToolError("command failed", command=None)
    assert error.command == []


def test_operation_error_inherits_from_base() -> None:
    """OperationError should inherit from QuickXSSError."""
    error = OperationError("write failed")
    assert isinstance(error, QuickXSSError)


def test_operation_error_message() -> None:
    """OperationError should store message."""
    error = OperationError("failed to write file")
    assert str(error) == "failed to write file"


def test_all_errors_catchable_as_base() -> None:
    """All errors should be catchable as QuickXSSError."""
    errors = [
        ValidationError("validation"),
        DependencyError("dependency"),
        ToolError("tool"),
        OperationError("operation"),
    ]
    for error in errors:
        try:
            raise error
        except QuickXSSError as e:
            assert str(e) in ["validation", "dependency", "tool", "operation"]


def test_errors_are_distinct() -> None:
    """Each error type should be distinguishable."""
    with pytest.raises(ValidationError):
        raise ValidationError("test")

    with pytest.raises(DependencyError):
        raise DependencyError("test")

    with pytest.raises(ToolError):
        raise ToolError("test")

    with pytest.raises(OperationError):
        raise OperationError("test")
