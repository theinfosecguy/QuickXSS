"""Pytest configuration and shared fixtures."""

from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest

from quickxss.models.scan import ScanConfig, ScanResult
from quickxss.models.setup import SetupReport
from quickxss.utils.log import Logger


@pytest.fixture
def quiet_logger() -> Logger:
    """Create a quiet logger for testing."""
    return Logger(verbose=False, quiet=True)


@pytest.fixture
def verbose_logger() -> Logger:
    """Create a verbose logger for testing."""
    return Logger(verbose=True, quiet=False)


@pytest.fixture
def mock_logger() -> MagicMock:
    """Create a mock logger."""
    return MagicMock(spec=Logger)


@pytest.fixture
def sample_scan_config(tmp_path: Path) -> ScanConfig:
    """Create a sample scan configuration."""
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


@pytest.fixture
def sample_scan_result(tmp_path: Path) -> ScanResult:
    """Create a sample scan result."""
    return ScanResult(
        total_urls=100,
        candidate_urls=50,
        findings=5,
        results_file=tmp_path / "results.txt",
    )


@pytest.fixture
def all_tools_ok_report() -> SetupReport:
    """Create a setup report with all tools installed."""
    return SetupReport(
        tools={"gf": True, "dalfox": True, "waybackurls": True, "gau": True},
        gf_pattern=True,
        os_name="linux",
        install_supported=True,
    )


@pytest.fixture
def missing_tools_report() -> SetupReport:
    """Create a setup report with missing tools."""
    return SetupReport(
        tools={"gf": False, "dalfox": False, "waybackurls": False, "gau": False},
        gf_pattern=False,
        os_name="linux",
        install_supported=True,
    )


@pytest.fixture
def gf_home(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """Create a temporary home directory with .gf folder."""
    monkeypatch.setenv("HOME", str(tmp_path))
    gf_dir = tmp_path / ".gf"
    gf_dir.mkdir()
    return gf_dir


@pytest.fixture
def fake_subprocess_success() -> SimpleNamespace:
    """Create a fake successful subprocess result."""
    return SimpleNamespace(stdout="", stderr="", returncode=0)
