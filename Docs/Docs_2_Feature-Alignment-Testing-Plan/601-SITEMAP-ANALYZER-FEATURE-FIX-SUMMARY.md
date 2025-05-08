# Sitemap Analyzer Feature Fix Summary (ContentMap)

## Problem Description

The sitemap analyzer frontend interface was not functioning correctly due to a 403 error with the message "Feature not enabled: sitemap_analyzer". After investigation, we found:

1. The frontend calls this feature "ContentMap" but the backend code was checking for "sitemap_analyzer"
2. The "contentmap" feature already existed in the feature_flags table with ID 2a2f67fd-3ebb-4645-8d48-bf2b5bc7d6c3
3. The feature was not being enabled for the default tenant in development mode
4. There was no development mode bypass for feature checks

## Solutions Implemented

### 1. Code Changes

1. Updated all references in the codebase from "sitemap_analyzer" to "contentmap":
   - Changed feature name used in permission checks
   - Updated environment variable names
   - Renamed utility functions
   - Updated docstrings and comments

2. Created development-mode specific utility functions in `src/routers/modernized_sitemap.py`:
   ```python
   def is_feature_check_disabled() -> bool:
       """
       Checks if feature flag checks should be disabled.
       Used for development and testing environments.
       """
       return (
           os.getenv("DISABLE_PERMISSION_CHECKS", "").lower() == "true" or
           os.getenv("ENABLE_ALL_FEATURES", "").lower() == "true" or
           os.getenv("ENABLE_FEATURE_CONTENTMAP", "").lower() == "true"
       )

   async def require_contentmap_feature(
       tenant_id: str,
       user: Dict,
       session: AsyncSession
   ) -> None:
       """
       Check if contentmap feature is enabled for a tenant.
       This is the feature that powers the sitemap analyzer functionality.
       In development mode, this check is bypassed with a warning.

       Args:
           tenant_id: The tenant ID
           user: The user dictionary containing permissions
           session: Database session
       """
       if is_development_mode() and is_feature_check_disabled():
           logger.warning("⚠️ Feature checks DISABLED for contentmap in development mode ⚠️")
           return

       # Proceed with normal feature check
       user_permissions = user.get("permissions", [])
       await require_feature_enabled(
           tenant_id=tenant_id,
           feature_name="contentmap",
           session=session,
           user_permissions=user_permissions
       )
   ```

### 2. Database Changes

1. Created a database enablement script in `scripts/rbac/enable_contentmap.py`:
   - This script checks if the contentmap feature exists, uses the existing one if present
   - Assigns the feature to the default tenant and enables it

2. No migration was necessary since the contentmap feature already exists in the feature_flags table

### 3. Development Tools

1. Created a convenience script in `scripts/enable_contentmap.sh`:
   - Sets the necessary environment variables for development mode
   - Runs the database enablement script
   - Starts the server with the proper configuration

## Frontend/Backend Feature Mapping

We discovered that the backend and frontend use different naming conventions:

| Backend Name     | Frontend UI Name | Frontend Component  | Description                      |
|------------------|------------------|---------------------|----------------------------------|
| contentmap       | ContentMap       | Not built yet       | Sitemap analyzer for content     |
| google_maps_api  | LocalMiner       | LocalMiner.tsx      | Google Maps scraping tool        |
| batch_page_scraper | N/A            | N/A                 | Batch page scraping functionality|
| frontendscout    | FrontendScout    | DomainStaging.tsx   | Homepage scraping tool           |
| siteharvest      | SiteHarvest      | Not built yet       | Full site scraper               |

The static HTML page at `/static/sitemap-analyzer.html` is a development/testing page, not the final React component which would be called ContentMap.tsx.

## Testing Instructions

1. Run the development script:
   ```bash
   chmod +x scripts/enable_contentmap.sh
   ./scripts/enable_contentmap.sh
   ```

2. Navigate to http://localhost:8000/static/sitemap-analyzer.html

3. Enter a domain and click "Scan"

4. Monitor server logs for any errors or warnings

## Production Rollout

To enable the contentmap feature in production:

1. Verify that the feature exists in the feature_flags table:
   ```sql
   SELECT * FROM feature_flags WHERE name = 'contentmap';
   ```

2. Enable the feature for the required tenants:
   ```sql
   UPDATE tenant_features
   SET is_enabled = TRUE
   WHERE feature_id = '2a2f67fd-3ebb-4645-8d48-bf2b5bc7d6c3'
   AND tenant_id = 'YOUR_TENANT_ID';
   ```

3. Check that the feature is enabled for all required tenants:
   ```sql
   SELECT tf.is_enabled, t.name
   FROM tenant_features tf
   JOIN feature_flags ff ON tf.feature_id = ff.id
   JOIN tenants t ON tf.tenant_id = t.id
   WHERE ff.name = 'contentmap';
   ```
