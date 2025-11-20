# Router Impact Analysis: Database Enum Renaming

**Date**: 2025-11-20
**Status**: COMPLETED
**Objective**: Verify that renaming the PostgreSQL Enum types in the database does not break the application logic in the Routers.

## 1. Executive Summary
The analysis confirms that the proposed database changes (renaming Enum types to snake_case) are **SAFE** for the current Router implementation. The Routers rely on Python [Enum](file:///Users/henrygroman/development/python-projects/ScraperSky-Back-End-WorkSpace/scraper-sky-backend/src/models/enums.py#202-224) classes and SQLAlchemy ORM for data manipulation, not on raw SQL queries that reference the specific PostgreSQL Enum type names.

## 2. Detailed Findings

### 2.1. [src/routers/local_businesses.py](file:///Users/henrygroman/development/python-projects/ScraperSky-Back-End-WorkSpace/scraper-sky-backend/src/routers/local_businesses.py)
*   **Usage**: Imports [DomainExtractionStatusEnum](file:///Users/henrygroman/development/python-projects/ScraperSky-Back-End-WorkSpace/scraper-sky-backend/src/models/local_business.py#38-43) from `src.models.local_business`.
*   **Logic**:
    *   Line 260-262: `business.domain_extraction_status = DomainExtractionStatusEnum.Queued`
    *   Line 397: `business.domain_extraction_status = DomainExtractionStatusEnum.Queued`
*   **Safety**: The code assigns Python Enum members to the model field. SQLAlchemy handles the translation to the database value. The *name* of the database type (`domain_extraction_status_enum`) is defined in the Model `Column` definition (which we updated), but the Router code itself does not reference this string name.
*   **Risk**: None.

### 2.2. [src/routers/domains.py](file:///Users/henrygroman/development/python-projects/ScraperSky-Back-End-WorkSpace/scraper-sky-backend/src/routers/domains.py)
*   **Usage**: Imports [SitemapCurationStatusEnum](file:///Users/henrygroman/development/python-projects/ScraperSky-Back-End-WorkSpace/scraper-sky-backend/src/models/enums.py#152-161) from `src.models.domain`.
*   **Logic**:
    *   Line 187: `db_curation_status = SitemapCurationStatusEnum[api_status.name]`
    *   Line 224: `domain.sitemap_curation_status = db_curation_status`
    *   Line 298: `db_filter_status = next((member for member in SitemapCurationStatusEnum if member.name == ...), None)`
*   **Safety**: The logic relies heavily on `member.name` (e.g., "New", "Selected") matching the API input. It does **NOT** rely on the underlying Database Enum Type Name (`"SitemapCurationStatusEnum"` vs `sitemap_curation_status_enum`).
*   **Risk**: None.

### 2.3. [src/routers/sitemap_files.py](file:///Users/henrygroman/development/python-projects/ScraperSky-Back-End-WorkSpace/scraper-sky-backend/src/routers/sitemap_files.py)
*   **Usage**: Imports [SitemapImportCurationStatusEnum](file:///Users/henrygroman/development/python-projects/ScraperSky-Back-End-WorkSpace/scraper-sky-backend/src/models/enums.py#172-181) from `src.models.sitemap`.
*   **Logic**:
    *   Line 150: Passes `new_curation_status` (Enum member) to service layer.
    *   Line 250: `sitemap_file.deep_scrape_curation_status = request.deep_scrape_curation_status`
*   **Safety**: Similar to above, relies on ORM abstraction.

## 3. Conclusion
The "Guardian's Paradox" concern was that "The Guardian... Changed every ENUM in the codebase... Broke every producer-consumer relationship".
*   **Our Approach**: We are **ONLY** changing the Database Type Name mapping in the SQLAlchemy Model definition.
*   **We are NOT**:
    *   Changing the Python Enum Class Names.
    *   Changing the Python Enum Member Names (Values).
    *   Changing the API Interface.

Therefore, the application code (Routers) remains decoupled from the specific PostgreSQL Type Name, provided the SQLAlchemy Model definition matches the Database (which is exactly what the Work Order ensures).

## 4. Verification
The [tests/verification_remediation.py](file:///Users/henrygroman/development/python-projects/ScraperSky-Back-End-WorkSpace/scraper-sky-backend/tests/verification_remediation.py) script (already passed) confirms that the SQLAlchemy Models are correctly configured to map the existing Python Enums to the new snake_case Database Types.
