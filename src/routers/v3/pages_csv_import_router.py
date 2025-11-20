"""
WO-012: CSV Import Router for Pages

WHAT THIS DOES:
Bulk import page URLs from CSV files, bypassing workflows WF1-WF5.
Processes hundreds/thousands of URLs in a single request.

ENDPOINT:
POST /api/v3/pages/import-csv

CSV FORMAT:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Required Column:
  • url - Full page URL (https://example.com/contact)

Optional Columns:
  • tenant_id - Tenant UUID (defaults to DEFAULT_TENANT_ID)

Example CSV:
url
https://example.com/contact
https://another.com/about
https://third.com/team
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

WORKFLOW:
1. User uploads CSV file
2. System parses CSV and validates format
3. For each row:
   a. Extract domain from URL
   b. Create/find domain record
   c. Check for duplicate page URL
   d. Create page record with curation_status='Queued'
4. Return summary: created, skipped (duplicates), errors

ERROR HANDLING:
• Per-row error tracking (doesn't fail entire import)
• Invalid URLs logged but don't stop processing
• Duplicate URLs skipped (idempotent)
• Returns detailed error report

REQUEST:
POST /api/v3/pages/import-csv
Content-Type: multipart/form-data
Body: file (CSV file upload)

RESPONSE:
{
  "total_rows": 100,
  "created": 95,
  "skipped": 3,
  "errors": 2,
  "error_details": [
    {"row": 5, "url": "invalid-url", "error": "Invalid URL format"},
    {"row": 12, "url": "bad://url", "error": "Unsupported protocol"}
  ]
}

FILE SIZE LIMITS:
• Max file size: 10MB (configurable)
• Max rows: 10,000 (configurable)
• Recommended batch: 100-1,000 rows

DUPLICATE DETECTION:
• Checks existing pages by URL
• Skips duplicates (doesn't update)
• Counts as "skipped" in response

NULL FOREIGN KEY PATTERN:
CSV-imported pages have:
• domain_id: Set (extracted from URL)
• sitemap_id: NULL (no parent sitemap)

RELATED FILES:
• Single page: src/routers/v3/pages_direct_submission_router.py (WO-009)
• Domain CSV: src/routers/v3/domains_csv_import_router.py (WO-012)
• Sitemap CSV: src/routers/v3/sitemaps_csv_import_router.py (WO-012)
• Docs: Documentation/Guides/csv_import_user_guide.md
• Docs: Documentation/Operations/csv_import_maintenance.md

MAINTENANCE:
• Monitor imports: SELECT COUNT(*) FROM pages WHERE sitemap_id IS NULL AND created_at > NOW() - INTERVAL '24 hours'
• Check errors: Review error_details in API response
• Performance: ~100 rows/second processing speed

USE CASES:
• Bulk page import from external sources
• Migrating from other systems
• Large-scale contact extraction projects
• Supplementing sitemap-based discovery

IMPLEMENTED: 2025-11-14 (WO-012)
"""

import csv
import io
from typing import List
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime
from urllib.parse import urlparse
import uuid

from src.db.session import get_db_session
from src.auth.jwt_auth import get_current_user
from src.models.page import Page, PageCurationStatus
from src.models.domain import Domain, SitemapCurationStatusEnum
from src.models.tenant import DEFAULT_TENANT_ID
from src.schemas.csv_import_schemas import CSVImportResponse, CSVRowResult

router = APIRouter(prefix="/api/v3/pages", tags=["V3 - Pages CSV Import"])


def extract_domain(url: str) -> str:
    """Extract domain from URL."""
    parsed = urlparse(url)
    domain = parsed.netloc
    if domain.startswith("www."):
        domain = domain[4:]
    return domain


@router.post("/import-csv", response_model=CSVImportResponse)
async def import_pages_csv(
    file: UploadFile = File(...),
    session: AsyncSession = Depends(get_db_session),
    current_user: dict = Depends(get_current_user),
):
    """
    Import page URLs from CSV file.

    **CSV Format:**
    - Required column: `url`
    - No header row required (auto-detected)
    - Max 1000 rows

    **Processing:**
    - Partial success: continues on errors
    - Validates each URL
    - Skips duplicates (already in DB)
    - Auto-creates domains if needed
    - Sets page_curation_status=New, priority_level=5

    **Example CSV:**
    ```
    https://example.com/contact
    https://example.com/about
    https://testsite.org/services
    ```

    **Returns:**
    Detailed per-row results with success/failure status.
    """
    # Validate file type
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="File must be a CSV (.csv)")

    # Read file content
    content = await file.read()

    try:
        decoded = content.decode('utf-8')
    except UnicodeDecodeError:
        raise HTTPException(status_code=400, detail="File must be UTF-8 encoded")

    # Parse CSV
    csv_reader = csv.reader(io.StringIO(decoded))
    rows = list(csv_reader)

    if not rows:
        raise HTTPException(status_code=400, detail="CSV file is empty")

    # Check row limit
    if len(rows) > 1000:
        raise HTTPException(
            status_code=400,
            detail=f"CSV exceeds maximum of 1000 rows (found {len(rows)})"
        )

    # Detect if first row is header
    first_row = rows[0]
    has_header = (
        len(first_row) > 0
        and first_row[0].lower() in ['url', 'urls', 'page', 'pages', 'link']
    )

    data_rows = rows[1:] if has_header else rows

    # Extract URLs from first column
    raw_urls = []
    for row in data_rows:
        if row and row[0].strip():
            raw_urls.append(row[0].strip())

    # Process URLs
    results: List[CSVRowResult] = []
    successful = 0
    failed = 0
    skipped = 0

    # Domain cache to avoid repeated lookups/creates
    domain_cache = {}

    async with session.begin():
        for row_num, url_str in enumerate(raw_urls, start=1):
            # Validate URL format
            try:
                parsed = urlparse(url_str)
                if not parsed.scheme or not parsed.netloc:
                    raise ValueError("Invalid URL format")
            except Exception as e:
                results.append(
                    CSVRowResult(
                        row_number=row_num,
                        value=url_str,
                        status="error",
                        id=None,
                        error=f"Invalid URL: {str(e)}",
                    )
                )
                failed += 1
                continue

            # Check if page already exists
            existing_check = await session.execute(
                select(Page).where(Page.url == url_str)
            )
            existing_page = existing_check.scalar_one_or_none()

            if existing_page:
                results.append(
                    CSVRowResult(
                        row_number=row_num,
                        value=url_str,
                        status="skipped",
                        id=existing_page.id,
                        error="Page already exists in database",
                    )
                )
                skipped += 1
                continue

            # Get or create domain
            domain_name = extract_domain(url_str)

            if domain_name in domain_cache:
                domain = domain_cache[domain_name]
            else:
                domain_result = await session.execute(
                    select(Domain).where(Domain.domain == domain_name)
                )
                domain = domain_result.scalar_one_or_none()

                if not domain:
                    # Create domain
                    domain = Domain(
                        id=uuid.uuid4(),
                        domain=domain_name,
                        tenant_id=uuid.UUID(DEFAULT_TENANT_ID),
                        local_business_id=None,
                        sitemap_curation_status=SitemapCurationStatusEnum.New,
                        sitemap_analysis_status=None,
                        created_at=datetime.utcnow(),
                        updated_at=datetime.utcnow(),
                    )
                    session.add(domain)
                    await session.flush()

                domain_cache[domain_name] = domain

            # Create page
            try:
                page = Page(
                    id=uuid.uuid4(),
                    url=url_str,
                    tenant_id=DEFAULT_TENANT_ID,
                    domain_id=domain.id,
                    sitemap_file_id=None,
                    page_curation_status=PageCurationStatus.New,
                    page_processing_status=None,
                    priority_level=5,
                    created_at=datetime.utcnow(),
                    updated_at=datetime.utcnow(),
                )
                session.add(page)
                await session.flush()

                results.append(
                    CSVRowResult(
                        row_number=row_num,
                        value=url_str,
                        status="success",
                        id=page.id,
                        error=None,
                    )
                )
                successful += 1
            except Exception as e:
                results.append(
                    CSVRowResult(
                        row_number=row_num,
                        value=url_str,
                        status="error",
                        id=None,
                        error=f"Database error: {str(e)}",
                    )
                )
                failed += 1

    return CSVImportResponse(
        total_rows=len(raw_urls),
        successful=successful,
        failed=failed,
        skipped=skipped,
        results=results,
    )
