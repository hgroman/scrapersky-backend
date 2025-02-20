Below is a revised version of your README that reflects your current workflow and technology choices. I've replaced references to BigQuery with Supabase, updated the project structure accordingly, and highlighted your modern deployment workflow with Vercel and Lovable.dev.

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

| Endpoint                        | Method | Purpose                             | Example                                                                 |
|---------------------------------|--------|-------------------------------------|-------------------------------------------------------------------------|
| `/api/v1/scrapersky_endpoint`   | POST   | Scan website metadata               | `curl -X POST http://localhost:8000/api/v1/scrapersky_endpoint -d '{"base_url":"https://example.com", "max_pages": 100}'` |
| `/api/v1/status/{job_id}`      | GET    | Get scan status                     | `curl http://localhost:8000/api/v1/status/scan_123`                      |
| `/chat`                         | POST   | Chat with the AI (OpenAI integration)| `curl -X POST http://localhost:8000/chat -H "Content-Type: application/json" -d '{"message":"Hello"}'`  |
| `/email-scanner/domains`        | GET    | List available domains for scanning | `curl http://localhost:8000/email-scanner/domains`                        |
| `/email-scanner/scan/{domain_id}` | POST | Start scanning a domain for emails  | `curl -X POST http://localhost:8000/email-scanner/scan/1 -H "Content-Type: application/json"`  |
| `/email-scanner/scan/{domain_id}/status` | GET | Check email scanning status | `curl http://localhost:8000/email-scanner/scan/1/status`                  |

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
- `OPENAI_API_KEY`: OpenAI API key for chat functionality.
- `SCRAPER_API_KEY`: Key for ScraperAPI.
- `SUPABASE_URL`: Your Supabase project URL.
- `SUPABASE_SERVICE_ROLE_KEY`: Service role key for Supabase.
- `SUPABASE_ANON_KEY`: Anonymous key for Supabase.
- `SUPABASE_DB_PASSWORD`: Database password for Supabase.
- `USER_AGENT`: Custom user agent string for HTTP requests (optional).

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

## Contributing

1. Create a feature branch.
2. Add new functionality in the appropriate modules.
3. Update documentation.
4. Submit a pull request.

## License

MIT

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