# Tento - Frontend Architecture

## Table of Contents

- [Overview](#overview)
- [Technology Stack](#technology-stack)
- [Project Structure](#project-structure)
- [State Management](#state-management)
- [Data Fetching Strategy](#data-fetching-strategy)
- [Routing Architecture](#routing-architecture)
- [API Integration](#api-integration)
- [Type Safety](#type-safety)
- [Build and Development](#build-and-development)

## Overview

The Tento frontend is a modern React single-page application (SPA) built with TypeScript, featuring automatic token refresh, optimized data caching, and a component-based architecture.

### Design Principles

1. **Type Safety**: Full TypeScript coverage for compile-time error detection
2. **Separation of Concerns**: Clear boundaries between UI, business logic, and data layers
3. **Code Reusability**: Custom hooks and shared utilities
4. **Performance**: Optimized caching and code splitting
5. **Developer Experience**: Hot module replacement, TypeScript, and clear patterns

## Technology Stack

### Core Technologies

| Technology | Version | Purpose |
|------------|---------|---------|
| React | 19.x | UI library |
| TypeScript | 5.9.x | Type-safe JavaScript |
| Vite | 7.x (Rolldown) | Build tool and dev server |
| React Router | 6.x | Client-side routing |
| TanStack React Query | Latest | Server state management |
| Axios | Latest | HTTP client |
| graphql-request | Latest | GraphQL client |

### Development Tools

- ESLint: Code linting
- TypeScript Compiler: Type checking
- Vite HMR: Hot module replacement
- React DevTools: Component inspection
- React Query DevTools: Query debugging

## Project Structure

```
tento-web/
├── src/
│   ├── api/                      # API integration layer
│   │   ├── client.ts             # Axios instance with interceptors
│   │   ├── graphql-client.ts     # GraphQL client configuration
│   │   ├── auth.ts               # Authentication endpoints
│   │   ├── users.ts              # User API calls
│   │   └── quizzes.ts            # Quiz API calls
│   │
│   ├── contexts/                 # React contexts
│   │   └── AuthContext.tsx       # Authentication state management
│   │
│   ├── hooks/                    # Custom hooks
│   │   ├── useAuth.ts            # Authentication hook
│   │   └── api/                  # React Query hooks
│   │       ├── useUsers.ts       # User data hooks
│   │       └── useQuizzes.ts     # Quiz data hooks
│   │
│   ├── lib/                      # Third-party library configurations
│   │   └── queryClient.ts        # React Query configuration
│   │
│   ├── types/                    # TypeScript type definitions
│   │   └── api.ts                # API type definitions
│   │
│   ├── utils/                    # Utility functions
│   │   ├── constants.ts          # Application constants
│   │   └── storage.ts            # localStorage utilities
│   │
│   ├── App.tsx                   # Main application component
│   ├── main.tsx                  # Application entry point
│   └── index.css                 # Global styles
│
├── public/                       # Static assets
├── .env                          # Environment variables
├── .env.example                  # Environment template
├── package.json                  # Dependencies
├── tsconfig.json                 # TypeScript configuration
├── vite.config.ts                # Vite configuration
└── index.html                    # HTML entry point
```

## State Management

Tento uses a hybrid state management approach:

### 1. Server State (React Query)

**Purpose:** Manage data from backend API

**Features:**
- Automatic caching
- Background refetching
- Optimistic updates
- Automatic retry on failure

**Configuration:**
```typescript
// src/lib/queryClient.ts
export const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 1000 * 60 * 5,      // 5 minutes
      gcTime: 1000 * 60 * 10,         // 10 minutes
      retry: 1,                       // Retry once on failure
      refetchOnWindowFocus: false,
      refetchOnMount: false,
      refetchOnReconnect: false,
    },
    mutations: {
      retry: 1,
    },
  },
});
```

**Query Keys:**
```typescript
export const queryKeys = {
  users: ['users'],
  user: (id: string) => ['users', id],
  quizzes: ['quizzes'],
  quiz: (id: string) => ['quizzes', id],
  currentUser: ['auth', 'currentUser'],
};
```

### 2. Client State (React Context)

**Purpose:** Manage authentication state

**AuthContext:**
```typescript
interface AuthContextType {
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  login: (token: string, refreshToken: string, userData: Partial<User>) => void;
  logout: () => void;
}
```

**Features:**
- Initialize from localStorage on mount
- Persist user data across sessions
- Provide global authentication status
- Handle login/logout actions

### 3. Component State (useState/useReducer)

**Purpose:** Manage local component state

**Examples:**
- Form inputs
- UI toggles (modals, dropdowns)
- Temporary selections
- Loading states (component-level)

## Data Fetching Strategy

### React Query Hooks Pattern

**Query Hook Example:**
```typescript
// src/hooks/api/useUsers.ts
export function useUsers() {
  return useQuery({
    queryKey: queryKeys.users,
    queryFn: usersApi.getAllUsers,
  });
}

export function useUser(id: string) {
  return useQuery({
    queryKey: queryKeys.user(id),
    queryFn: () => usersApi.getUser(id),
    enabled: !!id,  // Only fetch if id exists
  });
}
```

**Mutation Hook Example:**
```typescript
export function useCreateUser() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: CreateUserRequest) => usersApi.createUser(data),
    onSuccess: () => {
      // Invalidate and refetch users list
      queryClient.invalidateQueries({ queryKey: queryKeys.users });
    },
  });
}
```

**Usage in Components:**
```typescript
function UsersList() {
  const { data: users, isLoading, error } = useUsers();
  const createUser = useCreateUser();

  if (isLoading) return <div>Loading...</div>;
  if (error) return <div>Error: {error.message}</div>;

  return (
    <div>
      {users?.map(user => (
        <UserCard key={user.id} user={user} />
      ))}
      <button onClick={() => createUser.mutate(newUserData)}>
        Add User
      </button>
    </div>
  );
}
```

### Caching Strategy

**Cache Levels:**

1. **Stale Time (5 minutes):**
   - Data considered fresh for 5 minutes
   - No refetch during this period
   - Immediate response from cache

2. **Garbage Collection (10 minutes):**
   - Unused data removed after 10 minutes
   - Keeps memory usage reasonable
   - Balances performance and freshness

3. **Cache Invalidation:**
   - Manual: `queryClient.invalidateQueries()`
   - Automatic: On mutations (create, update, delete)
   - Optimistic: Update cache before server response

**Cache Flow Diagram:**

```
Request Data
     │
     ├──► Cache Exists?
     │         │
     │         ├─ Yes ──► Is Stale?
     │         │              │
     │         │              ├─ No ──► Return from Cache
     │         │              │
     │         │              └─ Yes ──► Return Cache + Refetch in Background
     │         │
     │         └─ No ──► Fetch from Server ──► Update Cache
     │
     └──► Return Data
```

## Routing Architecture

### Route Structure

```
/                       # Home page (public)
/login                  # Login page (public)
/auth/callback          # OAuth callback handler (public)
/dashboard              # Dashboard (protected)
/users                  # Users list (protected)
/users/:id              # User detail (protected)
/quizzes                # Quizzes list (protected)
/quizzes/:id            # Quiz detail (protected)
/profile                # User profile (protected)
```

### Protected Routes Implementation

**ProtectedRoute Component:**
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
```

**Usage:**
```typescript
<Route
  path="/dashboard"
  element={
    <ProtectedRoute>
      <DashboardPage />
    </ProtectedRoute>
  }
/>
```

### OAuth Callback Flow

```typescript
function AuthCallbackPage() {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const { login } = useAuth();

  useEffect(() => {
    const code = searchParams.get('code');
    
    if (!code) {
      navigate('/login');
      return;
    }

    const authenticate = async () => {
      try {
        const response = await handleGithubCallback(code);
        login(response.token, response.refresh_token, {
          username: response.username,
          email: response.email,
        });
        navigate('/dashboard');
      } catch (error) {
        console.error('Authentication failed:', error);
        navigate('/login');
      }
    };

    authenticate();
  }, [searchParams, navigate, login]);

  return <div>Authenticating...</div>;
}
```

## API Integration

### Axios Client with Token Refresh

**Architecture:**

```
Component Request
       │
       ▼
   API Hook (React Query)
       │
       ▼
   API Function (users.ts, quizzes.ts)
       │
       ▼
   Axios Client
       │
       ├──► Request Interceptor: Add Bearer Token
       │
       ▼
   Backend API
       │
       ▼
   Response Interceptor
       │
       ├──► Status 401?
       │         │
       │         ├─ Yes ──► Refresh Token Flow
       │         │              │
       │         │              ├──► POST /auth/refresh
       │         │              │
       │         │              ├──► Store New Tokens
       │         │              │
       │         │              └──► Retry Original Request
       │         │
       │         └─ No ──► Return Response
       │
       ▼
   Component
```

**Request Interceptor:**
```typescript
apiClient.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    const token = storage.getAccessToken();
    
    if (token && config.headers) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    
    return config;
  },
  (error) => Promise.reject(error)
);
```

**Response Interceptor (401 Handling):**
```typescript
apiClient.interceptors.response.use(
  (response) => response,
  async (error: AxiosError) => {
    const originalRequest = error.config;

    if (error.response?.status !== 401 || originalRequest._retry) {
      return Promise.reject(error);
    }

    // Handle token refresh and retry
    originalRequest._retry = true;
    // ... refresh logic
  }
);
```

### GraphQL Client

**Configuration:**
```typescript
// src/api/graphql-client.ts
export const graphqlClient = new GraphQLClient(
  `${API_BASE_URL}/graphql`,
  {
    headers: {},
  }
);

// Request middleware to inject token
graphqlClient.requestConfig.requestMiddleware = async (request) => {
  const token = storage.getAccessToken();
  
  if (token) {
    return {
      ...request,
      headers: {
        ...request.headers,
        Authorization: `Bearer ${token}`,
      },
    };
  }
  
  return request;
};
```

**Usage:**
```typescript
import { executeGraphQLQuery } from './api/graphql-client';

const query = `
  query GetUsers {
    users {
      id
      username
      email
    }
  }
`;

const data = await executeGraphQLQuery<UsersData>(query);
```

## Type Safety

### API Type Definitions

**Location:** `src/types/api.ts`

**Categories:**

1. **Authentication Types:**
```typescript
export interface AuthResponse {
  token: string;
  refresh_token: string;
  username: string;
  email: string;
}
```

2. **User Types:**
```typescript
export interface User {
  id: string;
  username: string;
  email: string;
  full_name?: string;
  role: 'admin' | 'user';
  created_at: string;
  updated_at: string;
}
```

3. **Quiz Types:**
```typescript
export interface Quiz {
  id: string;
  title: string;
  description?: string;
  questions: QuizQuestion[];
  created_by: string;
  created_at: string;
  updated_at: string;
}
```

### Type-Safe API Calls

**API Function with Types:**
```typescript
export async function getUser(id: string): Promise<UserResponse> {
  const response = await apiClient.get<UserResponse>(`/api/users/${id}`);
  return response.data;
}
```

**React Query Hook with Types:**
```typescript
export function useUser(id: string) {
  return useQuery<UserResponse, Error>({
    queryKey: queryKeys.user(id),
    queryFn: () => usersApi.getUser(id),
  });
}
```

**Component Usage:**
```typescript
function UserProfile({ userId }: { userId: string }) {
  const { data: user, isLoading } = useUser(userId);
  
  // TypeScript knows 'user' is UserResponse | undefined
  // Full autocomplete and type checking
  
  return (
    <div>
      {user?.username}
      {user?.email}
    </div>
  );
}
```

## Build and Development

### Development Server

**Start Server:**
```bash
npm run dev
```

**Features:**
- Hot Module Replacement (HMR)
- Fast refresh for React components
- Instant TypeScript compilation
- Port: 5173 (default)

**Configuration (vite.config.ts):**
```typescript
export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    open: true,
  },
});
```

### Production Build

**Build Command:**
```bash
npm run build
```

**Process:**
1. TypeScript type checking (`tsc -b`)
2. Vite production build
3. Code minification
4. Asset optimization
5. Generate source maps

**Output:**
```
dist/
├── index.html
├── assets/
│   ├── index-[hash].js    # Main bundle
│   └── index-[hash].css   # Styles
└── ...
```

**Build Optimization:**
- Tree shaking (removes unused code)
- Code splitting (lazy loading)
- Asset compression (gzip)
- CSS minification

### Environment Variables

**Configuration:**
```bash
# .env
VITE_API_BASE_URL=http://localhost:8080
VITE_GH_CLIENT_ID=Iv23li3afZQidOsZm08j
VITE_GH_REDIRECT_URI=http://localhost:5173/auth/callback
```

**Access in Code:**
```typescript
const apiUrl = import.meta.env.VITE_API_BASE_URL;
const ghClientId = import.meta.env.VITE_GH_CLIENT_ID;
```

**Note:** Variables must be prefixed with `VITE_` to be exposed to client code.

### Code Linting

**Run ESLint:**
```bash
npm run lint
```

**Configuration:** `eslint.config.js`

**Rules:**
- React hooks rules
- TypeScript recommended rules
- Import order
- Unused variables

## Performance Optimization

### Code Splitting

**Route-Based Splitting:**
```typescript
import { lazy, Suspense } from 'react';

const DashboardPage = lazy(() => import('./pages/DashboardPage'));

<Route
  path="/dashboard"
  element={
    <Suspense fallback={<div>Loading...</div>}>
      <DashboardPage />
    </Suspense>
  }
/>
```

### React Query Optimizations

**Prefetching:**
```typescript
const queryClient = useQueryClient();

// Prefetch data before navigation
queryClient.prefetchQuery({
  queryKey: queryKeys.users,
  queryFn: usersApi.getAllUsers,
});
```

**Optimistic Updates:**
```typescript
const updateUser = useMutation({
  mutationFn: (data) => usersApi.updateUser(id, data),
  onMutate: async (newData) => {
    // Cancel outgoing refetches
    await queryClient.cancelQueries({ queryKey: queryKeys.user(id) });
    
    // Snapshot previous value
    const previousUser = queryClient.getQueryData(queryKeys.user(id));
    
    // Optimistically update cache
    queryClient.setQueryData(queryKeys.user(id), newData);
    
    return { previousUser };
  },
  onError: (err, newData, context) => {
    // Rollback on error
    queryClient.setQueryData(queryKeys.user(id), context?.previousUser);
  },
  onSettled: () => {
    // Always refetch after error or success
    queryClient.invalidateQueries({ queryKey: queryKeys.user(id) });
  },
});
```

### Bundle Size

**Current Build:**
- Main bundle: ~299 KB
- Gzipped: ~97 KB

**Optimization Strategies:**
- Use dynamic imports for large dependencies
- Remove unused dependencies
- Analyze bundle with `npm run build -- --analyze`

## Testing Strategy

**Recommended Setup:**

1. **Unit Tests:** Vitest
2. **Component Tests:** React Testing Library
3. **E2E Tests:** Playwright

**Example Test Structure:**
```
src/
├── components/
│   ├── UserCard.tsx
│   └── UserCard.test.tsx
├── hooks/
│   ├── useAuth.ts
│   └── useAuth.test.ts
└── utils/
    ├── storage.ts
    └── storage.test.ts
```

## Future Enhancements

**Planned Improvements:**

1. **Error Boundaries:** Graceful error handling
2. **Loading States:** Skeleton screens
3. **Offline Support:** Service workers, cache API
4. **Internationalization:** i18n support
5. **Accessibility:** ARIA labels, keyboard navigation
6. **Analytics:** User behavior tracking
7. **Performance Monitoring:** Web vitals tracking
8. **PWA Features:** Install prompt, offline mode
9. **Advanced Caching:** Background sync, cache strategies
10. **Component Library:** Shared UI components
