# Tento - API Reference

## Table of Contents

- [Overview](#overview)
- [Base URLs](#base-urls)
- [Authentication](#authentication)
- [Error Handling](#error-handling)
- [Public Endpoints](#public-endpoints)
- [Protected Endpoints](#protected-endpoints)
- [GraphQL Endpoint](#graphql-endpoint)

## Overview

The Tento API provides both REST and GraphQL interfaces for managing users, quizzes, and summary documents. The API follows RESTful conventions with JSON request/response payloads.

### API Versioning

**Current Version:** v1 (implicit)

**Base Path:** `/api` for protected REST endpoints

### Content Type

All requests and responses use `application/json` content type.

### Response Format

**Success Response:**
```json
{
  "id": "...",
  "field": "value",
  ...
}
```

**Error Response:**
```json
{
  "message": "Error description",
  "status": 400
}
```

## Base URLs

| Environment | URL |
|------------|-----|
| Development | `http://localhost:8080` |
| Production | TBD |

## Authentication

### Public Endpoints

No authentication required:
- `GET /health`
- `GET /auth/github/callback`
- `POST /auth/refresh`

### Protected Endpoints

Require JWT token in Authorization header:

```http
Authorization: Bearer <access_token>
```

**Token Expiration:**
- Access Token: 1 hour
- Refresh Token: 7 days (168 hours)

**Token Refresh:**
When access token expires (401 response), use refresh token to obtain new tokens via `/auth/refresh` endpoint.

## Error Handling

### HTTP Status Codes

| Code | Meaning | Description |
|------|---------|-------------|
| 200 | OK | Request successful |
| 201 | Created | Resource created successfully |
| 400 | Bad Request | Invalid request parameters |
| 401 | Unauthorized | Missing or invalid authentication |
| 403 | Forbidden | Insufficient permissions |
| 404 | Not Found | Resource not found |
| 500 | Internal Server Error | Server-side error |

### Error Response Format

```json
{
  "message": "Detailed error message",
  "status": 400
}
```

### Common Error Messages

**Authentication Errors:**
- "No token provided" - Missing Authorization header
- "Token has expired" - Access token expired (use refresh token)
- "Invalid token format" - Malformed JWT
- "Invalid token signature" - Token signature verification failed

**Authorization Errors:**
- "Admin access required" - Endpoint requires admin role
- "You don't have permission to access this resource" - User not owner or admin

**Validation Errors:**
- "Invalid email format"
- "Username must be at least 3 characters"
- "Required field missing: <field_name>"

## Public Endpoints

### Health Check

Check API health status.

**Endpoint:** `GET /health`

**Authentication:** None

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2026-02-11T12:34:56Z"
}
```

**Example:**
```bash
curl http://localhost:8080/health
```

---

### GitHub OAuth Callback

Handle GitHub OAuth callback and return JWT tokens.

**Endpoint:** `GET /auth/github/callback`

**Authentication:** None

**Query Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| code | string | Yes | GitHub authorization code |

**Response:**
```json
{
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "username": "johndoe",
  "email": "john@example.com"
}
```

**Example:**
```bash
curl "http://localhost:8080/auth/github/callback?code=abc123"
```

**Process:**
1. Exchange authorization code for GitHub access token
2. Fetch user profile from GitHub
3. Create or update user in database
4. Generate JWT access and refresh tokens
5. Return tokens and user info

---

### Token Refresh

Obtain new access and refresh tokens using a valid refresh token.

**Endpoint:** `POST /auth/refresh`

**Authentication:** None (uses refresh token in body)

**Request Body:**
```json
{
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

**Response:**
```json
{
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

**Errors:**
- `401 Unauthorized` - Refresh token expired, invalid, or wrong type
- `404 Not Found` - User associated with token not found

**Example:**
```bash
curl -X POST http://localhost:8080/auth/refresh \
  -H "Content-Type: application/json" \
  -d '{"refresh_token":"eyJhbGci..."}'
```

## Protected Endpoints

All protected endpoints require valid JWT access token in Authorization header.

### Users

#### Get All Users

**Endpoint:** `GET /api/users`

**Authentication:** Required (JWT)

**Authorization:** Any authenticated user

**Response:**
```json
{
  "users": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "username": "johndoe",
      "email": "john@example.com",
      "full_name": "John Doe",
      "role": "user",
      "created_at": "2026-01-01T00:00:00Z",
      "updated_at": "2026-02-01T00:00:00Z"
    }
  ],
  "total": 1
}
```

**Example:**
```bash
curl http://localhost:8080/api/users \
  -H "Authorization: Bearer <access_token>"
```

---

#### Get User by ID

**Endpoint:** `GET /api/users/{id}`

**Authentication:** Required (JWT)

**Authorization:** Any authenticated user

**Path Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| id | UUID | User ID |

**Response:**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "username": "johndoe",
  "email": "john@example.com",
  "full_name": "John Doe",
  "role": "user",
  "created_at": "2026-01-01T00:00:00Z",
  "updated_at": "2026-02-01T00:00:00Z"
}
```

**Errors:**
- `404 Not Found` - User not found

**Example:**
```bash
curl http://localhost:8080/api/users/550e8400-e29b-41d4-a716-446655440000 \
  -H "Authorization: Bearer <access_token>"
```

---

#### Create User

**Endpoint:** `POST /api/users`

**Authentication:** Required (JWT)

**Authorization:** Admin only

**Request Body:**
```json
{
  "username": "johndoe",
  "email": "john@example.com",
  "full_name": "John Doe"
}
```

**Validation:**
- `username`: 3-50 characters, alphanumeric and underscores
- `email`: Valid email format
- `full_name`: Optional, max 100 characters

**Response:**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "username": "johndoe",
  "email": "john@example.com",
  "full_name": "John Doe",
  "role": "user",
  "created_at": "2026-02-11T12:34:56Z",
  "updated_at": "2026-02-11T12:34:56Z"
}
```

**Errors:**
- `400 Bad Request` - Validation error
- `403 Forbidden` - Not admin
- `409 Conflict` - Username or email already exists

**Example:**
```bash
curl -X POST http://localhost:8080/api/users \
  -H "Authorization: Bearer <access_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "johndoe",
    "email": "john@example.com",
    "full_name": "John Doe"
  }'
```

---

#### Update User

**Endpoint:** `PUT /api/users/{id}`

**Authentication:** Required (JWT)

**Authorization:** Owner or Admin

**Path Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| id | UUID | User ID |

**Request Body:**
```json
{
  "username": "johndoe_updated",
  "email": "john.new@example.com",
  "full_name": "John Updated Doe",
  "role": "admin"
}
```

**Note:** All fields optional. Only provided fields will be updated. Role change requires admin privileges.

**Response:**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "username": "johndoe_updated",
  "email": "john.new@example.com",
  "full_name": "John Updated Doe",
  "role": "admin",
  "created_at": "2026-01-01T00:00:00Z",
  "updated_at": "2026-02-11T12:34:56Z"
}
```

**Errors:**
- `400 Bad Request` - Validation error
- `403 Forbidden` - Not owner or admin
- `404 Not Found` - User not found

**Example:**
```bash
curl -X PUT http://localhost:8080/api/users/550e8400-e29b-41d4-a716-446655440000 \
  -H "Authorization: Bearer <access_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "full_name": "John Updated Doe"
  }'
```

---

#### Delete User

**Endpoint:** `DELETE /api/users/{id}`

**Authentication:** Required (JWT)

**Authorization:** Admin only

**Path Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| id | UUID | User ID |

**Response:**
```
204 No Content
```

**Errors:**
- `403 Forbidden` - Not admin
- `404 Not Found` - User not found

**Example:**
```bash
curl -X DELETE http://localhost:8080/api/users/550e8400-e29b-41d4-a716-446655440000 \
  -H "Authorization: Bearer <access_token>"
```

---

### Quizzes

#### Get Quiz by ID

**Endpoint:** `GET /api/quizzes/{id}`

**Authentication:** Required (JWT)

**Authorization:** Any authenticated user

**Path Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| id | UUID | Quiz ID |

**Response:**
```json
{
  "id": "660e8400-e29b-41d4-a716-446655440000",
  "title": "JavaScript Basics",
  "description": "Test your JavaScript knowledge",
  "questions": [
    {
      "id": "q1",
      "question": "What is a closure?",
      "options": [
        "A function inside another function",
        "A loop construct",
        "A data type",
        "None of the above"
      ],
      "correct_answer": 0
    }
  ],
  "created_by": "550e8400-e29b-41d4-a716-446655440000",
  "created_at": "2026-01-15T00:00:00Z",
  "updated_at": "2026-02-01T00:00:00Z"
}
```

**Errors:**
- `404 Not Found` - Quiz not found

**Example:**
```bash
curl http://localhost:8080/api/quizzes/660e8400-e29b-41d4-a716-446655440000 \
  -H "Authorization: Bearer <access_token>"
```

## GraphQL Endpoint

### GraphQL API

**Endpoint:** `POST /graphql`

**Authentication:** Required (JWT)

**Content-Type:** `application/json`

**Request Format:**
```json
{
  "query": "query GetUser($id: ID!) { user(id: $id) { id username email } }",
  "variables": {
    "id": "550e8400-e29b-41d4-a716-446655440000"
  }
}
```

**Response Format:**
```json
{
  "data": {
    "user": {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "username": "johndoe",
      "email": "john@example.com"
    }
  }
}
```

**GraphQL Playground:**
- Available in development mode only
- URL: `http://localhost:8080/playground`
- Interactive GraphQL IDE for testing queries

**Example Query:**
```bash
curl -X POST http://localhost:8080/graphql \
  -H "Authorization: Bearer <access_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "{ users { id username email } }"
  }'
```

### GraphQL Schema

**Types:**

```graphql
type User {
  id: ID!
  username: String!
  email: String!
  fullName: String
  role: String!
  createdAt: String!
  updatedAt: String!
}

type Quiz {
  id: ID!
  title: String!
  description: String
  questions: [Question!]!
  createdBy: String!
  createdAt: String!
  updatedAt: String!
}

type Question {
  id: ID!
  question: String!
  options: [String!]!
  correctAnswer: Int!
}
```

**Queries:**

```graphql
type Query {
  user(id: ID!): User
  users: [User!]!
  quiz(id: ID!): Quiz
  quizzes: [Quiz!]!
}
```

**Mutations:**

```graphql
type Mutation {
  createUser(input: CreateUserInput!): User!
  updateUser(id: ID!, input: UpdateUserInput!): User!
  deleteUser(id: ID!): Boolean!
  
  createQuiz(input: CreateQuizInput!): Quiz!
  updateQuiz(id: ID!, input: UpdateQuizInput!): Quiz!
  deleteQuiz(id: ID!): Boolean!
}
```

## Rate Limiting

**Current Status:** Not implemented

**Planned Implementation:**
- Per-IP rate limiting
- Per-user rate limiting (after authentication)
- Different limits for different endpoint categories

## CORS Configuration

**Allowed Origins:**
- `http://localhost:5173` (Vite dev server)
- `http://localhost:3000` (Alternative dev port)

**Allowed Methods:**
- GET, POST, PUT, DELETE, OPTIONS

**Allowed Headers:**
- Authorization, Accept, Content-Type

**Exposed Headers:**
- Authorization

**Credentials:** Supported

## Testing Endpoints

### Using curl

**Public Endpoint:**
```bash
curl http://localhost:8080/health
```

**Protected Endpoint:**
```bash
# Get access token first via OAuth flow
TOKEN="your_access_token_here"

curl http://localhost:8080/api/users \
  -H "Authorization: Bearer $TOKEN"
```

**Token Refresh:**
```bash
REFRESH_TOKEN="your_refresh_token_here"

curl -X POST http://localhost:8080/auth/refresh \
  -H "Content-Type: application/json" \
  -d "{\"refresh_token\":\"$REFRESH_TOKEN\"}"
```

### Using Test Script

A test script is provided for testing token refresh:

```bash
# Location: components/api/tento-server/scripts/test_refresh_token.sh

# Test invalid tokens
./scripts/test_refresh_token.sh

# Test with valid refresh token
./scripts/test_refresh_token.sh YOUR_REFRESH_TOKEN
```

### Using GraphQL Playground

1. Start backend server: `cargo run`
2. Navigate to: `http://localhost:8080/playground`
3. Set Authorization header in HTTP Headers section:
```json
{
  "Authorization": "Bearer your_access_token_here"
}
```
4. Execute queries and mutations interactively

## API Client Libraries

### Frontend (TypeScript/JavaScript)

**Axios Client with Token Refresh:**
```typescript
import apiClient from './api/client';

// Automatically handles token refresh
const response = await apiClient.get('/api/users');
```

**GraphQL Client:**
```typescript
import { executeGraphQLQuery } from './api/graphql-client';

const data = await executeGraphQLQuery<UserData>(
  `query { users { id username email } }`
);
```

### React Query Hooks

**Users:**
```typescript
import { useUsers, useCreateUser, useUpdateUser, useDeleteUser } from './hooks/api/useUsers';

// Query
const { data: users, isLoading } = useUsers();

// Mutations
const createUser = useCreateUser();
const updateUser = useUpdateUser(userId);
const deleteUser = useDeleteUser();
```

**Quizzes:**
```typescript
import { useQuizzes, useQuiz, useCreateQuiz } from './hooks/api/useQuizzes';

// Query
const { data: quizzes } = useQuizzes();
const { data: quiz } = useQuiz(quizId);

// Mutation
const createQuiz = useCreateQuiz();
```

## Future Enhancements

**Planned Features:**
- Pagination support for list endpoints
- Filtering and sorting query parameters
- Batch operations
- Webhook support
- API versioning in URL path
- OpenAPI/Swagger documentation
- WebSocket support for real-time updates
- File upload endpoints
