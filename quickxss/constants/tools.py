"""Tooling constants."""

from __future__ import annotations

from typing import Dict, List

REQUIRED_TOOLS: List[str] = ["gf", "dalfox", "waybackurls", "gau"]

GO_TOOLS: Dict[str, str] = {
    "gf": "github.com/tomnomnom/gf@latest",
    "waybackurls": "github.com/tomnomnom/waybackurls@latest",
    "dalfox": "github.com/hahwul/dalfox/v2@latest",
    "gau": "github.com/lc/gau@latest",
}

GF_REPO_URL: str = "https://github.com/tomnomnom/gf"
GF_PATTERNS_REPO_URL: str = "https://github.com/1ndianl33t/Gf-Patterns"
