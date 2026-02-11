# Tento - Architecture Overview

## Table of Contents

- [System Architecture](#system-architecture)
- [Technology Stack](#technology-stack)
- [Component Overview](#component-overview)
- [Data Flow](#data-flow)
- [Security Model](#security-model)

## System Architecture

Tento is a full-stack web application built with a modern microservices-oriented architecture, consisting of a Rust backend API and a React frontend application.

```
┌─────────────────────────────────────────────────────────────────┐
│                         Client Layer                            │
│                                                                 │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │          React SPA (tento-web)                           │  │
│  │                                                          │  │
│  │  - React Router (routing)                                │  │
│  │  - React Query (data fetching/caching)                   │  │
│  │  - Axios (HTTP client with token refresh)                │  │
│  │  - GraphQL Client (graphql-request)                      │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
                              │
                              │ HTTPS
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                         API Layer                               │
│                                                                 │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │      Actix-Web API Server (tento-server)                 │  │
│  │                                                          │  │
│  │  ┌────────────┐  ┌──────────────┐  ┌────────────────┐  │  │
│  │  │  REST API  │  │   GraphQL    │  │  OAuth2 Flow   │  │  │
│  │  │ Endpoints  │  │   Endpoint   │  │  (GitHub)      │  │  │
│  │  └────────────┘  └──────────────┘  └────────────────┘  │  │
│  │                                                          │  │
│  │  ┌────────────────────────────────────────────────────┐ │  │
│  │  │         JWT Authentication Middleware              │ │  │
│  │  └────────────────────────────────────────────────────┘ │  │
│  │                                                          │  │
│  │  ┌────────────────────────────────────────────────────┐ │  │
│  │  │              Service Layer                         │ │  │
│  │  │  - UserService                                     │ │  │
│  │  │  - QuizService                                     │ │  │
│  │  │  - JwtService                                      │ │  │
│  │  └────────────────────────────────────────────────────┘ │  │
│  │                                                          │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
                              │
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                      Data Layer                                 │
│                                                                 │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │                   MongoDB Database                       │  │
│  │                                                          │  │
│  │  Collections:                                            │  │
│  │  - users                                                 │  │
│  │  - quizzes                                               │  │
│  │  - summary_documents                                     │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

## Technology Stack

### Backend (tento-server)

| Component | Technology | Purpose |
|-----------|-----------|---------|
| Runtime | Rust | High-performance, memory-safe systems programming |
| Web Framework | Actix-Web 4.x | Async web server with actor model |
| Database Driver | MongoDB (official driver) | NoSQL database access |
| Authentication | JWT (jsonwebtoken) | Stateless authentication tokens |
| GraphQL | async-graphql | Type-safe GraphQL implementation |
| OAuth2 | octocrab | GitHub OAuth integration |
| CORS | actix-cors | Cross-origin resource sharing |
| Logging | env_logger, log | Application logging |

### Frontend (tento-web)

| Component | Technology | Purpose |
|-----------|-----------|---------|
| Framework | React 19.x | UI component library |
| Language | TypeScript 5.x | Type-safe JavaScript |
| Build Tool | Vite (rolldown) | Fast bundler and dev server |
| Routing | React Router 6.x | Client-side routing |
| Data Fetching | TanStack React Query | Server state management and caching |
| HTTP Client | Axios | Promise-based HTTP client |
| GraphQL Client | graphql-request | Lightweight GraphQL client |
| State Management | React Context API | Authentication state |

## Component Overview

### Backend Components

#### 1. API Handlers (`src/handlers/`)
- **Purpose**: Handle HTTP requests and responses
- **Components**:
  - `auth_handler.rs` - GitHub OAuth callback, token refresh
  - `user_handler.rs` - User CRUD operations
  - `quiz_handler.rs` - Quiz operations
- **Responsibilities**: Request validation, response formatting, error handling

#### 2. Services (`src/services/`)
- **Purpose**: Business logic layer
- **Components**:
  - `user_service.rs` - User management logic
  - `quiz_service.rs` - Quiz management logic
  - `jwt_service.rs` - Token generation and validation
- **Responsibilities**: Data processing, business rules, database operations

#### 3. Repositories (`src/repositories/`)
- **Purpose**: Data access layer
- **Components**:
  - `user_repository.rs` - User data persistence
  - `quiz_repository.rs` - Quiz data persistence
  - `summary_document_repository.rs` - Document data persistence
- **Responsibilities**: Database queries, data mapping

#### 4. Authentication (`src/auth/`)
- **Purpose**: Security and authentication
- **Components**:
  - `jwt.rs` - Token creation, validation
  - `claims.rs` - JWT claims structures
  - `middleware.rs` - Request authentication
  - `utils.rs` - Authorization helpers
- **Responsibilities**: Token management, access control

#### 5. GraphQL (`src/graphql/`)
- **Purpose**: GraphQL API implementation
- **Components**:
  - `schema.rs` - GraphQL schema definition
  - Query and mutation resolvers
- **Responsibilities**: GraphQL query execution

### Frontend Components

#### 1. API Layer (`src/api/`)
- **Purpose**: Backend communication
- **Components**:
  - `client.ts` - Axios instance with token refresh
  - `graphql-client.ts` - GraphQL client configuration
  - `auth.ts` - Authentication endpoints
  - `users.ts` - User API calls
  - `quizzes.ts` - Quiz API calls
- **Responsibilities**: HTTP requests, error handling, token management

#### 2. Contexts (`src/contexts/`)
- **Purpose**: Global state management
- **Components**:
  - `AuthContext.tsx` - Authentication state
- **Responsibilities**: User session, login/logout

#### 3. Hooks (`src/hooks/`)
- **Purpose**: Reusable logic
- **Components**:
  - `useAuth.ts` - Authentication hook
  - `api/useUsers.ts` - User data queries/mutations
  - `api/useQuizzes.ts` - Quiz data queries/mutations
- **Responsibilities**: Data fetching, mutations, cache management

#### 4. Utilities (`src/utils/`)
- **Purpose**: Helper functions
- **Components**:
  - `constants.ts` - Configuration constants
  - `storage.ts` - LocalStorage management
- **Responsibilities**: Token storage, configuration

## Data Flow

### 1. Authentication Flow

```
User                    Frontend                Backend                GitHub
 │                         │                        │                     │
 │  Click "Login"          │                        │                     │
 ├────────────────────────►│                        │                     │
 │                         │  Redirect to GitHub    │                     │
 │                         ├───────────────────────────────────────────►│
 │                         │                        │                     │
 │  Authorize App          │                        │                     │
 ├─────────────────────────────────────────────────────────────────────►│
 │                         │                        │                     │
 │                         │  Callback with code    │                     │
 │◄────────────────────────┤                        │                     │
 │                         │                        │                     │
 │                         │  POST /auth/github/callback?code=XXX        │
 │                         ├───────────────────────►│                     │
 │                         │                        │  Exchange code      │
 │                         │                        ├────────────────────►│
 │                         │                        │  Return access_token│
 │                         │                        ◄─────────────────────┤
 │                         │                        │                     │
 │                         │                        │  Fetch user info    │
 │                         │                        ├────────────────────►│
 │                         │                        ◄─────────────────────┤
 │                         │                        │                     │
 │                         │                        │  Create/update user │
 │                         │                        │  (MongoDB)          │
 │                         │                        │                     │
 │                         │                        │  Generate JWT tokens│
 │                         │                        │                     │
 │                         │  Response:             │                     │
 │                         │  {                     │                     │
 │                         │    token,              │                     │
 │                         │    refresh_token,      │                     │
 │                         │    username,           │                     │
 │                         │    email               │                     │
 │                         │  }                     │                     │
 │                         ◄────────────────────────┤                     │
 │                         │                        │                     │
 │                         │  Store tokens          │                     │
 │                         │  (localStorage)        │                     │
 │                         │                        │                     │
 │  Redirect to Dashboard  │                        │                     │
 ◄─────────────────────────┤                        │                     │
 │                         │                        │                     │
```

### 2. Token Refresh Flow

```
Frontend                                    Backend
    │                                          │
    │  API Request with expired token          │
    ├─────────────────────────────────────────►│
    │                                          │
    │  401 Unauthorized                        │
    ◄──────────────────────────────────────────┤
    │                                          │
    │  POST /auth/refresh                      │
    │  { refresh_token: "..." }                │
    ├─────────────────────────────────────────►│
    │                                          │
    │                                          │ Validate refresh_token
    │                                          │ Generate new tokens
    │                                          │
    │  Response:                               │
    │  {                                       │
    │    token: "new_access_token",            │
    │    refresh_token: "new_refresh_token"    │
    │  }                                       │
    ◄──────────────────────────────────────────┤
    │                                          │
    │  Store new tokens                        │
    │  Retry original request                  │
    ├─────────────────────────────────────────►│
    │                                          │
    │  200 OK with data                        │
    ◄──────────────────────────────────────────┤
    │                                          │
```

### 3. Protected API Request Flow

```
Frontend                    Backend                    Database
    │                          │                           │
    │  API Request             │                           │
    │  Authorization: Bearer   │                           │
    ├─────────────────────────►│                           │
    │                          │                           │
    │                          │ Validate JWT              │
    │                          │ Extract claims            │
    │                          │                           │
    │                          │ Execute business logic    │
    │                          │                           │
    │                          │ Query/Update data         │
    │                          ├──────────────────────────►│
    │                          │                           │
    │                          │ Return data               │
    │                          ◄───────────────────────────┤
    │                          │                           │
    │  Response with data      │                           │
    ◄──────────────────────────┤                           │
    │                          │                           │
```

## Security Model

### Authentication

**Token Types:**
- **Access Token**: Short-lived (1 hour), used for API authentication
- **Refresh Token**: Long-lived (7 days), used to obtain new access tokens

**Token Storage:**
- Frontend: localStorage (keys: `tento_access_token`, `tento_refresh_token`)
- Backend: Stateless JWT validation (no server-side storage)

### Authorization

**Role-Based Access Control (RBAC):**
- **User Role**: Standard user permissions
- **Admin Role**: Full system access

**Middleware Protection:**
```rust
// All protected routes require valid JWT
.service(
    web::scope("")
        .wrap(AuthMiddleware)  // Validates JWT and injects Claims
        .service(protected_endpoint)
)
```

**Authorization Helpers:**
- `require_admin()` - Ensures user has admin role
- `require_owner_or_admin()` - Ensures user owns resource or is admin

### CORS Configuration

**Allowed Origins:**
- `http://localhost:5173` (development frontend)
- `http://localhost:3000` (alternative dev port)

**Allowed Methods:**
- GET, POST, PUT, DELETE, OPTIONS

**Allowed Headers:**
- Authorization, Accept, Content-Type

**Configuration Location:** `components/api/tento-server/src/main.rs`

### Token Security

**JWT Claims Structure:**
```rust
// Access Token Claims
{
    sub: username,        // Subject (user identifier)
    id: user_id,          // User UUID
    role: "user|admin",   // User role
    exp: timestamp,       // Expiration (1 hour)
    iat: timestamp        // Issued at
}

// Refresh Token Claims
{
    sub: username,        // Subject (user identifier)
    token_type: "refresh", // Token type identifier
    exp: timestamp,       // Expiration (7 days)
    iat: timestamp        // Issued at
}
```

**Token Validation:**
1. Signature verification using secret key
2. Expiration check
3. Token type validation (for refresh tokens)
4. Claims extraction

## Directory Structure

```
tento-main/
├── components/
│   ├── api/
│   │   └── tento-server/           # Rust backend
│   │       ├── src/
│   │       │   ├── handlers/       # HTTP request handlers
│   │       │   ├── services/       # Business logic
│   │       │   ├── repositories/   # Data access
│   │       │   ├── auth/           # Authentication
│   │       │   ├── graphql/        # GraphQL implementation
│   │       │   ├── models/         # Data models
│   │       │   ├── errors/         # Error types
│   │       │   └── main.rs         # Application entry
│   │       ├── Cargo.toml          # Rust dependencies
│   │       └── .env.local          # Backend configuration
│   │
│   └── ui/
│       └── tento-web/              # React frontend
│           ├── src/
│           │   ├── api/            # API clients
│           │   ├── contexts/       # React contexts
│           │   ├── hooks/          # Custom hooks
│           │   ├── utils/          # Utilities
│           │   ├── types/          # TypeScript types
│           │   ├── lib/            # Libraries
│           │   ├── App.tsx         # Main component
│           │   └── main.tsx        # Application entry
│           ├── package.json        # npm dependencies
│           └── .env                # Frontend configuration
│
└── docs/                           # Documentation
    └── architecture-overview.md    # This file
```

## Related Documentation

- [Authentication Flow](./authentication-flow.md) - Detailed authentication documentation
- [API Reference](./api-reference.md) - Backend API endpoints
- [Frontend Architecture](./frontend-architecture.md) - Frontend implementation details
- [Deployment Guide](./deployment-guide.md) - Configuration and deployment
