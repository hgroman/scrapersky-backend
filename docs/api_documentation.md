# ScraperSky API Documentation

This document provides comprehensive details about the ScraperSky API endpoints, focusing on the newly implemented batch processing capabilities and other features.

## Base URL

```
https://scrapersky-backend.onrender.com/api/v1
```

For local development:

```
http://localhost:8000/api/v1
```

## Authentication

All API requests require a valid tenant ID to be included in the request body. This ID is used to associate scanned domains with specific tenants in the database.

Example tenant ID format: `550e8400-e29b-41d4-a716-446655440000` (UUID format)

## Endpoints

### 1. Single Domain Scan

**Endpoint:** `/scrapersky`
**Method:** `POST`
**Description:** Scans a single domain and extracts metadata.

#### Request Body

```json
{
  "base_url": "example.com",
  "tenant_id": "550e8400-e29b-41d4-a716-446655440000"
}
```

| Parameter | Type   | Required | Description                                            |
| --------- | ------ | -------- | ------------------------------------------------------ |
| base_url  | string | Yes      | The domain to scan (with or without http/https prefix) |
| tenant_id | string | Yes      | UUID of the tenant                                     |

#### Response

```json
{
  "job_id": "scan_1fa3b605358f4a0d927c0d11b0eb27de",
  "status_url": "/api/v1/status/scan_1fa3b605358f4a0d927c0d11b0eb27de"
}
```

| Field      | Type   | Description                         |
| ---------- | ------ | ----------------------------------- |
| job_id     | string | Unique identifier for the scan job  |
| status_url | string | URL to check the status of the scan |

### 2. Batch Domain Scan

**Endpoint:** `/batch`
**Method:** `POST`
**Description:** Scans multiple domains in batch mode.

#### Request Body

```json
{
  "domains": ["example.com", "github.com", "stackoverflow.com"],
  "tenant_id": "550e8400-e29b-41d4-a716-446655440000"
}
```

| Parameter | Type   | Required | Description              |
| --------- | ------ | -------- | ------------------------ |
| domains   | array  | Yes      | Array of domains to scan |
| tenant_id | string | Yes      | UUID of the tenant       |

#### Response

```json
{
  "batch_id": "batch_8f7d6c5e4b3a2c1d0e9f8a7b6c5d4e3f",
  "status_url": "/api/v1/batch/status/batch_8f7d6c5e4b3a2c1d0e9f8a7b6c5d4e3f",
  "job_count": 3
}
```

| Field      | Type    | Description                          |
| ---------- | ------- | ------------------------------------ |
| batch_id   | string  | Unique identifier for the batch job  |
| status_url | string  | URL to check the status of the batch |
| job_count  | integer | Number of domains in the batch       |

### 3. Check Scan Status

**Endpoint:** `/status/{job_id}`
**Method:** `GET`
**Description:** Checks the status of a single domain scan.

#### URL Parameters

| Parameter | Type   | Required | Description                               |
| --------- | ------ | -------- | ----------------------------------------- |
| job_id    | string | Yes      | The job ID returned from the scan request |

#### Response

```json
{
  "job_id": "scan_1fa3b605358f4a0d927c0d11b0eb27de",
  "status": "completed",
  "started_at": "2025-02-24T20:48:44.861811",
  "completed_at": "2025-02-24T20:48:45.482812",
  "metadata": {
    "title": "Example Domain",
    "description": "This domain is for use in illustrative examples in documents.",
    "language": "en",
    "is_wordpress": false,
    "wordpress_version": null,
    "has_elementor": false,
    "favicon_url": "https://example.com/favicon.ico",
    "logo_url": "https://example.com/logo.png",
    "contact_info": {
      "email": ["info@example.com"],
      "phone": ["+1-123-456-7890"]
    },
    "social_links": {
      "facebook": "https://facebook.com/example",
      "twitter": "https://twitter.com/example",
      "linkedin": "https://linkedin.com/company/example",
      "instagram": "https://instagram.com/example"
    },
    "tech_stack": {
      "cms": [],
      "frameworks": ["Jquery", "Vue"],
      "analytics": ["Google Analytics"],
      "widgets": []
    },
    "performance": {
      "image_count": 16,
      "script_count": 39,
      "css_count": 3,
      "form_count": 5,
      "link_count": 256,
      "total_elements": 1389
    }
  },
  "error": null,
  "progress": {
    "step": "completed",
    "message": "Scan completed successfully"
  }
}
```

| Status    | Description                          |
| --------- | ------------------------------------ |
| pending   | Scan has been queued but not started |
| running   | Scan is in progress                  |
| completed | Scan has completed successfully      |
| failed    | Scan has failed                      |

### 4. Check Batch Status

**Endpoint:** `/batch/status/{batch_id}`
**Method:** `GET`
**Description:** Checks the status of a batch scan.

#### URL Parameters

| Parameter | Type   | Required | Description                                       |
| --------- | ------ | -------- | ------------------------------------------------- |
| batch_id  | string | Yes      | The batch ID returned from the batch scan request |

#### Response

```json
{
  "batch_id": "batch_8f7d6c5e4b3a2c1d0e9f8a7b6c5d4e3f",
  "status": "in_progress",
  "started_at": "2025-02-24T20:48:44.861811",
  "completed_at": null,
  "total_jobs": 3,
  "completed_jobs": 1,
  "failed_jobs": 0,
  "jobs": [
    {
      "domain": "example.com",
      "job_id": "scan_1fa3b605358f4a0d927c0d11b0eb27de",
      "status": "completed"
    },
    {
      "domain": "github.com",
      "job_id": "scan_2eb4c716469b5b1e038d1e22c1fc38ef",
      "status": "running"
    },
    {
      "domain": "stackoverflow.com",
      "job_id": "scan_3fc5d827570c6c2f149e2f33d2fd49fg",
      "status": "pending"
    }
  ]
}
```

| Batch Status | Description                           |
| ------------ | ------------------------------------- |
| pending      | Batch has been queued but not started |
| in_progress  | Batch is in progress                  |
| completed    | All jobs in the batch have completed  |
| failed       | All jobs in the batch have failed     |
| partial      | Some jobs completed, some failed      |

## CSV Upload Integration

The backend supports processing CSV files for batch domain scanning. The UI should implement the following:

1. **File Input Component**:

   - Accept `.csv` files
   - Validate file size (max 5MB recommended)
   - Parse CSV on client-side to preview domains

2. **CSV Format Requirements**:

   - The CSV should have a header row
   - It should contain a column named either "domain", "url", or "website"
   - Example:
     ```
     domain
     example.com
     github.com
     stackoverflow.com
     ```

3. **Domain Validation**:

   - The UI should validate domains before submission
   - Remove any protocol prefixes (http://, https://)
   - Remove "www." prefixes
   - Remove paths and query parameters
   - Basic domain format validation (e.g., must contain a dot, valid TLD)

4. **Batch Processing UI**:
   - Display a progress bar for overall batch completion
   - Show individual domain status (pending, running, completed, failed)
   - Allow viewing detailed results for each domain
   - Provide error messages for failed domains

## Multi-line Domain Input

The backend also supports direct input of multiple domains. The UI should:

1. **Text Area Component**:

   - Accept multiple lines of text
   - Each line should be treated as a separate domain
   - Validate and clean each domain as described above

2. **Parsing Logic**:
   - Split input by newline characters
   - Trim whitespace from each line
   - Filter out empty lines
   - Validate each domain

## Error Handling

The API returns standard HTTP status codes:

| Status Code | Description                                      |
| ----------- | ------------------------------------------------ |
| 200         | Success                                          |
| 400         | Bad Request (invalid domain, missing parameters) |
| 404         | Not Found (job ID not found)                     |
| 500         | Server Error                                     |

Error responses include a detail message:

```json
{
  "detail": "Invalid domain format"
}
```

## Rate Limiting

The API implements rate limiting to prevent abuse:

- 60 requests per minute per IP address
- 5 batch requests per minute per IP address (max 100 domains per batch)

## Implementation Notes for UI

1. **Domain Handling**:

   ```javascript
   function cleanDomain(domain) {
     if (!domain) return null;

     // Clean the domain - remove whitespace, convert to lowercase
     domain = domain.trim().toLowerCase();

     // Remove any protocol prefix if present
     if (domain.includes("://")) {
       domain = domain.split("://")[1];
     }

     // Remove www. prefix if present
     if (domain.startsWith("www.")) {
       domain = domain.substring(4);
     }

     // Remove any paths or query parameters
     domain = domain.split("/")[0];

     // Basic domain validation
     const domainPattern = /^[a-z0-9]+([\-\.]{1}[a-z0-9]+)*\.[a-z]{2,}$/;
     if (!domainPattern.test(domain)) {
       return null;
     }

     return domain;
   }
   ```

2. **CSV Parsing**:

   ```javascript
   function parseCSV(file) {
     return new Promise((resolve, reject) => {
       const reader = new FileReader();
       reader.onload = (e) => {
         const contents = e.target.result;
         const lines = contents.split("\n");

         // Find header row and domain column
         let domainColumnIndex = -1;
         const headerRow = lines[0].split(",");

         for (let i = 0; i < headerRow.length; i++) {
           const header = headerRow[i].trim().toLowerCase();
           if (
             header === "domain" ||
             header === "url" ||
             header === "website"
           ) {
             domainColumnIndex = i;
             break;
           }
         }

         if (domainColumnIndex === -1) {
           reject(
             'Could not find a column named "domain", "url", or "website"'
           );
           return;
         }

         // Extract domains
         const domains = [];
         for (let i = 1; i < lines.length; i++) {
           if (!lines[i].trim()) continue;

           const columns = lines[i].split(",");
           if (columns.length > domainColumnIndex) {
             const domain = cleanDomain(columns[domainColumnIndex]);
             if (domain) domains.push(domain);
           }
         }

         resolve(domains);
       };

       reader.onerror = () => reject("Error reading file");
       reader.readAsText(file);
     });
   }
   ```

3. **Polling for Status**:

   ```javascript
   async function pollStatus(jobId, onUpdate) {
     try {
       const response = await fetch(`/api/v1/status/${jobId}`);
       const data = await response.json();

       onUpdate(data);

       if (data.status === "completed" || data.status === "failed") {
         return data;
       }

       // Continue polling
       setTimeout(() => pollStatus(jobId, onUpdate), 2000);
     } catch (error) {
       onUpdate({ status: "failed", error: error.message });
     }
   }
   ```

## Database Schema

The domains are stored in the Supabase database with the following schema:

```sql
CREATE TABLE domains (
  id SERIAL PRIMARY KEY,
  tenant_id UUID NOT NULL,
  domain VARCHAR(255) NOT NULL,
  title VARCHAR(255),
  description TEXT,
  favicon_url TEXT,
  logo_url TEXT,
  language VARCHAR(10),
  is_wordpress BOOLEAN DEFAULT FALSE,
  wordpress_version VARCHAR(20),
  has_elementor BOOLEAN DEFAULT FALSE,
  email_addresses TEXT[],
  phone_numbers TEXT[],
  facebook_url TEXT,
  twitter_url TEXT,
  linkedin_url TEXT,
  instagram_url TEXT,
  youtube_url TEXT,
  tech_stack JSONB,
  content_scrape_status VARCHAR(20) DEFAULT 'pending',
  content_scrape_at TIMESTAMP,
  first_scan TIMESTAMP DEFAULT NOW(),
  last_scan TIMESTAMP DEFAULT NOW(),
  meta_json JSONB,
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW(),
  UNIQUE(tenant_id, domain)
);
```

## Deployment Information

The backend is deployed on Render.com with automatic deployments from the GitHub repository. The UI should be configured to use the production API endpoint:

```
https://scrapersky-backend.onrender.com/api/v1
```

For local development, the UI should use:

```
http://localhost:8000/api/v1
```

## Conclusion

This API documentation provides all the necessary information for the UI team at Lovable.dev to integrate with the ScraperSky backend, particularly the new batch processing capabilities. If you have any questions or need further clarification, please contact the backend team.
