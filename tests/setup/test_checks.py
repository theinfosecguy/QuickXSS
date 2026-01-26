"""Unit tests for quickxss.setup.checks module."""

from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

import pytest

from quickxss.setup import checks


@patch.object(checks, "which", side_effect=lambda name: f"/usr/bin/{name}")
def test_detect_tools_all_present(mock_which: patch) -> None:
    """Should return True for all present tools."""
    result = checks.detect_tools(["gf", "dalfox"])
    assert result == {"gf": True, "dalfox": True}


@patch.object(checks, "which", return_value=None)
def test_detect_tools_all_missing(mock_which: patch) -> None:
    """Should return False for all missing tools."""
    result = checks.detect_tools(["gf", "dalfox"])
    assert result == {"gf": False, "dalfox": False}


def test_detect_tools_mixed(monkeypatch: pytest.MonkeyPatch) -> None:
    """Should return mixed results."""

    def fake_which(name):
        return f"/usr/bin/{name}" if name in ("gf", "dalfox") else None

    monkeypatch.setattr(checks, "which", fake_which)
    result = checks.detect_tools(["gf", "dalfox", "waybackurls", "gau"])
    assert result == {"gf": True, "dalfox": True, "waybackurls": False, "gau": False}


def test_detect_tools_empty() -> None:
    """Should handle empty input."""
    result = checks.detect_tools([])
    assert result == {}


@patch.object(checks.platform, "system", return_value="Darwin")
def test_detect_os_returns_lowercase(mock_system: patch) -> None:
    """Should return lowercase OS name."""
    assert checks.detect_os() == "darwin"


@patch.object(checks.platform, "system", return_value="Linux")
def test_detect_os_linux(mock_system: patch) -> None:
    """Should detect Linux."""
    assert checks.detect_os() == "linux"


@patch.object(checks.platform, "system", return_value="Windows")
def test_detect_os_windows(mock_system: patch) -> None:
    """Should detect Windows."""
    assert checks.detect_os() == "windows"


@patch.object(checks, "which", return_value="/usr/local/bin/brew")
def test_has_brew_true(mock_which: patch) -> None:
    """Should return True when brew is available."""
    assert checks.has_brew() is True


@patch.object(checks, "which", return_value=None)
def test_has_brew_false(mock_which: patch) -> None:
    """Should return False when brew is not available."""
    assert checks.has_brew() is False


@patch.object(checks, "which", return_value="/usr/bin/apt-get")
def test_has_apt_true(mock_which: patch) -> None:
    """Should return True when apt-get is available."""
    assert checks.has_apt() is True


@patch.object(checks, "which", return_value=None)
def test_has_apt_false(mock_which: patch) -> None:
    """Should return False when apt-get is not available."""
    assert checks.has_apt() is False


@patch.object(checks, "has_brew", return_value=True)
def test_install_supported_darwin_with_brew(mock_brew: patch) -> None:
    """Should return True on Darwin with Homebrew."""
    assert checks.install_supported("darwin") is True


@patch.object(checks, "has_brew", return_value=False)
def test_install_supported_darwin_without_brew(mock_brew: patch) -> None:
    """Should return False on Darwin without Homebrew."""
    assert checks.install_supported("darwin") is False


@patch.object(checks, "has_apt", return_value=True)
def test_install_supported_linux_with_apt(mock_apt: patch) -> None:
    """Should return True on Linux with apt-get."""
    assert checks.install_supported("linux") is True


@patch.object(checks, "has_apt", return_value=False)
def test_install_supported_linux_without_apt(mock_apt: patch) -> None:
    """Should return False on Linux without apt-get."""
    assert checks.install_supported("linux") is False


def test_install_supported_windows() -> None:
    """Should return False on Windows."""
    assert checks.install_supported("windows") is False


def test_install_supported_unknown_os() -> None:
    """Should return False on unknown OS."""
    assert checks.install_supported("freebsd") is False


def test_has_gf_pattern_gf_not_available() -> None:
    """Should return False when gf is not available."""
    assert checks.has_gf_pattern("xss", gf_available=False) is False


def test_has_gf_pattern_file_exists(gf_home: Path) -> None:
    """Should return True when pattern file exists."""
    (gf_home / "xss.json").write_text("{}")
    assert checks.has_gf_pattern("xss", gf_available=True) is True


def test_has_gf_pattern_from_list(
    gf_home: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Should return True when pattern in gf -list."""

    def fake_run(*_args, **_kwargs):
        return SimpleNamespace(stdout="xss\nsqli\n", returncode=0)

    monkeypatch.setattr(checks.subprocess, "run", fake_run)
    assert checks.has_gf_pattern("xss", gf_available=True) is True


def test_has_gf_pattern_not_found(
    gf_home: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Should return False when pattern not found."""

    def fake_run(*_args, **_kwargs):
        return SimpleNamespace(stdout="sqli\nssrf\n", returncode=0)

    monkeypatch.setattr(checks.subprocess, "run", fake_run)
    assert checks.has_gf_pattern("xss", gf_available=True) is False


def test_has_gf_pattern_gf_command_not_found(
    gf_home: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Should return False when gf command fails."""

    def fake_run(*_args, **_kwargs):
        raise FileNotFoundError()

    monkeypatch.setattr(checks.subprocess, "run", fake_run)
    assert checks.has_gf_pattern("xss", gf_available=True) is False
