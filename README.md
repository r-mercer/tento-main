# tento-main

Monorepo for Tento:

- Backend API: [components/api/tento-server](components/api/tento-server/README.md)
- Frontend app: [components/ui/tento-web](components/ui/tento-web/README.md)

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
