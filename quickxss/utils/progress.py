"""Progress display helpers."""

from __future__ import annotations

from contextlib import contextmanager
from dataclasses import dataclass, field
from typing import Iterator

from rich.console import Console


@dataclass(slots=True)
class Progress:
    """Minimal spinner-based progress helper."""

    enabled: bool
    _console: Console | None = field(init=False, default=None)

    def __post_init__(self) -> None:
        self._console = Console() if self.enabled else None

    @contextmanager
    def task(self, message: str) -> Iterator[None]:
        """Show a spinner while the wrapped task runs."""

        if not self._console:
            yield
            return
        with self._console.status(message, spinner="dots"):
            yield
