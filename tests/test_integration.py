from __future__ import annotations

import os
import shutil
from pathlib import Path
from typing import List

import pytest
from typer.testing import CliRunner

import quickxss.cli as cli

REQUIRED_TOOLS = ["gf", "dalfox", "waybackurls", "gau"]


def _missing_tools() -> List[str]:
    return [tool for tool in REQUIRED_TOOLS if shutil.which(tool) is None]


def _integration_enabled() -> bool:
    return os.getenv("QUICKXSS_INTEGRATION") == "1"


def _has_gf_pattern() -> bool:
    return (Path.home() / ".gf" / "xss.json").exists()


@pytest.mark.integration
def test_integration_scan(tmp_path: Path) -> None:
    if not _integration_enabled():
        pytest.skip("set QUICKXSS_INTEGRATION=1 to enable integration tests")

    missing = _missing_tools()
    if missing:
        pytest.skip(f"missing external tools: {', '.join(missing)}")

    if not _has_gf_pattern():
        pytest.skip("missing gf pattern: ~/.gf/xss.json")

    domain = os.getenv("QUICKXSS_TARGET", "testphp.vulnweb.com")

    runner = CliRunner()
    result = runner.invoke(
        cli.app,
        [
            "scan",
            "-d",
            domain,
            "--results-dir",
            str(tmp_path),
            "--overwrite",
            "--quiet",
        ],
    )

    assert result.exit_code == 0

    base_dir = tmp_path / domain
    urls_file = base_dir / f"{domain}.txt"
    candidates_file = base_dir / f"{domain}_xss.txt"
    results_file = base_dir / "results.txt"

    assert urls_file.exists()
    assert candidates_file.exists()
    assert results_file.exists()
    assert urls_file.read_text(encoding="utf-8").strip()
    assert candidates_file.read_text(encoding="utf-8").strip()
