# WO-018: DeBounce Email Validation - API Endpoints

**Date:** 2025-11-19  
**Priority:** 🟡 **HIGH**  
**Depends On:** WO-017 (Complete ✅)  
**Status:** 📋 **READY FOR IMPLEMENTATION**

---

## Objective

Create FastAPI endpoints to expose DeBounce email validation functionality to the frontend. Frontend will validate endpoints via FastAPI automatic documentation (`/docs`).

---

## API Endpoints Overview

### Summary Table

| Endpoint | Method | Purpose | Auth Required |
|----------|--------|---------|---------------|
| `/api/contacts/validate` | POST | Trigger validation for selected contacts | ✅ Yes |
| `/api/contacts/validate/all` | POST | Trigger validation for filtered contacts | ✅ Yes |
| `/api/contacts/validation-status` | GET | Get validation status for contacts | ✅ Yes |
| `/api/contacts/validation-summary` | GET | Get validation statistics | ✅ Yes |
| `/api/contacts` | GET | List contacts (add validation filters) | ✅ Yes |

---

## Endpoint Specifications

### 1. Trigger Validation for Selected Contacts

**Endpoint:** `POST /api/contacts/validate`

**Purpose:** Queue specific contacts for DeBounce email validation

**Request Body:**
```json
{
  "contact_ids": [
    "8ef2449f-d3eb-4831-b85e-a385332b6475",
    "f1bae019-a2a4-4caf-aeb6-43c1d8464fd6"
  ]
}
```

**Response (200 OK):**
```json
{
  "success": true,
  "message": "2 contacts queued for validation",
  "queued_count": 2,
  "already_processing": 0,
  "already_validated": 0,
  "invalid_ids": [],
  "details": {
    "queued": [
      {
        "id": "8ef2449f-d3eb-4831-b85e-a385332b6475",
        "email": "test@example.com",
        "status": "queued"
      }
    ]
  }
}
```

**Response (400 Bad Request):**
```json
{
  "success": false,
  "message": "No valid contact IDs provided",
  "error": "contact_ids must be a non-empty array"
}
```

**Response (404 Not Found):**
```json
{
  "success": false,
  "message": "Some contacts not found",
  "queued_count": 1,
  "invalid_ids": ["invalid-uuid-here"]
}
```

**Pydantic Models:**
```python
from pydantic import BaseModel, Field
from typing import List, Optional

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
    status: str  # "queued", "already_processing", "already_validated"

class ValidateContactsResponse(BaseModel):
    success: bool
    message: str
    queued_count: int
    already_processing: int = 0
    already_validated: int = 0
    invalid_ids: List[str] = []
    details: Optional[dict] = None
```

**Implementation Notes:**
- Validate all UUIDs are valid format
- Check contacts exist in database
- Skip contacts already in "Processing" status
- Skip contacts already "Complete" (unless re-validation requested)
- Update `debounce_processing_status` to "Queued"
- Scheduler will pick up queued contacts automatically
- Return detailed breakdown of what happened

---

### 2. Trigger Validation for Filtered Contacts

**Endpoint:** `POST /api/contacts/validate/all`

**Purpose:** Queue all contacts matching current filters for validation

**Request Body:**
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

**Response (200 OK):**
```json
{
  "success": true,
  "message": "25 contacts queued for validation",
  "queued_count": 25,
  "already_processing": 3,
  "already_validated": 10,
  "total_matched": 38,
  "filters_applied": {
    "curation_status": "Skipped",
    "validation_status": "not_validated"
  }
}
```

**Pydantic Models:**
```python
class ContactFilters(BaseModel):
    curation_status: Optional[str] = None
    validation_status: Optional[str] = None  # "valid", "invalid", "disposable", "pending", "not_validated"
    search_email: Optional[str] = None
    search_name: Optional[str] = None
    domain_id: Optional[str] = None
    page_id: Optional[str] = None

class ValidateAllContactsRequest(BaseModel):
    filters: ContactFilters
    max_contacts: int = Field(
        default=100,
        ge=1,
        le=500,
        description="Maximum number of contacts to queue (safety limit)"
    )

class ValidateAllContactsResponse(BaseModel):
    success: bool
    message: str
    queued_count: int
    already_processing: int
    already_validated: int
    total_matched: int
    filters_applied: dict
```

**Implementation Notes:**
- Apply same filters as contact list endpoint
- Add safety limit (max 500 contacts per request)
- Return count of contacts that matched filters
- Return count of contacts actually queued
- Skip already processing/validated contacts
- Log the bulk validation request for audit

---

### 3. Get Validation Status for Contacts

**Endpoint:** `GET /api/contacts/validation-status`

**Purpose:** Get current validation status for specific contacts (for real-time updates)

**Query Parameters:**
```
?contact_ids=id1,id2,id3
```

**Response (200 OK):**
```json
{
  "success": true,
  "contacts": [
    {
      "id": "8ef2449f-d3eb-4831-b85e-a385332b6475",
      "email": "test.valid@gmail.com",
      "validation_status": "Complete",
      "processing_status": "Complete",
      "result": "valid",
      "score": 100,
      "reason": "Deliverable",
      "suggestion": "",
      "validated_at": "2025-11-19T04:23:57.684093Z",
      "error": null
    },
    {
      "id": "f1bae019-a2a4-4caf-aeb6-43c1d8464fd6",
      "email": "test@invalid.com",
      "validation_status": "Complete",
      "processing_status": "Complete",
      "result": "invalid",
      "score": 0,
      "reason": "Bounce",
      "suggestion": "",
      "validated_at": "2025-11-19T04:23:59.277236Z",
      "error": null
    },
    {
      "id": "abc123...",
      "email": "pending@example.com",
      "validation_status": "Queued",
      "processing_status": "Processing",
      "result": null,
      "score": null,
      "reason": null,
      "suggestion": null,
      "validated_at": null,
      "error": null
    }
  ]
}
```

**Pydantic Models:**
```python
from datetime import datetime

class ContactValidationStatus(BaseModel):
    id: str
    email: str
    validation_status: str  # "Queued", "Complete", "Error"
    processing_status: str  # "Queued", "Processing", "Complete", "Error"
    result: Optional[str] = None  # "valid", "invalid", "disposable", "catch-all", "unknown"
    score: Optional[int] = None  # 0-100
    reason: Optional[str] = None
    suggestion: Optional[str] = None
    validated_at: Optional[datetime] = None
    error: Optional[str] = None

class ValidationStatusResponse(BaseModel):
    success: bool
    contacts: List[ContactValidationStatus]
```

**Implementation Notes:**
- Accept comma-separated list of contact IDs
- Return current status for each contact
- Include validation results if complete
- Include error message if validation failed
- Frontend can poll this endpoint for real-time updates
- Consider adding WebSocket support in future

---

### 4. Get Validation Summary Statistics

**Endpoint:** `GET /api/contacts/validation-summary`

**Purpose:** Get aggregate validation statistics for dashboard/summary display

**Query Parameters:**
```
?domain_id=uuid (optional)
?page_id=uuid (optional)
?curation_status=Skipped (optional)
```

**Response (200 OK):**
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
      "catch_all": 5,
      "unknown": 0
    },
    "not_validated": 150,
    "pending_validation": 50,
    "validation_rate": 60.0,
    "valid_rate": 83.3,
    "last_updated": "2025-11-19T04:30:00Z"
  },
  "filters_applied": {
    "domain_id": null,
    "page_id": null,
    "curation_status": null
  }
}
```

**Pydantic Models:**
```python
class ValidationBreakdown(BaseModel):
    total: int
    valid: int
    invalid: int
    disposable: int
    catch_all: int
    unknown: int

class ValidationSummary(BaseModel):
    total_contacts: int
    validated: ValidationBreakdown
    not_validated: int
    pending_validation: int
    validation_rate: float  # Percentage
    valid_rate: float  # Percentage of validated that are valid
    last_updated: datetime

class ValidationSummaryResponse(BaseModel):
    success: bool
    summary: ValidationSummary
    filters_applied: dict
```

**Implementation Notes:**
- Calculate statistics from database
- Support optional filters (domain, page, status)
- Cache results for 1 minute to reduce DB load
- Return percentages for easy display
- Include timestamp of last validation

---

### 5. Enhanced Contact List Endpoint

**Endpoint:** `GET /api/contacts` (MODIFY EXISTING)

**Purpose:** Add validation status filtering to existing contact list endpoint

**New Query Parameters:**
```
?validation_status=valid,invalid,disposable,pending,not_validated
?validation_score_min=0
?validation_score_max=100
?sort_by=validation_score (new option)
```

**Response (200 OK):**
```json
{
  "success": true,
  "contacts": [
    {
      "id": "...",
      "email": "test@example.com",
      "name": "Test User",
      "curation_status": "Skipped",
      "validation_status": "Complete",
      "validation_result": "valid",
      "validation_score": 100,
      "brevo_sync_status": "Queued",
      "hubspot_sync_status": "New",
      "created_at": "2025-11-19T00:00:00Z",
      "validated_at": "2025-11-19T04:23:57Z"
    }
  ],
  "pagination": {
    "page": 1,
    "per_page": 50,
    "total": 250,
    "total_pages": 5
  },
  "filters_applied": {
    "validation_status": ["valid"],
    "curation_status": "Skipped"
  }
}
```

**Implementation Notes:**
- Add validation fields to contact response model
- Add validation status filter to query builder
- Add validation score range filter
- Add sort by validation score option
- Maintain backward compatibility

---

## Database Queries

### Query 1: Queue Contacts for Validation
```python
async def queue_contacts_for_validation(
    session: AsyncSession,
    contact_ids: List[str]
) -> dict:
    """
    Queue contacts for DeBounce validation.
    
    Returns:
        dict with counts of queued, already_processing, already_validated, invalid_ids
    """
    # Get contacts
    stmt = select(Contact).where(Contact.id.in_(contact_ids))
    result = await session.execute(stmt)
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
    
    await session.commit()
    
    return {
        "queued": queued,
        "already_processing": already_processing,
        "already_validated": already_validated,
        "invalid_ids": list(invalid_ids)
    }
```

### Query 2: Get Validation Summary
```python
async def get_validation_summary(
    session: AsyncSession,
    domain_id: Optional[str] = None,
    page_id: Optional[str] = None,
    curation_status: Optional[str] = None
) -> dict:
    """Get validation statistics."""
    
    # Base query
    stmt = select(Contact)
    
    # Apply filters
    if domain_id:
        stmt = stmt.where(Contact.domain_id == domain_id)
    if page_id:
        stmt = stmt.where(Contact.page_id == page_id)
    if curation_status:
        stmt = stmt.where(Contact.curation_status == curation_status)
    
    # Get all contacts
    result = await session.execute(stmt)
    contacts = result.scalars().all()
    
    # Calculate statistics
    total = len(contacts)
    validated = [c for c in contacts if c.debounce_validation_status == "Complete"]
    valid = [c for c in validated if c.debounce_result == "valid"]
    invalid = [c for c in validated if c.debounce_result == "invalid"]
    disposable = [c for c in validated if c.debounce_result == "disposable"]
    catch_all = [c for c in validated if c.debounce_result == "catch-all"]
    unknown = [c for c in validated if c.debounce_result == "unknown"]
    not_validated = [c for c in contacts if c.debounce_validation_status != "Complete"]
    pending = [c for c in contacts if c.debounce_processing_status in ["Queued", "Processing"]]
    
    return {
        "total_contacts": total,
        "validated": {
            "total": len(validated),
            "valid": len(valid),
            "invalid": len(invalid),
            "disposable": len(disposable),
            "catch_all": len(catch_all),
            "unknown": len(unknown)
        },
        "not_validated": len(not_validated),
        "pending_validation": len(pending),
        "validation_rate": (len(validated) / total * 100) if total > 0 else 0,
        "valid_rate": (len(valid) / len(validated) * 100) if len(validated) > 0 else 0
    }
```

---

## File Structure

### New Files to Create

```
src/
├── routers/
│   └── contacts_validation.py          # NEW - Validation endpoints
├── schemas/
│   └── contact_validation.py           # NEW - Pydantic models
└── services/
    └── email_validation/
        └── validation_api_service.py   # NEW - Business logic
```

### Existing Files to Modify

```
src/
├── routers/
│   └── contacts.py                     # MODIFY - Add validation filters
└── schemas/
    └── contact.py                      # MODIFY - Add validation fields
```

---

## Implementation Plan

### Phase 1: Core Endpoints (Priority 1)
1. ✅ Create Pydantic models (`contact_validation.py`)
2. ✅ Create validation API service (`validation_api_service.py`)
3. ✅ Create validation router (`contacts_validation.py`)
4. ✅ Implement `POST /api/contacts/validate`
5. ✅ Implement `GET /api/contacts/validation-status`
6. ✅ Register router in `main.py`
7. ✅ Test via FastAPI docs (`/docs`)

### Phase 2: Bulk Operations (Priority 2)
1. ✅ Implement `POST /api/contacts/validate/all`
2. ✅ Implement `GET /api/contacts/validation-summary`
3. ✅ Add validation filters to existing contact list endpoint
4. ✅ Test bulk operations via FastAPI docs

### Phase 3: Enhanced Features (Priority 3)
1. ⏳ Add re-validation support (force re-validate completed contacts)
2. ⏳ Add validation history endpoint
3. ⏳ Add WebSocket support for real-time updates
4. ⏳ Add validation export endpoint (CSV/JSON)

---

## Router Implementation Example

```python
# src/routers/contacts_validation.py

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from src.session.async_session import get_session_dependency
from src.schemas.contact_validation import (
    ValidateContactsRequest,
    ValidateContactsResponse,
    ValidateAllContactsRequest,
    ValidateAllContactsResponse,
    ValidationStatusResponse,
    ValidationSummaryResponse
)
from src.services.email_validation.validation_api_service import ValidationAPIService

router = APIRouter(
    prefix="/api/contacts",
    tags=["Email Validation"]
)

@router.post("/validate", response_model=ValidateContactsResponse)
async def validate_contacts(
    request: ValidateContactsRequest,
    session: AsyncSession = Depends(get_session_dependency)
):
    """
    Queue selected contacts for DeBounce email validation.
    
    - **contact_ids**: List of contact UUIDs to validate (max 100)
    
    Returns counts of queued, already processing, and already validated contacts.
    """
    service = ValidationAPIService(session)
    result = await service.queue_contacts_for_validation(request.contact_ids)
    return result

@router.post("/validate/all", response_model=ValidateAllContactsResponse)
async def validate_all_contacts(
    request: ValidateAllContactsRequest,
    session: AsyncSession = Depends(get_session_dependency)
):
    """
    Queue all contacts matching filters for DeBounce email validation.
    
    - **filters**: Contact filters (status, domain, page, etc.)
    - **max_contacts**: Safety limit (default 100, max 500)
    
    Returns counts of queued and already processed contacts.
    """
    service = ValidationAPIService(session)
    result = await service.queue_filtered_contacts_for_validation(
        request.filters,
        request.max_contacts
    )
    return result

@router.get("/validation-status", response_model=ValidationStatusResponse)
async def get_validation_status(
    contact_ids: str,  # Comma-separated list
    session: AsyncSession = Depends(get_session_dependency)
):
    """
    Get current validation status for specific contacts.
    
    - **contact_ids**: Comma-separated list of contact UUIDs
    
    Returns validation status, results, and scores for each contact.
    Use for real-time status updates in frontend.
    """
    ids = [id.strip() for id in contact_ids.split(",")]
    service = ValidationAPIService(session)
    result = await service.get_validation_status(ids)
    return result

@router.get("/validation-summary", response_model=ValidationSummaryResponse)
async def get_validation_summary(
    domain_id: str = None,
    page_id: str = None,
    curation_status: str = None,
    session: AsyncSession = Depends(get_session_dependency)
):
    """
    Get aggregate validation statistics.
    
    - **domain_id**: Optional filter by domain
    - **page_id**: Optional filter by page
    - **curation_status**: Optional filter by curation status
    
    Returns validation summary with counts and percentages.
    """
    service = ValidationAPIService(session)
    result = await service.get_validation_summary(
        domain_id=domain_id,
        page_id=page_id,
        curation_status=curation_status
    )
    return result
```

---

## Error Handling

### Standard Error Responses

```python
# 400 Bad Request
{
    "detail": "Invalid request: contact_ids must be a non-empty array"
}

# 404 Not Found
{
    "detail": "Contacts not found: [uuid1, uuid2]"
}

# 422 Unprocessable Entity (Pydantic validation)
{
    "detail": [
        {
            "loc": ["body", "contact_ids"],
            "msg": "field required",
            "type": "value_error.missing"
        }
    ]
}

# 500 Internal Server Error
{
    "detail": "Internal server error: Database connection failed"
}
```

---

## Testing Strategy

### 1. FastAPI Docs Testing (`/docs`)
Frontend will validate all endpoints via automatic documentation:
- Test request/response schemas
- Test validation rules
- Test error responses
- Test query parameters
- Test pagination

### 2. Manual Testing Script
```python
# test_validation_endpoints.py

import httpx
import asyncio

BASE_URL = "http://localhost:8000"

async def test_validate_contacts():
    """Test POST /api/contacts/validate"""
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{BASE_URL}/api/contacts/validate",
            json={
                "contact_ids": [
                    "8ef2449f-d3eb-4831-b85e-a385332b6475",
                    "f1bae019-a2a4-4caf-aeb6-43c1d8464fd6"
                ]
            }
        )
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")

async def test_validation_status():
    """Test GET /api/contacts/validation-status"""
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{BASE_URL}/api/contacts/validation-status",
            params={
                "contact_ids": "8ef2449f-d3eb-4831-b85e-a385332b6475,f1bae019-a2a4-4caf-aeb6-43c1d8464fd6"
            }
        )
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")

async def test_validation_summary():
    """Test GET /api/contacts/validation-summary"""
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{BASE_URL}/api/contacts/validation-summary"
        )
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")

if __name__ == "__main__":
    asyncio.run(test_validate_contacts())
    asyncio.run(test_validation_status())
    asyncio.run(test_validation_summary())
```

---

## Frontend Integration Notes

### Polling Strategy
```typescript
// Frontend can poll validation-status endpoint
const pollValidationStatus = async (contactIds: string[]) => {
  const interval = setInterval(async () => {
    const response = await fetch(
      `/api/contacts/validation-status?contact_ids=${contactIds.join(',')}`
    );
    const data = await response.json();
    
    // Check if all contacts are complete
    const allComplete = data.contacts.every(
      c => c.processing_status === 'Complete' || c.processing_status === 'Error'
    );
    
    if (allComplete) {
      clearInterval(interval);
      // Update UI with final results
    }
  }, 2000); // Poll every 2 seconds
};
```

### Real-time Updates (Future)
```typescript
// WebSocket support (Phase 3)
const ws = new WebSocket('ws://localhost:8000/ws/validation');
ws.onmessage = (event) => {
  const update = JSON.parse(event.data);
  // Update UI with real-time validation status
};
```

---

## Security Considerations

### Authentication
- All endpoints require authentication (JWT token)
- Validate user has access to requested contacts
- Rate limit validation requests (max 10 per minute per user)

### Input Validation
- Validate all UUIDs are valid format
- Limit array sizes (max 100 contact IDs per request)
- Sanitize search inputs to prevent SQL injection
- Validate filter values against allowed enums

### Rate Limiting
```python
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

@router.post("/validate")
@limiter.limit("10/minute")
async def validate_contacts(...):
    ...
```

---

## Performance Optimization

### Caching
```python
from functools import lru_cache
from datetime import datetime, timedelta

# Cache validation summary for 1 minute
_summary_cache = {}
_cache_ttl = timedelta(minutes=1)

async def get_validation_summary_cached(...):
    cache_key = f"{domain_id}:{page_id}:{curation_status}"
    
    if cache_key in _summary_cache:
        cached_data, cached_time = _summary_cache[cache_key]
        if datetime.utcnow() - cached_time < _cache_ttl:
            return cached_data
    
    # Fetch fresh data
    data = await get_validation_summary(...)
    _summary_cache[cache_key] = (data, datetime.utcnow())
    return data
```

### Database Indexing
```sql
-- Already created in WO-017
CREATE INDEX idx_contacts_debounce_processing_status ON contacts(debounce_processing_status);
CREATE INDEX idx_contacts_debounce_result ON contacts(debounce_result);

-- Additional indexes for filtering
CREATE INDEX idx_contacts_debounce_validation_status ON contacts(debounce_validation_status);
CREATE INDEX idx_contacts_debounce_score ON contacts(debounce_score);
```

---

## Documentation

### OpenAPI/Swagger Tags
```python
tags_metadata = [
    {
        "name": "Email Validation",
        "description": "DeBounce email validation operations. Queue contacts for validation, check status, and view statistics.",
    }
]
```

### Endpoint Descriptions
- Each endpoint has detailed docstring
- Request/response examples in Pydantic models
- Error responses documented
- Query parameters explained

---

## Success Criteria

### Phase 1 Complete When:
- ✅ All core endpoints implemented
- ✅ Pydantic models defined with validation
- ✅ Endpoints visible in FastAPI docs (`/docs`)
- ✅ Manual testing script passes
- ✅ Error handling works correctly

### Phase 2 Complete When:
- ✅ Bulk operations working
- ✅ Validation summary accurate
- ✅ Contact list filters working
- ✅ Frontend can validate via `/docs`

### Phase 3 Complete When:
- ✅ Re-validation support added
- ✅ WebSocket real-time updates working
- ✅ Export functionality implemented

---

## Timeline Estimate

### Phase 1: Core Endpoints
- **Time:** 4-6 hours
- **Tasks:** Models, service, router, basic testing

### Phase 2: Bulk Operations
- **Time:** 3-4 hours
- **Tasks:** Bulk validation, summary, filters

### Phase 3: Enhanced Features
- **Time:** 6-8 hours
- **Tasks:** Re-validation, WebSocket, export

**Total:** 13-18 hours for complete implementation

---

## Next Steps

1. **Online Claude:** Implement Phase 1 (core endpoints)
2. **Local Claude:** Test endpoints via FastAPI docs
3. **Frontend Team:** Integrate endpoints into Contact Launchpad
4. **Online Claude:** Implement Phase 2 (bulk operations)
5. **Local Claude:** End-to-end testing
6. **Optional:** Implement Phase 3 (enhanced features)

---

**Status:** 📋 **READY FOR IMPLEMENTATION**  
**Depends On:** WO-017 ✅ Complete  
**Blocks:** Frontend Contact Launchpad integration  
**Priority:** 🟡 **HIGH**

**Created:** 2025-11-19  
**Author:** Local Claude  
**For:** Online Claude Implementation
