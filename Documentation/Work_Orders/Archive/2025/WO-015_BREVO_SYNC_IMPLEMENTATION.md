# Work Order 015: Brevo Contact Sync Implementation
**Created:** 2025-01-18
**Priority:** P1 (High Priority)
**Status:** Draft - Awaiting Review
**Assignee:** Local Claude AI
**Reviewer:** User

---

## Executive Summary

Implement Brevo contact synchronization capability for ScraperSky, mirroring the existing HubSpot sync pattern. This implementation will enable users to select contacts and sync them to Brevo CRM via dedicated endpoints and background processing.

**Key Requirements:**
- Multi-platform sync support (HubSpot + Brevo + future Mautic)
- New dedicated Brevo endpoints (not reusing generic batch update)
- Background scheduler for async processing
- Full error handling and retry logic
- Extensible architecture for future CRM integrations

---

## Context & Background

### Current State
- ✅ Contacts table exists with full CRUD operations (`src/routers/v3/contacts_router.py`)
- ✅ HubSpot sync infrastructure already implemented:
  - `hubspot_sync_status` (curation status)
  - `hubspot_processing_status` (processing state)
  - `hubspot_processing_error` (error tracking)
- ✅ Dual-status pattern established and working
- ✅ SDK job loop pattern in use for schedulers

### Desired State
- ✅ Brevo sync fields added to contacts table
- ✅ Dedicated Brevo sync endpoints (`/api/v3/contacts/brevo/...`)
- ✅ Brevo sync service for API integration
- ✅ Background scheduler for async processing
- ✅ Frontend can select contacts and trigger Brevo sync
- ✅ Extensible architecture ready for Mautic integration

### Related Work Orders
- **WO-004:** Multi-scheduler patterns and background task triggers
- **WO-005:** Knowledge repository and system patterns
- **Reference:** HubSpot sync implementation (existing)

---

## Architecture Decision: Multi-Platform Sync Pattern

### Design Philosophy
Each CRM platform gets:
1. **Dedicated status fields** (independent sync states)
2. **Dedicated endpoints** (platform-specific operations)
3. **Dedicated service** (platform-specific API logic)
4. **Dedicated scheduler** (independent processing loops)

### Why Not Shared/Generic?
- ❌ Different CRM APIs have different requirements
- ❌ Different retry/error handling strategies per platform
- ❌ Different rate limits and quotas
- ❌ Users may want to sync to multiple platforms simultaneously
- ✅ Explicit separation = easier debugging and maintenance

### Pattern Reference
See `src/models/WF7_V2_L1_1of1_ContactModel.py` lines 38-49 for HubSpot pattern.

---

## Phase 1: Database Schema Changes

### 1.1 Add Brevo ENUMs to `src/models/enums.py`

**Location:** After line 67 (after HubSpotProcessingStatus)

```python
class BrevoSyncStatus(str, Enum):
    """Status values for Brevo sync workflow (curation status)"""

    New = "New"            # Initial state, not queued
    Queued = "Queued"      # User selected for Brevo sync
    Processing = "Processing"  # Currently syncing to Brevo
    Complete = "Complete"  # Successfully synced to Brevo
    Error = "Error"        # Sync failed (see brevo_processing_error)
    Skipped = "Skipped"    # Intentionally skipped (e.g., invalid email)


class BrevoProcessingStatus(str, Enum):
    """Status values for Brevo processing workflow (system state)"""

    Queued = "Queued"      # Waiting for scheduler pickup
    Processing = "Processing"  # Currently syncing
    Complete = "Complete"  # Sync successful
    Error = "Error"        # Sync failed
```

**Why These Values:**
- Mirrors HubSpotSyncStatus for consistency
- `New` = default state (not queued for sync)
- `Queued` = user selected, waiting for scheduler
- `Processing` = actively syncing to Brevo API
- `Complete` = successfully synced
- `Error` = sync failed, see error field
- `Skipped` = intentionally not synced (e.g., bounced email)

---

### 1.2 Add Brevo Fields to Contact Model

**File:** `src/models/WF7_V2_L1_1of1_ContactModel.py`
**Location:** After line 49 (after hubspot_processing_error)

```python
    # Brevo sync status fields (mirrors HubSpot pattern)
    brevo_sync_status = Column(
        Enum('New', 'Queued', 'Processing', 'Complete', 'Error', 'Skipped', name='brevo_sync_status'),
        nullable=False,
        default='New',
        index=True,
    )
    brevo_processing_status = Column(
        Enum('Queued', 'Processing', 'Complete', 'Error', name='brevo_sync_processing_status'),
        nullable=True,
        index=True,
    )
    brevo_processing_error = Column(Text, nullable=True)
    brevo_contact_id = Column(String, nullable=True, index=True)  # Brevo's contact ID after sync
```

**New Field Explanation:**
- `brevo_contact_id`: Stores Brevo's unique contact ID after successful sync (useful for updates/deduplication)

---

### 1.3 Database Migration

**Task:** Create Alembic migration script

**Commands:**
```bash
# Generate migration
alembic revision --autogenerate -m "Add Brevo sync fields to contacts table"

# Review generated migration
# Edit if needed (check ENUM creation order)

# Apply migration
alembic upgrade head
```

**Critical Notes:**
- ⚠️ ENUMs must be created BEFORE columns that reference them
- ⚠️ Check migration for proper ENUM creation: `CREATE TYPE brevo_sync_status AS ENUM (...);`
- ⚠️ Existing contacts should default to `brevo_sync_status = 'New'`

**Migration Verification Query:**
```sql
-- Verify columns exist
SELECT column_name, data_type, is_nullable, column_default
FROM information_schema.columns
WHERE table_name = 'contacts'
AND column_name LIKE 'brevo%';

-- Verify ENUMs created
SELECT typname FROM pg_type WHERE typname LIKE 'brevo%';

-- Check all contacts have default status
SELECT COUNT(*), brevo_sync_status
FROM contacts
GROUP BY brevo_sync_status;
```

---

## Phase 2: Schema Updates

### 2.1 Update Pydantic Schemas

**File:** `src/schemas/contact_schemas.py`

**Add to imports:**
```python
from src.models.enums import (
    ...,
    BrevoSyncStatus,
    BrevoProcessingStatus,
)
```

**Add new request schema (after ContactCurationFilteredUpdateRequest):**
```python
class BrevoSyncBatchRequest(BaseModel):
    """Request to queue contacts for Brevo sync"""
    contact_ids: List[uuid.UUID]

    model_config = ConfigDict(from_attributes=True)


class BrevoSyncFilteredRequest(BaseModel):
    """Request to queue contacts for Brevo sync using filters"""
    # Filter criteria (same as list endpoint)
    contact_curation_status: Optional[ContactCurationStatus] = None
    contact_processing_status: Optional[ContactProcessingStatus] = None
    email_type: Optional[ContactEmailTypeEnum] = None
    domain_id: Optional[uuid.UUID] = None
    page_id: Optional[uuid.UUID] = None
    email_contains: Optional[str] = None
    name_contains: Optional[str] = None
    has_gmail: Optional[bool] = None

    model_config = ConfigDict(from_attributes=True)


class BrevoSyncResponse(BaseModel):
    """Response for Brevo sync operations"""
    queued_count: int
    already_queued_count: int = 0
    skipped_count: int = 0
    message: str

    model_config = ConfigDict(from_attributes=True)
```

**Update ContactRead schema to include Brevo fields:**
```python
class ContactRead(BaseModel):
    id: uuid.UUID
    # ... existing fields ...

    # Add Brevo fields
    brevo_sync_status: BrevoSyncStatus
    brevo_processing_status: Optional[BrevoProcessingStatus] = None
    brevo_processing_error: Optional[str] = None
    brevo_contact_id: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)
```

---

## Phase 3: API Endpoints

### 3.1 Create Brevo Router

**File:** `src/routers/v3/brevo_contacts_router.py` (NEW FILE)

```python
"""
Brevo Contact Sync Router
Handles queuing contacts for Brevo CRM synchronization
"""

import uuid
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from src.auth.jwt_auth import get_current_user
from src.db.session import get_db_session
from src.models.enums import (
    ContactCurationStatus,
    ContactEmailTypeEnum,
    ContactProcessingStatus,
    BrevoSyncStatus,
    BrevoProcessingStatus,
)
from src.models.WF7_V2_L1_1of1_ContactModel import Contact
from src.schemas.contact_schemas import (
    BrevoSyncBatchRequest,
    BrevoSyncFilteredRequest,
    BrevoSyncResponse,
)

router = APIRouter(
    prefix="/api/v3/contacts/brevo",
    tags=["Brevo Sync"],
    responses={404: {"description": "Not found"}},
)


@router.post("/sync/batch", response_model=BrevoSyncResponse)
async def queue_contacts_for_brevo_sync_batch(
    request: BrevoSyncBatchRequest,
    session: AsyncSession = Depends(get_db_session),
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    """
    Queue specific contacts for Brevo sync by contact IDs.

    Sets brevo_sync_status = 'Queued' and brevo_processing_status = 'Queued'.
    Scheduler will pick up queued contacts and sync to Brevo API.
    """
    if not request.contact_ids:
        return BrevoSyncResponse(
            queued_count=0,
            message="No contact IDs provided"
        )

    stmt = select(Contact).where(Contact.id.in_(request.contact_ids))
    result = await session.execute(stmt)
    contacts = result.scalars().all()

    if not contacts:
        raise HTTPException(
            status_code=404,
            detail="No contacts found with provided IDs"
        )

    queued_count = 0
    already_queued_count = 0
    skipped_count = 0

    for contact in contacts:
        # Skip if already queued or processing
        if contact.brevo_sync_status in [BrevoSyncStatus.Queued, BrevoSyncStatus.Processing]:
            already_queued_count += 1
            continue

        # Skip if no email
        if not contact.email:
            skipped_count += 1
            contact.brevo_sync_status = BrevoSyncStatus.Skipped.value
            contact.brevo_processing_error = "No email address"
            continue

        # Queue for sync
        contact.brevo_sync_status = BrevoSyncStatus.Queued.value
        contact.brevo_processing_status = BrevoProcessingStatus.Queued.value
        contact.brevo_processing_error = None  # Clear previous errors
        queued_count += 1

    await session.commit()

    return BrevoSyncResponse(
        queued_count=queued_count,
        already_queued_count=already_queued_count,
        skipped_count=skipped_count,
        message=f"Queued {queued_count} contacts for Brevo sync"
    )


@router.post("/sync/filtered", response_model=BrevoSyncResponse)
async def queue_contacts_for_brevo_sync_filtered(
    request: BrevoSyncFilteredRequest,
    session: AsyncSession = Depends(get_db_session),
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    """
    Queue contacts for Brevo sync using filter criteria.

    Allows bulk queuing based on:
    - Contact curation/processing status
    - Email type (SERVICE, CORPORATE, FREE, UNKNOWN)
    - Domain or page association
    - Email/name search
    - Gmail flag
    """
    filters = []

    if request.contact_curation_status:
        filters.append(Contact.contact_curation_status == request.contact_curation_status.value)
    if request.contact_processing_status:
        filters.append(Contact.contact_processing_status == request.contact_processing_status.value)
    if request.email_type:
        filters.append(Contact.email_type == request.email_type.value)
    if request.domain_id:
        filters.append(Contact.domain_id == request.domain_id)
    if request.page_id:
        filters.append(Contact.page_id == request.page_id)
    if request.email_contains:
        filters.append(Contact.email.ilike(f"%{request.email_contains}%"))
    if request.name_contains:
        filters.append(Contact.name.ilike(f"%{request.name_contains}%"))
    if request.has_gmail is not None:
        filters.append(Contact.has_gmail == request.has_gmail)

    stmt = select(Contact).where(*filters)
    result = await session.execute(stmt)
    contacts = result.scalars().all()

    if not contacts:
        return BrevoSyncResponse(
            queued_count=0,
            message="No contacts match the provided filters"
        )

    queued_count = 0
    already_queued_count = 0
    skipped_count = 0

    for contact in contacts:
        # Skip if already queued or processing
        if contact.brevo_sync_status in [BrevoSyncStatus.Queued, BrevoSyncStatus.Processing]:
            already_queued_count += 1
            continue

        # Skip if no email
        if not contact.email:
            skipped_count += 1
            contact.brevo_sync_status = BrevoSyncStatus.Skipped.value
            contact.brevo_processing_error = "No email address"
            continue

        # Queue for sync
        contact.brevo_sync_status = BrevoSyncStatus.Queued.value
        contact.brevo_processing_status = BrevoProcessingStatus.Queued.value
        contact.brevo_processing_error = None
        queued_count += 1

    await session.commit()

    return BrevoSyncResponse(
        queued_count=queued_count,
        already_queued_count=already_queued_count,
        skipped_count=skipped_count,
        message=f"Queued {queued_count} contacts for Brevo sync (filtered)"
    )


@router.get("/status/summary")
async def get_brevo_sync_status_summary(
    session: AsyncSession = Depends(get_db_session),
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    """
    Get summary of Brevo sync status counts.

    Returns count of contacts in each sync state:
    - New (not yet queued)
    - Queued (waiting for sync)
    - Processing (currently syncing)
    - Complete (successfully synced)
    - Error (sync failed)
    - Skipped (intentionally not synced)
    """
    from sqlalchemy import func

    stmt = (
        select(Contact.brevo_sync_status, func.count(Contact.id))
        .group_by(Contact.brevo_sync_status)
    )
    result = await session.execute(stmt)
    status_counts = dict(result.all())

    return {
        "new": status_counts.get("New", 0),
        "queued": status_counts.get("Queued", 0),
        "processing": status_counts.get("Processing", 0),
        "complete": status_counts.get("Complete", 0),
        "error": status_counts.get("Error", 0),
        "skipped": status_counts.get("Skipped", 0),
        "total_contacts": sum(status_counts.values()),
    }
```

**Why Separate Router:**
- ✅ Clear separation of concerns (Brevo-specific operations)
- ✅ Easier to add Brevo-specific endpoints later (webhooks, status checks, etc.)
- ✅ Independent from generic contact CRUD operations
- ✅ Sets pattern for future Mautic integration

---

### 3.2 Update Main App to Register Router

**File:** `src/main.py`

**Add import:**
```python
from src.routers.v3 import brevo_contacts_router
```

**Add router registration (after existing contact router):**
```python
app.include_router(brevo_contacts_router.router)
```

---

### 3.3 Update Existing Contacts Router

**File:** `src/routers/v3/contacts_router.py`

**Add Brevo imports to line 17:**
```python
from src.models.enums import (
    ...,
    BrevoSyncStatus,  # ADD
)
```

**Update list_contacts function (line 103) - add Brevo filter:**
```python
@router.get("", response_model=List[ContactRead])
async def list_contacts(
    session: AsyncSession = Depends(get_db_session),
    current_user: Dict[str, Any] = Depends(get_current_user),
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    contact_curation_status: Optional[ContactCurationStatus] = Query(None),
    contact_processing_status: Optional[ContactProcessingStatus] = Query(None),
    hubspot_sync_status: Optional[HubSpotSyncStatus] = Query(None),
    brevo_sync_status: Optional[BrevoSyncStatus] = Query(None),  # ADD THIS
    email_type: Optional[ContactEmailTypeEnum] = Query(None),
    domain_id: Optional[uuid.UUID] = Query(None),
    page_id: Optional[uuid.UUID] = Query(None),
    email_contains: Optional[str] = Query(None),
    name_contains: Optional[str] = Query(None),
    has_gmail: Optional[bool] = Query(None),
):
    """Retrieve a list of contacts with filtering and pagination."""
    filters = []
    if contact_curation_status:
        filters.append(Contact.contact_curation_status == contact_curation_status.value)
    if contact_processing_status:
        filters.append(Contact.contact_processing_status == contact_processing_status.value)
    if hubspot_sync_status:
        filters.append(Contact.hubspot_sync_status == hubspot_sync_status.value)
    if brevo_sync_status:  # ADD THIS BLOCK
        filters.append(Contact.brevo_sync_status == brevo_sync_status.value)
    # ... rest of function unchanged ...
```

---

## Phase 4: Service Layer

### 4.1 Create Brevo Sync Service

**File:** `src/services/brevo_sync_service.py` (NEW FILE)

```python
"""
Brevo Contact Sync Service
Handles synchronization of contacts to Brevo CRM via their API
"""

import logging
from typing import Optional
import httpx
from sqlalchemy.ext.asyncio import AsyncSession

from src.config.settings import settings
from src.models.WF7_V2_L1_1of1_ContactModel import Contact
from src.models.enums import BrevoSyncStatus, BrevoProcessingStatus

logger = logging.getLogger(__name__)


class BrevoSyncService:
    """Service for syncing contacts to Brevo CRM"""

    def __init__(self):
        self.api_key = settings.BREVO_API_KEY
        self.list_id = settings.BREVO_LIST_ID
        self.base_url = "https://api.brevo.com/v3"

        if not self.api_key:
            logger.warning("BREVO_API_KEY not configured - Brevo sync will fail")
        if not self.list_id:
            logger.warning("BREVO_LIST_ID not configured - contacts will sync without list assignment")

    async def process_single_contact(
        self,
        contact: Contact,
        session: AsyncSession
    ) -> None:
        """
        Process a single contact for Brevo sync.

        Called by scheduler via SDK job loop pattern.
        Updates contact.brevo_sync_status based on result.

        Args:
            contact: Contact model instance
            session: Async database session (managed by SDK)
        """
        logger.info(f"Processing Brevo sync for contact {contact.id} ({contact.email})")

        try:
            # Validate contact has email
            if not contact.email:
                raise ValueError("Contact has no email address")

            # Update to processing state
            contact.brevo_sync_status = BrevoSyncStatus.Processing.value
            contact.brevo_processing_status = BrevoProcessingStatus.Processing.value
            await session.commit()  # Commit status change immediately

            # Call Brevo API
            brevo_contact_id = await self._sync_to_brevo_api(contact)

            # Update to complete state
            contact.brevo_sync_status = BrevoSyncStatus.Complete.value
            contact.brevo_processing_status = BrevoProcessingStatus.Complete.value
            contact.brevo_processing_error = None
            contact.brevo_contact_id = brevo_contact_id

            logger.info(f"Successfully synced contact {contact.id} to Brevo (Brevo ID: {brevo_contact_id})")

        except Exception as e:
            error_msg = str(e)
            logger.exception(f"Failed to sync contact {contact.id} to Brevo: {error_msg}")

            # Update to error state
            contact.brevo_sync_status = BrevoSyncStatus.Error.value
            contact.brevo_processing_status = BrevoProcessingStatus.Error.value
            contact.brevo_processing_error = error_msg[:500]  # Truncate long errors

            # Don't re-raise - let SDK handle transaction

    async def _sync_to_brevo_api(self, contact: Contact) -> Optional[str]:
        """
        Sync contact to Brevo via API.

        API Documentation: https://developers.brevo.com/reference/createcontact

        Returns:
            Brevo contact ID (email address) if successful

        Raises:
            httpx.HTTPError: If API request fails
            ValueError: If response is invalid
        """
        if not self.api_key:
            raise ValueError("BREVO_API_KEY not configured")

        headers = {
            "api-key": self.api_key,
            "Content-Type": "application/json",
        }

        # Build Brevo contact payload
        payload = {
            "email": contact.email,
            "attributes": {},
            "updateEnabled": True,  # Update if contact already exists
        }

        # Add optional attributes
        if contact.name:
            # Try to split name into first/last
            name_parts = contact.name.split(maxsplit=1)
            payload["attributes"]["FIRSTNAME"] = name_parts[0]
            if len(name_parts) > 1:
                payload["attributes"]["LASTNAME"] = name_parts[1]

        if contact.phone_number:
            payload["attributes"]["SMS"] = contact.phone_number

        # Add custom attributes
        if contact.domain_id:
            payload["attributes"]["DOMAIN_ID"] = str(contact.domain_id)
        if contact.page_id:
            payload["attributes"]["PAGE_ID"] = str(contact.page_id)
        if contact.email_type:
            payload["attributes"]["EMAIL_TYPE"] = contact.email_type
        if contact.source_url:
            payload["attributes"]["SOURCE_URL"] = contact.source_url

        # Add to list if configured
        if self.list_id:
            payload["listIds"] = [int(self.list_id)]

        logger.debug(f"Brevo API payload: {payload}")

        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{self.base_url}/contacts",
                headers=headers,
                json=payload,
            )

            # Brevo returns 201 for new contact, 204 for updated contact
            if response.status_code in [201, 204]:
                # Brevo uses email as contact ID
                return contact.email

            # Handle errors
            response.raise_for_status()

            # Shouldn't reach here but handle gracefully
            logger.warning(f"Unexpected Brevo API response: {response.status_code} - {response.text}")
            return contact.email
```

**Key Design Decisions:**
- ✅ Uses `process_single_contact()` signature compatible with SDK job loop
- ✅ Updates status to `Processing` immediately (commits early for visibility)
- ✅ Stores Brevo contact ID (email) for future reference
- ✅ Handles Brevo API errors gracefully (doesn't crash scheduler)
- ✅ Truncates long error messages to fit database field
- ✅ Uses `updateEnabled=True` to handle duplicate emails (idempotent)

---

### 4.2 Add Configuration Settings

**File:** `src/config/settings.py`

**Add Brevo configuration:**
```python
class Settings(BaseSettings):
    # ... existing settings ...

    # Brevo CRM Integration
    BREVO_API_KEY: Optional[str] = None
    BREVO_LIST_ID: Optional[str] = None  # Target list ID for contacts

    # Brevo Scheduler Configuration
    BREVO_SYNC_SCHEDULER_INTERVAL_MINUTES: int = 5  # Default: every 5 minutes
    BREVO_SYNC_SCHEDULER_BATCH_SIZE: int = 10  # Process 10 contacts per run
    BREVO_SYNC_SCHEDULER_MAX_INSTANCES: int = 1  # Prevent overlapping runs
```

**Environment Variables (.env.example):**
```bash
# Brevo CRM Integration
BREVO_API_KEY=your_brevo_api_key_here
BREVO_LIST_ID=123  # Brevo list ID (numeric)

# Brevo Scheduler
BREVO_SYNC_SCHEDULER_INTERVAL_MINUTES=5
BREVO_SYNC_SCHEDULER_BATCH_SIZE=10
BREVO_SYNC_SCHEDULER_MAX_INSTANCES=1
```

---

### 4.3 Create Brevo Scheduler

**File:** `src/services/brevo_sync_scheduler.py` (NEW FILE)

```python
"""
Brevo Contact Sync Scheduler
Background scheduler that processes queued contacts for Brevo sync
"""

import logging
from sqlalchemy import asc
from src.scheduler_instance import scheduler
from src.config.settings import settings
from src.models.WF7_V2_L1_1of1_ContactModel import Contact
from src.models.enums import BrevoSyncStatus, BrevoProcessingStatus
from src.services.brevo_sync_service import BrevoSyncService
from src.common.curation_sdk.scheduler_loop import run_job_loop

logger = logging.getLogger(__name__)


async def process_brevo_sync_queue():
    """
    Scheduler job: Process contacts queued for Brevo sync.

    Finds contacts where brevo_sync_status = 'Queued' and processes them
    using the SDK job loop pattern.
    """
    logger.info("Starting Brevo sync scheduler cycle")

    try:
        service = BrevoSyncService()

        await run_job_loop(
            model=Contact,
            status_enum=BrevoProcessingStatus,
            queued_status=BrevoProcessingStatus.Queued,
            processing_status=BrevoProcessingStatus.Processing,
            completed_status=BrevoProcessingStatus.Complete,
            failed_status=BrevoProcessingStatus.Error,
            processing_function=service.process_single_contact,
            batch_size=settings.BREVO_SYNC_SCHEDULER_BATCH_SIZE,
            order_by_column=asc(Contact.updated_at),
            status_field_name="brevo_processing_status",
            error_field_name="brevo_processing_error",
        )

    except Exception as e:
        logger.exception(f"Critical error in Brevo sync scheduler: {e}")
        # Don't re-raise - let scheduler continue on next interval

    logger.info("Finished Brevo sync scheduler cycle")


def setup_brevo_sync_scheduler():
    """
    Register Brevo sync scheduler with shared scheduler instance.

    Called from src/scheduler_manager.py during app startup.
    """
    job_id = "brevo_contact_sync_processor"

    if not settings.BREVO_API_KEY:
        logger.warning("BREVO_API_KEY not configured - Brevo sync scheduler will be disabled")
        return

    scheduler.add_job(
        process_brevo_sync_queue,
        trigger="interval",
        minutes=settings.BREVO_SYNC_SCHEDULER_INTERVAL_MINUTES,
        id=job_id,
        name="Brevo Contact Sync Processor",
        replace_existing=True,
        max_instances=settings.BREVO_SYNC_SCHEDULER_MAX_INSTANCES,
        misfire_grace_time=1800,  # 30 minutes grace period
    )

    logger.info(
        f"Added Brevo sync scheduler (interval: {settings.BREVO_SYNC_SCHEDULER_INTERVAL_MINUTES} min, "
        f"batch size: {settings.BREVO_SYNC_SCHEDULER_BATCH_SIZE})"
    )
```

**Pattern Reference:**
- ✅ Uses SDK `run_job_loop()` for consistent error handling
- ✅ Queries by `brevo_processing_status` (not `brevo_sync_status`)
- ✅ Comprehensive error handling (won't crash scheduler)
- ✅ Configurable interval and batch size
- ✅ Prevents overlapping runs with `max_instances=1`

---

### 4.4 Register Scheduler at Startup

**File:** `src/scheduler_manager.py` or equivalent startup file

**Add import:**
```python
from src.services.brevo_sync_scheduler import setup_brevo_sync_scheduler
```

**Add to scheduler setup function:**
```python
def setup_schedulers():
    """Initialize all schedulers"""
    # ... existing schedulers ...

    # Brevo sync scheduler
    setup_brevo_sync_scheduler()

    logger.info("All schedulers initialized")
```

---

## Phase 5: Testing & Verification

### 5.1 Unit Tests

**File:** `tests/services/test_brevo_sync_service.py` (NEW FILE)

```python
"""
Unit tests for Brevo sync service
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from src.services.brevo_sync_service import BrevoSyncService
from src.models.WF7_V2_L1_1of1_ContactModel import Contact
from src.models.enums import BrevoSyncStatus, BrevoProcessingStatus


@pytest.mark.asyncio
async def test_process_single_contact_success():
    """Test successful contact sync to Brevo"""
    service = BrevoSyncService()

    # Mock contact
    contact = Contact(
        email="test@example.com",
        name="Test User",
        phone_number="555-1234",
    )

    # Mock session
    session = AsyncMock()

    # Mock API call
    with patch.object(service, '_sync_to_brevo_api', return_value="test@example.com"):
        await service.process_single_contact(contact, session)

    # Verify status updates
    assert contact.brevo_sync_status == BrevoSyncStatus.Complete.value
    assert contact.brevo_processing_status == BrevoProcessingStatus.Complete.value
    assert contact.brevo_processing_error is None
    assert contact.brevo_contact_id == "test@example.com"


@pytest.mark.asyncio
async def test_process_single_contact_no_email():
    """Test contact sync fails gracefully when email missing"""
    service = BrevoSyncService()

    contact = Contact(email=None)
    session = AsyncMock()

    await service.process_single_contact(contact, session)

    assert contact.brevo_sync_status == BrevoSyncStatus.Error.value
    assert contact.brevo_processing_status == BrevoProcessingStatus.Error.value
    assert "no email" in contact.brevo_processing_error.lower()


@pytest.mark.asyncio
async def test_process_single_contact_api_error():
    """Test contact sync handles API errors"""
    service = BrevoSyncService()

    contact = Contact(email="test@example.com")
    session = AsyncMock()

    # Mock API failure
    with patch.object(service, '_sync_to_brevo_api', side_effect=Exception("API Error")):
        await service.process_single_contact(contact, session)

    assert contact.brevo_sync_status == BrevoSyncStatus.Error.value
    assert contact.brevo_processing_status == BrevoProcessingStatus.Error.value
    assert "API Error" in contact.brevo_processing_error
```

**Run tests:**
```bash
pytest tests/services/test_brevo_sync_service.py -v
```

---

### 5.2 Integration Tests

**File:** `tests/integration/test_brevo_endpoints.py` (NEW FILE)

```python
"""
Integration tests for Brevo sync endpoints
"""

import pytest
from httpx import AsyncClient
from src.main import app


@pytest.mark.asyncio
async def test_queue_contacts_for_brevo_sync_batch(test_db, auth_headers):
    """Test batch queueing contacts for Brevo sync"""
    # Create test contacts
    # ... setup code ...

    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post(
            "/api/v3/contacts/brevo/sync/batch",
            json={"contact_ids": [str(contact1.id), str(contact2.id)]},
            headers=auth_headers,
        )

    assert response.status_code == 200
    data = response.json()
    assert data["queued_count"] == 2

    # Verify database state
    # ... verification code ...


@pytest.mark.asyncio
async def test_brevo_sync_status_summary(test_db, auth_headers):
    """Test Brevo sync status summary endpoint"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get(
            "/api/v3/contacts/brevo/status/summary",
            headers=auth_headers,
        )

    assert response.status_code == 200
    data = response.json()
    assert "new" in data
    assert "queued" in data
    assert "complete" in data
```

---

### 5.3 Manual Testing Checklist

**Prerequisites:**
- [ ] Brevo API key configured in `.env`
- [ ] Brevo list ID configured in `.env`
- [ ] Application deployed or running locally
- [ ] Test contacts exist in database

**Test Flow:**

1. **Queue contacts for sync:**
   ```bash
   curl -X POST http://localhost:8000/api/v3/contacts/brevo/sync/batch \
     -H "Authorization: Bearer $JWT_TOKEN" \
     -H "Content-Type: application/json" \
     -d '{"contact_ids": ["<uuid>", "<uuid>"]}'
   ```

   Expected: `{"queued_count": 2, "message": "..."}`

2. **Verify contacts queued:**
   ```sql
   SELECT id, email, brevo_sync_status, brevo_processing_status
   FROM contacts
   WHERE brevo_sync_status = 'Queued';
   ```

   Expected: See queued contacts

3. **Wait for scheduler (5 minutes or trigger manually)**

4. **Verify contacts synced:**
   ```sql
   SELECT id, email, brevo_sync_status, brevo_contact_id, brevo_processing_error
   FROM contacts
   WHERE brevo_sync_status = 'Complete';
   ```

   Expected: Contacts moved to 'Complete' with Brevo contact ID

5. **Check Brevo dashboard:**
   - Log in to Brevo
   - Navigate to Contacts
   - Verify test contacts appear in target list

6. **Test error handling (invalid email):**
   - Queue contact with invalid email
   - Verify status moves to 'Error'
   - Verify error message in `brevo_processing_error`

7. **Test status summary:**
   ```bash
   curl http://localhost:8000/api/v3/contacts/brevo/status/summary \
     -H "Authorization: Bearer $JWT_TOKEN"
   ```

   Expected: Count breakdown by status

---

## Phase 6: Documentation

### 6.1 Update API Documentation

**File:** `Documentation/API/CONTACTS_API.md` or equivalent

Add section:
```markdown
## Brevo Sync Endpoints

### Queue Contacts for Brevo Sync (Batch)
`POST /api/v3/contacts/brevo/sync/batch`

Queue specific contacts for Brevo CRM synchronization.

**Request Body:**
```json
{
  "contact_ids": ["uuid1", "uuid2", "uuid3"]
}
```

**Response:**
```json
{
  "queued_count": 2,
  "already_queued_count": 1,
  "skipped_count": 0,
  "message": "Queued 2 contacts for Brevo sync"
}
```

### Queue Contacts for Brevo Sync (Filtered)
`POST /api/v3/contacts/brevo/sync/filtered`

Queue contacts matching filter criteria for Brevo sync.

**Request Body:**
```json
{
  "email_type": "CORPORATE",
  "has_gmail": false,
  "contact_curation_status": "Complete"
}
```

### Get Brevo Sync Status Summary
`GET /api/v3/contacts/brevo/status/summary`

Returns count of contacts in each Brevo sync state.
```

---

### 6.2 Update SYSTEM_MAP.md

**File:** `Documentation/Context_Reconstruction/SYSTEM_MAP.md`

Add to External Dependencies section:
```markdown
### Brevo CRM
- **Used By:** Contact sync (background scheduler)
- **Purpose:** Sync contacts to Brevo CRM for email marketing
- **Cost:** Free up to 300 emails/day, paid plans available
- **Rate Limit:** 10 requests/second (check current limits)
- **Failure Mode:** contact.brevo_sync_status='Error'
- **Config:** `settings.BREVO_API_KEY`, `settings.BREVO_LIST_ID`
```

---

### 6.3 Create WO-015 Summary Document

This document serves as the summary! Archive as:
`Documentation/Work_Orders/WO-015_BREVO_SYNC_IMPLEMENTATION.md`

---

## Phase 7: Future Extensibility (Mautic)

### 7.1 Pattern Established

The Brevo implementation establishes the pattern for future CRM integrations.

**To add Mautic sync:**
1. Copy Brevo ENUM pattern → `MauticSyncStatus`, `MauticProcessingStatus`
2. Add 4 fields to Contact model: `mautic_sync_status`, `mautic_processing_status`, `mautic_processing_error`, `mautic_contact_id`
3. Create `src/routers/v3/mautic_contacts_router.py`
4. Create `src/services/mautic_sync_service.py`
5. Create `src/services/mautic_sync_scheduler.py`
6. Add Mautic config to `settings.py`

**Estimated effort:** 4-6 hours (following established pattern)

---

### 7.2 N8N Integration Opportunity

User has n8n instance available. Consider:

**Option A: n8n as Primary Sync Engine**
- ScraperSky queues contacts (status = 'Queued')
- n8n polls ScraperSky API for queued contacts
- n8n handles sync to multiple CRMs (Brevo, HubSpot, Mautic)
- n8n updates ScraperSky contact status via API

**Option B: ScraperSky Webhooks to n8n**
- ScraperSky triggers n8n webhook when contact queued
- n8n orchestrates multi-platform sync
- n8n calls back to ScraperSky to update status

**Recommendation:** Implement Phase 1-6 first (native Brevo sync), then evaluate n8n integration based on complexity and performance needs.

---

## Implementation Timeline

### Sprint 1 (Week 1)
- [ ] Phase 1: Database migration (Day 1-2)
- [ ] Phase 2: Schema updates (Day 2)
- [ ] Phase 3: API endpoints (Day 3-4)
- [ ] Testing & debugging (Day 5)

### Sprint 2 (Week 2)
- [ ] Phase 4: Service layer (Day 1-3)
- [ ] Phase 5: Testing (Day 4)
- [ ] Phase 6: Documentation (Day 5)

### Total Estimated Effort: 8-10 days

---

## Risks & Mitigations

### Risk 1: Brevo API Rate Limits
**Mitigation:**
- Start with batch_size=10, interval=5min (120 contacts/hour max)
- Monitor Brevo API responses for 429 (rate limit) errors
- Implement exponential backoff if rate limited

### Risk 2: Duplicate Contacts in Brevo
**Mitigation:**
- Use `updateEnabled=true` in Brevo API (idempotent)
- Store `brevo_contact_id` for tracking

### Risk 3: Scheduler Overlap
**Mitigation:**
- Set `max_instances=1` in scheduler config
- Use SDK job loop (handles status transitions atomically)

### Risk 4: Missing BREVO_API_KEY
**Mitigation:**
- Scheduler checks for API key, disables if missing
- Endpoints return clear error messages
- Documentation emphasizes configuration requirements

---

## Success Criteria

- [ ] Database migration successful (all 3 Brevo fields added)
- [ ] All Brevo endpoints functional and tested
- [ ] Scheduler processes queued contacts every 5 minutes
- [ ] Test contact successfully syncs to Brevo CRM
- [ ] Error handling works (invalid emails marked as Skipped)
- [ ] Status summary endpoint returns accurate counts
- [ ] No performance regression on existing endpoints
- [ ] All tests passing (unit + integration)
- [ ] Documentation complete and accurate

---

## Rollback Plan

If issues arise in production:

1. **Disable scheduler:**
   ```python
   # In src/services/brevo_sync_scheduler.py
   # Comment out setup_brevo_sync_scheduler() call
   ```

2. **Remove router registration:**
   ```python
   # In src/main.py
   # Comment out: app.include_router(brevo_contacts_router.router)
   ```

3. **Database rollback:**
   ```bash
   alembic downgrade -1
   ```

4. **Revert code changes:**
   ```bash
   git revert <commit-hash>
   ```

---

## References

### Code Patterns
- HubSpot sync: `src/models/WF7_V2_L1_1of1_ContactModel.py` lines 38-49
- SDK job loop: `src/common/curation_sdk/scheduler_loop.py`
- Dual-status pattern: `Documentation/Context_Reconstruction/GLOSSARY.md`
- Service communication: `Documentation/Context_Reconstruction/PATTERNS.md`

### External Documentation
- Brevo API Docs: https://developers.brevo.com/reference/createcontact
- Brevo Rate Limits: https://developers.brevo.com/docs/api-limits
- FastAPI Background Tasks: https://fastapi.tiangolo.com/tutorial/background-tasks/

### Related Work Orders
- WO-004: Multi-scheduler split and background task fixes
- WO-005: Knowledge repository patterns

---

## Questions for Review

1. **Brevo List ID:** Should contacts be added to a specific list, or sync without list assignment?
2. **Brevo Attributes:** Are there additional custom fields needed in Brevo beyond name/phone/email?
3. **Retry Logic:** Should failed syncs auto-retry, or require manual re-queue?
4. **Webhooks:** Should we add Brevo webhook endpoint for bounce/unsubscribe tracking?
5. **N8N Integration:** Should we plan for n8n integration now, or implement later?

---

**END OF WORK ORDER**

**Status:** Ready for Local Claude Review
**Next Step:** Local Claude reviews → Database migration → Implementation
**Estimated Completion:** 2 weeks (10 business days)
