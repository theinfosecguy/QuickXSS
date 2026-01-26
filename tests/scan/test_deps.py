"""Unit tests for quickxss.scan.deps module."""

from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

import pytest

import quickxss.scan.deps as deps
from quickxss.scan.errors import DependencyError


@patch.object(deps, "which", return_value=None)
def test_missing_binaries_returns_missing(mock_which: patch) -> None:
    """Should return list of missing binaries."""
    result = deps.missing_binaries(["gf", "dalfox"])
    assert result == ["gf", "dalfox"]


@patch.object(deps, "which", side_effect=lambda name: f"/usr/bin/{name}")
def test_missing_binaries_returns_empty_when_all_present(mock_which: patch) -> None:
    """Should return empty list when all binaries present."""
    result = deps.missing_binaries(["gf", "dalfox"])
    assert result == []


def test_missing_binaries_partial(monkeypatch: pytest.MonkeyPatch) -> None:
    """Should return only missing binaries."""

    def fake_which(name):
        return f"/usr/bin/{name}" if name == "gf" else None

    monkeypatch.setattr(deps, "which", fake_which)
    result = deps.missing_binaries(["gf", "dalfox", "waybackurls"])
    assert result == ["dalfox", "waybackurls"]


@patch.object(deps, "which", return_value=None)
def test_check_binaries_missing(mock_which: patch) -> None:
    """Should raise DependencyError when binaries missing."""
    with pytest.raises(DependencyError) as exc_info:
        deps.check_binaries(["gf", "dalfox"])
    assert "gf" in str(exc_info.value)
    assert "dalfox" in str(exc_info.value)


@patch.object(deps, "which", side_effect=lambda name: "/bin/" + name)
def test_check_binaries_ok(mock_which: patch) -> None:
    """Should not raise when all binaries present."""
    deps.check_binaries(["gf", "dalfox"])


@patch.object(deps, "which", return_value=None)
def test_check_binaries_empty_list(mock_which: patch) -> None:
    """Should not raise for empty required list."""
    deps.check_binaries([])


def test_check_gf_pattern_file_exists(gf_home: Path) -> None:
    """Should pass when pattern file exists in ~/.gf."""
    (gf_home / "xss.json").write_text("{}")
    deps.check_gf_pattern("xss")


def test_check_gf_pattern_from_list(
    gf_home: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Should pass when pattern available via gf -list."""

    def fake_run(*_args, **_kwargs):
        return SimpleNamespace(stdout="xss\nsqli\nssrf\n", returncode=0)

    monkeypatch.setattr(deps.subprocess, "run", fake_run)
    deps.check_gf_pattern("xss")


def test_check_gf_pattern_not_found(
    gf_home: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Should raise when pattern not found anywhere."""

    def fake_run(*_args, **_kwargs):
        return SimpleNamespace(stdout="sqli\nssrf\n", returncode=0)

    monkeypatch.setattr(deps.subprocess, "run", fake_run)
    with pytest.raises(DependencyError) as exc_info:
        deps.check_gf_pattern("xss")
    assert "xss" in str(exc_info.value)


def test_check_gf_pattern_gf_not_found(
    gf_home: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Should raise when gf command not found."""

    def fake_run(*_args, **_kwargs):
        raise FileNotFoundError()

    monkeypatch.setattr(deps.subprocess, "run", fake_run)
    with pytest.raises(DependencyError) as exc_info:
        deps.check_gf_pattern("xss")
    assert "gf" in str(exc_info.value).lower()


def test_check_gf_pattern_custom_pattern(gf_home: Path) -> None:
    """Should work with custom pattern names."""
    (gf_home / "custom-pattern.json").write_text("{}")
    deps.check_gf_pattern("custom-pattern")
