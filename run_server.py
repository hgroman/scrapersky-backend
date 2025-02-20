import os
import sys
import uvicorn

# Add src directory to Python path
src_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "src")
sys.path.append(src_dir)

if __name__ == "__main__":
    # Get port from environment variable for Render compatibility
    port = int(os.getenv("PORT", "8000"))
    
    # Disable reload in production
    reload = os.getenv("ENVIRONMENT", "development") == "development"
    
    uvicorn.run(
        "src.main:app",
        host="0.0.0.0",
        port=port,
        reload=reload
    )
