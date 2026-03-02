Guidelines Snapshot

This document provides a quick-reference map to the authoritative, package-scoped guidelines used by AI coding agents across this repository.

Key references (link targets are relative to the repo root):
- Root Copilot Instructions: .github/copilot-instructions.md
- Frontend package instructions: components/ui/tento-web/.github/copilot-instructions.md
- Backend package instructions: components/api/tento-server/.github/copilot-instructions.md
- Frontend AGENTS guidance: components/ui/tento-web/.models/AGENTS.md
- Backend AGENTS guidance: components/api/tento-server/.models/AGENTS.md
- Frontend implementation plans: components/ui/tento-web/.models/implementation-plans/
- Backend implementation plans: components/api/tento-server/.models/implementation-plans/
- Guidelines for PRs and tests are anchored in the respective package AGENTS.md and TODOs.

Usage notes:
- Treat package-level files as the source of truth when editing within that package.
- Use the root file for monorepo-wide defaults and shared conventions.

Last updated: 2026-03-02

## Automation helper

- Guidelines drift detector: tools/guidelines_drift.py
- Run: python3 tools/guidelines_drift.py
- Purpose: quick health check to ensure Last updated stamps exist on the three Copilot instruction files and match the canonical date used in this repo.
