# Agent Orchestration Architecture Decision Record (ADR)

Status: Accepted
Date: 2026-03-02

## Context

The Tento monorepo comprises multiple agent-related packages that together perform autonomous, task-driven workflows. To enable reliable, scalable coordination across these agents while keeping the design approachable, we need a clear orchestration strategy. Goals include:

- Efficient task scheduling across heterogeneous agents
- Observability of task progress, retries, and performance
- Resilience to agent churn and partial outages
- Simple evolution path with well-defined versioning and compatibility rules

This ADR documents the rationale and decisions around agent orchestration, trade-offs considered, and a minimal monorepo CI plan to support the design.

## Decision

Adopt a central orchestrator pattern with registration, heartbeats, and a per-task queue that assigns work to agents based on capabilities and current load. Communication is via HTTP/JSON for requests and WebSocket (or long-polling) for streaming updates. The architecture emphasizes clear interfaces, idempotent task execution, and observable state transitions.

Key components:

- Orchestrator service: central coordinator responsible for task submission, scheduling, and accounting.
- Agent registry: maintains agent metadata, capabilities, version, and health status via periodic heartbeats.
- Task model: describes work, requirements, priority, timeouts, and retry policies.
- Communication layer: REST APIs for submission and management; WebSocket/streaming channel for progress updates; optional message-bus integration for decoupled environments.

This ADR intentionally focuses on a minimal, pragmatic implementation that can evolve with the project. It favors clarity and reliability over speculative optimizations.

## Rationale

- Central orchestrator provides a single source of truth for task state, simplifying debugging, auditing, and replay scenarios.
- Clear per-task lifecycle (CREATED -> SCHEDULED -> ASSIGNED -> IN_PROGRESS -> COMPLETED/FAILED) enables robust retry and timeout semantics.
- Explicit agent metadata (capabilities, version, load) makes it straightforward to support heterogeneous agents and capacity-based scheduling.
- Observability: standardized events and metrics allow rapid diagnosis of bottlenecks and failures.
- Extensibility: the orchestration layer can be extended to support more complex scheduling heuristics, routing rules, and policy enforcement without destabilizing agents.

Trade-offs considered:

- Centralized bottleneck vs resilience: We mitigate risk with stateless task carriers, retries, and a lightweight back-end database to store state. In the future, we can introduce a hybrid mode with local scheduling at edge agents when high isolation is required.
- Protocol simplicity vs performance: HTTP + WebSocket is chosen for simplicity and wide framework support. We can add a message bus (Kafka/RabbitMQ) if throughput or decoupling becomes necessary.
- Developer velocity vs operational complexity: A pragmatic, incremental approach keeps CI/simple, while leaving room for deeper optimizations as needs grow.

## Consequences

- Positive:
  - Predictable task lifecycle and easier debugging
  - Clear auditing trail and metrics
  - Incremental migration path: can start with a small orchestrator and grow features over time
- Negative:
  - Introducing a central point of failure requires careful reliability design (heartbeats, retries, graceful degradation)
  - Slightly more complex deployment topology

## Alternatives Considered

1) Fully decentralized (peer-to-peer) orchestration
   - Pros: eliminates single orchestrator, potentially higher resilience to orchestrator failure
   - Cons: scheduling consistency is hard; higher complexity; more difficult to audit and test

2) Brokered architecture using a message bus
   - Pros: decoupled components; scalable through backpressure
   - Cons: adds operational overhead and more moving parts; requires event schemas and tooling

3) Hybrid approach (local worker queues with a lightweight central coordinator)
   - Pros: reduces central bottlenecks; preserves some global visibility
   - Cons: partial convergence on policy may be tricky; more migration work

Chosen option: central orchestrator with a shared task registry and per-agent queues (with hooks for future hybrid/messaging enablement).

## Data Model (High level)

- Agent
  - id: string
  - capabilities: string[]
  - version: string
  - status: 'online' | 'offline' | 'busy'
  - last_seen: timestamp

- Task
  - id: string
  - type: string
  - payload: object
  - requirements: string[] (capabilities required)
  - priority: number
  - timeout_ms: number
  - max_retries: number
  - status: 'CREATED' | 'SCHEDULED' | 'ASSIGNED' | 'IN_PROGRESS' | 'COMPLETED' | 'FAILED'
  - assigned_agent_id?: string
  - created_at: timestamp
  - updated_at: timestamp
  - history: Array<{ event: string, at: timestamp, detail?: string }>

## Implementation Outline (What to build first)

- Orchestrator service (Node/Go/Rust)
  - API: register_agent, submit_task, query_task, cancel_task, heartbeat
  - Scheduling: pick most suitable available agent based on capabilities and recent load
  - Persistence: lightweight DB (SQLite/PostgreSQL) to store task state and history
  - Broadcast updates via WebSocket or server-sent events

- Agent client (library or runtime)
  - Register on startup; send heartbeats; poll or listen for tasks
  - Execute task payloads; report progress and completion

- Observability
  - Emit metrics for tasks_created, tasks_assigned, tasks_in_progress, tasks_completed, tasks_failed
  - Structured logs with correlation IDs between orchestrator and agents

- Security
  - TLS, token-based authentication, scoped permissions

## Monorepo CI Plan (Minimal, per-package checks)

Purpose: Ensure each package in the monorepo remains healthy (lint, typecheck, tests, and build) and that the orchestrator integration remains compatible with the agent libraries.

Packages assumed in the monorepo:
- packages/agent-core
- packages/agent-runtime
- packages/agent-orchestrator
- packages/agent-ui

Per-package checks (adjust to your actual package.json scripts):
- lint: lint sources
- typecheck: run type checks (e.g., tsc --noEmit)
- test: unit tests
- build: compile/transpile
- e2e (optional): end-to-end tests for orchestration flows

CI goals:
- Run checks per package in parallel where possible
- Cache dependencies to speed up builds
- Fail fast on first broken package
- Produce a summary of coverage and test results

## Example Workflow Outline (GitHub Actions)

This is a minimal starting point. It uses npm workspaces and a matrix to exercise all top-level packages.

```
name: Monorepo CI

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

jobs:
  ci:
    runs-on: ubuntu-latest
    strategy:
      fail-fast: false
      matrix:
        package: ["agent-core", "agent-runtime", "agent-orchestrator", "agent-ui"]
    steps:
      - name: Checkout
        uses: actions/checkout@v4

      - name: Setup Node
        uses: actions/setup-node@v4
        with:
          node-version: '18'

      - name: Install dependencies (workspace)
        run: |
          npm ci --workspaces

      - name: Lint
        run: |
          npm run -w ${{ matrix.package }} lint

      - name: Typecheck
        run: |
          npm run -w ${{ matrix.package }} typecheck

      - name: Build
        run: |
          npm run -w ${{ matrix.package }} build

      - name: Test
        run: |
          npm run -w ${{ matrix.package }} test

      - name: End-to-end checks (optional)
        if: ${{ matrix.package == 'agent-orchestrator' }}
        run: |
          echo "Run optional e2e checks here"

      - name: Coverage summary (optional)
        if: always()
        run: |
          echo "Collect and upload coverage if applicable"
```

Notes:
- If you use a different monorepo tool (e.g., pnpm, Yarn workspaces, or Nx), adapt the workspace commands accordingly.
- Consider adding a separate workflow for integration tests that exercises orchestration flows using a small sample dataset.
- You can extend the matrix with additional packages or variants (e.g., Node vs TS builds, or different Node versions).
