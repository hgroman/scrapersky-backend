import logging
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
from src.routers import routers  # Import routers list from __init__.py

# Configure logging with environment-based levels
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL, logging.INFO),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()]
)

app = FastAPI(
    title="ScraperSky",
    description="A FastAPI-based web scraping service for extracting website metadata.",
    version="1.0.0"
)

# CORS Configuration
# WARNING: This configuration is for development purposes only!
# In production, replace '*' with specific origins for security
# Example for production: allow_origins=['https://your-domain.com']
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # TODO: Restrict this in production
    allow_credentials=True,
    allow_methods=["*"],  # TODO: Restrict to specific methods in production
    allow_headers=["*"],  # TODO: Restrict to specific headers in production
)

# Dynamically include all routers from the routers list
for router in routers:
    app.include_router(router)

# Serve static files with absolute path
static_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "static")
app.mount("/static", StaticFiles(directory=static_dir, html=True), name="static")

@app.get("/")
async def root():
    """Redirect root to static index page."""
    return RedirectResponse(url="/static/index.html")

@app.get("/sitemap-viewer")
async def sitemap_viewer():
    """Serve the sitemap viewer interface."""
    return RedirectResponse(url="/static/sitemap-viewer.html")

@app.get("/sitemap-data-viewer")
async def sitemap_data_viewer():
    """Serve the sitemap data viewer interface."""
    return RedirectResponse(url="/static/sitemap-data-viewer.html")

@app.get("/email-scanner")
async def email_scanner_view():
    """Serve the email scanner interface."""
    return RedirectResponse(url="/static/email-scanner.html")

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "operational"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
