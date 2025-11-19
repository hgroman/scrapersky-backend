# WO-018: API Endpoints Handoff - For Online Claude

**Date:** 2025-11-19  
**From:** Local Claude (Windsurf)  
**To:** Online Claude (Code Implementation)  
**Priority:** 🔴 **CRITICAL - BLOCKS FRONTEND**

---

## Context: What We've Built So Far

### WO-017 Phase 1 & 2: ✅ COMPLETE

We successfully implemented DeBounce email validation:

1. **Database Schema** (8 new fields)
   - `debounce_validation_status` (Queued/Complete/Error)
   - `debounce_processing_status` (Queued/Processing/Complete/Error)
   - `debounce_result` (valid/invalid/disposable/catch-all/unknown)
   - `debounce_score` (0-100)
   - `debounce_reason` (e.g., "Deliverable", "Bounce", "Disposable")
   - `debounce_suggestion` (e.g., "did you mean...")
   - `debounce_processing_error` (error messages)
   - `debounce_validated_at` (timestamp)

2. **DeBounce Service** (`src/services/email_validation/debounce_service.py`)
   - `process_batch_validation()` - Main validation method
   - `_call_debounce_api()` - API integration (GET requests)
   - `_map_debounce_result()` - Result mapping
   - `_calculate_score()` - Score calculation
   - `_auto_queue_for_crm()` - Auto-queue valid emails

3. **Background Scheduler** (`src/services/email_validation/debounce_scheduler.py`)
   - Runs every 5 minutes automatically
   - Processes contacts with `debounce_processing_status = 'Queued'`
   - Updates database with validation results
   - **Tested and working perfectly** ✅

### Current State

**What Works:**
- ✅ Contacts get validated automatically in background
- ✅ Results stored in database
- ✅ Valid emails auto-queued for CRM sync
- ✅ Invalid/disposable emails skipped

**What's Missing:**
- ❌ **No API endpoints** for frontend to interact with validation
- ❌ Frontend cannot trigger validation manually
- ❌ Frontend cannot see validation status
- ❌ Frontend cannot filter by validation results

---

## The Problem

The frontend team wants to add email validation features to the Contact Launchpad page:

1. **"Validate Selected" button** - User selects contacts, clicks button, validation happens
2. **"Validate ALL Filtered" button** - User applies filters, clicks button, all matching contacts validated
3. **Validation status column** - Show ✅ Valid, ❌ Invalid, 🗑️ Disposable badges
4. **Validation filter** - Filter contacts by validation status
5. **Validation summary** - Show stats (X valid, Y invalid, Z pending)
6. **Real-time updates** - Poll for validation progress

**But they can't do any of this because there are no API endpoints!**

---

## Your Task: Create API Endpoints

You need to create **5 FastAPI endpoints** that expose the existing DeBounce functionality to the frontend.

### Why This Matters

The backend validation is working perfectly, but it's **invisible to users**. They need a way to:
- Manually trigger validation (instead of waiting for scheduler)
- See validation results in the UI
- Filter contacts by validation status
- Make informed decisions about which contacts to push to CRM

---

## Endpoints to Implement

### 1. POST /api/v3/contacts/validate
**Purpose:** Queue selected contacts for validation

**Request:**
```json
{
  "contact_ids": [
    "8ef2449f-d3eb-4831-b85e-a385332b6475",
    "f1bae019-a2a4-4caf-aeb6-43c1d8464fd6"
  ]
}
```

**What It Should Do:**
1. Validate UUIDs are valid format
2. Check contacts exist in database
3. Skip contacts already in "Processing" status
4. Skip contacts already "Complete" (unless re-validation requested)
5. Update `debounce_processing_status` to "Queued"
6. Return counts of queued/already_processing/already_validated

**Response:**
```json
{
  "success": true,
  "message": "2 contacts queued for validation",
  "queued_count": 2,
  "already_processing": 0,
  "already_validated": 0,
  "invalid_ids": []
}
```

**Key Point:** The scheduler will pick up queued contacts automatically within 5 minutes.

---

### 2. POST /api/v3/contacts/validate/all
**Purpose:** Queue all contacts matching filters for validation

**Request:**
```json
{
  "filters": {
    "curation_status": "Skipped",
    "validation_status": "not_validated",
    "search_email": "",
    "search_name": "",
    "domain_id": null,
    "page_id": null
  },
  "max_contacts": 100
}
```

**What It Should Do:**
1. Apply same filters as contact list endpoint
2. Find all matching contacts
3. Queue them for validation (same logic as endpoint #1)
4. Return counts

**Response:**
```json
{
  "success": true,
  "message": "25 contacts queued for validation",
  "queued_count": 25,
  "already_processing": 3,
  "already_validated": 10,
  "total_matched": 38
}
```

**Safety:** Include max_contacts limit (default 100, max 500) to prevent accidental mass queueing.

---

### 3. GET /api/v3/contacts/validation-status
**Purpose:** Get current validation status for specific contacts (for real-time polling)

**Query:** `?contact_ids=id1,id2,id3`

**What It Should Do:**
1. Parse comma-separated contact IDs
2. Query database for current status
3. Return validation results if complete

**Response:**
```json
{
  "success": true,
  "contacts": [
    {
      "id": "8ef2449f-d3eb-4831-b85e-a385332b6475",
      "email": "test@example.com",
      "validation_status": "Complete",
      "processing_status": "Complete",
      "result": "valid",
      "score": 100,
      "reason": "Deliverable",
      "validated_at": "2025-11-19T04:23:57Z"
    },
    {
      "id": "abc123...",
      "email": "pending@example.com",
      "validation_status": "Queued",
      "processing_status": "Processing",
      "result": null,
      "score": null
    }
  ]
}
```

**Key Point:** Frontend will poll this endpoint every 2 seconds to show real-time progress.

---

### 4. GET /api/v3/contacts/validation-summary
**Purpose:** Get aggregate validation statistics

**Query:** `?domain_id=uuid&page_id=uuid&curation_status=Skipped` (all optional)

**What It Should Do:**
1. Count contacts by validation status
2. Calculate percentages
3. Support optional filters

**Response:**
```json
{
  "success": true,
  "summary": {
    "total_contacts": 500,
    "validated": {
      "total": 300,
      "valid": 250,
      "invalid": 30,
      "disposable": 15,
      "catch_all": 5
    },
    "not_validated": 150,
    "pending_validation": 50,
    "validation_rate": 60.0,
    "valid_rate": 83.3
  }
}
```

**Optimization:** Cache results for 1 minute to reduce database load.

---

### 5. GET /api/v3/contacts (MODIFY EXISTING)
**Purpose:** Add validation status filtering to existing contact list endpoint

**New Query Parameters:**
- `?validation_status=valid,invalid,disposable,pending,not_validated`
- `?validation_score_min=0`
- `?validation_score_max=100`

**What It Should Do:**
1. Add validation fields to response model
2. Add validation status filter to query builder
3. Maintain backward compatibility

**Response:** (existing format + validation fields)
```json
{
  "contacts": [
    {
      "id": "...",
      "email": "test@example.com",
      "validation_status": "Complete",
      "validation_result": "valid",
      "validation_score": 100,
      "validated_at": "2025-11-19T04:23:57Z"
    }
  ],
  "pagination": { ... }
}
```

---

## File Structure

### New Files to Create

```
src/
├── routers/
│   └── v3/
│       └── contacts_validation_router.py    ⬅️ NEW
│
├── schemas/
│   └── contact_validation_schemas.py        ⬅️ NEW
│
└── services/
    └── email_validation/
        └── validation_api_service.py        ⬅️ NEW
```

### Existing Files to Modify

```
src/
├── routers/
│   └── v3/
│       └── contacts_router.py               ⬅️ MODIFY (add validation filters)
│
├── schemas/
│   └── contact_schemas.py                   ⬅️ MODIFY (add validation fields)
│
└── main.py                                  ⬅️ MODIFY (register new router)
```

---

## Implementation Pattern to Follow

### 1. Pydantic Schemas (`contact_validation_schemas.py`)

```python
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

class ValidateContactsRequest(BaseModel):
    contact_ids: List[str] = Field(
        ...,
        description="List of contact UUIDs to validate",
        min_items=1,
        max_items=100
    )

class ContactValidationDetail(BaseModel):
    id: str
    email: str
    status: str

class ValidateContactsResponse(BaseModel):
    success: bool
    message: str
    queued_count: int
    already_processing: int = 0
    already_validated: int = 0
    invalid_ids: List[str] = []

# ... more schemas
```

### 2. Service Layer (`validation_api_service.py`)

```python
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from src.models.WF7_V2_L1_1of1_ContactModel import Contact
from datetime import datetime
from typing import List, Dict

class ValidationAPIService:
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def queue_contacts_for_validation(
        self, 
        contact_ids: List[str]
    ) -> Dict:
        """
        Queue contacts for DeBounce validation.
        
        Returns:
            dict with counts of queued, already_processing, already_validated, invalid_ids
        """
        # Get contacts
        stmt = select(Contact).where(Contact.id.in_(contact_ids))
        result = await self.session.execute(stmt)
        contacts = result.scalars().all()
        
        queued = []
        already_processing = []
        already_validated = []
        invalid_ids = set(contact_ids) - {str(c.id) for c in contacts}
        
        for contact in contacts:
            if contact.debounce_processing_status == "Processing":
                already_processing.append(contact)
            elif contact.debounce_validation_status == "Complete":
                already_validated.append(contact)
            else:
                # Queue for validation
                contact.debounce_validation_status = "Queued"
                contact.debounce_processing_status = "Queued"
                contact.updated_at = datetime.utcnow()
                queued.append(contact)
        
        await self.session.commit()
        
        return {
            "success": True,
            "message": f"{len(queued)} contacts queued for validation",
            "queued_count": len(queued),
            "already_processing": len(already_processing),
            "already_validated": len(already_validated),
            "invalid_ids": list(invalid_ids)
        }
    
    # ... more methods
```

### 3. Router (`contacts_validation_router.py`)

```python
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from src.db.session import get_db_session
from src.auth.jwt_auth import get_current_user
from src.schemas.contact_validation_schemas import (
    ValidateContactsRequest,
    ValidateContactsResponse
)
from src.services.email_validation.validation_api_service import ValidationAPIService

router = APIRouter(
    prefix="/api/v3/contacts",
    tags=["Email Validation"]
)

@router.post("/validate", response_model=ValidateContactsResponse)
async def validate_contacts(
    request: ValidateContactsRequest,
    session: AsyncSession = Depends(get_db_session),
    current_user = Depends(get_current_user)
):
    """
    Queue selected contacts for DeBounce email validation.
    
    The scheduler will process queued contacts automatically within 5 minutes.
    Use GET /api/v3/contacts/validation-status to poll for results.
    """
    service = ValidationAPIService(session)
    result = await service.queue_contacts_for_validation(request.contact_ids)
    return result

# ... more endpoints
```

### 4. Register Router (`main.py`)

```python
# Add to main.py after existing routers
from src.routers.v3.contacts_validation_router import router as contacts_validation_router

app.include_router(contacts_validation_router)
```

---

## Key Implementation Notes

### 1. Don't Duplicate Validation Logic
- **DO NOT** call DeBounce API directly from endpoints
- **DO** just update `debounce_processing_status` to "Queued"
- The existing scheduler will handle actual validation
- This keeps validation logic centralized in the service

### 2. Database Queries
- Use existing `Contact` model (already has all DeBounce fields)
- Fields are already indexed for performance
- Just query and update status fields

### 3. Authentication
- All endpoints require JWT authentication
- Use existing `get_current_user` dependency
- Follow same pattern as other v3 endpoints

### 4. Error Handling
- Return 400 for invalid UUIDs
- Return 404 for contacts not found
- Return 422 for Pydantic validation errors
- Use FastAPI's automatic error responses

### 5. Testing
- Endpoints will be visible in `/docs` automatically
- Frontend will validate via Swagger UI
- Local Claude will test after implementation

---

## Success Criteria

### You're Done When:

1. ✅ All 5 endpoints implemented
2. ✅ Pydantic schemas defined with validation
3. ✅ Service layer handles business logic
4. ✅ Router registered in main.py
5. ✅ Endpoints visible in `/docs`
6. ✅ No errors when starting server
7. ✅ Can queue contacts via POST /validate
8. ✅ Can see status via GET /validation-status

### Testing Checklist:

```bash
# 1. Start server
docker compose up --build

# 2. Visit http://localhost:8000/docs

# 3. Test POST /api/v3/contacts/validate
# Body: { "contact_ids": ["uuid1", "uuid2"] }
# Expected: 200 OK with queued_count

# 4. Test GET /api/v3/contacts/validation-status
# Query: ?contact_ids=uuid1,uuid2
# Expected: 200 OK with contact statuses

# 5. Test GET /api/v3/contacts/validation-summary
# Expected: 200 OK with summary stats
```

---

## What Happens After You're Done

1. **Local Claude** will test endpoints via `/docs`
2. **Frontend team** will validate endpoints work
3. **Frontend team** will implement WO-019 (UI features)
4. **Users** will be able to validate emails manually!

---

## Questions?

If anything is unclear:
1. Check `WO-018_DEBOUNCE_API_ENDPOINTS.md` for detailed specs
2. Look at existing v3 routers for patterns
3. Check `debounce_service.py` to understand validation flow
4. Ask Local Claude for clarification

---

## Summary

**What you're building:** API endpoints to expose existing DeBounce validation to frontend

**Why it matters:** Backend works perfectly but frontend can't use it yet

**How it works:** Endpoints just queue contacts, scheduler does actual validation

**Time estimate:** 4-6 hours for Phase 1 (core endpoints)

**Priority:** CRITICAL - Frontend is blocked waiting for this

---

**Ready to implement?** Start with endpoint #1 (POST /validate) and work your way through!

**Good luck!** 🚀

---

**Created:** 2025-11-19  
**Author:** Local Claude (Windsurf)  
**For:** Online Claude (Code Implementation)
