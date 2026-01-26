"""Unit tests for quickxss.setup.runner module."""

from __future__ import annotations

from quickxss.models.setup import SetupReport
from quickxss.setup import runner
from quickxss.utils.log import Logger


def test_setup_ok(monkeypatch, quiet_logger: Logger, all_tools_ok_report) -> None:
    """Setup with all tools installed should return 0."""
    monkeypatch.setattr(runner, "build_report", lambda: all_tools_ok_report)
    assert runner.run_setup(False, quiet_logger) == 0


def test_setup_missing_check_only(monkeypatch, quiet_logger: Logger) -> None:
    """Setup with missing tools (check only) should return 3."""
    report = SetupReport(
        tools={"gf": True, "dalfox": False, "waybackurls": True, "gau": False},
        gf_pattern=False,
        os_name="linux",
        install_supported=True,
    )
    monkeypatch.setattr(runner, "build_report", lambda: report)
    assert runner.run_setup(False, quiet_logger) == 3


def test_setup_install_unsupported(monkeypatch, quiet_logger: Logger) -> None:
    """Setup with unsupported OS should return 3."""
    report = SetupReport(
        tools={"gf": False, "dalfox": False, "waybackurls": False, "gau": False},
        gf_pattern=False,
        os_name="windows",
        install_supported=False,
    )
    monkeypatch.setattr(runner, "build_report", lambda: report)
    assert runner.run_setup(True, quiet_logger) == 3


def test_setup_install_success(
    monkeypatch, quiet_logger: Logger, missing_tools_report, all_tools_ok_report
) -> None:
    """Setup install should return 0 when all deps installed."""
    reports = iter([missing_tools_report, all_tools_ok_report])
    monkeypatch.setattr(runner, "build_report", lambda: next(reports))
    monkeypatch.setattr(runner, "install_missing", lambda *_: None)
    assert runner.run_setup(True, quiet_logger) == 0


def test_setup_install_partial_failure(
    monkeypatch, quiet_logger: Logger, missing_tools_report
) -> None:
    """Setup install should return 3 when some deps still missing."""
    report_still_missing = SetupReport(
        tools={"gf": True, "dalfox": False, "waybackurls": True, "gau": False},
        gf_pattern=True,
        os_name="linux",
        install_supported=True,
    )
    reports = iter([missing_tools_report, report_still_missing])
    monkeypatch.setattr(runner, "build_report", lambda: next(reports))
    monkeypatch.setattr(runner, "install_missing", lambda *_: None)
    assert runner.run_setup(True, quiet_logger) == 3


def test_setup_darwin(monkeypatch, quiet_logger: Logger) -> None:
    """Setup on Darwin should work correctly."""
    report = SetupReport(
        tools={"gf": True, "dalfox": True, "waybackurls": True, "gau": True},
        gf_pattern=True,
        os_name="darwin",
        install_supported=True,
    )
    monkeypatch.setattr(runner, "build_report", lambda: report)
    assert runner.run_setup(False, quiet_logger) == 0


def test_build_report_returns_setup_report(monkeypatch) -> None:
    """Should return a SetupReport instance."""
    monkeypatch.setattr(runner, "detect_os", lambda: "linux")
    monkeypatch.setattr(
        runner, "detect_tools", lambda _: {"gf": True, "dalfox": True}
    )
    monkeypatch.setattr(runner, "has_gf_pattern", lambda name, has_gf: True)
    monkeypatch.setattr(runner, "install_supported", lambda os: True)

    report = runner.build_report()
    assert isinstance(report, SetupReport)


def test_build_report_passes_required_tools(monkeypatch) -> None:
    """Should detect required tools."""
    detected = []

    def mock_detect(tools):
        detected.extend(tools)
        return {"gf": True, "dalfox": True, "waybackurls": True, "gau": True}

    monkeypatch.setattr(runner, "detect_os", lambda: "linux")
    monkeypatch.setattr(runner, "detect_tools", mock_detect)
    monkeypatch.setattr(runner, "has_gf_pattern", lambda name, has_gf: True)
    monkeypatch.setattr(runner, "install_supported", lambda os: True)

    runner.build_report()
    assert "gf" in detected
    assert "dalfox" in detected


def test_print_report_prints_os_name(capsys) -> None:
    """Should print detected OS."""
    report = SetupReport(
        tools={"gf": True},
        gf_pattern=True,
        os_name="darwin",
        install_supported=True,
    )
    logger = Logger(verbose=False, quiet=False)
    runner.print_report(report, logger)
    captured = capsys.readouterr()
    assert "darwin" in captured.out


def test_print_report_prints_tool_status(capsys) -> None:
    """Should print status for each tool."""
    report = SetupReport(
        tools={"gf": True, "dalfox": False},
        gf_pattern=True,
        os_name="linux",
        install_supported=True,
    )
    logger = Logger(verbose=False, quiet=False)
    runner.print_report(report, logger)
    captured = capsys.readouterr()
    assert "gf" in captured.out
    assert "ok" in captured.out
    assert "dalfox" in captured.out
    assert "missing" in captured.out


def test_print_report_prints_gf_pattern_status(capsys) -> None:
    """Should print gf pattern status."""
    report = SetupReport(
        tools={"gf": True},
        gf_pattern=False,
        os_name="linux",
        install_supported=True,
    )
    logger = Logger(verbose=False, quiet=False)
    runner.print_report(report, logger)
    captured = capsys.readouterr()
    assert "gf patterns" in captured.out
    assert "missing" in captured.out


def test_suggested_commands_empty_when_nothing_missing() -> None:
    """No missing tools should return empty list."""
    commands = runner.suggested_commands([], True)
    assert commands == []


def test_suggested_commands_go_install_for_missing_tools() -> None:
    """Missing tools should have go install commands."""
    commands = runner.suggested_commands(["gf", "dalfox"], True)
    assert any("go install" in cmd for cmd in commands)


def test_suggested_commands_gf_pattern_commands() -> None:
    """Missing gf pattern should have clone commands."""
    commands = runner.suggested_commands([], False)
    assert any("git clone" in cmd for cmd in commands)
    assert any("mkdir" in cmd for cmd in commands)


def test_suggested_commands_combined() -> None:
    """Missing tools and patterns should have both commands."""
    commands = runner.suggested_commands(["gf"], False)
    assert any("go install" in cmd for cmd in commands)
    assert any("git clone" in cmd for cmd in commands)


def test_install_missing_installs_system_packages(
    monkeypatch, quiet_logger: Logger
) -> None:
    """Should install system packages when needed."""
    installed_packages = []

    def mock_install_system(os_name, packages, logger):
        installed_packages.extend(packages)

    monkeypatch.setattr(runner, "install_system_packages", mock_install_system)
    monkeypatch.setattr(runner, "install_go_tools", lambda *_: None)
    monkeypatch.setattr(runner, "install_gf_patterns", lambda *_: None)

    report = SetupReport(
        tools={"gf": False},
        gf_pattern=False,
        os_name="linux",
        install_supported=True,
    )
    runner.install_missing(report, quiet_logger)
    assert len(installed_packages) > 0


def test_install_missing_installs_go_tools(monkeypatch, quiet_logger: Logger) -> None:
    """Should install missing Go tools."""
    installed_tools = []

    def mock_install_go(tools, logger):
        installed_tools.extend(tools)

    monkeypatch.setattr(runner, "install_system_packages", lambda *_: None)
    monkeypatch.setattr(runner, "install_go_tools", mock_install_go)
    monkeypatch.setattr(runner, "install_gf_patterns", lambda *_: None)

    report = SetupReport(
        tools={"gf": False, "dalfox": False},
        gf_pattern=True,
        os_name="linux",
        install_supported=True,
    )
    runner.install_missing(report, quiet_logger)
    assert "gf" in installed_tools or "dalfox" in installed_tools


def test_install_missing_installs_gf_patterns(
    monkeypatch, quiet_logger: Logger
) -> None:
    """Should install gf patterns when missing."""
    patterns_installed = []

    def mock_install_patterns(logger):
        patterns_installed.append(True)

    monkeypatch.setattr(runner, "install_system_packages", lambda *_: None)
    monkeypatch.setattr(runner, "install_go_tools", lambda *_: None)
    monkeypatch.setattr(runner, "install_gf_patterns", mock_install_patterns)

    report = SetupReport(
        tools={"gf": True, "dalfox": True, "waybackurls": True, "gau": True},
        gf_pattern=False,
        os_name="linux",
        install_supported=True,
    )
    runner.install_missing(report, quiet_logger)
    assert patterns_installed == [True]
