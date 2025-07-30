# SQLAlchemy Documentation

## Overview & Installation

SQLAlchemy is the Database Toolkit for Python, providing a comprehensive suite of tools for interacting with databases. It features both a Core expression language and an Object-Relational Mapper (ORM) that provides a full-featured data mapper pattern.

### Key Features
- **Mature and Battle-tested**: Over 15 years of development
- **Flexible Architecture**: Use Core for raw SQL power or ORM for object-oriented design
- **Database Agnostic**: Works with PostgreSQL, MySQL, SQLite, Oracle, Microsoft SQL Server, and more
- **High Performance**: Efficient lazy loading, connection pooling, and query optimization
- **Type Safety**: Strong typing support with modern Python type hints
- **Async Support**: Full asyncio support for modern Python applications

### Installation

**Standard Installation:**
```bash
pip install sqlalchemy
```

**With Asyncio Support:**
```bash
pip install sqlalchemy[asyncio]
```

**Version Check:**
```python
import sqlalchemy
print(sqlalchemy.__version__)
```

## Core Concepts & Architecture

### SQLAlchemy Core vs ORM

**Core**: Expression language for building SQL statements programmatically
**ORM**: Object-Relational Mapper for working with database records as Python objects

### Engine and Connection
The Engine is the starting point for any SQLAlchemy application:

```python
from sqlalchemy import create_engine

# Create engine
engine = create_engine("sqlite:///example.db", echo=True)

# Basic connection usage
with engine.connect() as conn:
    result = conn.execute(text("SELECT 'Hello World'"))
    print(result.fetchall())
```

### MetaData and Table Definitions
```python
from sqlalchemy import MetaData, Table, Column, Integer, String, ForeignKey

metadata_obj = MetaData()

user_table = Table(
    "user_account",
    metadata_obj,
    Column("id", Integer, primary_key=True),
    Column("name", String(30)),
    Column("fullname", String),
)
```

## Common Usage Patterns

### 1. Modern Declarative ORM Setup (SQLAlchemy 2.0 Style)

```python
from typing import List, Optional
from sqlalchemy import Column, ForeignKey, create_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship, Session

class Base(DeclarativeBase):
    pass

class User(Base):
    __tablename__ = "user_account"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(30))
    fullname: Mapped[Optional[str]]
    
    addresses: Mapped[List["Address"]] = relationship(back_populates="user")
    
    def __repr__(self) -> str:
        return f"User(id={self.id!r}, name={self.name!r})"

class Address(Base):
    __tablename__ = "address"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    email_address: Mapped[str]
    user_id: Mapped[int] = mapped_column(ForeignKey("user_account.id"))
    
    user: Mapped["User"] = relationship(back_populates="addresses")
    
    def __repr__(self) -> str:
        return f"Address(id={self.id!r}, email_address={self.email_address!r})"
```

### 2. Database Setup and Session Management

```python
# Create engine and tables
engine = create_engine("sqlite+pysqlite:///:memory:", echo=True)
Base.metadata.create_all(engine)

# Create session
session = Session(engine)

# Add data
session.add_all([
    User(
        name="spongebob",
        fullname="Spongebob Squarepants",
        addresses=[Address(email_address="spongebob@sqlalchemy.org")],
    ),
    User(
        name="sandy",
        fullname="Sandy Cheeks",
        addresses=[
            Address(email_address="sandy@sqlalchemy.org"),
            Address(email_address="squirrel@squirrelpower.org"),
        ],
    ),
])
session.commit()
```

### 3. Querying Data

```python
from sqlalchemy import select

# Simple select
stmt = select(User).where(User.name == "spongebob")
user = session.scalar(stmt)

# Join queries
stmt = select(User).join(User.addresses).where(Address.email_address.contains("sqlalchemy"))
users = session.scalars(stmt).all()

# Using relationships
user = session.get(User, 1)
for address in user.addresses:
    print(address.email_address)
```

### 4. Async Usage

```python
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

# Create async engine
engine = create_async_engine("postgresql+asyncpg://user:pass@localhost/db")

# Create async session
async_session = async_sessionmaker(engine, class_=AsyncSession)

async def async_main():
    async with async_session() as session:
        stmt = select(User).where(User.name == "spongebob")
        result = await session.execute(stmt)
        user = result.scalar_one()
        print(user)
```

## Best Practices & Security

### 1. Connection Management
```python
# Use connection pooling
engine = create_engine(
    "postgresql://user:pass@localhost/db",
    pool_size=20,
    max_overflow=0,
    pool_pre_ping=True,
    pool_recycle=3600
)
```

### 2. Query Security - Always Use Bound Parameters
```python
# ✅ SECURE: Using bound parameters
stmt = select(User).where(User.name == user_input)

# ❌ INSECURE: String formatting (SQL injection risk)
# stmt = text(f"SELECT * FROM users WHERE name = '{user_input}'")
```

### 3. Transaction Management
```python
# Using context managers for automatic rollback
with engine.begin() as conn:
    conn.execute(
        text("INSERT INTO some_table (x, y, z) VALUES (:x, :y, :z)"),
        [{"x": 1, "y": 2, "z": 3}, {"x": 2, "y": 4, "z": 6}]
    )
    # Automatically commits on success, rolls back on exception
```

### 4. Session Lifecycle
```python
# Proper session handling
with Session(engine) as session:
    # Do work
    user = User(name="new_user")
    session.add(user)
    session.commit()
    # Session automatically closed
```

## Integration Examples

### With FastAPI
```python
from fastapi import Depends, FastAPI
from sqlalchemy.orm import Session

app = FastAPI()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/users/{user_id}")
async def read_user(user_id: int, db: Session = Depends(get_db)):
    return db.get(User, user_id)
```

### Connection String Examples
```python
# PostgreSQL
engine = create_engine("postgresql+psycopg2://user:pass@localhost/db")
engine = create_engine("postgresql+asyncpg://user:pass@localhost/db")  # Async

# MySQL
engine = create_engine("mysql+pymysql://user:pass@localhost/db")

# SQLite
engine = create_engine("sqlite:///path/to/database.db")
engine = create_engine("sqlite+aiosqlite:///path/to/database.db")  # Async

# SQL Server
engine = create_engine("mssql+pyodbc://user:pass@server/db?driver=ODBC+Driver+17+for+SQL+Server")
```

### Performance Optimization
```python
# Eager loading to avoid N+1 queries
from sqlalchemy.orm import selectinload, joinedload

# Select-in loading (recommended for collections)
stmt = select(User).options(selectinload(User.addresses))

# Joined loading (for single relationships)
stmt = select(User).options(joinedload(User.profile))

# Lazy loading control
addresses: Mapped[List["Address"]] = relationship(lazy="select")  # Default
addresses: Mapped[List["Address"]] = relationship(lazy="selectin")  # Batch load
```

## Troubleshooting & FAQs

### Common Issues

1. **"Table doesn't exist" errors**
   ```python
   # Ensure tables are created
   Base.metadata.create_all(engine)
   ```

2. **Connection pool exhaustion**
   ```python
   # Always close sessions
   with Session(engine) as session:
       # work here
       pass  # session closed automatically
   ```

3. **Async/await issues**
   ```python
   # Use async session for async operations
   async with async_session() as session:
       result = await session.execute(stmt)
   ```

### Migration Patterns
```python
# For database migrations, use Alembic
from alembic import command
from alembic.config import Config

alembic_cfg = Config("alembic.ini")
command.upgrade(alembic_cfg, "head")
```

### Custom Types
```python
from sqlalchemy.types import TypeDecorator, String
import json

class JSONType(TypeDecorator):
    impl = String
    cache_ok = True

    def process_bind_param(self, value, dialect):
        return json.dumps(value) if value is not None else None

    def process_result_value(self, value, dialect):
        return json.loads(value) if value is not None else None
```

## ScraperSky-Specific Implementation Notes

### Current Usage in ScraperSky
- **Version**: SQLAlchemy 2.0.38 (as per requirements.txt)
- **Database**: PostgreSQL via Supabase with connection pooling
- **Driver**: AsyncPG for async operations
- **Session Management**: Async sessions with dependency injection

### Database Configuration
```python
# ScraperSky connection pattern
DATABASE_URL = "postgresql+asyncpg://user:pass@host:port/db?raw_sql=true&no_prepare=true&statement_cache_size=0"

# Engine setup for Supavisor compatibility
engine = create_async_engine(
    DATABASE_URL,
    echo=False,
    pool_pre_ping=True,
    pool_recycle=3600
)
```

### Model Examples from ScraperSky
```python
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import String, DateTime, Integer, Text, Boolean
from datetime import datetime

class Base(DeclarativeBase):
    pass

class Domain(Base):
    __tablename__ = "domains"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    domain_name: Mapped[str] = mapped_column(String(255), unique=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    last_scraped: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

class Sitemap(Base):
    __tablename__ = "sitemaps"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    url: Mapped[str] = mapped_column(Text)
    domain_id: Mapped[int] = mapped_column(ForeignKey("domains.id"))
    status: Mapped[str] = mapped_column(String(50), default="pending")
    
    domain: Mapped["Domain"] = relationship("Domain")
```

### Async Session Dependency
```python
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends

async def get_async_session() -> AsyncSession:
    async with async_session() as session:
        yield session

@router.get("/domains/")
async def list_domains(db: AsyncSession = Depends(get_async_session)):
    stmt = select(Domain).where(Domain.is_active == True)
    result = await db.execute(stmt)
    return result.scalars().all()
```

### Key Configuration Requirements
- **Supavisor Compatibility**: `raw_sql=true`, `no_prepare=true`, `statement_cache_size=0`
- **Async Operations**: All database operations use `await`
- **Connection Pooling**: Handled by Supavisor, not SQLAlchemy's pool
- **Type Hints**: Modern Mapped[] syntax for all model attributes

This documentation provides comprehensive guidance for working with SQLAlchemy in the ScraperSky project context, emphasizing async patterns and Supabase integration.