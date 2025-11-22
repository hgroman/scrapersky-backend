# Environment Variables Reference

**Document:** 09_ENVIRONMENT_VARIABLES.md  
**Type:** Reference  
**Purpose:** Complete .env template with explanations

---

## Complete .env Template

```bash
# ============================================================================
# APPLICATION SETTINGS
# ============================================================================

ENVIRONMENT=development                    # development | staging | production
HOST=0.0.0.0                              # Bind address
PORT=8000                                 # Port number
LOG_LEVEL=INFO                            # DEBUG | INFO | WARNING | ERROR

# ============================================================================
# SUPABASE CORE CONFIGURATION
# ============================================================================

SUPABASE_URL=https://{project-ref}.supabase.co
SUPABASE_ANON_KEY=eyJhbGc...               # Public anon key
SUPABASE_SERVICE_ROLE_KEY=eyJhbGc...      # Secret service role key
SUPABASE_DB_PASSWORD=your-db-password     # Database password
SUPABASE_JWT_SECRET=your-jwt-secret       # JWT secret for token verification

# ============================================================================
# SUPABASE CONNECTION POOLER (SUPAVISOR) - RECOMMENDED
# ============================================================================

SUPABASE_POOLER_HOST=aws-0-{region}.pooler.supabase.com
SUPABASE_POOLER_PORT=6543                 # Pooler port (always 6543)
SUPABASE_POOLER_USER=postgres.{project-ref}
SUPABASE_POOLER_PASSWORD=your-db-password # Same as SUPABASE_DB_PASSWORD

# ============================================================================
# SUPABASE DIRECT CONNECTION (FALLBACK)
# ============================================================================

SUPABASE_DB_HOST=db.{project-ref}.supabase.co
SUPABASE_DB_PORT=5432                     # Direct connection port
SUPABASE_DB_USER=postgres.{project-ref}
SUPABASE_DB_NAME=postgres                 # Default database name

# ============================================================================
# DATABASE POOL SETTINGS
# ============================================================================

DB_MIN_POOL_SIZE=1                        # Minimum connections in pool
DB_MAX_POOL_SIZE=10                       # Maximum connections in pool
DB_CONNECTION_TIMEOUT=30                  # Connection timeout (seconds)

# ============================================================================
# CORS CONFIGURATION
# ============================================================================

# Development: Allow all origins
CORS_ORIGINS=*

# Production: Specific origins (comma-separated or JSON array)
# CORS_ORIGINS=https://your-app.vercel.app,https://your-domain.com
# CORS_ORIGINS=["https://your-app.vercel.app","https://your-domain.com"]

# ============================================================================
# EXTERNAL API KEYS (Optional)
# ============================================================================

# Google Maps API
GOOGLE_MAPS_API_KEY=your-google-maps-api-key

# OpenAI API
OPENAI_API_KEY=sk-your-openai-api-key

# ScraperAPI
SCRAPER_API_KEY=your-scraper-api-key

# ============================================================================
# SCHEDULER SETTINGS (Optional)
# ============================================================================

# Example: Data processing scheduler
DATA_PROCESSING_SCHEDULER_INTERVAL_MINUTES=5
DATA_PROCESSING_SCHEDULER_BATCH_SIZE=10
DATA_PROCESSING_SCHEDULER_MAX_INSTANCES=1

# ============================================================================
# FEATURE FLAGS (Optional)
# ============================================================================

ENABLE_BACKGROUND_TASKS=true
ENABLE_EMAIL_NOTIFICATIONS=false
ENABLE_ANALYTICS=true

# ============================================================================
# MONITORING & LOGGING (Optional)
# ============================================================================

SENTRY_DSN=https://your-sentry-dsn
LOG_FILE_PATH=logs/app.log
ENABLE_PERFORMANCE_MONITORING=false
```

---

## Variable Explanations

### Application Settings

**ENVIRONMENT**
- `development` - Local development
- `staging` - Staging environment
- `production` - Production environment

**LOG_LEVEL**
- `DEBUG` - Verbose logging (development)
- `INFO` - Standard logging (production)
- `WARNING` - Warnings only
- `ERROR` - Errors only

### Supabase Configuration

**SUPABASE_URL**
- Format: `https://{project-ref}.supabase.co`
- Get from: Supabase Dashboard → Settings → API

**SUPABASE_ANON_KEY**
- Public key for client-side requests
- Safe to expose in frontend
- Get from: Supabase Dashboard → Settings → API

**SUPABASE_SERVICE_ROLE_KEY**
- Secret key with full database access
- NEVER expose in frontend
- Use only in backend
- Get from: Supabase Dashboard → Settings → API

**SUPABASE_DB_PASSWORD**
- Database password set during project creation
- Required for direct database connections
- Get from: Supabase Dashboard → Settings → Database

### Connection Pooler (Supavisor)

**Why use pooler:**
- Better performance
- Connection reuse
- Handles connection limits
- Required for production

**SUPABASE_POOLER_HOST**
- Format: `aws-0-{region}.pooler.supabase.com`
- Region examples: `us-east-1`, `eu-west-1`
- Get from: Supabase Dashboard → Settings → Database → Connection Pooling

**SUPABASE_POOLER_PORT**
- Always `6543` for Supavisor
- Different from direct connection port (5432)

### Database Pool Settings

**DB_MIN_POOL_SIZE**
- Minimum connections kept open
- Development: 1
- Production: 5-10

**DB_MAX_POOL_SIZE**
- Maximum connections allowed
- Development: 10
- Production: 20-50 (based on Supabase plan)

**DB_CONNECTION_TIMEOUT**
- Seconds to wait for connection
- Default: 30
- Increase for slow networks

### CORS Configuration

**Development:**
```bash
CORS_ORIGINS=*
```

**Production (comma-separated):**
```bash
CORS_ORIGINS=https://app.example.com,https://www.example.com
```

**Production (JSON array):**
```bash
CORS_ORIGINS=["https://app.example.com","https://www.example.com"]
```

---

## Security Best Practices

### Never Commit .env

```bash
# .gitignore should include:
.env
.env.local
.env.*.local
```

### Use .env.example

```bash
# Create template without secrets
cp .env .env.example

# Remove actual values
# Commit .env.example to repository
```

### Rotate Secrets Regularly

- Database passwords: Every 90 days
- API keys: When compromised
- JWT secrets: When compromised

### Environment-Specific Files

```bash
.env.development    # Local development
.env.staging        # Staging environment
.env.production     # Production environment
```

---

## Loading Environment Variables

### In Application

```python
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    environment: str = "development"
    supabase_url: str
    supabase_db_password: str
    
    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=False
    )

settings = Settings()
```

### In Docker

```yaml
# docker-compose.yml
services:
  app:
    env_file:
      - .env
    environment:
      - ENVIRONMENT=production
```

### In Render

Add via dashboard:
1. Go to Environment tab
2. Click "Add Environment Variable"
3. Paste key-value pairs

---

## Verification

```bash
# Check if .env is loaded
python -c "from src.config.settings import settings; print(settings.supabase_url)"

# Should print your Supabase URL
```

---

**Status:** ✅ Environment variables documented
