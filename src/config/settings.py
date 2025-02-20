from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # Database Configuration
    supabase_url: str
    supabase_service_role_key: str
    supabase_anon_key: str
    supabase_db_password: str

    # API Keys
    openai_api_key: str
    scraper_api_key: str

    # Application Settings
    log_level: str = "INFO"
    port: int = 8000
    host: str = "0.0.0.0"
    max_workers: int = 4

    # Storage Settings
    chroma_persist_dir: str = "./chroma_data"

    class Config:
        env_file = ".env"
        case_sensitive = False  # Allow case-insensitive env var names
