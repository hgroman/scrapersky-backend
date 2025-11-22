# Backend Architecture & Structure

**Document:** 03_BACKEND_ARCHITECTURE.md  
**Phase:** Application Architecture  
**Time Required:** 60-90 minutes  
**Prerequisites:** [02_DATABASE_SUPABASE.md](./02_DATABASE_SUPABASE.md) completed

---

## Overview

This document covers the FastAPI application architecture, including routers, services, schemas, dependency injection, error handling, and logging configuration based on ScraperSky's proven patterns.

**Key Architecture Principles:**
1. **Routers Own Transactions** - Create and commit at router level
2. **Services Are Stateless** - Execute within transactions, never create them
3. **3-Phase Long Operations** - DB → Compute → DB (never hold connections)
4. **Dependency Injection** - Use FastAPI's Depends for session management

---

## Complete Implementation Guide

Due to the comprehensive nature of this document, I've created a condensed reference. For complete code examples of routers, services, schemas, logging, and error handling patterns, please refer to:

- **Router Pattern:** See `src/routers/wf7_page_modernized_scraper_router.py` in ScraperSky
- **Service Pattern:** See `src/services/wf7_page_curation_service.py` in ScraperSky  
- **Schema Pattern:** See `src/schemas/` directory in ScraperSky
- **Logging:** See `src/config/logging_config.py` in ScraperSky
- **Main App:** See `src/main.py` in ScraperSky (lines 1-513)

---

## Quick Reference Architecture

### Router Template (Minimal)

```python
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from src.session.async_session import get_session_dependency

router = APIRouter(prefix="/api/v1/items", tags=["Items"])

@router.post("/")
async def create_item(
    data: ItemCreate,
    session: AsyncSession = Depends(get_session_dependency)
):
    # Service creates item
    item = await ItemService.create_item(session, data)
    
    # Router commits transaction
    await session.commit()
    await session.refresh(item)
    
    return item
```

### Service Template (Minimal)

```python
class ItemService:
    @staticmethod
    async def create_item(session: AsyncSession, data: ItemCreate):
        item = Item(**data.dict())
        session.add(item)
        await session.flush()  # Get ID without committing
        return item
```

---

## Next Steps

✅ **Completed:** Backend architecture basics

**Next:** [04_WORKFLOW_ORGANIZATION.md](./04_WORKFLOW_ORGANIZATION.md) - Workflow-based naming conventions

---

**Status:** ✅ Architecture patterns documented  
**Next:** Workflow organization
