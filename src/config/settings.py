import json
import logging
import uuid
from pathlib import Path
from typing import List, Optional

from pydantic_settings import BaseSettings, SettingsConfigDict


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
    # How often the scheduler runs (in minutes)
    DOMAIN_SCHEDULER_INTERVAL_MINUTES: int = 1
    # Number of domains processed in each batch
    DOMAIN_SCHEDULER_BATCH_SIZE: int = 50  # Increased from 10 to 50
    # Maximum concurrent instances of the scheduler
    DOMAIN_SCHEDULER_MAX_INSTANCES: int = 3  # Increased from 1 to 3

    # Sitemap Scheduler settings
    # How often the scheduler runs (in minutes)
    SITEMAP_SCHEDULER_INTERVAL_MINUTES: int = (
        1  # Fixed: Changed from 5 to 1 minute to match other schedulers
    )
    # Number of sitemaps processed in each batch
    SITEMAP_SCHEDULER_BATCH_SIZE: int = 25  # Increased from 5 to 25
    # Maximum concurrent instances of the scheduler
    SITEMAP_SCHEDULER_MAX_INSTANCES: int = 3  # Increased from 1 to 3

    # Domain Sitemap Submission Scheduler settings (New)
    DOMAIN_SITEMAP_SCHEDULER_INTERVAL_MINUTES: int = (
        1  # Default interval changed to 1 minute
    )
    DOMAIN_SITEMAP_SCHEDULER_BATCH_SIZE: int = 10  # Default batch size
    # DOMAIN_SITEMAP_SCHEDULER_MAX_INSTANCES: int = 1 # Add if needed, defaults to 1 in setup logic usually

    # Sitemap Import Scheduler settings (Renamed from Deep Scrape)
    SITEMAP_IMPORT_SCHEDULER_INTERVAL_MINUTES: int = 1  # Default interval
    SITEMAP_IMPORT_SCHEDULER_BATCH_SIZE: int = 20  # Default batch size
    SITEMAP_IMPORT_SCHEDULER_MAX_INSTANCES: int = 1  # Default max instances

    # External API Keys
    # openai_api_key: Optional[str] = None  # Removed OpenAI API key
    scraper_api_key: Optional[str] = None
    # langchain_api_key: Optional[str] = None  # Removed Langchain API key
    google_maps_api_key: Optional[str] = None

    # LangChain settings - Removed
    # langchain_tracing_v2: Optional[str] = None
    # langchain_endpoint: Optional[str] = None
    # langchain_project: Optional[str] = None

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
    user_agent: str = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"

    # User settings
    development_user_id: str = str(uuid.uuid4())
    system_user_id: str = "00000000-0000-0000-0000-000000000000"
    default_tenant_id: str = "550e8400-e29b-41d4-a716-446655440000"
    dev_user_id: Optional[str] = None
    # DEV_TOKEN removed - production uses proper service authentication

    # Path settings
    base_dir: Optional[Path] = None
    static_dir: Optional[Path] = None

    # Cache settings
    cache_ttl: int = 3600  # Default cache TTL in seconds

    # =============================================================================
    # CRITICAL DATABASE CONNECTION REQUIREMENTS - DO NOT MODIFY OR REMOVE
    # =============================================================================
    # This system EXCLUSIVELY uses Supavisor for connection pooling.
    # The following parameters are NON-NEGOTIABLE and MANDATORY for all deployments:
    #
    # 1. raw_sql=true     - Use raw SQL instead of ORM
    # 2. no_prepare=true  - Disable prepared statements
    # 3. statement_cache_size=0 - Control statement caching
    #
    # These settings are applied in:
    # - src/session/async_session.py
    # - src/db/engine.py
    #
    # NEVER modify these settings or reintroduce other connection pooling methods.
    # =============================================================================

    model_config = SettingsConfigDict(
        env_file=".env", case_sensitive=False, extra="allow"
    )

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


# Create a settings instance
settings = Settings()
