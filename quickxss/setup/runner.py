"""Setup command runner."""

from __future__ import annotations

from typing import Iterable, List, Set

from quickxss.constants.platform import GO_PKG_DARWIN, GO_PKG_LINUX, OS_DARWIN, OS_LINUX
from quickxss.constants.tools import GF_PATTERNS_REPO_URL, GF_REPO_URL, GO_TOOLS, REQUIRED_TOOLS
from quickxss.models.setup import SetupReport
from quickxss.setup.checks import detect_os, detect_tools, has_gf_pattern, install_supported
from quickxss.setup.installer import install_gf_patterns, install_go_tools, install_system_packages
from quickxss.utils.log import Logger
from quickxss.utils.progress import Progress


def run_setup(install: bool, logger: Logger) -> int:
    """Run setup checks and optional installation."""

    progress = Progress(enabled=not logger.quiet)
    with progress.task("Checking environment..."):
        report = build_report()
    print_report(report, logger)

    if report.ok:
        logger.info("")
        if install:
            logger.info("All dependencies are already installed. No action needed.")
        else:
            logger.info("All dependencies are installed.")
        return 0

    if not install:
        print_suggestions(report, logger)
        logger.info("")
        logger.info("To install automatically, run: quickxss setup --install")
        return 3

    if not report.install_supported:
        logger.warn("Auto-install is not supported on this OS.")
        print_suggestions(report, logger)
        return 3

    with progress.task("Installing dependencies..."):
        install_missing(report, logger)
    logger.info("Re-checking dependencies...")
    with progress.task("Re-checking environment..."):
        final_report = build_report()
    print_report(final_report, logger)
    if final_report.ok:
        logger.info("")
        logger.info("Setup complete.")
        return 0

    logger.warn("Some dependencies are still missing.")
    print_suggestions(final_report, logger)
    return 3


def build_report() -> SetupReport:
    """Build a setup status report."""

    os_name = detect_os()
    tools = detect_tools(REQUIRED_TOOLS)
    gf_pattern_ok = has_gf_pattern("xss", tools.get("gf", False))
    supported = install_supported(os_name)

    return SetupReport(
        tools=tools,
        gf_pattern=gf_pattern_ok,
        os_name=os_name,
        install_supported=supported,
    )


def print_report(report: SetupReport, logger: Logger) -> None:
    """Print a setup report."""

    logger.info("Setup status")
    logger.info("------------")
    logger.info(f"OS detected: {report.os_name}")
    logger.info("")
    for tool, ok in report.tools.items():
        logger.info(f"{tool}: {'ok' if ok else 'missing'}")
    logger.info(f"gf patterns (xss): {'ok' if report.gf_pattern else 'missing'}")


def print_suggestions(report: SetupReport, logger: Logger) -> None:
    """Print suggested manual install commands."""

    commands = suggested_commands(report.missing_tools, report.gf_pattern)
    if not commands:
        return
    logger.info("")
    logger.info("Next steps:")
    for command in commands:
        logger.info(command)


def suggested_commands(missing_tools: Iterable[str], gf_pattern_ok: bool) -> List[str]:
    """Return manual install commands for missing items."""

    commands: List[str] = []
    for tool in missing_tools:
        module = GO_TOOLS.get(tool)
        if module:
            commands.append(f"go install {module}")

    if not gf_pattern_ok:
        commands.extend(
            [
                "mkdir -p ~/.gf",
                f"git clone {GF_REPO_URL} /tmp/gf",
                "cp -r /tmp/gf/examples/* ~/.gf/",
                f"git clone {GF_PATTERNS_REPO_URL} /tmp/Gf-Patterns",
                "cp -r /tmp/Gf-Patterns/*.json ~/.gf/",
            ]
        )

    return commands


def install_missing(report: SetupReport, logger: Logger) -> None:
    """Install missing dependencies when supported."""

    packages: Set[str] = set()
    if report.os_name in {OS_DARWIN, OS_LINUX}:
        if report.missing_tools:
            packages.add(GO_PKG_DARWIN if report.os_name == OS_DARWIN else GO_PKG_LINUX)
        if report.tools.get("gf") is False or not report.gf_pattern:
            packages.add("git")

    if packages:
        logger.info("Installing system packages...")
        install_system_packages(report.os_name, sorted(packages), logger)

    if report.missing_tools:
        logger.info("Installing Go tools...")
        install_go_tools(report.missing_tools, logger)

    if not report.gf_pattern:
        logger.info("Installing gf patterns...")
        install_gf_patterns(logger)
