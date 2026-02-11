# Tento - Deployment and Configuration Guide

## Table of Contents

- [Prerequisites](#prerequisites)
- [Environment Configuration](#environment-configuration)
- [Backend Setup](#backend-setup)
- [Frontend Setup](#frontend-setup)
- [Database Setup](#database-setup)
- [GitHub OAuth Setup](#github-oauth-setup)
- [Development Workflow](#development-workflow)
- [Production Deployment](#production-deployment)
- [Troubleshooting](#troubleshooting)

## Prerequisites

### Required Software

| Software | Minimum Version | Purpose |
|----------|----------------|---------|
| Rust | 1.70+ | Backend compilation |
| Node.js | 18.x+ | Frontend build |
| npm | 9.x+ | Package management |
| MongoDB | 6.0+ | Database |
| Git | 2.x+ | Version control |

### Optional Tools

- **cargo-watch**: Auto-reload during development
- **jq**: JSON formatting for testing
- **curl**: API testing

## Environment Configuration

### Backend Environment Variables

**Location:** `components/api/tento-server/.env.local`

```bash
# Server Configuration
WEB_SERVER_HOST=127.0.0.1
WEB_SERVER_PORT=8080

# Database Configuration
MONGODB_URI=mongodb://localhost:27017
MONGODB_DATABASE=tento

# JWT Configuration
JWT_SECRET=your-secret-key-here-change-in-production
JWT_EXPIRATION_HOURS=1
JWT_REFRESH_EXPIRATION_HOURS=168

# GitHub OAuth Configuration
GH_CLIENT_ID=your-github-client-id
GH_CLIENT_SECRET=your-github-client-secret

# Logging
RUST_LOG=info
RUST_ENV=development
```

**Security Notes:**
- Never commit `.env.local` to version control
- Use strong, random JWT_SECRET in production
- Rotate secrets regularly

### Frontend Environment Variables

**Location:** `components/ui/tento-web/.env`

```bash
# API Configuration
VITE_API_BASE_URL=http://localhost:8080

# GitHub OAuth Configuration
VITE_GH_CLIENT_ID=your-github-client-id
VITE_GH_REDIRECT_URI=http://localhost:5173/auth/callback
```

**Template:** `.env.example` contains placeholder values

## Backend Setup

### Step 1: Install Rust

**Using rustup (recommended):**
```bash
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
source $HOME/.cargo/env
```

**Verify installation:**
```bash
rustc --version
cargo --version
```

### Step 2: Clone Repository

```bash
git clone <repository-url>
cd tento-main/components/api/tento-server
```

### Step 3: Configure Environment

```bash
# Copy example and edit values
cp .env.local.example .env.local
nano .env.local
```

**Required changes:**
- Set `JWT_SECRET` to a random string
- Set `GH_CLIENT_ID` and `GH_CLIENT_SECRET` (see GitHub OAuth Setup)
- Configure `MONGODB_URI` if not using default

### Step 4: Build and Run

**Development mode:**
```bash
cargo run
```

**With auto-reload:**
```bash
cargo install cargo-watch
cargo watch -x run
```

**Production build:**
```bash
cargo build --release
./target/release/tento-server
```

### Step 5: Verify Backend

```bash
# Health check
curl http://localhost:8080/health

# Expected response:
# {"status":"healthy","timestamp":"..."}
```

## Frontend Setup

### Step 1: Install Node.js

**Using nvm (recommended):**
```bash
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.0/install.sh | bash
nvm install 18
nvm use 18
```

**Verify installation:**
```bash
node --version
npm --version
```

### Step 2: Navigate to Frontend

```bash
cd tento-main/components/ui/tento-web
```

### Step 3: Install Dependencies

```bash
npm install
```

**Dependencies installed:**
- react, react-dom
- react-router-dom
- @tanstack/react-query
- axios
- graphql-request, graphql
- TypeScript and build tools

### Step 4: Configure Environment

```bash
# Copy example and edit values
cp .env.example .env
nano .env
```

**Required changes:**
- Set `VITE_GH_CLIENT_ID` to your GitHub OAuth app client ID
- Set `VITE_API_BASE_URL` if backend not on localhost:8080

### Step 5: Run Development Server

```bash
npm run dev
```

**Output:**
```
  VITE v7.2.5  ready in 324 ms

  ➜  Local:   http://localhost:5173/
  ➜  Network: use --host to expose
  ➜  press h + enter to show help
```

### Step 6: Build for Production

```bash
npm run build
```

**Output:** `dist/` directory with optimized assets

**Preview production build:**
```bash
npm run preview
```

## Database Setup

### MongoDB Installation

**macOS (Homebrew):**
```bash
brew tap mongodb/brew
brew install mongodb-community@6.0
brew services start mongodb-community@6.0
```

**Ubuntu:**
```bash
wget -qO - https://www.mongodb.org/static/pgp/server-6.0.asc | sudo apt-key add -
echo "deb [ arch=amd64,arm64 ] https://repo.mongodb.org/apt/ubuntu focal/mongodb-org/6.0 multiverse" | sudo tee /etc/apt/sources.list.d/mongodb-org-6.0.list
sudo apt-get update
sudo apt-get install -y mongodb-org
sudo systemctl start mongod
```

**Docker:**
```bash
docker run -d \
  --name tento-mongodb \
  -p 27017:27017 \
  -v tento-data:/data/db \
  mongo:6.0
```

### Database Verification

```bash
# Connect to MongoDB
mongosh

# List databases
show dbs

# Switch to tento database
use tento

# List collections
show collections
```

### Database Schema

The backend automatically creates collections on first use:

**Collections:**
- `users` - User accounts
- `quizzes` - Quiz content
- `summary_documents` - Document summaries

**Indexes:**
Created automatically by the application:
- `users.username` (unique)
- `users.email` (unique)
- `users.github_id` (unique, sparse)

## GitHub OAuth Setup

### Step 1: Create OAuth App

1. Navigate to GitHub Settings: https://github.com/settings/developers
2. Click "OAuth Apps" > "New OAuth App"
3. Fill in application details:
   - **Application name**: Tento (Development)
   - **Homepage URL**: http://localhost:5173
   - **Authorization callback URL**: http://localhost:5173/auth/callback
4. Click "Register application"

### Step 2: Get Credentials

After creating the app:
- **Client ID**: Displayed on app settings page
- **Client Secret**: Click "Generate a new client secret"

### Step 3: Configure Applications

**Backend (.env.local):**
```bash
GH_CLIENT_ID=Iv23li3afZQidOsZm08j
GH_CLIENT_SECRET=<your-generated-secret>
```

**Frontend (.env):**
```bash
VITE_GH_CLIENT_ID=Iv23li3afZQidOsZm08j
VITE_GH_REDIRECT_URI=http://localhost:5173/auth/callback
```

### Step 4: Test OAuth Flow

1. Start backend and frontend
2. Navigate to http://localhost:5173
3. Click "Login with GitHub"
4. Authorize the application
5. You should be redirected to dashboard

## Development Workflow

### Starting Development Environment

**Terminal 1 - Database:**
```bash
# If using Docker
docker start tento-mongodb

# If using system MongoDB
brew services start mongodb-community@6.0
```

**Terminal 2 - Backend:**
```bash
cd components/api/tento-server
cargo run
# or with auto-reload:
cargo watch -x run
```

**Terminal 3 - Frontend:**
```bash
cd components/ui/tento-web
npm run dev
```

### Development URLs

| Service | URL | Purpose |
|---------|-----|---------|
| Frontend | http://localhost:5173 | React application |
| Backend API | http://localhost:8080 | REST/GraphQL API |
| GraphQL Playground | http://localhost:8080/playground | Interactive GraphQL IDE |
| Health Check | http://localhost:8080/health | API status |

### Testing Endpoints

**Backend health check:**
```bash
curl http://localhost:8080/health
```

**Token refresh test:**
```bash
cd components/api/tento-server
./scripts/test_refresh_token.sh
```

**API request with authentication:**
```bash
# Get token from OAuth flow first
TOKEN="your_access_token"

curl http://localhost:8080/api/users \
  -H "Authorization: Bearer $TOKEN"
```

### Code Quality Checks

**Backend:**
```bash
# Run tests
cargo test

# Format code
cargo fmt

# Lint code
cargo clippy
```

**Frontend:**
```bash
# Type check
npm run build  # Includes tsc -b

# Lint
npm run lint

# Format (if configured)
npm run format
```

## Production Deployment

### Backend Deployment

#### Option 1: Binary Deployment

**Build:**
```bash
cd components/api/tento-server
cargo build --release
```

**Deploy:**
```bash
# Copy binary to server
scp target/release/tento-server user@server:/opt/tento/

# Copy .env.local (with production values)
scp .env.local user@server:/opt/tento/

# Run on server
ssh user@server
cd /opt/tento
./tento-server
```

**Systemd service (Linux):**
```ini
# /etc/systemd/system/tento-server.service
[Unit]
Description=Tento API Server
After=network.target

[Service]
Type=simple
User=tento
WorkingDirectory=/opt/tento
ExecStart=/opt/tento/tento-server
Restart=always
Environment="RUST_LOG=info"
Environment="RUST_ENV=production"
EnvironmentFile=/opt/tento/.env.local

[Install]
WantedBy=multi-user.target
```

**Enable and start:**
```bash
sudo systemctl enable tento-server
sudo systemctl start tento-server
sudo systemctl status tento-server
```

#### Option 2: Docker Deployment

**Dockerfile:**
```dockerfile
# Build stage
FROM rust:1.70 as builder
WORKDIR /app
COPY . .
RUN cargo build --release

# Runtime stage
FROM debian:bullseye-slim
RUN apt-get update && apt-get install -y ca-certificates && rm -rf /var/lib/apt/lists/*
COPY --from=builder /app/target/release/tento-server /usr/local/bin/
EXPOSE 8080
CMD ["tento-server"]
```

**Build and run:**
```bash
docker build -t tento-server .
docker run -d \
  --name tento-api \
  -p 8080:8080 \
  -e MONGODB_URI=mongodb://mongo:27017 \
  -e JWT_SECRET=<production-secret> \
  -e GH_CLIENT_ID=<client-id> \
  -e GH_CLIENT_SECRET=<client-secret> \
  --link tento-mongodb:mongo \
  tento-server
```

### Frontend Deployment

#### Option 1: Static Hosting (Vercel, Netlify, etc.)

**Build:**
```bash
cd components/ui/tento-web
npm run build
```

**Deploy to Vercel:**
```bash
npm install -g vercel
vercel --prod
```

**Environment variables on Vercel:**
Set in project settings:
- `VITE_API_BASE_URL`
- `VITE_GH_CLIENT_ID`
- `VITE_GH_REDIRECT_URI`

#### Option 2: Nginx Static Files

**Build and copy:**
```bash
npm run build
scp -r dist/* user@server:/var/www/tento/
```

**Nginx configuration:**
```nginx
server {
    listen 80;
    server_name tento.example.com;
    root /var/www/tento;
    index index.html;

    # SPA routing
    location / {
        try_files $uri $uri/ /index.html;
    }

    # API proxy
    location /api {
        proxy_pass http://localhost:8080;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### Production Environment Variables

**Backend Production Values:**
```bash
WEB_SERVER_HOST=0.0.0.0
WEB_SERVER_PORT=8080
MONGODB_URI=mongodb://production-host:27017
JWT_SECRET=<strong-random-secret-64-chars>
JWT_EXPIRATION_HOURS=1
JWT_REFRESH_EXPIRATION_HOURS=168
GH_CLIENT_ID=<production-github-app-client-id>
GH_CLIENT_SECRET=<production-github-app-secret>
RUST_LOG=info
RUST_ENV=production
```

**Frontend Production Values:**
```bash
VITE_API_BASE_URL=https://api.tento.example.com
VITE_GH_CLIENT_ID=<production-github-app-client-id>
VITE_GH_REDIRECT_URI=https://tento.example.com/auth/callback
```

### Security Checklist

**Before deploying to production:**

- [ ] Change JWT_SECRET to strong random value
- [ ] Use HTTPS for all connections
- [ ] Configure CORS for production domains only
- [ ] Set secure MongoDB credentials
- [ ] Enable MongoDB authentication
- [ ] Configure firewall rules
- [ ] Set up SSL certificates (Let's Encrypt)
- [ ] Enable rate limiting
- [ ] Configure backup strategy
- [ ] Set up monitoring and alerts
- [ ] Review and minimize log verbosity
- [ ] Disable GraphQL Playground in production

### Monitoring

**Recommended Tools:**
- **Application logs**: systemd journal, Docker logs
- **Error tracking**: Sentry, Rollbar
- **Performance**: New Relic, DataDog
- **Uptime**: UptimeRobot, Pingdom
- **Database**: MongoDB Atlas monitoring

**Log locations:**
- Backend logs: journalctl -u tento-server -f
- Nginx logs: /var/log/nginx/access.log
- MongoDB logs: /var/log/mongodb/mongod.log

## Troubleshooting

### Backend Issues

**Problem: "JWT_SECRET not set"**
```
Error: Configuration validation failed: JWT_SECRET environment variable must be set
```
**Solution:** Set JWT_SECRET in `.env.local`

**Problem: "Failed to connect to MongoDB"**
```
Error: Failed to connect to MongoDB at mongodb://localhost:27017
```
**Solution:**
1. Check MongoDB is running: `brew services list`
2. Verify connection string in `.env.local`
3. Check firewall rules

**Problem: "Port 8080 already in use"**
```
Error: Address already in use (os error 48)
```
**Solution:**
1. Find process: `lsof -i :8080`
2. Kill process: `kill -9 <PID>`
3. Or change port in `.env.local`

### Frontend Issues

**Problem: "CORS error"**
```
Access to fetch at 'http://localhost:8080/api/users' from origin 'http://localhost:5173' has been blocked by CORS policy
```
**Solution:**
1. Ensure backend is running
2. Check CORS configuration in backend `main.rs`
3. Verify allowed origin includes `http://localhost:5173`

**Problem: "Module not found"**
```
Error: Cannot find module 'axios'
```
**Solution:**
```bash
rm -rf node_modules package-lock.json
npm install
```

**Problem: "TypeScript errors during build"**
```
error TS2345: Argument of type 'X' is not assignable to parameter of type 'Y'
```
**Solution:**
1. Check type definitions in `src/types/api.ts`
2. Verify import statements use `type` keyword for type-only imports
3. Run `npm run build` to see all errors

### GitHub OAuth Issues

**Problem: "Invalid client_id"**
**Solution:**
1. Verify `GH_CLIENT_ID` matches GitHub OAuth app
2. Check both backend and frontend have same client ID
3. Ensure no trailing spaces in environment variables

**Problem: "Redirect URI mismatch"**
**Solution:**
1. Go to GitHub OAuth app settings
2. Verify callback URL matches `VITE_GH_REDIRECT_URI`
3. Must be exact match including protocol and port

### Database Issues

**Problem: "Unique constraint violation"**
```
Error: E11000 duplicate key error collection: tento.users index: username_1
```
**Solution:** Username or email already exists, use different values

**Problem: "Connection timeout"**
**Solution:**
1. Check MongoDB is running
2. Verify network connectivity
3. Check firewall rules
4. Increase connection timeout in `MONGODB_URI`

### Token Refresh Issues

**Problem: "Token refresh fails silently"**
**Solution:**
1. Check browser console for errors
2. Verify refresh token exists in localStorage
3. Test `/auth/refresh` endpoint manually:
```bash
./scripts/test_refresh_token.sh <refresh_token>
```

**Problem: "Infinite redirect loop"**
**Solution:**
1. Clear localStorage
2. Verify token expiration times in backend config
3. Check AuthContext initialization logic

## Useful Commands

### Backend

```bash
# Run tests
cargo test

# Run with debug logging
RUST_LOG=debug cargo run

# Build optimized binary
cargo build --release

# Check for issues
cargo clippy

# Format code
cargo fmt
```

### Frontend

```bash
# Development server
npm run dev

# Production build
npm run build

# Preview build
npm run preview

# Type check
npx tsc --noEmit

# Lint
npm run lint
```

### Database

```bash
# Connect to MongoDB
mongosh

# Backup database
mongodump --db tento --out backup/

# Restore database
mongorestore --db tento backup/tento/

# Export collection
mongoexport --db tento --collection users --out users.json

# Import collection
mongoimport --db tento --collection users --file users.json
```

## Support

For issues and questions:
1. Check this documentation
2. Review error logs
3. Search existing GitHub issues
4. Create new issue with:
   - Environment details
   - Steps to reproduce
   - Error messages
   - Relevant logs
