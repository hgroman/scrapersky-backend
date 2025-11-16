# ScraperSky Configuration - Quick Reference Guide

## Generated Documentation Files

The following comprehensive documentation has been created and saved to the repository:

1. **CONFIGURATION_ANALYSIS.md** - Complete configuration guide
   - Settings structure and patterns
   - All environment variables by category
   - Deployment configurations
   - Logging setup
   - Best practices and concerns

2. **CONFIGURATION_CODE_EXAMPLES.md** - Code snippets and examples
   - Settings class implementation
   - Database connection patterns
   - Docker configurations
   - JWT setup
   - Usage examples

Located in: `/home/user/scrapersky-backend/Docs/`

---

## Critical Files to Know

| File | Purpose | Type |
|------|---------|------|
| `src/config/settings.py` | Central configuration | Python |
| `.env` | Runtime configuration | Environment |
| `.env.example` | Template for .env | Template |
| `docker-compose.yml` | Dev environment | Docker |
| `docker-compose.prod.yml` | Production environment | Docker |
| `Dockerfile` | Container image build | Docker |
| `render.yaml` | Render.com deployment | Config |
| `k8s/deployment.yaml` | Kubernetes deployment | K8s |
| `k8s/secrets.yaml` | Kubernetes secrets | K8s |
| `src/config/logging_config.py` | Logging setup | Python |
| `src/session/async_session.py` | Database session management | Python |
| `src/db/engine.py` | SQLAlchemy engine creation | Python |

---

## Critical Environment Variables (Must Set)

```bash
# 1. DATABASE - MANDATORY for any deployment
SUPABASE_URL=https://xxxx.supabase.co
SUPABASE_DB_PASSWORD=your_password
SUPABASE_POOLER_HOST=xxxx.pooler.supabase.co
SUPABASE_POOLER_PORT=6543
SUPABASE_POOLER_USER=postgres.pooler

# 2. AUTHENTICATION - MANDATORY (app will crash without this)
JWT_SECRET_KEY=very-long-random-secret-key

# 3. APPLICATION MODE
ENVIRONMENT=development  # or production

# 4. OPTIONAL BUT IMPORTANT (for features to work)
SCRAPER_API_KEY=your_api_key
GOOGLE_MAPS_API_KEY=your_api_key
```

---

## Quick Setup Guide

### Development Setup (5 minutes)

```bash
# 1. Copy environment template
cp .env.example .env

# 2. Edit .env with your Supabase credentials
nano .env

# 3. Start containers
docker compose up --build

# 4. Verify health
curl http://localhost:8000/health

# 5. Check logs
docker compose logs -f scrapersky
```

### Production Deployment Checklist

```bash
# 1. Verify all required variables are set
echo $SUPABASE_URL
echo $JWT_SECRET_KEY
echo $ENVIRONMENT

# 2. Check security settings
# - CORS_ORIGINS should NOT be "*"
# - SCRAPER_API cost flags should be false
# - LOG_LEVEL should be INFO or WARNING

# 3. Start with docker compose prod
docker compose -f docker-compose.prod.yml up -d

# 4. Monitor health
docker compose logs -f scrapersky

# 5. Test database connection
curl http://localhost:8000/health/database
```

---

## Settings Categories Quick Lookup

### Database Connection (6 variants)
- **Supabase Pooler** (Recommended): SUPABASE_POOLER_*
- **Direct Connection** (Backup): SUPABASE_DB_*
- **Full URL** (Alternative): DATABASE_URL
- **Pool Settings**: DB_MIN_POOL_SIZE, DB_MAX_POOL_SIZE, DB_CONNECTION_TIMEOUT

### Authentication & Security
- JWT_SECRET_KEY (CRITICAL - no default)
- JWT_EXPIRE_MINUTES
- DEVELOPMENT_USER_ID, SYSTEM_USER_ID, DEFAULT_TENANT_ID
- DEV_TOKEN

### External APIs
- SCRAPER_API_KEY (with 5 cost control flags)
- GOOGLE_MAPS_API_KEY
- MAUTIC_* (CRM integration)
- GCP_* (Google Cloud)

### Schedulers (5 types, each with 3 settings)
- DOMAIN_SCHEDULER_* (WF4)
- SITEMAP_SCHEDULER_* (WF2, WF3, WF5)
- DOMAIN_SITEMAP_SCHEDULER_* (NEW)
- SITEMAP_IMPORT_SCHEDULER_* (WF6)
- PAGE_CURATION_SCHEDULER_* (WF7)

### Application Settings
- PORT, HOST, MAX_WORKERS
- ENVIRONMENT (dev/prod/staging)
- CORS_ORIGINS, USER_AGENT
- LOG_LEVEL, CACHE_TTL

---

## Configuration Validation

### Pre-Deployment Checks

```bash
# Check database connection
docker compose logs | grep -i "supavisor\|database\|connection"

# Check JWT setup
docker compose logs | grep -i "jwt\|auth"

# Check all schedulers
docker compose logs | grep -i "scheduler\|setup"

# Check for warnings
docker compose logs | grep -i "warning"

# Health check
curl -v http://localhost:8000/health
```

### What Can Go Wrong

| Issue | Symptom | Fix |
|-------|---------|-----|
| Missing JWT_SECRET_KEY | Application crashes on startup | Set JWT_SECRET_KEY env var |
| No database connection | 500 errors on any DB query | Verify SUPABASE_POOLER_* settings |
| Wrong ENVIRONMENT | Validation failures in prod | Set ENVIRONMENT=production |
| CORS_ORIGINS too open | Security issues | Set specific origins for prod |
| ScraperAPI cost flags enabled | Unexpected billing spike | Set all SCRAPER_API_ENABLE_* to false |
| LOG_LEVEL hardcoded | Can't change logging verbosity | Use improved logging_config.py |

---

## Key Configuration Patterns

### 1. Singleton Settings Pattern
```python
from src.config.settings import settings

# Use globally - same instance everywhere
pool_size = settings.db_max_pool_size
```

### 2. Pydantic Configuration
- Case-insensitive environment variable names
- Optional fields don't fail on missing values
- Defaults provided for most settings
- Extra fields allowed (extra="allow")

### 3. Supavisor Requirements (NON-NEGOTIABLE)
```python
# These MUST be present in all database connections:
execution_options={
    "raw_sql": True,           # Use raw SQL
    "no_prepare": True,        # Disable prepared statements
    "statement_cache_size": 0, # No caching
}
```

### 4. Environment Detection
```python
# Automatic detection by hostname or explicit setting
ENVIRONMENT=development  # Sets pool_size=5
ENVIRONMENT=production   # Sets pool_size=DB_MAX_POOL_SIZE
```

---

## Scheduler Configuration Reference

### Standard Pattern
```
{SCHEDULER_NAME}_INTERVAL_MINUTES=1    # How often to run
{SCHEDULER_NAME}_BATCH_SIZE=N          # Items per batch
{SCHEDULER_NAME}_MAX_INSTANCES=1       # Concurrent runs
```

### Default Values
| Scheduler | Interval | Batch Size | Max Instances |
|-----------|----------|-----------|---------------|
| Domain | 1 min | 50 | 3 |
| Sitemap | 1 min | 25 | 3 |
| Domain-Sitemap | 1 min | 10 | 1* |
| Sitemap Import | 1 min | 20 | 1 |
| Page Curation | 1 min | 10 | 1 |

*No explicit MAX_INSTANCES setting in settings.py

---

## ScraperAPI Cost Control (CRITICAL)

### Safe Defaults (Already Set)
```
SCRAPER_API_ENABLE_PREMIUM=false           # 5-10x cost
SCRAPER_API_ENABLE_JS_RENDERING=false      # 10-25x cost
SCRAPER_API_ENABLE_GEOTARGETING=false      # 2-3x cost
SCRAPER_API_MAX_RETRIES=1                  # Reduced from 3
SCRAPER_API_COST_CONTROL_MODE=true         # Monitoring enabled
WF7_ENABLE_JS_RENDERING=false              # WF7 specific
```

### Consequences of Enabling
- One enabled premium feature = 5-25x increase in charges
- Multiple enabled = compounding costs
- Only enable if budget allows and explicitly needed

### Recommendation
NEVER enable premium features without explicit approval and monitoring setup.

---

## Tenant Isolation Status

**REMOVED AND NOT TO BE RE-ADDED**

- Tenant isolation: REMOVED
- RBAC (Role-Based Access Control): REMOVED
- Multi-tenant features: REMOVED
- System now single-tenant by design
- DEFAULT_TENANT_ID used for all requests

Do NOT attempt to re-add tenant features without full architectural review.

---

## Known Issues & Workarounds

### Issue 1: Logging Configuration
**Status**: Hardcoded to DEBUG level, ignores LOG_LEVEL env var
**Impact**: Can't control log verbosity from environment
**Workaround**: Edit src/config/logging_config.py or use improved version in CONFIGURATION_CODE_EXAMPLES.md

### Issue 2: Configuration Mismatch
**Status**: docker-compose.yml, .env.example, and settings.py have different scheduler values
**Impact**: Unclear which values are actually used
**Workaround**: Verify in logs on startup; prefer environment variables

### Issue 3: Optional Keys Risk
**Status**: Many optional settings could cause runtime failures
**Impact**: Missing SCRAPER_API_KEY will break scraping features
**Workaround**: Validate required keys on startup

### Issue 4: Database Connection Fallback
**Status**: Multiple connection methods with implicit fallback
**Impact**: Unclear which method is active
**Workaround**: Check startup logs for connection method used

---

## Testing Configuration

### Health Check Endpoints
```bash
# Basic health
curl http://localhost:8000/health

# Database health
curl http://localhost:8000/health/database

# Debug routes (dev only)
curl http://localhost:8000/debug/routes
curl http://localhost:8000/debug/loaded-src-files
```

### Configuration Validation in Code
```python
from src.config.settings import settings

# Validate critical settings
if not settings.supabase_url:
    raise ValueError("SUPABASE_URL not configured")

if settings.environment == "production":
    settings.validate()  # Validate production requirements
```

---

## Files to Review

### For Understanding Current Configuration
1. `/home/user/scrapersky-backend/src/config/settings.py` - Complete settings definition
2. `/home/user/scrapersky-backend/.env.example` - All available variables
3. `/home/user/scrapersky-backend/CLAUDE.md` - Project guidelines

### For Understanding Database Setup
1. `/home/user/scrapersky-backend/src/session/async_session.py` - Async session management
2. `/home/user/scrapersky-backend/src/db/engine.py` - Engine creation
3. `/home/user/scrapersky-backend/src/auth/jwt_auth.py` - JWT configuration

### For Understanding Deployment
1. `/home/user/scrapersky-backend/Dockerfile` - Container build
2. `/home/user/scrapersky-backend/docker-compose.yml` - Dev environment
3. `/home/user/scrapersky-backend/docker-compose.prod.yml` - Production environment
4. `/home/user/scrapersky-backend/render.yaml` - Render.com deployment
5. `/home/user/scrapersky-backend/k8s/deployment.yaml` - Kubernetes deployment

---

## Environment Variable Defaults Summary

```python
# Database
DB_MIN_POOL_SIZE = 1
DB_MAX_POOL_SIZE = 10
DB_CONNECTION_TIMEOUT = 30
SUPABASE_DB_NAME = "postgres"

# Schedulers (all interval=1 minute)
DOMAIN_SCHEDULER_BATCH_SIZE = 50
DOMAIN_SCHEDULER_MAX_INSTANCES = 3
SITEMAP_SCHEDULER_BATCH_SIZE = 25
SITEMAP_SCHEDULER_MAX_INSTANCES = 3
DOMAIN_SITEMAP_SCHEDULER_BATCH_SIZE = 10
SITEMAP_IMPORT_SCHEDULER_BATCH_SIZE = 20
SITEMAP_IMPORT_SCHEDULER_MAX_INSTANCES = 1
PAGE_CURATION_SCHEDULER_BATCH_SIZE = 10
PAGE_CURATION_SCHEDULER_MAX_INSTANCES = 1

# Application
PORT = 8000
HOST = 0.0.0.0
MAX_WORKERS = 4
ENVIRONMENT = "development"
CORS_ORIGINS = "*"
LOG_LEVEL = "INFO"
CACHE_TTL = 3600

# Diagnostic
DIAGNOSTIC_DIR = "/tmp/scraper_sky_scheduler_diagnostics"

# User IDs
SYSTEM_USER_ID = "00000000-0000-0000-0000-000000000000"
DEFAULT_TENANT_ID = "550e8400-e29b-41d4-a716-446655440000"
DEVELOPMENT_USER_ID = [generated UUID]

# Cost Control (all safe defaults)
SCRAPER_API_ENABLE_PREMIUM = false
SCRAPER_API_ENABLE_JS_RENDERING = false
SCRAPER_API_ENABLE_GEOTARGETING = false
SCRAPER_API_MAX_RETRIES = 1
SCRAPER_API_COST_CONTROL_MODE = true
WF7_ENABLE_JS_RENDERING = false
```

---

## Additional Resources

See the following files for more detailed information:

- **CONFIGURATION_ANALYSIS.md** - Full analysis with all details
- **CONFIGURATION_CODE_EXAMPLES.md** - Code snippets and patterns
- **CLAUDE.md** - Project guidelines and architecture
- **src/config/settings.py** - Source of truth for all settings

