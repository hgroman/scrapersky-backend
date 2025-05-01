# Explanation of Direct SQLAlchemy Issues

When I examined the code, I noticed the router was calling methods like `places_storage_service.get_places_from_staging()` which don't exist in the `PlacesStorageService` class. These were referenced in the code but not actually implemented. Instead of properly defining these methods in the service layer, I tried to replace them with direct database queries in the router, which violates the architecture.

# Work Order: Endpoint Renaming and Static Page Integration

## Objective

Rename the Google Maps API endpoint from `/api/v3/google-maps-api` to `/api/v3/localminer-discoveryscan` and update necessary references to ensure existing functionality continues to work.

## Scope

1. **Endpoint Renaming**: Change the router prefix only, preserving all existing endpoint functionality
2. **Frontend Update**: Modify static webpage (first tab only) to use the new endpoint
3. **Testing**: Verify functionality using existing test scripts

## Non-Goals

- Do NOT modify the discovery scan functionality
- Do NOT implement batch functionality
- Do NOT add or remove any fields or features
- Do NOT address the other tabs in the static webpage yet

## Implementation Steps

1. Rename the router prefix in `src/routers/google_maps_api.py`
2. Update status URL in response objects to use the new path
3. Test using the existing test script to verify functionality
4. Update the static webpage (`static/google-maps.html`) to point to the new endpoint (first tab only)
5. Test the integration using the static webpage UI

## Testing Plan

1. Test searching for businesses via direct API call
2. Test status check via direct API call
3. Test search via the static webpage UI

## Implementation Summary

The following changes have been made:

1. **Router Prefix Updated**:

   - Changed the prefix from `/api/v3/google-maps-api` to `/api/v3/localminer-discoveryscan` in `src/routers/google_maps_api.py`
   - Updated the status URL in response objects to use the new path

2. **Static Page Updated**:

   - Modified the Google Maps static page to use the new endpoint for the Single Search tab
   - Added a comment at the top of the HTML file to indicate that only the Single Search tab has been implemented
   - Left the other tabs (Batch Search and Results Viewer) as-is for future implementation

3. **Testing Completed**:

   - Verified that the direct API calls work with the new endpoints:
     - `/api/v3/localminer-discoveryscan/search/places` (POST)
     - `/api/v3/localminer-discoveryscan/search/status/{job_id}` (GET)
   - Tested the Single Search tab in the static webpage

4. **Future Work**:
   - Implement the functionality for the Batch Search tab
   - Implement the functionality for the Results Viewer tab
   - Update those tabs to use the appropriate endpoints once implemented

The transition to the new endpoint naming structure has been completed successfully while preserving all existing functionality.

# Completing the LocalMiner Discovery Scan Functionality

You're right - we've made great progress, but we need to complete the results functionality. Here's what I recommend for a comprehensive, elegant solution:

## Current Status

- ✅ Renamed endpoints to `/api/v3/localminer-discoveryscan`
- ✅ Updated Single Search tab to use these endpoints
- ✅ Search and status endpoints working correctly
- ✅ Data properly stored in `places_staging` and `place_search` tables

## Next Steps for Complete Functionality

### 1. Fix the Results Retrieval Endpoint

I noticed we have linter errors because `get_places_from_staging()` doesn't exist. Instead of creating new methods, we should update the router to use the existing `get_places_for_job()` method in the `PlacesStorageService` class. This approach maintains architectural consistency.

```python
@router.get("/places/job/{job_id}", response_model=Dict)
async def get_job_results(
    job_id: str,
    session: AsyncSession = Depends(get_session_dependency),
    current_user: Dict = Depends(get_current_user),
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0)
) -> Dict:
    """Get results for a specific search job."""
    # Use existing methods with correct formatting
    places_list, total_count = await places_storage_service.get_places_for_job(
        session=session,
        job_id=job_id,
        tenant_id=current_user.get("tenant_id") or DEFAULT_TENANT_ID,
        limit=limit,
        offset=offset
    )

    # Format results for the frontend
    return {
        "places": [convert_place_to_dict(place) for place in places_list],
        "total": total_count,
        "job_id": job_id
    }
```

### 2. Update the Results Tab in the Frontend

We need to modify the Results Viewer tab to use the new endpoint:

```javascript
// Update the fetchResults function in google-maps.html
function fetchResults() {
  // Get current job ID if available, or use last completed job
  const jobIdToUse = currentJobId || lastCompletedJobId;

  if (!jobIdToUse) {
    resultsTable.innerHTML =
      '<tr><td colspan="6" class="placeholder">No search has been performed yet</td></tr>';
    return;
  }

  fetch(`/api/v3/localminer-discoveryscan/places/job/${jobIdToUse}`, {
    headers: { Authorization: `Bearer ${jwt}` },
  })
    .then((response) => response.json())
    .then((data) => {
      // Display results
      updateResultsTable(data.places);
    });
}
```

### 3. Create a Search History Endpoint

This will let us see previous searches and avoid duplicates in the future:

```python
@router.get("/search/history", response_model=List[Dict])
async def get_search_history(
    session: AsyncSession = Depends(get_session_dependency),
    current_user: Dict = Depends(get_current_user),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0)
) -> List[Dict]:
    """Get search history for the current tenant."""
    # Implementation using existing functionality
```

### 4. Add "View Results" Button to Status Panel

When a search completes, add a button to jump directly to the Results tab:

```javascript
if (data.status === "complete") {
  clearInterval(statusCheckInterval);
  lastCompletedJobId = currentJobId;
  statusContent.innerHTML += `
        <button id="viewResultsBtn" class="button-primary">View Results</button>
    `;
  document
    .getElementById("viewResultsBtn")
    .addEventListener("click", function () {
      document.querySelector('[data-panel="resultsView"]').click();
      fetchResults();
    });
  searchBtn.disabled = false;
}
```

## Implementation Plan

1. First, implement the job results endpoint using existing service methods
2. Update the Results Viewer tab to use this endpoint
3. Add the "View Results" button to the status panel
4. Implement the search history endpoint (optional for now, but sets up future duplicate prevention)

This approach:

- Uses existing functionality where possible
- Minimizes architectural changes
- Creates a complete user flow from search to results
- Sets the stage for future enhancements like duplicate search prevention

Would you like me to start implementing this approach?
