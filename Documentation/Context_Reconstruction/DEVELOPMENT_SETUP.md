# ScraperSky Backend - Development Setup Guide
**Purpose:** Complete local development environment setup
**Last Updated:** November 17, 2025
**Audience:** New developers, AI assistants bootstrapping context

---

## Prerequisites

### Required Software
- **Python:** 3.10+ (3.11 recommended)
- **Docker:** For local development stack
- **Git:** Version control
- **PostgreSQL Client:** For database inspection (optional)

### Required Accounts
- **Supabase:** Database hosting
- **Google Cloud Platform:** For Google Maps API key
- **ScraperAPI:** For web scraping (WF7)
- **Render.com:** For production deployment (optional for local dev)

---

## Quick Start (5 Minutes)

### 1. Clone Repository
```bash
git clone https://github.com/hgroman/scrapersky-backend.git
cd scrapersky-backend
```

### 2. Create Virtual Environment
```bash
python3.11 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Configure Environment
```bash
# Copy example environment file
cp .env.example .env

# Edit .env with your actual credentials
nano .env  # or your preferred editor
```

### 5. Run Application
```bash
# Option A: Direct Python
python -m uvicorn src.main:app --reload --port 8000

# Option B: Docker Compose (includes database)
docker compose up --build
```

### 6. Verify Setup
```bash
# Check health endpoint
curl http://localhost:8000/health

# Check database health
curl http://localhost:8000/health/database
```

---

## Environment Variables

### Required Variables

```bash
# Database Configuration (Supabase)
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_POOLER_HOST=aws-0-us-west-1.pooler.supabase.com
SUPABASE_POOLER_PORT=6543
SUPABASE_POOLER_USER=postgres.your-project-id
SUPABASE_DB_PASSWORD=your_database_password

# Database Connection String
# CRITICAL: Must use these exact parameters for Supavisor compatibility
DATABASE_URL=postgresql+asyncpg://${SUPABASE_POOLER_USER}:${SUPABASE_DB_PASSWORD}@${SUPABASE_POOLER_HOST}:${SUPABASE_POOLER_PORT}/postgres?raw_sql=true&no_prepare=true&statement_cache_size=0

# Authentication
JWT_SECRET_KEY=your_jwt_secret_key_here
JWT_ALGORITHM=HS256
JWT_EXPIRATION_HOURS=24

# External APIs
GOOGLE_MAPS_API_KEY=your_google_maps_api_key_here  # For WF1-2
SCRAPER_API_KEY=your_scraper_api_key_here          # For WF7

# Application Configuration
ENVIRONMENT=development  # development | staging | production
LOG_LEVEL=INFO          # DEBUG | INFO | WARNING | ERROR
PORT=8000
```

### Scheduler Configuration (Optional)

```bash
# Domain Sitemap Submission Scheduler (WF4)
DOMAIN_SITEMAP_SUBMISSION_SCHEDULER_INTERVAL_SECONDS=60
DOMAIN_SITEMAP_SUBMISSION_SCHEDULER_BATCH_SIZE=5
DOMAIN_SITEMAP_SUBMISSION_SCHEDULER_MAX_INSTANCES=1

# Sitemap Import Scheduler (WF6)
SITEMAP_IMPORT_SCHEDULER_INTERVAL_SECONDS=300
SITEMAP_IMPORT_SCHEDULER_BATCH_SIZE=10
SITEMAP_IMPORT_SCHEDULER_MAX_INSTANCES=1

# Page Curation Scheduler (WF7)
PAGE_CURATION_SCHEDULER_INTERVAL_SECONDS=300
PAGE_CURATION_SCHEDULER_BATCH_SIZE=5
PAGE_CURATION_SCHEDULER_MAX_INSTANCES=1
```

---

## Database Setup

### Option 1: Use Existing Supabase Database (Recommended)

The application connects to a shared Supabase database. No local database setup required!

**Configuration:**
1. Get credentials from project owner
2. Add to `.env` file (see above)
3. Application auto-connects on startup

**Verification:**
```bash
# Test database connection
curl http://localhost:8000/health/database

# Expected response:
{
  "status": "healthy",
  "database": "connected",
  "timestamp": "2025-11-17T..."
}
```

### Option 2: Local PostgreSQL (Advanced)

For isolated development or testing:

```bash
# Install PostgreSQL locally
brew install postgresql@15  # macOS
# or use Docker:
docker run --name postgres-local -e POSTGRES_PASSWORD=localpass -p 5432:5432 -d postgres:15

# Update .env for local database
DATABASE_URL=postgresql+asyncpg://postgres:localpass@localhost:5432/scrapersky

# Run migrations (if available)
alembic upgrade head
```

**Note:** Local database requires manual schema setup. Use Supabase for development unless you need full isolation.

---

## Running the Application

### Development Mode (Auto-reload)

```bash
# Activate virtual environment
source venv/bin/activate

# Run with auto-reload
uvicorn src.main:app --reload --port 8000
```

**Access:**
- **API:** http://localhost:8000
- **Docs:** http://localhost:8000/docs (Swagger UI)
- **ReDoc:** http://localhost:8000/redoc

### Docker Compose (Full Stack)

```bash
# Start all services
docker compose up --build

# Run in background
docker compose up -d

# View logs
docker compose logs -f app

# Stop services
docker compose down
```

**Services:**
- **app:** FastAPI application
- **Database:** Connected to Supabase (no local PostgreSQL needed)

### Production Mode

```bash
# Run without reload (production-like)
uvicorn src.main:app --host 0.0.0.0 --port 8000 --workers 4
```

---

## Testing

### Run All Tests
```bash
# Activate virtual environment
source venv/bin/activate

# Run with pytest
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=src --cov-report=html
```

### Run Specific Tests
```bash
# Test specific module
pytest tests/services/test_domain_extraction_scheduler.py -v

# Test specific function
pytest tests/services/test_domain_extraction_scheduler.py::test_scheduler_runs -v
```

### WF6 Component Testing
```bash
cd tests/WF6
./scripts/test_component.py
```

**Test Configuration:** `tests/conftest.py`

---

## Code Quality

### Linting and Formatting
```bash
# Check code style
ruff check .

# Auto-fix issues
ruff check . --fix

# Format code
ruff format .
```

### Pre-commit Hooks
```bash
# Install pre-commit hooks
pre-commit install

# Run all checks manually
pre-commit run --all-files
```

---

## Common Development Tasks

### Verify Workflows

```bash
# Check WF1-3 pipeline (Google Maps → Domains)
curl -X POST http://localhost:8000/api/v3/google-maps-api/search/places \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{"query": "eye doctors in Honolulu"}'

# Check WF4 (Sitemap Discovery)
# View domains in GUI or query database

# Check WF7 (Page Extraction)
curl http://localhost:8000/api/v3/pages
```

### Database Queries

```bash
# Connect to Supabase database
psql "postgresql://postgres.your-project-id:password@aws-0-us-west-1.pooler.supabase.com:6543/postgres"

# Or use Supabase dashboard
```

**Common Queries:** See [HEALTH_CHECKS.md](./HEALTH_CHECKS.md)

### View Application Logs

```bash
# Docker
docker compose logs -f app

# Direct run (logs to stdout)
uvicorn src.main:app --reload --log-level debug
```

---

## Architecture Overview

### Project Structure
```
scrapersky-backend/
├── src/
│   ├── main.py                    # Application entry point
│   ├── config/                    # Configuration and settings
│   │   ├── settings.py            # Environment variables
│   │   └── logging_config.py      # Logging setup
│   ├── models/                    # SQLAlchemy models (Layer 1)
│   │   ├── place.py               # WF1-2
│   │   ├── domain.py              # WF3-4
│   │   ├── sitemap_file.py        # WF4-6
│   │   └── page.py                # WF6-7
│   ├── schemas/                   # Pydantic schemas (Layer 2)
│   ├── routers/                   # API endpoints (Layer 3)
│   │   ├── google_maps_api.py     # WF1
│   │   └── v3/                    # V3 API routes
│   ├── services/                  # Business logic (Layer 4)
│   │   ├── places/                # WF1-2 services
│   │   ├── sitemap/               # WF4-6 services
│   │   └── page_scraper/          # WF7 services
│   ├── schedulers/                # Background jobs
│   │   └── scheduler_instance.py  # Shared scheduler
│   └── db/                        # Database configuration
│       └── session.py             # Async session management
├── Documentation/                 # This guide and more
├── tests/                         # Test suite
├── docker-compose.yml            # Docker configuration
├── requirements.txt              # Python dependencies
└── .env.example                  # Environment template
```

### Key Concepts

**Layers (Constitutional Architecture):**
- **Layer 1:** Models (database schema)
- **Layer 2:** Schemas (API contracts)
- **Layer 3:** Routers (API endpoints, transaction boundaries)
- **Layer 4:** Services (business logic)

**Workflows:**
- **WF1-3:** Google Maps → Domains
- **WF4-6:** Domains → Pages
- **WF7:** Pages → Contacts

**Critical Patterns:**
- **Dual-Status Pattern:** Curation status + Processing status
- **Direct Service Calls:** No HTTP between services
- **SDK Scheduler Loop:** Standard background processing

**Reference:** [PATTERNS.md](./PATTERNS.md)

---

## Troubleshooting

### Database Connection Issues

**Problem:** `connection refused` or `timeout`

**Solutions:**
1. Verify Supabase credentials in `.env`
2. Check Supabase project is active
3. Verify connection string parameters (must include `?raw_sql=true&no_prepare=true`)
4. Test with health endpoint: `curl http://localhost:8000/health/database`

### Import Errors

**Problem:** `ModuleNotFoundError`

**Solutions:**
1. Ensure virtual environment is activated
2. Reinstall dependencies: `pip install -r requirements.txt`
3. Check Python version: `python --version` (must be 3.10+)

### Scheduler Not Running

**Problem:** Background jobs not processing

**Solutions:**
1. Check scheduler logs for errors
2. Verify scheduler configuration in `.env`
3. Ensure database connection is healthy
4. Check for stuck jobs: See [HEALTH_CHECKS.md](./HEALTH_CHECKS.md)

### API Key Errors

**Problem:** `403 Forbidden` from Google Maps or ScraperAPI

**Solutions:**
1. Verify API keys in `.env`
2. Check API key quotas in respective dashboards
3. Ensure environment is loaded: `echo $GOOGLE_MAPS_API_KEY`

---

## Next Steps

### After Setup

1. **Read Quick Start:** [QUICK_START.md](./QUICK_START.md) - 5-minute overview
2. **Understand Workflows:** [SYSTEM_MAP.md](./SYSTEM_MAP.md) - Complete architecture
3. **Learn Patterns:** [PATTERNS.md](./PATTERNS.md) - Do/Don't patterns
4. **Check Health:** [HEALTH_CHECKS.md](./HEALTH_CHECKS.md) - Verification queries

### Development Workflow

1. **Create feature branch:** `git checkout -b feature/your-feature`
2. **Make changes** following [PATTERNS.md](./PATTERNS.md)
3. **Run tests:** `pytest tests/ -v`
4. **Run linter:** `ruff check . && ruff format .`
5. **Commit:** `git commit -m "feat: your feature"`
6. **Push:** `git push origin feature/your-feature`
7. **Create PR** on GitHub

---

## Getting Help

### Documentation
- **Quick Reference:** [QUICK_START.md](./QUICK_START.md)
- **Complete System:** [SYSTEM_MAP.md](./SYSTEM_MAP.md)
- **Code Patterns:** [PATTERNS.md](./PATTERNS.md)
- **Health Checks:** [HEALTH_CHECKS.md](./HEALTH_CHECKS.md)
- **Dependencies:** [DEPENDENCY_MAP.md](./DEPENDENCY_MAP.md)
- **Incidents:** [INCIDENTS/](../INCIDENTS/)

### Code Examples
Look at existing implementations:
- **WF7 Service:** `src/services/page_scraper/WF7_V2_L4_1of2_PageCurationService.py`
- **WF7 Router:** `src/routers/v3/WF7_V3_L3_1of1_PagesRouter.py`
- **Scheduler:** `src/schedulers/WF7_V2_L4_2of2_PageCurationScheduler.py`

### Common Issues
See [INCIDENTS/](../INCIDENTS/) for documented failures and solutions.

---

## Environment-Specific Notes

### Development
- Use `ENVIRONMENT=development` in `.env`
- Auto-reload enabled
- Debug logging
- Local testing safe

### Staging
- Use `ENVIRONMENT=staging` in `.env`
- Connected to staging Supabase
- Production-like configuration
- Safe for integration testing

### Production
- Use `ENVIRONMENT=production` in `.env`
- Connected to production Supabase
- Multiple workers
- Strict error handling
- Monitor logs on Render.com

---

**Last Updated:** November 17, 2025
**Status:** Complete and tested
**Questions?** See [QUICK_START.md](./QUICK_START.md) or [SYSTEM_MAP.md](./SYSTEM_MAP.md)
