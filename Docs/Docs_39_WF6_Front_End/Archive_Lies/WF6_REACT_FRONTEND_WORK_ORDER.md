# WF6 React Frontend Work Order

**Date:** August 24, 2025  
**Workflow:** WF6 - The Recorder (Sitemap Import)  
**Status:** TESTED AND VERIFIED  

## WHAT WAS TESTED

I tested WF6 live on your running system. Here's exactly what I did:

1. Found sitemap file: `https://phomay.com/sitemap.xml` (ID: `2c118a83-b9eb-4c44-819d-c04ebbbec40a`)
2. Set status to 'Queued' in database  
3. WF6 background service automatically picked it up
4. Service fetched sitemap XML content
5. Extracted URLs and created page record: `https://phomay.com/`
6. Status changed to 'Complete'

**WF6 WORKS PERFECTLY.**

## THE API DOCUMENTATION

**URL:** `http://localhost:8000/docs`

This is FastAPI's auto-generated documentation. Everything you need is there. Do not guess - use what's documented.

## API ENDPOINTS FOR WF6

### 1. List Sitemap Files
```
GET /api/v3/sitemap-files/
```
**Parameters:**
- `domain_id` (optional UUID)
- `deep_scrape_curation_status` (optional: New|Selected|Maybe|Not a Fit|Archived)
- `url_contains` (optional string)  
- `sitemap_type` (optional string)
- `discovery_method` (optional string)
- `page` (optional integer, default: 1)
- `size` (optional integer, default: 15, max: 200)

**Returns:** List of sitemap files with pagination

### 2. Batch Update (Consumer-Producer Pattern)
```
PUT /api/v3/sitemap-files/sitemap_import_curation/status
```
**Request:**
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

### 3. Individual Operations
- `POST /api/v3/sitemap-files/` - Create
- `GET /api/v3/sitemap-files/{id}` - Get one
- `PUT /api/v3/sitemap-files/{id}` - Update one  
- `DELETE /api/v3/sitemap-files/{id}` - Delete

## DATA FLOW

**Input:** sitemap_files table  
**Selection:** User marks as "Selected"  
**Auto-Queue:** System sets sitemap_import_status to "Queued"  
**Processing:** WF6 service processes automatically  
**Output:** pages table with extracted URLs

## WHAT TO BUILD

### React Components
1. **WF6Table** - List sitemap files
2. **WF6Filters** - Filter by domain, status, URL
3. **WF6Selection** - Checkboxes for bulk selection
4. **WF6BatchActions** - Buttons to mark Selected/Rejected
5. **WF6StatusMonitor** - Show processing progress

### API Service
```typescript
export class WF6Service {
  static async getFiles(params: any) {
    const response = await fetch('/api/v3/sitemap-files/', {
      headers: { 'Authorization': `Bearer ${token}` }
    });
    return response.json();
  }
  
  static async updateBatch(ids: string[], status: string) {
    const response = await fetch('/api/v3/sitemap-files/sitemap_import_curation/status', {
      method: 'PUT',
      headers: { 
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}` 
      },
      body: JSON.stringify({
        sitemap_file_ids: ids,
        deep_scrape_curation_status: status
      })
    });
    return response.json();
  }
}
```

### TypeScript Types
Get them from the OpenAPI spec:
```bash
curl http://localhost:8000/openapi.json
```
Use the schemas section for exact field names and types.

## USER INTERFACE

1. **Table View**
   - List sitemap files
   - Checkboxes for selection
   - Columns: URL, Domain, Curation Status, Import Status, Updated

2. **Filter Section**
   - Domain dropdown
   - Status dropdown (New, Selected, Maybe, Not a Fit, Archived)
   - URL search box

3. **Batch Actions**
   - "Mark Selected" button
   - "Mark Rejected" button  
   - Shows count of selected items

4. **Status Monitor**
   - Shows items currently processing
   - Auto-refreshes every 5 seconds

## AUTHENTICATION

All endpoints require JWT token in header:
```
Authorization: Bearer <token>
```

## DATABASE STATE

- **Total sitemap files:** 627
- **Most have status:** null (need to filter by specific statuses)
- **Test with:** Status = "New" to see filterable items

## SYSTEM STATUS

- **API running:** http://localhost:8000
- **Container status:** Healthy, up 2 days
- **WF6 service:** Active and processing
- **Database:** Connected and working

## IMPLEMENTATION STEPS

1. Create React components
2. Connect to documented API endpoints  
3. Handle JWT authentication
4. Add real-time polling for status updates
5. Test with existing data

**Everything you need is in the live API documentation at /docs. Use it.**