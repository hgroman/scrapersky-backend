# Modernized Page Scraper Fix Work Order - 2025-03-26

## Overview

This document outlines the necessary changes to fix linter errors and standardize the Modernized Page Scraper implementation according to our core architectural principles. This follows the successful standardization of the Google Maps API implementation.

> **NOTE:** This work order should be implemented following the standardization template documented in [07-29-GOOGLE-MAPS-API-STANDARDIZATION-TEMPLATE.md](/project-docs/07-database-connection-audit/07-29-GOOGLE-MAPS-API-STANDARDIZATION-TEMPLATE.md), which provides comprehensive guidance on implementing standardized endpoints.

## Current Issues

### 1. Pydantic Model Errors

The `modernized_page_scraper.py` router has linter errors related to missing attributes in the Pydantic models:

```
Line 127: No parameter named "tenant_id"
Line 134: Cannot access attribute "tenant_id" for class "SitemapScrapingRequest"
  Attribute "tenant_id" is unknown
Line 182: Cannot access attribute "tenant_id" for class "BatchRequest"
  Attribute "tenant_id" is unknown
```

These issues are related to the discrepancy between the `SitemapScrapingRequest` and `BatchRequest` models defined in `src/models/api_models.py` and their actual usage in the router code.

According to the code comments in the models file, the `tenant_id` field was "removed" with a note that the default tenant ID should be used. However, the router code still attempts to access this field.

### 2. Potential Transaction Management Issues

While reviewing the code, we should verify that the implementation follows our transaction management principles:

- Routers own transactions
- Services are transaction-aware but don't manage transactions
- Background tasks manage their own sessions

### 3. No Dedicated Test Script

Unlike the Google Maps API and Sitemap implementations, the Modernized Page Scraper doesn't have a dedicated test script to validate its functionality.

## Required Changes

### 1. Update Pydantic Models

Modify the `SitemapScrapingRequest` and `BatchRequest` models in `src/models/api_models.py` to include the missing `tenant_id` field:

```python
class SitemapScrapingRequest(BaseModel):
    """Request model for sitemap scraping endpoint."""
    base_url: str = Field(..., description="Domain URL to scan")
    max_pages: int = Field(1000, description="Maximum number of pages to scan")
    # Add tenant_id field
    tenant_id: Optional[str] = Field(None, description="Tenant ID for the scan")

class BatchRequest(BaseModel):
    """Request model for batch scraping endpoint."""
    domains: List[str] = Field(..., description="List of domains to scan")
    max_pages: int = Field(1000, description="Maximum number of pages to scan per domain")
    # Add tenant_id field
    tenant_id: Optional[str] = Field(None, description="Tenant ID for the scan")
```

### 2. Verify Transaction Management

1. Review the router code to ensure it properly manages transactions:

   - Confirm `async with session.begin():` is used around service calls
   - Verify service methods don't commit or rollback transactions

2. Check background tasks to ensure they create their own sessions and manage their own transactions.

### 3. Create Test Script

Create a test script at `scripts/testing/test_page_scraper.py` that follows the pattern established in `test_google_maps_api.py` and `test_sitemap_with_user.py`:

- Use real user credentials
- Test both single domain and batch scanning
- Verify job status and batch status retrieval
- Validate database operations

## Implementation Steps

### 1. Update Pydantic Models

1. Modify `src/models/api_models.py` to add the `tenant_id` field to both request models.
2. Update any relevant validators or docstring comments.

### 2. Verify Router Implementation

1. Review `src/routers/modernized_page_scraper.py` to ensure it follows our architectural principles:

   - Proper transaction boundaries
   - Correct UUID handling
   - Authentication only at router level

2. Make any necessary corrections to the implementation.

### 3. Create Test Script

Create a comprehensive test script at `scripts/testing/test_page_scraper.py` that:

1. Uses the test user credentials from `10-TEST_USER_INFORMATION.md`
2. Tests single domain scanning functionality
3. Tests batch scanning functionality
4. Verifies status endpoints
5. Validates database results

### 4. Update Documentation

1. Update this document to include the implementation details and any challenges encountered.
2. Add the test script to our test suite documentation.

## Verification Steps

After implementing these changes, verify the correct functionality by:

1. **Linter Verification**: Run the linter to confirm no more errors related to these models.

2. **API Testing**: Use curl to test the APIs:

   ```bash
   # Test single domain scan
   curl -v http://localhost:8000/api/v3/modernized_page_scraper/scan -X POST \
     -H "Content-Type: application/json" \
     -H "Authorization: Bearer scraper_sky_2024" \
     -d '{"base_url": "https://www.example.com", "max_pages": 10, "tenant_id": "550e8400-e29b-41d4-a716-446655440000"}'

   # Test batch scan
   curl -v http://localhost:8000/api/v3/modernized_page_scraper/batch -X POST \
     -H "Content-Type: application/json" \
     -H "Authorization: Bearer scraper_sky_2024" \
     -d '{"domains": ["https://www.example.com", "https://www.example.org"], "max_pages": 10, "tenant_id": "550e8400-e29b-41d4-a716-446655440000"}'
   ```

3. **Test Script**: Run the test script to verify full functionality:
   ```bash
   python scripts/testing/test_page_scraper.py
   ```

## Reference Materials

- [07-26-GOOGLE-MAPS-API-FIX-IMPLEMENTATION-2025-03-26.md](/project-docs/07-database-connection-audit/07-26-GOOGLE-MAPS-API-FIX-IMPLEMENTATION-2025-03-26.md) - Reference implementation
- [11-AUTHENTICATION_BOUNDARY.md](/AI_GUIDES/11-AUTHENTICATION_BOUNDARY.md) - Critical authentication principles
- [13-TRANSACTION_MANAGEMENT_GUIDE.md](/AI_GUIDES/13-TRANSACTION_MANAGEMENT_GUIDE.md) - Transaction management guidelines
- [16-UUID_STANDARDIZATION_GUIDE.md](/AI_GUIDES/16-UUID_STANDARDIZATION_GUIDE.md) - UUID formatting standards
- [test_google_maps_api.py](/scripts/testing/test_google_maps_api.py) - Reference test implementation
