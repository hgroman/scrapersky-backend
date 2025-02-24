Below is a revised version of your README that reflects your current workflow and technology choices. I've replaced references to BigQuery with Supabase, updated the project structure accordingly, and highlighted your modern deployment workflow with Vercel and Lovable.dev.

Test Domain
curl -X POST "http://localhost:8000/api/v1/scrapersky" -H "Content-Type: application/json" -d '{"base_url": "https://txkidney.com", "max_pages": 100}'

---

# ScraperSky

A modular FastAPI-based web scraping system that extracts website metadata and stores it in Supabase. It integrates seamlessly with modern workflows—using Lovable.dev for UI design and GitHub for version control, with Vercel for rapid front-end deployment.

## Project Structure

```
ScraperSky/
├── src/
│   ├── main.py                    # FastAPI application setup and router inclusion
│   ├── models.py                  # Pydantic models (data validation and schemas)
│   ├── routers/
│   │   ├── __init__.py
│   │   ├── chat.py                # Chat endpoints (OpenAI integration)
│   │   ├── email_scanner.py       # Email scanning endpoints (using Supabase)
│   │   └── sitemap_scraper.py     # Sitemap scanning endpoints
│   ├── schemas/
│   │   └── contact.py             # Data models for contact information
│   ├── scraper/
│   │   ├── __init__.py
│   │   ├── metadata_extractor.py  # Website metadata extraction logic
│   │   └── utils.py               # Utility functions (e.g., ScraperAPI integration)
│   ├── services/
│   │   └── supabase.py            # Supabase client and database operations
│   └── tasks/
│       └── email_scraper.py       # Background task for email scraping
├── tests/                         # Unit and integration tests
│   ├── __init__.py
│   ├── test_metadata_extractor.py
│   ├── test_supabase_integration.py  # Updated to test Supabase usage
│   └── test_utils.py
├── static/
│   └── [various static files for web interfaces, e.g., index.html, chat.html, etc.]
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── pytest.ini                    # Test configuration
```

> **Note:** Old references to BigQuery have been removed. All data operations now use Supabase as the primary datastore.

## Features

### Current Capabilities

1. **Website Metadata Extraction**

   - Extracts comprehensive metadata from websites.
   - Detects CMS systems (e.g., WordPress, Elementor).
   - Identifies contact information and social links.
   - Analyzes tracking and analytics implementations.

2. **Supabase Integration**

   - Stores website metadata, contact data, and scan history in a Supabase PostgreSQL database.
   - Supports batch processing and maintains scan history.
   - Utilizes a robust connection setup (with connection pooling).

3. **Modular Architecture**

   - Clear separation between routes, scraping logic, background tasks, and database interactions.
   - Utility functions for common operations.
   - Comprehensive test coverage.

4. **Modern Workflow & Deployment**
   - UI design and GitHub integration via Lovable.dev.
   - Instant deployment of front-end changes on Vercel.
   - Back-end containerized with Docker and orchestrated on Kubernetes.
   - Environment configuration and secret management for secure deployments.

### API Endpoints

| Endpoint                  | Method | Purpose                | Example Request                                                                                                                                      |
| ------------------------- | ------ | ---------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------- |
| `/api/v1/scrapersky`      | POST   | Start sitemap scanning | `curl -X POST http://localhost:8000/api/v1/scrapersky -H "Content-Type: application/json" -d '{"base_url":"https://example.com", "max_pages": 100}'` |
| `/api/v1/status/{job_id}` | GET    | Get scan job status    | `curl http://localhost:8000/api/v1/status/job_123abc`                                                                                                |
| `/health`                 | GET    | Check service health   | `curl http://localhost:8000/health`                                                                                                                  |

Response Examples:

```json
# POST /api/v1/scrapersky response:
{
    "job_id": "job_123abc",
    "status": "started",
    "status_url": "/api/v1/status/job_123abc"
}

# GET /api/v1/status/{job_id} response:
{
    "status": "completed",
    "metadata": {
        "pages_scanned": 50,
        "wordpress_version": "6.4.3",
        "has_elementor": true
        // ... other metadata
    }
}
```

## Quick Start

1. **Environment Setup**

   ```bash
   # Copy example env file
   cp .env.example .env

   # Edit .env with your API keys and Supabase credentials
   OPENAI_API_KEY=your-openai-key-here
   SCRAPER_API_KEY=your-scraper-api-key-here
   SUPABASE_URL=your-supabase-url
   SUPABASE_SERVICE_ROLE_KEY=your-supabase-service-role-key
   SUPABASE_ANON_KEY=your-supabase-anon-key
   SUPABASE_DB_PASSWORD=your-supabase-db-password
   USER_AGENT=Your User Agent String (optional)
   ```

2. **Install Dependencies**

   ```bash
   pip install -r requirements.txt
   ```

3. **Run Tests**

   ```bash
   pytest
   ```

4. **Run with Docker**

   ```bash
   docker-compose up --build
   ```

5. **Test the Server**

   ```bash
   # Health check
   curl http://localhost:8000/health

   # Chat test
   curl -X POST http://localhost:8000/chat \
     -H "Content-Type: application/json" \
     -d '{"message":"Hello"}'
   ```

6. **Web Interface**
   Open [http://localhost:8000/static/index.html](http://localhost:8000/static/index.html) in your browser.

## Development

### Adding New Features

1. Create a new router in `src/routers/`.
2. Add models to `src/models.py` (or `src/schemas/` for API schemas).
3. Include the new router in `src/main.py`.
4. Update tests and documentation.

### Environment Variables

#### Core API Keys

- `OPENAI_API_KEY`: OpenAI API key for chat functionality.
- `SCRAPER_API_KEY`: Key for ScraperAPI.
- `USER_AGENT`: Custom user agent string for HTTP requests (optional).

#### Supabase Configuration

##### Basic Connection (Required)

- `SUPABASE_URL`: Your Supabase project URL.
- `SUPABASE_SERVICE_ROLE_KEY`: Service role key for Supabase.
- `SUPABASE_ANON_KEY`: Anonymous key for Supabase.
- `SUPABASE_DB_PASSWORD`: Database password for Supabase.

##### Pooler Connection (Required for Render.com and IPv4-only environments)

- `SUPABASE_POOLER_HOST`: Supabase pooler hostname (e.g., aws-0-us-west-1.pooler.supabase.com)
- `SUPABASE_POOLER_PORT`: Pooler port (default: 6543)
- `SUPABASE_POOLER_USER`: Pooler username (format: postgres.[project-ref])

> **Note**: Pooler configuration is essential for deployments on platforms like Render.com that require IPv4 connectivity.

### Supabase Integration

#### Credentials Setup (CRITICAL)

- **Service Account File:** Not applicable (using Supabase).
- **Project:** Managed via Supabase dashboard.
- **Database:** All data is stored in Supabase PostgreSQL, with tables for domains, pages, and contacts.

#### Usage in Code

```python
# ✅ Correct: Always use the standard Supabase client from our services module.
from ..services.supabase import db
```

#### Key Implementation Files

- **Database Connection:** `/src/db/sb_connection.py`
- **Usage Example:** `/src/routers/sitemap_scraper.py` and `/src/routers/email_scanner.py`

For detailed Supabase setup and troubleshooting, see our internal documentation.

## Next Steps

1. **Web Scraping Integration**

   - Enhance the scraping logic in `src/scraper/metadata_extractor.py` and related utilities.
   - Refine the email scanning logic to support high-concurrency (consider async HTTP clients).

2. **Security Enhancements**

   - Implement rate limiting and API authentication.
   - Use proper secret management for environment variables.

3. **Infrastructure**
   - Finalize Docker and Kubernetes deployment configurations.
   - Set up monitoring, CI/CD pipelines, and automated testing.

## Recent Updates

### 1. Development Workflow Enhancement (February 2025)

Our project leverages a modern, integrated development pipeline:

#### Frontend Development

- **Design & Development**: Lovable.dev
  - Direct integration with GitHub
  - Automated publishing of UI changes
  - Seamless version control integration

#### Backend Development

- **IDE & Development**: Windsurf
  - AI-assisted development environment
  - Direct GitHub integration
  - Advanced codebase management
  - Integrated testing and validation

#### Deployment Pipeline

- **Frontend**: GitHub → Vercel

  - Automatic deployment on push
  - Zero-configuration setup
  - Instant preview environments

- **Backend**: GitHub → Render.com
  - Automated deployment from main branch
  - Container-based deployment
  - IPv4-compatible infrastructure

### 2. Database Connection Improvements (February 2025)

#### IPv4 Compatibility for Cloud Deployments

- Added support for Supabase connection pooler to ensure IPv4 compatibility
- Implemented smart fallback mechanism: pooler first, direct connection as backup
- Critical for deployments on platforms like Render.com that require IPv4 connectivity

#### Additional Environment Variables

For Supabase pooler support, add these to your `.env`:

```env
# Supabase Pooler Configuration (IPv4 Compatible)
SUPABASE_POOLER_HOST=aws-0-us-west-1.pooler.supabase.com
SUPABASE_POOLER_PORT=6543
SUPABASE_POOLER_USER=postgres.[your-project-ref]
```

#### Connection Testing

Added two utility scripts for connection validation:

- `test_db_connection.py`: Comprehensive database connection testing
- `check_env.py`: Environment variable verification

To verify your setup:

```bash
# Check environment variables
python check_env.py

# Test database connection
python test_db_connection.py
```

### 3. Endpoint and Router Fixes

- Fixed and simplified `/api/v1/scrapersky` endpoint
- Added asynchronous job processing with status tracking
- Improved error handling and validation
- Added `/health` endpoint for service monitoring

### 2. Database Integration

- Enhanced Supabase connection with proper connection pooling
- Improved data insertion logic for website metadata
- Added comprehensive database testing

### 3. Frontend Testing

- Added `/static/endpoint-test.html` for easy API testing
- Improved error feedback and status monitoring

### 4. Development and Testing

- Enhanced Docker integration
- Added environment variable validation
- Improved logging and error tracking

## Contributing

1. Create a feature branch.
2. Add new functionality in the appropriate modules.
3. Update documentation.
4. Submit a pull request.

## License

MIT

---

## Database Connection Evolution

### Connection Strategy Changes

#### Previous Implementation

- Direct connection to Supabase database
- Used standard PostgreSQL connection (port 5432)
- IPv6-first DNS resolution
- Challenges with IPv4-only environments

#### Current Implementation (February 2025)

- Primary: Supabase Connection Pooler
  - IPv4-compatible connection
  - Transaction pooling for better resource management
  - Improved reliability in cloud environments
- Fallback: Direct Connection
  - Maintains backward compatibility
  - Supports IPv6-capable environments
  - Useful for local development

### Why We Made These Changes

1. **Cloud Deployment Compatibility**

   - Render.com and similar platforms often lack IPv6 support
   - Direct connections defaulting to IPv6 caused deployment failures
   - Pooler connection ensures reliable IPv4 connectivity

2. **Performance Benefits**

   - Connection pooling reduces database connection overhead
   - Better handling of concurrent connections
   - Improved resource utilization

3. **Reliability Improvements**
   - Smart fallback mechanism ensures connection availability
   - Automatic retry with alternative connection method
   - Better error handling and logging

### Implementation Details

#### Connection Logic

```python
# The system tries pooler connection first:
postgresql://postgres.[project-ref]@aws-0-us-west-1.pooler.supabase.com:6543/postgres

# Falls back to direct connection if pooler not configured:
postgresql://postgres.[project-ref]@db.[project-ref].supabase.co:5432/postgres
```

#### Verification

Use the provided test scripts to verify your connection:

```bash
# Verify environment setup
python check_env.py

# Test database connectivity
python test_db_connection.py
```

---

### Summary of Revisions:

- **BigQuery to Supabase:**
  All references to BigQuery have been removed; data operations now use Supabase.
- **Modern Deployment Workflow:**
  Updated to reflect your modern workflow using Lovable.dev, GitHub, and Vercel.
- **Project Structure:**
  Adjusted file names and paths (e.g., renamed `bigquery_integration.py` to focus on Supabase in the services folder).
- **Environment Variables:**
  Updated the environment variable list to include Supabase credentials and removed BigQuery-related variables.
- **Deployment & Development:**
  Emphasized Docker, Kubernetes, and continuous integration practices.

Feel free to adjust any details further to ensure the README accurately reflects your project's reality. Let me know if you need any more changes or additional information!

---

## API Integration Guide for Frontend Development

### API Endpoints

#### 1. Sitemap Scanning Endpoint

```
POST /api/v1/scrapersky
```

##### Request Format

```json
{
    "base_url": "https://example.com",
    "max_pages": 100,
    "tenant_id": "550e8400-e29b-41d4-a716-446655440000"  # Required UUID format
}
```

##### Response Format

```json
{
  "job_id": "unique_job_id",
  "status": "started",
  "status_url": "/api/v1/status/unique_job_id"
}
```

#### 2. Job Status Endpoint

```
GET /api/v1/status/{job_id}
```

##### Response Format

```json
{
  "status": "completed", // or "running", "failed"
  "metadata": {
    "title": "Website Title",
    "description": "Meta description",
    "language": "en",
    "is_wordpress": true,
    "wordpress_version": "6.4.3",
    "has_elementor": true,
    "favicon_url": "https://example.com/favicon.ico",
    "logo_url": "https://example.com/logo.png",
    "contact_info": {
      "email": ["contact@example.com"],
      "phone": ["+1-555-0123"]
    },
    "social_links": {
      "facebook": "https://facebook.com/example",
      "twitter": "https://twitter.com/example"
    }
  }
}
```

### Integration Requirements

1. **CORS Support**

   - API supports CORS for frontend integration
   - No additional headers required for basic operation
   - Production endpoints should restrict origins

2. **Error Handling**

   ```json
   {
     "detail": "Error message description",
     "status_code": 400
   }
   ```

3. **Rate Limiting**
   - Maximum 100 requests per minute per IP
   - Status code 429 when limit exceeded

### Example Integration Code

```javascript
// Submit URL for scanning
async function scanWebsite(url) {
  try {
    const response = await fetch(
      "https://scrapersky-backend.onrender.com/api/v1/scrapersky",
      {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          base_url: url,
          tenant_id: "550e8400-e29b-41d4-a716-446655440000",
        }),
      }
    );

    const data = await response.json();
    return data;
  } catch (error) {
    console.error("Scanning error:", error);
    throw error;
  }
}

// Check job status
async function checkStatus(jobId) {
  try {
    const response = await fetch(
      `https://scrapersky-backend.onrender.com/api/v1/status/${jobId}`
    );
    const data = await response.json();
    return data;
  } catch (error) {
    console.error("Status check error:", error);
    throw error;
  }
}

// Example usage with status polling
async function scanAndMonitor(url) {
  // Start scan
  const scanResult = await scanWebsite(url);

  // Poll for status
  const checkInterval = setInterval(async () => {
    const status = await checkStatus(scanResult.job_id);

    if (status.status === "completed") {
      clearInterval(checkInterval);
      // Handle completion
      console.log("Scan completed:", status.metadata);
    } else if (status.status === "failed") {
      clearInterval(checkInterval);
      // Handle failure
      console.error("Scan failed:", status.error);
    }
    // Continue polling if status is 'running'
  }, 5000); // Check every 5 seconds
}
```

### UI Implementation Guidelines

1. **User Input**

   - URL input field with validation
   - Optional max pages input
   - Submit button with loading state

2. **Progress Display**

   - Job ID display
   - Status indicator
   - Loading animation during scanning

3. **Results Display**

   - Organized sections for different metadata types
   - Error handling and user feedback
   - Copy/export functionality for results

4. **Recommended Libraries**
   - Axios or fetch for API calls
   - React Query for state management
   - Material-UI or Tailwind for components

### Testing Endpoints

- Development: `http://localhost:8000`
- Production: `https://scrapersky-backend.onrender.com`
- Swagger Docs: `https://scrapersky-backend.onrender.com/docs`
- OpenAPI Spec: `https://scrapersky-backend.onrender.com/openapi.json`

Refer to the example implementation in `/static/endpoint-test.html` for a working reference.

## API Requirements

### Tenant ID

- All API requests require a valid tenant ID in UUID format
- Example tenant ID: `550e8400-e29b-41d4-a716-446655440000`
- The tenant ID must be a valid UUID (32-36 characters)
- This is used for data isolation and access control

### API Endpoints

#### Single URL Scraping

```bash
POST /api/v1/scrapersky

{
    "base_url": "https://example.com",
    "max_pages": 100,
    "tenant_id": "550e8400-e29b-41d4-a716-446655440000"  # Required UUID format
}
```
