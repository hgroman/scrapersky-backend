# ScraperSky Backend Configuration & Environment Analysis

## Table of Contents
1. [Settings Structure & Patterns](#settings-structure--patterns)
2. [Environment Variables by Category](#environment-variables-by-category)
3. [Deployment Configuration](#deployment-configuration)
4. [Logging Configuration](#logging-configuration)
5. [Configuration Best Practices & Concerns](#configuration-best-practices--concerns)

---

## Settings Structure & Patterns

### Framework & Location
- **File**: `/home/user/scrapersky-backend/src/config/settings.py`
- **Framework**: Pydantic V2 with `BaseSettings` and `SettingsConfigDict`
- **Load Source**: Environment variables from `.env` file (case-insensitive)
- **Configuration Pattern**: `SettingsConfigDict(env_file=".env", case_sensitive=False, extra="allow")`

### Key Settings Class Features

#### 1. **Singleton Pattern**
```python
settings = Settings()  # Global instance created at module import
```
The settings instance is imported throughout the application and used as a singleton.

#### 2. **Optional vs Required Settings**
- Most settings are **Optional[str]** - only fail during specific operational contexts
- Database settings are built with fallbacks
- Production environment has explicit validation via `validate()` method

#### 3. **Instance Methods**
- `get_cors_origins()`: Parses CORS configuration (JSON array or comma-separated)
- `redacted_database_url()`: Returns password-masked database URL for safe logging
- `validate()`: Validates production-specific requirements

#### 4. **Pydantic Configuration**
- Case-insensitive environment variable matching
- Extra fields allowed (extra="allow")
- Loads from `.env` file if present

---

## Environment Variables by Category

### A. DATABASE CONNECTION (Critical - Supavisor Required)

#### Connection String Variants
```
Method 1: Individual Supabase Components
  SUPABASE_URL                    - Supabase project URL
  SUPABASE_DB_PASSWORD            - Database password
  SUPABASE_DB_HOST               - Direct database host (backup)
  SUPABASE_DB_PORT               - Direct database port (backup)
  SUPABASE_DB_USER               - Direct database user (backup)
  SUPABASE_DB_NAME              - Database name (default: "postgres")

Method 2: Supabase Pooler (Recommended - Supavisor)
  SUPABASE_POOLER_HOST           - Pooler host (e.g., region.pooler.supabase.co)
  SUPABASE_POOLER_PORT           - Pooler port (usually 6543)
  SUPABASE_POOLER_USER           - Pooler user (format: user_supabase_pooler)
  SUPABASE_POOLER_PASSWORD       - Pooler password

Method 3: Full Database URL
  DATABASE_URL                   - Complete PostgreSQL URL
                                 Format: postgresql+asyncpg://user:pass@host:port/dbname
```

#### CRITICAL - Supavisor Connection Parameters (NON-NEGOTIABLE)
```
These are MANDATORY and built into connection strings:
  raw_sql=true               - Use raw SQL instead of ORM
  no_prepare=true            - Disable prepared statements (Supavisor compatibility)
  statement_cache_size=0     - Prevent caching issues with connection pooling
```

**Implementation**:
- Applied in `src/session/async_session.py` (line 183-187)
- Applied in `src/db/engine.py` (line 187-191)
- Enforced via `execution_options` and `connect_args`

#### Connection Pool Settings
```python
DB_MIN_POOL_SIZE           int  Default: 1
DB_MAX_POOL_SIZE           int  Default: 10
DB_CONNECTION_TIMEOUT      int  Default: 30 seconds
                                (Increased to 60s in docker-compose.yml for long operations)
```

#### Supabase Project Keys
```
SUPABASE_ANON_KEY                - Anonymous/public key (for client SDK)
SUPABASE_SERVICE_ROLE_KEY        - Admin/server key (for backend)
SUPABASE_JWT_SECRET              - Secret for signing JWT tokens
```

---

### B. AUTHENTICATION & SECURITY

#### JWT Settings
```
JWT_SECRET_KEY             string (REQUIRED)
                          - Must be set in environment (no default)
                          - Application WILL NOT START without this
                          - Used for signing/verifying JWT tokens
                          - Algorithm: HS256

JWT_EXPIRE_MINUTES        int  Default: 30 minutes
                          - Configurable token expiration

DEV_TOKEN                 string Optional
                          - Internal/dev API calls token
                          - Default in settings: undefined
                          - Docker-compose sets: "scraper_sky_2024"
```

#### User & Tenant IDs (After Tenant Isolation Removal)
```
DEVELOPMENT_USER_ID       UUID  Default: Generated via uuid.uuid4()
                          - Used for dev API calls

SYSTEM_USER_ID            UUID  Default: "00000000-0000-0000-0000-000000000000"
                          - System-level operations

DEFAULT_TENANT_ID         UUID  Default: "550e8400-e29b-41d4-a716-446655440000"
                          - Default tenant for requests (singleton now)

DEV_USER_ID               UUID Optional
                          - Specific development user override
```

**Important**: Tenant isolation, RBAC, and multi-tenant features have been EXPLICITLY REMOVED.

---

### C. EXTERNAL API KEYS

#### Premium/Expensive Services (Cost Control Flags Added)
```
SCRAPER_API_KEY                   string Optional
                                 - ScraperAPI API key for web scraping
                                 - Cost control is CRITICAL for this API

SCRAPER_API_ENABLE_PREMIUM       bool  Default: false
                                 - Enables premium features (5-10x cost multiplier)
                                 
SCRAPER_API_ENABLE_JS_RENDERING  bool  Default: false
                                 - Enables JavaScript rendering (10-25x cost multiplier)
                                 
SCRAPER_API_ENABLE_GEOTARGETING  bool  Default: false
                                 - Enables geotargeting (2-3x cost multiplier)
                                 
SCRAPER_API_MAX_RETRIES          int  Default: 1 (reduced from default 3)
                                 - Minimize costly retries
                                 
SCRAPER_API_COST_CONTROL_MODE    bool  Default: true
                                 - Enable cost monitoring and alerts
                                 
WF7_ENABLE_JS_RENDERING          bool  Default: false
                                 - Workflow 7 specific JS rendering flag
```

#### Google Maps API
```
GOOGLE_MAPS_API_KEY               string Optional
                                 - Google Maps API key for location services
```

#### Removed APIs
```
OPENAI_API_KEY              REMOVED - No longer used
LANGCHAIN_API_KEY           REMOVED - No longer used
LANGCHAIN_TRACING_V2        REMOVED - No longer used
LANGCHAIN_ENDPOINT          REMOVED - No longer used
LANGCHAIN_PROJECT           REMOVED - No longer used
```

---

### D. MAUTIC CRM INTEGRATION (Optional)
```
MAUTIC_BASE_URL             string Optional  - Base URL of Mautic instance
MAUTIC_CLIENT_ID            string Optional  - OAuth client ID
MAUTIC_CLIENT_SECRET        string Optional  - OAuth client secret
```

---

### E. GOOGLE CLOUD PLATFORM (Optional)
```
GCP_PROJECT_ID                    string Optional  - GCP project ID
GCP_SERVICE_ACCOUNT_EMAIL         string Optional  - Service account email
GCP_SERVICE_ACCOUNT_PRIVATE_KEY   string Optional  - Private key (escaped newlines)
GCP_SERVICE_ACCOUNT_TOKEN_URI     string Optional  Default: https://oauth2.googleapis.com/token
```

---

### F. SCHEDULER CONFIGURATION

#### Domain Scheduler (WF4)
```
DOMAIN_SCHEDULER_INTERVAL_MINUTES      int  Default: 1 minute
                                      - How often scheduler runs
                                      
DOMAIN_SCHEDULER_BATCH_SIZE           int  Default: 50
                                      - Increased from 10 for better throughput
                                      
DOMAIN_SCHEDULER_MAX_INSTANCES        int  Default: 3
                                      - Increased from 1 for parallel processing
```

#### Sitemap Scheduler (WF2, WF3, WF5)
```
SITEMAP_SCHEDULER_INTERVAL_MINUTES     int  Default: 1 minute
                                      - Changed from 5 to match domain scheduler
                                      
SITEMAP_SCHEDULER_BATCH_SIZE          int  Default: 25
                                      - Increased from 5
                                      
SITEMAP_SCHEDULER_MAX_INSTANCES       int  Default: 3
                                      - Increased from 1
```

#### Domain Sitemap Submission Scheduler (New)
```
DOMAIN_SITEMAP_SCHEDULER_INTERVAL_MINUTES   int  Default: 1 minute

DOMAIN_SITEMAP_SCHEDULER_BATCH_SIZE        int  Default: 10
```

#### Sitemap Import Scheduler (WF6 - Renamed from Deep Scrape)
```
SITEMAP_IMPORT_SCHEDULER_INTERVAL_MINUTES    int  Default: 1 minute

SITEMAP_IMPORT_SCHEDULER_BATCH_SIZE         int  Default: 20

SITEMAP_IMPORT_SCHEDULER_MAX_INSTANCES      int  Default: 1
```

#### Page Curation Scheduler (WF7 - V2)
```
PAGE_CURATION_SCHEDULER_INTERVAL_MINUTES     int  Default: 1 minute

PAGE_CURATION_SCHEDULER_BATCH_SIZE          int  Default: 10

PAGE_CURATION_SCHEDULER_MAX_INSTANCES       int  Default: 1
```

---

### G. APPLICATION SETTINGS

#### Server Configuration
```
PORT                    int     Default: 8000
                       - Server port for Uvicorn

HOST                    str     Default: "0.0.0.0"
                       - Server bind address

MAX_WORKERS             int     Default: 4
                       - Uvicorn worker processes

ENVIRONMENT             str     Default: "development"
                       - Values: "development", "production", "staging"
                       - Affects validation and logging behavior

UVICORN_RELOAD          bool    Default: false (set in docker-compose)
                       - Hot reload for development
                       - Disabled in production
```

#### CORS Configuration
```
CORS_ORIGINS            str     Default: "*"
                       - Can be:
                         * "*" for all origins
                         * JSON array: '["http://localhost:3000"]'
                         * Comma-separated: "http://localhost:3000,http://example.com"
                       - Parsed by get_cors_origins() method
```

#### User Agent
```
USER_AGENT              str     Default: Chrome 91 on Windows 10
                       - Used for web scraping requests
                       - Can be overridden for specific scenarios
```

#### Cache Settings
```
CACHE_TTL               int     Default: 3600 seconds (1 hour)
                       - Default time-to-live for cache entries
```

---

### H. LOGGING & DIAGNOSTICS

#### Logging
```
LOG_LEVEL               str     Default: "INFO"
                       - Levels: TRACE, DEBUG, INFO, WARNING, ERROR
                       - Docker-compose.yml sets "TRACE" for detailed logging

DIAGNOSTIC_DIR          str     Default: "/tmp/scraper_sky_scheduler_diagnostics"
                       - Directory for scheduler diagnostic output

ENABLE_IMPORT_TRACING   bool    Default: true (docker-compose)
                       - Enable import path logging
                       - Disables reload during tracing
```

#### Path Settings
```
BASE_DIR                Path    Optional
                       - Base directory for application (derived if not set)

STATIC_DIR              Path    Optional
                       - Static files directory (derived if not set)
```

---

### I. DEPRECATED/UNUSED SETTINGS

#### Storage
```
CHROMA_PERSIST_DIR      str     Default: "./chroma_data"
                       - NOT in Pydantic Settings (unclear if used)
                       - May be deprecated
```

---

## Configuration by Environment

### Development Environment

**Detected by**:
- `ENVIRONMENT=development` setting
- OR hostname pattern: localhost, dev, 127.0.0.1, 192.168.x.x, 10.x.x.x, 172.16.x.x, *.local

**Key Characteristics**:
```
- SSL certificate verification: DISABLED (easier local development)
- Pool size: 5 (smaller)
- Max overflow: 5
- Reload: Enabled by default
- Logging: TRACE level
- Health check start period: 10s
- Dev token: "scraper_sky_2024"
```

**Docker Compose File**: `/home/user/scrapersky-backend/docker-compose.yml`
- Single service: `scrapersky`
- Hot-reload via volume mounts
- Loads `.env` file
- Health check interval: 30s

### Production Environment

**Configuration**:
```
ENVIRONMENT=production
UVICORN_RELOAD=false
LOG_LEVEL=INFO (or WARNING)
```

**Key Characteristics**:
- SSL certificate verification: DISABLED (Supabase compatibility)
- Pool size: Uses `DB_MAX_POOL_SIZE` setting
- Max overflow: 10
- Reload: Disabled
- Health check start period: 30s (longer grace period)

**Docker Compose File**: `/home/user/scrapersky-backend/docker-compose.prod.yml`
```yaml
Environment Variables:
  ENVIRONMENT: production
  UVICORN_RELOAD: false

Resource Limits:
  Memory: 1024M limit, 256M reserved
  CPU: 0.5 limit, 0.25 reserved

Restart Policy: always

Health Check:
  Interval: 30s
  Timeout: 10s
  Retries: 3
  Start period: 30s
```

**Benefits**:
- Automatic backups (Supabase managed)
- Point-in-time recovery
- High availability
- Automatic scaling
- Security patches applied automatically

---

## Deployment Configuration

### Docker Setup

#### Dockerfile Structure (Multi-stage build)

**Stage 1: Builder**
- Base: `python:3.11-slim`
- Installs build essentials, curl, wget
- Creates non-root user (`myuser`)
- Installs Python dependencies to local user path
- Copies entire project

**Stage 2: Runtime**
- Base: `python:3.11-slim`
- Copies only necessary artifacts from builder
- Recreates non-root user
- Sets PATH and PYTHONPATH
- Disables reload: `UVICORN_RELOAD=false`
- Healthcheck: HTTP GET to `/health`

**Health Check**
```dockerfile
HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \
  CMD curl -f http://localhost:8000/health || exit 1
```

#### Docker Compose Development (`docker-compose.yml`)
```yaml
Service: scrapersky
Image: Built locally from ./Dockerfile
Ports: 8000:8000
Volumes:
  - ./src:/app/src (hot-reload)
  - ./static:/app/static
  - ./templates:/app/templates
Healthcheck:
  - Interval: 30s
  - Timeout: 10s
  - Retries: 3
  - Start period: 10s
```

#### Docker Compose Production (`docker-compose.prod.yml`)
```yaml
Service: scrapersky
Build:
  - Context: .
  - Dockerfile: ./Dockerfile
Image: scrapersky:v1
Ports: 8000:8000
Environment:
  - ENVIRONMENT=production
  - UVICORN_RELOAD=false
Restart: always
Healthcheck:
  - Interval: 30s
  - Timeout: 10s
  - Retries: 3
  - Start period: 30s (longer grace period)
Resources:
  - Memory limit: 1024M
  - Memory reservation: 256M
  - CPU limit: 0.5
  - CPU reservation: 0.25
```

### Render.com Configuration (`render.yaml`)

**Service Definition**:
```yaml
Type: web
Name: scrapersky
Environment: docker
Region: oregon (customizable)
Plan: starter
Docker Image: Built from ./Dockerfile

Health Check:
  Path: /health

Environment Variables:
  UVICORN_RELOAD: false
  SCRAPER_API_KEY: (sync: false - use Render env var)
  SUPABASE_URL: (sync: false)
  SUPABASE_SERVICE_ROLE_KEY: (sync: false)
  SUPABASE_DB_PASSWORD: (sync: false)

Auto Deploy: true
Instances: 1 (configurable)
```

**Key Note**: Variables with `sync: false` are provided via Render dashboard, not synced from `.env`.

### Kubernetes Configuration

#### Deployment (`k8s/deployment.yaml`)
```yaml
Replicas: 1 (adjustable)
Container Image: scrapersky:v1

Resources:
  Requests:
    - Memory: 256Mi
    - CPU: 250m
  Limits:
    - Memory: 512Mi
    - CPU: 500m

Probes:
  - Readiness: /health (initialDelay: 5s, period: 10s)
  - Liveness: /health (initialDelay: 15s, period: 20s)

Secrets:
  - Loaded from: scrapersky-secrets
  - Via secretRef
```

#### Service (`k8s/deployment.yaml`)
```yaml
Type: ClusterIP
Port: 80 (maps to 8000)
Selector: app: scrapersky
```

#### Ingress with TLS (`k8s/deployment.yaml`)
```yaml
Class: nginx
TLS Issuer: letsencrypt-prod
Domain: scrapersky.yourdomain.com (customize)

Annotations:
  - kubernetes.io/ingress.class: "nginx"
  - cert-manager.io/cluster-issuer: "letsencrypt-prod"

Rules:
  - Host: scrapersky.yourdomain.com
  - Path: /
  - Service: scrapersky:80
```

#### Secrets (`k8s/secrets.yaml`)
```yaml
Type: Opaque
Variables (from environment):
  - SCRAPER_API_KEY
  - SUPABASE_URL
  - SUPABASE_SERVICE_ROLE_KEY
  - SUPABASE_DB_PASSWORD
```

---

## Logging Configuration

### Location & Implementation
**File**: `/home/user/scrapersky-backend/src/config/logging_config.py`

### Current Setup
```python
def setup_logging():
    """Configures logging for the application."""
    
    Log Directory: logs/
    Log File: logs/app.log
    
    Configuration:
      - Level: DEBUG (hardcoded)
      - Format: "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
      - Handlers:
        1. StreamHandler (console output)
        2. FileHandler (logs/app.log)
```

### Issues Identified

1. **Log Level Hardcoded**: Currently hardcoded to `DEBUG`, ignoring `LOG_LEVEL` env var
2. **Settings Not Used**: Doesn't respect `settings.log_level` from configuration
3. **Limited Flexibility**: No rotating file handler (logs can grow unbounded)
4. **No Diagnostic Integration**: Doesn't use `DIAGNOSTIC_DIR` for scheduler diagnostics

### Logging in Application Code

**Module Setup** (in `src/main.py`):
```python
from .config.logging_config import setup_logging
setup_logging()  # Must be called FIRST
logger = logging.getLogger(__name__)
```

**Pattern Throughout Codebase**:
```python
logger = logging.getLogger(__name__)
logger.info("Starting up the ScraperSky API...")
logger.error(f"Failed to setup Domain scheduler: {e}", exc_info=True)
```

### Special Logging Features

#### Database Connection Logging
- Redacted passwords in logs (via `redacted_database_url()`)
- Logs Supavisor connection detection
- Logs SSL verification status
- Connection pool settings logged on engine creation

#### Scheduler Logging
- Scheduler jobs log their operations
- Diagnostic output saved to `DIAGNOSTIC_DIR`
- Import tracing available via `ENABLE_IMPORT_TRACING`

---

## Configuration Best Practices & Concerns

### CRITICAL REQUIREMENTS

#### 1. **Database Connection - MANDATORY**
```
Issue: Supavisor-only connection pooling
Solution: ALWAYS use these parameters:
  - raw_sql=true
  - no_prepare=true
  - statement_cache_size=0
  
Never:
  - Switch to different connection pooler (PgBouncer, etc.)
  - Use ORM for complex queries
  - Enable prepared statements
```

#### 2. **JWT Authentication - SECURITY CRITICAL**
```
Issue: Application will CRASH without JWT_SECRET_KEY
Solution: ALWAYS set before deployment
  export JWT_SECRET_KEY="your-very-long-random-secret"
  
Never:
  - Use default values
  - Commit to version control
  - Use weak/short secrets
  - Rotate without proper handling
```

### CONFIGURATION CONCERNS

#### 1. **ScraperAPI Cost Control - FINANCIAL RISK**
```
Current defaults are SAFE (premium features disabled)
But VERIFY these settings in production:
  SCRAPER_API_ENABLE_PREMIUM: false      (Critical!)
  SCRAPER_API_ENABLE_JS_RENDERING: false (Critical!)
  SCRAPER_API_ENABLE_GEOTARGETING: false (Critical!)
  SCRAPER_API_MAX_RETRIES: 1             (Minimize cost)
  
Cost Multipliers if enabled:
  Premium: 5-10x
  JS Rendering: 10-25x
  Geotargeting: 2-3x
  
Recommendation: Monitor actual API usage in production
```

#### 2. **Logging Configuration - INCOMPLETE**
```
Issue: Hardcoded DEBUG level, ignoring env vars
Concerns:
  - No log rotation (unbounded disk growth risk)
  - No level control from environment
  - Verbose logging in production
  
Recommendations:
  - Use RotatingFileHandler
  - Respect LOG_LEVEL environment variable
  - Different levels for dev vs production
  - Archive old logs
```

#### 3. **Tenant Isolation REMOVED**
```
Status: All tenant isolation, RBAC, and multi-tenant features removed
Implication:
  - System is now single-tenant by design
  - DEFAULT_TENANT_ID used for all requests
  - Do NOT re-add tenant features without full review
  - Authentication is simplified but less flexible
```

#### 4. **Database Connection Fallback Complexity**
```
Multiple connection methods with implicit fallback:
  Method 1: SUPABASE_POOLER_* (preferred)
  Method 2: SUPABASE_DB_* (fallback)
  Method 3: DATABASE_URL (fallback)
  
Concern: Unclear which is used without checking code
Recommendation:
  - Document which method is being used for each deployment
  - Log connection method during startup
  - Standardize on one method per environment
```

#### 5. **Optional Keys Risk**
```
Many optional settings could cause runtime failures:
  - SCRAPER_API_KEY (missing = feature fails)
  - GOOGLE_MAPS_API_KEY (missing = feature fails)
  - JWT_SECRET_KEY (missing = CRASH)

Recommendations:
  - Validate required keys on startup
  - Provide clear error messages
  - Document which features require which keys
  - Test in staging before production
```

### CONFIGURATION MISMATCHES

#### 1. **docker-compose.yml vs .env.example**
```
Discrepancy in Sitemap Scheduler:
  .env.example:
    SITEMAP_SCHEDULER_INTERVAL_MINUTES=1 (with comment about docker-compose having 1)
    SITEMAP_SCHEDULER_BATCH_SIZE=20
    
  docker-compose.yml:
    (Uses .env file - values unclear)
    
  settings.py:
    SITEMAP_SCHEDULER_INTERVAL_MINUTES=1
    SITEMAP_SCHEDULER_BATCH_SIZE=25
    
Recommendation: Align all three sources
```

#### 2. **LOG_LEVEL Not Respected**
```
.env.example:
  LOG_LEVEL=TRACE
  
settings.py:
  log_level: str = "INFO"
  
logging_config.py:
  logging.basicConfig(level=logging.DEBUG) # hardcoded!
  
Recommendation: Refactor logging_config.py to use settings.log_level
```

### ENVIRONMENT-SPECIFIC CONCERNS

#### Development
```
Strengths:
  - SSL disabled for easier local testing
  - Hot reload enabled
  - Verbose logging

Concerns:
  - Smaller connection pool (5 connections)
  - May not catch production issues
```

#### Production
```
Strengths:
  - Reload disabled
  - Larger connection pool (configurable)
  - Supabase managed backups

Concerns:
  - SSL still disabled (Supabase compatibility)
  - Single instance by default
  - No horizontal scaling configuration
  - Limited error handling without proper logging
```

#### Kubernetes
```
Strengths:
  - Declarative configuration
  - Auto-healing with liveness probes
  - Automatic TLS with cert-manager

Concerns:
  - Domain hardcoded (scrapersky.yourdomain.com)
  - Image tag hardcoded (scrapersky:v1)
  - Only 1 replica by default
  - No resource requests/limits for all resources
```

---

## Configuration Validation Checklist

### Before Development Deployment
- [ ] Copy `.env.example` to `.env`
- [ ] Set all SUPABASE_* variables
- [ ] Set JWT_SECRET_KEY to a strong random value
- [ ] Verify CORS_ORIGINS for dev environment
- [ ] Set optional API keys (SCRAPER_API_KEY, GOOGLE_MAPS_API_KEY)
- [ ] Verify scheduler intervals (should be 1 minute for dev)
- [ ] Test database connection: `docker compose up`
- [ ] Check health endpoint: `curl http://localhost:8000/health`

### Before Production Deployment
- [ ] Set ENVIRONMENT=production
- [ ] Verify all required keys are set
- [ ] Check SCRAPER_API cost control flags (all false)
- [ ] Review LOG_LEVEL (should be INFO or WARNING)
- [ ] Verify DB_MAX_POOL_SIZE for expected load
- [ ] Test database connection in staging first
- [ ] Validate database backups are enabled (Supabase)
- [ ] Set JWT_EXPIRE_MINUTES appropriately
- [ ] Review CORS_ORIGINS (should NOT be "*")
- [ ] Verify health check passes multiple times
- [ ] Check logs for any warnings on startup
- [ ] Test with real external API keys
- [ ] Monitor initial deployment for errors
- [ ] Verify scheduler jobs run without errors
- [ ] Check database connection pool usage

### Before Kubernetes Deployment
- [ ] Update domain in ingress configuration
- [ ] Update container image repository/tag
- [ ] Create k8s/secrets.yaml with actual values
- [ ] Verify cert-manager is installed
- [ ] Test DNS resolution for domain
- [ ] Verify resource requests/limits are appropriate
- [ ] Test health check endpoints
- [ ] Configure readiness/liveness probe thresholds
- [ ] Set up pod disruption budgets
- [ ] Enable horizontal pod autoscaling if needed

---

## Configuration Files Summary Table

| File | Purpose | Env Override | Auto-Load |
|------|---------|--------------|-----------|
| `src/config/settings.py` | Pydantic settings | env vars | Yes (.env) |
| `.env` | Local environment variables | Manual | Yes (auto-loaded) |
| `.env.example` | Documentation template | N/A | No (reference) |
| `docker-compose.yml` | Dev services | env vars | No (manual) |
| `docker-compose.prod.yml` | Production services | env vars | No (manual) |
| `render.yaml` | Render.com deployment | Render dashboard | No (Render) |
| `k8s/deployment.yaml` | K8s deployment | Kubernetes | No (kubectl) |
| `k8s/secrets.yaml` | K8s secrets | Kubernetes | No (kubectl) |
| `src/config/logging_config.py` | Logging setup | Hardcoded | Yes (import) |
| `Dockerfile` | Container build | N/A | No (docker build) |

---

## Key Takeaways

1. **Supavisor is mandatory** - all three connection parameters (raw_sql, no_prepare, statement_cache_size=0) must be present
2. **JWT_SECRET_KEY is critical** - application will not start without it
3. **Cost control for ScraperAPI is essential** - default settings are safe but need verification in production
4. **Logging needs improvement** - currently hardcoded DEBUG level, should respect environment configuration
5. **Database connection uses implicit fallback** - unclear which method is active without checking logs
6. **Configuration validated only for production** - development mode has looser requirements
7. **Multiple scheduler types with different purposes** - verify all are configured correctly for your use case
8. **Tenant isolation is removed** - system is now single-tenant by design

