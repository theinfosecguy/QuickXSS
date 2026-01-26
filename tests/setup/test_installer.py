"""Unit tests for quickxss.setup.installer module."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from quickxss.constants.platform import APT_CMD, BREW_CMD, OS_DARWIN, OS_LINUX
from quickxss.scan.errors import ToolError
from quickxss.setup.installer import (
    install_gf_patterns,
    install_go_tools,
    install_system_packages,
)


@patch("quickxss.setup.installer.run_command")
def test_empty_packages_does_nothing(
    mock_run: patch, mock_logger: MagicMock
) -> None:
    """Empty packages list should not call any commands."""
    install_system_packages(OS_DARWIN, [], mock_logger)
    mock_run.assert_not_called()


@patch("quickxss.setup.installer.run_command")
def test_darwin_uses_brew(mock_run: patch, mock_logger: MagicMock) -> None:
    """Darwin should use brew install."""
    install_system_packages(OS_DARWIN, ["pkg1", "pkg2"], mock_logger)
    mock_run.assert_called_once_with(
        [BREW_CMD, "install", "pkg1", "pkg2"], mock_logger
    )


@patch("quickxss.setup.installer.run_command")
def test_linux_uses_apt(mock_run: patch, mock_logger: MagicMock) -> None:
    """Linux should use apt-get update and install."""
    install_system_packages(OS_LINUX, ["pkg1", "pkg2"], mock_logger)
    assert mock_run.call_count == 2
    calls = mock_run.call_args_list
    assert calls[0][0][0] == [APT_CMD, "update"]
    assert calls[1][0][0] == [APT_CMD, "install", "-y", "pkg1", "pkg2"]


def test_unsupported_os_raises_tool_error(mock_logger: MagicMock) -> None:
    """Unsupported OS should raise ToolError."""
    with pytest.raises(ToolError, match="not supported"):
        install_system_packages("unsupported_os", ["pkg1"], mock_logger)


@patch("quickxss.setup.installer.run_command")
def test_single_package(mock_run: patch, mock_logger: MagicMock) -> None:
    """Single package should work correctly."""
    install_system_packages(OS_DARWIN, ["single_pkg"], mock_logger)
    mock_run.assert_called_once_with(
        [BREW_CMD, "install", "single_pkg"], mock_logger
    )


@patch("quickxss.setup.installer.run_command")
def test_empty_tools_does_nothing(mock_run: patch, mock_logger: MagicMock) -> None:
    """Empty tools list should not call any commands."""
    install_go_tools([], mock_logger)
    mock_run.assert_not_called()


@patch("quickxss.setup.installer.run_command")
def test_installs_known_tools(mock_run: patch, mock_logger: MagicMock) -> None:
    """Known tools should be installed with go install."""
    install_go_tools(["gf"], mock_logger)
    assert mock_run.call_count == 1
    call_args = mock_run.call_args[0][0]
    assert call_args[0] == "go"
    assert call_args[1] == "install"


@patch("quickxss.setup.installer.run_command")
def test_installs_multiple_tools(mock_run: patch, mock_logger: MagicMock) -> None:
    """Multiple tools should each be installed separately."""
    install_go_tools(["gf", "dalfox", "waybackurls", "gau"], mock_logger)
    assert mock_run.call_count == 4


@patch("quickxss.setup.installer.run_command")
def test_unknown_tool_skipped(mock_run: patch, mock_logger: MagicMock) -> None:
    """Unknown tool should be skipped."""
    install_go_tools(["unknown_tool"], mock_logger)
    mock_run.assert_not_called()


@patch("shutil.copy2")
@patch("quickxss.setup.installer.copy_tree")
@patch("quickxss.setup.installer.run_command")
def test_creates_gf_directory(
    mock_run: patch,
    mock_copy_tree: patch,
    mock_copy2: patch,
    mock_logger: MagicMock,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Should create ~/.gf directory if it doesn't exist."""
    mock_home = tmp_path / "home"
    mock_home.mkdir()
    monkeypatch.setattr(Path, "home", lambda: mock_home)

    try:
        install_gf_patterns(mock_logger)
    except Exception:
        pass

    gf_dir = mock_home / ".gf"
    assert gf_dir.exists()


@patch("shutil.copy2")
@patch("quickxss.setup.installer.copy_tree")
@patch("quickxss.setup.installer.run_command")
def test_clones_gf_repo(
    mock_run: patch,
    mock_copy_tree: patch,
    mock_copy2: patch,
    mock_logger: MagicMock,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Should clone gf repository."""
    mock_home = tmp_path / "home"
    mock_home.mkdir()
    monkeypatch.setattr(Path, "home", lambda: mock_home)

    cloned_repos = []

    def track_run_command(cmd, logger):
        if cmd[0] == "git" and cmd[1] == "clone":
            cloned_repos.append(cmd[4])

    mock_run.side_effect = track_run_command
    install_gf_patterns(mock_logger)

    assert any("gf" in repo for repo in cloned_repos)


@patch("shutil.copy2")
@patch("quickxss.setup.installer.copy_tree")
@patch("quickxss.setup.installer.run_command")
def test_clones_patterns_repo(
    mock_run: patch,
    mock_copy_tree: patch,
    mock_copy2: patch,
    mock_logger: MagicMock,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Should clone Gf-Patterns repository."""
    mock_home = tmp_path / "home"
    mock_home.mkdir()
    monkeypatch.setattr(Path, "home", lambda: mock_home)

    cloned_repos = []

    def track_run_command(cmd, logger):
        if cmd[0] == "git" and cmd[1] == "clone":
            cloned_repos.append(cmd[4])

    mock_run.side_effect = track_run_command
    install_gf_patterns(mock_logger)

    assert any("patterns" in repo.lower() for repo in cloned_repos)


@patch("shutil.copy2")
@patch("quickxss.setup.installer.run_command")
def test_copies_examples(
    mock_run: patch,
    mock_copy2: patch,
    mock_logger: MagicMock,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Should copy examples to ~/.gf."""
    mock_home = tmp_path / "home"
    mock_home.mkdir()
    monkeypatch.setattr(Path, "home", lambda: mock_home)

    copy_tree_calls = []

    def track_copy_tree(src, dst):
        copy_tree_calls.append((src, dst))

    with patch("quickxss.setup.installer.copy_tree", side_effect=track_copy_tree):
        install_gf_patterns(mock_logger)

    assert len(copy_tree_calls) == 1
    src, dst = copy_tree_calls[0]
    assert "examples" in str(src)
    assert ".gf" in str(dst)
