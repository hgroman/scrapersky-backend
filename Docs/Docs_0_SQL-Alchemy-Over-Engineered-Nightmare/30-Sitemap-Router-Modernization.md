# Sitemap Router Modernization

## Overview

This document tracks the modernization of the legacy sitemap scraper router to use the new router factory pattern.

## Key Components

### 1. Router Factory

The router factory (`RouterFactory`) provides a standardized way to create FastAPI routes with consistent:

- Error handling
- Parameter validation
- Authentication
- Response formatting
- Background task processing

### 2. Sitemap Service

We've created a dedicated sitemap service (`SitemapService`) that encapsulates the business logic previously embedded in the router functions. This provides:

- Better separation of concerns
- Testability
- Reusability
- Type safety

### 3. Modernized Sitemap Router

The modernized sitemap router (`modernized_sitemap.py`) demonstrates how to use the router factory pattern to create standardized routes. It:

- Imports the necessary dependencies
- Creates a router with appropriate prefix and tags
- Uses the router factory to create standardized GET and POST routes
- References the sitemap service for business logic

## Endpoints Modernized

### Phase 1 (Current)

1. **GET /sitemap/status/{job_id}**

   - Gets the status of a sitemap scanning job
   - Simplified from original `/status/{job_id}` endpoint

2. **POST /sitemap/scan**
   - Initiates a domain scan
   - Simplified from original `/scrapersky` endpoint

### Phase 2 (Upcoming)

3. **POST /sitemap/batch**

   - For batch scanning multiple domains
   - Will replace `/batch` endpoint

4. **GET /sitemap/batch/{batch_id}/status**

   - For checking batch job status
   - Will replace `/batch/{batch_id}/status` endpoint

5. **Debug/Test Endpoints**
   - Will modernize test endpoints as needed

## Implementation Process

1. **Create Core Services**

   - AuthService: Handles authentication and authorization
   - ValidationService: Validates input parameters
   - ErrorService: Standardizes error handling

2. **Extract Business Logic to Services**

   - SitemapService: Handles sitemap scanning and processing

3. **Create Modernized Router**

   - Using router factory to standardize endpoint creation

4. **Modernize Endpoints Incrementally**
   - Start with core endpoints
   - Add remaining endpoints over time
   - Maintain backward compatibility during transition

## Benefits

1. **Standardization**

   - Consistent endpoint structure
   - Standardized error responses
   - Simplified route definition

2. **Separation of Concerns**

   - Business logic in services
   - Route definition separate from implementation
   - Easier to maintain and test

3. **Type Safety**
   - Better typing throughout
   - Consistent interface for all endpoints
   - Reduced chance of runtime errors

## Next Steps

1. Continue modernizing remaining endpoints in sitemap_scraper.py
2. Apply router factory pattern to other routers
3. Create service classes for remaining business logic
4. Enhance testing for modernized endpoints
