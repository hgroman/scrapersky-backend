# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Development Commands

### Testing & Quality
```bash
# Run tests
pytest -q

# Lint and format code
ruff check .
ruff format .

# Run all pre-commit checks
pre-commit run --all-files
```

### Docker Development
```bash
# Start development stack
docker compose up --build

# View app logs
docker compose logs -f app

# Shutdown
docker compose down
```

### File System Audit
```bash
# Check for orphaned/phantom files
python tools/file_discovery.py
```

## Architecture Overview

ScraperSky is a multi-tenant FastAPI service for large-scale web metadata extraction. The system follows a layered architecture with clear separation of concerns:

### Core Layers
- **Models** (`src/models/`): SQLAlchemy models defining database schema
- **Routers** (`src/routers/`): FastAPI route handlers grouped by functionality
- **Services** (`src/services/`): Business logic and processing services
- **Database** (`src/db/`): Database connections and session management
- **Schedulers**: Background job processing using APScheduler

### Key Components

#### Database Architecture
- **Primary Database**: Supabase PostgreSQL with connection pooling via Supavisor (port 6543)
- **Connection Pattern**: Uses `postgresql+asyncpg://` with specific connection parameters:
  - `raw_sql=true` - Use raw SQL instead of ORM for complex queries
  - `no_prepare=true` - Disable prepared statements for Supavisor compatibility
  - `statement_cache_size=0` - Control statement caching
- **Session Management**: Async sessions via `src/session/async_session.py`

#### Background Processing
The system uses multiple schedulers for different workflows:
- **Domain Scheduler**: Processes domain discovery and analysis
- **Sitemap Scheduler**: Handles sitemap parsing and URL extraction
- **Domain Sitemap Submission Scheduler**: Manages sitemap-to-domain mapping
- **Sitemap Import Scheduler**: Processes deep sitemap content analysis

Each scheduler is configured via environment variables for interval, batch size, and max instances.

#### Service Architecture
Services are organized by domain:
- **Places Services** (`src/services/places/`): Google Maps API integration
- **Sitemap Services** (`src/services/sitemap/`): Sitemap analysis and processing
- **Batch Services** (`src/services/batch/`): Multi-domain batch processing
- **Page Scraper Services** (`src/services/page_scraper/`): Individual page analysis

### API Versioning
The API uses v3 endpoints with consistent naming:
- **Pattern**: `/api/v3/{resource}`
- **Example**: `/api/v3/google-maps-api/search/places`
- Router prefixes are either defined within routers (full `/api/v3/...` path) or added during inclusion

### Important Implementation Notes

#### Database Connection Requirements
**CRITICAL**: This system exclusively uses Supavisor for connection pooling. The connection parameters `raw_sql=true`, `no_prepare=true`, and `statement_cache_size=0` are mandatory and cannot be modified.

#### Authentication
- Uses JWT tokens for API authentication
- Dependency-based authentication pattern (not middleware-based)
- Development mode may bypass auth for some endpoints

#### Router Inclusion Pattern
When adding routers to `main.py`:
- If router defines full prefix including `/api/v3`, include without prefix
- If router only defines resource-specific prefix, include with `prefix="/api/v3"`
- Failure to follow this pattern causes 404 errors

#### Tenant Isolation Removed
The system has explicitly removed all tenant isolation, RBAC middleware, and multi-tenant features. Do not re-add tenant-related functionality.

### Vector Database Integration
The system includes semantic search capabilities:
- Use `Docs/Docs_18_Vector_Operations/Scripts/semantic_query_cli.py` for vector queries
- Never pass vector embeddings as raw strings in SQL queries
- Vector operations use dedicated PostgreSQL RPC functions

### Development Guidelines
- All schedulers use the shared scheduler instance from `scheduler_instance.py`
- Database transactions should use the async session pattern
- Static files are served from `/static` directory
- Comprehensive error handling with standardized JSON responses
- Logging configured via `src/config/logging_config.py`

### File Organization Patterns
- Models follow SQLAlchemy declarative patterns
- Services use dependency injection for database sessions  
- Routers group related endpoints with consistent error handling
- Configuration centralized in `src/config/settings.py`

## Environment Setup

Key environment variables (see `.env.example`):
- `SUPABASE_URL`, `SUPABASE_POOLER_HOST`, `SUPABASE_POOLER_PORT` - Database connection
- `SUPABASE_POOLER_USER`, `SUPABASE_DB_PASSWORD` - Database credentials
- `JWT_SECRET_KEY` - Authentication secret
- `GOOGLE_MAPS_API_KEY` - External API integration
- Scheduler configuration via `*_SCHEDULER_*` variables

## Testing Strategy
- Async-friendly tests using pytest
- Type checking with MyPy
- Database health checks available at `/health/database`
- Debug routes available for development (`/debug/routes`, `/debug/loaded-src-files`)