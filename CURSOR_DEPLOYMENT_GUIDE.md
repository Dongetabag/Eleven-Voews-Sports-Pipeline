# 🚀 AI Gold Mine System - Cursor Deployment Guide
## Vercel + Railway Production Deployment

> **Target**: Deploy full-stack AI arbitrage platform to Vercel (frontend/API routes) + Railway (Python backend, databases)
> 
> **Cursor Agent Mode**: Full access enabled with Vercel CLI, GitHub integration, and all MCP tools

---

## 📋 Architecture Overview

### Current Stack
- **Frontend**: Next.js 14 (React 18, TypeScript, Tailwind)
- **Python API**: FastAPI + Uvicorn (AI engine, scraping, automation)
- **NestJS API**: TypeScript microservices (optional secondary backend)
- **Databases**: PostgreSQL, Redis, MongoDB
- **AI Models**: Google Gemini 2.5 Flash (primary), OpenAI/Anthropic (fallback)

### Deployment Strategy
```
┌─────────────────────────────────────────┐
│ VERCEL (Edge Network)                   │
│ ├── Next.js Frontend (Static + SSR)    │
│ ├── API Routes (/api/*)                │
│ └── Serverless Functions               │
└─────────────────────────────────────────┘
              ↓ HTTPS
┌─────────────────────────────────────────┐
│ RAILWAY (Container Platform)            │
│ ├── Python FastAPI (Main Backend)      │
│ ├── PostgreSQL Database                │
│ ├── Redis Cache                        │
│ ├── MongoDB (Opportunities DB)         │
│ └── Celery Workers (Background Tasks)  │
└─────────────────────────────────────────┘
```

---

## 🛠️ MCP Tools Available to Cursor

### Vercel Tools (Priority)
```typescript
// Essential Vercel operations
vercel:deploy_to_vercel              // Deploy current project
vercel:search_vercel_documentation   // Search Vercel docs
vercel:list_projects                 // List all projects
vercel:get_project                   // Get project details
vercel:list_deployments              // Check deployment status
vercel:get_deployment                // Get deployment info
vercel:get_deployment_build_logs     // Debug build failures
vercel:list_teams                    // List teams/orgs
vercel:check_domain_availability_and_price  // Domain management
```

### GitHub Tools (Code Management)
```typescript
// Repository operations
github:create_repository             // Create new repo if needed
github:create_branch                 // Create deployment branch
github:create_or_update_file         // Update single file
github:push_files                    // Push multiple files at once
github:get_file_contents            // Read current files
github:list_commits                  // Check commit history
github:create_pull_request          // Create PR for changes
```

### File Operations (Local Development)
```bash
bash_tool                            # Execute shell commands
str_replace                          # Replace code in files
create_file                          # Create new files
view                                 # View file contents
```

### Documentation & Search
```bash
web_search                           # Search for solutions
web_fetch                            # Fetch documentation
```

---

## 🎯 PHASE 1: Project Analysis & Preparation

### Step 1: Analyze Current Structure
```bash
# Use Cursor's bash_tool to run these commands:

# Check project structure
cd /path/to/ai-arbitrage-system
tree -L 2 -I 'node_modules|__pycache__|.next|dist'

# Identify all configuration files
find . -name "*.json" -o -name "*.yaml" -o -name "*.yml" -o -name ".env*" | head -20

# Check for existing Vercel/Railway configs
ls -la vercel.json railway.json Procfile nixpacks.toml 2>/dev/null
```

### Step 2: Verify Dependencies
```bash
# Check package.json files
cat frontend/package.json | jq '.dependencies'
cat backend-nestjs/package.json | jq '.dependencies'

# Check Python requirements
cat requirements.txt
cat requirements-railway.txt
```

### Step 3: Search Vercel Documentation
Use MCP tool: `Vercel:search_vercel_documentation`

**Key Topics to Search:**
- "Next.js deployment environment variables"
- "API routes proxy configuration"
- "CORS configuration"
- "serverless function timeout"
- "build output API"
- "monorepo deployment"

---

## 🔧 PHASE 2: Code Fixes & Configuration

### A. Frontend (Next.js) - Vercel Optimization

#### 1. Update `frontend/next.config.js`
Use `str_replace` or `create_file`:

```javascript
/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  swcMinify: true,
  
  // Environment variables
  env: {
    NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL || 'https://your-railway-api.railway.app',
    NEXT_PUBLIC_WS_URL: process.env.NEXT_PUBLIC_WS_URL || 'wss://your-railway-api.railway.app',
  },
  
  // API proxy for development
  async rewrites() {
    return [
      {
        source: '/api/v1/:path*',
        destination: `${process.env.NEXT_PUBLIC_API_URL}/api/v1/:path*`,
      },
    ];
  },
  
  // Headers for CORS
  async headers() {
    return [
      {
        source: '/api/:path*',
        headers: [
          { key: 'Access-Control-Allow-Credentials', value: 'true' },
          { key: 'Access-Control-Allow-Origin', value: '*' },
          { key: 'Access-Control-Allow-Methods', value: 'GET,DELETE,PATCH,POST,PUT' },
          { key: 'Access-Control-Allow-Headers', value: 'X-CSRF-Token, X-Requested-With, Accept, Accept-Version, Content-Length, Content-MD5, Content-Type, Date, X-Api-Version' },
        ],
      },
    ];
  },
  
  // Optimize images
  images: {
    domains: ['localhost', 'railway.app', 'vercel.app'],
    formats: ['image/avif', 'image/webp'],
  },
  
  // Output for standalone deployment
  output: 'standalone',
  
  // Disable TypeScript/ESLint errors blocking build
  typescript: {
    ignoreBuildErrors: process.env.VERCEL_ENV === 'production',
  },
  eslint: {
    ignoreDuringBuilds: process.env.VERCEL_ENV === 'production',
  },
};

module.exports = nextConfig;
```

#### 2. Create `frontend/vercel.json`
```json
{
  "version": 2,
  "buildCommand": "npm run build",
  "outputDirectory": ".next",
  "framework": "nextjs",
  "installCommand": "npm install",
  "devCommand": "npm run dev",
  "env": {
    "NEXT_PUBLIC_API_URL": "https://your-railway-api.railway.app",
    "NEXT_PUBLIC_WS_URL": "wss://your-railway-api.railway.app"
  },
  "build": {
    "env": {
      "NEXT_TELEMETRY_DISABLED": "1"
    }
  },
  "functions": {
    "pages/api/**/*.ts": {
      "maxDuration": 60
    }
  },
  "headers": [
    {
      "source": "/api/(.*)",
      "headers": [
        {
          "key": "Access-Control-Allow-Credentials",
          "value": "true"
        },
        {
          "key": "Access-Control-Allow-Origin",
          "value": "*"
        },
        {
          "key": "Access-Control-Allow-Methods",
          "value": "GET,OPTIONS,PATCH,DELETE,POST,PUT"
        },
        {
          "key": "Access-Control-Allow-Headers",
          "value": "X-CSRF-Token, X-Requested-With, Accept, Accept-Version, Content-Length, Content-MD5, Content-Type, Date, X-Api-Version, Authorization"
        }
      ]
    }
  ]
}
```

#### 3. Update API Client Configuration
Create/update `frontend/src/lib/api-client.ts`:

```typescript
import axios, { AxiosInstance } from 'axios';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

// Create axios instance with defaults
const apiClient: AxiosInstance = axios.create({
  baseURL: API_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
  withCredentials: false, // Set to true if using cookies
});

// Request interceptor for auth tokens
apiClient.interceptors.request.use(
  (config) => {
    // Add auth token if exists
    const token = localStorage.getItem('auth_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Response interceptor for error handling
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Handle unauthorized
      localStorage.removeItem('auth_token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

export default apiClient;
```

#### 4. Update Environment Variables Reference
Create `frontend/.env.example`:

```bash
# API Configuration
NEXT_PUBLIC_API_URL=https://your-railway-api.railway.app
NEXT_PUBLIC_WS_URL=wss://your-railway-api.railway.app

# Optional: Analytics
NEXT_PUBLIC_GOOGLE_ANALYTICS=
NEXT_PUBLIC_SENTRY_DSN=

# Build Configuration
NEXT_TELEMETRY_DISABLED=1
```

### B. Python Backend (FastAPI) - Railway Optimization

#### 1. Create `railway.json`
```json
{
  "$schema": "https://railway.app/railway.schema.json",
  "build": {
    "builder": "nixpacks",
    "buildCommand": "pip install -r requirements-railway.txt"
  },
  "deploy": {
    "startCommand": "uvicorn api.fastapi_endpoints:app --host 0.0.0.0 --port $PORT",
    "restartPolicyType": "on-failure",
    "restartPolicyMaxRetries": 10
  },
  "healthcheck": {
    "path": "/health",
    "interval": 30,
    "timeout": 10
  }
}
```

#### 2. Create `Procfile` (Railway Alternative)
```
web: uvicorn api.fastapi_endpoints:app --host 0.0.0.0 --port $PORT --workers 4
worker: celery -A tasks.celery_tasks worker --loglevel=info
beat: celery -A tasks.celery_tasks beat --loglevel=info
```

#### 3. Create `nixpacks.toml`
```toml
[phases.setup]
nixPkgs = ["python311", "postgresql", "gcc", "g++"]

[phases.install]
cmds = ["pip install -r requirements-railway.txt"]

[phases.build]
cmds = ["echo 'Build phase completed'"]

[start]
cmd = "uvicorn api.fastapi_endpoints:app --host 0.0.0.0 --port $PORT --workers 2"
```

#### 4. Update FastAPI CORS Configuration
Modify `api/fastapi_endpoints.py`:

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os

app = FastAPI(
    title="AI Arbitrage System API",
    description="Autonomous AI-powered arbitrage platform",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS Configuration - Allow Vercel domains
origins = [
    "http://localhost:3000",
    "http://localhost:3001",
    "https://*.vercel.app",
    "https://your-domain.com",  # Your custom domain
]

# If VERCEL_URL env var exists, add it
if vercel_url := os.getenv("VERCEL_URL"):
    origins.append(f"https://{vercel_url}")

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)

# Health check endpoint
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "environment": os.getenv("RAILWAY_ENVIRONMENT", "development"),
        "service": "ai-arbitrage-api"
    }

# Add your existing routes here...
```

#### 5. Update Database Connection for Railway
Create/update `database/db_config.py`:

```python
import os
from urllib.parse import quote_plus

# Railway automatically provides these environment variables
DATABASE_URL = os.getenv("DATABASE_URL")  # PostgreSQL
REDIS_URL = os.getenv("REDIS_URL")        # Redis
MONGODB_URL = os.getenv("MONGO_URL")      # MongoDB

# If using Railway's database services, they provide these automatically
# Otherwise, construct from individual vars
if not DATABASE_URL:
    db_user = os.getenv("PGUSER", "postgres")
    db_pass = quote_plus(os.getenv("PGPASSWORD", ""))
    db_host = os.getenv("PGHOST", "localhost")
    db_port = os.getenv("PGPORT", "5432")
    db_name = os.getenv("PGDATABASE", "arbitrage_db")
    DATABASE_URL = f"postgresql://{db_user}:{db_pass}@{db_host}:{db_port}/{db_name}"

# Redis configuration
if not REDIS_URL:
    redis_host = os.getenv("REDIS_HOST", "localhost")
    redis_port = os.getenv("REDIS_PORT", "6379")
    redis_pass = os.getenv("REDIS_PASSWORD", "")
    if redis_pass:
        REDIS_URL = f"redis://:{redis_pass}@{redis_host}:{redis_port}/0"
    else:
        REDIS_URL = f"redis://{redis_host}:{redis_port}/0"

# MongoDB configuration
if not MONGODB_URL:
    mongo_user = os.getenv("MONGO_USER", "")
    mongo_pass = quote_plus(os.getenv("MONGO_PASSWORD", ""))
    mongo_host = os.getenv("MONGO_HOST", "localhost")
    mongo_port = os.getenv("MONGO_PORT", "27017")
    mongo_db = os.getenv("MONGO_DB", "arbitrage")
    
    if mongo_user and mongo_pass:
        MONGODB_URL = f"mongodb://{mongo_user}:{mongo_pass}@{mongo_host}:{mongo_port}/{mongo_db}"
    else:
        MONGODB_URL = f"mongodb://{mongo_host}:{mongo_port}/{mongo_db}"

print(f"🗄️  Database URLs configured for Railway environment")
```

#### 6. Create Production Settings File
Create `config/production.yaml`:

```yaml
environment: production
debug: false

server:
  host: 0.0.0.0
  port: ${PORT:-8000}
  workers: 4
  
database:
  url: ${DATABASE_URL}
  pool_size: 20
  max_overflow: 10
  pool_pre_ping: true
  
redis:
  url: ${REDIS_URL}
  max_connections: 50
  
mongodb:
  url: ${MONGODB_URL}
  max_pool_size: 100
  
ai_settings:
  reasoning:
    model: "gemini-2.5-flash"
    temperature: 0.7
    api_key: ${GOOGLE_AI_API_KEY}
    
api_keys:
  google_ai: ${GOOGLE_AI_API_KEY}
  openai: ${OPENAI_API_KEY}
  keepa: ${KEEPA_API_KEY}
  
security:
  allowed_origins:
    - "https://*.vercel.app"
    - "https://your-domain.com"
  api_key_header: "X-API-Key"
  
rate_limiting:
  enabled: true
  requests_per_minute: 60
  
monitoring:
  sentry_dsn: ${SENTRY_DSN}
  prometheus_enabled: true
  log_level: "INFO"
```

### C. Environment Variables Setup

#### Create `.env.railway.template`
```bash
# ============================================
# Railway Environment Variables Template
# ============================================

# === Automatically Provided by Railway ===
# (Don't set these - Railway provides them)
# DATABASE_URL
# REDIS_URL
# MONGO_URL
# PORT
# RAILWAY_ENVIRONMENT
# RAILWAY_PROJECT_ID
# RAILWAY_SERVICE_ID

# === AI API Keys (REQUIRED) ===
GOOGLE_AI_API_KEY=your_google_ai_api_key_here
OPENAI_API_KEY=your_openai_api_key_here  # Optional fallback

# === Marketplace APIs ===
KEEPA_API_KEY=your_keepa_api_key
BOOKSCOUTER_API_KEY=your_bookscouter_key
TCGPLAYER_API_KEY=your_tcgplayer_key
BUYBOTPRO_API_KEY=your_buybotpro_key

# === Amazon SP-API ===
AMAZON_SP_CLIENT_ID=your_sp_client_id
AMAZON_SP_CLIENT_SECRET=your_sp_client_secret
AMAZON_SP_REFRESH_TOKEN=your_refresh_token
AMAZON_REGION=us-east-1

# === eBay API ===
EBAY_APP_ID=your_ebay_app_id
EBAY_DEV_ID=your_ebay_dev_id
EBAY_CERT_ID=your_ebay_cert_id

# === Payment Processing ===
STRIPE_API_KEY=your_stripe_key
STRIPE_WEBHOOK_SECRET=your_webhook_secret

# === Communication ===
TWILIO_ACCOUNT_SID=your_twilio_sid
TWILIO_AUTH_TOKEN=your_twilio_token
TWILIO_PHONE_NUMBER=your_phone_number

SENDGRID_API_KEY=your_sendgrid_key
SENDGRID_FROM_EMAIL=noreply@yourdomain.com

# === Monitoring ===
SENTRY_DSN=your_sentry_dsn

# === Security ===
SECRET_KEY=your_secret_key_min_32_chars
API_KEY=your_api_key_for_client_access

# === Frontend URL (for CORS) ===
FRONTEND_URL=https://your-app.vercel.app
```

#### Create `.env.vercel.template`
```bash
# ============================================
# Vercel Environment Variables Template
# ============================================

# === API Configuration ===
NEXT_PUBLIC_API_URL=https://your-railway-api.railway.app
NEXT_PUBLIC_WS_URL=wss://your-railway-api.railway.app

# === Optional Analytics ===
NEXT_PUBLIC_GOOGLE_ANALYTICS=
NEXT_PUBLIC_SENTRY_DSN=

# === Build Configuration ===
NEXT_TELEMETRY_DISABLED=1

# === API Key (for protected routes) ===
API_SECRET_KEY=your_secret_key_matches_backend
```

---

## 🚀 PHASE 3: Deployment Execution

### Step 1: Prepare Git Repository

```bash
# Initialize git if not exists
git init
git add .
git commit -m "Initial commit: AI Arbitrage System"

# Create GitHub repository using MCP tool
# Use: github:create_repository
# Parameters:
#   name: "ai-arbitrage-system"
#   description: "AI-powered arbitrage platform"
#   private: true

# Push to GitHub
git remote add origin https://github.com/YOUR_USERNAME/ai-arbitrage-system.git
git branch -M main
git push -u origin main
```

### Step 2: Deploy to Railway (Backend + Databases)

```bash
# Install Railway CLI (if not installed)
npm install -g @railway/cli

# Login to Railway
railway login

# Initialize Railway project
railway init

# Create services:
# 1. Python API Service
railway add --name python-api

# 2. PostgreSQL Database
railway add --plugin postgresql

# 3. Redis Cache
railway add --plugin redis

# 4. MongoDB Database
railway add --plugin mongodb

# Link repository
railway link

# Set environment variables (use template above)
railway variables set GOOGLE_AI_API_KEY=your_key
railway variables set OPENAI_API_KEY=your_key
# ... continue with all required env vars

# Deploy!
railway up --service python-api
```

**Alternative: Railway Dashboard Method**
1. Go to https://railway.app
2. Click "New Project"
3. Select "Deploy from GitHub repo"
4. Choose your repository
5. Railway auto-detects Python and creates service
6. Add PostgreSQL, Redis, MongoDB plugins
7. Set environment variables in dashboard
8. Deploy automatically happens

### Step 3: Deploy Frontend to Vercel

**Using Vercel CLI (Recommended with Cursor):**

```bash
# Cursor can execute these commands via bash_tool

# Navigate to frontend directory
cd frontend

# Install Vercel CLI globally
npm install -g vercel

# Login to Vercel
vercel login

# Deploy (first time - interactive)
vercel

# Follow prompts:
# - Link to existing project? N
# - Project name: ai-arbitrage-dashboard
# - Directory: ./
# - Override settings? N

# Deploy to production
vercel --prod
```

**Using MCP Vercel Tool:**

```typescript
// Cursor can use this MCP tool directly
await tools.Vercel.deploy_to_vercel({
  // Automatically deploys current directory
});

// Check deployment status
await tools.Vercel.list_deployments({
  projectId: "prj_xxxxx",
  teamId: "team_xxxxx"
});

// Get build logs if issues
await tools.Vercel.get_deployment_build_logs({
  idOrUrl: "dpl_xxxxx",
  teamId: "team_xxxxx",
  limit: 100
});
```

**Using Vercel Dashboard:**
1. Go to https://vercel.com
2. Click "Add New Project"
3. Import from GitHub
4. Select repository
5. Configure:
   - Framework Preset: Next.js
   - Root Directory: `frontend`
   - Build Command: `npm run build`
   - Output Directory: `.next`
   - Install Command: `npm install`
6. Add environment variables from template
7. Click "Deploy"

### Step 4: Configure Custom Domains (Optional)

```bash
# Add domain to Vercel
vercel domains add yourdomain.com

# Add domain to Railway
railway domain add api.yourdomain.com

# Update DNS records:
# Vercel: Add CNAME record pointing to cname.vercel-dns.com
# Railway: Add CNAME record pointing to your-service.up.railway.app
```

---

## 🔍 PHASE 4: Testing & Validation

### A. Test Backend Health

```bash
# Test Railway API health endpoint
curl https://your-railway-api.railway.app/health

# Expected response:
# {
#   "status": "healthy",
#   "environment": "production",
#   "service": "ai-arbitrage-api"
# }

# Test API docs
curl https://your-railway-api.railway.app/docs

# Test WebSocket connection
wscat -c wss://your-railway-api.railway.app/ws
```

### B. Test Frontend Deployment

```bash
# Visit Vercel deployment URL
curl https://your-app.vercel.app

# Check API proxy
curl https://your-app.vercel.app/api/v1/health

# Test from browser:
# - Open developer console
# - Navigate to https://your-app.vercel.app
# - Check for CORS errors
# - Verify API calls succeed
```

### C. Test Database Connections

```python
# Create test script: scripts/test_railway_db.py
import asyncio
from database.db_config import DATABASE_URL, REDIS_URL, MONGODB_URL
from sqlalchemy import create_engine, text
import redis
from pymongo import MongoClient

async def test_connections():
    print("Testing Railway database connections...")
    
    # Test PostgreSQL
    try:
        engine = create_engine(DATABASE_URL)
        with engine.connect() as conn:
            result = conn.execute(text("SELECT version();"))
            print(f"✅ PostgreSQL: {result.fetchone()[0]}")
    except Exception as e:
        print(f"❌ PostgreSQL Error: {e}")
    
    # Test Redis
    try:
        r = redis.from_url(REDIS_URL)
        r.ping()
        print(f"✅ Redis: Connected")
    except Exception as e:
        print(f"❌ Redis Error: {e}")
    
    # Test MongoDB
    try:
        client = MongoClient(MONGODB_URL)
        client.admin.command('ping')
        print(f"✅ MongoDB: Connected")
    except Exception as e:
        print(f"❌ MongoDB Error: {e}")

if __name__ == "__main__":
    asyncio.run(test_connections())
```

```bash
# Run on Railway
railway run python scripts/test_railway_db.py
```

### D. Load Testing

```bash
# Install Apache Bench
sudo apt-get install apache2-utils

# Test API endpoint
ab -n 1000 -c 10 https://your-railway-api.railway.app/health

# Test frontend
ab -n 1000 -c 10 https://your-app.vercel.app/
```

---

## 🐛 PHASE 5: Common Issues & Fixes

### Issue 1: Vercel Build Fails

**Symptoms:**
- Build logs show TypeScript errors
- Module not found errors
- Out of memory errors

**Cursor Fix Steps:**

```bash
# Use MCP tools to get build logs
# Tool: Vercel:get_deployment_build_logs

# Fix TypeScript errors
# Update frontend/tsconfig.json
{
  "compilerOptions": {
    "skipLibCheck": true,
    "strict": false,
    "forceConsistentCasingInFileNames": true
  }
}

# Fix memory issues in vercel.json
{
  "build": {
    "env": {
      "NODE_OPTIONS": "--max-old-space-size=4096"
    }
  }
}

# Commit and redeploy
git add .
git commit -m "Fix: Vercel build configuration"
git push origin main
```

### Issue 2: Railway Container Crashes

**Symptoms:**
- Service shows "crashed" status
- Health check fails
- Port binding errors

**Cursor Fix Steps:**

```bash
# Check Railway logs
railway logs --service python-api

# Common fixes:

# 1. Port binding issue
# Update api/fastapi_endpoints.py
import os
PORT = int(os.getenv("PORT", 8000))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=PORT)

# 2. Missing dependencies
# Check requirements-railway.txt has all needed packages

# 3. Database connection timeout
# Update database/db_config.py
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    pool_recycle=3600,
    connect_args={"connect_timeout": 10}
)

# Redeploy
railway up
```

### Issue 3: CORS Errors

**Symptoms:**
- Browser console shows CORS errors
- OPTIONS requests fail
- Cross-origin requests blocked

**Cursor Fix Steps:**

```python
# Update api/fastapi_endpoints.py CORS middleware
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Temporarily allow all for testing
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)

# Add OPTIONS handler for preflight
@app.options("/{path:path}")
async def options_handler(path: str):
    return {"status": "ok"}

# After confirming it works, restrict origins:
allow_origins=[
    "https://your-app.vercel.app",
    "https://*.vercel.app",
]
```

### Issue 4: Environment Variables Not Loading

**Cursor Fix Steps:**

```bash
# Verify Railway variables
railway variables

# Verify Vercel variables
vercel env ls

# Pull environment variables locally for testing
railway variables > .env.railway
vercel env pull .env.vercel

# Test locally
source .env.railway
python main.py
```

### Issue 5: Database Connection Pool Exhausted

**Cursor Fix:**

```python
# Update database/db_config.py
from sqlalchemy import create_engine
from sqlalchemy.pool import QueuePool

engine = create_engine(
    DATABASE_URL,
    poolclass=QueuePool,
    pool_size=20,
    max_overflow=10,
    pool_pre_ping=True,
    pool_recycle=3600,
    echo=False
)

# Add connection cleanup
@app.on_event("shutdown")
async def shutdown():
    engine.dispose()
```

### Issue 6: WebSocket Connection Fails

**Cursor Fix:**

```python
# Ensure Railway has WebSocket support
# Update railway.json
{
  "deploy": {
    "startCommand": "uvicorn api.fastapi_endpoints:app --host 0.0.0.0 --port $PORT --ws-ping-interval 30 --ws-ping-timeout 30"
  }
}

# Update frontend WebSocket connection
const ws = new WebSocket(
  `${process.env.NEXT_PUBLIC_WS_URL}/ws`,
  {
    headers: {
      'Origin': window.location.origin
    }
  }
);

ws.onopen = () => console.log('WebSocket connected');
ws.onerror = (error) => console.error('WebSocket error:', error);
```

---

## 📊 PHASE 6: Monitoring & Optimization

### A. Set Up Monitoring

**Railway Monitoring:**
```bash
# View real-time logs
railway logs --follow

# Check metrics
railway metrics

# Set up Sentry (in api/fastapi_endpoints.py)
import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration

sentry_sdk.init(
    dsn=os.getenv("SENTRY_DSN"),
    integrations=[FastApiIntegration()],
    traces_sample_rate=1.0,
    environment=os.getenv("RAILWAY_ENVIRONMENT", "production")
)
```

**Vercel Monitoring:**
```bash
# View deployment analytics
vercel inspect <deployment-url>

# Check function logs
vercel logs <deployment-url>

# Monitor with Vercel Analytics (add to _app.tsx)
import { Analytics } from '@vercel/analytics/react';

function MyApp({ Component, pageProps }) {
  return (
    <>
      <Component {...pageProps} />
      <Analytics />
    </>
  );
}
```

### B. Performance Optimization

**Backend Optimizations:**

```python
# Add Redis caching layer
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from fastapi_cache.decorator import cache

@app.on_event("startup")
async def startup():
    redis = aioredis.from_url(REDIS_URL)
    FastAPICache.init(RedisBackend(redis), prefix="arbitrage-cache:")

# Cache expensive API calls
@app.get("/api/v1/opportunities")
@cache(expire=60)  # Cache for 60 seconds
async def get_opportunities():
    # Your logic here
    pass

# Add connection pooling
from sqlalchemy.pool import NullPool
engine = create_engine(DATABASE_URL, poolclass=NullPool)

# Enable compression
from fastapi.middleware.gzip import GZipMiddleware
app.add_middleware(GZipMiddleware, minimum_size=1000)
```

**Frontend Optimizations:**

```typescript
// Use dynamic imports for large components
import dynamic from 'next/dynamic';

const HeavyComponent = dynamic(() => import('./HeavyComponent'), {
  ssr: false,
  loading: () => <p>Loading...</p>
});

// Enable Image Optimization
import Image from 'next/image';

<Image
  src="/product.jpg"
  width={500}
  height={500}
  loading="lazy"
  placeholder="blur"
/>

// Use SWR for data fetching with caching
import useSWR from 'swr';

const { data, error } = useSWR('/api/opportunities', fetcher, {
  refreshInterval: 30000,
  revalidateOnFocus: false
});
```

### C. Cost Optimization

**Railway Tips:**
- Use horizontal scaling only when needed
- Set up auto-scaling based on CPU/memory
- Use Railway's sleep feature for dev environments
- Monitor database connection pools

**Vercel Tips:**
- Optimize images (use Next.js Image component)
- Enable edge caching
- Reduce serverless function execution time
- Use ISR (Incremental Static Regeneration)

```javascript
// Enable ISR in Next.js pages
export async function getStaticProps() {
  const data = await fetchData();
  
  return {
    props: { data },
    revalidate: 60, // Revalidate every 60 seconds
  };
}
```

---

## 🔄 PHASE 7: Continuous Deployment Setup

### A. GitHub Actions for Vercel

Create `.github/workflows/vercel-deploy.yml`:

```yaml
name: Deploy to Vercel

on:
  push:
    branches: [main]
    paths:
      - 'frontend/**'
  pull_request:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Setup Node.js
        uses: actions/setup-node@v3
        with:
          node-version: '18'
          
      - name: Install dependencies
        run: cd frontend && npm ci
        
      - name: Build
        run: cd frontend && npm run build
        env:
          NEXT_PUBLIC_API_URL: ${{ secrets.NEXT_PUBLIC_API_URL }}
          
      - name: Deploy to Vercel
        uses: amondnet/vercel-action@v20
        with:
          vercel-token: ${{ secrets.VERCEL_TOKEN }}
          vercel-org-id: ${{ secrets.VERCEL_ORG_ID }}
          vercel-project-id: ${{ secrets.VERCEL_PROJECT_ID }}
          working-directory: ./frontend
          vercel-args: '--prod'
```

### B. GitHub Actions for Railway

Create `.github/workflows/railway-deploy.yml`:

```yaml
name: Deploy to Railway

on:
  push:
    branches: [main]
    paths:
      - 'api/**'
      - 'core/**'
      - 'database/**'
      - 'requirements-railway.txt'

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Install Railway CLI
        run: npm install -g @railway/cli
        
      - name: Deploy to Railway
        run: railway up --service python-api
        env:
          RAILWAY_TOKEN: ${{ secrets.RAILWAY_TOKEN }}
```

### C. Add Secrets to GitHub

```bash
# Get Vercel tokens
vercel whoami
vercel project ls

# Get Railway token
railway whoami
railway tokens create

# Add to GitHub:
# Settings -> Secrets and variables -> Actions -> New repository secret
# Add:
# - VERCEL_TOKEN
# - VERCEL_ORG_ID
# - VERCEL_PROJECT_ID
# - RAILWAY_TOKEN
```

---

## 📝 PHASE 8: Documentation & Handoff

### A. Create Deployment Checklist

Create `DEPLOYMENT_CHECKLIST.md`:

```markdown
# Deployment Checklist

## Pre-Deployment
- [ ] All environment variables configured in Railway
- [ ] All environment variables configured in Vercel
- [ ] Database migrations run
- [ ] API keys tested and valid
- [ ] CORS origins updated with production URLs
- [ ] Error tracking (Sentry) configured
- [ ] Health check endpoints working

## Deployment
- [ ] Backend deployed to Railway
- [ ] Databases provisioned and connected
- [ ] Frontend deployed to Vercel
- [ ] Custom domains configured (if applicable)
- [ ] SSL certificates active
- [ ] DNS records updated

## Post-Deployment
- [ ] Health checks passing
- [ ] API endpoints responding
- [ ] Frontend loads without errors
- [ ] WebSocket connections working
- [ ] Database connections stable
- [ ] No CORS errors in console
- [ ] Monitoring dashboards active
- [ ] Load testing completed

## Verification
- [ ] Test user signup/login
- [ ] Test opportunity scanning
- [ ] Test AI negotiation
- [ ] Test product listing
- [ ] Test customer support bot
- [ ] Verify email notifications
- [ ] Verify SMS notifications
- [ ] Check error logs
```

### B. Create Operations Guide

Create `OPERATIONS_GUIDE.md`:

```markdown
# Operations Guide

## Daily Operations

### View Logs
```bash
# Railway logs
railway logs --service python-api --follow

# Vercel logs
vercel logs https://your-app.vercel.app
```

### Monitor Health
- Railway Dashboard: https://railway.app
- Vercel Dashboard: https://vercel.com
- Sentry: https://sentry.io

### Restart Services
```bash
# Railway restart
railway service restart python-api

# Vercel redeploy
vercel --prod
```

## Scaling

### Horizontal Scaling (Railway)
```bash
railway scale --replicas 3 python-api
```

### Vertical Scaling (Railway)
- Go to Railway dashboard
- Select service
- Update memory/CPU limits

## Database Management

### Backups
```bash
# PostgreSQL backup
railway run pg_dump $DATABASE_URL > backup.sql

# Restore
railway run psql $DATABASE_URL < backup.sql
```

### Migrations
```bash
railway run alembic upgrade head
```

## Troubleshooting

### High Memory Usage
- Check for memory leaks in Python code
- Review database connection pools
- Check for unclosed resources

### Slow Response Times
- Review database query performance
- Check external API latencies
- Review caching strategy

### Connection Errors
- Verify environment variables
- Check database connection limits
- Review CORS configuration
```

---

## 🎯 PHASE 9: Final Optimization

### A. Security Hardening

```python
# Add rate limiting
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

@app.get("/api/v1/opportunities")
@limiter.limit("60/minute")
async def get_opportunities(request: Request):
    pass

# Add API key authentication
from fastapi.security import APIKeyHeader
from fastapi import Security, HTTPException

api_key_header = APIKeyHeader(name="X-API-Key")

async def verify_api_key(api_key: str = Security(api_key_header)):
    if api_key != os.getenv("API_KEY"):
        raise HTTPException(status_code=403, detail="Invalid API Key")
    return api_key

@app.get("/api/v1/protected")
async def protected_route(api_key: str = Depends(verify_api_key)):
    pass
```

### B. Performance Tuning

```python
# Enable query optimization
from sqlalchemy import event
from sqlalchemy.engine import Engine
import time

@event.listens_for(Engine, "before_cursor_execute")
def before_cursor_execute(conn, cursor, statement, parameters, context, executemany):
    conn.info.setdefault('query_start_time', []).append(time.time())

@event.listens_for(Engine, "after_cursor_execute")
def after_cursor_execute(conn, cursor, statement, parameters, context, executemany):
    total = time.time() - conn.info['query_start_time'].pop(-1)
    if total > 1:  # Log slow queries
        print(f"Slow query ({total:.2f}s): {statement}")

# Add database indexes
from sqlalchemy import Index

class Opportunity(Base):
    __tablename__ = "opportunities"
    
    id = Column(Integer, primary_key=True)
    category = Column(String, index=True)
    profit_margin = Column(Float, index=True)
    created_at = Column(DateTime, index=True)
    
    __table_args__ = (
        Index('ix_category_margin', 'category', 'profit_margin'),
    )
```

### C. Caching Strategy

```python
# Implement multi-tier caching
from functools import lru_cache
import redis
import pickle

# L1: In-memory cache (LRU)
@lru_cache(maxsize=1000)
def get_category_keywords(category: str):
    return fetch_keywords_from_db(category)

# L2: Redis cache
def cached_api_call(key: str, fetch_func, ttl: int = 300):
    redis_client = redis.from_url(REDIS_URL)
    
    # Try cache first
    cached = redis_client.get(key)
    if cached:
        return pickle.loads(cached)
    
    # Fetch and cache
    result = fetch_func()
    redis_client.setex(key, ttl, pickle.dumps(result))
    return result

# Usage
opportunities = cached_api_call(
    "opportunities:latest",
    lambda: fetch_opportunities_from_db(),
    ttl=60
)
```

---

## ✅ PHASE 10: Verification & Sign-off

### Final Verification Script

Create `scripts/verify_deployment.py`:

```python
#!/usr/bin/env python3
"""
Deployment Verification Script
Run after deployment to verify everything works
"""

import requests
import asyncio
import sys
from typing import Dict, List

class DeploymentVerifier:
    def __init__(self, backend_url: str, frontend_url: str):
        self.backend_url = backend_url
        self.frontend_url = frontend_url
        self.results: List[Dict] = []
    
    def test_backend_health(self):
        """Test backend health endpoint"""
        try:
            response = requests.get(f"{self.backend_url}/health", timeout=10)
            assert response.status_code == 200
            assert response.json()["status"] == "healthy"
            self.results.append({"test": "Backend Health", "status": "✅ PASS"})
        except Exception as e:
            self.results.append({"test": "Backend Health", "status": f"❌ FAIL: {e}"})
    
    def test_backend_docs(self):
        """Test API documentation endpoint"""
        try:
            response = requests.get(f"{self.backend_url}/docs", timeout=10)
            assert response.status_code == 200
            self.results.append({"test": "API Docs", "status": "✅ PASS"})
        except Exception as e:
            self.results.append({"test": "API Docs", "status": f"❌ FAIL: {e}"})
    
    def test_frontend_load(self):
        """Test frontend loading"""
        try:
            response = requests.get(self.frontend_url, timeout=10)
            assert response.status_code == 200
            assert len(response.content) > 1000  # Basic sanity check
            self.results.append({"test": "Frontend Load", "status": "✅ PASS"})
        except Exception as e:
            self.results.append({"test": "Frontend Load", "status": f"❌ FAIL: {e}"})
    
    def test_cors(self):
        """Test CORS configuration"""
        try:
            headers = {"Origin": self.frontend_url}
            response = requests.options(
                f"{self.backend_url}/api/v1/opportunities",
                headers=headers,
                timeout=10
            )
            assert "access-control-allow-origin" in response.headers
            self.results.append({"test": "CORS Configuration", "status": "✅ PASS"})
        except Exception as e:
            self.results.append({"test": "CORS Configuration", "status": f"❌ FAIL: {e}"})
    
    def test_api_endpoint(self):
        """Test actual API endpoint"""
        try:
            response = requests.get(
                f"{self.backend_url}/api/v1/opportunities",
                timeout=10
            )
            assert response.status_code in [200, 401]  # 401 if auth required
            self.results.append({"test": "API Endpoint", "status": "✅ PASS"})
        except Exception as e:
            self.results.append({"test": "API Endpoint", "status": f"❌ FAIL: {e}"})
    
    def run_all_tests(self):
        """Run all verification tests"""
        print("🔍 Running Deployment Verification Tests...\n")
        
        self.test_backend_health()
        self.test_backend_docs()
        self.test_frontend_load()
        self.test_cors()
        self.test_api_endpoint()
        
        print("\n📊 Test Results:")
        print("=" * 50)
        for result in self.results:
            print(f"{result['test']}: {result['status']}")
        print("=" * 50)
        
        # Check if all passed
        failed = [r for r in self.results if "FAIL" in r["status"]]
        if failed:
            print(f"\n❌ {len(failed)} tests failed!")
            sys.exit(1)
        else:
            print("\n✅ All tests passed! Deployment verified.")
            sys.exit(0)

if __name__ == "__main__":
    # Update these with your actual URLs
    BACKEND_URL = "https://your-railway-api.railway.app"
    FRONTEND_URL = "https://your-app.vercel.app"
    
    verifier = DeploymentVerifier(BACKEND_URL, FRONTEND_URL)
    verifier.run_all_tests()
```

Run verification:
```bash
python scripts/verify_deployment.py
```

---

## 📚 Additional Resources

### Documentation Links
- **Vercel Docs**: https://vercel.com/docs
- **Railway Docs**: https://docs.railway.app
- **FastAPI Deployment**: https://fastapi.tiangolo.com/deployment/
- **Next.js Deployment**: https://nextjs.org/docs/deployment

### Cursor AI Tools Summary

**Priority Tools for This Deployment:**

1. `Vercel:deploy_to_vercel` - Deploy frontend
2. `Vercel:search_vercel_documentation` - Find solutions
3. `Vercel:get_deployment_build_logs` - Debug issues
4. `bash_tool` - Execute CLI commands
5. `str_replace` - Fix code issues
6. `create_file` - Create config files
7. `view` - Read current files
8. `github:push_files` - Push multiple files at once
9. `web_search` - Search for solutions
10. `web_fetch` - Fetch documentation

### Quick Reference Commands

```bash
# Railway CLI
railway login
railway init
railway up
railway logs
railway variables set KEY=value
railway domain add

# Vercel CLI
vercel login
vercel
vercel --prod
vercel env add
vercel domains add
vercel logs

# Testing
curl https://api-url/health
curl https://frontend-url
ab -n 1000 -c 10 https://api-url/health

# Database
railway run psql $DATABASE_URL
railway run redis-cli -u $REDIS_URL
railway run mongosh $MONGODB_URL
```

---

## 🎓 Cursor Agent Instructions

**When Cursor Agent encounters issues:**

1. **Read error messages carefully**
   - Use `view` to read log files
   - Use `Vercel:get_deployment_build_logs` for Vercel errors
   - Use `railway logs` for Railway errors

2. **Search for solutions**
   - Use `Vercel:search_vercel_documentation`
   - Use `web_search` for error messages
   - Use `web_fetch` to get full documentation

3. **Make incremental changes**
   - Fix one issue at a time
   - Test after each change
   - Commit working changes

4. **Use MCP tools efficiently**
   - Batch file updates with `github:push_files`
   - Use `str_replace` for precise edits
   - Use `bash_tool` for complex commands

5. **Verify changes**
   - Run local tests first
   - Deploy to staging (if available)
   - Monitor logs after deployment

---

## 🚨 Emergency Rollback

If something goes wrong:

```bash
# Vercel rollback
vercel rollback <deployment-url>

# Railway rollback
railway rollback <deployment-id>

# Or redeploy previous working commit
git revert HEAD
git push origin main
```

---

## ✨ Success Criteria

Deployment is considered successful when:

- ✅ Backend health check returns 200
- ✅ Frontend loads without errors
- ✅ API endpoints respond correctly
- ✅ WebSocket connections work
- ✅ Database connections stable
- ✅ No CORS errors
- ✅ Monitoring is active
- ✅ All environment variables set
- ✅ SSL certificates active
- ✅ No critical errors in logs

---

**Document Version:** 1.0.0  
**Last Updated:** $(date)  
**For:** Cursor AI Agent with MCP Tools  
**Target:** Vercel + Railway Deployment
