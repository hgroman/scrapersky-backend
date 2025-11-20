# PRD: n8n Contact Enrichment Workflow

**Version:** 1.0  
**Date:** 2025-11-20  
**Status:** Draft - Ready for n8n Implementation  
**Related:** WO-020 (Outbound), WO-021 (Inbound)

---

## Executive Summary

Build an n8n workflow that receives contact data from ScraperSky, enriches it using external APIs (Clearbit, Hunter.io, LinkedIn, etc.), and returns the enriched data to ScraperSky's webhook endpoint.

**Input:** Contact with email address (minimum)  
**Output:** 15 enrichment fields populated with data from multiple sources  
**Success Criteria:** 70%+ enrichment success rate, <30 second processing time

---

## 1. INPUT SPECIFICATION

### What ScraperSky Sends to n8n

**Webhook Trigger:** POST request from ScraperSky  
**Endpoint:** Your n8n webhook URL (configured in ScraperSky)  
**Authentication:** Optional Bearer token (N8N_WEBHOOK_SECRET)

**Payload Structure:**
```json
{
  "contact_id": "550e8400-e29b-41d4-a716-446655440000",
  "email": "john.doe@acmecorp.com",
  "first_name": "John",
  "last_name": "Doe",
  "company": "Acme Corp",
  "phone": "+1-555-0123",
  "domain_id": "uuid-string",
  "page_id": "uuid-string"
}
```

### Guaranteed Fields (Always Present)
- ✅ `contact_id` (UUID) - **CRITICAL**: Use this to send data back
- ✅ `email` (string) - **PRIMARY KEY**: Main enrichment input

### Optional Fields (May Be Present)
- ⚠️ `first_name` (string or null)
- ⚠️ `last_name` (string or null)
- ⚠️ `company` (string or null)
- ⚠️ `phone` (string or null)
- ⚠️ `domain_id` (UUID or null)
- ⚠️ `page_id` (UUID or null)

### What You Can Rely On

**ALWAYS available:**
- Email address (required for enrichment)
- Contact ID (required to send results back)

**SOMETIMES available:**
- Name fields (use if present, enrich if missing)
- Company name (use as hint for enrichment)
- Phone (use as validation if present)

**Strategy:** Use available fields as hints/validation, but don't depend on them.

---

## 2. OUTPUT SPECIFICATION

### What n8n Must Return to ScraperSky

**Webhook Endpoint:** POST to ScraperSky's inbound webhook  
**URL:** `https://your-scrapersky-api.com/api/v3/webhooks/n8n/enrichment-complete`  
**Authentication:** Bearer token (N8N_WEBHOOK_SECRET from ScraperSky)

**Required Response Structure:**
```json
{
  "contact_id": "550e8400-e29b-41d4-a716-446655440000",
  "enrichment_id": "enrich_20251120_001234",
  "status": "complete",
  "timestamp": "2025-11-20T08:30:00Z",
  "enriched_data": {
    "phone": "+1-555-0199",
    "address": {
      "street": "123 Main Street",
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
      "name": "Acme Corporation",
      "website": "https://acmecorp.com",
      "industry": "Technology",
      "size": "50-200"
    },
    "additional_emails": [
      "j.doe@acmecorp.com",
      "johndoe@gmail.com"
    ],
    "confidence_score": 85,
    "sources": [
      "clearbit",
      "hunter.io",
      "linkedin_api"
    ]
  },
  "metadata": {
    "duration_seconds": 12.5,
    "api_calls": 3,
    "cost_estimate": 0.15
  }
}
```

### The 15 Fields Explained

#### Status Fields (5) - Managed by ScraperSky
These are set by ScraperSky based on your response. **Don't include in payload.**
- `enrichment_status` - ScraperSky sets based on your `status` field
- `enrichment_started_at` - ScraperSky sets when workflow triggered
- `enrichment_completed_at` - ScraperSky sets from your `timestamp`
- `enrichment_error` - ScraperSky sets if you return `status: "failed"`
- `last_enrichment_id` - ScraperSky sets from your `enrichment_id`

#### Data Fields (7) - YOU MUST POPULATE
These are the enrichment results you need to find:

**1. enriched_phone** (string or null)
```json
"phone": "+1-555-0199"
```
- Format: E.164 international format preferred (+1-555-0199)
- Fallback: Any format is acceptable
- Source: Clearbit, Hunter.io, LinkedIn, company website scraping
- **If not found:** Send `null`

**2. enriched_address** (object or null)
```json
"address": {
  "street": "123 Main Street",
  "city": "San Francisco",
  "state": "CA",
  "zip": "94102",
  "country": "USA"
}
```
- All fields optional within object
- Send partial data if only some fields found
- Source: Clearbit, LinkedIn, company website
- **If not found:** Send `null`

**3. enriched_social_profiles** (object or null)
```json
"social_profiles": {
  "linkedin": "https://linkedin.com/in/johndoe",
  "twitter": "https://twitter.com/johndoe",
  "facebook": "https://facebook.com/johndoe",
  "github": "https://github.com/johndoe",
  "instagram": "https://instagram.com/johndoe"
}
```
- Include any social profiles found
- Full URLs preferred
- Source: Clearbit, Hunter.io, Google search, LinkedIn API
- **If not found:** Send `null` or `{}`

**4. enriched_company** (object or null)
```json
"company": {
  "name": "Acme Corporation",
  "website": "https://acmecorp.com",
  "industry": "Technology",
  "size": "50-200"
}
```
- All fields optional within object
- Size format: "1-10", "11-50", "51-200", "201-500", "501-1000", "1000+"
- Source: Clearbit, LinkedIn, company website, Crunchbase
- **If not found:** Send `null`

**5. enriched_additional_emails** (array or null)
```json
"additional_emails": [
  "j.doe@acmecorp.com",
  "johndoe@gmail.com"
]
```
- Array of email strings
- Don't include the original email
- Source: Hunter.io, Clearbit, LinkedIn
- **If not found:** Send `null` or `[]`

**6. enrichment_confidence_score** (integer 0-100)
```json
"confidence_score": 85
```
- 0-100 scale
- Based on: number of sources, data freshness, source reliability
- Calculation suggestion:
  - 100: All fields found from 3+ reliable sources
  - 80-99: Most fields found from 2+ sources
  - 60-79: Some fields found from 1-2 sources
  - 40-59: Minimal data from 1 source
  - 0-39: Very little data found
- **Always required:** Send a number, even if 0

**7. enrichment_sources** (array)
```json
"sources": [
  "clearbit",
  "hunter.io",
  "linkedin_api",
  "google_search"
]
```
- Array of source identifiers
- Use consistent naming (lowercase, underscores)
- **Always required:** Send array, even if empty `[]`

#### Metadata Fields (3) - YOU MUST POPULATE
Track enrichment performance:

**1. enrichment_duration_seconds** (float)
```json
"duration_seconds": 12.5
```
- Total workflow execution time
- Use n8n's built-in timing
- **Always required**

**2. enrichment_api_calls** (integer)
```json
"api_calls": 3
```
- Count of external API calls made
- Helps track rate limits and costs
- **Always required**

**3. enrichment_cost_estimate** (float)
```json
"cost_estimate": 0.15
```
- Estimated cost in USD
- Sum of all API call costs
- Example: Clearbit ($0.10) + Hunter.io ($0.05) = $0.15
- **Always required:** Send 0.00 if free tier

---

## 3. STATUS VALUES

Your `status` field determines how ScraperSky handles the response:

### "complete" ✅
```json
{
  "status": "complete",
  "enriched_data": { /* all or most fields populated */ }
}
```
**Use when:** Successfully enriched contact with good data  
**ScraperSky sets:** `enrichment_status = 'complete'`  
**Required:** `enriched_data` object with at least some fields

### "partial" ⚠️
```json
{
  "status": "partial",
  "enriched_data": { /* some fields populated, many null */ }
}
```
**Use when:** Found some data but not everything  
**ScraperSky sets:** `enrichment_status = 'partial'`  
**Required:** `enriched_data` object with at least 1-2 fields

### "failed" ❌
```json
{
  "status": "failed",
  "enriched_data": null,
  "error": "Email not found in any data source"
}
```
**Use when:** Enrichment completely failed  
**ScraperSky sets:** `enrichment_status = 'failed'`, `enrichment_error = your error message`  
**Required:** `error` field with explanation

---

## 4. ENRICHMENT STRATEGY

### Recommended n8n Workflow Structure

```
1. WEBHOOK TRIGGER
   ↓
2. VALIDATE INPUT
   - Check contact_id exists
   - Check email exists and is valid
   ↓
3. PARALLEL ENRICHMENT (Run simultaneously)
   ├─→ CLEARBIT ENRICHMENT
   │   - Person API: phone, social, company
   │   - Company API: company details
   ├─→ HUNTER.IO ENRICHMENT
   │   - Email Finder: additional emails
   │   - Email Verifier: validate email
   ├─→ LINKEDIN ENRICHMENT (if available)
   │   - Profile search by email
   │   - Extract company, social, location
   └─→ GOOGLE SEARCH ENRICHMENT (fallback)
       - Search for "email + name"
       - Extract social profiles from results
   ↓
4. MERGE RESULTS
   - Combine data from all sources
   - Resolve conflicts (prefer most recent/reliable)
   - Calculate confidence score
   ↓
5. FORMAT RESPONSE
   - Build enriched_data object
   - Set status (complete/partial/failed)
   - Add metadata
   ↓
6. SEND TO SCRAPERSKY
   - POST to webhook endpoint
   - Include Bearer token
   - Handle errors
```

### Data Source Priority

**For phone numbers:**
1. Clearbit Person API
2. LinkedIn profile
3. Company website scraping
4. Hunter.io

**For social profiles:**
1. Clearbit Person API
2. LinkedIn API
3. Google search results
4. Hunter.io

**For company info:**
1. Clearbit Company API
2. LinkedIn company page
3. Crunchbase
4. Company website scraping

**For additional emails:**
1. Hunter.io Email Finder
2. Clearbit
3. LinkedIn

**For address:**
1. Clearbit Person API
2. LinkedIn profile
3. Company website

### Confidence Score Calculation

```javascript
// Pseudocode for n8n
let score = 0;
let sourceCount = enrichment_sources.length;

// Base score from number of sources
if (sourceCount >= 3) score += 40;
else if (sourceCount >= 2) score += 25;
else if (sourceCount >= 1) score += 10;

// Points for each field found
if (phone) score += 10;
if (address && address.city) score += 10;
if (social_profiles && Object.keys(social_profiles).length > 0) score += 15;
if (company && company.name) score += 10;
if (additional_emails && additional_emails.length > 0) score += 10;

// Bonus for high-quality sources
if (sources.includes('clearbit')) score += 5;
if (sources.includes('linkedin_api')) score += 5;

// Cap at 100
score = Math.min(score, 100);
```

---

## 5. ERROR HANDLING

### n8n Workflow Error Scenarios

**Scenario 1: Invalid Email**
```json
{
  "contact_id": "uuid",
  "enrichment_id": "enrich_xxx",
  "status": "failed",
  "timestamp": "2025-11-20T08:30:00Z",
  "enriched_data": null,
  "error": "Invalid email format",
  "metadata": {
    "duration_seconds": 0.5,
    "api_calls": 0,
    "cost_estimate": 0.00
  }
}
```

**Scenario 2: API Rate Limit**
```json
{
  "status": "failed",
  "error": "Clearbit API rate limit exceeded. Retry in 60 seconds."
}
```
**Action:** ScraperSky will retry with exponential backoff

**Scenario 3: No Data Found**
```json
{
  "status": "partial",
  "enriched_data": {
    "phone": null,
    "address": null,
    "social_profiles": null,
    "company": null,
    "additional_emails": null,
    "confidence_score": 0,
    "sources": []
  }
}
```
**Action:** ScraperSky marks as partial, user sees "no data found"

### Retry Logic (ScraperSky Side)

If your n8n workflow fails to respond or returns an error:
- Attempt 1 fails → retry in 5 minutes
- Attempt 2 fails → retry in 10 minutes
- Attempt 3 fails → retry in 20 minutes
- After 3 attempts → mark as permanently failed

**Your responsibility:** Return a response within 30 seconds or ScraperSky will timeout

---

## 6. TESTING & VALIDATION

### Test Cases

**Test 1: Full Enrichment Success**
```
Input: john.doe@acmecorp.com
Expected: All 7 data fields populated, confidence 80+
```

**Test 2: Partial Enrichment**
```
Input: obscure.person@tiny-company.com
Expected: 2-3 fields populated, confidence 40-60
```

**Test 3: Complete Failure**
```
Input: fake@nonexistent-domain-12345.com
Expected: status="failed", error message
```

**Test 4: Invalid Input**
```
Input: not-an-email
Expected: status="failed", error="Invalid email format"
```

### Validation Checklist

Before sending response to ScraperSky:
- [ ] `contact_id` matches input
- [ ] `enrichment_id` is unique
- [ ] `status` is one of: complete, partial, failed
- [ ] `timestamp` is ISO 8601 format
- [ ] `enriched_data` structure matches spec
- [ ] `confidence_score` is 0-100
- [ ] `sources` is an array
- [ ] `metadata` has all 3 fields
- [ ] Response size < 100KB

---

## 7. IMPLEMENTATION CHECKLIST

### n8n Nodes You'll Need

- [ ] **Webhook** - Receive contact from ScraperSky
- [ ] **HTTP Request** (multiple) - Call Clearbit, Hunter.io, etc.
- [ ] **Code** - Merge results, calculate confidence
- [ ] **HTTP Request** - Send results back to ScraperSky
- [ ] **Error Trigger** - Handle workflow failures

### Environment Variables in n8n

```
SCRAPERSKY_WEBHOOK_URL=https://your-api.com/api/v3/webhooks/n8n/enrichment-complete
SCRAPERSKY_WEBHOOK_SECRET=your-bearer-token
CLEARBIT_API_KEY=your-clearbit-key
HUNTER_IO_API_KEY=your-hunter-key
LINKEDIN_API_KEY=your-linkedin-key (if available)
```

### API Keys You'll Need

1. **Clearbit** (recommended)
   - Person Enrichment API
   - Company Enrichment API
   - Cost: ~$0.10 per lookup

2. **Hunter.io** (recommended)
   - Email Finder
   - Email Verifier
   - Cost: ~$0.05 per lookup

3. **LinkedIn API** (optional, requires partnership)
   - Profile API
   - Cost: Varies

4. **Alternatives:**
   - Pipl
   - FullContact
   - RocketReach
   - Apollo.io

---

## 8. SUCCESS METRICS

### Target KPIs

- **Enrichment Success Rate:** >70% (complete or partial)
- **Average Processing Time:** <30 seconds
- **Average Confidence Score:** >60
- **Cost Per Enrichment:** <$0.25
- **API Error Rate:** <5%

### Monitoring

Track in n8n:
- Total enrichments processed
- Success/partial/failed breakdown
- Average processing time
- Total API costs
- Error types and frequencies

---

## 9. EXAMPLE SCENARIOS

### Scenario A: Corporate Email (Best Case)

**Input:**
```json
{
  "contact_id": "uuid-1",
  "email": "sarah.johnson@salesforce.com"
}
```

**Expected Output:**
```json
{
  "status": "complete",
  "enriched_data": {
    "phone": "+1-415-555-0123",
    "address": {
      "city": "San Francisco",
      "state": "CA",
      "country": "USA"
    },
    "social_profiles": {
      "linkedin": "https://linkedin.com/in/sarahjohnson",
      "twitter": "https://twitter.com/sjohnson"
    },
    "company": {
      "name": "Salesforce",
      "website": "https://salesforce.com",
      "industry": "Software",
      "size": "10000+"
    },
    "additional_emails": ["s.johnson@salesforce.com"],
    "confidence_score": 95,
    "sources": ["clearbit", "hunter.io", "linkedin_api"]
  },
  "metadata": {
    "duration_seconds": 8.2,
    "api_calls": 3,
    "cost_estimate": 0.20
  }
}
```

### Scenario B: Personal Email (Moderate Case)

**Input:**
```json
{
  "contact_id": "uuid-2",
  "email": "johndoe123@gmail.com",
  "first_name": "John",
  "last_name": "Doe"
}
```

**Expected Output:**
```json
{
  "status": "partial",
  "enriched_data": {
    "phone": null,
    "address": null,
    "social_profiles": {
      "linkedin": "https://linkedin.com/in/john-doe-123"
    },
    "company": {
      "name": "Freelance Consultant"
    },
    "additional_emails": [],
    "confidence_score": 45,
    "sources": ["linkedin_api", "google_search"]
  },
  "metadata": {
    "duration_seconds": 15.3,
    "api_calls": 2,
    "cost_estimate": 0.05
  }
}
```

### Scenario C: Invalid Email (Failure Case)

**Input:**
```json
{
  "contact_id": "uuid-3",
  "email": "fake@nonexistent-domain-xyz.com"
}
```

**Expected Output:**
```json
{
  "status": "failed",
  "enriched_data": null,
  "error": "Email domain does not exist",
  "metadata": {
    "duration_seconds": 2.1,
    "api_calls": 1,
    "cost_estimate": 0.00
  }
}
```

---

## 10. NEXT STEPS

1. **Review this PRD** with your team
2. **Set up n8n workspace** and install required nodes
3. **Obtain API keys** for Clearbit, Hunter.io, etc.
4. **Build workflow** following the structure in Section 4
5. **Test with examples** from Section 9
6. **Deploy to production** and monitor metrics from Section 8

---

**Questions? Issues?**  
Refer to code headers:
- Outbound: `src/services/crm/n8n_sync_service.py`
- Inbound: `src/routers/v3/n8n_webhook_router.py`
- Enrichment: `src/services/crm/n8n_enrichment_service.py`

**Last Updated:** 2025-11-20  
**Version:** 1.0
