# FastAPI + Supabase + Vercel Stack - Complete Setup Guide

**Created:** 2025-11-21  
**Based On:** ScraperSky Backend Architecture  
**Status:** Production-Ready Blueprint

---

## What You'll Build

A production-ready FastAPI application with:

✅ **Zero Technical Debt** - Clean architecture from day one  
✅ **Workflow-Based Organization** - Clear data flow  
✅ **Supabase PostgreSQL** - Managed database with connection pooling  
✅ **Async Everything** - SQLAlchemy 2.0 + asyncpg  
✅ **Render Deployment** - Backend hosting  
✅ **Vercel Frontend** - React deployment  
✅ **Production Patterns** - Battle-tested in ScraperSky

---

## Quick Start (30 Minutes)

### For Experienced Developers

1. **Read:** [07_CRITICAL_PATTERNS.md](./07_CRITICAL_PATTERNS.md) - Non-negotiable patterns
2. **Copy:** [08_DEPENDENCIES.md](./08_DEPENDENCIES.md) - Get requirements.txt
3. **Copy:** [09_ENVIRONMENT_VARIABLES.md](./09_ENVIRONMENT_VARIABLES.md) - Get .env template
4. **Skim:** [04_WORKFLOW_ORGANIZATION.md](./04_WORKFLOW_ORGANIZATION.md) - Naming conventions
5. **Build:** Follow [01_PROJECT_SETUP.md](./01_PROJECT_SETUP.md) - 30 minutes to working app

---

## Complete Guide (1-2 Days)

### Core Setup (Required)

1. **[01_PROJECT_SETUP.md](./01_PROJECT_SETUP.md)** (30-45 min)
   - Prerequisites and tools
   - Project initialization
   - Directory structure
   - Virtual environment
   - Git repository

2. **[02_DATABASE_SUPABASE.md](./02_DATABASE_SUPABASE.md)** (45-60 min)
   - Supabase project creation
   - Database configuration
   - Connection pooling (Supavisor)
   - SQLAlchemy async setup
   - Migration system

3. **[03_BACKEND_ARCHITECTURE.md](./03_BACKEND_ARCHITECTURE.md)** (60-90 min)
   - FastAPI application structure
   - Router patterns
   - Service layer patterns
   - Dependency injection
   - Error handling
   - Logging configuration

4. **[04_WORKFLOW_ORGANIZATION.md](./04_WORKFLOW_ORGANIZATION.md)** (30 min)
   - Workflow-based naming conventions
   - File organization
   - Enum management
   - Complete examples

5. **[05_DEPLOYMENT.md](./05_DEPLOYMENT.md)** (45-60 min)
   - Render backend deployment
   - Vercel frontend deployment
   - Environment configuration
   - Health checks
   - Monitoring

### Reference Documents (As Needed)

6. **[07_CRITICAL_PATTERNS.md](./07_CRITICAL_PATTERNS.md)**
   - Supavisor connection requirements (MANDATORY)
   - Transaction boundaries (MANDATORY)
   - Dual-status workflow pattern
   - 3-phase long operations
   - Centralized enums

7. **[08_DEPENDENCIES.md](./08_DEPENDENCIES.md)**
   - Complete requirements.txt
   - Package explanations
   - Version pinning strategy
   - Optional dependencies

8. **[09_ENVIRONMENT_VARIABLES.md](./09_ENVIRONMENT_VARIABLES.md)**
   - Complete .env template
   - Variable explanations
   - Security best practices
   - Environment-specific configs

---

## Technology Stack

### Backend
- **FastAPI 0.115+** - Async Python web framework
- **SQLAlchemy 2.0+** - Async ORM
- **Pydantic 2.0+** - Data validation
- **asyncpg 0.30+** - PostgreSQL async driver
- **APScheduler 3.10+** - Background tasks
- **Uvicorn** - ASGI server

### Database
- **Supabase** - Managed PostgreSQL
- **Supavisor** - Connection pooling
- **Alembic** - Migrations (optional)

### Deployment
- **Render** - Backend hosting
- **Docker** - Containerization
- **Vercel** - Frontend hosting

### Frontend
- **React 18+** - UI framework
- **Vite** - Build tool
- **TailwindCSS** - Styling
- **shadcn/ui** - Components

---

## Key Principles

### 1. Code is Truth
- Code is the source of truth
- Documentation explains "why" and "how"
- When docs conflict with code, code wins

### 2. Workflow-Based Organization
- Name everything by workflow (WF1, WF2, etc.)
- Makes data flow immediately obvious
- Simplifies debugging and maintenance

### 3. Dual-Status Pattern
- Processable entities have TWO status fields
- Separates user intent from system state
- Enables reliable background processing

### 4. Transaction Boundaries
- Routers own transactions
- Services execute within transactions
- Never create transactions in services

### 5. 3-Phase Long Operations
- Phase 1: Write to database (fast)
- Phase 2: Perform computation (no DB connection)
- Phase 3: Write results back (fast)

---

## Critical Patterns (Must Follow)

### Supavisor Connection Parameters (MANDATORY)

```python
connect_args = {
    "statement_cache_size": 0,
    "prepared_statement_cache_size": 0,
}

execution_options = {
    "no_prepare": True,
    "raw_sql": True,
}
```

**Why:** Required for Supabase connection pooler compatibility

### Router Transaction Pattern (MANDATORY)

```python
@router.post("/items")
async def create_item(
    data: ItemCreate,
    session: AsyncSession = Depends(get_session_dependency)
):
    item = await ItemService.create_item(session, data)
    await session.commit()  # Router commits
    return item
```

**Why:** Clear responsibility, prevents deadlocks

---

## Project Structure

```
your-project/
├── src/
│   ├── main.py                    # FastAPI app entry point
│   ├── config/
│   │   ├── settings.py            # Environment configuration
│   │   └── logging_config.py      # Logging setup
│   ├── db/
│   │   └── engine.py              # Database engine
│   ├── session/
│   │   └── async_session.py       # Session management
│   ├── models/
│   │   ├── base.py                # Base model
│   │   ├── enums.py               # All enums
│   │   └── wf*_*.py               # Workflow models
│   ├── routers/
│   │   └── wf*_*_router.py        # Workflow routers
│   ├── services/
│   │   └── wf*_*_service.py       # Business logic
│   └── schemas/
│       └── wf*_*_schemas.py       # Pydantic schemas
├── supabase/
│   └── migrations/                # SQL migrations
├── tests/
│   ├── unit/
│   └── integration/
├── Documentation/
├── requirements.txt
├── .env
├── .env.example
├── Dockerfile
├── docker-compose.yml
└── README.md
```

---

## Common Pitfalls (Avoid These)

❌ **Modifying Supavisor connection parameters** - Causes connection failures  
❌ **Creating transactions in services** - Causes deadlocks  
❌ **Holding DB connections during long operations** - Exhausts connection pool  
❌ **Single status field for processable entities** - Confuses user intent with system state  
❌ **Not using workflow-based naming** - Makes codebase hard to navigate  
❌ **Skipping migration system** - Causes schema drift  
❌ **Not setting up proper logging** - Makes debugging impossible  
❌ **Deploying without health checks** - Can't monitor application health

---

## Success Criteria

After completing this guide, you will have:

✅ Working FastAPI application with async SQLAlchemy  
✅ Supabase PostgreSQL database with connection pooling  
✅ Workflow-based organization (routers, models, enums)  
✅ Background task scheduling with APScheduler  
✅ Proper error handling and logging  
✅ Docker containerization  
✅ Render backend deployment  
✅ React frontend with Vercel deployment  
✅ Complete test suite  
✅ Production-ready monitoring  
✅ Zero technical debt

---

## Getting Help

### Documentation References
- **FastAPI:** https://fastapi.tiangolo.com/
- **SQLAlchemy:** https://docs.sqlalchemy.org/
- **Supabase:** https://supabase.com/docs
- **Render:** https://render.com/docs
- **Vercel:** https://vercel.com/docs

### ScraperSky References
- **Architecture Decisions:** `../Architecture/`
- **Integration Playbook:** `../INTEGRATION_PLAYBOOK.md`
- **Development Philosophy:** `../DEVELOPMENT_PHILOSOPHY.md`

---

## What Makes This Different

### From Other Guides

**Traditional guides teach:**
- Basic FastAPI setup
- Simple CRUD operations
- Toy examples

**This guide teaches:**
- Production-proven patterns
- Zero technical debt architecture
- Battle-tested in real applications
- Workflow-based organization
- Complete deployment pipeline

### From ScraperSky

**ScraperSky is:**
- A specific application with specific workflows
- Complex with 7 workflows and 20+ routers
- Evolved over months of development

**This guide is:**
- A clean-slate blueprint
- Adaptable to any workflow structure
- Distilled best practices
- Ready to build on

---

## Next Steps

1. **Start Here:** [01_PROJECT_SETUP.md](./01_PROJECT_SETUP.md)
2. **Follow in Order:** Complete each document sequentially
3. **Test at Milestones:** Verify each phase works before proceeding
4. **Reference as Needed:** Use documents 07-09 for specific questions

---

## Document Maintenance

**Update this guide when:**
- New critical patterns are discovered
- Deployment procedures change
- Technology stack is upgraded
- Common pitfalls are identified

**Keep it:**
- Minimal and essential
- Production-focused
- Based on real experience
- Zero technical debt

---

**Welcome to building production-ready FastAPI applications.**

**Let's build something great.**
