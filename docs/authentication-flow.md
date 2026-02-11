# Tento - Authentication Flow

## Table of Contents

- [Overview](#overview)
- [GitHub OAuth Flow](#github-oauth-flow)
- [Token Management](#token-management)
- [Token Refresh Flow](#token-refresh-flow)
- [Frontend Implementation](#frontend-implementation)
- [Backend Implementation](#backend-implementation)
- [Security Considerations](#security-considerations)

## Overview

Tento uses a hybrid authentication system combining:
- **GitHub OAuth 2.0** for user authentication
- **JWT (JSON Web Tokens)** for API authorization
- **Refresh Token** mechanism for seamless session management

### Authentication Strategy

```
┌──────────────────────────────────────────────────────────────┐
│                    Authentication Layers                     │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│  Layer 1: GitHub OAuth 2.0                                   │
│  ┌────────────────────────────────────────────────────────┐ │
│  │  - User proves identity to GitHub                      │ │
│  │  - Application receives authorization code             │ │
│  │  - Exchange code for GitHub access token               │ │
│  └────────────────────────────────────────────────────────┘ │
│                           ↓                                  │
│  Layer 2: User Provisioning                                  │
│  ┌────────────────────────────────────────────────────────┐ │
│  │  - Fetch user profile from GitHub                      │ │
│  │  - Create or update user in MongoDB                    │ │
│  │  - Assign roles and permissions                        │ │
│  └────────────────────────────────────────────────────────┘ │
│                           ↓                                  │
│  Layer 3: JWT Token Generation                               │
│  ┌────────────────────────────────────────────────────────┐ │
│  │  - Generate access token (1 hour expiry)               │ │
│  │  - Generate refresh token (7 day expiry)               │ │
│  │  - Return tokens to frontend                           │ │
│  └────────────────────────────────────────────────────────┘ │
│                           ↓                                  │
│  Layer 4: Session Management                                 │
│  ┌────────────────────────────────────────────────────────┐ │
│  │  - Frontend stores tokens in localStorage              │ │
│  │  - Automatic token refresh on expiration               │ │
│  │  - Stateless authentication via JWT validation         │ │
│  └────────────────────────────────────────────────────────┘ │
│                                                              │
└──────────────────────────────────────────────────────────────┘
```

## GitHub OAuth Flow

### Step-by-Step Process

#### Step 1: Initiate Login

**Frontend Action:**
```typescript
// User clicks "Login with GitHub" button
const handleLogin = () => {
  const githubAuthUrl = `https://github.com/login/oauth/authorize?client_id=${GH_CLIENT_ID}&scope=read:user user:email`;
  window.location.href = githubAuthUrl;
};
```

**User Interaction:**
- User is redirected to GitHub
- GitHub displays authorization screen
- User authorizes the application

#### Step 2: GitHub Callback

**GitHub Action:**
```
Redirect to: http://localhost:5173/auth/callback?code=AUTHORIZATION_CODE
```

**Frontend Action:**
```typescript
// AuthCallbackPage component extracts code
const code = searchParams.get('code');

// Call backend OAuth endpoint
const response = await handleGithubCallback(code);
```

#### Step 3: Backend Token Exchange

**Backend Process (src/handlers/auth_handler.rs):**

```rust
#[get("/auth/github/callback")]
pub async fn auth_github_callback(
    state: web::Data<AppState>,
    web::Query(params): web::Query<CallbackParams>,
) -> Result<HttpResponse, AppError> {
    // 1. Exchange authorization code for GitHub access token
    let oauth = oauth_client
        .post::<_, serde_json::Value>(
            "/login/oauth/access_token",
            Some(&serde_json::json!({
                "code": params.code,
                "client_id": client_id,
                "client_secret": client_secret,
            })),
        )
        .await?;
    
    // 2. Use GitHub access token to fetch user profile
    let gh_user = client.current().user().await?;
    
    // 3. Create or update user in database
    let user = User::from_github(
        github_id,
        username,
        email,
        name,
    );
    let saved_user = state.user_service.upsert_oauth_user(user).await?;
    
    // 4. Generate JWT tokens
    let token = state.jwt_service.create_token(&saved_user)?;
    let refresh_token_str = state.jwt_service.create_refresh_token(&saved_user.username)?;
    
    // 5. Return tokens to frontend
    Ok(HttpResponse::Ok().json(AuthResponse {
        token,
        refresh_token: refresh_token_str,
        username: saved_user.username,
        email: saved_user.email,
    }))
}
```

#### Step 4: Frontend Token Storage

**Frontend Action:**
```typescript
// Store tokens in localStorage
login(response.token, response.refresh_token, {
  username: response.username,
  email: response.email,
});

// Navigate to dashboard
navigate('/dashboard');
```

### Sequence Diagram

```
User          Frontend       Backend       GitHub        MongoDB
 │                │              │             │             │
 │  Click Login   │              │             │             │
 ├───────────────►│              │             │             │
 │                │              │             │             │
 │                │  Redirect to GitHub OAuth  │             │
 │                ├─────────────────────────────►            │
 │                │              │             │             │
 │  Authorize App │              │             │             │
 ├────────────────────────────────────────────►│             │
 │                │              │             │             │
 │  Callback      │              │             │             │
 │  (with code)   │              │             │             │
 ◄────────────────┤              │             │             │
 │                │              │             │             │
 │                │  POST /auth/github/callback              │
 │                │  ?code=XXX   │             │             │
 │                ├─────────────►│             │             │
 │                │              │             │             │
 │                │              │  Exchange   │             │
 │                │              │  code for   │             │
 │                │              │  token      │             │
 │                │              ├────────────►│             │
 │                │              │             │             │
 │                │              │  GitHub     │             │
 │                │              │  Access     │             │
 │                │              │  Token      │             │
 │                │              ◄─────────────┤             │
 │                │              │             │             │
 │                │              │  Fetch User │             │
 │                │              │  Profile    │             │
 │                │              ├────────────►│             │
 │                │              ◄─────────────┤             │
 │                │              │             │             │
 │                │              │  Upsert User│             │
 │                │              ├────────────────────────────►
 │                │              │             │             │
 │                │              │  User Data  │             │
 │                │              ◄─────────────────────────────┤
 │                │              │             │             │
 │                │              │  Generate   │             │
 │                │              │  JWT Tokens │             │
 │                │              │             │             │
 │                │  Response:   │             │             │
 │                │  {           │             │             │
 │                │    token,    │             │             │
 │                │    refresh,  │             │             │
 │                │    username, │             │             │
 │                │    email     │             │             │
 │                │  }           │             │             │
 │                ◄──────────────┤             │             │
 │                │              │             │             │
 │                │  Store in    │             │             │
 │                │  localStorage│             │             │
 │                │              │             │             │
 │  Navigate to   │              │             │             │
 │  Dashboard     │              │             │             │
 ◄────────────────┤              │             │             │
 │                │              │             │             │
```

## Token Management

### Token Types and Purposes

#### Access Token

**Purpose:** Authenticate API requests

**Configuration:**
- **Expiry:** 1 hour
- **Storage:** localStorage (`tento_access_token`)
- **Usage:** Sent in `Authorization: Bearer <token>` header
- **Validation:** Every protected API request

**JWT Claims:**
```rust
{
    "sub": "username",           // Subject (user identifier)
    "id": "uuid",                // User UUID
    "role": "user|admin",        // Authorization role
    "exp": 1234567890,           // Expiration timestamp (1 hour)
    "iat": 1234567890            // Issued at timestamp
}
```

**Backend Generation (src/auth/jwt.rs):**
```rust
pub fn create_token(&self, user: &User) -> Result<String, AppError> {
    let expiration = Utc::now()
        .checked_add_signed(chrono::Duration::hours(self.config.jwt_expiration_hours))
        .expect("Invalid timestamp")
        .timestamp();

    let claims = Claims {
        sub: user.username.clone(),
        id: user.id.to_string(),
        role: user.role.clone(),
        exp: expiration as usize,
        iat: Utc::now().timestamp() as usize,
    };

    encode(
        &Header::default(),
        &claims,
        &EncodingKey::from_secret(self.config.jwt_secret.expose_secret().as_bytes()),
    )
    .map_err(|e| AppError::InternalError(format!("JWT encoding error: {}", e)))
}
```

#### Refresh Token

**Purpose:** Obtain new access tokens without re-authentication

**Configuration:**
- **Expiry:** 7 days (168 hours)
- **Storage:** localStorage (`tento_refresh_token`)
- **Usage:** Sent to `/auth/refresh` endpoint when access token expires
- **Validation:** Only on token refresh requests

**JWT Claims:**
```rust
{
    "sub": "username",           // Subject (user identifier)
    "token_type": "refresh",     // Token type discriminator
    "exp": 1234567890,           // Expiration timestamp (7 days)
    "iat": 1234567890            // Issued at timestamp
}
```

**Backend Generation (src/auth/jwt.rs):**
```rust
pub fn create_refresh_token(&self, username: &str) -> Result<String, AppError> {
    let expiration = Utc::now()
        .checked_add_signed(chrono::Duration::hours(self.config.jwt_refresh_expiration_hours))
        .expect("Invalid timestamp")
        .timestamp();

    let claims = RefreshClaims {
        sub: username.to_string(),
        token_type: "refresh".to_string(),
        exp: expiration as usize,
        iat: Utc::now().timestamp() as usize,
    };

    encode(
        &Header::default(),
        &claims,
        &EncodingKey::from_secret(self.config.jwt_secret.expose_secret().as_bytes()),
    )
    .map_err(|e| AppError::InternalError(format!("JWT encoding error: {}", e)))
}
```

### Token Validation

**Access Token Validation:**

```rust
pub fn validate_token(&self, token: &str) -> Result<Claims, AppError> {
    let token_data = decode::<Claims>(
        token,
        &DecodingKey::from_secret(self.config.jwt_secret.expose_secret().as_bytes()),
        &Validation::default(),
    )
    .map_err(|e| match e.kind() {
        ErrorKind::ExpiredSignature => {
            AppError::Unauthorized("Token has expired".to_string())
        }
        ErrorKind::InvalidToken => {
            AppError::Unauthorized("Invalid token format".to_string())
        }
        ErrorKind::InvalidSignature => {
            AppError::Unauthorized("Invalid token signature".to_string())
        }
        _ => AppError::Unauthorized(format!("Token validation failed: {}", e)),
    })?;

    Ok(token_data.claims)
}
```

**Refresh Token Validation:**

```rust
pub fn validate_refresh_token(&self, token: &str) -> Result<RefreshClaims, AppError> {
    let token_data = decode::<RefreshClaims>(
        token,
        &DecodingKey::from_secret(self.config.jwt_secret.expose_secret().as_bytes()),
        &Validation::default(),
    )
    .map_err(|e| match e.kind() {
        ErrorKind::ExpiredSignature => {
            AppError::Unauthorized("Refresh token has expired. Please log in again.".to_string())
        }
        ErrorKind::InvalidToken => {
            AppError::Unauthorized("Invalid refresh token format".to_string())
        }
        ErrorKind::InvalidSignature => {
            AppError::Unauthorized("Invalid refresh token signature".to_string())
        }
        _ => AppError::Unauthorized(format!("Refresh token validation failed: {}", e)),
    })?;

    // Validate token type
    if token_data.claims.token_type != "refresh" {
        return Err(AppError::Unauthorized(
            "Invalid token type - expected refresh token".to_string(),
        ));
    }

    Ok(token_data.claims)
}
```

## Token Refresh Flow

### Automatic Token Refresh

The frontend automatically handles token refresh when an API request fails with a 401 status.

### Flow Diagram

```
API Request
    │
    ├──► Access Token Valid?
    │         │
    │         ├─ Yes ──► Continue Request ──► Return Response
    │         │
    │         └─ No ──► 401 Unauthorized
    │                        │
    │                        ├──► Refresh Token Valid?
    │                        │         │
    │                        │         ├─ Yes ──► POST /auth/refresh
    │                        │         │              │
    │                        │         │              ├──► New Tokens
    │                        │         │              │
    │                        │         │              ├──► Store Tokens
    │                        │         │              │
    │                        │         │              └──► Retry Original Request
    │                        │         │
    │                        │         └─ No ──► Redirect to Login
    │                        │
    │                        └──► Multiple Concurrent Requests?
    │                                  │
    │                                  ├─ Yes ──► Queue Requests
    │                                  │              │
    │                                  │              └──► Retry All After Refresh
    │                                  │
    │                                  └─ No ──► Single Refresh Flow
```

### Frontend Implementation

**Axios Interceptor (src/api/client.ts):**

```typescript
apiClient.interceptors.response.use(
  (response) => response,
  async (error: AxiosError) => {
    const originalRequest = error.config;

    // If not 401 or already retried, reject
    if (error.response?.status !== 401 || originalRequest._retry) {
      return Promise.reject(error);
    }

    // If already refreshing, queue this request
    if (isRefreshing) {
      return new Promise((resolve) => {
        subscribeTokenRefresh((token: string) => {
          originalRequest.headers.Authorization = `Bearer ${token}`;
          resolve(apiClient(originalRequest));
        });
      });
    }

    originalRequest._retry = true;
    isRefreshing = true;

    const refreshToken = storage.getRefreshToken();

    if (!refreshToken) {
      isRefreshing = false;
      storage.clear();
      window.location.href = '/login';
      return Promise.reject(error);
    }

    try {
      // Call refresh endpoint
      const response = await axios.post(
        `${API_BASE_URL}/auth/refresh`,
        { refresh_token: refreshToken }
      );

      const { token: newAccessToken, refresh_token: newRefreshToken } = response.data;

      // Store new tokens
      storage.setTokens(newAccessToken, newRefreshToken);

      // Update authorization header
      originalRequest.headers.Authorization = `Bearer ${newAccessToken}`;

      // Notify all waiting requests
      onTokenRefreshed(newAccessToken);
      isRefreshing = false;

      // Retry original request
      return apiClient(originalRequest);
    } catch (refreshError) {
      // Refresh failed - clear tokens and redirect to login
      isRefreshing = false;
      storage.clear();
      window.location.href = '/login';
      return Promise.reject(refreshError);
    }
  }
);
```

### Backend Refresh Endpoint

**Handler (src/handlers/auth_handler.rs):**

```rust
#[post("/auth/refresh")]
pub async fn refresh_token(
    state: web::Data<AppState>,
    request: web::Json<RefreshTokenRequest>,
) -> Result<HttpResponse, AppError> {
    // 1. Validate refresh token with detailed error messages
    let refresh_claims = state
        .jwt_service
        .validate_refresh_token(&request.refresh_token)?;
    
    // 2. Get full user object from database
    let user = state
        .user_service
        .get_user_for_token(&refresh_claims.sub)
        .await
        .map_err(|_| AppError::Unauthorized("User associated with refresh token not found".to_string()))?;
    
    // 3. Generate new tokens
    let new_token = state.jwt_service.create_token(&user)?;
    let new_refresh_token = state.jwt_service.create_refresh_token(&refresh_claims.sub)?;
    
    log::info!("Token refreshed successfully for user: {}", refresh_claims.sub);
    
    // 4. Return new tokens
    Ok(HttpResponse::Ok().json(RefreshTokenResponse {
        token: new_token,
        refresh_token: new_refresh_token,
    }))
}
```

## Frontend Implementation

### AuthContext Provider

**Location:** `src/contexts/AuthContext.tsx`

**Purpose:** Manage global authentication state

**Features:**
- Initialize auth state from localStorage on mount
- Provide login/logout functions
- Expose authentication status
- Store user data

**Implementation:**
```typescript
export function AuthProvider({ children }: AuthProviderProps) {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  // Initialize from localStorage
  useEffect(() => {
    const token = storage.getAccessToken();
    const storedUser = storage.getUser<User>();

    if (token && storedUser) {
      setUser(storedUser);
    }

    setIsLoading(false);
  }, []);

  const login = (token: string, refreshToken: string, userData: Partial<User>) => {
    storage.setTokens(token, refreshToken);
    storage.setUser(userData);
    setUser(userData as User);
  };

  const logout = () => {
    storage.clear();
    setUser(null);
  };

  return (
    <AuthContext.Provider value={{ user, isAuthenticated: !!user, isLoading, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
}
```

### Protected Routes

**Location:** `src/App.tsx`

**Implementation:**
```typescript
function ProtectedRoute({ children }: ProtectedRouteProps) {
  const { isAuthenticated, isLoading } = useAuth();

  if (isLoading) {
    return <div>Loading...</div>;
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  return <>{children}</>;
}

// Usage
<Route
  path="/dashboard"
  element={
    <ProtectedRoute>
      <DashboardPage />
    </ProtectedRoute>
  }
/>
```

## Backend Implementation

### Authentication Middleware

**Location:** `src/auth/middleware.rs`

**Purpose:** Validate JWT tokens on protected routes

**Implementation:**
```rust
impl<S, B> Transform<S, ServiceRequest> for AuthMiddleware
where
    S: Service<ServiceRequest, Response = ServiceResponse<B>, Error = Error>,
    S::Future: 'static,
    B: 'static,
{
    type Response = ServiceResponse<B>;
    type Error = Error;
    type Transform = AuthMiddlewareService<S>;
    type InitError = ();
    type Future = Ready<Result<Self::Transform, Self::InitError>>;

    fn new_transform(&self, service: S) -> Self::Future {
        ready(Ok(AuthMiddlewareService { service }))
    }
}

pub struct AuthMiddlewareService<S> {
    service: S,
}

impl<S, B> Service<ServiceRequest> for AuthMiddlewareService<S>
where
    S: Service<ServiceRequest, Response = ServiceResponse<B>, Error = Error>,
    S::Future: 'static,
    B: 'static,
{
    type Response = ServiceResponse<B>;
    type Error = Error;
    type Future = LocalBoxFuture<'static, Result<Self::Response, Self::Error>>;

    fn call(&self, req: ServiceRequest) -> Self::Future {
        // Extract JWT service from request
        let jwt_service = req
            .app_data::<web::Data<Arc<JwtService>>>()
            .expect("JwtService not found");

        // Extract token from Authorization header
        let token = req
            .headers()
            .get("Authorization")
            .and_then(|h| h.to_str().ok())
            .and_then(|h| h.strip_prefix("Bearer "));

        let token = match token {
            Some(t) => t.to_string(),
            None => {
                return Box::pin(async move {
                    Err(AppError::Unauthorized("No token provided".to_string()).into())
                });
            }
        };

        // Validate token
        let claims = match jwt_service.validate_token(&token) {
            Ok(c) => c,
            Err(e) => {
                return Box::pin(async move { Err(e.into()) });
            }
        };

        // Insert claims into request extensions
        req.extensions_mut().insert(claims);

        // Continue to next middleware
        let fut = self.service.call(req);
        Box::pin(async move { fut.await })
    }
}
```

### Authorization Utilities

**Location:** `src/auth/utils.rs`

**Admin-Only Access:**
```rust
pub fn require_admin(claims: &Claims) -> Result<(), AppError> {
    if claims.role != "admin" {
        return Err(AppError::Forbidden(
            "Admin access required".to_string(),
        ));
    }
    Ok(())
}
```

**Owner or Admin Access:**
```rust
pub fn require_owner_or_admin(
    claims: &Claims,
    resource_owner_id: &str,
) -> Result<(), AppError> {
    if claims.id != resource_owner_id && claims.role != "admin" {
        return Err(AppError::Forbidden(
            "You don't have permission to access this resource".to_string(),
        ));
    }
    Ok(())
}
```

## Security Considerations

### Token Security

**Storage:**
- Tokens stored in localStorage (XSS vulnerable but acceptable for MVP)
- Consider httpOnly cookies for production (prevents XSS attacks)

**Transmission:**
- Tokens sent in Authorization header (not in URL)
- HTTPS required for production

**Expiration:**
- Short-lived access tokens (1 hour) limit exposure
- Refresh tokens provide user convenience
- Both tokens use absolute expiration (not sliding)

### CORS Configuration

**Development Setup:**
```rust
.wrap(
    Cors::default()
        .allowed_origin("http://localhost:5173")
        .allowed_origin("http://localhost:3000")
        .allowed_methods(vec!["GET", "POST", "PUT", "DELETE", "OPTIONS"])
        .allowed_headers(vec![
            http::header::AUTHORIZATION,
            http::header::ACCEPT,
            http::header::CONTENT_TYPE,
        ])
        .expose_headers(vec![http::header::AUTHORIZATION])
        .max_age(3600)
        .supports_credentials()
)
```

**Production Considerations:**
- Replace hardcoded origins with environment variable
- Validate origin against whitelist
- Consider subdomain support

### Password Security

**Current Implementation:**
- OAuth-only authentication (no passwords)
- GitHub handles password security

**Future Considerations:**
- If adding password authentication:
  - Use bcrypt or argon2 for hashing
  - Enforce minimum password strength
  - Implement rate limiting on login attempts

### Session Management

**Current Approach:**
- Stateless JWT validation (no server-side sessions)
- Tokens cannot be revoked before expiration

**Production Enhancements:**
- Token blacklist for logout
- Redis-based session tracking
- Device/location tracking
- Suspicious activity detection

### API Rate Limiting

**Current Status:** Not implemented

**Recommended Implementation:**
- Rate limit by IP address
- Rate limit by user (after authentication)
- Separate limits for authentication vs. API endpoints
- Consider using actix-limitation crate

### Environment Variables

**Sensitive Configuration:**
```bash
# Backend (.env.local)
JWT_SECRET=<random-secret-key>
GH_CLIENT_SECRET=<github-oauth-secret>
MONGODB_URI=<database-connection-string>

# Frontend (.env)
VITE_GH_CLIENT_ID=<github-oauth-client-id>
```

**Security Best Practices:**
- Never commit .env files to version control
- Use different secrets for each environment
- Rotate secrets regularly
- Use secret management service in production (AWS Secrets Manager, etc.)
