# AI Guide: FastAPI Router Prefix Convention

**Document ID:** 23-FASTAPI_ROUTER_PREFIX_CONVENTION
**Status:** Active
**Created:** April 2025
**Author:** Gemini Assistant & User

## 1. Objective

To establish a clear and consistent convention for including FastAPI `APIRouter` instances in `src/main.py`, specifically regarding the use of the `prefix` argument in `app.include_router()`. Adhering to this convention prevents `404 Not Found` errors caused by incorrect or duplicated URL prefixes.

## 2. The Problem

FastAPI allows defining a `prefix` both when creating an `APIRouter` instance within its module (e.g., `router = APIRouter(prefix="/api/v3/myresource")`) and when including that router in the main `FastAPI` app instance (e.g., `app.include_router(my_router, prefix="/api/v3")`).

If a prefix is defined in _both_ places, FastAPI concatenates them, leading to unexpected and incorrect final route paths (e.g., `/api/v3/api/v3/myresource/endpoint`), resulting in `404 Not Found` errors when the frontend tries to call the expected path (e.g., `/api/v3/myresource/endpoint`).

This issue has occurred multiple times, particularly with routers that define their _full_ path, including the `/api/v3` base.

## 3. The Convention

**Rule:** Before including a router in `src/main.py`, **ALWAYS CHECK** how the `prefix` is defined within the router's own source file.

There are two scenarios:

**Scenario 1: Router Defines the FULL Prefix (including `/api/v3`)**

- **Router Definition Example (`src/routers/some_router.py`):**
  ```python
  router = APIRouter(prefix="/api/v3/specific-resource", tags=["Specific Resource"])
  ```
- **Correct Inclusion in `src/main.py`:** Include the router **WITHOUT** adding the `prefix` argument, as it's already fully defined.
  ```python
  # Correct: Prefix is defined within the router itself
  app.include_router(some_router_instance)
  ```
- **Current Code Example (`src/main.py`):**

  ```python
  # google_maps_api_router defines '/api/v3/localminer-discoveryscan'
  app.include_router(google_maps_api_router)

  # local_businesses_api_router defines '/api/v3/local-businesses'
  app.include_router(local_businesses_api_router)
  ```

**Scenario 2: Router Defines ONLY the Resource-Specific Prefix (NOT including `/api/v3`)**

- **Router Definition Example (`src/routers/another_router.py`):**
  ```python
  # Note: Only includes the resource part, assumes base prefix is added elsewhere
  router = APIRouter(prefix="/another-resource", tags=["Another Resource"])
  ```
- **Correct Inclusion in `src/main.py`:** Include the router **WITH** `prefix="/api/v3"` to prepend the standard API base path.
  ```python
  # Correct: Add the standard /api/v3 prefix
  app.include_router(another_router_instance, prefix="/api/v3", tags=["Another Resource"])
  ```
- **Current Code Example (`src/main.py`):**

  ```python
  # modernized_sitemap_api_router likely defines '/sitemap/...'
  app.include_router(modernized_sitemap_api_router, prefix="/api/v3", tags=["Sitemap"])

  # profile_api_router likely defines '/profile/...'
  app.include_router(profile_api_router, prefix="/api/v3", tags=["Profile"])
  ```

## 4. Reference Comment in `src/main.py`

The following comment block exists in `src/main.py` directly above the `app.include_router` calls as a high-visibility reminder:

```python
# --- IMPORTANT ROUTER PREFIX CONVENTION --- #
# When including routers below:
# 1. If the router DEFINES its own FULL prefix (including '/api/v3'),
#    include it WITHOUT adding the prefix here.
#    Example: google_maps_api_router defines '/api/v3/localminer-discoveryscan',
#             so it's included as `app.include_router(google_maps_api_router)`.
# 2. If the router only defines the RESOURCE-SPECIFIC part of its prefix
#    (e.g., '/sitemap'), then include it WITH `prefix="/api/v3"` here.
#    Example: `app.include_router(modernized_sitemap_api_router, prefix="/api/v3", ...)`
# *** Failure to follow this causes 404 errors. Double-check prefixes! ***
# --- END IMPORTANT ROUTER PREFIX CONVENTION --- #
```

## 5. Conclusion

Strict adherence to this convention is mandatory when adding or modifying router registrations in `src/main.py`. Always verify the prefix definition within the specific router module being included.
