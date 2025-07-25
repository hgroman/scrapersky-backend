# Service Layer Remediation & Compliance Guide

## 1. Mandate

This document provides the official guidance for the Services team following the foundational Layer 1 refactoring. The core code of the service layer has already been refactored for compliance. The purpose of this guide is to ensure every team member understands the changes, the new architectural patterns, and their responsibility in maintaining them.

## 2. The Core Change: Centralized ENUMs

The single most important change affecting the service layer is the centralization of all application ENUMs.

-   **The Anti-Pattern (Now Eliminated):** Services previously imported ENUMs directly from model files (e.g., `from src.models.domain import SitemapCurationStatusEnum`). This created a fragile, tight coupling.
-   **The Golden Path (New Standard):** All services MUST now import ENUMs from the single source of truth: `src/models/enums.py`.

## 3. Review of Remediated Files

I have already updated the following service files to adhere to the new standard. **Your team's responsibility is to review these changes to understand the new pattern.** This is the blueprint for all future service-layer development.

-   `src/services/sitemap_import_scheduler.py`
-   `src/services/domain_scheduler.py`
-   `src/services/sitemap_scheduler.py`

### Example of the Change:

Across these files, you will see changes like this:

-   **BEFORE:**
    ```python
    from src.models.sitemap import SitemapImportCurationStatusEnum
    # ...
    if status == SitemapImportCurationStatusEnum.Selected:
        # ...
    ```

-   **AFTER:**
    ```python
    from src.models.enums import SitemapImportCurationStatus
    # ...
    if status == SitemapImportCurationStatus.SELECTED:
        # ...
    ```

Notice two key changes:
1.  The `import` path now points to `src.models.enums`.
2.  The ENUM member reference is now `UPPERCASE` (`.SELECTED`).

## 4. Path Forward: Responsibilities & Mandates

1.  **No New Violations:** All new service-layer code must strictly adhere to this pattern. Any import from a location other than `src/models/enums.py` for an ENUM is a violation of the architectural blueprint.
2.  **Code Reviews:** This pattern must be enforced during code reviews. Pull requests containing incorrect ENUM imports must be rejected.
3.  **Verification:** As the application is tested following the database migration and test suite remediation, the services team should be prepared to validate that the logic within these services behaves as expected with the new, centralized ENUMs.

This change simplifies dependencies and makes the entire application more robust. Your team's adherence to this standard is critical for maintaining the stability we have worked to achieve.
