# Router Layer Remediation & Compliance Guide

## 1. Mandate

This document provides the official guidance for the API/Router team following the foundational Layer 1 refactoring. The router layer underwent the most significant architectural changes. The core code has already been refactored for compliance. The purpose of this guide is to ensure every team member understands the new, non-negotiable patterns for defining API schemas and handling data contracts.

## 2. The Core Changes: A Three-Part Refactor

The router layer was affected by three major architectural improvements that must be understood and adopted.

### Change 1: Decommissioning of `api_models.py`

-   **The Anti-Pattern (Now Eliminated):** A monolithic file at `src/models/api_models.py` served as a dumping ground for Pydantic schemas. This violated the separation of concerns.
-   **The Golden Path (New Standard):** This file has been **deleted**. No code should ever reference it again. All API schemas now have a dedicated home.

### Change 2: The New Schema Layer (`src/schemas`)

-   **The Anti-Pattern (Now Eliminated):** Schemas were defined in `api_models.py` or, even worse, directly inside router files.
-   **The Golden Path (New Standard):** A new `src/schemas` directory is now the **single source of truth for all Pydantic API models.** Each data domain has its own file (e.g., `src/schemas/domain.py`). Routers MUST import all request and response models from this directory.

### Change 3: Centralized ENUMs

-   **The Anti-Pattern (Now Eliminated):** Routers imported ENUMs from various model files and contained fragile logic to map them.
-   **The Golden Path (New Standard):** Routers, like all other layers, MUST import ENUMs directly from `src/models/enums.py`. This eliminates the need for mapping logic.

## 3. Review of Remediated Files

I have already refactored the following routers and created their corresponding schemas. **Your team's responsibility is to review these changes to understand the new, mandatory workflow.**

-   **Routers Changed:**
    -   `src/routers/domains.py`
    -   `src/routers/local_businesses.py`
    -   `src/routers/sitemap_files.py`
    -   `src/routers/batch_sitemap.py`

-   **New Schemas to Review:**
    -   `src/schemas/domain.py`
    -   `src/schemas/local_business.py`
    -   `src/schemas/sitemap_file.py`

### Example of the Change (`domains.py` router):

-   **BEFORE:**
    ```python
    from src.models.api_models import DomainRecord # From the monolith
    from src.models.domain import SitemapCurationStatusEnum # Local ENUM
    # ... router logic with manual ENUM mapping ...
    ```

-   **AFTER:**
    ```python
    from src.schemas.domain import DomainRecord # From the new schema layer
    from src.models.enums import SitemapCurationStatus # From the centralized ENUMs
    # ... router logic is now simpler, no mapping needed ...
    ```

## 4. Path Forward: Responsibilities & Mandates

1.  **No New Violations:** All new API endpoints and schemas MUST follow this pattern. Creating schemas anywhere but `src/schemas` or importing ENUMs from anywhere but `src/models/enums.py` is a direct violation of the architecture.
2.  **Code Reviews:** This three-part pattern is the most critical standard to enforce during API code reviews. Pull requests that do not adhere to it must be rejected.
3.  **Verification:** After the database and test suite are remediated, the router team should perform end-to-end testing (e.g., using Swagger UI or `curl`) to validate that all refactored endpoints behave as expected with the new schemas and ENUMs.

Adherence to this structure is essential for maintaining a decoupled, scalable, and maintainable API layer.
