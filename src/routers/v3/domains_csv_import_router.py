"""
CSV Import Router for Domains (WO-014).

Implements /api/v3/domains/import-csv endpoint for bulk domain import via CSV.
"""

import csv
import io
from typing import List
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime
import uuid

from src.db.session import get_db_session
from src.auth.jwt_auth import get_current_user
from src.models.domain import (
    Domain,
    SitemapCurationStatusEnum,
)
from src.models.tenant import DEFAULT_TENANT_ID
from src.schemas.csv_import_schemas import CSVImportResponse, CSVRowResult
from src.schemas.domains_direct_submission_schemas import DirectDomainSubmissionRequest

router = APIRouter(prefix="/api/v3/domains", tags=["V3 - Domains CSV Import"])


@router.post("/import-csv", response_model=CSVImportResponse)
async def import_domains_csv(
    file: UploadFile = File(...),
    session: AsyncSession = Depends(get_db_session),
    current_user: dict = Depends(get_current_user),
):
    """
    Import domains from CSV file.

    **CSV Format:**
    - Required column: `domain`
    - No header row required (auto-detected)
    - Max 1000 rows

    **Processing:**
    - Partial success: continues on errors
    - Validates each domain
    - Skips duplicates (already in DB)
    - Deduplicates within CSV

    **Example CSV:**
    ```
    example.com
    testsite.org
    https://www.another-site.com
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
        and first_row[0].lower() in ['domain', 'domains', 'url', 'website']
    )

    data_rows = rows[1:] if has_header else rows

    # Extract domains from first column
    raw_domains = []
    for row in data_rows:
        if row and row[0].strip():  # Skip empty rows
            raw_domains.append(row[0].strip())

    # Normalize and validate using existing schema
    normalized_domains = []
    validation_errors = {}

    for idx, domain_str in enumerate(raw_domains, start=1):
        try:
            # Use existing validation from DirectDomainSubmissionRequest
            request = DirectDomainSubmissionRequest(
                domains=[domain_str],
                auto_queue=False
            )
            normalized_domains.append((idx, request.domains[0]))
        except Exception as e:
            validation_errors[idx] = str(e)

    # Deduplicate within CSV
    seen = set()
    unique_domains = []
    duplicate_rows = set()

    for idx, domain in normalized_domains:
        if domain not in seen:
            seen.add(domain)
            unique_domains.append((idx, domain))
        else:
            duplicate_rows.add(idx)

    # Process domains
    results: List[CSVRowResult] = []
    successful = 0
    failed = 0
    skipped = 0

    async with session.begin():
        for row_num, domain_str in unique_domains:
            # Check if already exists in DB
            existing_check = await session.execute(
                select(Domain).where(Domain.domain == domain_str)
            )
            existing_domain = existing_check.scalar_one_or_none()

            if existing_domain:
                results.append(
                    CSVRowResult(
                        row_number=row_num,
                        value=domain_str,
                        status="skipped",
                        id=existing_domain.id,
                        error="Domain already exists in database",
                    )
                )
                skipped += 1
                continue

            # Create domain
            try:
                domain = Domain(
                    id=uuid.uuid4(),
                    domain=domain_str,
                    tenant_id=uuid.UUID(DEFAULT_TENANT_ID),
                    local_business_id=None,
                    sitemap_curation_status=SitemapCurationStatusEnum.New,
                    sitemap_analysis_status=None,
                    created_at=datetime.utcnow(),
                    updated_at=datetime.utcnow(),
                )
                session.add(domain)
                await session.flush()

                results.append(
                    CSVRowResult(
                        row_number=row_num,
                        value=domain_str,
                        status="success",
                        id=domain.id,
                        error=None,
                    )
                )
                successful += 1
            except Exception as e:
                results.append(
                    CSVRowResult(
                        row_number=row_num,
                        value=domain_str,
                        status="error",
                        id=None,
                        error=f"Database error: {str(e)}",
                    )
                )
                failed += 1

    # Add validation errors to results
    for row_num, error in validation_errors.items():
        results.append(
            CSVRowResult(
                row_number=row_num,
                value=raw_domains[row_num - 1],
                status="error",
                id=None,
                error=error,
            )
        )
        failed += 1

    # Add duplicate rows to results
    for row_num in duplicate_rows:
        # Find the domain value for this row
        domain_value = next(
            (d for idx, d in normalized_domains if idx == row_num),
            raw_domains[row_num - 1]
        )
        results.append(
            CSVRowResult(
                row_number=row_num,
                value=domain_value,
                status="skipped",
                id=None,
                error="Duplicate within CSV (already processed)",
            )
        )
        skipped += 1

    # Sort results by row number
    results.sort(key=lambda x: x.row_number)

    return CSVImportResponse(
        total_rows=len(raw_domains),
        successful=successful,
        failed=failed,
        skipped=skipped,
        results=results,
    )
