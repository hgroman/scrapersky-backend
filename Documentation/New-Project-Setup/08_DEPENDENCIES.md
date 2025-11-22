# Dependencies Reference

**Document:** 08_DEPENDENCIES.md  
**Type:** Reference  
**Purpose:** Complete requirements.txt with explanations

---

## Complete requirements.txt

```txt
# Core FastAPI Stack
fastapi==0.115.8          # Web framework
uvicorn==0.34.0           # ASGI server
pydantic==2.10.6          # Data validation
pydantic-settings==2.7.1  # Settings management
starlette==0.40.0         # ASGI toolkit (FastAPI dependency)

# Database - Async PostgreSQL
SQLAlchemy==2.0.38        # ORM
asyncpg==0.30.0           # Async PostgreSQL driver
psycopg[binary]==3.2.5    # Sync PostgreSQL driver (migrations)
greenlet==3.1.1           # Async support for SQLAlchemy

# HTTP Clients
aiohttp>=3.9.3            # Async HTTP client
httpx                     # Modern HTTP client
requests==2.32.3          # Sync HTTP client

# Supabase
supabase                  # Supabase Python client

# Authentication & Security
PyJWT==2.10.1             # JWT tokens
python-jose==3.3.0        # JWT encoding/decoding
cryptography==44.0.2      # Cryptographic recipes

# Utilities
python-dotenv==1.0.0      # Load .env files
PyYAML==6.0.2             # YAML parsing
orjson==3.10.15           # Fast JSON serialization
tenacity==8.2.3           # Retry logic
validators==0.20.0        # Data validation
email-validator==2.2.0    # Email validation
python-multipart==0.0.6   # Form data parsing

# Web Scraping (Optional)
beautifulsoup4==4.13.3    # HTML parsing
lxml>=5.2.2               # XML/HTML parser

# Background Tasks
APScheduler==3.10.4       # Task scheduling

# Testing
pytest==7.4.3             # Testing framework
pytest-asyncio==0.21.1    # Async test support
pytest-cov==4.1.0         # Coverage reporting

# Development
black==23.12.1            # Code formatting
flake8==6.1.0             # Linting
mypy==1.7.1               # Type checking
```

---

## Package Explanations

### Core Framework

**fastapi** - Modern async web framework
- Auto-generated OpenAPI docs
- Built-in validation with Pydantic
- High performance

**uvicorn** - Lightning-fast ASGI server
- Production-ready
- Auto-reload in development
- WebSocket support

**pydantic** - Data validation using Python type hints
- Runtime type checking
- JSON schema generation
- Settings management

### Database

**SQLAlchemy 2.0** - Modern async ORM
- Full async support
- Type hints
- Relationship management

**asyncpg** - Fastest PostgreSQL driver for Python
- Pure async
- Prepared statements
- Connection pooling

**psycopg[binary]** - Sync PostgreSQL driver
- Used for migrations
- Alembic compatibility
- Python 3.13 compatible

### Authentication

**PyJWT** - JSON Web Token implementation
- Token generation
- Token verification
- Standard compliant

**python-jose** - JOSE implementation
- JWT encoding/decoding
- JWS/JWE support

**cryptography** - Cryptographic recipes
- Password hashing
- Encryption
- Key generation

### Background Tasks

**APScheduler** - Advanced Python Scheduler
- Cron-like scheduling
- Interval-based jobs
- Persistent job stores

### Testing

**pytest** - Modern testing framework
- Fixtures
- Parametrization
- Plugin ecosystem

**pytest-asyncio** - Async test support
- Async fixtures
- Event loop management

---

## Optional Dependencies

### For API Integrations

```txt
googlemaps==4.10.0        # Google Maps API
openai                    # OpenAI API
```

### For Scraping

```txt
scraperapi-sdk==1.5.3     # ScraperAPI client
selenium==4.15.0          # Browser automation
playwright==1.40.0        # Modern browser automation
```

### For Monitoring

```txt
sentry-sdk==1.39.0        # Error tracking
prometheus-client==0.19.0 # Metrics
```

---

## Version Pinning Strategy

**Exact versions** for:
- Core framework (FastAPI, SQLAlchemy)
- Database drivers (asyncpg, psycopg)
- Security packages (cryptography, PyJWT)

**Minimum versions** for:
- HTTP clients (aiohttp, httpx)
- Utilities (lxml)

**Why:** Balance stability with security updates

---

## Installation

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Verify installation
pip list
```

---

## Updating Dependencies

```bash
# Check for updates
pip list --outdated

# Update specific package
pip install --upgrade package-name

# Update requirements.txt
pip freeze > requirements.txt
```

---

**Status:** ✅ Dependencies documented
