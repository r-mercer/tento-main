Tento Workflow Rules and Delegation Guide

Purpose
- This document codifies how I analyze tasks, decide whether to delegate to specialized agents, and execute work in a reliable, auditable way within this codebase.

Overview of the core workflow
1) Understand
- Parse the explicit requirements and infer implicit needs.
2) Path Analysis
- Evaluate options to optimize for quality, speed, cost, and reliability; choose the best path.
3) Delegation Check
- Before acting, review specialist capabilities and decide whether delegation provides a net efficiency gain.
- If delegating, perform the delegation in the same turn.
4) Parallelize
- Break work into independent tasks and execute in parallel where safe and beneficial.
5) Execute
- Perform the tasks (either by self or delegated specialists) and integrate results.
6) Verify
- Validate outputs with diagnostics and user requirements; iterate if needed.

Specialist Roles and When to Use Them
- @explorer: Parallel discovery across codebase (finding files, symbols, patterns)
- @librarian: Official docs and API references for evolving libraries
- @oracle: High-stakes architectural decisions and persistent problems
- @designer: UI/UX polish and design systems
- @fixer: Implementer for clearly specified tasks; executes changes

Delegation Protocol
- Use delegation to leverage specialized expertise when it yields greater speed/quality.
- When you mention a specialist, I will launch the relevant agent in the same turn.
- Reference paths/lines (e.g., src/app.ts:42) instead of printing full files.
- Provide context summaries; let specialists pull needed details.
- If the task is trivial or highly time-sensitive, I’ll perform it myself without delegation.
- Ensure changes are minimal and testable; break into small patches when possible.

Task States
- pending: task not started
- in_progress: currently being worked on (limit: ONE in_progress at a time)
- completed: finished successfully
- cancelled: no longer needed

How I use tools safely
- Avoid destructive operations unless explicitly requested.
- If you want a patch committed, I will prompt for confirmation or you may specify to proceed.
- I will not push to remotes without explicit instruction.

Example runthrough (high level)
- Step 1: Understand a request for a multi-part feature
- Step 2: Path Analysis suggests two independent parts: (A) frontend polish and (B) backend contract drift fixes
- Step 3: Delegation Check: delegate A to @designer for UI polish; delegate B to @fixer or @librarian depending on content
- Step 4: Parallelize: Run A and B in parallel
- Step 5: Execute: Apply patches; run tests
- Step 6: Verify: Run lints/tests; confirm user requirements met

Patchability and Verification
- For any patch: provide a patch description, files touched, and rationale
- After patch, run tests (where feasible) and report results

Notes
- This document is a living artifact; update it as processes evolve.
