import os
from pydantic_settings import BaseSettings
from typing import Optional, List
from pathlib import Path

class Settings(BaseSettings):
    # Environment
    environment: str = "development"
    
    # Database Configuration
    supabase_url: str
    supabase_service_role_key: str
    supabase_anon_key: str
    supabase_db_password: str
    supabase_jwt_secret: Optional[str] = None
    
    # Database connection settings
    db_min_pool_size: int = 1
    db_max_pool_size: int = 10
    db_connection_timeout: int = 10
    
    # API Keys
    openai_api_key: str
    scraper_api_key: str

    # Application Settings
    log_level: str = "INFO"
    port: int = 8000
    host: str = "0.0.0.0"
    max_workers: int = 4
    user_agent: str = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    
    # CORS Settings
    cors_origins: str = "*"  # Comma-separated list in .env, parsed to list in get_cors_origins()
    
    # Storage Settings
    chroma_persist_dir: str = os.path.join(Path(__file__).parent.parent.parent.absolute(), "chroma_data")
    
    # Cache settings
    cache_ttl: int = 3600  # Default cache TTL in seconds

    class Config:
        env_file = ".env"
        case_sensitive = False  # Allow case-insensitive env var names
        extra = "ignore"        # Ignore extra environment variables
        
    def get_cors_origins(self) -> List[str]:
        """Parse CORS origins from comma-separated string to list."""
        if self.cors_origins == "*":
            return ["*"]
        return [origin.strip() for origin in self.cors_origins.split(",")]
        
    def validate(self) -> None:
        """Validate required settings."""
        missing = []
        
        # Check required database settings
        if not self.supabase_url:
            missing.append("SUPABASE_URL")
        if not self.supabase_db_password:
            missing.append("SUPABASE_DB_PASSWORD")
            
        # Check API keys
        if not self.scraper_api_key:
            missing.append("SCRAPER_API_KEY")
            
        if missing:
            raise ValueError(f"Missing required environment variables: {', '.join(missing)}")
            
        return True
        
# Create and validate settings
settings = Settings()
settings.validate()
