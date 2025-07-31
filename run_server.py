import os
import sys

import uvicorn

# Add src directory to Python path
src_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "src")
sys.path.append(src_dir)

from src.config.settings import settings

if __name__ == "__main__":
    # Get port from environment variable for Render compatibility
    port = int(os.getenv("PORT", "8000"))

    # Determine if debug mode is enabled via environment variable
    debug_mode = os.getenv("FASTAPI_DEBUG_MODE", "false").lower() == "true"

    # Disable reload if debug mode is enabled, otherwise use standard logic
    reload_enabled = (not debug_mode) and (
        settings.environment.lower() == "development"
    )

    if debug_mode:
        print("INFO: FASTAPI_DEBUG_MODE=true, Uvicorn reload DISABLED.")
    else:
        print(
            f"INFO: FASTAPI_DEBUG_MODE=false/unset, Uvicorn reload={'ENABLED' if reload_enabled else 'DISABLED'}."
        )

    uvicorn.run(
        "src.main:app",
        host="0.0.0.0",
        port=port,
        reload=reload_enabled,  # Use the calculated reload status
    )
