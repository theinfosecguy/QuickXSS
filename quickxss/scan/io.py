"""Filesystem helpers for QuickXSS."""

from __future__ import annotations

from pathlib import Path
from typing import Iterable

from quickxss.models.scan import ScanPaths
from quickxss.scan.errors import ValidationError


def validate_domain(domain: str) -> str:
    """Validate the domain input and return a normalized value."""

    value = domain.strip()
    if not value:
        raise ValidationError("Domain is required.")
    # Block path traversal and accidental directory nesting.
    if "/" in value or "\\" in value:
        raise ValidationError("Domain must not contain path separators.")
    if ".." in value:
        raise ValidationError("Domain must not contain '..'.")
    return value


def ensure_scan_paths(
    results_dir: Path, domain: str, output_name: str, overwrite: bool
) -> ScanPaths:
    """Create and return output paths for a scan."""

    base_dir = results_dir / domain
    if base_dir.exists() and not overwrite:
        raise ValidationError(
            f"Results directory already exists: {base_dir}. Use --overwrite to reuse it."
        )
    base_dir.mkdir(parents=True, exist_ok=True)
    urls_file = base_dir / f"{domain}.txt"
    temp_xss_file = base_dir / f"{domain}_temp_xss.txt"
    xss_file = base_dir / f"{domain}_xss.txt"
    results_file = base_dir / output_name
    return ScanPaths(
        base_dir=base_dir,
        urls_file=urls_file,
        temp_xss_file=temp_xss_file,
        xss_file=xss_file,
        results_file=results_file,
    )


def validate_output_name(name: str) -> str:
    """Validate the output filename and return a normalized value."""

    value = name.strip()
    if not value:
        raise ValidationError("Output filename is required.")
    if "/" in value or "\\" in value:
        raise ValidationError("Output filename must not contain path separators.")
    if ".." in value:
        raise ValidationError("Output filename must not contain '..'.")
    return value


def write_lines(path: Path, lines: Iterable[str]) -> None:
    """Write lines to a file, ensuring a trailing newline when non-empty."""

    content = "\n".join(lines)
    if content:
        content += "\n"
    path.write_text(content, encoding="utf-8")


def dedupe_preserve_order(lines: Iterable[str]) -> list[str]:
    """De-duplicate lines while preserving order."""

    seen: set[str] = set()
    output: list[str] = []
    for line in lines:
        if line not in seen:
            seen.add(line)
            output.append(line)
    return output
