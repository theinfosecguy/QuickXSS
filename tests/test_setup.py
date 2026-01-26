from __future__ import annotations

from quickxss.models.setup import SetupReport
from quickxss.setup import runner
from quickxss.utils.log import Logger


def test_setup_ok(monkeypatch) -> None:
    report = SetupReport(
        tools={"gf": True, "dalfox": True, "waybackurls": True, "gau": True},
        gf_pattern=True,
        os_name="linux",
        install_supported=True,
    )
    monkeypatch.setattr(runner, "build_report", lambda: report)
    logger = Logger(verbose=False, quiet=True)
    assert runner.run_setup(False, logger) == 0


def test_setup_missing_check_only(monkeypatch) -> None:
    report = SetupReport(
        tools={"gf": True, "dalfox": False, "waybackurls": True, "gau": False},
        gf_pattern=False,
        os_name="linux",
        install_supported=True,
    )
    monkeypatch.setattr(runner, "build_report", lambda: report)
    logger = Logger(verbose=False, quiet=True)
    assert runner.run_setup(False, logger) == 3


def test_setup_install_unsupported(monkeypatch) -> None:
    report = SetupReport(
        tools={"gf": False, "dalfox": False, "waybackurls": False, "gau": False},
        gf_pattern=False,
        os_name="windows",
        install_supported=False,
    )
    monkeypatch.setattr(runner, "build_report", lambda: report)
    logger = Logger(verbose=False, quiet=True)
    assert runner.run_setup(True, logger) == 3


def test_setup_install_success(monkeypatch) -> None:
    report_missing = SetupReport(
        tools={"gf": False, "dalfox": False, "waybackurls": False, "gau": False},
        gf_pattern=False,
        os_name="linux",
        install_supported=True,
    )
    report_ok = SetupReport(
        tools={"gf": True, "dalfox": True, "waybackurls": True, "gau": True},
        gf_pattern=True,
        os_name="linux",
        install_supported=True,
    )
    reports = iter([report_missing, report_ok])
    monkeypatch.setattr(runner, "build_report", lambda: next(reports))
    monkeypatch.setattr(runner, "install_missing", lambda *_: None)

    logger = Logger(verbose=False, quiet=True)
    assert runner.run_setup(True, logger) == 0
