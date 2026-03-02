#!/usr/bin/env python3
"""
Guidelines drift detector for OpenCode usage.

Checks that the Last updated stamp exists on package Copilot instruction files
and warns if the stamps are missing or differ from the expected value.
"""

import re
import sys
from pathlib import Path

# Repo root (tento-main)
ROOT = Path(__file__).resolve().parents[1]

# Target guideline files to validate
GUIDELINE_FILES = [
    ".github/copilot-instructions.md",
    "components/ui/tento-web/.github/copilot-instructions.md",
    "components/api/tento-server/.github/copilot-instructions.md",
    "components/ui/tento-web/.models/AGENTS.md",
    "components/api/tento-server/.models/AGENTS.md",
]

# Expected stamp value (kept in sync with patch updates)
EXPECTED_LAST_UPDATED = "Last updated: 2026-03-02"

def read_text(p: Path) -> str:
    try:
        return p.read_text(encoding="utf-8", errors="ignore")
    except FileNotFoundError:
        return ""

from typing import Optional

def extract_last_updated(text: str) -> Optional[str]:
    m = re.search(r"^Last updated:\s*(.+)$", text, re.MULTILINE)
    if m:
        return f"Last updated: {m.group(1).strip()}"
    return None

def main() -> int:
    issues = []
    for rel in GUIDELINE_FILES:
        path = ROOT / rel
        content = read_text(path)
        if not content:
            issues.append((str(path), "MISSING"))
            continue
        found = extract_last_updated(content)
        if not found:
            issues.append((str(path), "MISSING_LAST_UPDATED"))
        elif found != EXPECTED_LAST_UPDATED:
            issues.append((str(path), f"MISMATCH('{found}')"))

    if issues:
        print("Guidelines drift detected:")
        for p, note in issues:
            print(f"- {p}: {note}")
        return 2
    print("All guidelines stamps are up to date.")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
