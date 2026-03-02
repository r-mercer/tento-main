OpenCode Cross-Package Policy Matrix
Last updated: 2026-03-02

- Purpose: A concise reference outlining how major policy areas are implemented across packages, to reduce drift and speed onboarding.

- Scope: Applies to root repo and package-level guidelines for tento-main.

- Key Policy Areas and Where to Read:

- Precedence and Scope
  - Rule: Package-level Copilot instructions override root for that package (see root .github/copilot-instructions.md and per-package copies).
  - Where to read: .github/copilot-instructions.md (root), components/ui/tento-web/.github/copilot-instructions.md, components/api/tento-server/.github/copilot-instructions.md

- Authentication / Ownership Checks
  - Principle: Centralized auth contracts and owner checks live in backend (claims) and frontend uses contextual auth state; both should align with documented policy in their AGENTS.md.
  - Where to read: components/api/tento-server/.models/AGENTS.md, components/ui/tento-web/.models/AGENTS.md, and their respective implementation plans.

- Logging / Security / Secrets
  - Principle: Do not log secrets; redact sensitive payloads in real logging paths; use env/config with SecretString where applicable.
  - Where to read: AGENTS.md for frontend/backend, and implementation plans discuss redaction and secure logging practices.

- Testing & Validation
  - Principle: Ensure unit/integration tests cover new policy edges; run npm run lint, npm run test, and npm run build for frontend; cargo test and cargo clippy for backend.
  - Where to read: Implementation plans (W0–S3 sections) outline tests; AGENTS.md contains testing guidance.

- Documentation Alignment
  - Principle: Keep docs in sync with code; update READMEs and docs when API/auth contracts change.
  - Where to read: Implementation plans and the root Copilot instructions docs.

- Quick Reference: How to verify
  - Frontend: npm run lint; npm run test; npm run build
  - Backend: cargo fmt --check; cargo clippy; cargo test; cargo test --test integration_tests; cargo test --test repository_contract_tests

This matrix is intended to be lightweight and is not a full policy spec. For detailed behavior, consult the per-package AGENTS.md and Copilot-instructions files.
