# Tento Documentation

Welcome to the Tento project documentation.

## Quick Links

| Document | Description |
|----------|-------------|
| [Architecture Overview](./architecture-overview.md) | System architecture, technology stack, and component overview |
| [Frontend Architecture](./frontend-architecture.md) | Frontend implementation details, state management, and data fetching |
| [API Reference](./api-reference.md) | REST and GraphQL API endpoints |
| [Authentication Flow](./authentication-flow.md) | Detailed OAuth and JWT authentication documentation |
| [Deployment Guide](./deployment-guide.md) | Setup, configuration, and production deployment |
| [ADR: Agent Orchestration](./adr-agent-orchestration.md) | Architecture decision record for agent orchestration |

## Getting Started

### Development Setup

1. **Backend**: See [components/api/tento-server/README.md](../components/api/tento-server/README.md)
2. **Frontend**: See [components/ui/tento-web/README.md](../components/ui/tento-web/README.md)

### Quick Start

```bash
# Backend (Rust)
cd components/api/tento-server
cargo build
cargo run

# Frontend (React + Vite)
cd components/ui/tento-web
npm install
npm run dev
```

## Documentation Sections

### Architecture
- [Architecture Overview](./architecture-overview.md) - High-level system design
- [Frontend Architecture](./frontend-architecture.md) - Frontend patterns and structure

### API
- [API Reference](./api-reference.md) - Complete API endpoint documentation
- [Authentication Flow](./authentication-flow.md) - OAuth 2.0 and JWT implementation

### Operations
- [Deployment Guide](./deployment-guide.md) - Development and production setup
- [ADR: Agent Orchestration](./adr-agent-orchestration.md) - Agent architecture decisions

## Schema

JSON schemas for data models are located in the `schema/` directory:

- [quiz.json](./schema/quiz.json) - Quiz, QuizQuestion, and QuizQuestionOption models
