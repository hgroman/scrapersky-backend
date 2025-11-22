# Project Setup & Prerequisites

**Document:** 01_PROJECT_SETUP.md  
**Phase:** Initial Setup  
**Time Required:** 30-45 minutes  
**Prerequisites:** None (this is the starting point)

---

## Overview

This document guides you through the initial project setup, from installing prerequisites to creating the basic project structure. By the end, you'll have a clean project ready for FastAPI development.

---

## Prerequisites

### Required Software

#### 1. Python 3.11+

**Check if installed:**
```bash
python3 --version
```

**Install (macOS):**
```bash
brew install python@3.11
```

**Install (Ubuntu/Debian):**
```bash
sudo apt update
sudo apt install python3.11 python3.11-venv python3.11-dev
```

**Install (Windows):**
Download from https://www.python.org/downloads/

#### 2. Git

**Check if installed:**
```bash
git --version
```

**Install (macOS):**
```bash
brew install git
```

**Install (Ubuntu/Debian):**
```bash
sudo apt install git
```

**Install (Windows):**
Download from https://git-scm.com/download/win

#### 3. Docker Desktop

**Why needed:** For local development and testing

**Install:**
- macOS/Windows: https://www.docker.com/products/docker-desktop
- Linux: https://docs.docker.com/engine/install/

**Verify:**
```bash
docker --version
docker-compose --version
```

#### 4. Code Editor

**Recommended:** VS Code with extensions:
- Python
- Pylance
- Docker
- GitLens
- Better Comments

**Alternative:** PyCharm Professional, Cursor, Windsurf

---

## Project Initialization

### Step 1: Create Project Directory

```bash
# Create project directory
mkdir your-project-name
cd your-project-name

# Initialize git repository
git init

# Create .gitignore
cat > .gitignore << 'EOF'
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Virtual Environment
venv/
env/
ENV/
.venv

# Environment Variables
.env
.env.local
.env.*.local

# IDE
.vscode/
.idea/
*.swp
*.swo
*~

# OS
.DS_Store
Thumbs.db

# Logs
*.log
logs/

# Database
*.db
*.sqlite3

# Docker
docker-compose.override.yml

# Testing
.pytest_cache/
.coverage
htmlcov/
.tox/

# Temporary
tmp/
temp/
*.tmp
EOF
```

### Step 2: Create Directory Structure

```bash
# Create main directories
mkdir -p src/{config,db,session,models,routers,services,schemas,utils}
mkdir -p supabase/migrations
mkdir -p tests/{unit,integration}
mkdir -p Documentation
mkdir -p static
mkdir -p logs

# Create __init__.py files
touch src/__init__.py
touch src/config/__init__.py
touch src/db/__init__.py
touch src/session/__init__.py
touch src/models/__init__.py
touch src/routers/__init__.py
touch src/services/__init__.py
touch src/schemas/__init__.py
touch src/utils/__init__.py
touch tests/__init__.py
touch tests/unit/__init__.py
touch tests/integration/__init__.py
```

**Your structure should look like:**
```
your-project-name/
├── src/
│   ├── __init__.py
│   ├── main.py                    # (create next)
│   ├── config/
│   │   ├── __init__.py
│   │   ├── settings.py            # (create in doc 02)
│   │   └── logging_config.py      # (create in doc 03)
│   ├── db/
│   │   ├── __init__.py
│   │   └── engine.py              # (create in doc 02)
│   ├── session/
│   │   ├── __init__.py
│   │   └── async_session.py       # (create in doc 02)
│   ├── models/
│   │   ├── __init__.py
│   │   ├── base.py                # (create in doc 03)
│   │   └── enums.py               # (create in doc 04)
│   ├── routers/
│   │   └── __init__.py
│   ├── services/
│   │   └── __init__.py
│   ├── schemas/
│   │   └── __init__.py
│   └── utils/
│       └── __init__.py
├── supabase/
│   └── migrations/
├── tests/
│   ├── __init__.py
│   ├── unit/
│   │   └── __init__.py
│   └── integration/
│       └── __init__.py
├── Documentation/
├── static/
├── logs/
├── .gitignore
└── README.md
```

### Step 3: Create Virtual Environment

```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
# macOS/Linux:
source venv/bin/activate

# Windows:
# venv\Scripts\activate

# Verify activation (should show venv path)
which python
```

**Important:** Always activate the virtual environment before working on the project.

### Step 4: Create requirements.txt

Create `requirements.txt` in project root:

```txt
# Core FastAPI
fastapi==0.115.8
uvicorn==0.34.0
pydantic==2.10.6
pydantic-settings==2.7.1
starlette==0.40.0

# Database
SQLAlchemy==2.0.38
asyncpg==0.30.0
psycopg[binary]==3.2.5
greenlet==3.1.1

# HTTP and API
aiohttp>=3.9.3
httpx
requests==2.32.3
python-multipart==0.0.6

# Supabase
supabase

# Authentication
PyJWT==2.10.1
python-jose==3.3.0
cryptography==44.0.2

# Utilities
python-dotenv==1.0.0
PyYAML==6.0.2
orjson==3.10.15
tenacity==8.2.3
validators==0.20.0
email-validator==2.2.0

# Scraping (if needed)
beautifulsoup4==4.13.3
lxml>=5.2.2

# Scheduling
APScheduler==3.10.4

# Testing
pytest==7.4.3
pytest-asyncio==0.21.1
pytest-cov==4.1.0
httpx  # For testing FastAPI endpoints

# Development
black==23.12.1
flake8==6.1.0
mypy==1.7.1
```

### Step 5: Install Dependencies

```bash
# Upgrade pip
pip install --upgrade pip

# Install dependencies
pip install -r requirements.txt

# Verify installation
pip list
```

### Step 6: Create Basic README.md

```bash
cat > README.md << 'EOF'
# Your Project Name

FastAPI application built with Supabase, deployed on Render with Vercel frontend.

## Tech Stack

- **Backend:** FastAPI, SQLAlchemy, asyncpg
- **Database:** Supabase (PostgreSQL)
- **Deployment:** Render (backend), Vercel (frontend)
- **Frontend:** React, Vite, TailwindCSS

## Setup

1. Clone repository
2. Create virtual environment: `python3 -m venv venv`
3. Activate: `source venv/bin/activate`
4. Install dependencies: `pip install -r requirements.txt`
5. Copy `.env.example` to `.env` and configure
6. Run: `uvicorn src.main:app --reload`

## Documentation

See `Documentation/` for complete setup guide.

## License

[Your License]
EOF
```

### Step 7: Create Minimal main.py

Create `src/main.py`:

```python
"""
Main FastAPI Application

This is the entry point for your FastAPI application.
"""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan event handler for FastAPI application.
    
    Handles startup and shutdown events.
    """
    logger.info("Starting up application...")
    
    # Startup logic here (schedulers, connections, etc.)
    
    yield  # Application runs here
    
    logger.info("Shutting down application...")
    
    # Shutdown logic here (close connections, etc.)


# Initialize FastAPI app
app = FastAPI(
    title="Your Project Name API",
    description="API for your project",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan,
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure properly in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Health check endpoint
@app.get("/health", tags=["health"])
async def health_check():
    """Basic health check endpoint."""
    return {"status": "ok"}


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Welcome to Your Project API",
        "docs": "/docs",
        "health": "/health"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

### Step 8: Test Basic Setup

```bash
# Run the application
uvicorn src.main:app --reload

# In another terminal, test the endpoints
curl http://localhost:8000/
curl http://localhost:8000/health

# Open browser to see docs
open http://localhost:8000/docs
```

**Expected Results:**
- Server starts without errors
- Root endpoint returns JSON
- Health check returns `{"status": "ok"}`
- Swagger docs load at `/docs`

---

## Git Repository Setup

### Step 1: Initial Commit

```bash
# Stage all files
git add .

# Create initial commit
git commit -m "Initial project setup

- Created project structure
- Added requirements.txt
- Created basic FastAPI app
- Added .gitignore and README"
```

### Step 2: Create GitHub Repository (Optional)

```bash
# Create repository on GitHub first, then:
git remote add origin https://github.com/yourusername/your-project-name.git
git branch -M main
git push -u origin main
```

### Step 3: Create .env.example

Create `.env.example` (template for environment variables):

```bash
cat > .env.example << 'EOF'
# Application Settings
ENVIRONMENT=development
HOST=0.0.0.0
PORT=8000
LOG_LEVEL=INFO

# Database (will configure in next document)
SUPABASE_URL=your_supabase_url_here
SUPABASE_ANON_KEY=your_supabase_anon_key_here
SUPABASE_SERVICE_ROLE_KEY=your_supabase_service_role_key_here
SUPABASE_DB_PASSWORD=your_supabase_db_password_here

# CORS
CORS_ORIGINS=*

# Add more as needed
EOF
```

**Note:** Never commit `.env` file (it's in .gitignore)

---

## Docker Setup (Optional but Recommended)

### Create Dockerfile

Create `Dockerfile` in project root:

```dockerfile
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first (for caching)
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose port
EXPOSE 8000

# Run application
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Create docker-compose.yml

Create `docker-compose.yml` in project root:

```yaml
version: '3.8'

services:
  app:
    build: .
    ports:
      - "8000:8000"
    environment:
      - ENVIRONMENT=development
      - LOG_LEVEL=INFO
    env_file:
      - .env
    volumes:
      - .:/app
      - /app/venv  # Exclude venv from mount
    command: uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload
```

### Test Docker Setup

```bash
# Build and run
docker-compose up --build

# Test in another terminal
curl http://localhost:8000/health

# Stop
docker-compose down
```

---

## Development Tools Setup

### VS Code Settings

Create `.vscode/settings.json`:

```json
{
    "python.defaultInterpreterPath": "${workspaceFolder}/venv/bin/python",
    "python.linting.enabled": true,
    "python.linting.pylintEnabled": false,
    "python.linting.flake8Enabled": true,
    "python.formatting.provider": "black",
    "editor.formatOnSave": true,
    "editor.codeActionsOnSave": {
        "source.organizeImports": true
    },
    "python.testing.pytestEnabled": true,
    "python.testing.unittestEnabled": false,
    "files.exclude": {
        "**/__pycache__": true,
        "**/*.pyc": true
    }
}
```

### Pre-commit Hooks (Optional)

```bash
# Install pre-commit
pip install pre-commit

# Create .pre-commit-config.yaml
cat > .pre-commit-config.yaml << 'EOF'
repos:
  - repo: https://github.com/psf/black
    rev: 23.12.1
    hooks:
      - id: black
        language_version: python3.11

  - repo: https://github.com/pycqa/flake8
    rev: 6.1.0
    hooks:
      - id: flake8
        args: ['--max-line-length=100', '--extend-ignore=E203,W503']

  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.5.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-added-large-files
EOF

# Install hooks
pre-commit install
```

---

## Verification Checklist

Before proceeding to the next document, verify:

- [ ] Python 3.11+ installed and working
- [ ] Virtual environment created and activated
- [ ] All dependencies installed without errors
- [ ] Project structure created correctly
- [ ] Basic FastAPI app runs at http://localhost:8000
- [ ] `/health` endpoint returns `{"status": "ok"}`
- [ ] `/docs` shows Swagger UI
- [ ] Git repository initialized
- [ ] `.gitignore` configured
- [ ] `.env.example` created
- [ ] Docker setup working (optional)
- [ ] Code editor configured

---

## Troubleshooting

### Issue: Python version mismatch

**Problem:** `python3 --version` shows wrong version

**Solution:**
```bash
# macOS with Homebrew
brew install python@3.11
brew link python@3.11

# Use explicit version
python3.11 -m venv venv
```

### Issue: pip install fails

**Problem:** Compilation errors during `pip install`

**Solution:**
```bash
# macOS
xcode-select --install

# Ubuntu/Debian
sudo apt install python3-dev build-essential

# Then retry
pip install -r requirements.txt
```

### Issue: Port 8000 already in use

**Problem:** `Address already in use`

**Solution:**
```bash
# Find process using port 8000
lsof -i :8000

# Kill the process
kill -9 <PID>

# Or use different port
uvicorn src.main:app --reload --port 8001
```

### Issue: Import errors

**Problem:** `ModuleNotFoundError: No module named 'src'`

**Solution:**
```bash
# Make sure you're in project root
pwd

# Make sure virtual environment is activated
which python

# Reinstall in development mode
pip install -e .
```

---

## Next Steps

✅ **Completed:** Basic project setup

**Next:** [02_DATABASE_SUPABASE.md](./02_DATABASE_SUPABASE.md) - Set up Supabase database and connection

---

## Quick Reference

### Common Commands

```bash
# Activate virtual environment
source venv/bin/activate

# Run development server
uvicorn src.main:app --reload

# Run with Docker
docker-compose up

# Install new package
pip install package-name
pip freeze > requirements.txt

# Run tests
pytest

# Format code
black src/

# Lint code
flake8 src/
```

### Project Structure Quick Reference

```
src/
├── main.py              # FastAPI app entry point
├── config/              # Configuration (settings, logging)
├── db/                  # Database engine
├── session/             # Session management
├── models/              # SQLAlchemy models
├── routers/             # API endpoints
├── services/            # Business logic
├── schemas/             # Pydantic schemas
└── utils/               # Utility functions
```

---

**Status:** ✅ Project setup complete  
**Next:** Database configuration with Supabase
