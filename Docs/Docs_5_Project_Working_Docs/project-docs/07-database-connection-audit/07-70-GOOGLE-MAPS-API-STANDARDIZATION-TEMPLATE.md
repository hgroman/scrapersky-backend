# Google Maps API Standardization Template

## 1. Overview

This document serves as a comprehensive specification for the standardized Google Maps API implementation. It details all components, endpoints, data flows, and implementation patterns that should be followed when standardizing other endpoints (such as the Sitemap API and Modernized Page Scraper API).

## 2. Architecture Components

The implementation follows a layered architecture with clear separation of concerns:

```
┌───────────────┐     ┌───────────────┐     ┌───────────────┐     ┌───────────────┐
│  Static HTML  │────▶│  API Routers  │────▶│   Services    │────▶│  DB Models    │
│   Frontend    │◀────│   (FastAPI)   │◀────│               │◀────│               │
└───────────────┘     └───────────────┘     └───────────────┘     └───────────────┘
```

### 2.1 Component Responsibilities

1. **Static HTML Frontend**:

   - Provides user interface for search, status tracking, and results viewing
   - Makes AJAX calls to API endpoints
   - Handles presentation logic and user interactions

2. **API Routers (FastAPI)**:

   - Define endpoints and handle HTTP requests/responses
   - Manage authentication (JWT validation)
   - Own transaction boundaries
   - Coordinate between client and services

3. **Services**:

   - Implement business logic
   - Are transaction-aware but don't manage transactions
   - Handle external API interactions (Google Maps API)
   - Process and transform data

4. **Database Models**:
   - Define data structure
   - Provide CRUD operations
   - Enforce data integrity

## 3. API Endpoints

### 3.1 Search Endpoint

**Path**: `/api/v3/localminer-discoveryscan/search`
**Method**: POST
**Authentication**: JWT Bearer token

**Request Body**:

```json
{
  "business_type": "string",
  "location": "string",
  "params": {
    "radius_km": "number"
  },
  "tenant_id": "string (optional)"
}
```

**Response**:

```json
{
  "job_id": "uuid",
  "status": "string",
  "message": "string"
}
```

**Purpose**: Initiates a search for places matching the specified business type and location.

### 3.2 Search Status Endpoint

**Path**: `/api/v3/localminer-discoveryscan/search/status/{job_id}`
**Method**: GET
**Authentication**: JWT Bearer token
**Parameters**:

- `job_id`: UUID of the search job
- `tenant_id`: (query parameter, optional)

**Response**:

```json
{
  "status": "string",
  "progress": "number",
  "message": "string",
  "total_results": "number (optional)"
}
```

**Purpose**: Retrieves the current status of a search job.

### 3.3 Results Endpoint

**Path**: `/api/v3/localminer-discoveryscan/results/{job_id}`
**Method**: GET
**Authentication**: JWT Bearer token
**Parameters**:

- `job_id`: UUID of the search job
- `tenant_id`: (query parameter, optional)
- `limit`: (query parameter, optional) Number of results to return
- `offset`: (query parameter, optional) Pagination offset
- `filter_status`: (query parameter, optional) Filter by status

**Response**:

```json
{
  "places": [
    {
      "id": "string",
      "place_id": "string",
      "name": "string",
      "business_type": "string",
      "formatted_address": "string",
      "location": "string",
      "latitude": "number",
      "longitude": "number",
      "rating": "number",
      "user_ratings_total": "number",
      "status": "string",
      "search_time": "datetime"
    }
  ],
  "total": "number",
  "job": {
    "id": "uuid",
    "status": "string",
    "created_at": "datetime"
  }
}
```

**Purpose**: Retrieves the results of a completed search job.

### 3.4 Search History Endpoint

**Path**: `/api/v3/localminer-discoveryscan/search/history`
**Method**: GET
**Authentication**: JWT Bearer token
**Parameters**:

- `tenant_id`: (query parameter, optional)
- `limit`: (query parameter, optional) Number of history items to return
- `offset`: (query parameter, optional) Pagination offset
- `status`: (query parameter, optional) Filter by status

**Response**:

```json
[
  {
    "id": "uuid",
    "business_type": "string",
    "location": "string",
    "status": "string",
    "created_at": "datetime",
    "updated_at": "datetime",
    "params": {
      "radius_km": "number"
    }
  }
]
```

**Purpose**: Retrieves a list of previous search jobs.

## 4. Database Models

### 4.1 PlaceSearch Model

```python
class PlaceSearch(Base):
    """Model for storing search job information."""
    __tablename__ = "place_search"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    business_type = Column(String, nullable=False)
    location = Column(String, nullable=False)
    status = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    params = Column(JSON, nullable=True)
    user_id = Column(String, nullable=True)
    total_results = Column(Integer, nullable=True)
    progress = Column(Integer, nullable=True)
    error_message = Column(String, nullable=True)
```

### 4.2 PlaceStaging Model

```python
class PlaceStaging(Base):
    """Model for storing search results."""
    __tablename__ = "places_staging"

    id = Column(String, primary_key=True)
    place_id = Column(String, nullable=False)
    name = Column(String, nullable=False)
    business_type = Column(String, nullable=False)
    formatted_address = Column(String, nullable=True)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    rating = Column(Float, nullable=True)
    user_ratings_total = Column(Integer, nullable=True)
    status = Column(String, nullable=True)
    search_time = Column(DateTime, default=datetime.utcnow)
    search_job_id = Column(UUID(as_uuid=True), ForeignKey("place_search.id"))
```

## 5. Service Implementation

### 5.1 Places Storage Service

The `PlacesStorageService` class provides methods for:

1. **Creating and managing search jobs**:

   - `create_search_job`: Creates a new search job record
   - `update_job_status`: Updates the status of a search job
   - `update_job_progress`: Updates the progress of a search job
   - `get_job_status`: Retrieves the status of a search job

2. **Storing and retrieving search results**:

   - `store_places`: Stores place results from the Google Maps API
   - `get_places_for_job`: Retrieves places for a specific job

3. **Managing search history**:
   - `get_search_history`: Retrieves search history records

### 5.2 Google Maps Service

The `GoogleMapsService` class provides methods for:

1. **Searching for places**:

   - `search_places`: Searches for places using the Google Maps API
   - `search_and_store`: Searches for places and stores the results

2. **Processing place data**:
   - `_extract_place_data`: Extracts relevant data from Google Maps API responses
   - `_format_place_for_storage`: Formats place data for storage

## 6. Frontend Implementation

### 6.1 Static HTML Page Structure

The `google-maps.html` file is organized into three main tabs:

1. **Single Search Tab**:

   - Search form for business type, location, and radius
   - Recent searches section with reuse and results options
   - Search status display

2. **Batch Search Tab**:

   - Form for batch searching multiple locations
   - Status display for batch operations

3. **Results Viewer Tab**:
   - Results filtering options
   - Results table with place details
   - Pagination controls

### 6.2 JavaScript Functions

Key JavaScript functions include:

1. **Search Operations**:

   - `searchPlaces`: Initiates a search operation
   - `fetchStatus`: Polls for search status
   - `fetchResults`: Retrieves search results
   - `fetchSearchHistory`: Retrieves search history

2. **UI Interactions**:
   - `displayResults`: Renders search results
   - `applyFilters`: Filters search results
   - `updateSearchHistoryAfterSearch`: Updates history after search completes

## 7. Data Flow

### 7.1 Search Flow

```
┌────────────┐  1. Submit Search  ┌────────────┐  2. Create Job  ┌────────────┐
│  Frontend  │─────────────────▶ │   Router   │────────────────▶│  Service   │
└────────────┘                   └────────────┘                 └────────────┘
      ▲                                │                              │
      │                                │                              │
      │                                ▼                              ▼
      │                          ┌────────────┐               ┌────────────┐
      │  5. Display Status       │ DB (Search │  3. Start    │Google Maps │
      └─────────────────────────┤    Job)     │◀───────────  │    API     │
                                └────────────┘  Background   └────────────┘
                                      ▲          Task              │
                                      │                            │
                                      │                            ▼
                                      │                      ┌────────────┐
                                      │  4. Store Results   │ DB (Places │
                                      └────────────────────┤   Staging)  │
                                                           └────────────┘
```

### 7.2 Results Retrieval Flow

```
┌────────────┐  1. Request Results  ┌────────────┐
│  Frontend  │────────────────────▶ │   Router   │
└────────────┘                      └────────────┘
      ▲                                   │
      │                                   ▼
      │                             ┌────────────┐
      │                             │  Service   │
      │                             └────────────┘
      │                                   │
      │                                   ▼
      │                             ┌────────────┐
      │  3. Display Results         │  Database  │
      └────────────────────────────┤   Query    │
                                   └────────────┘
                                        │
                                        ▼
                            ┌─────────────────────┐
                            │Join Place Search and│
                            │  Places Staging     │
                            └─────────────────────┘
```

## 8. Testing

### 8.1 API Testing

The `test_google_maps_api.py` script tests:

1. **Search endpoint**:

   - Initiates a search with valid parameters
   - Verifies job ID is returned

2. **Status endpoint**:

   - Polls for status using job ID
   - Verifies status updates correctly

3. **Results endpoint**:

   - Retrieves results for a completed job
   - Verifies result structure and content

4. **Search history endpoint**:
   - Retrieves search history
   - Verifies history structure and content

### 8.2 UI Testing

Manual testing of the UI involves:

1. **Search functionality**:

   - Enter business type and location
   - Verify search initiates correctly
   - Observe status updates

2. **Results viewing**:

   - Switch to results tab
   - Apply filters
   - Verify results display correctly

3. **Search history**:
   - Verify recent searches display
   - Test "Reuse" functionality
   - Test "Results" direct navigation

## 9. Standardization for Other Endpoints

### 9.1 Applying to Sitemap API

To standardize the Sitemap API using this template:

1. **Update API endpoints**:

   - Follow the naming pattern: `/api/v3/sitemap/{function}`
   - Implement consistent status and results endpoints

2. **Update database models**:

   - Ensure proper UUID usage
   - Follow similar schema design patterns

3. **Service implementation**:

   - Maintain transaction-aware design
   - Follow background task pattern

4. **Frontend implementation**:
   - Follow tab-based design
   - Implement history, status, and results viewing

### 9.2 Applying to Modernized Page Scraper

As detailed in the work order `07-27-MODERNIZED-PAGE-SCRAPER-FIX-WORK-ORDER-2025-03-26.md`, standardize by:

1. **Fixing Pydantic models**:

   - Add missing fields
   - Follow consistent patterns

2. **Verifying transaction management**:

   - Ensure routers own transactions
   - Ensure services are transaction-aware

3. **Creating test scripts**:
   - Follow the pattern in `test_google_maps_api.py`

## 10. Future Enhancements

### 10.1 Search History Improvements

1. **Duplicate search prevention**:

   - Implement check against existing searches
   - Provide option to reuse existing results or force new search

2. **Enhanced UI for search history**:
   - Add search/filter for history
   - Implement sorting options
   - Add history management (delete, rename)

### 10.2 Results Management

1. **Enhanced filtering**:

   - Add more filter options (rating, distance)
   - Implement saved filters

2. **Batch operations**:

   - Add ability to select multiple results
   - Implement batch status changes

3. **Export functionality**:
   - Add export to CSV/Excel
   - Implement data integration with other systems

### 10.3 UI Improvements

1. **Theme customization**:

   - Address the white background in search history table to match dark theme
   - Implement theme selection

2. **Responsive design**:
   - Improve mobile experience
   - Add responsive layouts

### 10.4 API Enhancements

1. **Rate limiting**:

   - Implement per-user rate limits
   - Add usage statistics

2. **Bulk operations**:
   - Add bulk search capabilities
   - Implement batch status updates

## 11. Implementation Notes

1. **CSS Styling Fix**: The search history table currently has a white background that doesn't match the dark theme. This should be fixed in a future update by modifying the table styling in `google-maps.html`.

2. **Status Field Options**: As shown in the Results Viewer tab, the status field options include:

   - All Statuses
   - New
   - Selected
   - Maybe
   - Not a Fit
   - Archived

3. **Transaction Management**: The implementation strictly follows our transaction management principles where routers own transactions and services are transaction-aware but don't manage transactions. Background tasks manage their own sessions.

4. **UUID Standardization**: All job IDs and other identifiers use the standard UUID format without prefixes, following our UUID standardization guidelines.

## 12. Conclusion

This standardization template provides a comprehensive guide for implementing and standardizing API endpoints in the ScraperSky backend. By following this template, we ensure consistent design patterns, properly managed transactions, standardized UUID usage, and a clear separation of concerns across all API endpoints.

The implementation of the Google Maps API serves as the exemplar for all other endpoints, setting the standard for code quality, architecture, and user experience. Applying these patterns to the Sitemap API and Modernized Page Scraper will create a unified, maintainable, and robust system.
