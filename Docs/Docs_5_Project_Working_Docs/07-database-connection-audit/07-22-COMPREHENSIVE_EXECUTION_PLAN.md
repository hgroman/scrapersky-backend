# ScraperSky Backend Standardization: Comprehensive Execution Plan

## Overview

This document provides a structured approach to complete the standardization of the ScraperSky Backend codebase, building on the successful patterns established in the sitemap implementation. Each phase includes specific tasks, guidance, and prompt templates for working with AI assistants.

## Progress Summary

The ScraperSky Backend project has made significant progress:

- ✅ Established core architectural principles
- ✅ Standardized database connection patterns
- ✅ Implemented sitemap functionality with proper session management
- ✅ Fixed UUID handling in database schema
- ✅ Created comprehensive testing framework
- ✅ Developed clear roadmap for standardization

## Phase 1: Complete Google Maps API Integration

### Task 1.1: Fix Google Maps API Test Script

**Priority:** HIGH
**Estimated time:** 2-3 hours

#### Action Items:
- Review Places service classes for correct method signatures
- Update method calls in test script to match actual service API
- Ensure database verification uses correct table names
- Test with sample location to verify functionality

#### Files to Modify:
- `scripts/testing/test_google_maps_api.py`
- Possibly update Places service files to align API

#### AI Prompt Template:
```
I need to fix the Google Maps API test script at `scripts/testing/test_google_maps_api.py`. The script currently has method compatibility issues:

1. "create_async_session" is unknown import symbol
2. Cannot access attribute "fetch_places" for class "PlacesSearchService"
3. Cannot access attribute "store_place" for class "PlacesStorageService"
4. Cannot access attribute "fetch_place_details" for class "PlacesService"

First, analyze these service classes to determine the correct method signatures:
- `src/services/places/places_service.py`
- `src/services/places/places_search_service.py`
- `src/services/places/places_storage_service.py`

Then update the test script to match the actual service API. Make sure to:
1. Fix imports for session management
2. Update method calls to match available methods
3. Verify table names for database verification
4. Ensure the script follows our testing framework guidelines in 07-19-TESTING_FRAMEWORK.md

Focus on making the script functional while preserving its structure and purpose.
```

### Task 1.2: Apply Sitemap Patterns to Google Maps API Router

**Priority:** HIGH
**Estimated time:** 3-4 hours

#### Action Items:
- Ensure router owns transactions with `async with session.begin()`
- Update background tasks to create their own sessions
- Replace direct session creation with dependency injection
- Implement proper error handling and logging

#### Files to Modify:
- `src/routers/google_maps_api.py`
- `src/services/places/places_service.py`
- `src/services/places/places_search_service.py`
- `src/services/places/places_storage_service.py`

#### AI Prompt Template:
```
I need to update the Google Maps API implementation to follow our architectural principles. The main focus is on applying the same patterns we used successfully in the modernized sitemap implementation.

First, review the Google Maps API router at `src/routers/google_maps_api.py` and check for:

1. Transaction management - Routers should own transactions with `async with session.begin()`
2. Session creation - Replace direct `async_session_factory()` calls with dependency injection
3. Background task patterns - Background tasks should create their own sessions
4. Error handling - Check for proper error handling and logging

Then, update the code to follow these principles:

1. Ensure routers own transactions (not services)
2. Fix any direct session creation with dependency injection
3. Update background tasks to create their own dedicated sessions
4. Implement proper error handling for transactions and operations

Please follow the examples from `src/routers/modernized_sitemap.py` and `src/services/sitemap/background_service.py` as reference implementations.
```

### Task 1.3: Document Google Maps API Updates

**Priority:** MEDIUM
**Estimated time:** 1-2 hours

#### Action Items:
- Document changes made to Google Maps API
- Update API documentation
- Create example requests and responses
- Document testing process

#### Files to Create/Modify:
- `project-docs/07-database-connection-audit/07-23-GOOGLE_MAPS_API_STANDARDIZATION.md`

#### AI Prompt Template:
```
I need to document the standardization changes made to the Google Maps API implementation. Create a new document at `project-docs/07-database-connection-audit/07-23-GOOGLE_MAPS_API_STANDARDIZATION.md` that includes:

1. A summary of the changes made to the Google Maps API implementation
2. Example code showing the correct patterns for:
   - Transaction management in routers
   - Session management in background tasks
   - Error handling and logging
3. API documentation with example requests and responses
4. Testing instructions using the updated test script
5. Any lessons learned from updating this service

Reference the patterns in our architectural principles (07-17-ARCHITECTURAL_PRINCIPLES.md) and follow the documentation style used in other files in this directory.
```

## Phase 2: UUID Standardization

### Task 2.1: Update Job Service for UUID Consistency

**Priority:** HIGH
**Estimated time:** 3-4 hours

#### Action Items:
- Audit job service for UUID handling
- Replace string IDs with proper UUID objects
- Update database queries for UUID compatibility
- Test changes with real data

#### Files to Modify:
- `src/services/job_service.py`
- Any models referencing job IDs

#### AI Prompt Template:
```
I need to standardize UUID handling in the job service. This follows our work in 07-14-job-id-standardization-2025-03-25.md where we standardized the sitemap service.

First, audit the job service at `src/services/job_service.py` for UUID handling issues:
1. Look for custom-formatted job IDs or prefixing (e.g., `job_{uuid}`)
2. Identify string-based UUID handling that should use UUID objects
3. Check SQLAlchemy models for proper PGUUID types
4. Review database queries that may need updates for UUID handling

Then update the code to follow our UUID standardization principles:
1. Use proper UUIDs without prefixes (e.g., `str(uuid.uuid4())`)
2. Update database queries to handle UUIDs correctly
3. Ensure SQLAlchemy models use PGUUID type for UUID columns
4. Handle type conversion gracefully when needed

Follow the patterns established in `src/services/sitemap/processing_service.py` and the fixes documented in 07-13-database-schema-type-fix-2025-03-25.md.
```

### Task 2.2: Review Domain Service for UUID Consistency

**Priority:** MEDIUM
**Estimated time:** 2-3 hours

#### Action Items:
- Examine UUID handling in domain service
- Standardize inconsistent UUID handling
- Update database operations for UUID compatibility
- Test changes with real data

#### Files to Modify:
- `src/services/domain_service.py`
- Any models related to domains

#### AI Prompt Template:
```
I need to review and update the domain service for UUID consistency. After standardizing the job service, this is the next priority for UUID handling.

First, examine UUID handling in `src/services/domain_service.py`:
1. Check how UUIDs are generated and formatted
2. Look for any string vs. UUID type conversions
3. Review database operations that use domain IDs
4. Identify any model definitions that should use PGUUID type

Then update the code to follow our UUID standardization principles:
1. Use proper UUIDs without prefixes (e.g., `str(uuid.uuid4())`)
2. Update database operations to handle UUIDs correctly
3. Ensure models use PGUUID type for UUID columns
4. Handle type conversion gracefully when needed

Follow the patterns from our job service updates and the principles in 07-17-ARCHITECTURAL_PRINCIPLES.md.
```

### Task 2.3: Create UUID Standardization Test Script

**Priority:** MEDIUM
**Estimated time:** 2-3 hours

#### Action Items:
- Create a test script for UUID handling
- Test job ID generation and retrieval
- Test domain ID handling
- Verify database operations with UUIDs

#### Files to Create:
- `scripts/testing/test_uuid_handling.py`

#### AI Prompt Template:
```
I need to create a comprehensive test script for UUID handling that verifies our standardization efforts. Create a new file at `scripts/testing/test_uuid_handling.py` that:

1. Tests job ID generation and retrieval
2. Tests domain ID handling
3. Verifies database operations with UUIDs
4. Checks type conversion between string and UUID

The script should follow our testing framework pattern from 07-19-TESTING_FRAMEWORK.md and use real user credentials as in `scripts/testing/test_sitemap_with_user.py`.

The test should:
1. Create a new job with a proper UUID
2. Verify it's stored correctly in the database
3. Retrieve it using both string and UUID parameters
4. Test the domain service with UUID operations
5. Report on any type conversion issues

Use the same session handling and database verification patterns as our other test scripts.
```

## Phase 3: Service Standardization

### Task 3.1: Batch Processing Service Review

**Priority:** MEDIUM
**Estimated time:** 3-4 hours

#### Action Items:
- Apply the same patterns from sitemap processing
- Ensure proper session management in background tasks
- Standardize UUID handling
- Create test script

#### Files to Modify:
- `src/services/batch/batch_processor_service.py`
- Other batch-related files

#### AI Prompt Template:
```
I need to review and update the batch processing service to follow our architectural patterns. This follows the same approach we used for the sitemap service.

First, review the batch processing service at `src/services/batch/batch_processor_service.py`:
1. Check for transaction management patterns
2. Review session handling in background tasks
3. Look for UUID handling that needs standardization
4. Assess error handling and logging

Then update the code to follow our architectural principles:
1. Ensure services are transaction-aware but don't manage transactions
2. Make background tasks create their own sessions
3. Standardize UUID handling to use proper formats
4. Implement proper error handling with context

Follow the patterns established in `src/services/sitemap/background_service.py` and documented in 07-17-ARCHITECTURAL_PRINCIPLES.md.
```

### Task 3.2: Page Scraper Service Review

**Priority:** MEDIUM
**Estimated time:** 3-4 hours

#### Action Items:
- Check for transaction boundary issues
- Update any direct session creation
- Standardize error handling
- Create dedicated test script

#### Files to Modify:
- `src/services/page_scraper/processing_service.py`
- Other page scraper files

#### AI Prompt Template:
```
I need to review and update the page scraper service to follow our architectural patterns, similar to how we updated the sitemap service.

First, review the page scraper service at `src/services/page_scraper/processing_service.py`:
1. Check for transaction boundary issues (services shouldn't manage transactions)
2. Look for direct session creation that should use dependency injection
3. Review error handling and logging
4. Check UUID handling for standardization opportunities

Then update the code to follow our architectural principles:
1. Make services transaction-aware but not transaction-managing
2. Replace direct session creation with proper patterns
3. Implement consistent error handling
4. Standardize UUID handling

Follow the patterns established in our sitemap implementation and documented in 07-17-ARCHITECTURAL_PRINCIPLES.md.
```

### Task 3.3: Create Service Standardization Documentation

**Priority:** MEDIUM
**Estimated time:** 2-3 hours

#### Action Items:
- Document service standardization patterns
- Create examples of correct implementations
- Document testing approach
- Update service inventory status

#### Files to Create/Modify:
- `project-docs/07-database-connection-audit/07-24-SERVICE_STANDARDIZATION_REPORT.md`
- Update `07-18-SERVICES_INVENTORY.md`

#### AI Prompt Template:
```
I need to document our service standardization efforts. Create a new document at `project-docs/07-database-connection-audit/07-24-SERVICE_STANDARDIZATION_REPORT.md` that:

1. Summarizes the standardization patterns applied to each service
2. Provides code examples of correct implementations
3. Documents the testing approach for each service
4. Highlights any service-specific considerations

Then update `07-18-SERVICES_INVENTORY.md` to reflect the current compliance status of each service based on our standardization work.

Follow the documentation style used in other files in this directory and focus on creating a clear reference for future development.
```

## Phase 4: Core Services Standardization

### Task 4.1: Core Directory Services Review

**Priority:** MEDIUM
**Estimated time:** 3-4 hours

#### Action Items:
- Review services in `/src/services/core/`
- Apply transaction-aware patterns
- Ensure proper session handling
- Create test scripts for core services

#### Files to Modify:
- Various files in `/src/services/core/`

#### AI Prompt Template:
```
I need to review and update the core services to follow our architectural principles. These are foundational services that need to be compliant with our standards.

First, review the services in `/src/services/core/`:
1. Identify transaction management patterns
2. Check session handling
3. Look for UUID handling that needs standardization
4. Review error handling and logging

Then update the code to follow our architectural principles:
1. Ensure services are transaction-aware but don't manage transactions
2. Fix any session management issues
3. Standardize UUID handling
4. Implement consistent error handling

Pay special attention to authentication boundary principles - core services should receive user IDs, not tokens, and should not perform JWT verification.

Follow the patterns established in our standardized services and documented in 07-17-ARCHITECTURAL_PRINCIPLES.md.
```

### Task 4.2: Storage Services Review

**Priority:** MEDIUM
**Estimated time:** 2-3 hours

#### Action Items:
- Review services in `/src/services/storage/`
- Apply connection pooling best practices
- Standardize error handling
- Create test scripts

#### Files to Modify:
- Various files in `/src/services/storage/`

#### AI Prompt Template:
```
I need to review and update the storage services to follow our architectural principles, particularly around database connections and error handling.

First, review the services in `/src/services/storage/`:
1. Check for connection pooling usage
2. Review transaction boundary compliance
3. Look for error handling patterns
4. Assess UUID handling

Then update the code to follow our architectural principles:
1. Ensure proper use of Supavisor connection pooling
2. Make services transaction-aware but not transaction-managing
3. Implement consistent error handling
4. Standardize UUID handling

Follow the patterns established in our standardized services and documented in 07-17-ARCHITECTURAL_PRINCIPLES.md.
```

## Phase 5: Comprehensive Testing

### Task 5.1: Complete Test Scripts for All Key Services

**Priority:** HIGH (Ongoing)
**Estimated time:** 1-2 hours per service

#### Action Items:
- Create test scripts for each service following the template
- Use real user credentials
- Verify database operations
- Test error handling and edge cases

#### Files to Create:
- Various test scripts in `scripts/testing/`

#### AI Prompt Template:
```
I need to create a test script for the [SERVICE_NAME] service following our testing framework template. This will verify that the service follows our architectural principles and works correctly.

Create a new file at `scripts/testing/test_[service_name].py` that:

1. Tests the main functionality of the service
2. Uses real user credentials for authentication
3. Verifies database operations work correctly
4. Tests error handling and edge cases

The script should follow our testing framework pattern from 07-19-TESTING_FRAMEWORK.md and similar to `scripts/testing/test_sitemap_with_user.py`.

The test should:
1. Set up any necessary test prerequisites
2. Call the service methods with appropriate parameters
3. Verify results in the database
4. Test both happy path and error conditions
5. Clean up any test data created

Use the same session handling and logging patterns as our other test scripts.
```

### Task 5.2: Create Integration Test Suite

**Priority:** MEDIUM
**Estimated time:** 4-6 hours

#### Action Items:
- Create tests for end-to-end flows
- Test interactions between multiple services
- Verify data consistency across services
- Test error propagation

#### Files to Create:
- `scripts/testing/test_integration.py`

#### AI Prompt Template:
```
I need to create an integration test suite that tests how multiple services work together. This will verify end-to-end flows and data consistency across services.

Create a new file at `scripts/testing/test_integration.py` that:

1. Tests complete workflows involving multiple services
2. Verifies data consistency between services
3. Tests error propagation through service boundaries
4. Validates the full user experience

Include tests for these key workflows:
1. Domain scanning → Sitemap extraction → URL processing
2. Google Maps search → Place details retrieval → Storage
3. Batch processing workflows
4. Any other critical end-to-end processes

Use real user credentials and follow our testing framework from 07-19-TESTING_FRAMEWORK.md. The test should verify both functionality and adherence to our architectural principles, especially around transaction boundaries and error handling.
```

## Phase 6: Documentation Finalization

### Task 6.1: Update API Documentation

**Priority:** MEDIUM
**Estimated time:** 3-4 hours

#### Action Items:
- Document standardized API patterns
- Update references to old patterns
- Create usage examples
- Document authentication flow

#### Files to Create/Modify:
- `project-docs/07-database-connection-audit/07-25-API_DOCUMENTATION.md`

#### AI Prompt Template:
```
I need comprehensive API documentation that reflects our standardized patterns. Create a new document at `project-docs/07-database-connection-audit/07-25-API_DOCUMENTATION.md` that:

1. Documents our standardized API patterns
2. Provides usage examples for each endpoint
3. Describes the authentication flow
4. Includes response formats and error handling

The documentation should cover these key API routes:
1. Sitemap scanning endpoints
2. Google Maps API endpoints
3. Batch processing endpoints
4. User profile endpoints
5. Domain management endpoints

For each endpoint, include:
- HTTP method and URL
- Request parameters and body format
- Response format with examples
- Authentication requirements
- Error responses and status codes

Follow the style of our existing documentation and ensure it aligns with the current implementation.
```

### Task 6.2: Create Developer Onboarding Guide

**Priority:** MEDIUM
**Estimated time:** 3-4 hours

#### Action Items:
- Create guide based on architectural principles
- Document common patterns and anti-patterns
- Provide examples of correct implementations
- Include troubleshooting guidance

#### Files to Create:
- `project-docs/07-database-connection-audit/07-26-DEVELOPER_ONBOARDING.md`

#### AI Prompt Template:
```
I need to create a comprehensive developer onboarding guide for the ScraperSky Backend. This will help new developers understand our architectural principles and implementation patterns.

Create a new document at `project-docs/07-database-connection-audit/07-26-DEVELOPER_ONBOARDING.md` that includes:

1. A summary of our core architectural principles
2. Detailed explanations of key patterns with code examples:
   - Transaction management
   - Session handling
   - UUID standardization
   - Authentication boundary
   - Error handling
3. Common anti-patterns to avoid
4. Troubleshooting guidance for common issues
5. Development workflow recommendations
6. Testing approach and requirements

The guide should be comprehensive enough for a new developer to understand our architecture and start contributing effectively. Include references to our standardized services as exemplars of the correct implementation patterns.
```

## Progress Tracking

Use this table to track progress on each task:

| Task ID | Task Name | Status | Completed Date | Notes |
|---------|-----------|--------|----------------|-------|
| 1.1 | Fix Google Maps API Test Script | Not Started |  |  |
| 1.2 | Apply Sitemap Patterns to Google Maps API Router | Not Started |  |  |
| 1.3 | Document Google Maps API Updates | Not Started |  |  |
| 2.1 | Update Job Service for UUID Consistency | Not Started |  |  |
| 2.2 | Review Domain Service for UUID Consistency | Not Started |  |  |
| 2.3 | Create UUID Standardization Test Script | Not Started |  |  |
| 3.1 | Batch Processing Service Review | Not Started |  |  |
| 3.2 | Page Scraper Service Review | Not Started |  |  |
| 3.3 | Create Service Standardization Documentation | Not Started |  |  |
| 4.1 | Core Directory Services Review | Not Started |  |  |
| 4.2 | Storage Services Review | Not Started |  |  |
| 5.1 | Complete Test Scripts for All Key Services | Not Started |  |  |
| 5.2 | Create Integration Test Suite | Not Started |  |  |
| 6.1 | Update API Documentation | Not Started |  |  |
| 6.2 | Create Developer Onboarding Guide | Not Started |  |  |

## Reference Information

### Key Architectural Principles

1. **Connection Management**
   - Always use Supavisor connection pooling
   - Sessions should not be shared across asynchronous contexts

2. **Responsibility Boundaries**
   - Routers OWN transactions
   - Services are transaction-AWARE
   - Background jobs manage their OWN sessions/transactions

3. **UUID Standardization**
   - All UUIDs must be proper UUIDs without prefixes
   - Use PostgreSQL UUID type in database schema
   - Use PGUUID SQLAlchemy type for UUID columns

4. **Authentication Boundary**
   - JWT authentication happens ONLY at API gateway/router level
   - Services must be authentication-agnostic

5. **Error Handling**
   - Provide detailed error messages with context
   - Handle database errors gracefully with try/except blocks

### Test User Information

For testing, use these credentials:

- ID: `5905e9fe-6c61-4694-b09a-6602017b000a`
- Email: `hankgroman@gmail.com`
- Tenant ID: `550e8400-e29b-41d4-a716-446655440000`

## Conclusion

This plan provides a comprehensive approach to completing the standardization of the ScraperSky Backend. By following this structured process, we can ensure that the successful patterns established in the sitemap implementation are consistently applied across all services, resulting in a maintainable, scalable, and reliable application.
