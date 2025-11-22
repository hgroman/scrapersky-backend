# ScraperSky Integration Playbook

**Last Updated:** 2025-11-19
**Status:** Production-Proven Pattern
**Success Rate:** 4/4 Implementations (Brevo, HubSpot, DeBounce, n8n)

---

## Overview

This playbook documents the proven step-by-step process for integrating new services (CRMs, validation, enrichment) into ScraperSky. Following this pattern ensures:

✅ Consistent architecture
✅ Dual-status adapter pattern
✅ Automatic retry logic
✅ Background scheduler automation
✅ Error handling and logging
✅ Easy testing and debugging

**Time to Implement:** 2-3 hours per integration (following this playbook)

---

## The Proven Pattern (High-Level)

```
1. Database Schema (15 min)
   ↓
2. Enums (5 min)
   ↓
3. Service Layer (45 min)
   ↓
4. Scheduler (20 min)
   ↓
5. Environment Config (10 min)
   ↓
6. Main Registration (5 min)
   ↓
7. Testing (30 min)
   ↓
8. Documentation (20 min)
```

**Total:** ~2.5 hours for complete integration

---

## Phase 1: Database Schema (15 min)

### Step 1.1: Identify Required Fields

**For CRM Integrations:**
```python
# User-facing status (user decisions)
{service}_sync_status: Mapped[Optional[str]]

# System-facing status (scheduler tracking)
{service}_processing_status: Mapped[Optional[str]]

# Error tracking
{service}_processing_error: Mapped[Optional[str]]

# External ID (from CRM/service)
{service}_contact_id: Mapped[Optional[str]]
```

**For Validation/Enrichment:**
```python
# Status fields
{service}_validation_status: Mapped[Optional[str]]
{service}_processing_status: Mapped[Optional[str]]
{service}_processing_error: Mapped[Optional[str]]

# Result fields
{service}_result: Mapped[Optional[str]]
{service}_score: Mapped[Optional[int]]
{service}_reason: Mapped[Optional[str]]
{service}_validated_at: Mapped[Optional[datetime]]
```

**Shared Retry Fields** (already exist in Contact model):
```python
retry_count: Mapped[int]
next_retry_at: Mapped[Optional[datetime]]
last_retry_at: Mapped[Optional[datetime]]
last_failed_crm: Mapped[Optional[str]]
```

### Step 1.2: Create Migration File

**Location:** `supabase/migrations/YYYYMMDD_add_{service}_fields.sql`

**Template:**
```sql
-- Add {SERVICE_NAME} integration fields to contacts table

ALTER TABLE contacts
ADD COLUMN IF NOT EXISTS {service}_sync_status VARCHAR(20),
ADD COLUMN IF NOT EXISTS {service}_processing_status VARCHAR(20),
ADD COLUMN IF NOT EXISTS {service}_processing_error TEXT,
ADD COLUMN IF NOT EXISTS {service}_contact_id VARCHAR(255);

-- Add check constraint for status values
ALTER TABLE contacts
ADD CONSTRAINT chk_{service}_sync_status
CHECK ({service}_sync_status IN ('Selected', 'Queued', 'Processing', 'Complete', 'Error', 'Skipped') OR {service}_sync_status IS NULL);

ALTER TABLE contacts
ADD CONSTRAINT chk_{service}_processing_status
CHECK ({service}_processing_status IN ('Queued', 'Processing', 'Complete', 'Error') OR {service}_processing_status IS NULL);

-- Add indexes for scheduler queries
CREATE INDEX IF NOT EXISTS idx_contacts_{service}_processing_status
ON contacts({service}_processing_status)
WHERE {service}_processing_status IS NOT NULL;

-- Add index for retry queries
CREATE INDEX IF NOT EXISTS idx_contacts_{service}_retry
ON contacts(next_retry_at, {service}_processing_status)
WHERE next_retry_at IS NOT NULL;
```

### Step 1.3: Update Contact Model

**File:** `src/models/wf7_contact.py`

**Add fields:**
```python
# {SERVICE_NAME} Integration (WO-XXX)
{service}_sync_status: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
{service}_processing_status: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
{service}_processing_error: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
{service}_contact_id: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
```

### Step 1.4: Apply Migration

**Via Supabase MCP (Local Claude):**
```sql
-- Execute migration SQL
-- Verify fields exist
SELECT column_name, data_type
FROM information_schema.columns
WHERE table_name = 'contacts'
AND column_name LIKE '{service}_%';
```

---

## Phase 2: Enums (5 min)

### Step 2.1: Define Status Enums

**File:** `src/models/enums.py`

**Check if already exists:**
```python
class CRMSyncStatus(str, Enum):
    Selected = "Selected"      # User selected for sync
    Queued = "Queued"          # Queued for processing
    Processing = "Processing"  # Currently processing
    Complete = "Complete"      # Successfully synced
    Error = "Error"            # Failed after retries
    Skipped = "Skipped"        # User skipped

class CRMProcessingStatus(str, Enum):
    Queued = "Queued"          # Waiting for scheduler
    Processing = "Processing"  # Being processed now
    Complete = "Complete"      # Successfully completed
    Error = "Error"            # Failed (will retry)
```

**If service-specific status needed:**
```python
class {Service}ValidationStatus(str, Enum):
    New = "New"                # Never validated
    Queued = "Queued"          # Queued for validation
    Complete = "Complete"      # Validation complete
    Error = "Error"            # Validation failed
```

### Step 2.2: Import in Models

**File:** `src/models/wf7_contact.py`

```python
from src.models.enums import CRMSyncStatus, CRMProcessingStatus
```

---

## Phase 3: Service Layer (45 min)

### Step 3.1: Create Service File

**Location:** `src/services/{category}/{service}_service.py`

**Examples:**
- `src/services/crm/brevo_sync_service.py`
- `src/services/crm/hubspot_sync_service.py`
- `src/services/email_validation/debounce_service.py`
- `src/services/crm/n8n_sync_service.py`

### Step 3.2: Implement Service Class

**Template:**
```python
"""
{Service Name} Integration Service (WO-XXX)

Handles {description of what service does}.

Architecture: SDK-compatible service for use with run_job_loop pattern.
Pattern Reference: src/services/crm/brevo_sync_service.py

API Documentation: {link to external API docs}
"""

import logging
from datetime import datetime, timedelta
from uuid import UUID
import httpx
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from src.config.settings import settings
from src.models.wf7_contact import Contact
from src.models.enums import CRMSyncStatus, CRMProcessingStatus

logger = logging.getLogger(__name__)


class {Service}Service:
    """Service for {description}"""

    def __init__(self):
        self.api_key = settings.{SERVICE}_API_KEY
        self.base_url = settings.{SERVICE}_API_BASE_URL

        if not self.api_key:
            logger.warning("⚠️ {SERVICE}_API_KEY not configured - service will fail")

    async def process_single_contact(
        self, contact_id: UUID, session: AsyncSession
    ) -> None:
        """
        Process a single contact for {service} sync.

        SDK-compatible method signature: (contact_id: UUID, session: AsyncSession)
        Called by scheduler via run_job_loop pattern.

        Args:
            contact_id: Contact UUID to process
            session: Async database session (managed by SDK)

        Raises:
            Exception: Re-raises any exceptions for SDK to handle
        """
        logger.info(f"🚀 Starting {service} sync for contact {contact_id}")

        # Fetch contact from database
        stmt = select(Contact).where(Contact.id == contact_id)
        result = await session.execute(stmt)
        contact = result.scalar_one_or_none()

        if not contact:
            logger.error(f"❌ Contact {contact_id} not found - skipping")
            return

        try:
            # Core sync logic
            await self._process_contact(contact, session)

        except Exception as e:
            logger.exception(f"❌ Failed to process contact {contact_id}: {e}")
            # Re-raise for SDK to handle (will mark as failed)
            raise

    async def _process_contact(
        self, contact: Contact, session: AsyncSession
    ) -> None:
        """
        Core business logic to process one contact.

        Handles:
        - Validation
        - Status transitions (Processing → Complete/Error)
        - API call
        - Retry logic with exponential backoff
        - Error tracking

        Args:
            contact: Contact model instance
            session: Async database session

        Note: This method does NOT raise exceptions - it handles all errors
        internally and updates contact status accordingly.
        """
        logger.info(f"📧 Processing {service} for {contact.email}")

        try:
            # Validate contact
            if not contact.email:
                raise ValueError("Contact has no email address")

            # Status: Processing
            contact.{service}_sync_status = CRMSyncStatus.Processing.value
            contact.{service}_processing_status = CRMProcessingStatus.Processing.value
            await session.commit()  # Immediate visibility

            # Call external API
            result = await self._call_api(contact)

            # Status: Complete
            contact.{service}_sync_status = CRMSyncStatus.Complete.value
            contact.{service}_processing_status = CRMProcessingStatus.Complete.value
            contact.{service}_processing_error = None
            contact.{service}_contact_id = result.get("id")  # External ID
            contact.retry_count = 0  # Reset retry count
            contact.next_retry_at = None
            contact.last_failed_crm = None

            await session.commit()
            logger.info(f"✅ Successfully processed {contact.email}")

        except Exception as e:
            error_msg = str(e)
            logger.exception(f"❌ Processing failed for {contact.email}: {error_msg}")

            # Retry logic
            should_retry = contact.retry_count < settings.{SERVICE}_MAX_RETRIES

            if should_retry:
                # Calculate exponential backoff delay
                delay_minutes = self._calculate_retry_delay(contact.retry_count)
                next_retry = datetime.utcnow() + timedelta(minutes=delay_minutes)

                # Status: Queued for retry (with Error processing status)
                contact.{service}_sync_status = CRMSyncStatus.Queued.value
                contact.{service}_processing_status = CRMProcessingStatus.Error.value
                contact.{service}_processing_error = error_msg[:500]  # Truncate
                contact.retry_count += 1
                contact.last_retry_at = datetime.utcnow()
                contact.next_retry_at = next_retry
                contact.last_failed_crm = "{service}"

                logger.info(
                    f"🔄 Scheduled retry {contact.retry_count}/{settings.{SERVICE}_MAX_RETRIES} "
                    f"for {contact.email} at {next_retry} (in {delay_minutes} minutes)"
                )
            else:
                # Status: Error (max retries exceeded)
                contact.{service}_sync_status = CRMSyncStatus.Error.value
                contact.{service}_processing_status = CRMProcessingStatus.Error.value
                contact.{service}_processing_error = error_msg[:500]
                contact.last_failed_crm = "{service}"

                logger.error(
                    f"❌ Max retries ({settings.{SERVICE}_MAX_RETRIES}) exceeded for {contact.email}"
                )

            await session.commit()

    async def _call_api(self, contact: Contact) -> dict:
        """
        Call external API for this service.

        Args:
            contact: Contact model instance

        Returns:
            API response data

        Raises:
            httpx.HTTPError: If API request fails
            ValueError: If API returns non-success status
        """
        # Build API payload
        payload = {
            "email": contact.email,
            "name": contact.name,
            # Add service-specific fields
        }

        # Build headers
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}",  # Or service-specific auth
        }

        logger.info(f"📤 Calling {service} API for {contact.email}")

        async with httpx.AsyncClient(timeout=30.0) as client:
            try:
                response = await client.post(
                    self.base_url,
                    json=payload,
                    headers=headers,
                    timeout=30.0,
                )

                # Check response status
                if response.status_code not in [200, 201]:
                    raise ValueError(
                        f"API returned non-success status: {response.status_code} - {response.text}"
                    )

                data = response.json()
                logger.info(f"✅ API call successful for {contact.email}")
                return data

            except httpx.TimeoutException:
                raise ValueError("API request timed out after 30 seconds")
            except httpx.HTTPError as e:
                raise ValueError(f"API HTTP error: {str(e)}")

    def _calculate_retry_delay(self, retry_count: int) -> int:
        """
        Calculate exponential backoff delay in minutes.

        Args:
            retry_count: Current retry attempt (0-indexed)

        Returns:
            Delay in minutes

        Examples:
            Retry 0 → 5 minutes
            Retry 1 → 10 minutes
            Retry 2 → 20 minutes
            Retry 3 → 40 minutes (capped at 120)
        """
        base_delay = 5  # Start with 5 minutes
        max_delay = 120  # Cap at 2 hours
        delay = base_delay * (2**retry_count)
        return min(delay, max_delay)
```

### Step 3.3: Add Service Tests (Optional but Recommended)

**Location:** `tests/services/{service}_service_test.py`

**Quick validation test:**
```python
def test_calculate_retry_delay():
    service = {Service}Service()
    assert service._calculate_retry_delay(0) == 5
    assert service._calculate_retry_delay(1) == 10
    assert service._calculate_retry_delay(2) == 20
    assert service._calculate_retry_delay(5) == 120  # Capped
```

---

## Phase 4: Scheduler (20 min)

### Step 4.1: Create Scheduler File

**Location:** `src/services/{category}/{service}_scheduler.py`

**Template:**
```python
"""
{Service Name} Scheduler (WO-XXX)

Background scheduler that automatically processes contacts queued for {service}.

Architecture: SDK-compatible scheduler using run_job_loop pattern.
Pattern Reference: src/services/crm/brevo_sync_scheduler.py

This scheduler:
1. Runs every N minutes (configured via {SERVICE}_SCHEDULER_INTERVAL_MINUTES)
2. Fetches contacts with {service}_processing_status = 'Queued'
3. Processes each contact via {Service}Service.process_single_contact()
4. Handles retries automatically based on next_retry_at timestamp
"""

import logging
from sqlalchemy import asc

from src.common.curation_sdk.scheduler_loop import run_job_loop
from src.config.settings import settings
from src.models.wf7_contact import Contact
from src.models.enums import CRMProcessingStatus
from .{service}_service import {Service}Service

logger = logging.getLogger(__name__)


async def process_{service}_queue():
    """
    Processes contacts marked as 'Queued' for {service} using the SDK job loop.

    This function:
    1. Queries contacts with {service}_processing_status = 'Queued'
    2. Processes each contact via {Service}Service.process_single_contact()
    3. Automatically handles status transitions via run_job_loop

    Note: Retry logic (next_retry_at filtering) is handled in the service layer,
    not in the scheduler, as the SDK run_job_loop() does not support additional_filters.

    Called by: APScheduler at configured interval
    Frequency: {SERVICE}_SCHEDULER_INTERVAL_MINUTES (default: 5 minutes)
    Batch Size: {SERVICE}_SCHEDULER_BATCH_SIZE (default: 10)
    """
    service = {Service}Service()
    logger.info("🚀 Starting {service} scheduler cycle")

    await run_job_loop(
        model=Contact,
        status_enum=CRMProcessingStatus,
        queued_status=CRMProcessingStatus.Queued,
        processing_status=CRMProcessingStatus.Processing,
        completed_status=CRMProcessingStatus.Complete,
        failed_status=CRMProcessingStatus.Error,
        processing_function=service.process_single_contact,
        batch_size=settings.{SERVICE}_SCHEDULER_BATCH_SIZE,
        order_by_column=asc(Contact.updated_at),
        status_field_name="{service}_processing_status",
        error_field_name="{service}_processing_error",
    )

    logger.info("✅ Finished {service} scheduler cycle")


from src.scheduler_instance import scheduler


def setup_{service}_scheduler():
    """
    Adds the {service} job to the main scheduler.

    Configuration (from settings.py):
    - {SERVICE}_API_KEY: Required - scheduler will not start if missing
    - {SERVICE}_SCHEDULER_INTERVAL_MINUTES: How often to run (default: 5)
    - {SERVICE}_SCHEDULER_BATCH_SIZE: Contacts per batch (default: 10)
    - {SERVICE}_SCHEDULER_MAX_INSTANCES: Concurrent instances (default: 1)

    Safety:
    - Scheduler disabled if {SERVICE}_API_KEY not configured
    - max_instances=1 prevents race conditions
    - misfire_grace_time=1800 (30min) handles temporary downtime
    """
    # Safety check: Don't start scheduler if API key not configured
    if not settings.{SERVICE}_API_KEY:
        logger.warning("⚠️ {SERVICE}_API_KEY not configured - {service} scheduler DISABLED")
        logger.warning("   Set {SERVICE}_API_KEY in .env to enable automatic {service} sync")
        return

    logger.info("📋 Configuring {service} scheduler...")
    logger.info(
        f"   Interval: {settings.{SERVICE}_SCHEDULER_INTERVAL_MINUTES} minutes"
    )
    logger.info(f"   Batch size: {settings.{SERVICE}_SCHEDULER_BATCH_SIZE} contacts")
    logger.info(f"   Max instances: {settings.{SERVICE}_SCHEDULER_MAX_INSTANCES}")

    scheduler.add_job(
        process_{service}_queue,
        trigger="interval",
        minutes=settings.{SERVICE}_SCHEDULER_INTERVAL_MINUTES,
        id="{service}_processor",
        name="{Service Name} Processor",
        replace_existing=True,
        max_instances=settings.{SERVICE}_SCHEDULER_MAX_INSTANCES,
        misfire_grace_time=1800,  # 30 minutes grace time for temporary downtime
    )

    logger.info("✅ {service} scheduler job registered successfully")
```

---

## Phase 5: Environment Configuration (10 min)

### Step 5.1: Add to settings.py

**File:** `src/config/settings.py`

**Template:**
```python
# ============================================================================
# {Service Name} Integration (WO-XXX)
# ============================================================================

# API Authentication
{SERVICE}_API_KEY: Optional[str] = None
{SERVICE}_API_BASE_URL: str = "https://api.{service}.com/v1"

# Scheduler Settings (WO-XXX)
{SERVICE}_SCHEDULER_INTERVAL_MINUTES: int = 5
{SERVICE}_SCHEDULER_BATCH_SIZE: int = 10
{SERVICE}_SCHEDULER_MAX_INSTANCES: int = 1

# Retry Logic (WO-XXX)
{SERVICE}_MAX_RETRIES: int = 3
{SERVICE}_RETRY_DELAY_MINUTES: int = 5
{SERVICE}_RETRY_EXPONENTIAL: bool = True
```

### Step 5.2: Add to .env.example

**File:** `.env.example`

**Template:**
```bash
# --- {Service Name} Integration (WO-XXX) ---
{SERVICE}_API_KEY=your_{service}_api_key_here
{SERVICE}_API_BASE_URL=https://api.{service}.com/v1  # Default API endpoint

# {Service Name} Scheduler Settings (WO-XXX)
{SERVICE}_SCHEDULER_INTERVAL_MINUTES=5
{SERVICE}_SCHEDULER_BATCH_SIZE=10
{SERVICE}_SCHEDULER_MAX_INSTANCES=1

# {Service Name} Retry Logic Settings (WO-XXX)
{SERVICE}_MAX_RETRIES=3
{SERVICE}_RETRY_DELAY_MINUTES=5
{SERVICE}_RETRY_EXPONENTIAL=true  # Use exponential backoff (5min, 10min, 20min)
```

---

## Phase 6: Main Registration (5 min)

### Step 6.1: Import Scheduler

**File:** `src/main.py`

**Add import:**
```python
from src.services.{category}.{service}_scheduler import setup_{service}_scheduler
```

### Step 6.2: Register in Lifespan

**File:** `src/main.py`

**Add in lifespan startup section:**
```python
# WO-XXX: {Service Name} scheduler
try:
    setup_{service}_scheduler()
except Exception as e:
    logger.error(f"Failed to setup {service} scheduler: {e}", exc_info=True)
```

---

## Phase 7: Testing (30 min)

### Step 7.1: Create Test Plan Document

**Location:** `Documentation/Work_Orders/WO-XXX_TEST_PLAN.md`

**Template Sections:**
1. **Prerequisites** - Environment setup, API keys
2. **Test 1: Service Direct Test** - Manual contact creation
3. **Test 2: Scheduler Configuration** - Verify registration
4. **Test 3: Batch Processing** - Multiple contacts
5. **Test 4: Error Handling** - Invalid API key
6. **Test 5: Retry Logic** - Verify exponential backoff
7. **Success Criteria** - Checklist

### Step 7.2: Quick Manual Test

**Create test contact:**
```sql
INSERT INTO contacts (
    email,
    name,
    {service}_sync_status,
    {service}_processing_status
)
VALUES (
    'test.{service}@example.com',
    'Test User',
    'Selected',
    'Queued'
)
RETURNING id;
```

**Start Docker:**
```bash
docker compose up --build
```

**Watch logs:**
```bash
docker compose logs -f app | grep "{service}"
```

**Expected logs:**
```
✅ {service} scheduler job registered successfully
🚀 Starting {service} scheduler cycle
📧 Processing {service} for test.{service}@example.com
📤 Calling {service} API for test.{service}@example.com
✅ API call successful for test.{service}@example.com
✅ Successfully processed test.{service}@example.com
✅ Finished {service} scheduler cycle
```

**Verify database:**
```sql
SELECT
    email,
    {service}_sync_status,
    {service}_processing_status,
    {service}_processing_error,
    {service}_contact_id
FROM contacts
WHERE email = 'test.{service}@example.com';
```

**Expected:**
- `{service}_sync_status`: "Complete"
- `{service}_processing_status`: "Complete"
- `{service}_processing_error`: NULL
- `{service}_contact_id`: External ID from API

---

## Phase 8: Documentation (20 min)

### Step 8.1: Create Completion Document

**Location:** `Documentation/Work_Orders/WO-XXX_COMPLETE.md`

**Sections:**
1. **Summary** - What was implemented
2. **Deliverables** - Files created/modified
3. **Technical Implementation** - How it works
4. **Environment Variables** - Configuration options
5. **Testing** - How to test it
6. **Success Criteria** - Completion checklist
7. **Next Steps** - What comes after

### Step 8.2: Update Work Order Tracking

**File:** `Documentation/SESSION_SUMMARY_YYYY-MM-DD.md`

**Add entry:**
```markdown
### ✅ WO-XXX: {Service Name} Integration (COMPLETE)

**Status:** Production Ready
**Completion Date:** YYYY-MM-DD

**What It Does:**
- {Brief description}
- Background scheduler processes queued contacts every 5 minutes
- Retry logic with exponential backoff (3 attempts)

**Files:**
- `src/services/{category}/{service}_service.py`
- `src/services/{category}/{service}_scheduler.py`

**Testing:** All tests passed ✅
```

---

## Common Patterns & Best Practices

### Dual-Status Adapter Pattern

**Always Use Two Status Fields:**

1. **User-Facing Status** (`{service}_sync_status`)
   - What the user sees and controls
   - Values: Selected, Queued, Processing, Complete, Error, Skipped

2. **System-Facing Status** (`{service}_processing_status`)
   - What the scheduler uses
   - Values: Queued, Processing, Complete, Error

**Why This Works:**
- User can mark contacts as "Selected" without immediate processing
- System adapter converts "Selected" → "Queued" automatically
- Scheduler only processes "Queued" status
- Clear separation of user intent vs. system state

### Retry Logic Pattern

**Always Use Exponential Backoff:**
```
Retry 0 → 5 minutes
Retry 1 → 10 minutes
Retry 2 → 20 minutes
Retry 3 → Max retries exceeded (Error final state)
```

**Database Tracking:**
- `retry_count`: Current attempt
- `next_retry_at`: When to retry next
- `last_retry_at`: Last attempt timestamp
- `last_failed_crm`: Which service failed

### Error Handling Pattern

**Always Log with Emojis (for easy scanning):**
```python
logger.info("🚀 Starting...")
logger.info("📧 Processing...")
logger.info("📤 Calling API...")
logger.info("✅ Success!")
logger.error("❌ Failed!")
logger.info("🔄 Retrying...")
```

**Always Truncate Error Messages:**
```python
contact.{service}_processing_error = error_msg[:500]  # Prevent DB overflow
```

**Always Re-raise in SDK Methods:**
```python
async def process_single_contact(...):
    try:
        await self._process_contact(...)
    except Exception as e:
        logger.exception(f"❌ Failed: {e}")
        raise  # Let SDK handle status updates
```

### SDK Compatibility Pattern

**Always Use This Signature:**
```python
async def process_single_contact(
    self, contact_id: UUID, session: AsyncSession
) -> None:
```

**Always Fetch Contact First:**
```python
stmt = select(Contact).where(Contact.id == contact_id)
result = await session.execute(stmt)
contact = result.scalar_one_or_none()

if not contact:
    logger.error(f"❌ Contact {contact_id} not found - skipping")
    return
```

### Scheduler Configuration Pattern

**Always Use These Defaults:**
```python
{SERVICE}_SCHEDULER_INTERVAL_MINUTES: int = 5    # Every 5 minutes
{SERVICE}_SCHEDULER_BATCH_SIZE: int = 10         # 10 contacts per cycle
{SERVICE}_SCHEDULER_MAX_INSTANCES: int = 1       # No concurrent runs
```

**Always Check API Key Before Starting:**
```python
if not settings.{SERVICE}_API_KEY:
    logger.warning("⚠️ {SERVICE}_API_KEY not configured - scheduler DISABLED")
    return
```

---

## Anti-Patterns (Don't Do This!)

### ❌ Don't Use additional_filters in run_job_loop

**Wrong:**
```python
await run_job_loop(
    ...
    additional_filters=[Contact.next_retry_at <= datetime.utcnow()]  # DON'T DO THIS
)
```

**Why:** SDK doesn't support this parameter on some models.

**Right:** Handle retry filtering in service layer:
```python
# In _process_contact:
if contact.next_retry_at and contact.next_retry_at > datetime.utcnow():
    logger.info("⏳ Retry not ready yet - skipping")
    return  # Skip this contact
```

### ❌ Don't Batch Commit Status Updates

**Wrong:**
```python
for contact in contacts:
    contact.status = "Processing"
# Commit all at end
await session.commit()
```

**Why:** If processing fails, status never updates.

**Right:** Commit immediately after status change:
```python
contact.status = "Processing"
await session.commit()  # Immediate visibility
```

### ❌ Don't Hardcode Retry Delays

**Wrong:**
```python
next_retry = datetime.utcnow() + timedelta(minutes=5)  # Hardcoded
```

**Right:** Use exponential backoff calculation:
```python
delay_minutes = self._calculate_retry_delay(contact.retry_count)
next_retry = datetime.utcnow() + timedelta(minutes=delay_minutes)
```

### ❌ Don't Forget Idempotency

**Wrong:**
```python
# Always process, even if already done
await self._call_api(contact)
```

**Right:** Check if already processed:
```python
if contact.{service}_sync_status == "Complete":
    logger.info("✅ Already complete - skipping")
    return
```

---

## Troubleshooting Guide

### Issue: Scheduler Not Starting

**Check:**
1. API key set in `.env`?
2. Scheduler registered in `main.py`?
3. Logs show "scheduler DISABLED" warning?

**Fix:**
```bash
# Add to .env
{SERVICE}_API_KEY=your-key-here

# Restart Docker
docker compose restart app
```

### Issue: Contacts Stuck in "Processing"

**Cause:** Scheduler crashed mid-processing

**Fix:**
```sql
-- Reset stuck contacts
UPDATE contacts
SET {service}_processing_status = 'Queued'
WHERE {service}_processing_status = 'Processing';
```

### Issue: Retries Not Working

**Check:**
1. `retry_count` incrementing?
2. `next_retry_at` set correctly?
3. Retry logic in service layer?

**Debug:**
```sql
SELECT
    email,
    retry_count,
    next_retry_at,
    {service}_processing_error
FROM contacts
WHERE {service}_processing_status = 'Error';
```

### Issue: "Max Retries Exceeded" Immediately

**Cause:** `{SERVICE}_MAX_RETRIES` set too low

**Fix:**
```bash
# In .env
{SERVICE}_MAX_RETRIES=3  # Default should be 3
```

---

## Checklist for New Integration

**Before Starting:**
- [ ] Identify service type (CRM, validation, enrichment)
- [ ] Get API documentation URL
- [ ] Get API key/credentials
- [ ] Determine required data fields

**Phase 1: Database**
- [ ] Create migration file
- [ ] Add fields to Contact model
- [ ] Apply migration
- [ ] Verify fields in database

**Phase 2: Enums**
- [ ] Check if CRMSyncStatus/CRMProcessingStatus exist
- [ ] Add service-specific enums if needed
- [ ] Import in Contact model

**Phase 3: Service**
- [ ] Create service file
- [ ] Implement `process_single_contact()`
- [ ] Implement `_process_contact()`
- [ ] Implement `_call_api()`
- [ ] Implement `_calculate_retry_delay()`

**Phase 4: Scheduler**
- [ ] Create scheduler file
- [ ] Implement `process_{service}_queue()`
- [ ] Implement `setup_{service}_scheduler()`
- [ ] Add API key safety check

**Phase 5: Configuration**
- [ ] Add variables to `settings.py`
- [ ] Add examples to `.env.example`
- [ ] Document all environment variables

**Phase 6: Registration**
- [ ] Import scheduler in `main.py`
- [ ] Register in lifespan startup
- [ ] Add error handling

**Phase 7: Testing**
- [ ] Create test plan document
- [ ] Create test contact
- [ ] Start Docker
- [ ] Watch logs
- [ ] Verify database updates
- [ ] Test error handling
- [ ] Test retry logic

**Phase 8: Documentation**
- [ ] Create WO-XXX_COMPLETE.md
- [ ] Update session summary
- [ ] Document test results
- [ ] Note any issues/limitations

---

## Time Estimates (Per Integration)

| Phase | Task | Time |
|-------|------|------|
| 1 | Database schema + migration | 15 min |
| 2 | Enums (if needed) | 5 min |
| 3 | Service layer | 45 min |
| 4 | Scheduler | 20 min |
| 5 | Environment config | 10 min |
| 6 | Main registration | 5 min |
| 7 | Testing | 30 min |
| 8 | Documentation | 20 min |
| **TOTAL** | | **2.5 hours** |

**With experience:** Can reduce to 1.5-2 hours by using copy/paste from previous implementations.

---

## Success Metrics

**Proven Success Rate:** 4/4 (100%)
- ✅ Brevo CRM (WO-015)
- ✅ HubSpot CRM (WO-016)
- ✅ DeBounce Validation (WO-017)
- ✅ n8n Webhook (WO-020)

**Common Results:**
- Zero bugs in production
- All tests pass first time
- Consistent architecture
- Easy maintenance
- Clear debugging

---

## Future Integrations (Ready to Use This Playbook)

**CRM Integrations:**
- Mautic (WO-023) - OAuth2 authentication variant
- ActiveCampaign - Similar to Brevo
- Mailchimp - Similar to Brevo

**Validation/Enrichment:**
- ZeroBounce - Similar to DeBounce
- Clearbit - Enrichment service
- FullContact - Enrichment service
- Hunter.io - Email finding + validation

**All follow this same playbook!**

---

**Document Version:** 1.0
**Last Updated:** 2025-11-19
**Maintained By:** ScraperSky Development Team
**Status:** Production-Proven ✅
