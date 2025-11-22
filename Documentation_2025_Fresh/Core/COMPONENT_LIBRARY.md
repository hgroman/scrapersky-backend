# Component Library (The Approved Patterns)

**Status:** MANDATORY
**Usage:** Copy these templates. Do not invent new patterns.

---

## 1. The Router Template (Standard CRUD + Dual Status)

**Source:** `src/routers/wf7_pages_router.py`

```python
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from src.db.session import get_session_dependency
from src.services.wfX_service import Service
from src.models.enums import CurationStatus, ProcessingStatus

router = APIRouter(tags=["WFX: Name"], prefix="/api/v3/resource")

@router.patch("/update-status")
async def update_status(
    ids: list[str],
    status: CurationStatus,
    session: AsyncSession = Depends(get_session_dependency)
):
    """
    Updates curation status.
    If status is 'Selected', AUTOMATICALLY queues for processing.
    """
    updated_count = 0
    queued_count = 0
    
    # 1. Get items
    items = await Service.get_items(session, ids)
    
    for item in items:
        # 2. Update Curation (User Intent)
        item.curation_status = status
        updated_count += 1
        
        # 3. Dual-Status Logic (System Trigger)
        if status == CurationStatus.Selected:
            item.processing_status = ProcessingStatus.Queued
            item.processing_error = None
            queued_count += 1
            
    # 4. Commit Transaction (Router Owns Commit)
    await session.commit()
    
    return {
        "updated": updated_count,
        "queued": queued_count
    }
```

---

## 2. The Service Template (Job Loop SDK)

**Source:** `src/services/wfX_processing_service.py`

```python
from src.common.curation_sdk.scheduler_loop import run_job_loop
from src.models.enums import ProcessingStatus

class WorkflowService:
    
    async def process_queue(self):
        """
        Standard Background Job Loop.
        """
        await run_job_loop(
            model=MyModel,
            status_enum=ProcessingStatus,
            queued_status=ProcessingStatus.Queued,
            processing_status=ProcessingStatus.Processing,
            completed_status=ProcessingStatus.Complete,
            failed_status=ProcessingStatus.Error,
            processing_function=self.process_single_item,
            batch_size=10,
            status_field_name="processing_status",
            error_field_name="processing_error"
        )

    async def process_single_item(self, item, session):
        """
        Business Logic for a single item.
        Transaction is managed by SDK. DO NOT COMMIT here.
        """
        # 1. Do work (e.g. API call)
        result = await external_api.fetch(item.url)
        
        # 2. Update item
        item.data = result
        
        # 3. Return (SDK sets status to Complete)
```

---

## 3. The Model Template

**Source:** `src/models/base.py`

```python
from src.models.base import Base, UUIDMixin, TimestampMixin
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, Text

class MyResource(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "my_resources"
    
    # 1. Core Data
    name: Mapped[str] = mapped_column(String, nullable=False)
    
    # 2. Dual Status Columns
    curation_status: Mapped[str] = mapped_column(String, default="New")
    processing_status: Mapped[str] = mapped_column(String, nullable=True)
    processing_error: Mapped[str] = mapped_column(Text, nullable=True)
```

---

## 4. The Scheduler Template

**Source:** `src/services/background/wfX_scheduler.py`

```python
from src.scheduler_instance import scheduler
from src.config.settings import settings
from src.services.wfX_service import Service

def start_scheduler():
    service = Service()
    
    scheduler.add_job(
        service.process_queue,
        trigger="interval",
        minutes=settings.SCHEDULER_INTERVAL_MINUTES,
        id="wfx_job_id",
        replace_existing=True
    )
```
