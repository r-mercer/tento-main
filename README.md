# Tento

A full-stack quiz application with a Rust backend API and React frontend.

## Features

- Quiz creation and management
- GitHub OAuth authentication
- JWT-based session management with token refresh
- REST and GraphQL APIs
- Role-based access control (user/admin)

## Tech Stack

| Layer | Technology |
|-------|------------|
| Frontend | React 19, TypeScript, Vite, TanStack Query, Fluent UI |
| Backend | Rust, Actix-web, async-graphql, MongoDB |
| Auth | GitHub OAuth 2.0, JWT |

## Prerequisites

- **Backend**: Rust (latest stable), MongoDB
- **Frontend**: Node.js 20+, npm

## Configuration

### Backend

Create `components/api/tento-server/.env` with required environment variables (see [backend README](components/api/tento-server/README.md) for full list):

```bash
MONGO_CONN_STRING=mongodb://localhost:27017
MONGO_DB_NAME=tento
GH_CLIENT_ID=your-github-client-id
GH_CLIENT_SECRET=your-github-client-secret
JWT_SECRET=your-secret-key
```

### Frontend

Create `components/ui/tento-web/.env`:

```bash
VITE_API_BASE_URL=http://localhost:8080
VITE_GH_CLIENT_ID=your-github-client-id
VITE_GH_REDIRECT_URI=http://localhost:5173/auth/callback
```

## Quick Start

### 1) Backend (Rust)

```bash
cd components/api/tento-server
cargo build
cargo run
```

### 2) Frontend (React + Vite)

```bash
cd components/ui/tento-web
npm install
npm run dev
```

Frontend expects `VITE_API_BASE_URL` to point to the backend (default: `http://localhost:8080`).

## Verification Commands

### Backend

```bash
cd components/api/tento-server
cargo test
cargo test --test integration_tests
cargo test --test repository_contract_tests
cargo clippy
cargo fmt -- --check
```

### Frontend

```bash
cd components/ui/tento-web
npm run lint
npm run build
```

## Docs

- General docs: [docs](docs/README.md)
- API reference: [docs/api-reference.md](docs/api-reference.md)
- Architecture overview: [docs/architecture-overview.md](docs/architecture-overview.md)
- Deployment guide: [docs/deployment-guide.md](docs/deployment-guide.md)
