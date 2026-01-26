from __future__ import annotations

from importlib import import_module
from pathlib import Path

from typer.testing import CliRunner

from quickxss.models.scan import ScanResult

cli = import_module("quickxss.cli.app")


def test_cli_requires_domain() -> None:
    runner = CliRunner()
    result = runner.invoke(cli.app, ["scan"])
    assert result.exit_code != 0


def test_cli_success(monkeypatch) -> None:
    def fake_run_scan(config, logger):
        return ScanResult(
            total_urls=1,
            candidate_urls=1,
            findings=0,
            results_file=Path("/tmp/results.txt"),
        )

    monkeypatch.setattr(cli, "run_scan", fake_run_scan)
    runner = CliRunner()
    with runner.isolated_filesystem():
        result = runner.invoke(cli.app, ["scan", "-d", "example.com"])
    assert result.exit_code == 0
    assert "Summary" in result.stdout
