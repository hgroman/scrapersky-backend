# WO-021: n8n Enrichment Return Data Pipeline

**Work Order:** WO-021
**Created:** 2025-11-19
**Status:** 📋 Planning Phase (Ready for Implementation)
**Priority:** 🔥 HIGH
**Depends On:** WO-020 (n8n Webhook Integration - Complete ✅)
**Estimated Effort:** 2-3 hours

---

## Executive Summary

WO-020 successfully sends contact data TO n8n for enrichment, but there's no way to receive enriched data BACK. This work order implements the return data pipeline to complete the two-way integration.

**Current State:**
- ✅ ScraperSky sends contacts to n8n webhook (WO-020)
- ✅ n8n receives data and can trigger enrichment workflows
- ✅ Database tracks webhook send status
- ❌ **Missing:** Endpoint to receive enriched data back from n8n
- ❌ **Missing:** Database fields to store enrichment results
- ❌ **Missing:** Enrichment status tracking (separate from webhook send)

**After WO-021:**
- ✅ n8n can POST enriched data back to ScraperSky
- ✅ ScraperSky validates and stores enrichment results
- ✅ Track enrichment progress separately from webhook send
- ✅ Frontend can display enriched contact data

---

## Objective

Create a secure endpoint that receives enriched contact data from n8n workflows and updates contact records with the enrichment results.

**Key Requirements:**
1. Accept POST requests from n8n with enriched contact data
2. Validate payload structure and authentication
3. Update contact records with enrichment results
4. Track enrichment status (pending/complete/failed)
5. Handle partial enrichments gracefully
6. Prevent duplicate processing (idempotency)

---

## Technical Design

### 1. API Endpoint

**Endpoint:**
```http
POST /api/v3/webhooks/n8n/enrichment-complete
Content-Type: application/json
Authorization: Bearer {N8N_WEBHOOK_SECRET}
```

**Request Payload:**
```json
{
  "contact_id": "uuid",
  "enrichment_id": "unique-enrichment-run-id",  // For idempotency
  "status": "complete",  // or "partial" or "failed"
  "timestamp": "2025-11-19T10:30:00Z",

  "enriched_data": {
    "phone": "+1-555-123-4567",
    "address": {
      "street": "123 Main St",
      "city": "San Francisco",
      "state": "CA",
      "zip": "94102",
      "country": "USA"
    },
    "social_profiles": {
      "linkedin": "https://linkedin.com/in/johndoe",
      "twitter": "https://twitter.com/johndoe",
      "facebook": "https://facebook.com/johndoe"
    },
    "company": {
      "name": "Acme Corp",
      "website": "https://acme.com",
      "industry": "Technology",
      "size": "51-200"
    },
    "additional_emails": [
      "john.doe@acme.com",
      "jdoe@acme.com"
    ],
    "confidence_score": 85,  // 0-100 quality metric
    "sources": [
      "linkedin_api",
      "clearbit",
      "fullcontact"
    ]
  },

  "metadata": {
    "enrichment_duration_seconds": 12.5,
    "api_calls_made": 3,
    "cost_estimate": 0.15
  }
}
```

**Response (Success):**
```json
{
  "success": true,
  "contact_id": "uuid",
  "enrichment_id": "unique-enrichment-run-id",
  "message": "Enrichment data saved successfully",
  "updated_fields": [
    "enriched_phone",
    "enriched_address",
    "enriched_social_profiles",
    "enriched_company"
  ]
}
```

**Response (Error):**
```json
{
  "success": false,
  "error": "Contact not found",
  "contact_id": "uuid",
  "enrichment_id": "unique-enrichment-run-id"
}
```

### 2. Database Schema Changes

**Add New Fields to Contact Model:**

```python
# Enrichment Status Tracking
enrichment_status: Mapped[Optional[str]]  # "pending", "complete", "partial", "failed"
enrichment_started_at: Mapped[Optional[datetime]]
enrichment_completed_at: Mapped[Optional[datetime]]
enrichment_error: Mapped[Optional[str]]  # Error message if failed
last_enrichment_id: Mapped[Optional[str]]  # For idempotency

# Enriched Data Fields
enriched_phone: Mapped[Optional[str]]
enriched_address: Mapped[Optional[dict]]  # JSON field
enriched_social_profiles: Mapped[Optional[dict]]  # JSON field
enriched_company: Mapped[Optional[dict]]  # JSON field
enriched_additional_emails: Mapped[Optional[list]]  # JSON array
enrichment_confidence_score: Mapped[Optional[int]]  # 0-100
enrichment_sources: Mapped[Optional[list]]  # JSON array

# Enrichment Metadata
enrichment_duration_seconds: Mapped[Optional[float]]
enrichment_api_calls: Mapped[Optional[int]]
enrichment_cost_estimate: Mapped[Optional[float]]
```

**Why JSON Fields:**
- Address structure can vary (street, city, state, country)
- Social profiles can have variable platforms
- Company info can have different fields
- Flexible schema for future enrichment sources

### 3. Pydantic Schemas

**File:** `src/schemas/n8n_enrichment_schemas.py`

```python
from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime

class AddressData(BaseModel):
    street: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    zip: Optional[str] = None
    country: Optional[str] = None

class SocialProfiles(BaseModel):
    linkedin: Optional[str] = None
    twitter: Optional[str] = None
    facebook: Optional[str] = None
    instagram: Optional[str] = None
    github: Optional[str] = None

class CompanyData(BaseModel):
    name: Optional[str] = None
    website: Optional[str] = None
    industry: Optional[str] = None
    size: Optional[str] = None
    description: Optional[str] = None

class EnrichedData(BaseModel):
    phone: Optional[str] = None
    address: Optional[AddressData] = None
    social_profiles: Optional[SocialProfiles] = None
    company: Optional[CompanyData] = None
    additional_emails: Optional[List[str]] = None
    confidence_score: Optional[int] = Field(None, ge=0, le=100)
    sources: Optional[List[str]] = None

class EnrichmentMetadata(BaseModel):
    enrichment_duration_seconds: Optional[float] = None
    api_calls_made: Optional[int] = None
    cost_estimate: Optional[float] = None

class EnrichmentCompleteRequest(BaseModel):
    contact_id: str
    enrichment_id: str  # Unique per enrichment run
    status: str = Field(..., regex="^(complete|partial|failed)$")
    timestamp: datetime
    enriched_data: Optional[EnrichedData] = None
    metadata: Optional[EnrichmentMetadata] = None

class EnrichmentCompleteResponse(BaseModel):
    success: bool
    contact_id: str
    enrichment_id: str
    message: str
    updated_fields: Optional[List[str]] = None
```

### 4. Service Layer

**File:** `src/services/crm/n8n_enrichment_service.py`

```python
class N8nEnrichmentService:
    """Service for processing enriched data from n8n"""

    async def process_enrichment(
        self,
        payload: EnrichmentCompleteRequest,
        session: AsyncSession
    ) -> Dict:
        """
        Process enriched data from n8n and update contact.

        Steps:
        1. Validate contact exists
        2. Check idempotency (already processed this enrichment_id?)
        3. Update enriched data fields
        4. Update enrichment status
        5. Return success response
        """

    async def _validate_contact(self, contact_id: UUID, session: AsyncSession) -> Contact:
        """Fetch and validate contact exists"""

    async def _check_idempotency(self, contact: Contact, enrichment_id: str) -> bool:
        """Check if this enrichment_id was already processed"""

    async def _update_enriched_data(
        self,
        contact: Contact,
        enriched_data: EnrichedData,
        session: AsyncSession
    ) -> List[str]:
        """Update contact with enriched data, return updated field names"""
```

### 5. Router

**File:** `src/routers/v3/n8n_webhook_router.py`

```python
router = APIRouter(
    prefix="/api/v3/webhooks/n8n",
    tags=["n8n Webhooks"],
)

@router.post("/enrichment-complete", response_model=EnrichmentCompleteResponse)
async def receive_enrichment_data(
    request: EnrichmentCompleteRequest,
    session: AsyncSession = Depends(get_db_session),
    # Authentication: Bearer token from n8n
    authorization: str = Header(None)
):
    """
    Receive enriched contact data from n8n workflows.

    **Authentication:** Requires Bearer token matching N8N_WEBHOOK_SECRET.

    **Idempotency:** Safe to retry - same enrichment_id won't duplicate data.

    **Partial Enrichments:** status="partial" saves available data, marks as partial.

    **Failed Enrichments:** status="failed" marks contact, logs error.
    """
```

---

## Implementation Plan

### Phase 1: Database Migration (30 min)

**Create Migration File:**
```
supabase/migrations/20251119_add_enrichment_fields.sql
```

**Add Fields:**
- Enrichment status tracking fields
- Enriched data JSON fields
- Enrichment metadata fields

**Test Migration:**
- Apply to local database
- Verify fields exist
- Test JSON field types

### Phase 2: Pydantic Schemas (20 min)

**File:** `src/schemas/n8n_enrichment_schemas.py`

**Create:**
- `AddressData`, `SocialProfiles`, `CompanyData`
- `EnrichedData`, `EnrichmentMetadata`
- `EnrichmentCompleteRequest`, `EnrichmentCompleteResponse`

**Validation:**
- Ensure all optional fields allow None
- Validate confidence_score range (0-100)
- Validate status enum

### Phase 3: Service Layer (45 min)

**File:** `src/services/crm/n8n_enrichment_service.py`

**Implement:**
- Contact validation
- Idempotency check
- Enriched data update logic
- Status tracking
- Error handling

**Key Logic:**
```python
# Idempotency check
if contact.last_enrichment_id == enrichment_id:
    logger.info(f"Enrichment {enrichment_id} already processed - skipping")
    return {"success": True, "message": "Already processed"}

# Update enriched data
contact.enriched_phone = enriched_data.phone
contact.enriched_address = enriched_data.address.dict() if enriched_data.address else None
# ... etc

# Update status
contact.enrichment_status = payload.status
contact.enrichment_completed_at = datetime.utcnow()
contact.last_enrichment_id = enrichment_id
```

### Phase 4: Router (30 min)

**File:** `src/routers/v3/n8n_webhook_router.py`

**Implement:**
- POST /enrichment-complete endpoint
- Bearer token authentication
- Call service layer
- Return standardized responses

**Authentication:**
```python
def verify_n8n_webhook_secret(authorization: str = Header(None)):
    if not authorization:
        raise HTTPException(401, "Missing Authorization header")

    if not authorization.startswith("Bearer "):
        raise HTTPException(401, "Invalid Authorization format")

    token = authorization.replace("Bearer ", "")
    if token != settings.N8N_WEBHOOK_SECRET:
        raise HTTPException(401, "Invalid webhook secret")
```

### Phase 5: Router Registration (5 min)

**File:** `src/main.py`

**Add:**
```python
from src.routers.v3.n8n_webhook_router import router as n8n_webhook_router

app.include_router(n8n_webhook_router)  # WO-021: n8n enrichment return
```

### Phase 6: Environment Variables (10 min)

**Update `.env.example`:**
```bash
# n8n Webhook Authentication (WO-021)
N8N_WEBHOOK_SECRET=your-secure-random-token-here  # Required for enrichment returns
```

**Update `src/config/settings.py`:**
```python
# n8n Webhook Security (WO-021)
N8N_WEBHOOK_SECRET: str = Field(..., description="Bearer token for n8n webhook authentication")
```

---

## Testing Strategy

### Test 1: Manual cURL Test (10 min)

**Step 1: Create test contact**
```sql
INSERT INTO contacts (email, name, n8n_sync_status, enrichment_status)
VALUES ('enrichment.test@example.com', 'Enrichment Test', 'Complete', 'pending')
RETURNING id;
```

**Step 2: Send enrichment data via cURL**
```bash
curl -X POST http://localhost:8000/api/v3/webhooks/n8n/enrichment-complete \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer your-webhook-secret" \
  -d '{
    "contact_id": "uuid-from-step-1",
    "enrichment_id": "test-enrichment-001",
    "status": "complete",
    "timestamp": "2025-11-19T10:00:00Z",
    "enriched_data": {
      "phone": "+1-555-123-4567",
      "address": {
        "city": "San Francisco",
        "state": "CA"
      },
      "confidence_score": 85
    }
  }'
```

**Expected Response:**
```json
{
  "success": true,
  "contact_id": "uuid",
  "enrichment_id": "test-enrichment-001",
  "message": "Enrichment data saved successfully",
  "updated_fields": ["enriched_phone", "enriched_address"]
}
```

**Step 3: Verify database**
```sql
SELECT
    email,
    enrichment_status,
    enriched_phone,
    enriched_address,
    enrichment_confidence_score,
    last_enrichment_id
FROM contacts
WHERE id = 'uuid-from-step-1';
```

### Test 2: Idempotency Test (5 min)

**Send same enrichment_id twice:**
```bash
# First request - should save data
curl ... (same as Test 1)

# Second request - should skip (idempotent)
curl ... (same as Test 1)
```

**Expected:** Second request returns success but doesn't duplicate data.

### Test 3: n8n Integration Test (15 min)

**Configure n8n workflow:**
1. Add "HTTP Request" node at end of enrichment workflow
2. Set method: POST
3. Set URL: `http://scrapersky:8000/api/v3/webhooks/n8n/enrichment-complete`
4. Set headers: `Authorization: Bearer {webhook_secret}`
5. Set body: JSON with enriched data

**Trigger workflow:**
- Send test contact to n8n (via WO-020)
- Watch n8n execute enrichment
- Verify n8n POSTs enrichment results back
- Verify ScraperSky receives and saves data

### Test 4: Authentication Test (5 min)

**Test invalid token:**
```bash
curl -X POST ... -H "Authorization: Bearer invalid-token" -d '{...}'
```

**Expected:** 401 Unauthorized

**Test missing token:**
```bash
curl -X POST ... -d '{...}'  # No Authorization header
```

**Expected:** 401 Unauthorized

### Test 5: Error Handling Test (10 min)

**Invalid contact_id:**
```bash
curl ... -d '{"contact_id": "00000000-0000-0000-0000-000000000000", ...}'
```

**Expected:** 404 Contact not found

**Malformed payload:**
```bash
curl ... -d '{"invalid": "payload"}'
```

**Expected:** 422 Validation Error

---

## Security Considerations

### 1. Authentication

**Requirement:** All requests must include valid Bearer token.

**Implementation:**
```python
if authorization != f"Bearer {settings.N8N_WEBHOOK_SECRET}":
    raise HTTPException(401, "Invalid webhook secret")
```

**Best Practice:** Use long random token (32+ characters).

### 2. Idempotency

**Requirement:** Prevent duplicate processing of same enrichment.

**Implementation:**
```python
if contact.last_enrichment_id == enrichment_id:
    return {"success": True, "message": "Already processed"}
```

**Why:** n8n might retry failed HTTP requests.

### 3. Input Validation

**Requirement:** Validate all incoming data.

**Implementation:** Pydantic schemas auto-validate:
- contact_id is valid UUID
- status is one of: complete/partial/failed
- confidence_score is 0-100
- timestamp is valid datetime

### 4. Rate Limiting (Future)

**Consideration:** Add rate limiting to prevent abuse.

**Recommendation:** 100 requests per minute per IP.

---

## Frontend Integration

### New API for Frontend

**Get enriched contact data:**
```http
GET /api/v3/contacts/{contact_id}
```

**Response includes enrichment fields:**
```json
{
  "id": "uuid",
  "email": "user@example.com",
  "name": "John Doe",

  // New enrichment fields
  "enrichment_status": "complete",
  "enriched_phone": "+1-555-123-4567",
  "enriched_address": {
    "city": "San Francisco",
    "state": "CA"
  },
  "enriched_social_profiles": {
    "linkedin": "https://linkedin.com/in/johndoe"
  },
  "enrichment_confidence_score": 85
}
```

### UI Display

**Contact Detail View:**
- Show enriched data in expandable section
- Display confidence score as badge
- Show enrichment timestamp
- Link to social profiles

**Contact Table:**
- Add "Enrichment Status" column
- Badges: ⏳ Pending, ✅ Complete, ⚠️ Partial, ❌ Failed
- Tooltip shows confidence score

---

## Migration Path

### Database Migration

**File:** `supabase/migrations/20251119_add_enrichment_fields.sql`

```sql
-- Add enrichment tracking fields
ALTER TABLE contacts
ADD COLUMN IF NOT EXISTS enrichment_status VARCHAR(20),
ADD COLUMN IF NOT EXISTS enrichment_started_at TIMESTAMP WITH TIME ZONE,
ADD COLUMN IF NOT EXISTS enrichment_completed_at TIMESTAMP WITH TIME ZONE,
ADD COLUMN IF NOT EXISTS enrichment_error TEXT,
ADD COLUMN IF NOT EXISTS last_enrichment_id VARCHAR(255);

-- Add enriched data fields (JSON)
ALTER TABLE contacts
ADD COLUMN IF NOT EXISTS enriched_phone VARCHAR(50),
ADD COLUMN IF NOT EXISTS enriched_address JSONB,
ADD COLUMN IF NOT EXISTS enriched_social_profiles JSONB,
ADD COLUMN IF NOT EXISTS enriched_company JSONB,
ADD COLUMN IF NOT EXISTS enriched_additional_emails JSONB,
ADD COLUMN IF NOT EXISTS enrichment_confidence_score INTEGER,
ADD COLUMN IF NOT EXISTS enrichment_sources JSONB;

-- Add enrichment metadata fields
ALTER TABLE contacts
ADD COLUMN IF NOT EXISTS enrichment_duration_seconds FLOAT,
ADD COLUMN IF NOT EXISTS enrichment_api_calls INTEGER,
ADD COLUMN IF NOT EXISTS enrichment_cost_estimate FLOAT;

-- Add indexes for common queries
CREATE INDEX IF NOT EXISTS idx_contacts_enrichment_status
ON contacts(enrichment_status);

CREATE INDEX IF NOT EXISTS idx_contacts_last_enrichment_id
ON contacts(last_enrichment_id);

-- Add check constraint for enrichment_status
ALTER TABLE contacts
ADD CONSTRAINT chk_enrichment_status
CHECK (enrichment_status IN ('pending', 'complete', 'partial', 'failed') OR enrichment_status IS NULL);

-- Add check constraint for confidence_score
ALTER TABLE contacts
ADD CONSTRAINT chk_enrichment_confidence_score
CHECK (enrichment_confidence_score >= 0 AND enrichment_confidence_score <= 100 OR enrichment_confidence_score IS NULL);
```

**Apply Migration:**
```bash
# Via Supabase MCP (Local Claude)
# Or manually via Supabase Dashboard
```

---

## Success Criteria

### Implementation Complete ✅

- [ ] Database migration applied successfully
- [ ] Pydantic schemas defined with validation
- [ ] Service layer processes enrichment data
- [ ] Router endpoint accepts POST requests
- [ ] Authentication validates Bearer token
- [ ] Idempotency prevents duplicate processing
- [ ] Error handling for all edge cases
- [ ] Environment variables documented
- [ ] Router registered in main.py

### Testing Complete ✅

- [ ] Manual cURL test passes
- [ ] Idempotency test passes (duplicate enrichment_id ignored)
- [ ] n8n integration test passes (end-to-end)
- [ ] Authentication test passes (invalid token rejected)
- [ ] Error handling tests pass (404, 422, 401)
- [ ] Database correctly stores enriched data
- [ ] JSON fields properly formatted

### Production Ready ✅

- [ ] Code follows established patterns
- [ ] Comprehensive error handling
- [ ] Security via Bearer token authentication
- [ ] Documentation complete
- [ ] Test plan validated

---

## Known Limitations

### What This Implementation Does NOT Include:

1. **Re-enrichment Logic** - No automatic re-enrichment of stale data
2. **Enrichment Versioning** - No tracking of multiple enrichment attempts
3. **Partial Update Strategy** - Partial enrichments might overwrite good data with nulls
4. **Data Quality Validation** - No validation of enriched data quality (e.g., phone format)
5. **Enrichment Source Prioritization** - If multiple sources conflict, last one wins

---

## Future Enhancements (WO-022, WO-023)

### WO-022: Enhanced Enrichment Schema

**Add:**
- Enrichment versioning (track multiple attempts)
- Data quality scores per field
- Source prioritization rules
- Automatic re-enrichment scheduling

### WO-023: Enrichment Analytics

**Add:**
- Enrichment success rate dashboard
- Cost tracking and budgeting
- Data quality reports
- Source performance comparison

---

## Dependencies

**Requires:**
- ✅ WO-020 (n8n webhook send) - Complete
- ✅ Contact model exists - Complete
- ✅ AsyncSession pattern - Complete
- ✅ Pydantic schemas pattern - Complete

**Blocks:**
- 📋 WO-022 (Enhanced enrichment schema)
- 📋 Frontend enrichment display (WO-019 extension)

---

## Timeline Estimate

| Phase | Task | Time |
|-------|------|------|
| Phase 1 | Database migration | 30 min |
| Phase 2 | Pydantic schemas | 20 min |
| Phase 3 | Service layer | 45 min |
| Phase 4 | Router | 30 min |
| Phase 5 | Router registration | 5 min |
| Phase 6 | Environment variables | 10 min |
| Testing | All test scenarios | 45 min |
| **TOTAL** | | **3 hours** |

---

## n8n Workflow Configuration

### Enrichment Workflow Structure

**Nodes in n8n:**

1. **Webhook Trigger** (from WO-020)
   - Receives contact data from ScraperSky

2. **Enrichment Nodes** (your choice)
   - Clearbit lookup
   - LinkedIn API
   - FullContact API
   - Custom scraping

3. **Data Aggregation**
   - Combine results from multiple sources
   - Calculate confidence score
   - Format address consistently

4. **HTTP Request Node** (NEW - for WO-021)
   - Method: POST
   - URL: `http://scrapersky:8000/api/v3/webhooks/n8n/enrichment-complete`
   - Headers: `Authorization: Bearer ${N8N_WEBHOOK_SECRET}`
   - Body: JSON (use template from this doc)

5. **Error Handling**
   - On enrichment failure, send status="failed"
   - On partial success, send status="partial"
   - Always send something back (don't leave hanging)

---

## Document Control

**Version:** 1.0 (Draft)
**Status:** Planning Phase - Ready for Implementation
**Dependencies:** WO-020 (Complete ✅)
**Next Implementer:** Online Claude or Local Claude
**Priority:** HIGH (completes two-way n8n integration)

---

**Created:** 2025-11-19
**Author:** Online Claude
**For:** Next Implementation Session

---

**END OF WORK ORDER**
