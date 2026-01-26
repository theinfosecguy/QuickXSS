"""Setup models."""

from __future__ import annotations

from dataclasses import dataclass
from typing import List, Mapping


@dataclass(frozen=True, slots=True)
class SetupReport:
    """Status report for setup checks."""

    tools: Mapping[str, bool]
    gf_pattern: bool
    os_name: str
    install_supported: bool

    @property
    def missing_tools(self) -> List[str]:
        """Return missing tool names in order."""

        return [name for name, ok in self.tools.items() if not ok]

    @property
    def ok(self) -> bool:
        """Return True when all requirements are met."""

        return not self.missing_tools and self.gf_pattern
