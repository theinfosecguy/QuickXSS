from __future__ import annotations

from importlib import import_module
from pathlib import Path

from typer.testing import CliRunner

from quickxss.models.scan import ScanResult

app_module = import_module("quickxss.cli.app")
scan_module = import_module("quickxss.cli.scan")


def test_cli_requires_domain() -> None:
    runner = CliRunner()
    result = runner.invoke(app_module.app, ["scan"])
    assert result.exit_code != 0


def test_cli_success(monkeypatch) -> None:
    def fake_run_scan(config, logger):
        return ScanResult(
            total_urls=1,
            candidate_urls=1,
            findings=0,
            results_file=Path("/tmp/results.txt"),
        )

    monkeypatch.setattr(scan_module, "run_scan", fake_run_scan)
    runner = CliRunner()
    with runner.isolated_filesystem():
        result = runner.invoke(app_module.app, ["scan", "-d", "example.com"])
    assert result.exit_code == 0
    assert "Summary" in result.stdout
