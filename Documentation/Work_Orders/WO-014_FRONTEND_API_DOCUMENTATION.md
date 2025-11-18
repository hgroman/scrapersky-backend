# WO-015: Frontend API Documentation - Direct Submission & CSV Import

**Date:** November 17, 2025
**Status:** Ready for Frontend Integration
**Backend Endpoints:** 6 new endpoints (3 direct-submit, 3 CSV import)
**Branch:** `claude/read-context-docs-01E8GWdNj2rJUHkN231xBFus`
**Commits:** 9fce378 (direct-submit), 630949e (CSV import)

---

## Overview

The backend now supports **direct submission** of domains, pages, and sitemaps via both JSON API and CSV file upload. This allows users to bypass the Google Maps workflow and submit data directly for processing.

**Two submission methods:**
1. **Direct Submit (JSON)** - Submit 1-100 items via JSON request body
2. **CSV Import** - Upload CSV file with up to 1000 items

---

## API Endpoints

### 1. Domains - Direct Submit (JSON)

**Endpoint:** `POST /api/v3/domains/direct-submit`

**Authentication:** Required (Bearer token)

**Request Body:**
```json
{
  "domains": [
    "example.com",
    "www.testsite.org",
    "https://another-site.com/path"
  ],
  "auto_queue": false
}
```

**Request Schema:**
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `domains` | array[string] | Yes | 1-100 domain names or URLs |
| `auto_queue` | boolean | No | If true, sets status to Selected+Queued for immediate processing. Default: false |

**Domain Normalization:**
- Removes protocol (`https://`, `http://`)
- Removes `www.` prefix
- Removes paths
- Converts to lowercase
- Example: `https://WWW.Example.COM/path` → `example.com`

**Response (200 OK):**
```json
{
  "submitted_count": 3,
  "domain_ids": [
    "123e4567-e89b-12d3-a456-426614174000",
    "123e4567-e89b-12d3-a456-426614174001",
    "123e4567-e89b-12d3-a456-426614174002"
  ],
  "auto_queued": false,
  "normalized_domains": [
    "example.com",
    "testsite.org",
    "another-site.com"
  ]
}
```

**Error Responses:**
- `401 Unauthorized` - Missing or invalid JWT token
- `409 Conflict` - Domain already exists in database
- `422 Unprocessable Entity` - Validation error (empty list, invalid format, exceeds 100)

**Example Error (409):**
```json
{
  "detail": "Domain already exists: example.com (ID: 123e4567-e89b-12d3-a456-426614174000)"
}
```

---

### 2. Pages - Direct Submit (JSON)

**Endpoint:** `POST /api/v3/pages/direct-submit`

**Authentication:** Required (Bearer token)

**Request Body:**
```json
{
  "urls": [
    "https://example.com/contact",
    "https://example.com/about",
    "https://testsite.org/services"
  ],
  "auto_queue": false,
  "priority_level": 5
}
```

**Request Schema:**
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `urls` | array[HttpUrl] | Yes | 1-100 page URLs |
| `auto_queue` | boolean | No | If true, sets status to Selected+Queued for immediate scraping. Default: false |
| `priority_level` | integer | No | 1-10 (1=highest, 10=lowest). Default: 5 |

**URL Validation:**
- Must be valid HTTP/HTTPS URL
- Pydantic HttpUrl validation

**Auto-Domain Creation:**
- Extracts domain from URL
- Creates domain record if doesn't exist
- Links page to domain automatically

**Response (200 OK):**
```json
{
  "submitted_count": 3,
  "page_ids": [
    "223e4567-e89b-12d3-a456-426614174000",
    "223e4567-e89b-12d3-a456-426614174001",
    "223e4567-e89b-12d3-a456-426614174002"
  ],
  "auto_queued": false
}
```

**Error Responses:**
- `401 Unauthorized` - Missing or invalid JWT token
- `409 Conflict` - Page URL already exists in database
- `422 Unprocessable Entity` - Validation error (invalid URL, empty list, exceeds 100)

---

### 3. Sitemaps - Direct Submit (JSON)

**Endpoint:** `POST /api/v3/sitemaps/direct-submit`

**Authentication:** Required (Bearer token)

**Request Body:**
```json
{
  "sitemap_urls": [
    "https://example.com/sitemap.xml",
    "https://example.com/sitemap_index.xml",
    "https://testsite.org/sitemap.xml"
  ],
  "auto_import": false
}
```

**Request Schema:**
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `sitemap_urls` | array[HttpUrl] | Yes | 1-50 sitemap URLs |
| `auto_import` | boolean | No | If true, sets status to Selected+Queued for immediate import. Default: false |

**URL Validation:**
- Must be valid HTTP/HTTPS URL
- Must end with `.xml` OR contain `sitemap` in path
- Examples: `/sitemap.xml`, `/sitemap_index.xml`, `/products-sitemap.xml`

**Auto-Domain Creation:**
- Extracts domain from sitemap URL
- Creates domain record if doesn't exist
- Links sitemap to domain automatically

**Response (200 OK):**
```json
{
  "submitted_count": 3,
  "sitemap_ids": [
    "323e4567-e89b-12d3-a456-426614174000",
    "323e4567-e89b-12d3-a456-426614174001",
    "323e4567-e89b-12d3-a456-426614174002"
  ],
  "auto_queued": false
}
```

**Error Responses:**
- `401 Unauthorized` - Missing or invalid JWT token
- `409 Conflict` - Sitemap URL already exists in database
- `422 Unprocessable Entity` - Validation error (not .xml, invalid URL, exceeds 50)

---

### 4. Domains - CSV Import

**Endpoint:** `POST /api/v3/domains/import-csv`

**Authentication:** Required (Bearer token)

**Request:** `multipart/form-data` file upload

**CSV Format:**
```csv
domain
example.com
www.testsite.org
https://another-site.com
```

**CSV Requirements:**
- Max 1000 rows
- Optional header row (auto-detected)
- Single column: `domain` (or no header)
- UTF-8 encoding
- File extension: `.csv`

**Header Detection:**
First row is considered a header if it contains: `domain`, `domains`, `url`, or `website` (case-insensitive).

**Processing Behavior:**
- **Partial Success:** Continues processing on errors
- **Deduplication:** Removes duplicates within CSV
- **Skips Existing:** If domain already in database, marks as "skipped"
- **Validation:** Each row validated individually

**Response (200 OK):**
```json
{
  "total_rows": 100,
  "successful": 95,
  "failed": 3,
  "skipped": 2,
  "results": [
    {
      "row_number": 1,
      "value": "example.com",
      "status": "success",
      "id": "123e4567-e89b-12d3-a456-426614174000",
      "error": null
    },
    {
      "row_number": 2,
      "value": "bad!domain@#$",
      "status": "error",
      "id": null,
      "error": "Invalid domain format: bad!domain@#$"
    },
    {
      "row_number": 3,
      "value": "testsite.org",
      "status": "skipped",
      "id": "223e4567-e89b-12d3-a456-426614174000",
      "error": "Domain already exists in database"
    }
  ]
}
```

**Response Schema:**
| Field | Type | Description |
|-------|------|-------------|
| `total_rows` | integer | Total rows processed (excluding header) |
| `successful` | integer | Successfully created domains |
| `failed` | integer | Validation or database errors |
| `skipped` | integer | Duplicates (within CSV or database) |
| `results` | array | Detailed per-row results |

**Result Item Schema:**
| Field | Type | Description |
|-------|------|-------------|
| `row_number` | integer | 1-based row number (excluding header) |
| `value` | string | The domain value from CSV |
| `status` | string | "success", "error", or "skipped" |
| `id` | UUID | Domain ID (null for errors) |
| `error` | string | Error message (null for success) |

**Error Responses:**
- `400 Bad Request` - File not .csv, not UTF-8, empty, or exceeds 1000 rows
- `401 Unauthorized` - Missing or invalid JWT token
- `422 Unprocessable Entity` - Missing file parameter

---

### 5. Pages - CSV Import

**Endpoint:** `POST /api/v3/pages/import-csv`

**Authentication:** Required (Bearer token)

**Request:** `multipart/form-data` file upload

**CSV Format:**
```csv
url
https://example.com/contact
https://example.com/about
https://testsite.org/services
```

**CSV Requirements:**
- Max 1000 rows
- Optional header row (auto-detected: `url`, `urls`, `page`, `pages`, `link`)
- Single column: page URLs
- UTF-8 encoding
- File extension: `.csv`

**Processing Behavior:**
- **Partial Success:** Continues processing on errors
- **Auto-Creates Domains:** If domain doesn't exist, creates it automatically
- **Skips Existing:** If page URL already in database, marks as "skipped"
- **Default Settings:**
  - `page_curation_status` = "New"
  - `priority_level` = 5
  - `page_processing_status` = NULL

**Response:** Same schema as Domains CSV Import (see above)

**Error Responses:**
- `400 Bad Request` - File not .csv, not UTF-8, empty, or exceeds 1000 rows
- `401 Unauthorized` - Missing or invalid JWT token
- `422 Unprocessable Entity` - Missing file parameter

---

### 6. Sitemaps - CSV Import

**Endpoint:** `POST /api/v3/sitemaps/import-csv`

**Authentication:** Required (Bearer token)

**Request:** `multipart/form-data` file upload

**CSV Format:**
```csv
sitemap_url
https://example.com/sitemap.xml
https://example.com/sitemap_index.xml
https://testsite.org/sitemap.xml
```

**CSV Requirements:**
- Max 1000 rows
- Optional header row (auto-detected: `sitemap_url`, `sitemap`, `url`, `sitemaps`, `sitemap_urls`)
- Single column: sitemap URLs
- UTF-8 encoding
- File extension: `.csv`

**Processing Behavior:**
- **Partial Success:** Continues processing on errors
- **Auto-Creates Domains:** If domain doesn't exist, creates it automatically
- **Skips Existing:** If sitemap URL already in database, marks as "skipped"
- **URL Validation:** Must end with `.xml` OR contain `sitemap` in path
- **Default Settings:**
  - `deep_scrape_curation_status` = "New"
  - `sitemap_type` = "STANDARD"
  - `sitemap_import_status` = NULL

**Response:** Same schema as Domains CSV Import (see above)

**Error Responses:**
- `400 Bad Request` - File not .csv, not UTF-8, empty, or exceeds 1000 rows
- `401 Unauthorized` - Missing or invalid JWT token
- `422 Unprocessable Entity` - Missing file parameter

---

## Frontend Integration Examples

### React + Axios - Direct Submit (JSON)

```jsx
import axios from 'axios';

// Submit domains
const submitDomains = async (domains, autoQueue = false) => {
  try {
    const response = await axios.post(
      '/api/v3/domains/direct-submit',
      {
        domains: domains,
        auto_queue: autoQueue
      },
      {
        headers: {
          'Authorization': `Bearer ${getAuthToken()}`,
          'Content-Type': 'application/json'
        }
      }
    );

    console.log(`Submitted ${response.data.submitted_count} domains`);
    console.log('Domain IDs:', response.data.domain_ids);
    return response.data;
  } catch (error) {
    if (error.response?.status === 409) {
      alert('One or more domains already exist');
    } else if (error.response?.status === 422) {
      alert('Invalid domain format: ' + error.response.data.detail);
    } else {
      alert('Error submitting domains');
    }
    throw error;
  }
};

// Submit pages
const submitPages = async (urls, autoQueue = false, priorityLevel = 5) => {
  try {
    const response = await axios.post(
      '/api/v3/pages/direct-submit',
      {
        urls: urls,
        auto_queue: autoQueue,
        priority_level: priorityLevel
      },
      {
        headers: {
          'Authorization': `Bearer ${getAuthToken()}`,
          'Content-Type': 'application/json'
        }
      }
    );

    return response.data;
  } catch (error) {
    console.error('Error submitting pages:', error);
    throw error;
  }
};

// Submit sitemaps
const submitSitemaps = async (sitemapUrls, autoImport = false) => {
  try {
    const response = await axios.post(
      '/api/v3/sitemaps/direct-submit',
      {
        sitemap_urls: sitemapUrls,
        auto_import: autoImport
      },
      {
        headers: {
          'Authorization': `Bearer ${getAuthToken()}`,
          'Content-Type': 'application/json'
        }
      }
    );

    return response.data;
  } catch (error) {
    console.error('Error submitting sitemaps:', error);
    throw error;
  }
};
```

---

### React + Axios - CSV Import

```jsx
import axios from 'axios';

const importCSV = async (file, endpoint) => {
  const formData = new FormData();
  formData.append('file', file);

  try {
    const response = await axios.post(
      endpoint, // '/api/v3/domains/import-csv' or '/api/v3/pages/import-csv' or '/api/v3/sitemaps/import-csv'
      formData,
      {
        headers: {
          'Authorization': `Bearer ${getAuthToken()}`,
          'Content-Type': 'multipart/form-data'
        }
      }
    );

    return response.data;
  } catch (error) {
    if (error.response?.status === 400) {
      const detail = error.response.data.detail;
      if (detail.includes('1000 rows')) {
        alert('CSV file too large. Maximum 1000 rows allowed.');
      } else if (detail.includes('UTF-8')) {
        alert('CSV must be UTF-8 encoded');
      } else {
        alert(`Invalid CSV: ${detail}`);
      }
    }
    throw error;
  }
};

// React component example
const CSVUploadComponent = () => {
  const [uploadType, setUploadType] = useState('domains');
  const [results, setResults] = useState(null);
  const [uploading, setUploading] = useState(false);

  const handleFileUpload = async (event) => {
    const file = event.target.files[0];
    if (!file) return;

    setUploading(true);

    const endpointMap = {
      domains: '/api/v3/domains/import-csv',
      pages: '/api/v3/pages/import-csv',
      sitemaps: '/api/v3/sitemaps/import-csv'
    };

    try {
      const data = await importCSV(file, endpointMap[uploadType]);
      setResults(data);

      alert(
        `Import complete!\n` +
        `Successful: ${data.successful}\n` +
        `Failed: ${data.failed}\n` +
        `Skipped: ${data.skipped}`
      );
    } catch (error) {
      console.error('Upload failed:', error);
    } finally {
      setUploading(false);
    }
  };

  return (
    <div>
      <select value={uploadType} onChange={(e) => setUploadType(e.target.value)}>
        <option value="domains">Domains</option>
        <option value="pages">Pages</option>
        <option value="sitemaps">Sitemaps</option>
      </select>

      <input
        type="file"
        accept=".csv"
        onChange={handleFileUpload}
        disabled={uploading}
      />

      {uploading && <p>Uploading...</p>}

      {results && (
        <div>
          <h3>Results</h3>
          <p>Total: {results.total_rows}</p>
          <p>Successful: {results.successful}</p>
          <p>Failed: {results.failed}</p>
          <p>Skipped: {results.skipped}</p>

          <table>
            <thead>
              <tr>
                <th>Row</th>
                <th>Value</th>
                <th>Status</th>
                <th>Error</th>
              </tr>
            </thead>
            <tbody>
              {results.results.map((result) => (
                <tr key={result.row_number}>
                  <td>{result.row_number}</td>
                  <td>{result.value}</td>
                  <td>{result.status}</td>
                  <td>{result.error || '-'}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
};
```

---

## Testing Guide

### Manual Testing (cURL)

**Prerequisites:**
```bash
# 1. Get JWT token
export JWT_TOKEN="your_jwt_token_here"

# 2. Set base URL
export BASE_URL="http://localhost:8000"
```

**Test 1: Submit Domains (JSON)**
```bash
curl -X POST "$BASE_URL/api/v3/domains/direct-submit" \
  -H "Authorization: Bearer $JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "domains": ["example.com", "testsite.org"],
    "auto_queue": false
  }'
```

**Expected:** 200 OK with `submitted_count: 2`

---

**Test 2: Submit Pages (JSON)**
```bash
curl -X POST "$BASE_URL/api/v3/pages/direct-submit" \
  -H "Authorization: Bearer $JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "urls": [
      "https://example.com/contact",
      "https://example.com/about"
    ],
    "auto_queue": false,
    "priority_level": 3
  }'
```

**Expected:** 200 OK with `submitted_count: 2`

---

**Test 3: Submit Sitemaps (JSON)**
```bash
curl -X POST "$BASE_URL/api/v3/sitemaps/direct-submit" \
  -H "Authorization: Bearer $JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "sitemap_urls": [
      "https://example.com/sitemap.xml"
    ],
    "auto_import": false
  }'
```

**Expected:** 200 OK with `submitted_count: 1`

---

**Test 4: Import Domains CSV**

Create `domains.csv`:
```csv
domain
example.com
testsite.org
another-domain.net
```

```bash
curl -X POST "$BASE_URL/api/v3/domains/import-csv" \
  -H "Authorization: Bearer $JWT_TOKEN" \
  -F "file=@domains.csv"
```

**Expected:** 200 OK with detailed results for each row

---

**Test 5: Import Pages CSV**

Create `pages.csv`:
```csv
url
https://example.com/page1
https://example.com/page2
https://testsite.org/contact
```

```bash
curl -X POST "$BASE_URL/api/v3/pages/import-csv" \
  -H "Authorization: Bearer $JWT_TOKEN" \
  -F "file=@pages.csv"
```

**Expected:** 200 OK with detailed results

---

**Test 6: Import Sitemaps CSV**

Create `sitemaps.csv`:
```csv
sitemap_url
https://example.com/sitemap.xml
https://testsite.org/sitemap_index.xml
```

```bash
curl -X POST "$BASE_URL/api/v3/sitemaps/import-csv" \
  -H "Authorization: Bearer $JWT_TOKEN" \
  -F "file=@sitemaps.csv"
```

**Expected:** 200 OK with detailed results

---

### Error Testing

**Test 7: Duplicate Domain (409)**
```bash
# Submit same domain twice
curl -X POST "$BASE_URL/api/v3/domains/direct-submit" \
  -H "Authorization: Bearer $JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "domains": ["example.com"],
    "auto_queue": false
  }'

# Try again - should get 409
curl -X POST "$BASE_URL/api/v3/domains/direct-submit" \
  -H "Authorization: Bearer $JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "domains": ["example.com"],
    "auto_queue": false
  }'
```

**Expected:** Second request returns 409 Conflict

---

**Test 8: Invalid Domain Format (422)**
```bash
curl -X POST "$BASE_URL/api/v3/domains/direct-submit" \
  -H "Authorization: Bearer $JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "domains": ["not a valid domain!@#$"],
    "auto_queue": false
  }'
```

**Expected:** 422 Unprocessable Entity

---

**Test 9: Missing Authentication (401)**
```bash
curl -X POST "$BASE_URL/api/v3/domains/direct-submit" \
  -H "Content-Type: application/json" \
  -d '{
    "domains": ["example.com"],
    "auto_queue": false
  }'
```

**Expected:** 401 Unauthorized

---

**Test 10: CSV Too Large (400)**

Create CSV with 1001 rows and upload:
```bash
curl -X POST "$BASE_URL/api/v3/domains/import-csv" \
  -H "Authorization: Bearer $JWT_TOKEN" \
  -F "file=@large_domains.csv"
```

**Expected:** 400 Bad Request with message "CSV exceeds maximum of 1000 rows"

---

## Edge Cases & Limitations

### Direct Submit (JSON)

**Domain Normalization:**
- ✅ Multiple variations normalize to same domain
- ✅ Deduplication happens automatically
- Example: `["www.example.com", "https://example.com", "example.com"]` → All become `"example.com"`, only 1 created

**Limits:**
- Max 100 domains per request
- Max 100 pages per request
- Max 50 sitemaps per request

**Validation:**
- Domains: Regex pattern validation
- Pages: Must be valid HTTP/HTTPS URL
- Sitemaps: Must be valid URL AND end with `.xml` or contain `sitemap`

**Duplicates:**
- Within request: Auto-deduplicated before DB insert
- In database: Returns 409 Conflict error, stops processing

---

### CSV Import

**Header Detection:**
- First row checked for known column names (case-insensitive)
- If header detected, skipped during processing
- If no header, all rows processed as data

**Empty Rows:**
- Automatically skipped
- Not counted in `total_rows`

**Duplicates Within CSV:**
- After normalization, duplicates removed
- Only first occurrence processed
- Subsequent occurrences marked as "skipped"

**Duplicates in Database:**
- Marked as "skipped" in results
- Returns existing ID in response
- Continues processing other rows

**Partial Success:**
- One bad row doesn't stop entire import
- Each row processed independently
- Errors collected and returned in results

**Transaction Handling:**
- All successful inserts committed in single transaction
- If transaction fails, all changes rolled back
- Partial commits not supported

---

## Common Issues & Solutions

### Issue 1: "401 Unauthorized"
**Cause:** Missing or invalid JWT token
**Solution:**
- Verify token is included in `Authorization: Bearer {token}` header
- Check token hasn't expired
- Regenerate token if needed

---

### Issue 2: "409 Conflict - Domain already exists"
**Cause:** Attempting to submit domain that's already in database
**Solution:**
- Check if domain exists before submitting
- Or: Handle 409 gracefully in UI (e.g., "This domain is already tracked")
- CSV Import: Use CSV method instead - it skips duplicates automatically

---

### Issue 3: CSV Import shows all "skipped"
**Cause:** All items already exist in database
**Solution:** This is normal behavior, not an error. Check `results` array for `error` field.

---

### Issue 4: "422 Unprocessable Entity - Invalid domain format"
**Cause:** Domain validation failed
**Solution:**
- Ensure domains don't contain special characters (except hyphens and dots)
- Don't include protocols (they'll be removed anyway)
- Examples:
  - ✅ Valid: `example.com`, `test-site.org`, `subdomain.example.co.uk`
  - ❌ Invalid: `example com`, `site!.com`, `http://` (just protocol)

---

### Issue 5: Sitemap URL rejected
**Cause:** URL doesn't end with `.xml` or contain `sitemap`
**Solution:**
- Ensure sitemap URLs end with `.xml`
- Or contain word `sitemap` in path
- Examples:
  - ✅ Valid: `/sitemap.xml`, `/sitemap_index.xml`, `/products-sitemap.xml`
  - ❌ Invalid: `/sitemaps` (no .xml), `/robots.txt`

---

### Issue 6: CSV import returns "File must be UTF-8 encoded"
**Cause:** CSV file is not UTF-8 encoded
**Solution:**
- Export CSV as UTF-8 from Excel/Google Sheets
- Excel: Save As → CSV UTF-8 (Comma delimited)
- Google Sheets: Download → Comma-separated values (.csv)

---

## Status Workflow

### Domain Status Flow

**When `auto_queue=false` (default):**
```
Created → sitemap_curation_status: "New"
       → sitemap_analysis_status: NULL
       → Requires manual curation in UI
```

**When `auto_queue=true`:**
```
Created → sitemap_curation_status: "Selected"
       → sitemap_analysis_status: "queued"
       → Scheduler picks up automatically
       → Sitemap discovery begins
```

---

### Page Status Flow

**When `auto_queue=false` (default):**
```
Created → page_curation_status: "New"
       → page_processing_status: NULL
       → Requires manual curation in UI
```

**When `auto_queue=true`:**
```
Created → page_curation_status: "Selected"
       → page_processing_status: "Queued"
       → Scheduler picks up automatically
       → Page scraping begins
```

---

### Sitemap Status Flow

**When `auto_import=false` (default):**
```
Created → deep_scrape_curation_status: "New"
       → sitemap_import_status: NULL
       → Requires manual curation in UI
```

**When `auto_import=true`:**
```
Created → deep_scrape_curation_status: "Selected"
       → sitemap_import_status: "Queued"
       → Scheduler picks up automatically
       → Sitemap parsing begins
```

---

## Database Records Created

### Direct Domain Submit
Creates record in `domains` table:
- `id` (UUID)
- `domain` (normalized)
- `tenant_id` (DEFAULT_TENANT_ID)
- `local_business_id` (NULL)
- `sitemap_curation_status` (New or Selected)
- `sitemap_analysis_status` (NULL or queued)

### Direct Page Submit
Creates records in:
1. **`pages` table:**
   - `id`, `url`, `domain_id`, `tenant_id`
   - `page_curation_status`, `page_processing_status`
   - `priority_level`, `sitemap_file_id` (NULL)

2. **`domains` table (if needed):**
   - Auto-created if domain doesn't exist

### Direct Sitemap Submit
Creates records in:
1. **`sitemap_files` table:**
   - `id`, `url`, `domain_id`
   - `deep_scrape_curation_status`, `sitemap_import_status`
   - `sitemap_type` ("STANDARD"), `user_id`

2. **`domains` table (if needed):**
   - Auto-created if domain doesn't exist

---

## UI/UX Recommendations

### Form Validation (Client-Side)

**Domains:**
```javascript
const validateDomain = (domain) => {
  // Remove protocol and www
  const normalized = domain
    .replace(/^https?:\/\//, '')
    .replace(/^www\./, '')
    .toLowerCase();

  // Check format
  const domainRegex = /^[a-z0-9]([a-z0-9-]{0,61}[a-z0-9])?(\.[a-z0-9]([a-z0-9-]{0,61}[a-z0-9])?)*$/;
  return domainRegex.test(normalized);
};
```

**Pages:**
```javascript
const validatePageUrl = (url) => {
  try {
    const parsed = new URL(url);
    return parsed.protocol === 'http:' || parsed.protocol === 'https:';
  } catch {
    return false;
  }
};
```

**Sitemaps:**
```javascript
const validateSitemapUrl = (url) => {
  try {
    const parsed = new URL(url);
    const hasProtocol = parsed.protocol === 'http:' || parsed.protocol === 'https:';
    const isSitemap = url.endsWith('.xml') || url.toLowerCase().includes('sitemap');
    return hasProtocol && isSitemap;
  } catch {
    return false;
  }
};
```

---

### Progress Indicators

**For CSV Import:**
```jsx
// Show progress during upload
const [uploadProgress, setUploadProgress] = useState(0);

const config = {
  onUploadProgress: (progressEvent) => {
    const percentCompleted = Math.round(
      (progressEvent.loaded * 100) / progressEvent.total
    );
    setUploadProgress(percentCompleted);
  }
};

await axios.post(endpoint, formData, { ...config, headers });
```

---

### Result Display

**Show summary stats:**
```jsx
<div className="import-summary">
  <div className="stat">
    <span className="label">Total:</span>
    <span className="value">{results.total_rows}</span>
  </div>
  <div className="stat success">
    <span className="label">Successful:</span>
    <span className="value">{results.successful}</span>
  </div>
  <div className="stat failed">
    <span className="label">Failed:</span>
    <span className="value">{results.failed}</span>
  </div>
  <div className="stat skipped">
    <span className="label">Skipped:</span>
    <span className="value">{results.skipped}</span>
  </div>
</div>
```

**Show detailed errors:**
```jsx
{results.results
  .filter(r => r.status === 'error')
  .map(result => (
    <div key={result.row_number} className="error-row">
      <strong>Row {result.row_number}:</strong> {result.value}
      <br />
      <span className="error-message">{result.error}</span>
    </div>
  ))
}
```

---

## Performance Considerations

### Rate Limiting
- No built-in rate limiting currently
- Frontend should implement request throttling for bulk operations
- Recommended: Max 5 concurrent CSV imports

### File Size
- CSV limited to 1000 rows per file
- For larger datasets, split into multiple files
- Process sequentially to avoid overwhelming backend

### Response Time
- Direct Submit (JSON): ~100-500ms for 100 items
- CSV Import: ~1-5 seconds for 1000 rows
- Depends on: duplicate checks, domain creation, network latency

---

## Security Notes

### Authentication
- All endpoints require valid JWT token
- Token must be included in `Authorization: Bearer {token}` header
- 401 Unauthorized returned if missing/invalid

### Input Validation
- All user input validated server-side
- Pydantic models enforce type checking
- SQL injection prevented via SQLAlchemy ORM

### File Upload Security
- Only `.csv` files accepted
- UTF-8 encoding required
- Max file size enforced (1000 rows)
- No executable code in CSV (data-only)

---

## Future Enhancements (Not Yet Implemented)

- [ ] Async processing for large CSV files (background jobs)
- [ ] Webhook notifications when import completes
- [ ] CSV download of import results
- [ ] Batch status updates (mark multiple as Selected/Rejected)
- [ ] Custom field mapping for CSV (non-standard columns)
- [ ] Excel (.xlsx) file support
- [ ] URL preview/validation before submit
- [ ] Duplicate detection across multiple CSVs

---

## Support & Troubleshooting

### Debugging Steps

1. **Check JWT Token:**
   ```javascript
   console.log('Token:', localStorage.getItem('authToken'));
   ```

2. **Inspect Network Request:**
   - Open browser DevTools → Network tab
   - Look for request to `/api/v3/*/direct-submit` or `/import-csv`
   - Check request headers, payload, response

3. **Verify CSV Format:**
   - Open CSV in text editor
   - Ensure UTF-8 encoding
   - Check for special characters
   - Verify single column structure

4. **Test with cURL:**
   - Use example cURL commands above
   - Isolate frontend vs backend issue

---

## Backend Developer Contact

For questions about:
- API behavior
- Bug reports
- Feature requests
- Integration issues

Contact: Backend team or create GitHub issue

---

**Document Version:** 1.0
**Last Updated:** November 17, 2025
**Status:** Production Ready ✅
