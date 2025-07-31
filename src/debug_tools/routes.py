from typing import List

from fastapi import APIRouter
from fastapi.routing import APIRoute

from .runtime_tracer import get_loaded_files

router = APIRouter()


@router.get("/routes")
def list_routes():
    """
    List all registered routes in the FastAPI application.

    Returns a list of route information including:
    - path: The URL path pattern
    - name: The route name
    - methods: HTTP methods supported by the route

    This is useful for debugging routing issues and understanding
    the complete API surface area.
    """
    from src.main import app  # Import here to avoid circular imports

    url_list = []
    for route in app.routes:
        route_info = {
            "path": getattr(route, "path", "N/A"),
            "name": getattr(route, "name", "N/A"),
        }
        # Check specifically for APIRoute to safely access methods
        if isinstance(route, APIRoute):
            route_info["methods"] = list(route.methods)
        else:
            route_info["methods"] = []
        url_list.append(route_info)
    return url_list


@router.get("/loaded-src-files", response_model=List[str])
async def get_loaded_src_files_endpoint():
    """
    Returns the list of unique /app/src/*.py files loaded during runtime.

    This endpoint provides insight into which Python files from the src/
    directory have been imported and executed. This is useful for:
    - Understanding code loading patterns
    - Identifying unused files
    - Debugging import issues
    - Performance analysis

    Returns:
        List[str]: Sorted list of absolute file paths that were loaded
    """
    files = get_loaded_files()
    return sorted(list(files))
