# Frontend/Backend Naming Convention Guide

## Overview

This document provides a comprehensive guide to the naming conventions used across the ScraperSky platform. There is a **critical mismatch between frontend and backend feature names** that must be understood when working on the codebase.

## Feature Naming Mapping

| Backend Name (Code) | Database Name (feature_flags) | Frontend UI Name | Frontend Component | Description |
|---------------------|------------------------------|------------------|-------------------|-------------|
| contentmap          | contentmap                   | ContentMap       | Not built yet     | Sitemap analyzer for content structure |
| google_maps_api     | localminer                   | LocalMiner       | LocalMiner.tsx    | Google Maps scraping and analysis tool |
| batch_page_scraper  | N/A                          | N/A              | N/A               | Batch page scraping functionality |
| frontendscout       | frontendscout                | FrontendScout    | DomainStaging.tsx | Homepage scraping and insights |
| siteharvest         | siteharvest                  | SiteHarvest      | Not built yet     | Full-site scraper for deeper data |
| emailhunter         | emailhunter                  | EmailHunter      | Not built yet     | Email scraping tool |
| actionqueue         | actionqueue                  | ActionQueue      | Not built yet     | Follow-up queue manager |
| socialradar         | socialradar                  | SocialRadar      | SocialStaging.tsx | Social media scraping & lead gen |
| contactlaunchpad    | contactlaunchpad             | ContactLaunchpad | ContactStaging.tsx| Contact staging & management |

## Static HTML Pages vs React Components

The static HTML pages used for development and testing have different naming conventions than the final React components:

| Static HTML Page | Associated Feature | Intended React Component | Current Status |
|------------------|-------------------|--------------------------|----------------|
| sitemap-analyzer.html | contentmap | ContentMap.tsx | Not built yet |
| google-maps.html | localminer | LocalMiner.tsx | Built |
| batch-domain-scanner.html | batch_page_scraper | N/A | N/A |
| single-domain-scanner.html | frontendscout | DomainStaging.tsx | Built |

## Critical Implementation Notes

1. **Permission Checks**: When implementing RBAC permissions for a feature, you MUST use the correct backend name in the code:
   ```python
   # CORRECT:
   await require_feature_enabled(tenant_id, "contentmap", session)
   
   # INCORRECT:
   await require_feature_enabled(tenant_id, "sitemap_analyzer", session)
   ```

2. **Database Records**: All feature flags must be registered in the database using the names from the "Database Name" column.

3. **Feature Map Constant**: The `FEATURE_MAP` dictionary in `src/constants/rbac.py` must correctly map backend feature names to frontend identifiers:
   ```python
   FEATURE_MAP = {
       "google_maps_api": "localminer",
       "batch_page_scraper": "discovery-scan",
       "contentmap": "deep-analysis",
       # and so on...
   }
   ```

4. **Environment Variables**: Development mode environment variables should use the backend code names:
   ```bash
   export ENABLE_FEATURE_CONTENTMAP=true  # Correct
   export ENABLE_FEATURE_SITEMAP_ANALYZER=true  # Incorrect
   ```

## Common Pitfalls

1. **"sitemap_analyzer" vs "contentmap"**: The most common error is using "sitemap_analyzer" in the code when the feature is actually named "contentmap" in the database. This will result in 403 errors with "Feature not enabled" messages.

2. **Static HTML vs React Components**: The static HTML pages (e.g., sitemap-analyzer.html) are for development/testing only and do not reflect the final React component names.

3. **Inconsistent Naming in API Endpoints**: Some API endpoints may still use older naming conventions. Always verify the actual endpoint path in the router definitions.

## How to Fix Naming Inconsistencies

If you encounter a naming inconsistency (e.g., a feature doesn't work due to name mismatch):

1. **NEVER** create a new feature in the database - check if it already exists with a different name
2. Update the code to match the database name, not vice versa
3. Document the mapping in this guide
4. Rename static HTML pages to match the frontend naming conventions
5. Update all references in other files to maintain consistency

## Database Feature Flag Entries

```sql
-- Reference: Current entries in the feature_flags table (as of March 2024)
SELECT id, name, description FROM feature_flags;
```

| ID | Name | Description |
|----|------|-------------|
| 2a2f67fd-3ebb-4645-8d48-bf2b5bc7d6c3 | contentmap | Sitemap analyzer for content structure |
| 38c4fa76-738b-4a21-a9e5-b9617feeac8b | actionqueue | Follow-up queue manager |
| 62dd4c91-315f-43dc-ba91-68011f824fa9 | siteharvest | Full-site scraper for deeper data |
| 6e754353-7df4-4e5c-b13a-8d25f60e1937 | localminer | Google Maps scraping and analysis tool |
| 6e81a6a4-6522-434c-872f-17b7a34204f4 | socialradar | Social media scraping & lead gen |
| 6e8e70af-0783-4671-84fe-9b1ab7805526 | emailhunter | Email scraping tool |
| 862bcc06-30c5-46bd-a374-2b2e6c25c02f | frontendscout | Homepage scraping and insights |
| f9fedb56-6e81-4c02-ab6e-38eb30432148 | contactlaunchpad | Contact staging & management |