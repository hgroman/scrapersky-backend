import requests
import time
import argparse
import json
import os

def get_all_endpoints(base_url):
    """Get all endpoints from OpenAPI schema"""
    openapi_url = f"{base_url}/openapi.json"
    try:
        response = requests.get(openapi_url)
        response.raise_for_status()
        schema = response.json()

        endpoints = []
        for path, methods in schema.get("paths", {}).items():
            for method in methods:
                if method.lower() in ["get", "post", "put", "delete", "patch"]:
                    endpoints.append((method.upper(), path))

        return endpoints
    except Exception as e:
        print(f"Failed to get OpenAPI schema: {str(e)}")
        return []

def exercise_all_endpoints(base_url, delay=0.5):
    """Call all API endpoints"""
    endpoints = get_all_endpoints(base_url)
    print(f"Found {len(endpoints)} endpoints to test")

    for method, path in endpoints:
        url = f"{base_url}{path}"
        try:
            print(f"Testing {method} {path}")

            # For GET requests without parameters
            if method == "GET" and "{" not in path:
                response = requests.get(url)
                status = response.status_code
                print(f"  Response: {status}")
            else:
                print(f"  Skipping (requires parameters or not GET)")

            # Add delay to avoid overwhelming the server
            time.sleep(delay)

        except Exception as e:
            print(f"  Error: {str(e)}")

def main():
    parser = argparse.ArgumentParser(description="Exercise API endpoints to trace module usage")
    parser.add_argument("--url", default="http://localhost:8000", help="Base URL of the API")
    parser.add_argument("--wait", type=int, default=30, help="Seconds to wait for scheduler tasks")
    args = parser.parse_args()

    print(f"Starting endpoint testing for {args.url}")
    exercise_all_endpoints(args.url)

    print(f"Waiting {args.wait} seconds for scheduled tasks to run...")
    time.sleep(args.wait)

    print("Test complete - check reports/runtime_loaded_files.txt for results")

if __name__ == "__main__":
    main()
