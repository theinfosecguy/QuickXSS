from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace

import pytest

import quickxss.scan.deps as deps
from quickxss.scan.errors import DependencyError


def test_check_binaries_missing(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(deps, "which", lambda name: None)
    with pytest.raises(DependencyError):
        deps.check_binaries(["gf", "dalfox"])


def test_check_binaries_ok(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(deps, "which", lambda name: "/bin/" + name)
    deps.check_binaries(["gf", "dalfox"])


def test_check_gf_pattern_file(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    monkeypatch.setenv("HOME", str(tmp_path))
    gf_dir = tmp_path / ".gf"
    gf_dir.mkdir()
    (gf_dir / "xss.json").write_text("{}")
    deps.check_gf_pattern("xss")


def test_check_gf_pattern_list(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    monkeypatch.setenv("HOME", str(tmp_path))

    def fake_run(*_args, **_kwargs):
        return SimpleNamespace(stdout="xss\n", returncode=0)

    monkeypatch.setattr(deps.subprocess, "run", fake_run)
    deps.check_gf_pattern("xss")
