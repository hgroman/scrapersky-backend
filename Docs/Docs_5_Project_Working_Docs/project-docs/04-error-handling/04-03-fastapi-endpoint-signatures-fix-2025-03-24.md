Below is a **comprehensive** document that explains:

1. **The Underlying Problem** (why the “args” and “kwargs” are showing up as required query parameters)
2. **The Mandatory (Correct) Approach** to fix it in a clean, “FastAPI standard” way
3. **Recommended Steps** for you (or your local AI) to implement the fix
4. **Potential Implementation Details** and expansions on each step

It’s verbose by design so you can hand it off as a blueprint.

---

# **Preserving Proper FastAPI Endpoint Signatures With a Global Error Wrapper**

## **1. The Problem Statement**

In FastAPI, each route’s function signature is used to auto-generate:

- The OpenAPI schema
- Automatic validation of query/body parameters

Thus, if the actual underlying function that handles the route has a signature like:

```python
async def scan_domain(
    request: SitemapScrapingRequest,
    background_tasks: BackgroundTasks,
    session: AsyncSession = Depends(...),
    tenant_id: str = Depends(...),
    current_user: dict = Depends(...)
):
    ...
```

then FastAPI knows those are (some in body, some in dependencies, etc.).

**But** when we apply a decorator like:

```python
def async_exception_handler(cls, func):
    async def wrapper(*args, **kwargs):
        ...
    return wrapper
```

we’re effectively replacing `scan_domain(...)` with a new function that has the signature:

```python
async def wrapper(*args, **kwargs):
    ...
```

FastAPI sees `wrapper(*args, **kwargs)` as the “true” route function. Consequently, it tries to interpret `args` and `kwargs` as **query parameters** with no defaults—hence the `"Field required"` errors for `args` and `kwargs`.

This is not an intended design of FastAPI, but a side effect of how it inspects function signatures for generating the request/response schema.

---

## **2. The “Right Way” (No Workarounds)**

**Goal**: We want to keep a global error handler that automatically wraps each route’s endpoint (for logging, capturing exceptions, returning a standard JSON error, etc.), **without** losing the original route signature that FastAPI uses for validation and the OpenAPI docs.

The **official** or “standard” way to do this in Python is:

1. **Preserve the original function signature** by using `functools.wraps(original_func)` on the wrapper function.
2. **Conditionally** handle synchronous vs. async, but always keep the signature from the original function in the final wrapped object.
3. **Ensure** we do not forcibly define `(*args, **kwargs)` if we can help it.

In short, `functools.wraps` copies over the original function’s signature (and other metadata like `__name__`, `__doc__`, etc.) so that FastAPI will see the correct parameters.

### **Example**

```python
import functools

@classmethod
def async_exception_handler(cls, func):
    @functools.wraps(func)  # This ensures the original signature is preserved.
    async def wrapper(*args, **kwargs):
        operation = func.__name__
        try:
            return await func(*args, **kwargs)
        except Exception as e:
            http_exception = cls.handle_exception(e, operation, include_traceback=True)
            raise http_exception
    return wrapper
```

Likewise for the sync version:

```python
@classmethod
def exception_handler(cls, func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        operation = func.__name__
        try:
            return func(*args, **kwargs)
        except Exception as e:
            http_exception = cls.handle_exception(e, operation, include_traceback=True)
            raise http_exception
    return wrapper
```

Then in `route_error_handler`, we do:

```python
@classmethod
def route_error_handler(cls, router):
    for route in router.routes:
        original_endpoint = route.endpoint
        if asyncio.iscoroutinefunction(original_endpoint):
            route.endpoint = cls.async_exception_handler(original_endpoint)
        else:
            route.endpoint = cls.exception_handler(original_endpoint)
    return router
```

Because of `@functools.wraps(...)`, the final `route.endpoint` remains an object that (to FastAPI) _appears_ to have the same parameter list as `scan_domain(...)`, not just `(*args, **kwargs)`.

**Result**:

- No spurious “args” and “kwargs” in query parameters.
- We get the same functionality of capturing exceptions globally.
- The OpenAPI docs match the real function signature.

---

## **3. **Recommended Steps** to Implement the Fix**

Below is a high-level plan you can give to your local AI or follow yourself:

1. **Open `error_service.py`** (where the `ErrorService` class lives):

   - Locate `cls.async_exception_handler(...)` and `cls.exception_handler(...)`.
   - Add `@functools.wraps(func)` immediately before the definition of each inner `wrapper(...)` function.

2. **Import `functools`**:

   - Make sure you have `import functools` at the top of `error_service.py`.
   - If it’s missing, add it.

3. **Confirm the Wrappers**:

   - Each wrapper function signature is currently `def wrapper(*args, **kwargs): ...`
   - That is fine. The critical piece is `@functools.wraps(func)` so that the final result is recognized by FastAPI as having the original signature from `func`.

4. **(Optional) Double-Check “async vs. sync”**:

   - If the original function is async, we use the `async_exception_handler`.
   - If sync, the `exception_handler`.
   - This is typically correct; just ensure the logic is correct if you rely on `asyncio.iscoroutinefunction()`.

5. **Remove or Re-check** any older references to “args, kwargs in query parameters” if you added them as a “workaround.” They’re no longer needed.

   - For instance, if at some point you tried `curl "...?args=&kwargs="`, remove that.
   - You want your request body or query parameters to match the actual function parameters.

6. **Redeploy** or **restart** your FastAPI app.
7. **Test** using a simple `curl` or any HTTP client. For the `/api/v3/sitemap/scan` route, you should now see either:
   - A **200** (or 202) if everything is working.
   - Or a **422** for a genuine reason (e.g. missing a field in the JSON body).
   - **But** you will _not_ see `args` or `kwargs` in the 422 error.

---

## **4. Potential Implementation Details & Caveats**

1. **Alternative: Global Exception Handlers**
   FastAPI already supports “global exception handlers” for common exception types via `@app.exception_handler(ExceptionType)`. If your main goal is to unify how errors appear, you could do it that way instead of wrapping each route. However, if you want per-route hooking or want additional “per-route” logic, your current approach with a route wrapper is fine.

2. **Preserving Docstrings**

   - `functools.wraps(func)` will preserve the docstring (`__doc__`) from the original function. That is beneficial if you rely on docstrings for your OpenAPI.

3. **Edge Cases**

   - If you do anything unusual with the route’s function object after you wrap it, keep in mind that the route now references the “wrapped” function. Usually, that’s not an issue.
   - If you do dynamic parameter injection (like reading a function’s signature at runtime to add parameters), that might conflict. But in a typical scenario, you’ll be fine.

4. **Conclusion**
   This approach is the **proper fix** in alignment with how typical Python decorators interact with frameworks that do signature inspection. It’s a known pattern in many frameworks (like Flask, Django, or even purely in Python reflection scenarios).

---

## **Example Final Implementation Snippet**

Below is a short snippet from your `ErrorService` that you can **literally** adopt (pseudocode):

```python
# error_service.py

import asyncio
import functools
import logging
from fastapi import HTTPException

logger = logging.getLogger(__name__)

class ErrorService:
    ...

    @classmethod
    def async_exception_handler(cls, func):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            operation = func.__name__
            try:
                return await func(*args, **kwargs)
            except Exception as e:
                http_exc = cls.handle_exception(e, operation, include_traceback=True)
                raise http_exc
        return wrapper

    @classmethod
    def exception_handler(cls, func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            operation = func.__name__
            try:
                return func(*args, **kwargs)
            except Exception as e:
                http_exc = cls.handle_exception(e, operation, include_traceback=True)
                raise http_exc
        return wrapper

    @classmethod
    def route_error_handler(cls, router):
        for route in router.routes:
            original_endpoint = route.endpoint
            if asyncio.iscoroutinefunction(original_endpoint):
                route.endpoint = cls.async_exception_handler(original_endpoint)
            else:
                route.endpoint = cls.exception_handler(original_endpoint)
        return router
```

That’s it. You’re done. Now every route in that router keeps its original signature from FastAPI’s perspective and still funnels through your centralized error-handling logic.

---

# **In Summary**

1. **Root Cause**: The generic wrapper’s `(*args, **kwargs)` overshadowed the original function’s typed signature, which forced FastAPI to treat them as required query parameters.
2. **Solution**: Use `@functools.wraps(original_func)` to preserve the underlying signature (the route’s real parameters).
3. **Implementation**: Adjust `error_service.py` so each wrapper function is decorated with `@functools.wraps(func)`. No more spurious “args” and “kwargs.”
4. **Outcome**: You maintain global error handling on each route, while preserving the correct OpenAPI docs and parameter handling that FastAPI expects.

You can now pass this “blueprint” to your local AI or developer to implement.
