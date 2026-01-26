"""Filesystem helpers."""

from __future__ import annotations

import shutil
from pathlib import Path


def copy_tree(source: Path, destination: Path) -> None:
    """Copy files and folders from source to destination."""

    for item in source.iterdir():
        target = destination / item.name
        if item.is_dir():
            shutil.copytree(item, target, dirs_exist_ok=True)
        else:
            shutil.copy2(item, target)
