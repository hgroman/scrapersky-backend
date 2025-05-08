# Legacy Routers Inventory and Classification

## Overview

This document provides a detailed inventory and classification of legacy routers in the ScraperSky backend. Based on our analysis of the codebase, we have identified several legacy routers that require standardization or deprecation.

## Inventory and Classification

| Router | File Path | Modernized Version | Current Usage | Classification |
|--------|-----------|-------------------|--------------|----------------|
| `page_scraper_router` | `/src/routers/page_scraper.py` | `modernized_page_scraper.py` | Used in `single-domain-scanner.html` | **Category A: Deprecate and Redirect** |
| `sitemap_router` | `/src/routers/sitemap.py` | `modernized_sitemap.py` | No direct frontend usage found | **Category D: Obsolete** |

## Detailed Analysis

### 1. Page Scraper Router (`/src/routers/page_scraper.py`)

**Classification: Category A (Deprecate and Redirect)**

- **Usage Level**: Low - Used only in `single-domain-scanner.html`
- **Modernization Status**: Yes - Replaced by `modernized_page_scraper.py`
- **Technical Debt**: Medium - Simple router with minimal functionality

**Implementation Plan**:
1. Add deprecation notices in comments and docstrings
2. Add deprecation warning logs on each endpoint
3. Implement redirection to modern endpoints
4. Update documentation to indicate deprecation
5. Do not modify core functionality or add transaction boundaries

### 2. Sitemap Router (`/src/routers/sitemap.py`)

**Classification: Category D (Obsolete)**

- **Usage Level**: None - No direct frontend usage found
- **Modernization Status**: Yes - Replaced by `modernized_sitemap.py`
- **Technical Debt**: Low - Only has a health check endpoint

**Implementation Plan**:
1. Add obsolete notice in comments and docstrings
2. Add "TO-DO: Remove in version X" comments
3. Add warning logs indicating obsolescence
4. Do not modify core functionality

## Summary of Actions

Based on this classification, we will implement the following standardization approach:

### Page Scraper Router

1. Add deprecation notices:
   ```python
   """
   DEPRECATED: This module is deprecated and will be removed in version 4.0.
   Use modernized_page_scraper.py instead.
   """
   ```

2. Add deprecation warning logs on each endpoint:
   ```python
   logger.warning("DEPRECATED ENDPOINT: This endpoint is deprecated and will be removed in version 4.0. Use /api/v3/batch_page_scraper instead.")
   ```

3. Implement redirection where possible:
   ```python
   return RedirectResponse(url=f"/api/v3/batch_page_scraper/scan?{urlencode(data)}")
   ```

4. Do not modify core functionality or add transaction boundaries

### Sitemap Router

1. Add obsolete notice:
   ```python
   """
   OBSOLETE: This module is obsolete and will be removed in version 4.0.
   It has been replaced by modernized_sitemap.py.
   TO-DO: Remove in version 4.0
   """
   ```

2. Add warning logs:
   ```python
   logger.warning("OBSOLETE ENDPOINT: This endpoint is obsolete and will be removed in version 4.0.")
   ```

3. Do not modify core functionality

## Next Steps

1. Implement the changes outlined above
2. Update API documentation to reflect the deprecation/obsolescence status
3. Create a migration guide for frontend developers to move to the new endpoints
4. Set a timeline for removal in version 4.0
