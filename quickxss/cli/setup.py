"""Setup command implementation."""

from __future__ import annotations

import typer

from quickxss.constants import CREDIT
from quickxss.scan.errors import ToolError
from quickxss.setup.runner import run_setup
from quickxss.utils.banner import render_banner
from quickxss.utils.log import Logger


def setup(
    install: bool = typer.Option(False, "--install", help="Install missing dependencies."),
    yes: bool = typer.Option(False, "--yes", help="Skip confirmation prompts."),
    verbose: bool = typer.Option(False, "--verbose", help="Verbose output."),
    quiet: bool = typer.Option(False, "--quiet", help="Suppress output."),
) -> None:
    """Check dependencies and optionally install them."""

    logger = Logger(verbose=verbose, quiet=quiet)
    if not quiet:
        logger.info(render_banner().rstrip())
        logger.info(CREDIT)
        logger.info("")

    install_requested = install
    if install and not yes:
        install_requested = typer.confirm("Proceed with installation?", default=False)
        if not install_requested:
            logger.info("Installation canceled.")
            raise typer.Exit(code=3)

    try:
        exit_code = run_setup(install_requested, logger)
    except ToolError as exc:
        logger.error(str(exc))
        raise typer.Exit(code=4) from exc
    except Exception as exc:
        logger.error(f"Unexpected error: {exc}")
        raise typer.Exit(code=1) from exc

    if exit_code != 0:
        raise typer.Exit(code=exit_code)
