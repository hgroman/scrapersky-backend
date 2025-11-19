# WO-018: CRM Sync API Endpoints & User Interface Layer

**Work Order:** WO-018
**Created:** 2025-11-18
**Status:** Future Work (Handoff Document)
**Priority:** High
**Depends On:** WO-015 (Brevo), WO-016 (HubSpot)
**Estimated Effort:** 6-8 hours

---

## Executive Summary

The CRM sync backend (Brevo, HubSpot) is complete with core services and schedulers, but **lacks user-facing API endpoints** for queueing contacts, checking status, and managing sync operations. This work order addresses the missing interface layer between frontend/users and the background sync services.

**Current State:**
- ✅ Database schema complete (WO-015.2)
- ✅ Brevo sync service + scheduler (WO-015)
- ✅ HubSpot sync service + scheduler (WO-016)
- ✅ Dual-status adapter pattern validated
- ✅ Retry logic with exponential backoff

**Missing:**
- ❌ API endpoints to queue contacts for sync
- ❌ API endpoints to check sync status
- ❌ API endpoints to retry failed syncs
- ❌ Bulk operation endpoints
- ❌ Admin credential validation endpoints

---

## Context for AI Handoff

### What Already Exists

**Database Schema (WO-015.2):**
```python
# Contact model has these fields for each CRM (Brevo, HubSpot, Mautic, n8n):
{crm}_sync_status: Mapped[Optional[str]]        # User decision
{crm}_processing_status: Mapped[Optional[str]]  # System state
{crm}_processing_error: Mapped[Optional[str]]   # Error messages
{crm}_contact_id: Mapped[Optional[str]]         # CRM's contact ID

# Shared retry fields:
retry_count: Mapped[int]
next_retry_at: Mapped[Optional[datetime]]
last_retry_at: Mapped[Optional[datetime]]
last_failed_crm: Mapped[Optional[str]]
```

**ENUMs:**
```python
class CRMSyncStatus(str, Enum):
    Selected = "Selected"  # User selected for sync
    Queued = "Queued"      # Queued for processing
    Processing = "Processing"
    Complete = "Complete"
    Error = "Error"
    Skipped = "Skipped"

class CRMProcessingStatus(str, Enum):
    Queued = "Queued"
    Processing = "Processing"
    Complete = "Complete"
    Error = "Error"
```

**Background Services:**
- `src/services/crm/brevo_sync_service.py` - Core Brevo sync logic
- `src/services/crm/brevo_sync_scheduler.py` - Automatic background processing
- `src/services/crm/hubspot_sync_service.py` - Core HubSpot sync logic
- `src/services/crm/hubspot_sync_scheduler.py` - Automatic background processing

**Pattern Reference:**
- See `src/routers/v3/contacts_router.py` for existing contact endpoints
- See `src/routers/v3/WF7_V3_L3_1of1_PagesRouter.py` for status update patterns

### How Sync Currently Works

**Manual Path (Testing Only):**
```bash
# User manually sets status in database:
UPDATE contacts SET brevo_sync_status = 'Queued', brevo_processing_status = 'Queued' WHERE id = '...';

# Scheduler picks it up automatically (every 5 minutes)
# OR use test script:
python test_manual_brevo_sync.py <contact_id>
```

**What's Missing:** User-facing API to do this programmatically.

---

## Required API Endpoints

### Group 1: Queue for Sync (High Priority)

#### 1.1 Queue Single Contact
```http
POST /api/v3/contacts/{contact_id}/queue-sync
Content-Type: application/json

{
  "crm": "brevo",  // or "hubspot", "mautic", "n8n"
  "priority": "normal"  // optional: "high" for immediate processing
}

Response 200:
{
  "contact_id": "uuid",
  "crm": "brevo",
  "sync_status": "Queued",
  "processing_status": "Queued",
  "estimated_processing_time": "Within 5 minutes"
}

Response 400:
{
  "error": "Contact does not have email address"
}

Response 404:
{
  "error": "Contact not found"
}
```

**Implementation Notes:**
- Validate contact exists
- Validate contact has email
- Set `{crm}_sync_status = 'Queued'`
- Set `{crm}_processing_status = 'Queued'`
- Reset retry fields: `retry_count = 0`, `next_retry_at = NULL`
- Commit to database
- Return status

**Code Pattern:**
```python
from src.models.WF7_V2_L1_1of1_ContactModel import Contact
from src.models.enums import CRMSyncStatus, CRMProcessingStatus

async def queue_contact_for_sync(contact_id: UUID, crm: str, session: AsyncSession):
    contact = await session.get(Contact, contact_id)
    if not contact:
        raise HTTPException(404, "Contact not found")
    if not contact.email:
        raise HTTPException(400, "Contact has no email address")

    # Set status fields dynamically based on CRM
    setattr(contact, f"{crm}_sync_status", CRMSyncStatus.Queued.value)
    setattr(contact, f"{crm}_processing_status", CRMProcessingStatus.Queued.value)
    contact.retry_count = 0
    contact.next_retry_at = None

    await session.commit()
    return contact
```

#### 1.2 Queue Multiple Contacts (Bulk)
```http
POST /api/v3/contacts/bulk-queue-sync
Content-Type: application/json

{
  "contact_ids": ["uuid1", "uuid2", "uuid3", ...],  // Max 100
  "crm": "brevo"
}

Response 200:
{
  "queued": 95,
  "skipped": 5,
  "errors": [
    {
      "contact_id": "uuid",
      "reason": "No email address"
    }
  ]
}
```

**Implementation Notes:**
- Batch update in database (more efficient than individual updates)
- Return summary with success/failure counts

#### 1.3 Queue All Contacts (Filtered)
```http
POST /api/v3/contacts/queue-all-sync
Content-Type: application/json

{
  "crm": "hubspot",
  "filters": {
    "has_email": true,
    "not_already_synced": true,
    "domain_id": "optional-uuid"  // Optional filter
  }
}

Response 200:
{
  "queued_count": 1523,
  "estimated_completion": "2025-11-18T15:30:00Z"
}
```

### Group 2: Status Queries (High Priority)

#### 2.1 Get Contact Sync Status
```http
GET /api/v3/contacts/{contact_id}/sync-status

Response 200:
{
  "contact_id": "uuid",
  "email": "user@example.com",
  "brevo": {
    "sync_status": "Complete",
    "processing_status": "Complete",
    "contact_id": "user@example.com",
    "synced_at": "2025-11-18T10:00:00Z"
  },
  "hubspot": {
    "sync_status": "Queued",
    "processing_status": "Queued",
    "contact_id": null,
    "estimated_processing": "Within 5 minutes"
  },
  "mautic": {
    "sync_status": null,
    "processing_status": null,
    "contact_id": null
  },
  "n8n": {
    "sync_status": null,
    "processing_status": null,
    "contact_id": null
  }
}
```

#### 2.2 Get Sync Statistics (Dashboard)
```http
GET /api/v3/contacts/sync-stats?crm=brevo

Response 200:
{
  "crm": "brevo",
  "total_contacts": 10000,
  "synced": 8500,
  "queued": 1200,
  "processing": 50,
  "errors": 250,
  "success_rate": 0.85,
  "last_24h": {
    "synced": 1200,
    "errors": 15
  }
}
```

#### 2.3 Get Failed Sync Contacts
```http
GET /api/v3/contacts/sync-failures?crm=hubspot&limit=50

Response 200:
{
  "crm": "hubspot",
  "failures": [
    {
      "contact_id": "uuid",
      "email": "user@example.com",
      "error": "HubSpot API authentication failed (HTTP 401)",
      "retry_count": 3,
      "last_retry_at": "2025-11-18T10:00:00Z",
      "can_retry": false  // Max retries exceeded
    }
  ],
  "total": 45
}
```

### Group 3: Manual Retry (High Priority)

#### 3.1 Retry Failed Sync
```http
POST /api/v3/contacts/{contact_id}/retry-sync
Content-Type: application/json

{
  "crm": "brevo",
  "reset_retry_count": false  // true = reset to 0 and retry from scratch
}

Response 200:
{
  "contact_id": "uuid",
  "crm": "brevo",
  "retry_count": 4,  // Incremented
  "next_retry_at": "2025-11-18T10:30:00Z",
  "message": "Retry scheduled"
}

Response 400:
{
  "error": "Contact not in error state"
}
```

**Implementation Notes:**
- If `reset_retry_count = true`: Set `retry_count = 0`, `next_retry_at = NULL`
- If `reset_retry_count = false`: Increment `retry_count`, calculate `next_retry_at`
- Set `{crm}_sync_status = 'Queued'`
- Set `{crm}_processing_status = 'Queued'`

#### 3.2 Bulk Retry All Failures
```http
POST /api/v3/contacts/retry-all-failures
Content-Type: application/json

{
  "crm": "hubspot",
  "reset_retry_count": true
}

Response 200:
{
  "crm": "hubspot",
  "retried_count": 45,
  "message": "All failures reset and queued for retry"
}
```

### Group 4: Admin/Configuration (Medium Priority)

#### 4.1 Test CRM Credentials
```http
POST /api/v3/admin/test-crm-credentials
Content-Type: application/json

{
  "crm": "brevo",
  "api_key": "xkeysib-test-key-here"  // Optional - test from .env if not provided
}

Response 200:
{
  "crm": "brevo",
  "status": "valid",
  "message": "Successfully authenticated with Brevo API"
}

Response 400:
{
  "crm": "hubspot",
  "status": "invalid",
  "error": "HTTP 401: Unauthorized",
  "message": "Invalid API token"
}
```

**Implementation Notes:**
- Create test contact payload
- Call CRM API search endpoint
- Don't create actual contact (just test auth)
- Return authentication status

#### 4.2 Get CRM Configuration
```http
GET /api/v3/admin/crm-config

Response 200:
{
  "brevo": {
    "enabled": true,
    "api_key_configured": true,
    "scheduler_interval": 5,
    "batch_size": 10
  },
  "hubspot": {
    "enabled": true,
    "api_key_configured": true,
    "scheduler_interval": 5,
    "batch_size": 10,
    "custom_properties": ["scrapersky_domain_id", "scrapersky_page_id"]
  },
  "mautic": {
    "enabled": false,
    "api_key_configured": false
  },
  "n8n": {
    "enabled": false,
    "api_key_configured": false
  }
}
```

---

## Implementation Plan

### Phase 1: Queue Endpoints (3-4 hours)

**Files to Create:**
```
src/routers/v3/crm_sync_router.py (NEW)
```

**Endpoints:**
1. POST `/api/v3/contacts/{contact_id}/queue-sync`
2. POST `/api/v3/contacts/bulk-queue-sync`
3. POST `/api/v3/contacts/queue-all-sync`

**Dependencies:**
```python
from src.models.WF7_V2_L1_1of1_ContactModel import Contact
from src.models.enums import CRMSyncStatus, CRMProcessingStatus
from src.session.async_session import get_db_session
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
```

**Pydantic Models:**
```python
class QueueSyncRequest(BaseModel):
    crm: str  # brevo, hubspot, mautic, n8n
    priority: str = "normal"

class BulkQueueRequest(BaseModel):
    contact_ids: list[UUID]
    crm: str

class QueueAllRequest(BaseModel):
    crm: str
    filters: dict = {}
```

### Phase 2: Status Endpoints (2 hours)

**Endpoints:**
1. GET `/api/v3/contacts/{contact_id}/sync-status`
2. GET `/api/v3/contacts/sync-stats`
3. GET `/api/v3/contacts/sync-failures`

**SQL Queries:**
```python
# Sync stats example:
SELECT
    COUNT(*) FILTER (WHERE brevo_sync_status = 'Complete') as synced,
    COUNT(*) FILTER (WHERE brevo_sync_status = 'Queued') as queued,
    COUNT(*) FILTER (WHERE brevo_sync_status = 'Processing') as processing,
    COUNT(*) FILTER (WHERE brevo_sync_status = 'Error') as errors
FROM contacts
WHERE brevo_sync_status IS NOT NULL;
```

### Phase 3: Retry Endpoints (1-2 hours)

**Endpoints:**
1. POST `/api/v3/contacts/{contact_id}/retry-sync`
2. POST `/api/v3/contacts/retry-all-failures`

**Logic:**
- Reset retry fields
- Re-queue for processing
- Return confirmation

### Phase 4: Admin Endpoints (1-2 hours)

**Endpoints:**
1. POST `/api/v3/admin/test-crm-credentials`
2. GET `/api/v3/admin/crm-config`

**Integration:**
```python
# Test Brevo credentials:
from src.services.crm.brevo_sync_service import BrevoSyncService

async def test_brevo_credentials(api_key: str = None):
    service = BrevoSyncService()
    if api_key:
        service.api_key = api_key

    # Try to search for non-existent contact (tests auth without creating data)
    try:
        headers = {"api-key": service.api_key}
        response = await client.post(
            f"{service.base_url}/contacts",
            headers=headers,
            json={"email": "test@scrapersky-test.com", "listIds": []}
        )
        return {"status": "valid"}
    except Exception as e:
        return {"status": "invalid", "error": str(e)}
```

### Phase 5: Router Registration (30 min)

**File:** `src/main.py`

Add:
```python
from .routers.v3.crm_sync_router import router as crm_sync_router

app.include_router(crm_sync_router)
```

---

## Testing Strategy

### Manual Testing

**Queue Contact:**
```bash
curl -X POST http://localhost:8008/api/v3/contacts/{uuid}/queue-sync \
  -H "Content-Type: application/json" \
  -d '{"crm": "brevo"}'
```

**Check Status:**
```bash
curl http://localhost:8008/api/v3/contacts/{uuid}/sync-status
```

**Verify in Database:**
```sql
SELECT
    email,
    brevo_sync_status,
    brevo_processing_status,
    hubspot_sync_status,
    hubspot_processing_status
FROM contacts
WHERE id = 'uuid';
```

**Wait for Scheduler:**
- Scheduler runs every 5 minutes
- Contact should sync automatically
- Check logs for sync activity

### Integration Testing

**Test Plan:** Create `WO-018_CRM_API_TEST_PLAN.md` with:
1. Queue single contact → Verify status → Wait for sync → Verify complete
2. Bulk queue 50 contacts → Verify all queued → Monitor scheduler
3. Force error (invalid API key) → Check failure endpoint → Retry endpoint
4. Test credential validation for all 4 CRMs

---

## Success Criteria

- [ ] Queue endpoints accept contact IDs and set database status correctly
- [ ] Status endpoints return accurate sync state for all CRMs
- [ ] Retry endpoints reset failed contacts and re-queue
- [ ] Admin endpoints validate credentials without creating test data
- [ ] All endpoints include proper error handling (404, 400, 500)
- [ ] Bulk operations handle 100+ contacts efficiently
- [ ] OpenAPI documentation auto-generated for all endpoints
- [ ] Integration test plan passes with Docker + Supabase MCP

---

## Related Work Orders

- **WO-015:** Brevo CRM Integration (reference for service layer)
- **WO-016:** HubSpot CRM Integration (reference for service layer)
- **WO-015.2:** Database Migration (schema context)
- **Future:** WO-019 (Mautic), WO-020 (n8n) will need same API pattern

---

## API Design Principles

**Consistency:**
- All CRM operations use same endpoint pattern
- CRM identifier passed as parameter: `{"crm": "brevo"}`
- Status responses use same structure across all CRMs

**Safety:**
- Validate contact exists before queueing
- Validate contact has email
- Return detailed error messages
- Use transactions for database updates

**Performance:**
- Bulk endpoints for >100 contacts
- Efficient SQL queries with filters
- Pagination for large result sets

**Future-Proof:**
- Generic `crm` parameter supports Mautic, n8n without code changes
- Status structure accommodates additional CRMs
- Admin endpoints work with any CRM service

---

## Estimated Effort Breakdown

| Phase | Endpoints | Time |
|-------|-----------|------|
| Phase 1: Queue | 3 endpoints | 3-4 hours |
| Phase 2: Status | 3 endpoints | 2 hours |
| Phase 3: Retry | 2 endpoints | 1-2 hours |
| Phase 4: Admin | 2 endpoints | 1-2 hours |
| Phase 5: Integration | Router + main.py | 30 min |
| **TOTAL** | **10 endpoints** | **6-8 hours** |

---

## Document Control

**Version:** 1.0
**Status:** Handoff Document (Future Work)
**Dependencies:** WO-015, WO-016
**Next Implementer:** Future AI agent or developer

---

**END OF WORK ORDER**
