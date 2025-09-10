#!/usr/bin/env python
"""
Debug script to test API endpoints directly and diagnose issues with ScraperSky backend.
"""

import asyncio
import json
import logging
import os
import sys
from urllib.parse import urljoin
import jwt
import datetime

import httpx

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()],
)
logger = logging.getLogger("debug_api")

# API configuration
BASE_URL = "http://localhost:8000"  # Adjust if your server is on a different port
API_VERSION = "v3"

# Endpoints to test
ENDPOINTS = [
    # Health check endpoints (no auth required)
    {"path": "/health", "method": "GET", "auth": False, "name": "Health Check"},
    {"path": "/health/db", "method": "GET", "auth": False, "name": "DB Health Check"},
    # API endpoints (auth required)
    {
        "path": f"/api/{API_VERSION}/domains",
        "method": "GET",
        "auth": True,
        "name": "Domains List",
    },
    {
        "path": f"/api/{API_VERSION}/local-businesses",
        "method": "GET",
        "auth": True,
        "name": "Local Businesses",
    },
    {
        "path": f"/api/{API_VERSION}/sitemap",
        "method": "GET",
        "auth": True,
        "name": "Sitemap List",
    },
    {
        "path": f"/api/{API_VERSION}/sitemap-files",
        "method": "GET",
        "auth": True,
        "name": "Sitemap Files",
    },
]

def generate_jwt():
    secret = os.environ.get("SUPABASE_JWT_SECRET")
    if not secret:
        raise ValueError("SUPABASE_JWT_SECRET not set in environment")
    payload = {
        "sub": "56adcb98-d218-40ad-8a1c-997c54d83154",
        "role": "authenticated",
        "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=1)
    }
    return jwt.encode(payload, secret, algorithm="HS256")


async def test_endpoint(client, endpoint, token):
    """Test a single endpoint and return the result."""
    url = urljoin(BASE_URL, endpoint["path"])
    headers = {}

    if endpoint["auth"]:
        headers["Authorization"] = f"Bearer {token}"

    logger.info(f"Testing {endpoint['name']} - {endpoint['method']} {url}")

    try:
        if endpoint["method"] == "GET":
            response = await client.get(url, headers=headers)
        elif endpoint["method"] == "POST":
            response = await client.post(url, headers=headers, json={})
        else:
            logger.error(f"Unsupported method: {endpoint['method']}")
            return

        status_code = response.status_code
        logger.info(f"Status code: {status_code}")

        try:
            response_json = response.json()
            logger.info(f"Response: {json.dumps(response_json, indent=2)[:500]}...")
        except Exception:
            logger.info(f"Response text: {response.text[:500]}...")

        return {
            "endpoint": endpoint["name"],
            "url": url,
            "status_code": status_code,
            "success": 200 <= status_code < 300,
        }
    except Exception as e:
        logger.error(f"Error testing {url}: {str(e)}")
        return {
            "endpoint": endpoint["name"],
            "url": url,
            "status_code": None,
            "success": False,
            "error": str(e),
        }


async def main():
    """Main function to test all endpoints."""
    logger.info("Starting API endpoint tests")
    logger.info(f"Base URL: {BASE_URL}")

    # Check if server is running
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(urljoin(BASE_URL, "/health"))
            if response.status_code != 200:
                logger.error(f"Server health check failed: {response.status_code}")
                return
            logger.info("Server is running")
    except Exception as e:
        logger.error(f"Could not connect to server: {str(e)}")
        logger.error("Make sure the server is running before running this script")
        return

    token = generate_jwt()
    print(f"Generated JWT: {token}")

    results = []
    async with httpx.AsyncClient(timeout=10.0) as client:
        for endpoint in ENDPOINTS:
            result = await test_endpoint(client, endpoint, token)
            if result:
                results.append(result)

    # Print summary
    logger.info("\n===== TEST RESULTS SUMMARY =====")
    success_count = sum(1 for r in results if r.get("success", False))
    logger.info(f"Successful endpoints: {success_count}/{len(results)}")

    for result in results:
        status = "✅ SUCCESS" if result.get("success", False) else "❌ FAILED"
        logger.info(
            f"{status} - {result['endpoint']} ({result.get('status_code', 'N/A')})"
        )

    # Check for common issues
    if success_count == 0:
        logger.warning("\n===== POTENTIAL ISSUES =====")
        logger.warning("1. Server might not be running correctly")
        logger.warning("2. Authentication token might be invalid")
        logger.warning("3. Database connection might be failing")
        logger.warning("4. API versioning might be inconsistent")
        logger.warning("\nCheck server logs for more details")


if __name__ == "__main__":
    if "--get-token" in sys.argv:
        print(generate_jwt())
    else:
        asyncio.run(main())