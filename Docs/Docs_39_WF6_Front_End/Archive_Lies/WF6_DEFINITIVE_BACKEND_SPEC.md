# WF6 DEFINITIVE BACKEND SPECIFICATION

**AUTHORITATIVE DOCUMENT - FINAL WORD ON WF6 API**

---

## API BASE URL

**PRODUCTION:** `https://scrapersky-backend.onrender.com`

---

## TENANT ISOLATION STATUS

**NO TENANT ISOLATION EXISTS IN THIS SYSTEM**
- Do NOT send tenant_id in any requests
- Do NOT include tenant_id in query parameters
- System operates without tenant context

---

## VERIFIED API ENDPOINTS

### 1. List Sitemap Files
```
GET /api/v3/sitemap-files/
```

**Query Parameters:**
- `domain_id` (optional UUID)
- `deep_scrape_curation_status` (optional: New|Selected|Maybe|Not a Fit|Archived)
- `url_contains` (optional string)
- `sitemap_type` (optional string)
- `discovery_method` (optional string)
- `page` (optional integer, default: 1)
- `size` (optional integer, default: 15, max: 200)

**Headers:**
```
Authorization: Bearer <jwt_token>
Content-Type: application/json
```

### 2. Batch Update Status
```
PUT /api/v3/sitemap-files/sitemap_import_curation/status
```

**Request Body:**
```json
{
  "sitemap_file_ids": ["uuid1", "uuid2"],
  "deep_scrape_curation_status": "Selected"
}
```

**Response:**
```json
{
  "updated_count": 2,
  "queued_count": 2
}
```

**Headers:**
```
Authorization: Bearer <jwt_token>
Content-Type: application/json
```

---

## DATA SCHEMA

### SitemapFile Object
```json
{
  "id": "uuid",
  "url": "https://example.com/sitemap.xml",
  "domain_id": "uuid",
  "deep_scrape_curation_status": "New|Selected|Maybe|Not a Fit|Archived",
  "sitemap_import_status": "Queued|Processing|Complete|Error",
  "sitemap_type": "string",
  "discovery_method": "string",
  "created_at": "ISO datetime",
  "updated_at": "ISO datetime",
  "domain": {
    "domain_name": "string",
    "id": "uuid"
  }
}
```

### Paginated Response
```json
{
  "items": [SitemapFile],
  "page": 1,
  "pages": 10,
  "total": 627
}
```

---

## STATUS ENUMS

**deep_scrape_curation_status:**
- "New"
- "Selected" 
- "Maybe"
- "Not a Fit"
- "Archived"

**sitemap_import_status:**
- "Queued"
- "Processing" 
- "Complete"
- "Error"

---

## AUTHENTICATION

All endpoints require JWT token in header:
```
Authorization: Bearer <token>
```

Get token from session: `session.access_token`

---

## ERROR RESPONSES

- **401**: Invalid/missing JWT token
- **404**: Sitemap files not found
- **422**: Invalid request data
- **500**: Server error

---

## WORKFLOW BEHAVIOR

1. Frontend marks records as "Selected"
2. Backend automatically sets sitemap_import_status to "Queued"
3. WF6 service processes queued items (5-15 seconds typically)
4. Status changes: Queued → Processing → Complete
5. Frontend polls every 5 seconds when items are Queued/Processing

---

## LIVE TESTED DATA

- **Total sitemap files:** 627
- **Test record used:** `https://phomay.com/sitemap.xml`
- **Processing time:** 14 seconds average
- **Output:** Creates records in pages table

---

**THIS IS THE FINAL SPECIFICATION - NO FURTHER CHANGES**