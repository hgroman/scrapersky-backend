# ScraperSky Backend

A FastAPI-based web scraping and analytics system with modern SQLAlchemy integration, RBAC security, and multi-tenant architecture.

## ⚠️ CRITICAL ARCHITECTURAL REQUIREMENTS ⚠️

### 1. NEVER USE RAW SQL IN APPLICATION CODE

```
⚠️ ABSOLUTELY NON-NEGOTIABLE ⚠️
┌─────────────────────────────────────────────────────┐
│ NEVER USE RAW SQL IN APPLICATION CODE               │
│                                                     │
│ ✅ ALWAYS use ORM methods                           │
│ ❌ NEVER write raw SQL queries                      │
└─────────────────────────────────────────────────────┘
```

- **ALWAYS** use SQLAlchemy ORM methods for ALL database operations
- **NEVER** write raw SQL with `text()` or `session.execute()`
- Access data through model classes like `Domain`, `User`, etc.
- Use model methods like `update_from_metadata()` instead of raw queries

Violations of this principle have resulted in 8+ wasted debugging hours and failed deployments.

### 2. CONNECTION CONFIGURATION REQUIREMENTS

**Always use Supavisor connection pooling with these parameters:**

- Connection string: `postgresql+asyncpg://postgres.your-project:password@aws-0-us-west-1.pooler.supabase.com:6543/postgres`
- Required parameters in connection configuration ONLY:
  - `raw_sql=true` - For Supavisor compatibility
  - `no_prepare=true` - For Supavisor compatibility
  - `statement_cache_size=0` - For Supavisor compatibility

**IMPORTANT**: These parameters are ONLY for connection configuration, NOT permission to use raw SQL in your code.

### 3. MODEL REQUIREMENTS

- All SQLAlchemy models must match the database schema exactly
- Include proper relationship configurations

**Failure to follow these requirements will result in application failures and wasted debugging time.**

For more information, see [01-ABSOLUTE_ORM_REQUIREMENT.md](/Docs/Docs_1_AI_GUIDES/01-ABSOLUTE_ORM_REQUIREMENT.md)

## Database Setup

**IMPORTANT:** This project connects to an **external Supabase database**.

- **Configuration:** Connection details are configured via environment variables (typically loaded from a `.env` file based on `.env.example`). Ensure the following variables are set correctly:
  - `SUPABASE_URL`
  - `SUPABASE_POOLER_HOST` (Recommended for connection pooling)
  - `SUPABASE_POOLER_PORT`
  - `SUPABASE_POOLER_USER`
  - `SUPABASE_DB_PASSWORD`
  - `DATABASE_URL` (Often constructed from the Supabase variables)
- **Local Docker:** The `docker-compose.yml` file in this project **does not** define or manage a local database service. It only runs the application service (`scrapersky`) which connects to the external database specified in the environment variables.
- **Inspection:** To manually inspect the database schema or data, use the primary inspection script. See the "Database Tools" section below.

## Project Overview

ScraperSky provides a robust backend platform for website metadata extraction, with a focus on security, scalability, and maintainability. It features:

- **Modern FastAPI Architecture**: Asynchronous API endpoints with dependency injection
- **SQLAlchemy 2.0 Integration**: Type-safe database operations with async support
- **Multi-Tenant Design**: Complete tenant isolation across all endpoints
- **Role-Based Access Control**: Fine-grained permission system with feature flags
- **Containerized Deployment**: Docker-based development and production environments

### Application Workflow

The system follows a multi-stage pipeline for discovering and processing web data:

1.  **Business Discovery:** Initial business search via Google Maps API.
2.  **Business Curation:** User selects businesses for detailed fetch.
3.  **Domain Curation:** User selects domains for further processing.
4.  **Sitemap Discovery:** Find sitemaps for selected domains.
5.  **Sitemap Curation:** User selects sitemaps for deep scraping (page extraction).

Data progresses: `Google Search -> local_business table -> domain table -> sitemap_files table -> pages table`.

## Quick Start

### Local Development Testing

```bash
# Required Test Credentials
DEV_TOKEN=scraper_sky_2024
DEFAULT_TENANT_ID=550e8400-e29b-41d4-a716-446655440000

# Add to your .env file for local testing
ENVIRONMENT=development
```

These credentials are pre-configured in all test HTML files for local development.

**IMPORTANT**: While the `DEV_TOKEN` provides authentication, operations involving `created_by` or `updated_by` fields often require a valid user UUID to satisfy database foreign key constraints (e.g., `sitemap_files.updated_by` references `users.id`).

Use the specific test user UUIDs documented in [10-TEST_USER_INFORMATION.md](/Docs/Docs_1_AI_GUIDES/10-TEST_USER_INFORMATION.md) (like `5905e9fe-6c61-4694-b09a-6602017b000a`) for these operations, and ensure these users exist in your development database (they should be present by default). The `get_current_user` dependency in `src/auth/jwt_auth.py` is configured to map `DEV_TOKEN` to the primary test user UUID in development environments.

**Primary Development Interface:**

During active MVP development, the primary interface for testing backend functionality and workflows is `/static/scraper-sky-mvp.html`. This page consolidates various testing tabs related to core services like LocalMiner, ContentMap, etc., and should be used as the main entry point for interacting with the backend API via a UI. Refer to `Docs/Docs_0_Architecture_and_Status/0.1_ScraperSky_Architecture_Flow_and_Components.md` for a mapping of the tabs on this page to their corresponding backend services.

### Development Environment

```bash
# Clone the repository
git clone https://github.com/your-org/scraper-sky-backend.git
cd scraper-sky-backend

# Set up environment variables
cp .env.example .env
# Edit .env with your credentials

# Start development environment
docker-compose up -d

# Apply database migrations
docker-compose exec app supabase db push --linked

# Access API documentation
open http://localhost:8000/docs
```

### Testing

```bash
# Run all tests
pytest

# Run specific test modules
pytest tests/services/rbac/
```

## Project Structure

```
scraper-sky-backend/
├── src/                      # Application source code
│   ├── main.py               # Application entry point
│   ├── models/               # SQLAlchemy models
│   ├── routers/              # API route definitions
│   ├── services/             # Business logic
│   ├── auth/                 # Authentication & authorization
│   ├── db/                   # Database configuration
│   └── middleware/           # FastAPI middleware
├── tests/                    # Test suite
├── scripts/                  # Utility scripts
│   ├── batch/                # Batch processing scripts
│   ├── db/                   # Database tools
│   ├── fixes/                # Fix scripts
│   ├── maintenance/          # Maintenance tools
│   ├── migrations/           # Database migration helpers
│   ├── monitoring/           # Job and batch monitoring
│   ├── sitemap/              # Sitemap testing and analysis
│   ├── testing/              # Testing utilities
│   └── utility/              # Development utilities
├── examples/                 # Example implementations
├── supabase/                # Supabase configuration
│   └── migrations/         # SQL migration files
├── Docs/                     # Project documentation
└── static/                   # Static files
```

## CI / Tooling

We use a minimal approach to code quality tooling to maximize development velocity while still maintaining a clean codebase:

### Pre-commit Configuration

Only essential whitespace checks are enforced at commit time:

```yaml
repos:
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.5.0
    hooks:
      - id: end-of-file-fixer # Ensures files end with a newline
      - id: trailing-whitespace # Trims trailing whitespace
```

### Code Formatting

Code formatting is handled at the editor level rather than as a commit-blocking check:

- **IDE Integration**: Configure your editor to format on save using either Black or Ruff
- **Manual Formatting**: Run formatters manually before pushing code

### Code Quality

To maintain code quality without blocking development velocity:

- Code quality checks run in CI only (not at commit time)
- Critical database connection parameters are reviewed in code review
- Focus is on working code first, polishing second

> Note: This approach was implemented in Work Order 49.1 to maximize development velocity for MVP work. After MVP completion, the team may revisit and add more stringent checks.

## Key Features

### FastAPI Endpoints

The application provides API endpoints for:

- Website metadata extraction
- Role-based access control
- User and tenant management
- Feature flag management

### Database Integration

- **SQLAlchemy 2.0**: Uses the latest SQLAlchemy with async support
- **Connection Pooling**: Properly configured for Supabase
- **Migration Management**: Supabase MCP for database schema evolution
- **Prepared Statements**: The system uses SQLAlchemy ORM by default, but endpoints support multiple parameters to bypass prepared statements when needed:
  - `raw_sql=true` - Tells the backend to use raw SQL instead of ORM
  - `no_prepare=true` - Disables prepared statements
  - `statement_cache_size=0` - Sets the asyncpg statement cache size to 0
  - **Note**: All three parameters must be used together for the profiles endpoint

> **IMPORTANT**: The system exclusively uses Supavisor for connection pooling. Any PgBouncer configurations should be immediately flagged and removed as they are incompatible with our architecture.

### Authentication & Authorization

- **JWT Authentication**: Secure token-based auth
- **RBAC System**: Fine-grained permission management
- **Tenant Isolation**: Complete data separation between tenants

## Environment Configuration

Critical environment variables:

```bash
# Database Configuration
DATABASE_URL=postgresql+asyncpg://postgres.your-project:password@aws-0-us-west-1.pooler.supabase.com:6543/postgres

# Server Settings
PORT=8000
ENVIRONMENT=development

# Authentication
JWT_SECRET_KEY=your-secret-key
```

## Deployment

ScraperSky is deployed to Render.com using the configuration in `render.yaml`:

```bash
# Deploy to Render.com
render deploy
```

## Database Tools

The primary tool for manually inspecting the database (viewing schemas, data, enums) is `scripts/db/db_inspector.py`.

**How to Use:**

1.  Ensure you are in the project root directory.
2.  Ensure the required `SUPABASE_*` environment variables are set (e.g., loaded from your `.env` file).
3.  Run the script as a module:

```bash
# Show help and usage instructions
python -m scripts.db.db_inspector --help

# List all tables
python -m scripts.db.db_inspector

# Inspect a specific table (e.g., domains)
python -m scripts.db.db_inspector domains

# Inspect a table with filtering and limits
python -m scripts.db.db_inspector sitemap_files --where "status = 'Completed'" --limit 50
```

Refer to the extensive docstring within `scripts/db/db_inspector.py` for detailed argument explanations and more examples.

## Scheduler Configuration

### Domain Scheduler

The domain scheduler processes domains with 'pending' status and can be configured with the following environment variables (defaults set in `docker-compose.yml`):

```bash
# How often the scheduler runs (in minutes)
# Default: 1 minute (set for MVP development, consider increasing later)
DOMAIN_SCHEDULER_INTERVAL_MINUTES=${DOMAIN_SCHEDULER_INTERVAL_MINUTES:-1}

# Number of domains processed in each batch
# Default: 10
DOMAIN_SCHEDULER_BATCH_SIZE=${DOMAIN_SCHEDULER_BATCH_SIZE:-10}

# Maximum concurrent instances of the scheduler
# Default: 1 (Should generally remain 1)
DOMAIN_SCHEDULER_MAX_INSTANCES=${DOMAIN_SCHEDULER_MAX_INSTANCES:-1}
```

### Sitemap Scheduler

The sitemap scheduler processes domains with `sitemap_analysis_status = 'Queued'` and can be configured with the following environment variables (defaults set in `docker-compose.yml`):

```bash
# How often the scheduler runs (in minutes)
# Default: 1 minute (set for MVP development, consider increasing later)
SITEMAP_SCHEDULER_INTERVAL_MINUTES=${SITEMAP_SCHEDULER_INTERVAL_MINUTES:-1}

# Number of sitemaps processed in each batch
# Default: 20
SITEMAP_SCHEDULER_BATCH_SIZE=${SITEMAP_SCHEDULER_BATCH_SIZE:-20}

# Maximum concurrent instances of the scheduler
# Default: 1 (Should generally remain 1)
SITEMAP_SCHEDULER_MAX_INSTANCES=${SITEMAP_SCHEDULER_MAX_INSTANCES:-1}
```

**Usage Guidelines (Applies to both Schedulers):**

- **Interval Minutes**: Controls how frequently the scheduler runs. Lower values increase processing frequency but also increase load. Consider raising these intervals (e.g., to 5 or 15 minutes) after the MVP phase.
- **Batch Size**: Controls how many items are processed in each run. Adjust based on system performance and throughput needs.
- **Max Instances**: Should generally remain at 1 to prevent race conditions or duplicate processing unless the scheduler logic is specifically designed for concurrency.

These settings can be configured in the `.env` file or directly in the Docker environment variables to override the defaults.

## Development Tips

### Editor Configuration for Smooth Commits

To ensure pre-commit hooks for whitespace and newlines pass seamlessly without interrupting your workflow, add these settings to your VS Code/Cursor settings (`settings.json`):

```json
{
  // Ensure these settings are enabled:
  "files.trimTrailingWhitespace": true,
  "files.insertFinalNewline": true,
  "editor.formatOnSave": true // Optional but recommended if using a formatter
}
```

_Why?_ This automatically cleans files on save, preventing hook failures during commits.

### Committing Changes Effectively

- **Multi-line Messages**: Use VS Code's **Source Control Panel UI** (recommended) or run `git commit` (with no flags) in the terminal to open your configured editor. Avoid `git commit -m` for multi-line messages due to shell quoting complexities.
- **Bypassing Hooks**: If you absolutely need to bypass pre-commit checks (use sparingly, e.g., for WIP commits), use `git commit --no-verify` or the shorthand `git commit -n`.

### Handling Multi-line Git Commits

If you encounter issues committing multi-line messages directly (especially with special characters or quotes), you can use a temporary file:

```bash
# 1. Craft your commit message with printf, ensuring proper quoting and newlines (\\n)
printf 'Subject Line\\n\\nDetailed body explaining the change.\\n- Bullet point 1\\n- Bullet point 2\\n\\nCloses #issue_number\\n' > /tmp/commit_msg.txt

# 2. Commit using the temporary file. Use --no-verify if needed to bypass hooks.
git commit -F /tmp/commit_msg.txt # Add --no-verify if needed

# 3. (Optional) Remove the temporary file
rm /tmp/commit_msg.txt
```

This method ensures the message is passed to Git exactly as intended, avoiding shell interpretation issues.

## Documentation

For detailed documentation, see:

- [Project Architecture](/Docs/70.0-ScraperSky%20Backend%20Architecture%20Summary.md)
- [Database Standards](/Docs/72.0-Database-Connection-Standards.md)
- [RBAC Implementation](/Docs/70.13-RBAC-Reference-Implementation-Template.md)

## License

MIT
