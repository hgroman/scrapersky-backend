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

    # Determine if runtime import tracing is enabled via environment variable
    enable_tracing = os.getenv("ENABLE_IMPORT_TRACING", "false").lower() == "true"

    # Disable reload if tracing is enabled, otherwise use standard logic
    reload_enabled = (not enable_tracing) and (settings.environment.lower() == "development")

    if enable_tracing:
        print("INFO: ENABLE_IMPORT_TRACING=true, Uvicorn reload DISABLED.")
    else:
        print(
            f"INFO: ENABLE_IMPORT_TRACING=false/unset, Uvicorn reload={'ENABLED' if reload_enabled else 'DISABLED'}."
        )

    uvicorn.run(
        "src.main:app",
        host="0.0.0.0",
        port=port,
        reload=reload_enabled,  # Use the calculated reload status
    )
