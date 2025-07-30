# FastAPI Documentation

## Overview & Installation

FastAPI is a modern, fast (high-performance), web framework for building APIs with Python 3.7+ based on standard Python type hints. It's designed for building production-ready APIs with automatic interactive documentation.

### Key Features
- **High Performance**: On par with NodeJS and Go
- **Fast to Code**: Increase development speed by 200-300%
- **Fewer Bugs**: Reduce human-induced errors by ~40%
- **Intuitive**: Great editor support with autocompletion
- **Easy**: Designed to be easy to use and learn
- **Short**: Minimize code duplication
- **Robust**: Get production-ready code with automatic interactive docs
- **Standards-based**: Based on OpenAPI and JSON Schema

### Installation

**Standard Installation (Recommended):**
```bash
pip install "fastapi[standard]"
```

**Minimal Installation:**
```bash
pip install fastapi
```

**ASGI Server (Required for Production):**
```bash
pip install "uvicorn[standard]"
```

## Core Concepts & Architecture

### FastAPI Application Instance
Every FastAPI application starts with creating an instance:

```python
from fastapi import FastAPI

app = FastAPI()
```

### Path Operations
Define API endpoints using HTTP method decorators:

```python
@app.get("/")
async def read_root():
    return {"message": "Hello World"}

@app.get("/items/{item_id}")
async def read_item(item_id: int, q: Union[str, None] = None):
    return {"item_id": item_id, "q": q}
```

### Asynchronous vs Synchronous Functions
FastAPI supports both sync and async functions:

```python
# Synchronous
@app.get("/sync")
def sync_endpoint():
    return {"type": "synchronous"}

# Asynchronous (recommended for I/O operations)
@app.get("/async")
async def async_endpoint():
    return {"type": "asynchronous"}
```

## Common Usage Patterns

### 1. Basic Application Structure
```python
from typing import Union
from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.get("/items/{item_id}")
def read_item(item_id: int, q: Union[str, None] = None):
    return {"item_id": item_id, "q": q}
```

### 2. Running the Development Server
```bash
# Using fastapi dev (recommended for development)
fastapi dev main.py

# Using uvicorn directly
uvicorn main:app --reload
```

### 3. Application Lifecycle Events
```python
@app.on_event("startup")
async def startup_event():
    # Initialize database connections, load models, etc.
    items_db["foo"] = {"name": "Foo", "price": 50.2}
    print("Application startup complete")

@app.on_event("shutdown")
async def shutdown_event():
    # Clean up resources
    print("Application shutdown")
```

### 4. Path Parameters and Query Parameters
```python
from typing import Union

@app.get("/items/{item_id}")
async def read_item(
    item_id: int,           # Path parameter
    q: Union[str, None] = None,  # Optional query parameter
    limit: int = 10         # Query parameter with default
):
    return {"item_id": item_id, "q": q, "limit": limit}
```

## Best Practices & Security

### 1. Use Type Hints
Always use Python type hints for automatic validation and documentation:

```python
from typing import Union, List
from pydantic import BaseModel

class Item(BaseModel):
    name: str
    price: float
    is_offer: Union[bool, None] = None

@app.post("/items/")
async def create_item(item: Item):
    return item
```

### 2. Dependency Injection
Use FastAPI's dependency injection system:

```python
from fastapi import Depends

async def get_database():
    # Database connection logic
    pass

@app.get("/items/")
async def read_items(db = Depends(get_database)):
    # Use database connection
    pass
```

### 3. Error Handling
```python
from fastapi import HTTPException

@app.get("/items/{item_id}")
async def read_item(item_id: int):
    if item_id not in items_db:
        raise HTTPException(status_code=404, detail="Item not found")
    return items_db[item_id]
```

### 4. Authentication & Authorization
```python
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer

security = HTTPBearer()

async def verify_token(token: str = Depends(security)):
    # Token verification logic
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials"
        )
    return token
```

## Integration Examples

### With SQLAlchemy (Database ORM)
```python
from sqlalchemy.orm import Session
from fastapi import Depends

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/users/{user_id}")
async def read_user(user_id: int, db: Session = Depends(get_db)):
    return db.query(User).filter(User.id == user_id).first()
```

### With Pydantic Models
```python
from pydantic import BaseModel
from typing import List

class UserBase(BaseModel):
    email: str
    is_active: bool = True

class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: int
    
    class Config:
        from_attributes = True

@app.post("/users/", response_model=User)
async def create_user(user: UserCreate):
    # Create user logic
    pass
```

## Troubleshooting & FAQs

### Common Issues

1. **Server Won't Start**
   ```bash
   # Check if port is already in use
   lsof -i :8000
   
   # Use different port
   uvicorn main:app --port 8001
   ```

2. **Import Errors**
   ```bash
   # Ensure FastAPI is installed
   pip install "fastapi[standard]"
   
   # Check Python path
   python -c "import fastapi; print(fastapi.__version__)"
   ```

3. **Automatic Docs Not Working**
   - Ensure your app is running
   - Check `/docs` for Swagger UI
   - Check `/redoc` for ReDoc
   - Verify no custom docs configuration

### Performance Tips

1. **Use Async Functions**: For I/O bound operations
2. **Enable Compression**: Use middleware for response compression
3. **Database Connection Pooling**: Use proper connection pooling
4. **Caching**: Implement caching strategies for frequently accessed data

### Testing
```python
from fastapi.testclient import TestClient

client = TestClient(app)

def test_read_main():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"msg": "Hello World"}
```

## ScraperSky-Specific Implementation Notes

### Current Usage in ScraperSky
- **Version**: FastAPI 0.115.8 (as per requirements.txt)
- **Server**: Uvicorn with async support
- **Architecture**: Multi-router structure with versioned APIs (`/api/v3/`)
- **Authentication**: JWT-based authentication with dependency injection
- **Database Integration**: Async SQLAlchemy sessions

### Key Components
1. **Main Application**: `src/main.py` - Central FastAPI app instance
2. **Routers**: `src/routers/` - Modular API endpoints
3. **Dependencies**: Authentication and database session dependencies
4. **Models**: Pydantic models for request/response validation

### Router Structure
```python
# Example from ScraperSky
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(prefix="/api/v3/domains")

@router.get("/")
async def list_domains(
    db: AsyncSession = Depends(get_async_session)
):
    # Domain listing logic
    pass
```

### Development Workflow
```bash
# Start development server
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000

# Or using Docker
docker compose up --build

# Access interactive docs
# http://localhost:8000/docs
```

This documentation provides comprehensive guidance for working with FastAPI in the ScraperSky project context.