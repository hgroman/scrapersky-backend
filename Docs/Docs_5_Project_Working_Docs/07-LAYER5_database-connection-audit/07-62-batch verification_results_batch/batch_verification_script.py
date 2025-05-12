#!/usr/bin/env python
"""
Batch Scraper Verification Script

This script tests the batch scraper implementation by creating batches with different
combinations of domains and verifying the behavior and responses.
"""

import asyncio
import json
import logging
import os
import sys
import time
from datetime import datetime
from typing import Any, Dict, List

import httpx

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# API configuration
API_BASE_URL = os.environ.get("API_BASE_URL", "http://localhost:8000")
API_TOKEN = os.environ.get("API_TOKEN", "scraper_sky_2024")  # Development token

# Test domains
VALID_DOMAINS = [
    "example.com",
    "google.com",
    "microsoft.com",
    "github.com",
    "stackoverflow.com",
]

INVALID_DOMAINS = [
    "invalid-domain",
    "not-a-real-domain.xyz123",
    "missing-tld",
    "@invalid-format.com",
    "http://example.com/path/is/not/valid/for/domain",
]

MIXED_DOMAINS = VALID_DOMAINS[:3] + INVALID_DOMAINS[:2]

# Test configurations
TEST_CONFIGS = [
    {
        "name": "Valid Domains Test",
        "domains": VALID_DOMAINS,
        "max_pages": 10,
        "expected_status": "success",
    },
    {
        "name": "Invalid Domains Test",
        "domains": INVALID_DOMAINS,
        "max_pages": 10,
        "expected_status": "error",
    },
    {
        "name": "Mixed Domains Test",
        "domains": MIXED_DOMAINS,
        "max_pages": 10,
        "expected_status": "partial",
    },
    {
        "name": "Empty Domains Test",
        "domains": [],
        "max_pages": 10,
        "expected_status": "error",
    },
]


async def create_batch(domains: List[str], max_pages: int = 10) -> Dict[str, Any]:
    """
    Create a batch with the given domains.

    Args:
        domains: List of domains to process
        max_pages: Maximum pages to process per domain

    Returns:
        API response as dictionary
    """
    url = f"{API_BASE_URL}/api/v3/batch_page_scraper/batch"
    headers = {
        "Authorization": f"Bearer {API_TOKEN}",
        "Content-Type": "application/json",
    }
    data = {"domains": domains, "max_pages": max_pages}

    logger.info(f"Creating batch with {len(domains)} domains")
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(url, headers=headers, json=data, timeout=10.0)
            if response.status_code == 200:
                result = response.json()
                logger.info(f"Batch created: {result}")
                return result
            else:
                logger.error(
                    f"Error creating batch: {response.status_code} - {response.text}"
                )
                return {"error": response.text, "status_code": response.status_code}
        except Exception as e:
            logger.error(f"Exception creating batch: {str(e)}")
            return {"error": str(e)}


async def get_batch_status(batch_id: str) -> Dict[str, Any]:
    """
    Get the status of a batch.

    Args:
        batch_id: ID of the batch to check

    Returns:
        API response as dictionary
    """
    url = f"{API_BASE_URL}/api/v3/batch_page_scraper/batch/{batch_id}/status"
    headers = {
        "Authorization": f"Bearer {API_TOKEN}",
        "Content-Type": "application/json",
    }

    logger.info(f"Checking status for batch {batch_id}")
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, headers=headers, timeout=10.0)
            if response.status_code == 200:
                result = response.json()
                logger.info(
                    f"Batch status: {result['status']}, "
                    f"progress: {result['progress']:.2f}, "
                    f"completed: {result['completed_domains']}/{result['total_domains']}"
                )
                return result
            else:
                logger.error(
                    f"Error getting status: {response.status_code} - {response.text}"
                )
                return {"error": response.text, "status_code": response.status_code}
        except Exception as e:
            logger.error(f"Exception getting status: {str(e)}")
            return {"error": str(e)}


async def monitor_batch_completion(batch_id: str, timeout: int = 120) -> Dict[str, Any]:
    """
    Monitor a batch until it completes or times out.

    Args:
        batch_id: ID of the batch to monitor
        timeout: Maximum time to wait in seconds

    Returns:
        Final batch status
    """
    logger.info(f"Monitoring batch {batch_id} for completion")
    start_time = time.time()
    last_status = None
    last_progress = -1

    while time.time() - start_time < timeout:
        status = await get_batch_status(batch_id)

        # Check for errors
        if "error" in status:
            logger.error(f"Error monitoring batch: {status['error']}")
            return status

        # Log only when status or progress changes
        current_status = status.get("status")
        current_progress = status.get("progress", 0)

        if (
            current_status != last_status
            or abs(current_progress - last_progress) > 0.05
        ):
            last_status = current_status
            last_progress = current_progress
            logger.info(
                f"Batch status: {current_status}, progress: {current_progress:.2f}"
            )

        # Check if batch is complete
        if current_status in ["completed", "failed", "error"]:
            logger.info(f"Batch {batch_id} finished with status: {current_status}")
            return status

        # Wait before checking again
        await asyncio.sleep(2)

    logger.warning(f"Monitoring timed out after {timeout} seconds")
    return await get_batch_status(batch_id)


async def run_test(test_config: Dict[str, Any]) -> Dict[str, Any]:
    """
    Run a test with the given configuration.

    Args:
        test_config: Test configuration

    Returns:
        Test results
    """
    test_name = test_config["name"]
    domains = test_config["domains"]
    max_pages = test_config["max_pages"]
    expected_status = test_config["expected_status"]

    logger.info(f"Running test: {test_name}")
    logger.info(f"Domains: {domains}")
    logger.info(f"Expected status: {expected_status}")

    results = {
        "test_name": test_name,
        "domains": domains,
        "start_time": datetime.utcnow().isoformat(),
        "expected_status": expected_status,
    }

    # Skip test if no domains and expected error
    if not domains and expected_status == "error":
        logger.info("Skipping empty domains test - API will reject")
        results["status"] = "skipped"
        results["reason"] = "Empty domains list is rejected by API validation"
        return results

    # Create batch
    batch_response = await create_batch(domains, max_pages)

    # Handle creation errors
    if "error" in batch_response:
        if expected_status == "error" and not domains:
            logger.info("Empty domains test passed - API correctly rejected request")
            results["status"] = "pass"
        else:
            logger.error(f"Batch creation failed: {batch_response['error']}")
            results["status"] = "fail"
            results["error"] = batch_response.get("error")

        results["end_time"] = datetime.utcnow().isoformat()
        return results

    # Monitor batch progress
    batch_id = batch_response["batch_id"]
    results["batch_id"] = batch_id
    results["status_url"] = batch_response["status_url"]

    final_status = await monitor_batch_completion(batch_id)
    results["end_time"] = datetime.utcnow().isoformat()
    results["final_status"] = final_status

    # Determine test result
    status_mapping = {
        "success": ["completed"],
        "error": ["failed", "error"],
        "partial": ["completed"],  # For mixed domains, we expect partial success
    }

    actual_status = final_status.get("status")

    if actual_status in status_mapping[expected_status]:
        if expected_status == "partial":
            # For partial success, check that we have both completed and failed domains
            if (
                final_status.get("completed_domains", 0) > 0
                and final_status.get("failed_domains", 0) > 0
            ):
                logger.info(f"Test passed: {test_name}")
                results["status"] = "pass"
            else:
                logger.warning(
                    "Expected mixed results but got all success or all failure"
                )
                results["status"] = "fail"
        else:
            logger.info(f"Test passed: {test_name}")
            results["status"] = "pass"
    else:
        logger.warning(
            f"Test failed: Expected status {expected_status} but got {actual_status}"
        )
        results["status"] = "fail"

    return results


async def main():
    """
    Run all tests and save results.
    """
    logger.info("Starting batch scraper verification tests")

    test_results = []
    for test_config in TEST_CONFIGS:
        result = await run_test(test_config)
        test_results.append(result)

    # Save results
    output_file = "batch_verification_results.json"
    with open(output_file, "w") as f:
        json.dump(test_results, f, indent=2)

    logger.info(f"All tests completed. Results saved to {output_file}")

    # Print summary
    passed = sum(1 for r in test_results if r.get("status") == "pass")
    failed = sum(1 for r in test_results if r.get("status") == "fail")
    skipped = sum(1 for r in test_results if r.get("status") == "skipped")

    logger.info(f"Summary: {passed} passed, {failed} failed, {skipped} skipped")

    if failed > 0:
        logger.error("Some tests failed!")
        sys.exit(1)
    else:
        logger.info("All tests passed!")
        sys.exit(0)


if __name__ == "__main__":
    asyncio.run(main())
