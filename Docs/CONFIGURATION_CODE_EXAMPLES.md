# Configuration Code Examples & Snippets

## Settings Class Structure

### Complete Settings Definition
**File**: `/home/user/scrapersky-backend/src/config/settings.py` (Lines 10-205)

```python
class Settings(BaseSettings):
    """
    Application settings using Pydantic BaseSettings.
    This reads values from environment variables matching the field names.
    """

    # Supabase Settings
    supabase_url: Optional[str] = None
    supabase_anon_key: Optional[str] = None
    supabase_service_role_key: Optional[str] = None
    supabase_db_password: Optional[str] = None
    supabase_jwt_secret: Optional[str] = None

    # Supabase Pooler Settings
    supabase_pooler_host: Optional[str] = None
    supabase_pooler_port: Optional[str] = None
    supabase_pooler_user: Optional[str] = None
    supabase_pooler_password: Optional[str] = None

    # Database Settings
    supabase_db_host: Optional[str] = None
    supabase_db_port: Optional[str] = None
    supabase_db_user: Optional[str] = None
    supabase_db_name: str = "postgres"
    database_url: Optional[str] = None

    # Database connection settings
    db_min_pool_size: int = 1
    db_max_pool_size: int = 10
    db_connection_timeout: int = 30

    # Diagnostic settings
    DIAGNOSTIC_DIR: str = "/tmp/scraper_sky_scheduler_diagnostics"

    # Domain Scheduler settings
    DOMAIN_SCHEDULER_INTERVAL_MINUTES: int = 1
    DOMAIN_SCHEDULER_BATCH_SIZE: int = 50
    DOMAIN_SCHEDULER_MAX_INSTANCES: int = 3

    # Sitemap Scheduler settings
    SITEMAP_SCHEDULER_INTERVAL_MINUTES: int = 1
    SITEMAP_SCHEDULER_BATCH_SIZE: int = 25
    SITEMAP_SCHEDULER_MAX_INSTANCES: int = 3

    # Domain Sitemap Submission Scheduler settings
    DOMAIN_SITEMAP_SCHEDULER_INTERVAL_MINUTES: int = 1
    DOMAIN_SITEMAP_SCHEDULER_BATCH_SIZE: int = 10

    # Sitemap Import Scheduler settings
    SITEMAP_IMPORT_SCHEDULER_INTERVAL_MINUTES: int = 1
    SITEMAP_IMPORT_SCHEDULER_BATCH_SIZE: int = 20
    SITEMAP_IMPORT_SCHEDULER_MAX_INSTANCES: int = 1

    # Page Curation Scheduler
    PAGE_CURATION_SCHEDULER_INTERVAL_MINUTES: int = 1
    PAGE_CURATION_SCHEDULER_BATCH_SIZE: int = 10
    PAGE_CURATION_SCHEDULER_MAX_INSTANCES: int = 1

    # External API Keys
    scraper_api_key: Optional[str] = None
    google_maps_api_key: Optional[str] = None

    # Mautic settings
    mautic_base_url: Optional[str] = None
    mautic_client_id: Optional[str] = None
    mautic_client_secret: Optional[str] = None

    # GCP settings
    gcp_project_id: Optional[str] = None
    gcp_service_account_email: Optional[str] = None
    gcp_service_account_private_key: Optional[str] = None
    gcp_service_account_token_uri: Optional[str] = None

    # Application Settings
    log_level: str = "INFO"
    port: int = 8000
    host: str = "0.0.0.0"
    max_workers: int = 4
    environment: str = "development"
    cors_origins: str = "*"
    user_agent: str = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36..."

    # User settings
    development_user_id: str = str(uuid.uuid4())
    system_user_id: str = "00000000-0000-0000-0000-000000000000"
    default_tenant_id: str = "550e8400-e29b-41d4-a716-446655440000"
    dev_user_id: Optional[str] = None
    dev_token: Optional[str] = None

    # Path settings
    base_dir: Optional[Path] = None
    static_dir: Optional[Path] = None

    # Cache settings
    cache_ttl: int = 3600

    model_config = SettingsConfigDict(
        env_file=".env", case_sensitive=False, extra="allow"
    )
```

### Key Instance Methods

#### 1. CORS Origins Parser
```python
def get_cors_origins(self) -> List[str]:
    """Get CORS origins as a list."""
    if self.cors_origins == "*":
        return ["*"]
    try:
        # Try to parse as JSON
        return json.loads(self.cors_origins)
    except json.JSONDecodeError:
        # Fallback to comma-separated list
        return [origin.strip() for origin in self.cors_origins.split(",")]
```

**Usage**:
```python
# In main.py
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.get_cors_origins(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

#### 2. Redacted Database URL for Logging
```python
def redacted_database_url(self) -> str:
    """Return a redacted version of the database URL for logging."""
    if self.database_url:
        # Create a redacted version of the URL that hides the password
        parts = self.database_url.split(":")
        if len(parts) >= 3:
            # Format: postgresql+asyncpg://user:password@host:port/dbname
            prefix = parts[0] + ":" + parts[1] + ":"
            remainder = ":".join(parts[2:])

            # Find password section
            if "@" in remainder:
                password_part = remainder.split("@")[0]
                host_part = "@" + remainder.split("@")[1]
                return prefix + "***REDACTED***" + host_part

        # Fallback if we can't parse properly
        return "postgresql+asyncpg://***REDACTED***"

    # If no database_url, show connection pattern
    if self.supabase_pooler_host:
        return f"postgresql+asyncpg://{self.supabase_pooler_user}:***REDACTED***@{self.supabase_pooler_host}:{self.supabase_pooler_port}/{self.supabase_db_name}"
    elif self.supabase_db_host:
        return f"postgresql+asyncpg://{self.supabase_db_user}:***REDACTED***@{self.supabase_db_host}:{self.supabase_db_port}/{self.supabase_db_name}"

    return "No database URL configured"
```

**Usage**:
```python
logger.info(f"Database URL: {settings.redacted_database_url()}")
```

#### 3. Production Validation
```python
def validate(self) -> None:
    """Validate the settings configuration."""
    # Check for required settings
    if self.environment == "production":
        assert self.supabase_url, "SUPABASE_URL is required in production"
        assert self.supabase_anon_key, "SUPABASE_ANON_KEY is required in production"
        assert self.supabase_service_role_key, (
            "SUPABASE_SERVICE_ROLE_KEY is required in production"
        )

    # Log warning if database credentials aren't set
    if (
        not self.supabase_db_host
        and not self.supabase_pooler_host
        and not self.database_url
    ):
        logging.warning("No database connection information provided!")
```

**Usage**:
```python
# In application startup
settings.validate()
```

---

## Database Connection Configuration

### Supavisor Connection Detection
**File**: `/home/user/scrapersky-backend/src/session/async_session.py` (Lines 67-134)

```python
def get_database_url() -> str:
    """
    Build a SQLAlchemy-compatible connection string from environment variables.
    Falls back to the original hardcoded string if environment variables are missing.
    """
    # Try to use environment variables first
    pooler_host = os.environ.get("SUPABASE_POOLER_HOST")
    pooler_port = os.environ.get("SUPABASE_POOLER_PORT")
    pooler_user = os.environ.get("SUPABASE_POOLER_USER")
    password = os.environ.get("SUPABASE_DB_PASSWORD")
    dbname = "postgres"  # Default database name for Supabase

    # Extract project reference from Supabase URL if available
    project_ref = None
    if settings.supabase_url:
        if "//" in settings.supabase_url:
            project_ref = settings.supabase_url.split("//")[1].split(".")[0]
        else:
            project_ref = settings.supabase_url.split(".")[0]

    # Check if all required env vars are available
    if all([pooler_host, pooler_port, pooler_user, password]):
        # Ensure password is a string before using quote_plus
        safe_password = str(password) if password is not None else ""

        # If pooler_user already includes project_ref, use it directly
        if pooler_user and "." in pooler_user:
            user_part = pooler_user
        # Otherwise, append project_ref if available
        elif project_ref:
            user_part = (
                f"{pooler_user}.{project_ref}"
                if pooler_user
                else f"postgres.{project_ref}"
            )
        else:
            user_part = pooler_user or "postgres"

        connection_string = (
            f"postgresql+asyncpg://{user_part}:{quote_plus(safe_password)}"
            f"@{pooler_host}:{pooler_port}/{dbname}"
        )
        logger.info(
            f"Using Supabase Supavisor connection pooler at {pooler_host}:{pooler_port}"
        )
        return connection_string

    # Raise an error if environment variables are missing
    raise ValueError(
        "Missing environment variables for database connection. "
        "Please set SUPABASE_POOLER_HOST, SUPABASE_POOLER_PORT, SUPABASE_POOLER_USER, "
        "and SUPABASE_DB_PASSWORD in your .env file."
    )
```

### Engine Creation with Supavisor Parameters
**File**: `/home/user/scrapersky-backend/src/session/async_session.py` (Lines 157-188)

```python
# Create connect_args with appropriate settings for Supavisor
connect_args = {
    "ssl": ssl_context,
    "timeout": settings.db_connection_timeout,
    # Generate unique prepared statement names for Supavisor compatibility
    "prepared_statement_name_func": lambda: f"__asyncpg_{uuid4()}__",
    # Required Supavisor connection parameters
    "server_settings": {"statement_cache_size": "0"},
    # Explicitly disable prepared statements for asyncpg 0.30.0
    "statement_cache_size": 0,
    "prepared_statement_cache_size": 0,
}

# Create async engine with environment-specific settings
engine = create_async_engine(
    DATABASE_URL,
    echo=False,  # Set to True for SQL query logging in development
    connect_args=connect_args,
    # Use a proper connection pool for Supavisor instead of NullPool
    pool_size=5 if IS_DEVELOPMENT else settings.db_max_pool_size,
    max_overflow=5 if IS_DEVELOPMENT else 10,
    pool_timeout=settings.db_connection_timeout,
    pool_recycle=1800,  # Recycle connections after 30 minutes
    # Apply Supavisor compatibility options at the engine level
    execution_options={
        "isolation_level": "READ COMMITTED",
        "no_prepare": True,
        "raw_sql": True,
    },
)
```

---

## Environment Detection

### Development vs Production Detection
**File**: `/home/user/scrapersky-backend/src/session/async_session.py` (Lines 32-64)

```python
def is_development_environment() -> bool:
    """
    Determine if the application is running in a development environment.

    Returns:
        True if running in development, False if in production
    """
    # Check explicit environment setting first
    if hasattr(settings, "environment") and settings.environment:
        return settings.environment.lower() in ("development", "dev", "local")

    # Check hostname
    hostname = socket.gethostname()
    is_dev = (
        "localhost" in hostname.lower()
        or "dev" in hostname.lower()
        or hostname == "127.0.0.1"
        or hostname.startswith("192.168.")
        or hostname.startswith("10.")
        or hostname.startswith("172.16.")
        or hostname.endswith(".local")
    )

    logger.info(
        f"Detected environment: {'Development' if is_dev else 'Production'} "
        f"based on hostname: {hostname}"
    )
    return is_dev
```

---

## JWT Authentication Configuration

### JWT Secret Key Enforcement
**File**: `/home/user/scrapersky-backend/src/auth/jwt_auth.py` (Lines 21-36)

```python
# --- JWT Configuration ---
# IMPORTANT: The application will NOT start if JWT_SECRET_KEY is not set in the environment.
# This is a security measure to prevent using a default/weak key.
try:
    SECRET_KEY = os.environ["JWT_SECRET_KEY"]
except KeyError:
    logger.error("FATAL: JWT_SECRET_KEY environment variable not set.")
    raise

ALGORITHM = "HS256"  # As per Supabase default
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("JWT_EXPIRE_MINUTES", "30"))

# Log the configuration on startup to aid debugging
logger.info(
    f"JWT Auth Initialized. Algorithm: {ALGORITHM}, Secret Key Hint: '{SECRET_KEY[:8]}...'."
)

# Default tenant for development/testing
DEFAULT_TENANT_ID = os.getenv(
    "DEFAULT_TENANT_ID", "550e8400-e29b-41d4-a716-446655440000"
)
```

---

## Logging Configuration

### Current Implementation
**File**: `/home/user/scrapersky-backend/src/config/logging_config.py`

```python
def setup_logging():
    """Configures logging for the application."""
    log_directory = "logs"
    log_file = os.path.join(log_directory, "app.log")

    # Ensure the log directory exists
    os.makedirs(log_directory, exist_ok=True)

    logging.basicConfig(
        level=logging.DEBUG,  # HARDCODED - Should use settings.log_level
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler(log_file),  # Use the variable here
        ],
    )
```

### Improved Implementation (Recommended)
```python
import logging
import os
from logging.handlers import RotatingFileHandler

def setup_logging():
    """Configures logging for the application with proper level handling."""
    from src.config.settings import settings
    
    log_directory = "logs"
    log_file = os.path.join(log_directory, "app.log")

    # Ensure the log directory exists
    os.makedirs(log_directory, exist_ok=True)

    # Parse log level from settings
    log_level_map = {
        "TRACE": logging.DEBUG,  # No TRACE in Python logging
        "DEBUG": logging.DEBUG,
        "INFO": logging.INFO,
        "WARNING": logging.WARNING,
        "ERROR": logging.ERROR,
    }
    level = log_level_map.get(settings.log_level.upper(), logging.INFO)

    # Create rotating file handler
    file_handler = RotatingFileHandler(
        log_file,
        maxBytes=10 * 1024 * 1024,  # 10MB
        backupCount=5
    )

    logging.basicConfig(
        level=level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.StreamHandler(),  # Console output
            file_handler,  # File output with rotation
        ],
    )
```

---

## Docker Configuration Examples

### Development Docker Compose Usage
**File**: `/home/user/scrapersky-backend/docker-compose.yml`

```yaml
services:
  scrapersky:
    build: .
    ports:
      - "8000:8000"
    env_file:
      - .env
    volumes:
      - ./src:/app/src        # Hot reload source
      - ./static:/app/static
      - ./templates:/app/templates
    healthcheck:
      test: [ "CMD", "curl", "-f", "http://localhost:8000/health" ]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 10s
```

**Start Development Environment**:
```bash
# Copy template
cp .env.example .env

# Edit .env with your settings
nano .env

# Start containers
docker compose up --build

# View logs
docker compose logs -f app

# Shutdown
docker compose down
```

### Production Docker Compose
**File**: `/home/user/scrapersky-backend/docker-compose.prod.yml`

```yaml
services:
  scrapersky:
    build:
      context: .
      dockerfile: Dockerfile
    image: scrapersky:v1
    ports:
      - "8000:8000"
    env_file:
      - ./.env
    environment:
      - ENVIRONMENT=production
      - UVICORN_RELOAD=false
    restart: always
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 30s
    deploy:
      resources:
        limits:
          memory: 1024M
          cpus: '0.5'
        reservations:
          memory: 256M
          cpus: '0.25'
```

---

## .env.example Template

### Complete Template
**File**: `/home/user/scrapersky-backend/.env.example` (Lines 1-116)

```bash
# ScraperSky Backend Environment Variables
# Copy this file to .env and fill in your actual values.

# --- Supabase & Database Configuration ---
# Core Supabase connection details
SUPABASE_URL=your_supabase_url_here
SUPABASE_ANON_KEY=your_supabase_anon_key_here
SUPABASE_SERVICE_ROLE_KEY=your_supabase_service_role_key_here
SUPABASE_DB_PASSWORD=your_supabase_db_password_here
SUPABASE_JWT_SECRET=your_supabase_jwt_secret_here

# Supabase Pooler specific settings (if using Supavisor in pooler mode)
SUPABASE_POOLER_HOST=your_supabase_pooler_host_here
SUPABASE_POOLER_PORT=your_supabase_pooler_port_here # e.g., 6543
SUPABASE_POOLER_USER=your_supabase_pooler_user_here # e.g., supabase_pooler_USER
SUPABASE_POOLER_PASSWORD=your_supabase_pooler_password_here

# Direct Database connection settings
SUPABASE_DB_HOST=your_supabase_db_host_here
SUPABASE_DB_PORT=your_supabase_db_port_here # e.g., 5432
SUPABASE_DB_USER=your_supabase_db_user_here # e.g., postgres
SUPABASE_DB_NAME=postgres # Default Supabase DB name

# Full Database URL (alternative method)
# Format: postgresql+asyncpg://USER:PASSWORD@HOST:PORT/DBNAME
DATABASE_URL=your_full_database_url_here

# Database connection pool settings
DB_MIN_POOL_SIZE=1
DB_MAX_POOL_SIZE=10
DB_CONNECTION_TIMEOUT=60

# --- Application Settings ---
LOG_LEVEL=TRACE
PORT=8000
HOST=0.0.0.0
MAX_WORKERS=4
ENVIRONMENT=development
CORS_ORIGINS="*"
USER_AGENT=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36...

# --- User & Tenant Settings ---
DEVELOPMENT_USER_ID=your_valid_uuid_for_dev_user
SYSTEM_USER_ID=00000000-0000-0000-0000-000000000000
DEFAULT_TENANT_ID=550e8400-e29b-41d4-a716-446655440000
DEV_USER_ID=
DEV_TOKEN=scraper_sky_2024

# --- External API Keys ---
SCRAPER_API_KEY=your_scraper_api_key_here
GOOGLE_MAPS_API_KEY=your_google_maps_api_key_here

# --- ScraperAPI Cost Control Settings ---
SCRAPER_API_ENABLE_PREMIUM=false
SCRAPER_API_ENABLE_JS_RENDERING=false
SCRAPER_API_ENABLE_GEOTARGETING=false
SCRAPER_API_MAX_RETRIES=1
SCRAPER_API_COST_CONTROL_MODE=true
WF7_ENABLE_JS_RENDERING=false

# --- Mautic Settings ---
MAUTIC_BASE_URL=your_mautic_base_url_here
MAUTIC_CLIENT_ID=your_mautic_client_id_here
MAUTIC_CLIENT_SECRET=your_mautic_client_secret_here

# --- GCP Settings ---
GCP_PROJECT_ID=your_gcp_project_id_here
GCP_SERVICE_ACCOUNT_EMAIL=your_gcp_service_account_email_here
GCP_SERVICE_ACCOUNT_PRIVATE_KEY="your_gcp_service_account_private_key_here_escaped_newlines"
GCP_SERVICE_ACCOUNT_TOKEN_URI=https://oauth2.googleapis.com/token

# --- Scheduler Settings ---
DOMAIN_SCHEDULER_INTERVAL_MINUTES=1
DOMAIN_SCHEDULER_BATCH_SIZE=10
DOMAIN_SCHEDULER_MAX_INSTANCES=1

SITEMAP_SCHEDULER_INTERVAL_MINUTES=1
SITEMAP_SCHEDULER_BATCH_SIZE=20
SITEMAP_SCHEDULER_MAX_INSTANCES=1

DOMAIN_SITEMAP_SCHEDULER_INTERVAL_MINUTES=1
DOMAIN_SITEMAP_SCHEDULER_BATCH_SIZE=10

SITEMAP_IMPORT_SCHEDULER_INTERVAL_MINUTES=1
SITEMAP_IMPORT_SCHEDULER_BATCH_SIZE=20
SITEMAP_IMPORT_SCHEDULER_MAX_INSTANCES=1

PAGE_CURATION_SCHEDULER_INTERVAL_MINUTES=1
PAGE_CURATION_SCHEDULER_BATCH_SIZE=10
PAGE_CURATION_SCHEDULER_MAX_INSTANCES=1

# --- Path & Cache Settings ---
CACHE_TTL=3600

# --- Diagnostic & Debug Settings ---
DIAGNOSTIC_DIR=/tmp/scraper_sky_scheduler_diagnostics
ENABLE_IMPORT_TRACING=true

# --- Storage Settings ---
CHROMA_PERSIST_DIR=./chroma_data
```

---

## Configuration Import Pattern

### In Application Modules
```python
from src.config.settings import settings

# Use settings throughout application
def setup_database():
    """Initialize database connection using settings."""
    pool_size = settings.db_max_pool_size
    timeout = settings.db_connection_timeout
    # ... setup code
    logger.info(f"Database pool size: {pool_size}")

def setup_cors(app: FastAPI):
    """Configure CORS using settings."""
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.get_cors_origins(),
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

def setup_scheduler():
    """Configure scheduler using settings."""
    scheduler.add_job(
        job_function,
        trigger="interval",
        minutes=settings.DOMAIN_SCHEDULER_INTERVAL_MINUTES,
        max_instances=settings.DOMAIN_SCHEDULER_MAX_INSTANCES,
    )
```

---

## Special Configuration Cases

### Cost Control for ScraperAPI
```python
from src.config.settings import settings
from src.utils.scraper_api import ScraperAPI

scraper = ScraperAPI(
    api_key=settings.scraper_api_key,
    enable_premium=settings.SCRAPER_API_ENABLE_PREMIUM,
    enable_js_rendering=settings.SCRAPER_API_ENABLE_JS_RENDERING,
    enable_geotargeting=settings.SCRAPER_API_ENABLE_GEOTARGETING,
    max_retries=settings.SCRAPER_API_MAX_RETRIES,
    cost_control_mode=settings.SCRAPER_API_COST_CONTROL_MODE,
)

# Never call premium features without explicit settings
if settings.SCRAPER_API_ENABLE_JS_RENDERING:
    # JS rendering enabled - costs 10-25x more
    result = scraper.scrape_with_js(url)
else:
    # Safe default - uses basic scraping
    result = scraper.scrape(url)
```

### Scheduler Configuration Example
```python
from src.config.settings import settings
from src.services.domain_scheduler import setup_domain_scheduler

def setup_domain_scheduler():
    """Setup domain scheduler with configuration from settings."""
    scheduler.add_job(
        process_domains,
        trigger="interval",
        minutes=settings.DOMAIN_SCHEDULER_INTERVAL_MINUTES,
        max_instances=settings.DOMAIN_SCHEDULER_MAX_INSTANCES,
        id="domain_scheduler",
    )

    logger.info(
        f"Domain Scheduler: interval={settings.DOMAIN_SCHEDULER_INTERVAL_MINUTES}min, "
        f"batch_size={settings.DOMAIN_SCHEDULER_BATCH_SIZE}, "
        f"max_instances={settings.DOMAIN_SCHEDULER_MAX_INSTANCES}"
    )
```

