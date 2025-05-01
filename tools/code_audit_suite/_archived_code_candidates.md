# Archived Code Candidates Manifest

## File: `src/api/models/places.py`

**Functionality (Layman's Terms):**
Defines the expected format for information about business locations (like addresses and ratings) used when communicating with the application's API.

**Key Classes/Functions Defined:**

- `PlaceModel`
- `PlacesPaginatedResponse`
- `UpdatePlaceStatusRequest`
- `BatchUpdatePlacesRequest`
- `StandardResponse`
- `BatchUpdateResponse`

## File: `src/db/direct_migration.py`

**Functionality (Layman's Terms):**
A technical script used once to update the database structure by adding a field to track the number of URLs in sitemap files. It bypasses the usual database update process.

**Key Classes/Functions Defined:**

- `execute_migration`
- `add_url_count_column`
- `main`

## File: `src/db/direct_session.py`

**Functionality (Layman's Terms):**
Provides a way for the application to connect directly to the main database, possibly as a workaround or for specific technical needs, bypassing the usual managed connection methods.

**Key Classes/Functions Defined:**

- `get_project_ref`
- `get_direct_engine`
- `get_direct_session`
- `get_direct_session_dependency`

## File: `src/db/domain_handler.py`

**Functionality (Layman's Terms):**
Designed to handle database tasks related to website domains, like adding new domains, retrieving their information, updating details, or deleting them.

**Key Classes/Functions Defined:**

- `DomainDBHandler`

## File: `src/models/feature_flag.py`

**Functionality (Layman's Terms):**
Defines how information about 'feature flags' (on/off switches for application features) is stored in the database.

**Key Classes/Functions Defined:**

- `FeatureFlag`

## File: `src/schemas/contact.py`

**Functionality (Layman's Terms):**
Specifies the format and expected fields (like name, email, company, social links) for contact information, probably related to storing contacts found during scraping or via an API.

**Key Classes/Functions Defined:**

- `ContactBase`
- `ContactCreate`
- `ContactUpdate`
- `ContactResponse`

## File: `src/scraper/data_formatter.py`

**Functionality (Layman's Terms):**
Prepares website information (like title, description, tech used, social links) extracted during scraping into the correct format for saving to the database.

**Key Classes/Functions Defined:**

- `_get_model_data`
- `format_website_data`

## File: `src/services/batch/task_debugger.py`

**Functionality (Layman's Terms):**
A tool intended for developers to help track and debug background tasks by creating log files (markers) when a task starts, progresses, and completes.

**Key Classes/Functions Defined:**

- `verify_task_start`
- `log_task_progress`
- `log_task_completion`
- `get_marker_files`
- `cleanup_markers`

## File: `src/services/sitemap/analyzer_service.py`

**Functionality (Layman's Terms):**
Designed to automatically find, download, and read website sitemap files (which list a site's pages) to extract the URLs.

**Key Classes/Functions Defined:**

- `SitemapType` (Enum-like class)
- `DiscoveryMethod` (Enum-like class)
- `SitemapAnalyzer`

## File: `src/services/sitemap/background_service.py`

**Functionality (Layman's Terms):**
Manages the process of analyzing website sitemaps in the background, either for a single website or a batch of websites, updating a job status as it progresses.

**Key Classes/Functions Defined:**

- `process_domain_background`
- `process_batch_background`
- `store_domain_data`

## File: `src/services/sitemap/sitemap_service.py`

**Functionality (Layman's Terms):**
Provides core functions for working with website sitemaps, including finding sitemap files, downloading them, extracting the list of URLs they contain, saving this information to the database, and managing background analysis jobs. (Note: This might be a duplicate or alternative version of `src/services/sitemap_service.py`)

**Key Classes/Functions Defined:**

- `SitemapService`

## File: `src/services/sitemap_service.py`

**Functionality (Layman's Terms):**
Provides core functions for working with website sitemaps, including finding sitemap files, downloading them, extracting the list of URLs they contain, saving this information to the database, and managing background analysis jobs. (Note: This might be a duplicate or alternative version of `src/services/sitemap/sitemap_service.py`)

**Key Classes/Functions Defined:**

- `SitemapScrapingRequest`
- `SitemapScrapingResponse`
- `JobStatusResponse`
- `SitemapService`

## File: `src/utils/db_schema_helper.py`

**Functionality (Layman's Terms):**
A technical tool for developers to automatically generate database table structure descriptions based on the application's data models (Pydantic models).

**Key Classes/Functions Defined:**

- `get_pg_type_from_py_type`
- `generate_schema_from_model`
- `extract_schemas_from_module`

## File: `src/utils/db_utils.py`

**Functionality (Layman's Terms):**
Provides a technical helper (@managed_transaction) to ensure database operations within service functions are handled safely and consistently as part of a larger request, preventing accidental data inconsistencies.

**Key Classes/Functions Defined:**

- `managed_transaction` (Decorator function)

## File: `src/utils/sidebar.py`

**Functionality (Layman's Terms):**
Contains functions to retrieve and manage the items (like links to different sections) that should appear in the application's navigation sidebar, based on user permissions and enabled features for their account.

**Key Classes/Functions Defined:**

- `get_sidebar_items`
- `get_tenant_feature_status`
- `set_feature_status`

## File: `src/auth/auth_service.py`

**Functionality (Layman's Terms):**
Provides simplified authentication and authorization checks (permissions, features) designed as compatibility stubs after RBAC removal. Assumes JWT is handled elsewhere.

**Key Classes/Functions Defined:**

- `AuthService` (with static methods: `_get_valid_user_id`, `get_user_permissions`, `check_permission`, `require_permission`, `get_tenant_features`, `check_feature_enabled`, `require_feature`, `clear_cache`)

## File: `src/models/sidebar.py`

**Functionality (Layman's Terms):**
Defines the database table structure (SQLAlchemy model) for storing information about navigation links intended for the application sidebar.

**Key Classes/Functions Defined:**

- `SidebarFeature`

## File: `src/services/core/auth_service.py`

**Functionality (Layman's Terms):**
Handles core authentication logic, primarily focused on validating JWT tokens received in API requests and extracting user information. Includes fallback mechanisms and mock user creation for development.

**Key Classes/Functions Defined:**

- `AuthService` (class with methods: `get_user_from_token`, `create_mock_user`)
- `get_current_user` (FastAPI dependency function)

## File: `src/services/domain_service.py`

**Functionality (Layman's Terms):**
Provides methods for managing website domain records in the database, such as creating new domain entries, retrieving existing ones by ID or name, updating them (e.g., from metadata), and listing domains.

**Key Classes/Functions Defined:**

- `DomainService` (with methods: `get_by_id`, `get_by_domain_name`, `get_all`, `create`, `create_from_metadata`, `update_from_metadata`, `update`, `process_domain_metadata`, `get_by_batch_id`, `get_or_create`)

## File: `src/services/scraping/scrape_executor_service.py`

**Functionality (Layman's Terms):**
A central service responsible for performing various web scraping tasks like analyzing website sitemaps, extracting metadata (title, tech stack, links), searching Google Places, and extracting contact information (emails, phone numbers, social media) from web pages.

**Key Classes/Functions Defined:**

- `ScrapeExecutorService` (with class methods: `execute_sitemap_analysis`, `execute_metadata_extraction`, `execute_places_search`, `execute_contact_extraction`, and various private helper methods for fetching/parsing)

## File: `src/api/__init__.py`

**Functionality (Layman's Terms):**
Defines `src/api` as a Python package. It appears to attempt to import and re-export routers from a non-existent `router` sub-directory within `api`. The `api` directory itself contains no other modules. Likely a remnant of previous structuring.

**Key Classes/Functions Defined:**

- (Imports `places_router` from `.router.places_router` but this sub-module doesn't exist)
- Exports `__all__ = ["places_router"]`

## File: `src/config/import_logger.py`

**Functionality (Layman's Terms):**
Defines a custom hook (`RuntimeImportHook`) to intercept and print information about Python module imports as they happen, likely for debugging or analysis. Appears superseded by `runtime_tracer.py`.

**Key Classes/Functions Defined:**

- `RuntimeImportHook`

## File: `src/core/exceptions.py`

**Functionality (Layman's Terms):**
Defines a set of custom exception classes (like `NotFoundError`, `ValidationError`, `DatabaseError`) inheriting from a base `BaseError`, intended for standardized error handling across the application. Appears unused.

**Key Classes/Functions Defined:**

- `BaseError`
- `NotFoundError`
- `ValidationError`
- `AuthenticationError`
- `AuthorizationError`
- `DatabaseError`

## File: `src/core/response.py`

**Functionality (Layman's Terms):**
Provides a function (`standard_response`) intended to wrap API response data in a consistent dictionary format (e.g., `{"data": ...}`). Appears unused.

**Key Classes/Functions Defined:**

- `standard_response` (function)

## File: `src/models.py`

**Functionality (Layman's Terms):**
Defines various Pydantic models, likely intended for validating API requests or structuring responses related to scraping, sitemaps, batch jobs, and places searches. Appears unused.

**Key Classes/Functions Defined:**

- `ScrapingRequest`, `ScrapingResponse`
- `SocialLinks`, `ContactInfo`, `TechnologyStack`
- `TaskStatus` (Enum)
- `SiteMetadata`
- `SitemapScrapingRequest`, `SitemapScrapingResponse`
- `BatchRequest`, `BatchResponse`
- `PageType` (Enum)
- `BatchJobStatus`
- `BatchSitemapRequest`
- `SitemapStats`
- `PlacesSearchRequest`, `PlacesSearchResponse`, `PlacesStatusResponse`
- `SitemapType` (Enum), `DiscoveryMethod` (Enum)
- `SitemapAnalyzerRequest`, `SitemapAnalyzerResponse`
- `SitemapAnalyzerBatchRequest`, `SitemapAnalyzerBatchResponse`
- `SitemapStatusResponse`
- `SitemapFileResponse`
- `SitemapUrlsResponse`

## File: `src/models/enums.py`

**Functionality (Layman's Terms):**
Defines Enum classes (`SitemapAnalysisStatusEnum`, `DomainStatusEnum`) for representing the status of sitemap analysis and domain processing. Appears unused and potentially duplicated within `src/models/domain.py`.

**Key Classes/Functions Defined:**

- `SitemapAnalysisStatusEnum`
- `DomainStatusEnum`

## File: `src/models/user.py`

**Functionality (Layman's Terms):**
Defines a Pydantic model `User` to represent an authenticated user, including their ID, username, email, tenant ID, and roles. Appears unused.

**Key Classes/Functions Defined:**

- `User` (Pydantic model)

## File: `src/routers/sqlalchemy/__init__.py`

**Functionality (Layman's Terms):**
Defines `src/routers/sqlalchemy` as a Python package and creates a simple test `APIRouter` (`test_router`) with a basic health check endpoint. The package contains no other modules and this test router is not included in the main application.

**Key Classes/Functions Defined:**

- `test_router` (FastAPI APIRouter)
- `health_check` (endpoint function)
- Exports `routers = [test_router]`

## File: `src/services/batch/types.py`

**Functionality (Layman's Terms):**
Defines various `TypedDict` structures (`BatchOptions`, `BatchStatus`, `DomainResult`, `BatchResult`) and constants (e.g., `BATCH_STATUS_PENDING`) intended for use within the batch processing system. Appears unused as the associated batch system is orphaned.

**Key Classes/Functions Defined:**

- `BatchOptions` (TypedDict)
- `BatchStatus` (TypedDict)
- `DomainResult` (TypedDict)
- `BatchResult` (TypedDict)
- Various status constants (e.g., `BATCH_STATUS_PENDING`)
- Type aliases (`DomainList`, `BatchId`, `UserId`, `Session`)

## File: `src/services/core/user_context_service.py`

**Functionality (Layman's Terms):**
Provides a `UserContextService` intended to manage user-specific context (like user ID, tenant ID) potentially retrieved from JWT tokens or environment variables. It offers methods like `get_valid_user_id`. Appears unused.

**Key Classes/Functions Defined:**

- `UserContextService`
- `user_context_service` (singleton instance)
