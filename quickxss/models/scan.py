"""Data models for QuickXSS."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Sequence


@dataclass(frozen=True, slots=True)
class ScanConfig:
    """Configuration for a QuickXSS scan."""

    domain: str
    results_dir: Path
    output_name: str
    overwrite: bool
    use_wayback: bool
    use_gau: bool
    gf_pattern: str
    blind_payload: str | None
    dalfox_args: Sequence[str]
    keep_temp: bool
    verbose: bool
    quiet: bool


@dataclass(frozen=True, slots=True)
class ScanPaths:
    """Computed output paths for a scan."""

    base_dir: Path
    urls_file: Path
    temp_xss_file: Path
    xss_file: Path
    results_file: Path


@dataclass(frozen=True, slots=True)
class ScanResult:
    """Summary of a scan run."""

    total_urls: int
    candidate_urls: int
    findings: int
    results_file: Path
