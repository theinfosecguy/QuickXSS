from __future__ import annotations

from pathlib import Path

import pytest

import quickxss.scan.pipeline as pipeline
from quickxss.models.scan import ScanConfig
from quickxss.utils.log import Logger


def test_run_scan_happy_path(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    monkeypatch.setattr(pipeline, "check_binaries", lambda *_: None)
    monkeypatch.setattr(pipeline, "check_gf_pattern", lambda *_: None)

    def fake_run_command(command, input_text, logger):
        if command[0] == "waybackurls":
            return "http://a.test/?q=1\n"
        if command[0] == "gau":
            return "http://b.test/?id=2\nhttp://a.test/?q=1\n"
        if command[0] == "gf":
            return "URL: http://a.test/?q=1\nhttp://b.test/?id=2\n"
        if command[0] == "dalfox":
            return ""
        raise AssertionError("unexpected command")

    monkeypatch.setattr(pipeline, "run_command", fake_run_command)

    config = ScanConfig(
        domain="example.com",
        results_dir=tmp_path,
        output_name="results.txt",
        overwrite=False,
        use_wayback=True,
        use_gau=True,
        gf_pattern="xss",
        blind_payload=None,
        dalfox_args=[],
        keep_temp=True,
        verbose=False,
        quiet=False,
    )

    logger = Logger(verbose=False, quiet=True)
    result = pipeline.run_scan(config, logger)

    base_dir = tmp_path / "example.com"
    assert base_dir.exists()
    assert (base_dir / "example.com.txt").exists()
    assert (base_dir / "example.com_xss.txt").exists()
    assert (base_dir / "results.txt").exists()
    assert result.total_urls == 2
    assert result.candidate_urls == 2
    assert result.findings == 0


def test_run_scan_no_candidates(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    monkeypatch.setattr(pipeline, "check_binaries", lambda *_: None)
    monkeypatch.setattr(pipeline, "check_gf_pattern", lambda *_: None)

    def fake_run_command(command, input_text, logger):
        if command[0] in {"waybackurls", "gau"}:
            return ""
        if command[0] == "gf":
            return ""
        if command[0] == "dalfox":
            raise AssertionError("dalfox should not run")
        raise AssertionError("unexpected command")

    monkeypatch.setattr(pipeline, "run_command", fake_run_command)

    config = ScanConfig(
        domain="example.com",
        results_dir=tmp_path,
        output_name="results.txt",
        overwrite=False,
        use_wayback=True,
        use_gau=True,
        gf_pattern="xss",
        blind_payload=None,
        dalfox_args=[],
        keep_temp=False,
        verbose=False,
        quiet=False,
    )

    logger = Logger(verbose=False, quiet=True)
    result = pipeline.run_scan(config, logger)

    base_dir = tmp_path / "example.com"
    assert not (base_dir / "example.com_temp_xss.txt").exists()
    assert (base_dir / "results.txt").exists()
    assert result.candidate_urls == 0
