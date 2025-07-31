### High-Level Goal

Strip **`src/main.py`** down to core API startup logic while **preserving** every auditing / tracing asset in a reusable “debug toolkit.”
No functionality is lost; it’s simply **relocated, guarded by a flag, and documented**.

---

## Implementation Plan for the Local AI

> **Target branch:** `refactor/debug-extraction` > **Coding style:** match existing Black-formatted code.
> **Commit granularity:** one commit per numbered step.

---

### 1 Create a dedicated `debug_tools` package

```
src/
 └── debug_tools/
      ├── __init__.py          # exports enable_debug(app)
      ├── runtime_tracer.py    # moved from src/config/
      ├── middleware.py        # holds debug_request_middleware
      └── routes.py            # /debug/routes & /debug/loaded-src-files
```

**`debug_tools/__init__.py`**

```python
from .middleware import debug_request_middleware
from .routes import router as debug_router
from .runtime_tracer import start_tracing, stop_tracing

def enable_debug(app):
    """Inject all debug utilities into a FastAPI app."""
    # lifespan hooks
    @app.on_event("startup")
    async def _start_tracing():
        start_tracing()

    @app.on_event("shutdown")
    async def _stop_tracing():
        stop_tracing()

    # middleware & routes
    app.middleware("http")(debug_request_middleware)
    app.include_router(debug_router, prefix="/debug", tags=["debug"])
```

---

### 2 Move & adapt the **runtime tracer**

- Cut-paste existing `src/config/runtime_tracer.py` into `debug_tools/runtime_tracer.py`.
- Remove any global logging calls; the router will expose results on demand.

---

### 3 Move the debug middleware and endpoints

- From **`main.py`** grab:

  - `debug_request_middleware`
  - `/debug/routes`
  - `/debug/loaded-src-files`

- Paste them into `debug_tools/middleware.py` and `debug_tools/routes.py` respectively and wire them through **`enable_debug()`** shown above.

---

### 4 Extract the huge inline HTML doc

1. Create **`static/docs.html`** (verbatim copy of the 400-line string).
2. Replace the whole block in **`main.py`** with:

```python
from fastapi.responses import FileResponse

@app.get("/api/documentation", include_in_schema=False)
def documentation():
    return FileResponse(Path(__file__).parent.parent / "static/docs.html",
                        media_type="text/html")
```

---

### 5 Refactor `main.py`

- **Delete**:

  - Working-directory printout
  - Any import-tracing startup/shutdown code
  - `debug_request_middleware` definition & registration
  - `/debug/*` endpoints
  - `debug=True` argument in `FastAPI()` call

- **Add**:

```python
from pydantic import BaseSettings

class Settings(BaseSettings):
    debug_mode: bool = False     # env FASTAPI_DEBUG_MODE
settings = Settings()

app = FastAPI(
    title="ScraperSky API",
    version="0.1.0",
    debug=settings.debug_mode,
)

if settings.debug_mode:
    from src.debug_tools import enable_debug
    enable_debug(app)
```

---

### 6 Update `run_server.py`

- Drop the `ENABLE_IMPORT_TRACING` env var handling—`debug_mode` now covers it.
- Ensure reload behaviour is unchanged.

---

### 7 Document everything (one-pager)

`docs/debug_tools_overview.md`

```
# ScraperSky Debug Toolkit

## Contents
- runtime_tracer – import/file load tracker
- debug_request_middleware – logs every request/response
- /debug/routes – shows registered routes
- /debug/loaded-src-files – lists traced modules/files

## Enabling
Set env FASTAPI_DEBUG_MODE=true **before** starting Uvicorn:

    FASTAPI_DEBUG_MODE=true poetry run python run_server.py

...
```

Link this file from `README.md`.

---

### 8 Delete dead code paths

- Remove unused imports left in `main.py`.
- Search for `start_tracing`, `stop_tracing`, and old debug endpoints across repo; purge or update tests.

---

### 9 Test matrix

| Scenario  | Command                                                   | Expected                                                         |
| --------- | --------------------------------------------------------- | ---------------------------------------------------------------- |
| **Prod**  | `poetry run python run_server.py`                         | No debug middleware; `/debug/*` 404; docs served from static     |
| **Debug** | `FASTAPI_DEBUG_MODE=true poetry run python run_server.py` | Trace starts; `/debug/routes` returns JSON; request logs visible |

Include pytest cases for both modes.

---

### 10 Commit & PR checklist

- [ ] All unit tests pass (`pytest -q`)
- [ ] `pre-commit run --all-files`
- [ ] Doc link verified
- [ ] PR description lists removed lines count & file size delta

---

## Hand-Off to the Local AI

_Feed it the exact step list above._
Tell it to create the branch, execute each commit, and push a PR.
Because every removal is guarded by version control + docs, you retain the 7-10 days of work while reclaiming a clean, maintainable **`main.py`**.
