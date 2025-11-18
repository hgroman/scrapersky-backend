"""
CSV Import Router for Sitemaps (WO-014).

Implements /api/v3/sitemaps/import-csv endpoint for bulk sitemap URL import via CSV.
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
from src.models.sitemap import (
    SitemapFile,
    SitemapImportCurationStatusEnum,
)
from src.models.domain import Domain, SitemapCurationStatusEnum
from src.models.tenant import DEFAULT_TENANT_ID
from src.schemas.csv_import_schemas import CSVImportResponse, CSVRowResult

router = APIRouter(prefix="/api/v3/sitemaps", tags=["V3 - Sitemaps CSV Import"])


def extract_domain_from_sitemap_url(url: str) -> str:
    """Extract domain from sitemap URL."""
    parsed = urlparse(url)
    domain = parsed.netloc
    if domain.startswith("www."):
        domain = domain[4:]
    return domain


@router.post("/import-csv", response_model=CSVImportResponse)
async def import_sitemaps_csv(
    file: UploadFile = File(...),
    session: AsyncSession = Depends(get_db_session),
    current_user: dict = Depends(get_current_user),
):
    """
    Import sitemap URLs from CSV file.

    **CSV Format:**
    - Required column: `sitemap_url` (or `url`)
    - No header row required (auto-detected)
    - Max 1000 rows

    **Processing:**
    - Partial success: continues on errors
    - Validates each sitemap URL (.xml requirement)
    - Skips duplicates (already in DB)
    - Auto-creates domains if needed
    - Sets deep_scrape_curation_status=New, sitemap_type=STANDARD

    **Example CSV:**
    ```
    https://example.com/sitemap.xml
    https://example.com/sitemap_index.xml
    https://testsite.org/sitemap.xml
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
        and first_row[0].lower()
        in ['sitemap_url', 'sitemap', 'url', 'sitemaps', 'sitemap_urls']
    )

    data_rows = rows[1:] if has_header else rows

    # Extract URLs from first column
    raw_urls = []
    for row in data_rows:
        if row and row[0].strip():
            raw_urls.append(row[0].strip())

    # Process sitemap URLs
    results: List[CSVRowResult] = []
    successful = 0
    failed = 0
    skipped = 0

    # Domain cache to avoid repeated lookups/creates
    domain_cache = {}

    async with session.begin():
        for row_num, url_str in enumerate(raw_urls, start=1):
            # Validate sitemap URL format
            try:
                parsed = urlparse(url_str)
                if not parsed.scheme or not parsed.netloc:
                    raise ValueError("Invalid URL format")
                if not (parsed.path.endswith('.xml') or 'sitemap' in parsed.path.lower()):
                    raise ValueError("URL must be a sitemap file (.xml)")
            except Exception as e:
                results.append(
                    CSVRowResult(
                        row_number=row_num,
                        value=url_str,
                        status="error",
                        id=None,
                        error=f"Invalid sitemap URL: {str(e)}",
                    )
                )
                failed += 1
                continue

            # Check if sitemap already exists
            existing_check = await session.execute(
                select(SitemapFile).where(SitemapFile.url == url_str)
            )
            existing_sitemap = existing_check.scalar_one_or_none()

            if existing_sitemap:
                results.append(
                    CSVRowResult(
                        row_number=row_num,
                        value=url_str,
                        status="skipped",
                        id=existing_sitemap.id,
                        error="Sitemap already exists in database",
                    )
                )
                skipped += 1
                continue

            # Get or create domain
            domain_name = extract_domain_from_sitemap_url(url_str)

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

            # Create sitemap
            try:
                sitemap_file = SitemapFile(
                    id=uuid.uuid4(),
                    url=url_str,
                    domain_id=domain.id,
                    deep_scrape_curation_status=SitemapImportCurationStatusEnum.New,
                    sitemap_import_status=None,
                    sitemap_type="STANDARD",
                    url_count=None,
                    last_modified=None,
                    size_bytes=None,
                    created_at=datetime.utcnow(),
                    updated_at=datetime.utcnow(),
                    user_id=current_user.get("user_id"),
                )
                session.add(sitemap_file)
                await session.flush()

                results.append(
                    CSVRowResult(
                        row_number=row_num,
                        value=url_str,
                        status="success",
                        id=sitemap_file.id,
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
