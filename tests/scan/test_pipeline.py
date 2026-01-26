"""Unit tests for quickxss.scan.pipeline module."""

from __future__ import annotations

from pathlib import Path

import pytest

import quickxss.scan.pipeline as pipeline
from quickxss.models.scan import ScanConfig
from quickxss.utils.log import Logger


@pytest.fixture
def scan_config(tmp_path: Path) -> ScanConfig:
    """Create a basic scan config."""
    return ScanConfig(
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


def test_run_scan_happy_path(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path, quiet_logger: Logger
) -> None:
    """Full scan should succeed and create expected files."""
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

    result = pipeline.run_scan(config, quiet_logger)

    base_dir = tmp_path / "example.com"
    assert base_dir.exists()
    assert (base_dir / "example.com.txt").exists()
    assert (base_dir / "example.com_xss.txt").exists()
    assert (base_dir / "results.txt").exists()
    assert result.total_urls == 2
    assert result.candidate_urls == 2
    assert result.findings == 0


def test_run_scan_no_candidates(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path, quiet_logger: Logger
) -> None:
    """Scan with no candidates should skip dalfox."""
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

    result = pipeline.run_scan(config, quiet_logger)

    base_dir = tmp_path / "example.com"
    assert not (base_dir / "example.com_temp_xss.txt").exists()
    assert (base_dir / "results.txt").exists()
    assert result.candidate_urls == 0


def test_run_scan_wayback_only(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path, quiet_logger: Logger
) -> None:
    """Scan with only waybackurls enabled."""
    monkeypatch.setattr(pipeline, "check_binaries", lambda *_: None)
    monkeypatch.setattr(pipeline, "check_gf_pattern", lambda *_: None)

    gau_called = False

    def fake_run_command(command, input_text, logger):
        nonlocal gau_called
        if command[0] == "waybackurls":
            return "http://test.com/?id=1\n"
        if command[0] == "gau":
            gau_called = True
            return ""
        if command[0] == "gf":
            return "http://test.com/?id=1\n"
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
        use_gau=False,
        gf_pattern="xss",
        blind_payload=None,
        dalfox_args=[],
        keep_temp=True,
        verbose=False,
        quiet=False,
    )

    result = pipeline.run_scan(config, quiet_logger)

    assert not gau_called
    assert result.total_urls == 1


def test_run_scan_with_blind_payload(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path, quiet_logger: Logger
) -> None:
    """Scan with blind XSS payload should pass it to dalfox."""
    monkeypatch.setattr(pipeline, "check_binaries", lambda *_: None)
    monkeypatch.setattr(pipeline, "check_gf_pattern", lambda *_: None)

    captured_dalfox_cmd = []

    def fake_run_command(command, input_text, logger):
        if command[0] == "waybackurls":
            return "http://test.com/?id=1\n"
        if command[0] == "gau":
            return ""
        if command[0] == "gf":
            return "http://test.com/?id=1\n"
        if command[0] == "dalfox":
            captured_dalfox_cmd.extend(command)
            return ""
        raise AssertionError("unexpected command")

    monkeypatch.setattr(pipeline, "run_command", fake_run_command)

    config = ScanConfig(
        domain="example.com",
        results_dir=tmp_path,
        output_name="results.txt",
        overwrite=False,
        use_wayback=True,
        use_gau=False,
        gf_pattern="xss",
        blind_payload="https://callback.evil.com",
        dalfox_args=[],
        keep_temp=True,
        verbose=False,
        quiet=False,
    )

    pipeline.run_scan(config, quiet_logger)

    assert "-b" in captured_dalfox_cmd
    assert "https://callback.evil.com" in captured_dalfox_cmd
    assert "-H" in captured_dalfox_cmd


def test_run_scan_with_custom_dalfox_args(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path, quiet_logger: Logger
) -> None:
    """Scan with custom dalfox args should include them."""
    monkeypatch.setattr(pipeline, "check_binaries", lambda *_: None)
    monkeypatch.setattr(pipeline, "check_gf_pattern", lambda *_: None)

    captured_dalfox_cmd = []

    def fake_run_command(command, input_text, logger):
        if command[0] == "waybackurls":
            return "http://test.com/?id=1\n"
        if command[0] == "gau":
            return ""
        if command[0] == "gf":
            return "http://test.com/?id=1\n"
        if command[0] == "dalfox":
            captured_dalfox_cmd.extend(command)
            return ""
        raise AssertionError("unexpected command")

    monkeypatch.setattr(pipeline, "run_command", fake_run_command)

    config = ScanConfig(
        domain="example.com",
        results_dir=tmp_path,
        output_name="results.txt",
        overwrite=False,
        use_wayback=True,
        use_gau=False,
        gf_pattern="xss",
        blind_payload=None,
        dalfox_args=["--timeout", "10", "--skip-headless"],
        keep_temp=True,
        verbose=False,
        quiet=False,
    )

    pipeline.run_scan(config, quiet_logger)

    assert "--timeout" in captured_dalfox_cmd
    assert "10" in captured_dalfox_cmd
    assert "--skip-headless" in captured_dalfox_cmd


def test_normalize_lines_strips_whitespace() -> None:
    """Should strip whitespace from lines."""
    result = pipeline.normalize_lines(["  hello  ", "  world  "])
    assert result == ["hello", "world"]


def test_normalize_lines_removes_empty() -> None:
    """Should remove empty lines."""
    result = pipeline.normalize_lines(["hello", "", "  ", "world"])
    assert result == ["hello", "world"]


def test_normalize_lines_empty_input() -> None:
    """Should handle empty input."""
    result = pipeline.normalize_lines([])
    assert result == []


def test_normalize_candidate_strips_url_prefix() -> None:
    """Should strip 'URL: ' prefix."""
    result = pipeline.normalize_candidate("URL: http://test.com/?id=1")
    assert result == "http://test.com/?id="


def test_normalize_candidate_truncates_at_equals() -> None:
    """Should truncate value after equals sign."""
    result = pipeline.normalize_candidate("http://test.com/?id=12345")
    assert result == "http://test.com/?id="


def test_normalize_candidate_no_equals() -> None:
    """Should return unchanged if no equals sign."""
    result = pipeline.normalize_candidate("http://test.com/path")
    assert result == "http://test.com/path"


def test_normalize_candidate_strips_whitespace() -> None:
    """Should strip whitespace."""
    result = pipeline.normalize_candidate("  http://test.com/?id=1  ")
    assert result == "http://test.com/?id="


def test_count_findings_counts_non_empty_lines(tmp_path: Path) -> None:
    """Should count non-empty lines."""
    results = tmp_path / "results.txt"
    results.write_text("finding1\nfinding2\nfinding3\n")
    assert pipeline.count_findings(results) == 3


def test_count_findings_ignores_empty_lines(tmp_path: Path) -> None:
    """Should ignore empty lines."""
    results = tmp_path / "results.txt"
    results.write_text("finding1\n\n\nfinding2\n")
    assert pipeline.count_findings(results) == 2


def test_count_findings_missing_file(tmp_path: Path) -> None:
    """Should return 0 for missing file."""
    results = tmp_path / "nonexistent.txt"
    assert pipeline.count_findings(results) == 0


def test_count_findings_empty_file(tmp_path: Path) -> None:
    """Should return 0 for empty file."""
    results = tmp_path / "empty.txt"
    results.write_text("")
    assert pipeline.count_findings(results) == 0


def test_count_findings_whitespace_only_lines(tmp_path: Path) -> None:
    """Should ignore whitespace-only lines."""
    results = tmp_path / "results.txt"
    results.write_text("finding1\n   \n\t\nfinding2\n")
    assert pipeline.count_findings(results) == 2
