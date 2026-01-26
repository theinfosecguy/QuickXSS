"""Unit tests for quickxss.models modules."""

from __future__ import annotations

from collections import OrderedDict
from pathlib import Path

import pytest

from quickxss.models.scan import ScanConfig, ScanPaths, ScanResult
from quickxss.models.setup import SetupReport


def test_scan_config_frozen(tmp_path: Path) -> None:
    """ScanConfig should be immutable (frozen)."""
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
    with pytest.raises(AttributeError):
        config.domain = "other.com"  # type: ignore


def test_scan_config_with_all_options(tmp_path: Path) -> None:
    """ScanConfig should accept all options."""
    config = ScanConfig(
        domain="example.com",
        results_dir=tmp_path,
        output_name="out.txt",
        overwrite=True,
        use_wayback=False,
        use_gau=False,
        gf_pattern="sqli",
        blind_payload="https://evil.com/callback",
        dalfox_args=["--timeout", "10"],
        keep_temp=False,
        verbose=True,
        quiet=False,
    )
    assert config.domain == "example.com"
    assert config.blind_payload == "https://evil.com/callback"
    assert config.dalfox_args == ["--timeout", "10"]
    assert config.use_wayback is False
    assert config.use_gau is False


def test_scan_paths_frozen(tmp_path: Path) -> None:
    """ScanPaths should be immutable (frozen)."""
    paths = ScanPaths(
        base_dir=tmp_path,
        urls_file=tmp_path / "urls.txt",
        temp_xss_file=tmp_path / "temp.txt",
        xss_file=tmp_path / "xss.txt",
        results_file=tmp_path / "results.txt",
    )
    with pytest.raises(AttributeError):
        paths.base_dir = Path("/other")  # type: ignore


def test_scan_paths_stores_paths(tmp_path: Path) -> None:
    """ScanPaths should store all path components."""
    paths = ScanPaths(
        base_dir=tmp_path / "base",
        urls_file=tmp_path / "urls.txt",
        temp_xss_file=tmp_path / "temp.txt",
        xss_file=tmp_path / "xss.txt",
        results_file=tmp_path / "results.txt",
    )
    assert paths.base_dir == tmp_path / "base"
    assert paths.urls_file == tmp_path / "urls.txt"
    assert paths.temp_xss_file == tmp_path / "temp.txt"


def test_scan_result_frozen(tmp_path: Path) -> None:
    """ScanResult should be immutable (frozen)."""
    result = ScanResult(
        total_urls=100,
        candidate_urls=50,
        findings=5,
        results_file=tmp_path / "results.txt",
    )
    with pytest.raises(AttributeError):
        result.total_urls = 200  # type: ignore


def test_scan_result_stores_metrics(tmp_path: Path) -> None:
    """ScanResult should store all metrics."""
    result = ScanResult(
        total_urls=1000,
        candidate_urls=100,
        findings=10,
        results_file=tmp_path / "results.txt",
    )
    assert result.total_urls == 1000
    assert result.candidate_urls == 100
    assert result.findings == 10
    assert result.results_file == tmp_path / "results.txt"


def test_setup_report_frozen() -> None:
    """SetupReport should be immutable (frozen)."""
    report = SetupReport(
        tools={"gf": True, "dalfox": True},
        gf_pattern=True,
        os_name="linux",
        install_supported=True,
    )
    with pytest.raises(AttributeError):
        report.os_name = "darwin"  # type: ignore


def test_missing_tools_returns_missing() -> None:
    """missing_tools property should return list of missing tools."""
    report = SetupReport(
        tools={"gf": True, "dalfox": False, "waybackurls": True, "gau": False},
        gf_pattern=True,
        os_name="linux",
        install_supported=True,
    )
    missing = report.missing_tools
    assert "dalfox" in missing
    assert "gau" in missing
    assert "gf" not in missing
    assert "waybackurls" not in missing


def test_missing_tools_empty_when_all_present() -> None:
    """missing_tools should return empty list when all tools present."""
    report = SetupReport(
        tools={"gf": True, "dalfox": True, "waybackurls": True, "gau": True},
        gf_pattern=True,
        os_name="linux",
        install_supported=True,
    )
    assert report.missing_tools == []


def test_ok_true_when_all_requirements_met() -> None:
    """ok property should return True when all requirements met."""
    report = SetupReport(
        tools={"gf": True, "dalfox": True, "waybackurls": True, "gau": True},
        gf_pattern=True,
        os_name="linux",
        install_supported=True,
    )
    assert report.ok is True


def test_ok_false_when_tools_missing() -> None:
    """ok property should return False when tools are missing."""
    report = SetupReport(
        tools={"gf": False, "dalfox": True},
        gf_pattern=True,
        os_name="linux",
        install_supported=True,
    )
    assert report.ok is False


def test_ok_false_when_gf_pattern_missing() -> None:
    """ok property should return False when gf_pattern is False."""
    report = SetupReport(
        tools={"gf": True, "dalfox": True, "waybackurls": True, "gau": True},
        gf_pattern=False,
        os_name="linux",
        install_supported=True,
    )
    assert report.ok is False


def test_missing_tools_preserves_order() -> None:
    """missing_tools should return tools in insertion order."""
    tools = OrderedDict([
        ("gf", False),
        ("dalfox", False),
        ("waybackurls", True),
        ("gau", False),
    ])
    report = SetupReport(
        tools=tools,
        gf_pattern=True,
        os_name="linux",
        install_supported=True,
    )
    missing = report.missing_tools
    assert missing == ["gf", "dalfox", "gau"]
