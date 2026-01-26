"""Typer CLI entrypoint for QuickXSS."""

from __future__ import annotations

import shlex
from pathlib import Path

import typer

from quickxss.constants import CREDIT
from quickxss.models.scan import ScanConfig, ScanResult
from quickxss.scan.errors import DependencyError, ToolError, ValidationError
from quickxss.scan.io import validate_domain, validate_output_name
from quickxss.scan.pipeline import run_scan
from quickxss.utils.banner import render_banner
from quickxss.utils.log import Logger

app = typer.Typer(
    add_completion=False,
    no_args_is_help=True,
    context_settings={"help_option_names": ["-h", "--help"]},
)


@app.callback()
def root() -> None:
    """QuickXSS command line interface."""


@app.command()
def scan(
    domain: str = typer.Option(..., "--domain", "-d", help="Target domain."),
    blind: str | None = typer.Option(
        None, "--blind", "-b", help="Blind XSS payload."
    ),
    output: str = typer.Option(
        "results.txt", "--output", "-o", help="Output filename."
    ),
    results_dir: Path = typer.Option(
        Path("results"),
        "--results-dir",
        help="Base directory for scan outputs.",
    ),
    overwrite: bool = typer.Option(
        False,
        "--overwrite",
        help="Overwrite existing results directory.",
    ),
    use_wayback: bool = typer.Option(
        True, "--use-wayback/--no-wayback", help="Use waybackurls."
    ),
    use_gau: bool = typer.Option(
        True, "--use-gau/--no-gau", help="Use gau."
    ),
    gf_pattern: str = typer.Option(
        "xss", "--gf-pattern", help="gf pattern to use."
    ),
    dalfox_args: str = typer.Option(
        "", "--dalfox-args", help="Extra arguments passed to Dalfox."
    ),
    keep_temp: bool = typer.Option(
        True, "--keep-temp/--no-temp", help="Keep temp candidate file."
    ),
    verbose: bool = typer.Option(False, "--verbose", help="Verbose output."),
    quiet: bool = typer.Option(False, "--quiet", help="Suppress output."),
) -> None:
    """Run QuickXSS against a target domain."""

    logger = Logger(verbose=verbose, quiet=quiet)
    if not quiet:
        logger.info(render_banner().rstrip())
        logger.info(CREDIT)
        logger.info("")
    try:
        domain_value = validate_domain(domain)
        output_name = validate_output_name(output)
        resolved_dir = results_dir.expanduser().resolve()
        # Respect user quoting so extra Dalfox flags stay intact.
        dalfox_list = shlex.split(dalfox_args) if dalfox_args else []

        config = ScanConfig(
            domain=domain_value,
            results_dir=resolved_dir,
            output_name=output_name,
            overwrite=overwrite,
            use_wayback=use_wayback,
            use_gau=use_gau,
            gf_pattern=gf_pattern,
            blind_payload=blind,
            dalfox_args=dalfox_list,
            keep_temp=keep_temp,
            verbose=verbose,
            quiet=quiet,
        )

        result = run_scan(config, logger)
    except ValidationError as exc:
        logger.error(str(exc))
        raise typer.Exit(code=2) from exc
    except DependencyError as exc:
        logger.error(str(exc))
        raise typer.Exit(code=3) from exc
    except ToolError as exc:
        logger.error(str(exc))
        raise typer.Exit(code=4) from exc

    if not quiet:
        summary = _format_summary(result)
        logger.info(summary)


def _format_summary(result: ScanResult) -> str:
    """Format the final scan summary for display."""

    line = "-" * 60
    return "\n".join(
        [
            "Summary",
            line,
            f"URLs collected : {result.total_urls}",
            f"Candidates     : {result.candidate_urls}",
            f"Findings       : {result.findings}",
            f"Results        : {result.results_file}",
            line,
        ]
    )


def main() -> None:
    """CLI entrypoint."""

    app()


if __name__ == "__main__":
    main()
