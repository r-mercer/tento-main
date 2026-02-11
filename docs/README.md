# Tento Documentation

Comprehensive documentation for the Tento full-stack application.

## Quick Start

1. [Deployment Guide](./deployment-guide.md) - Set up development environment
2. [Architecture Overview](./architecture-overview.md) - Understand system design
3. [Authentication Flow](./authentication-flow.md) - Learn how auth works

## Documentation Index

### Architecture and Design

**[Architecture Overview](./architecture-overview.md)**
- System architecture and component overview
- Technology stack
- Data flow diagrams
- Security model
- Directory structure

**[Authentication Flow](./authentication-flow.md)**
- GitHub OAuth integration
- JWT token management
- Token refresh mechanism
- Frontend and backend implementation
- Security considerations

**[Frontend Architecture](./frontend-architecture.md)**
- React application structure
- State management strategies
- Data fetching with React Query
- Routing architecture
- Type safety with TypeScript
- Performance optimization

### API Documentation

**[API Reference](./api-reference.md)**
- REST API endpoints
- GraphQL API
- Authentication requirements
- Request/response formats
- Error handling
- Testing examples

### Operations

**[Deployment and Configuration Guide](./deployment-guide.md)**
- Prerequisites and installation
- Environment configuration
- Backend setup (Rust/Actix-Web)
- Frontend setup (React/Vite)
- Database setup (MongoDB)
- GitHub OAuth configuration
- Production deployment
- Troubleshooting guide

## Project Structure

```
tento-main/
├── components/
│   ├── api/
│   │   └── tento-server/          # Backend (Rust)
│   └── ui/
│       └── tento-web/             # Frontend (React)
└── docs/                          # Documentation (you are here)
    ├── README.md                  # This file
    ├── architecture-overview.md
    ├── authentication-flow.md
    ├── api-reference.md
    ├── frontend-architecture.md
    └── deployment-guide.md
```

## Technology Stack

### Backend
- **Language**: Rust
- **Framework**: Actix-Web 4.x
- **Database**: MongoDB
- **Authentication**: JWT + GitHub OAuth

### Frontend
- **Framework**: React 19.x
- **Language**: TypeScript 5.9.x
- **Build Tool**: Vite 7.x
- **State Management**: React Query + Context API
- **Routing**: React Router 6.x

## Key Features

### Authentication
- GitHub OAuth 2.0 integration
- JWT access tokens (1 hour expiry)
- Refresh tokens (7 day expiry)
- Automatic token refresh on API requests
- Stateless authentication

### API
- RESTful endpoints for CRUD operations
- GraphQL endpoint for complex queries
- CORS support for cross-origin requests
- JWT middleware for protected routes
- Detailed error messages

### Frontend
- Type-safe API integration
- Automatic token refresh
- Optimized caching with React Query
- Protected route components
- Responsive design

## Development Workflow

### Starting the Application

**1. Start Database:**
```bash
# MongoDB via Homebrew
brew services start mongodb-community@6.0

# Or via Docker
docker start tento-mongodb
```

**2. Start Backend:**
```bash
cd components/api/tento-server
cargo run
```

**3. Start Frontend:**
```bash
cd components/ui/tento-web
npm run dev
```

### Access Points

| Service | URL | Description |
|---------|-----|-------------|
| Frontend | http://localhost:5173 | React application |
| Backend API | http://localhost:8080 | REST/GraphQL API |
| GraphQL Playground | http://localhost:8080/playground | Interactive GraphQL IDE |
| Health Check | http://localhost:8080/health | API health status |

## Common Tasks

### Testing the API

**Health check:**
```bash
curl http://localhost:8080/health
```

**Token refresh test:**
```bash
cd components/api/tento-server
./scripts/test_refresh_token.sh
```

**Protected endpoint:**
```bash
curl http://localhost:8080/api/users \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Building for Production

**Backend:**
```bash
cd components/api/tento-server
cargo build --release
./target/release/tento-server
```

**Frontend:**
```bash
cd components/ui/tento-web
npm run build
# Output in dist/ directory
```

## Environment Variables

### Backend (.env.local)
```bash
WEB_SERVER_HOST=127.0.0.1
WEB_SERVER_PORT=8080
MONGODB_URI=mongodb://localhost:27017
MONGODB_DATABASE=tento
JWT_SECRET=your-secret-key
JWT_EXPIRATION_HOURS=1
JWT_REFRESH_EXPIRATION_HOURS=168
GH_CLIENT_ID=your-github-client-id
GH_CLIENT_SECRET=your-github-client-secret
RUST_LOG=info
```

### Frontend (.env)
```bash
VITE_API_BASE_URL=http://localhost:8080
VITE_GH_CLIENT_ID=your-github-client-id
VITE_GH_REDIRECT_URI=http://localhost:5173/auth/callback
```

## Security Best Practices

1. **Never commit secrets** to version control
2. **Use strong JWT secrets** (64+ random characters)
3. **Enable HTTPS** in production
4. **Configure CORS** properly for production domains
5. **Rotate secrets** regularly
6. **Use environment-specific** OAuth apps
7. **Enable MongoDB authentication** in production
8. **Implement rate limiting** for API endpoints

## Troubleshooting

### Common Issues

**Backend won't start:**
- Check MongoDB is running
- Verify `.env.local` configuration
- Ensure port 8080 is available

**Frontend can't connect to API:**
- Verify backend is running
- Check CORS configuration
- Confirm `VITE_API_BASE_URL` is correct

**OAuth flow fails:**
- Verify GitHub OAuth app settings
- Check client ID matches in both apps
- Ensure redirect URI is exact match

**Token refresh fails:**
- Check refresh token in localStorage
- Verify JWT_SECRET matches
- Test `/auth/refresh` endpoint

See [Deployment Guide](./deployment-guide.md#troubleshooting) for detailed troubleshooting.

## API Endpoints Overview

### Public Endpoints
- `GET /health` - Health check
- `GET /auth/github/callback` - OAuth callback
- `POST /auth/refresh` - Refresh access token

### Protected Endpoints
- `GET /api/users` - List all users
- `GET /api/users/{id}` - Get user by ID
- `POST /api/users` - Create user (admin only)
- `PUT /api/users/{id}` - Update user
- `DELETE /api/users/{id}` - Delete user (admin only)
- `GET /api/quizzes/{id}` - Get quiz
- `POST /graphql` - GraphQL endpoint

See [API Reference](./api-reference.md) for complete documentation.

## Contributing

### Code Style

**Backend (Rust):**
- Format: `cargo fmt`
- Lint: `cargo clippy`
- Test: `cargo test`

**Frontend (TypeScript):**
- Lint: `npm run lint`
- Type check: `npm run build`
- Format: Follow project conventions

### Git Workflow

1. Create feature branch
2. Make changes
3. Run tests and linting
4. Commit with clear messages
5. Push and create pull request

## Resources

### Official Documentation
- [Rust](https://www.rust-lang.org/learn)
- [Actix-Web](https://actix.rs/)
- [React](https://react.dev/)
- [TypeScript](https://www.typescriptlang.org/docs/)
- [React Query](https://tanstack.com/query/latest)
- [MongoDB](https://www.mongodb.com/docs/)

### Tools
- [Cargo](https://doc.rust-lang.org/cargo/)
- [npm](https://docs.npmjs.com/)
- [Vite](https://vitejs.dev/)
- [React Router](https://reactrouter.com/)

## License

See LICENSE file for details.

## Support

For questions or issues:
1. Review this documentation
2. Check troubleshooting section
3. Search existing issues
4. Create new issue with details

---

Last updated: 2026-02-11
