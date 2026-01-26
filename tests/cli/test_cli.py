"""Unit tests for quickxss.cli module."""

from __future__ import annotations

from importlib import import_module
from pathlib import Path

import pytest
from typer.testing import CliRunner

from quickxss.models.scan import ScanResult
from quickxss.models.setup import SetupReport
from quickxss.scan.errors import DependencyError, ToolError, ValidationError

app_module = import_module("quickxss.cli.app")
scan_module = import_module("quickxss.cli.scan")
setup_cli_module = import_module("quickxss.cli.setup")
setup_runner = import_module("quickxss.setup.runner")


@pytest.fixture
def cli_runner():
    """Create a CLI runner."""
    return CliRunner()


def test_cli_requires_domain(cli_runner) -> None:
    """Scan without domain should fail."""
    result = cli_runner.invoke(app_module.app, ["scan"])
    assert result.exit_code != 0


def test_cli_success(monkeypatch, cli_runner) -> None:
    """Successful scan should show summary."""

    def fake_run_scan(config, logger):
        return ScanResult(
            total_urls=1,
            candidate_urls=1,
            findings=0,
            results_file=Path("/tmp/results.txt"),
        )

    monkeypatch.setattr(scan_module, "run_scan", fake_run_scan)
    with cli_runner.isolated_filesystem():
        result = cli_runner.invoke(app_module.app, ["scan", "-d", "example.com"])
    assert result.exit_code == 0
    assert "Summary" in result.stdout


def test_cli_displays_banner(monkeypatch, cli_runner) -> None:
    """Scan should display banner unless quiet."""

    def fake_run_scan(config, logger):
        return ScanResult(
            total_urls=1,
            candidate_urls=1,
            findings=0,
            results_file=Path("/tmp/results.txt"),
        )

    monkeypatch.setattr(scan_module, "run_scan", fake_run_scan)
    with cli_runner.isolated_filesystem():
        result = cli_runner.invoke(app_module.app, ["scan", "-d", "example.com"])
    assert result.exit_code == 0
    assert "XSS" in result.stdout or "___" in result.stdout


def test_cli_quiet_suppresses_output(monkeypatch, cli_runner) -> None:
    """Scan with --quiet should suppress output."""

    def fake_run_scan(config, logger):
        return ScanResult(
            total_urls=1,
            candidate_urls=1,
            findings=0,
            results_file=Path("/tmp/results.txt"),
        )

    monkeypatch.setattr(scan_module, "run_scan", fake_run_scan)
    with cli_runner.isolated_filesystem():
        result = cli_runner.invoke(
            app_module.app, ["scan", "-d", "example.com", "--quiet"]
        )
    assert result.exit_code == 0
    assert result.stdout == ""


def test_cli_validation_error_exit_code_2(monkeypatch, cli_runner) -> None:
    """Validation error should exit with code 2."""

    def fake_run_scan(config, logger):
        raise ValidationError("Invalid domain")

    monkeypatch.setattr(scan_module, "run_scan", fake_run_scan)
    with cli_runner.isolated_filesystem():
        result = cli_runner.invoke(app_module.app, ["scan", "-d", "example.com"])
    assert result.exit_code == 2


def test_cli_dependency_error_exit_code_3(monkeypatch, cli_runner) -> None:
    """Dependency error should exit with code 3."""

    def fake_run_scan(config, logger):
        raise DependencyError("Missing gf")

    monkeypatch.setattr(scan_module, "run_scan", fake_run_scan)
    with cli_runner.isolated_filesystem():
        result = cli_runner.invoke(app_module.app, ["scan", "-d", "example.com"])
    assert result.exit_code == 3


def test_cli_tool_error_exit_code_4(monkeypatch, cli_runner) -> None:
    """Tool error should exit with code 4."""

    def fake_run_scan(config, logger):
        raise ToolError("dalfox failed")

    monkeypatch.setattr(scan_module, "run_scan", fake_run_scan)
    with cli_runner.isolated_filesystem():
        result = cli_runner.invoke(app_module.app, ["scan", "-d", "example.com"])
    assert result.exit_code == 4


def test_cli_unexpected_error_exit_code_1(monkeypatch, cli_runner) -> None:
    """Unexpected error should exit with code 1."""

    def fake_run_scan(config, logger):
        raise RuntimeError("Unexpected error")

    monkeypatch.setattr(scan_module, "run_scan", fake_run_scan)
    with cli_runner.isolated_filesystem():
        result = cli_runner.invoke(app_module.app, ["scan", "-d", "example.com"])
    assert result.exit_code == 1


def test_cli_with_blind_payload(monkeypatch, cli_runner) -> None:
    """Scan with blind payload should pass it to config."""
    captured_config = {}

    def fake_run_scan(config, logger):
        captured_config["blind"] = config.blind_payload
        return ScanResult(
            total_urls=1,
            candidate_urls=1,
            findings=0,
            results_file=Path("/tmp/results.txt"),
        )

    monkeypatch.setattr(scan_module, "run_scan", fake_run_scan)
    with cli_runner.isolated_filesystem():
        result = cli_runner.invoke(
            app_module.app,
            ["scan", "-d", "example.com", "-b", "https://callback.com"],
        )
    assert result.exit_code == 0
    assert captured_config["blind"] == "https://callback.com"


def test_cli_with_custom_output(monkeypatch, cli_runner) -> None:
    """Scan with custom output name should use it."""
    captured_config = {}

    def fake_run_scan(config, logger):
        captured_config["output"] = config.output_name
        return ScanResult(
            total_urls=1,
            candidate_urls=1,
            findings=0,
            results_file=Path("/tmp/results.txt"),
        )

    monkeypatch.setattr(scan_module, "run_scan", fake_run_scan)
    with cli_runner.isolated_filesystem():
        result = cli_runner.invoke(
            app_module.app,
            ["scan", "-d", "example.com", "-o", "custom_output.txt"],
        )
    assert result.exit_code == 0
    assert captured_config["output"] == "custom_output.txt"


def test_setup_check_success(monkeypatch, cli_runner, all_tools_ok_report) -> None:
    """Setup check should pass when all requirements met."""
    monkeypatch.setattr(setup_runner, "build_report", lambda: all_tools_ok_report)

    result = cli_runner.invoke(app_module.app, ["setup"])
    assert result.exit_code == 0
    assert "ok" in result.stdout.lower()


def test_setup_check_missing_tools(monkeypatch, cli_runner) -> None:
    """Setup check should fail when tools missing."""
    report = SetupReport(
        tools={"gf": False, "dalfox": True, "waybackurls": True, "gau": True},
        gf_pattern=True,
        os_name="linux",
        install_supported=True,
    )
    monkeypatch.setattr(setup_runner, "build_report", lambda: report)

    result = cli_runner.invoke(app_module.app, ["setup"])
    assert result.exit_code == 3
    assert "missing" in result.stdout.lower()


def test_setup_displays_os(monkeypatch, cli_runner) -> None:
    """Setup should display detected OS."""
    report = SetupReport(
        tools={"gf": True, "dalfox": True, "waybackurls": True, "gau": True},
        gf_pattern=True,
        os_name="darwin",
        install_supported=True,
    )
    monkeypatch.setattr(setup_runner, "build_report", lambda: report)

    result = cli_runner.invoke(app_module.app, ["setup"])
    assert "darwin" in result.stdout.lower()


def test_setup_quiet_suppresses_output(
    monkeypatch, cli_runner, all_tools_ok_report
) -> None:
    """Setup with --quiet should suppress output."""
    monkeypatch.setattr(setup_runner, "build_report", lambda: all_tools_ok_report)

    result = cli_runner.invoke(app_module.app, ["setup", "--quiet"])
    assert result.exit_code == 0
    assert result.stdout.strip() == ""
