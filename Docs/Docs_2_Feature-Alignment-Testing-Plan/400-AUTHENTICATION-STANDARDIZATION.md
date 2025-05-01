# Authentication Standardization

## Issue
Different routers in the ScraperSky backend were using inconsistent authentication patterns, causing the Google Maps API endpoint to reject the same development token that works with other endpoints like the Batch Page Scraper.

## Root Cause
The `google_maps_api.py` router was directly using `get_current_user` from the auth service without the development mode checks that were present in `batch_page_scraper.py`.

1. In `batch_page_scraper.py`, there was an explicit `is_development_mode()` check and a custom `get_development_user()` function.
2. In `google_maps_api.py`, the standard dependency was used which didn't have the same development token handling.

## Solution
A standardized development mode check was implemented in the Google Maps API router:

1. Added explicit development mode detection with `is_development_mode()`
2. Added a `get_development_user()` function that returns a user with necessary permissions
3. Used a conditional dependency selection based on development mode
4. Updated all router endpoints to use the new dependency

The change allows the development token "scraper_sky_2024" to work consistently across all endpoints, making testing and development easier.

## Implementation Details
1. Added imports for `os` and `settings`
2. Defined `DEFAULT_TENANT_ID` consistent with other routers
3. Added `is_development_mode()` function that checks environment variables
4. Added `get_development_user()` function with appropriate permissions
5. Created a conditional `user_dependency` selection
6. Updated all endpoints to use `user_dependency` instead of direct dependency on `get_current_user`

## Testing
The implementation was tested with the development token and confirmed to work consistently across all Google Maps API endpoints.

## Future Recommendations
1. Create a shared authentication module that implements this pattern uniformly
2. Refactor all routers to use this shared module for consistent authentication behavior
3. Document the development token and its usage patterns for all developers