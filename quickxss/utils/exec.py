"""Command execution helpers."""

from __future__ import annotations

import subprocess
from typing import List

from quickxss.scan.errors import ToolError
from quickxss.utils.log import Logger


def run_command(command: List[str], logger: Logger) -> None:
    """Run a command and raise ToolError on failure."""

    logger.debug(f"Running: {' '.join(command)}")
    result = subprocess.run(command, capture_output=True, text=True, check=False)
    if result.returncode != 0:
        message = result.stderr.strip() or "Command failed."
        raise ToolError(message, command=command)
