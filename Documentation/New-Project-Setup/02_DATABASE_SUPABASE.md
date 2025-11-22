# Database & Supabase Configuration

**Document:** 02_DATABASE_SUPABASE.md  
**Phase:** Database Setup  
**Time Required:** 45-60 minutes  
**Prerequisites:** [01_PROJECT_SETUP.md](./01_PROJECT_SETUP.md) completed

---

## Overview

This document guides you through setting up Supabase as your PostgreSQL database, configuring connection pooling with Supavisor, and integrating SQLAlchemy async with your FastAPI application.

---

## Supabase Project Setup

### Step 1: Create Supabase Account

1. Go to https://supabase.com
2. Sign up or log in
3. Click "New Project"

### Step 2: Create New Project

**Project Configuration:**
- **Name:** your-project-name
- **Database Password:** Generate strong password (save it!)
- **Region:** Choose closest to your users
- **Pricing Plan:** Free tier is fine for development

**Wait 2-3 minutes for project to initialize.**

### Step 3: Gather Connection Details

Once project is ready, go to **Settings** → **Database**:

#### Direct Connection Details
```
Host: db.{project-ref}.supabase.co
Port: 5432
Database: postgres
User: postgres.{project-ref}
Password: [your database password]
```

#### Connection Pooler Details (Supavisor)
```
Host: aws-0-{region}.pooler.supabase.com
Port: 6543
Database: postgres
User: postgres.{project-ref}
Password: [same database password]
```

#### API Details
Go to **Settings** → **API**:
```
Project URL: https://{project-ref}.supabase.co
anon/public key: eyJhbGc...
service_role key: eyJhbGc... (keep secret!)
JWT Secret: [your JWT secret]
```

### Step 4: Configure .env File

Create `.env` in project root:

```bash
# Application Settings
ENVIRONMENT=development
HOST=0.0.0.0
PORT=8000
LOG_LEVEL=INFO

# Supabase Core
SUPABASE_URL=https://{project-ref}.supabase.co
SUPABASE_ANON_KEY=eyJhbGc...your-anon-key...
SUPABASE_SERVICE_ROLE_KEY=eyJhbGc...your-service-role-key...
SUPABASE_DB_PASSWORD=your-database-password
SUPABASE_JWT_SECRET=your-jwt-secret

# Supabase Connection Pooler (Supavisor) - RECOMMENDED
SUPABASE_POOLER_HOST=aws-0-{region}.pooler.supabase.com
SUPABASE_POOLER_PORT=6543
SUPABASE_POOLER_USER=postgres.{project-ref}
SUPABASE_POOLER_PASSWORD=your-database-password

# Direct Database Connection (Fallback)
SUPABASE_DB_HOST=db.{project-ref}.supabase.co
SUPABASE_DB_PORT=5432
SUPABASE_DB_USER=postgres.{project-ref}
SUPABASE_DB_NAME=postgres

# Database Pool Settings
DB_MIN_POOL_SIZE=1
DB_MAX_POOL_SIZE=10
DB_CONNECTION_TIMEOUT=30

# CORS
CORS_ORIGINS=*
```

**Important:** Replace all `{project-ref}` and placeholder values with your actual Supabase details.

---

## Application Configuration

### Step 1: Create settings.py

Create `src/config/settings.py`:

```python
"""
Application Settings

Centralized configuration using Pydantic Settings.
All environment variables are defined here.
"""

import json
from typing import List, Optional
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Application settings using Pydantic BaseSettings.
    
    This reads values from environment variables matching the field names.
    """
    
    # Application Settings
    environment: str = "development"
    host: str = "0.0.0.0"
    port: int = 8000
    log_level: str = "INFO"
    
    # Supabase Settings
    supabase_url: Optional[str] = None
    supabase_anon_key: Optional[str] = None
    supabase_service_role_key: Optional[str] = None
    supabase_db_password: Optional[str] = None
    supabase_jwt_secret: Optional[str] = None
    
    # Supabase Pooler Settings (Supavisor)
    supabase_pooler_host: Optional[str] = None
    supabase_pooler_port: Optional[str] = None
    supabase_pooler_user: Optional[str] = None
    supabase_pooler_password: Optional[str] = None
    
    # Direct Database Connection Settings
    supabase_db_host: Optional[str] = None
    supabase_db_port: Optional[str] = None
    supabase_db_user: Optional[str] = None
    supabase_db_name: str = "postgres"
    
    # Database Connection Pool Settings
    db_min_pool_size: int = 1
    db_max_pool_size: int = 10
    db_connection_timeout: int = 30
    
    # CORS Settings
    cors_origins: str = "*"
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )
    
    def get_cors_origins(self) -> List[str]:
        """
        Parse CORS origins from string or JSON array.
        
        Returns:
            List of allowed origins
        """
        if self.cors_origins == "*":
            return ["*"]
        
        # Try parsing as JSON array
        try:
            origins = json.loads(self.cors_origins)
            if isinstance(origins, list):
                return origins
        except (json.JSONDecodeError, TypeError):
            pass
        
        # Parse as comma-separated string
        return [origin.strip() for origin in self.cors_origins.split(",")]


# Create global settings instance
settings = Settings()
```

### Step 2: Create Database Engine

Create `src/db/engine.py`:

```python
"""
SQLAlchemy Database Engine

Provides async database connection to Supabase PostgreSQL using SQLAlchemy.

CRITICAL: This system uses Supavisor for connection pooling with required parameters:
- statement_cache_size=0 - Disable statement caching
- prepared_statement_cache_size=0 - Disable prepared statement caching
- no_prepare=True - Disable prepared statements
- raw_sql=True - Use raw SQL

These parameters are MANDATORY for Supabase Supavisor compatibility.
DO NOT MODIFY without understanding the implications.
"""

import logging
import ssl
import uuid
from urllib.parse import quote_plus

from sqlalchemy.ext.asyncio import create_async_engine

from src.config.settings import settings

logger = logging.getLogger(__name__)


class DatabaseConfig:
    """Configuration for Supabase database connection."""
    
    def __init__(self):
        # Extract project reference from Supabase URL
        self.supabase_url = settings.supabase_url
        if not self.supabase_url:
            raise ValueError("SUPABASE_URL environment variable is not set")
        
        # Handle URL format with or without protocol
        if "//" in self.supabase_url:
            self.project_ref = self.supabase_url.split("//")[1].split(".")[0]
        else:
            self.project_ref = self.supabase_url.split(".")[0]
        
        # Database connection parameters
        self.user = f"postgres.{self.project_ref}"
        self.password = settings.supabase_db_password or ""
        self.host = settings.supabase_db_host or f"db.{self.project_ref}.supabase.co"
        self.port = settings.supabase_db_port or "5432"
        self.dbname = settings.supabase_db_name
        
        if not all([self.project_ref, self.password]):
            raise ValueError(
                "Missing required database configuration. "
                "Please ensure SUPABASE_URL and SUPABASE_DB_PASSWORD are set in .env"
            )
        
        # Pooler connection settings
        self.pooler_host = settings.supabase_pooler_host
        self.pooler_port = settings.supabase_pooler_port
        self.pooler_user = settings.supabase_pooler_user
    
    @property
    def async_connection_string(self) -> str:
        """Generate the SQLAlchemy connection string for asyncpg."""
        # Use connection pooler if available (recommended)
        if all([self.pooler_host, self.pooler_port, self.pooler_user]):
            logger.info(f"Using Supavisor connection pooler at {self.pooler_host}")
            return (
                f"postgresql+asyncpg://{self.pooler_user}:"
                f"{quote_plus(str(self.password))}"
                f"@{self.pooler_host}:{self.pooler_port}/{self.dbname}"
            )
        
        # Fall back to direct connection
        logger.info(f"Using direct connection to {self.host}")
        return (
            f"postgresql+asyncpg://{self.user}:{quote_plus(str(self.password))}"
            f"@{self.host}:{self.port}/{self.dbname}"
        )
    
    @property
    def pooler_mode(self) -> bool:
        """Check if pooler connection details are configured."""
        return all([self.pooler_host, self.pooler_port, self.pooler_user])


def get_supavisor_ready_url(db_url: str) -> str:
    """
    Enhance database URL with required Supavisor connection pooling parameters.
    
    Args:
        db_url: Original database URL
    
    Returns:
        Enhanced URL with connection pooling parameters
    """
    if "?" in db_url:
        return f"{db_url}&statement_cache_size=0"
    else:
        return f"{db_url}?statement_cache_size=0"


# Initialize database configuration
db_config = DatabaseConfig()

# Configure SSL context for Supabase
ssl_context = ssl.create_default_context()
ssl_context.check_hostname = False
ssl_context.verify_mode = ssl.CERT_NONE  # Required for Supabase self-signed cert chain

# Configure connect_args for asyncpg with Supavisor compatibility
connect_args = {
    "server_settings": {
        "search_path": "public",
        "application_name": "your_app_name",
    },
    "prepared_statement_name_func": lambda: f"__asyncpg_{uuid.uuid4()}__",
    "ssl": ssl_context,
    "command_timeout": settings.db_connection_timeout,
    "statement_cache_size": 0,
    "prepared_statement_cache_size": 0,
}

# Create the async engine with proper connection pooling settings
engine = create_async_engine(
    get_supavisor_ready_url(db_config.async_connection_string),
    pool_size=settings.db_min_pool_size,
    max_overflow=settings.db_max_pool_size - settings.db_min_pool_size,
    pool_timeout=settings.db_connection_timeout,
    pool_recycle=1800,  # Recycle connections after 30 minutes
    echo=False,  # Set to True for SQL query logging in development
    connect_args=connect_args,
    # Required Supavisor parameters at engine level
    execution_options={
        "isolation_level": "READ COMMITTED",
        "no_prepare": True,
        "raw_sql": True,
    },
)

logger.info("SQLAlchemy async engine created with Supavisor connection pooling")
logger.info(f"Connected to: {db_config.pooler_host or db_config.host}")
```

### Step 3: Create Session Management

Create `src/session/async_session.py`:

```python
"""
Async Session Management

Provides async database sessions for FastAPI dependency injection.
"""

import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from src.db.engine import engine

logger = logging.getLogger(__name__)

# Create async session factory
async_session_factory = async_sessionmaker(
    engine,
    expire_on_commit=False,
    autoflush=False,
    autocommit=False,
)


@asynccontextmanager
async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Async context manager for database sessions.
    
    Provides a SQLAlchemy AsyncSession and handles committing changes and
    rolling back on exceptions.
    
    Example:
        async with get_session() as session:
            result = await session.execute(query)
            session.add(new_record)
    """
    session = async_session_factory()
    try:
        yield session
        await session.commit()
    except Exception as e:
        await session.rollback()
        logger.error(f"Database session error: {str(e)}")
        raise
    finally:
        await session.close()


async def get_session_dependency() -> AsyncGenerator[AsyncSession, None]:
    """
    Get an async session for use as a FastAPI dependency.
    
    This function is designed to be used with FastAPI's dependency injection system.
    
    Example:
        @router.get("/items")
        async def get_items(session: AsyncSession = Depends(get_session_dependency)):
            result = await session.execute(select(Item))
            return result.scalars().all()
    """
    async with get_session() as session:
        yield session
```

---

## Database Models Setup

### Step 1: Create Base Model

Create `src/models/base.py`:

```python
"""
SQLAlchemy Base Model

All database models inherit from this base class.
"""

from datetime import datetime
from typing import Optional
from uuid import uuid4

from sqlalchemy import DateTime, String, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    """Base class for all database models."""
    pass


class TimestampMixin:
    """Mixin for created_at and updated_at timestamps."""
    
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )
    
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False
    )


class UUIDMixin:
    """Mixin for UUID primary key."""
    
    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid4()),
        nullable=False
    )
```

### Step 2: Create Example Model

Create `src/models/wf1_example.py`:

```python
"""
Example Model (Workflow 1)

This is an example model showing the workflow-based naming convention.
Replace with your actual models.
"""

from typing import Optional

from sqlalchemy import String, Text
from sqlalchemy.orm import Mapped, mapped_column

from src.models.base import Base, TimestampMixin, UUIDMixin


class Example(Base, UUIDMixin, TimestampMixin):
    """
    Example model for demonstration.
    
    Table: examples
    Workflow: WF1 (Example Workflow)
    """
    
    __tablename__ = "examples"
    
    # Fields
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String(50), default="pending", nullable=False)
    
    def __repr__(self) -> str:
        return f"<Example(id={self.id}, name={self.name})>"
```

### Step 3: Update models/__init__.py

Update `src/models/__init__.py`:

```python
"""
Database Models

All SQLAlchemy models are imported here for easy access.
"""

from src.models.base import Base, TimestampMixin, UUIDMixin
from src.models.wf1_example import Example

__all__ = [
    "Base",
    "TimestampMixin",
    "UUIDMixin",
    "Example",
]
```

---

## Database Migrations

### Step 1: Create Migration Script

Create `supabase/migrations/20250121000000_initial_schema.sql`:

```sql
-- Initial Schema Migration
-- Created: 2025-01-21
-- Description: Create initial tables

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Create examples table
CREATE TABLE IF NOT EXISTS examples (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL,
    description TEXT,
    status VARCHAR(50) NOT NULL DEFAULT 'pending',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL
);

-- Create index on status for filtering
CREATE INDEX IF NOT EXISTS idx_examples_status ON examples(status);

-- Create updated_at trigger function
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create trigger for examples table
CREATE TRIGGER update_examples_updated_at
    BEFORE UPDATE ON examples
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Add comment to table
COMMENT ON TABLE examples IS 'Example table for demonstration (Workflow 1)';
```

### Step 2: Apply Migration via Supabase Dashboard

1. Go to Supabase Dashboard
2. Navigate to **SQL Editor**
3. Create new query
4. Paste migration SQL
5. Click **Run**
6. Verify tables created in **Table Editor**

### Step 3: Verify Database Connection

Update `src/main.py` to test database connection:

```python
"""
Main FastAPI Application
"""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.config.settings import settings
from src.session.async_session import get_session_dependency
from src.models import Example

logging.basicConfig(
    level=settings.log_level,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan event handler."""
    logger.info("Starting up application...")
    
    # Test database connection
    try:
        from src.db.engine import engine
        async with engine.begin() as conn:
            await conn.execute(select(1))
        logger.info("✅ Database connection successful")
    except Exception as e:
        logger.error(f"❌ Database connection failed: {e}")
        raise
    
    yield
    
    logger.info("Shutting down application...")


app = FastAPI(
    title="Your Project API",
    description="API for your project",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.get_cors_origins(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "ok"}


@app.get("/health/database")
async def database_health(session: AsyncSession = Depends(get_session_dependency)):
    """Database health check."""
    try:
        result = await session.execute(select(1))
        result.scalar()
        return {"status": "ok", "message": "Database connection successful"}
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        return {"status": "error", "message": str(e)}


@app.get("/examples")
async def list_examples(session: AsyncSession = Depends(get_session_dependency)):
    """List all examples."""
    result = await session.execute(select(Example))
    examples = result.scalars().all()
    return {"examples": [{"id": e.id, "name": e.name} for e in examples]}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=settings.host, port=settings.port)
```

---

## Testing Database Setup

### Step 1: Start Application

```bash
# Activate virtual environment
source venv/bin/activate

# Run application
uvicorn src.main:app --reload
```

**Expected Output:**
```
INFO:     Starting up application...
INFO:     Using Supavisor connection pooler at aws-0-us-east-1.pooler.supabase.com
INFO:     SQLAlchemy async engine created with Supavisor connection pooling
INFO:     ✅ Database connection successful
INFO:     Application startup complete.
```

### Step 2: Test Endpoints

```bash
# Health check
curl http://localhost:8000/health

# Database health check
curl http://localhost:8000/health/database

# List examples (should return empty array)
curl http://localhost:8000/examples
```

### Step 3: Insert Test Data

Via Supabase Dashboard:
1. Go to **Table Editor**
2. Select `examples` table
3. Click **Insert row**
4. Add test data
5. Save

Then test again:
```bash
curl http://localhost:8000/examples
```

Should return your test data.

---

## Verification Checklist

Before proceeding, verify:

- [ ] Supabase project created
- [ ] Connection details gathered
- [ ] `.env` file configured with all Supabase credentials
- [ ] `settings.py` created and loading environment variables
- [ ] `engine.py` created with Supavisor configuration
- [ ] `async_session.py` created with session management
- [ ] Base model created
- [ ] Example model created
- [ ] Initial migration created and applied
- [ ] Application starts without errors
- [ ] Database connection successful (check logs)
- [ ] `/health/database` endpoint returns success
- [ ] Can query database via API

---

## Troubleshooting

### Issue: Connection timeout

**Problem:** `asyncpg.exceptions.ConnectionDoesNotExistError`

**Solution:**
1. Verify Supabase project is active (not paused)
2. Check connection details are correct
3. Ensure using pooler connection (port 6543)
4. Verify password is correct

### Issue: SSL certificate error

**Problem:** `SSL certificate verification failed`

**Solution:**
Already handled in `engine.py` with:
```python
ssl_context.verify_mode = ssl.CERT_NONE
```

### Issue: Prepared statement error

**Problem:** `prepared statement "__asyncpg_stmt_..." does not exist`

**Solution:**
Verify `engine.py` has all Supavisor parameters:
```python
"statement_cache_size": 0,
"prepared_statement_cache_size": 0,
"no_prepare": True,
```

### Issue: Migration not applied

**Problem:** Table doesn't exist

**Solution:**
1. Go to Supabase SQL Editor
2. Run migration SQL manually
3. Verify in Table Editor
4. Check for SQL errors in dashboard

---

## Next Steps

✅ **Completed:** Database and Supabase configuration

**Next:** [03_BACKEND_ARCHITECTURE.md](./03_BACKEND_ARCHITECTURE.md) - Build FastAPI application architecture

---

## Quick Reference

### Connection String Format

**Pooler (Recommended):**
```
postgresql+asyncpg://postgres.{ref}:{password}@aws-0-{region}.pooler.supabase.com:6543/postgres
```

**Direct:**
```
postgresql+asyncpg://postgres.{ref}:{password}@db.{ref}.supabase.co:5432/postgres
```

### Required Supavisor Parameters

```python
# In connect_args
"statement_cache_size": 0
"prepared_statement_cache_size": 0

# In execution_options
"no_prepare": True
"raw_sql": True
```

### Common SQL Commands

```sql
-- List all tables
SELECT tablename FROM pg_tables WHERE schemaname = 'public';

-- Check table structure
\d examples

-- Count rows
SELECT COUNT(*) FROM examples;

-- View recent entries
SELECT * FROM examples ORDER BY created_at DESC LIMIT 10;
```

---

**Status:** ✅ Database configured and tested  
**Next:** Backend architecture and routing patterns
