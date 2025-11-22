# FastAPI + Supabase + Vercel Stack - Complete Setup Guide

**Created:** 2025-11-21  
**Based On:** ScraperSky Backend Architecture  
**Status:** Zero Technical Debt Blueprint  
**Philosophy:** Workflow-Based Organization, Production-Proven Patterns

---

## Purpose

This guide provides a complete, step-by-step blueprint for building a new FastAPI application from scratch using the proven patterns from ScraperSky. Follow this guide to create a production-ready application with:

✅ **Zero Technical Debt** - Clean architecture from day one  
✅ **Workflow-Based Organization** - All routers, models, and enums named by workflow  
✅ **Production-Proven Patterns** - Battle-tested in ScraperSky  
✅ **Complete Documentation** - Every step explained  
✅ **Supabase Integration** - PostgreSQL with connection pooling  
✅ **Render Deployment** - Backend hosting  
✅ **Vercel Frontend** - React frontend deployment  

---

## Documentation Structure

### Core Setup Documents

1. **[01_PROJECT_SETUP.md](./01_PROJECT_SETUP.md)**
   - Prerequisites and tools
   - Project initialization
   - Directory structure
   - Virtual environment setup
   - Git repository setup

2. **[02_DATABASE_SUPABASE.md](./02_DATABASE_SUPABASE.md)**
   - Supabase project creation
   - Database configuration
   - Connection pooling (Supavisor)
   - Environment variables
   - Migration system setup

3. **[03_BACKEND_ARCHITECTURE.md](./03_BACKEND_ARCHITECTURE.md)**
   - FastAPI application structure
   - SQLAlchemy async setup
   - Router patterns
   - Service layer patterns
   - Dependency injection
   - Error handling
   - Logging configuration

4. **[04_WORKFLOW_ORGANIZATION.md](./04_WORKFLOW_ORGANIZATION.md)**
   - Workflow-based naming conventions
   - Router organization
   - Model organization
   - Enum organization
   - Service organization
   - Complete examples

5. **[05_DEPLOYMENT.md](./05_DEPLOYMENT.md)**
   - Render backend deployment
   - Environment configuration
   - Docker setup
   - Health checks
   - Monitoring

6. **[06_FRONTEND_INTEGRATION.md](./06_FRONTEND_INTEGRATION.md)**
   - React + Vite setup
   - Vercel deployment
   - API integration
   - Authentication
   - CORS configuration

### Reference Documents

7. **[07_CRITICAL_PATTERNS.md](./07_CRITICAL_PATTERNS.md)**
   - Supavisor connection requirements
   - Dual-status workflow pattern
   - Transaction boundaries
   - 3-phase long operations
   - Retry logic patterns

8. **[08_DEPENDENCIES.md](./08_DEPENDENCIES.md)**
   - Complete requirements.txt
   - Package explanations
   - Version compatibility
   - Optional dependencies

9. **[09_ENVIRONMENT_VARIABLES.md](./09_ENVIRONMENT_VARIABLES.md)**
   - Complete .env template
   - Variable explanations
   - Development vs production
   - Security considerations

10. **[10_TESTING_STRATEGY.md](./10_TESTING_STRATEGY.md)**
    - Test structure
    - Docker testing
    - Integration tests
    - API testing
    - Database testing

---

## Quick Start Path

### For Experienced Developers

If you're familiar with FastAPI and just want the essentials:

1. Read **[07_CRITICAL_PATTERNS.md](./07_CRITICAL_PATTERNS.md)** - Non-negotiable patterns
2. Copy **[08_DEPENDENCIES.md](./08_DEPENDENCIES.md)** - Get requirements.txt
3. Copy **[09_ENVIRONMENT_VARIABLES.md](./09_ENVIRONMENT_VARIABLES.md)** - Get .env template
4. Skim **[04_WORKFLOW_ORGANIZATION.md](./04_WORKFLOW_ORGANIZATION.md)** - Naming conventions
5. Reference **[03_BACKEND_ARCHITECTURE.md](./03_BACKEND_ARCHITECTURE.md)** - Code templates

**Time:** 2-3 hours to working application

### For Complete Setup

If you want the full guided experience:

1. Follow documents 01-06 in order
2. Reference 07-10 as needed
3. Test at each milestone
4. Deploy incrementally

**Time:** 1-2 days to production-ready application

---

## What Makes This Different

### Workflow-Based Organization

**Traditional Approach:**
```
routers/
  users.py
  products.py
  orders.py
```

**ScraperSky Approach:**
```
routers/
  wf1_user_registration_router.py
  wf2_product_catalog_router.py
  wf3_order_processing_router.py
```

**Why:** Immediately understand data flow and dependencies

### Zero Technical Debt

This guide teaches you to:
- ✅ Set up correctly from day one
- ✅ Use proven patterns (not experiments)
- ✅ Avoid common pitfalls
- ✅ Build for production (not just development)

### Production-Proven

Every pattern in this guide is:
- ✅ Used in production ScraperSky
- ✅ Battle-tested under load
- ✅ Debugged and optimized
- ✅ Documented with lessons learned

---

## Architecture Overview

### Technology Stack

**Backend:**
- FastAPI 0.115+ (async Python web framework)
- SQLAlchemy 2.0+ (async ORM)
- Pydantic 2.0+ (data validation)
- asyncpg 0.30+ (PostgreSQL async driver)
- APScheduler 3.10+ (background tasks)
- Uvicorn (ASGI server)

**Database:**
- Supabase (managed PostgreSQL)
- Supavisor (connection pooling)
- Alembic (migrations)

**Deployment:**
- Render (backend hosting)
- Docker (containerization)
- Vercel (frontend hosting)

**Frontend:**
- React 18+ (UI framework)
- Vite (build tool)
- TailwindCSS (styling)
- shadcn/ui (components)

### Application Structure

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
│   └── (this guide)
├── requirements.txt
├── .env
├── .env.example
├── Dockerfile
├── docker-compose.yml
└── README.md
```

---

## Key Principles

### 1. Code is Truth

- Code is the source of truth
- Documentation explains "why" and "how"
- When docs conflict with code, code wins
- Keep docs minimal and essential

### 2. Workflow-Based Organization

- Name everything by workflow (WF1, WF2, etc.)
- Routers, models, services, enums all follow workflow naming
- Makes data flow immediately obvious
- Simplifies debugging and maintenance

### 3. Dual-Status Pattern

- Processable entities have TWO status fields:
  - `curation_status` - User intent (Selected, Queued, Complete)
  - `processing_status` - System state (Queued, Processing, Complete, Error)
- Separates user actions from system state
- Enables reliable background processing

### 4. Transaction Boundaries

- Routers own transactions
- Services execute within transactions
- Never create transactions in services
- Prevents deadlocks and connection leaks

### 5. 3-Phase Long Operations

For operations that take >1 second:
1. **Phase 1:** Write to database (fast)
2. **Phase 2:** Perform computation (no DB connection held)
3. **Phase 3:** Write results back (fast)

Never hold database connections during long operations.

---

## Critical Patterns (Must Follow)

### Supavisor Connection Parameters

**MANDATORY** - Do not modify:
```python
connect_args = {
    "statement_cache_size": 0,
    "prepared_statement_cache_size": 0,
    "prepared_statement_name_func": lambda: f"__asyncpg_{uuid4()}__",
}

execution_options = {
    "isolation_level": "READ COMMITTED",
    "no_prepare": True,
    "raw_sql": True,
}
```

**Why:** Supabase connection pooler (Supavisor) requires these exact parameters. Modifying them causes connection failures.

### Router Transaction Pattern

**MANDATORY:**
```python
@router.post("/items")
async def create_item(
    data: ItemCreate,
    session: AsyncSession = Depends(get_session_dependency)
):
    # Router owns the transaction
    item = await item_service.create_item(session, data)
    await session.commit()  # Router commits
    return item
```

**Why:** Clear responsibility, prevents deadlocks, enables proper error handling.

### Dual-Status Adapter Pattern

**MANDATORY for processable entities:**
```python
# User-facing status
item.curation_status = "Selected"

# Adapter converts to system status
if item.curation_status == "Selected":
    item.processing_status = "Queued"

# Scheduler processes based on system status
items = await session.execute(
    select(Item).where(Item.processing_status == "Queued")
)
```

**Why:** Separates user intent from system state, enables reliable automation.

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

## Next Steps

1. **Start Here:** [01_PROJECT_SETUP.md](./01_PROJECT_SETUP.md)
2. **Follow in Order:** Complete each document sequentially
3. **Test at Milestones:** Verify each phase works before proceeding
4. **Reference as Needed:** Use documents 07-10 for specific questions

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

**Welcome to building production-ready FastAPI applications. Let's build something great.**
