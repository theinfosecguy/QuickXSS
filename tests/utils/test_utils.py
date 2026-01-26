"""Unit tests for quickxss.utils modules."""

from __future__ import annotations

import io
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from quickxss.scan.errors import ToolError
from quickxss.utils.banner import render_banner
from quickxss.utils.exec import run_command
from quickxss.utils.fs import copy_tree
from quickxss.utils.log import Logger
from quickxss.utils.progress import Progress


def test_render_banner_returns_string() -> None:
    """Banner should return a non-empty string."""
    result = render_banner()
    assert isinstance(result, str)
    assert len(result) > 0


def test_render_banner_contains_quickxss() -> None:
    """Banner should contain 'QuickXSS' in some form."""
    result = render_banner()
    assert "Quick" in result or "_" in result or "/" in result


@patch("subprocess.run")
def test_run_command_success(mock_run: patch, quiet_logger: Logger) -> None:
    """Successful command should not raise."""
    mock_result = MagicMock()
    mock_result.returncode = 0
    mock_result.stderr = ""
    mock_run.return_value = mock_result

    run_command(["echo", "hello"], quiet_logger)
    mock_run.assert_called_once()


@patch("subprocess.run")
def test_run_command_failure_raises_tool_error(
    mock_run: patch, quiet_logger: Logger
) -> None:
    """Failed command should raise ToolError with stderr."""
    mock_result = MagicMock()
    mock_result.returncode = 1
    mock_result.stderr = "Command failed: error details"
    mock_run.return_value = mock_result

    with pytest.raises(ToolError) as exc_info:
        run_command(["failing_cmd"], quiet_logger)
    assert "Command failed: error details" in str(exc_info.value)


@patch("subprocess.run")
def test_run_command_failure_default_message(
    mock_run: patch, quiet_logger: Logger
) -> None:
    """Failed command with empty stderr should use default message."""
    mock_result = MagicMock()
    mock_result.returncode = 1
    mock_result.stderr = ""
    mock_run.return_value = mock_result

    with pytest.raises(ToolError) as exc_info:
        run_command(["failing_cmd"], quiet_logger)
    assert "Command failed" in str(exc_info.value)


@patch("subprocess.run")
def test_run_command_logs_debug(mock_run: patch, verbose_logger: Logger) -> None:
    """Command should log debug when verbose."""
    mock_result = MagicMock()
    mock_result.returncode = 0
    mock_result.stderr = ""
    mock_run.return_value = mock_result

    captured = io.StringIO()
    with patch.object(sys, "stderr", captured):
        run_command(["echo", "test"], verbose_logger)
    assert "Running:" in captured.getvalue()


def test_copy_tree_copies_files(tmp_path: Path) -> None:
    """Should copy files from source to destination."""
    source = tmp_path / "source"
    source.mkdir()
    (source / "file1.txt").write_text("content1")
    (source / "file2.txt").write_text("content2")

    dest = tmp_path / "dest"
    dest.mkdir()

    copy_tree(source, dest)

    assert (dest / "file1.txt").exists()
    assert (dest / "file2.txt").exists()
    assert (dest / "file1.txt").read_text() == "content1"
    assert (dest / "file2.txt").read_text() == "content2"


def test_copy_tree_copies_directories(tmp_path: Path) -> None:
    """Should copy directories recursively."""
    source = tmp_path / "source"
    source.mkdir()
    subdir = source / "subdir"
    subdir.mkdir()
    (subdir / "nested.txt").write_text("nested content")

    dest = tmp_path / "dest"
    dest.mkdir()

    copy_tree(source, dest)

    assert (dest / "subdir").is_dir()
    assert (dest / "subdir" / "nested.txt").exists()
    assert (dest / "subdir" / "nested.txt").read_text() == "nested content"


def test_copy_tree_overwrites_existing(tmp_path: Path) -> None:
    """Should overwrite existing files."""
    source = tmp_path / "source"
    source.mkdir()
    (source / "file.txt").write_text("new content")

    dest = tmp_path / "dest"
    dest.mkdir()
    (dest / "file.txt").write_text("old content")

    copy_tree(source, dest)

    assert (dest / "file.txt").read_text() == "new content"


def test_logger_info_prints_when_not_quiet(capsys) -> None:
    """Info should print when quiet is False."""
    logger = Logger(verbose=False, quiet=False)
    logger.info("test message")
    captured = capsys.readouterr()
    assert "test message" in captured.out


def test_logger_info_silent_when_quiet(capsys, quiet_logger: Logger) -> None:
    """Info should not print when quiet is True."""
    quiet_logger.info("test message")
    captured = capsys.readouterr()
    assert captured.out == ""


def test_logger_warn_prints_to_stderr(capsys) -> None:
    """Warn should print to stderr when not quiet."""
    logger = Logger(verbose=False, quiet=False)
    logger.warn("warning message")
    captured = capsys.readouterr()
    assert "warning message" in captured.err


def test_logger_warn_silent_when_quiet(capsys, quiet_logger: Logger) -> None:
    """Warn should not print when quiet is True."""
    quiet_logger.warn("warning message")
    captured = capsys.readouterr()
    assert captured.err == ""


def test_logger_error_always_prints(capsys, quiet_logger: Logger) -> None:
    """Error should always print to stderr even when quiet."""
    quiet_logger.error("error message")
    captured = capsys.readouterr()
    assert "error message" in captured.err


def test_logger_debug_prints_when_verbose(capsys, verbose_logger: Logger) -> None:
    """Debug should print when verbose is True and quiet is False."""
    verbose_logger.debug("debug message")
    captured = capsys.readouterr()
    assert "debug message" in captured.err


def test_logger_debug_silent_when_not_verbose(capsys) -> None:
    """Debug should not print when verbose is False."""
    logger = Logger(verbose=False, quiet=False)
    logger.debug("debug message")
    captured = capsys.readouterr()
    assert captured.err == ""


def test_logger_debug_silent_when_quiet(capsys) -> None:
    """Debug should not print when quiet is True even if verbose."""
    logger = Logger(verbose=True, quiet=True)
    logger.debug("debug message")
    captured = capsys.readouterr()
    assert captured.err == ""


def test_progress_enabled_creates_console() -> None:
    """Progress with enabled=True should create a console."""
    progress = Progress(enabled=True)
    assert progress._console is not None


def test_progress_disabled_no_console() -> None:
    """Progress with enabled=False should not create a console."""
    progress = Progress(enabled=False)
    assert progress._console is None


def test_progress_task_context_manager_works() -> None:
    """Task context manager should execute wrapped code."""
    progress = Progress(enabled=False)
    executed = False
    with progress.task("Testing..."):
        executed = True
    assert executed


def test_progress_task_enabled_context_manager() -> None:
    """Task context manager with enabled progress should work."""
    progress = Progress(enabled=True)
    executed = False
    with progress.task("Testing..."):
        executed = True
    assert executed
