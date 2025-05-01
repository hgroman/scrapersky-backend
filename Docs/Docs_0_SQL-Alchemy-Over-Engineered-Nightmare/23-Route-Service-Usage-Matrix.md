# ScraperSky Route-Service Usage Matrix

This document provides a comprehensive inventory of routes in the ScraperSky application, their service dependencies, and migration prioritization. Since backward compatibility is not a priority, this analysis focuses on forward-looking modernization without legacy support.

## Route Inventory Overview

| Route File         | Path Pattern                          | Primary Purpose                      | Service Architecture    |
| ------------------ | ------------------------------------- | ------------------------------------ | ----------------------- |
| sitemap_scraper.py | `/api/v1/scrapersky`, `/api/v1/batch` | Domain scanning and batch processing | Mixed (Modern + Legacy) |
| domain_manager.py  | `/api/v1/domains`                     | Domain CRUD operations               | Mixed (Modern + Legacy) |
| batch_processor.py | `/api/v1/batch/*`                     | Batch job management                 | Mixed (Modern + Legacy) |
| analytics.py       | `/api/v1/analytics/*`                 | Analytics and reporting              | Mostly Legacy           |
| export.py          | `/api/v1/export/*`                    | Data export operations               | Mostly Legacy           |
| user_management.py | `/api/v1/users/*`                     | User management                      | Mostly Legacy           |
| admin.py           | `/api/v1/admin/*`                     | Administrative operations            | Mostly Legacy           |

## Detailed Route-Service Matrix

Below is a detailed matrix showing which services are used by each route and the current implementation status.

### Core Services

| Route File         | auth_service     | user_context_service | db_service       | error_service    | validation_service |
| ------------------ | ---------------- | -------------------- | ---------------- | ---------------- | ------------------ |
| sitemap_scraper.py | ✅ Used (Legacy) | ✅ Used (Legacy)     | ✅ Used (Legacy) | ✅ Used (Legacy) | ✅ Used (Legacy)   |
| domain_manager.py  | ✅ Used (Legacy) | ✅ Used (Legacy)     | ✅ Used (Legacy) | ✅ Used (Legacy) | ✅ Used (Legacy)   |
| batch_processor.py | ✅ Used (Legacy) | ✅ Used (Legacy)     | ✅ Used (Legacy) | ✅ Used (Legacy) | ✅ Used (Legacy)   |
| analytics.py       | ✅ Used (Legacy) | ✅ Used (Legacy)     | ✅ Used (Legacy) | ✅ Used (Legacy) | ❌ Not Used        |
| export.py          | ✅ Used (Legacy) | ✅ Used (Legacy)     | ✅ Used (Legacy) | ✅ Used (Legacy) | ✅ Used (Legacy)   |
| user_management.py | ✅ Used (Legacy) | ✅ Used (Legacy)     | ✅ Used (Legacy) | ✅ Used (Legacy) | ✅ Used (Legacy)   |
| admin.py           | ✅ Used (Legacy) | ✅ Used (Legacy)     | ✅ Used (Legacy) | ✅ Used (Legacy) | ✅ Used (Legacy)   |

### Domain Services

| Route File         | domain_service   | job_service     | storage_service  | sitemap_service  |
| ------------------ | ---------------- | --------------- | ---------------- | ---------------- |
| sitemap_scraper.py | ✅ Used (Modern) | ✅ Used (Mixed) | ❌ Not Used      | ✅ Used (Legacy) |
| domain_manager.py  | ✅ Used (Modern) | ✅ Used (Mixed) | ❌ Not Used      | ❌ Not Used      |
| batch_processor.py | ✅ Used (Modern) | ✅ Used (Mixed) | ❌ Not Used      | ✅ Used (Legacy) |
| analytics.py       | ✅ Used (Modern) | ❌ Not Used     | ❌ Not Used      | ❌ Not Used      |
| export.py          | ✅ Used (Modern) | ❌ Not Used     | ✅ Used (Legacy) | ❌ Not Used      |
| user_management.py | ❌ Not Used      | ❌ Not Used     | ❌ Not Used      | ❌ Not Used      |
| admin.py           | ✅ Used (Modern) | ✅ Used (Mixed) | ❌ Not Used      | ❌ Not Used      |

### Process Services

| Route File         | batch_processor_service | scrape_executor_service | analytics_service | export_service   | report_service   |
| ------------------ | ----------------------- | ----------------------- | ----------------- | ---------------- | ---------------- |
| sitemap_scraper.py | ✅ Used (Mixed)         | ✅ Used (Legacy)        | ❌ Not Used       | ❌ Not Used      | ❌ Not Used      |
| domain_manager.py  | ✅ Used (Mixed)         | ❌ Not Used             | ❌ Not Used       | ❌ Not Used      | ❌ Not Used      |
| batch_processor.py | ✅ Used (Mixed)         | ✅ Used (Legacy)        | ❌ Not Used       | ❌ Not Used      | ❌ Not Used      |
| analytics.py       | ❌ Not Used             | ❌ Not Used             | ✅ Used (Legacy)  | ❌ Not Used      | ✅ Used (Legacy) |
| export.py          | ❌ Not Used             | ❌ Not Used             | ✅ Used (Legacy)  | ✅ Used (Legacy) | ✅ Used (Legacy) |
| user_management.py | ❌ Not Used             | ❌ Not Used             | ❌ Not Used       | ❌ Not Used      | ❌ Not Used      |
| admin.py           | ✅ Used (Mixed)         | ❌ Not Used             | ✅ Used (Legacy)  | ❌ Not Used      | ✅ Used (Legacy) |

### API Services

| Route File         | api_service      | webhook_service  | notification_service |
| ------------------ | ---------------- | ---------------- | -------------------- |
| sitemap_scraper.py | ❌ Not Used      | ❌ Not Used      | ❌ Not Used          |
| domain_manager.py  | ✅ Used (Legacy) | ✅ Used (Legacy) | ✅ Used (Legacy)     |
| batch_processor.py | ❌ Not Used      | ❌ Not Used      | ✅ Used (Legacy)     |
| analytics.py       | ✅ Used (Legacy) | ❌ Not Used      | ❌ Not Used          |
| export.py          | ❌ Not Used      | ❌ Not Used      | ✅ Used (Legacy)     |
| user_management.py | ✅ Used (Legacy) | ❌ Not Used      | ✅ Used (Legacy)     |
| admin.py           | ✅ Used (Legacy) | ✅ Used (Legacy) | ✅ Used (Legacy)     |

## Direct Database Access Analysis

The following routes have direct database access that bypasses the service layer:

| Route File         | Direct DB Operations    | SQL Queries | SQLAlchemy Direct | Priority for Migration |
| ------------------ | ----------------------- | ----------- | ----------------- | ---------------------- |
| sitemap_scraper.py | High (10+ instances)    | Yes         | Yes               | High                   |
| domain_manager.py  | Medium (5-10 instances) | Yes         | Yes               | High                   |
| batch_processor.py | Medium (5-10 instances) | Yes         | Yes               | High                   |
| analytics.py       | High (10+ instances)    | Yes         | No                | Medium                 |
| export.py          | Medium (5-10 instances) | Yes         | No                | Medium                 |
| user_management.py | Low (1-5 instances)     | Yes         | No                | Low                    |
| admin.py           | Medium (5-10 instances) | Yes         | Yes               | Medium                 |

## Route Migration Prioritization

Based on the analysis above, the following prioritization is recommended for route modernization:

### Phase 1 (Weeks 4-6)

1. **sitemap_scraper.py** - Highest priority due to:

   - Heavy usage of multiple services
   - Mix of modern and legacy patterns
   - High number of direct database operations
   - Central to core functionality

2. **domain_manager.py** - Second priority due to:

   - Dependency on domain_service (already modernized)
   - Direct database access
   - Key functionality for domain management

3. **batch_processor.py** - Third priority due to:
   - Related to sitemap_scraper.py functionality
   - Shares many service dependencies with sitemap_scraper.py
   - Would benefit from batch_processor_service modernization

### Phase 2 (Weeks 7-9)

4. **admin.py** - Fourth priority due to:

   - Moderate usage of various services
   - Administrative functionality impact

5. **analytics.py** - Fifth priority due to:
   - Heavy dependency on analytics_service
   - Less critical to core functionality

### Phase 3 (Weeks 10-12)

6. **export.py** - Sixth priority due to:

   - Specialized export functionality
   - Dependency on export_service and storage_service

7. **user_management.py** - Lowest priority due to:
   - Simple CRUD operations
   - Less integration with other services
   - Lower rate of change

## Service Impact Analysis

Modernizing these services will have the most significant impact across routes:

1. **auth_service** - Used by all routes (100%)
2. **db_service** - Used by all routes (100%)
3. **error_service** - Used by all routes (100%)
4. **user_context_service** - Used by all routes (100%)
5. **domain_service** - Used by 6/7 routes (86%)
6. **job_service** - Used by 4/7 routes (57%)
7. **batch_processor_service** - Used by 4/7 routes (57%)

## Route Modernization Approach

For each route, the modernization should follow this pattern:

1. **Service Usage Standardization**:

   - Update service imports to use the correct namespaced imports
   - Replace legacy service methods with SQLAlchemy-based methods
   - Remove any in-memory state tracking

2. **Database Access Elimination**:

   - Identify all direct database operations
   - Move these operations to appropriate service methods
   - Update route to call service methods instead

3. **Error Handling Standardization**:

   - Replace manual try/except blocks with error_service
   - Ensure consistent error response format
   - Add appropriate context to error handling

4. **Function Refactoring**:
   - Break down large route handler functions
   - Extract common functionality into helper functions
   - Ensure single responsibility for each function

## Conclusion

This route-service usage matrix provides a clear roadmap for modernizing the ScraperSky application routes. By focusing on forward-looking modernization without backward compatibility concerns, we can efficiently transform the codebase to use consistent SQLAlchemy ORM patterns across all routes and services.

The phased approach prioritizes routes based on their impact on core functionality and their complexity of service usage. By tackling the most critical routes first (sitemap_scraper.py, domain_manager.py, batch_processor.py), we can establish patterns that will accelerate the modernization of the remaining routes.

Since backward compatibility is not a concern, we can implement clean, modern patterns without compromise, resulting in a more maintainable and consistent codebase.
