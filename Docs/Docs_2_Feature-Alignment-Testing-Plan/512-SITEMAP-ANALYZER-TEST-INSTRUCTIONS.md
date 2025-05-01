# SITEMAP ANALYZER COMPREHENSIVE TEST INSTRUCTIONS

## OBJECTIVE
Test the entire sitemap analyzer functionality end-to-end, focusing on both backend API endpoints and frontend integration. We will not stop until the page is fully functional.

## ENDPOINTS TO TEST
Test ALL of these endpoints thoroughly to make sure they work properly:

1. SINGLE DOMAIN ANALYSIS:
   - Endpoint: `/api/v1/sitemap-analyzer/analyze` (POST)
   - Test with valid domain, invalid domain, and edge cases
   - Verify job_id is returned and properly formatted

2. SINGLE DOMAIN STATUS CHECK:
   - Endpoint: `/api/v1/sitemap-analyzer/status/{job_id}` (GET)
   - Test with valid job_id, invalid job_id
   - Verify all status states (pending, running, completed, failed)

3. BATCH DOMAIN ANALYSIS:
   - Endpoint: `/api/v3/batch_page_scraper/batch` (POST)
   - Test with single domain, multiple domains, and invalid domains
   - Verify batch_id is returned properly

4. BATCH STATUS CHECK:
   - Endpoint: `/api/v3/batch_page_scraper/batch/{batch_id}/status` (GET)
   - Test with valid batch_id, invalid batch_id
   - Verify all batch states and progress tracking

## FRONT-END INTEGRATION TESTS
Verify the sitemap-analyzer.html page works correctly:

1. Start the application with `python -m src.main`
2. Navigate to http://localhost:8000/static/sitemap-analyzer.html
3. Test the SINGLE DOMAIN form:
   - Enter a valid domain (e.g., example.com)
   - Submit and check if status polling works
   - Verify results are displayed correctly when complete
   - Try an invalid domain, check error handling

4. Test the BATCH ANALYSIS form:
   - Enter multiple domains (one per line)
   - Set concurrency to 3
   - Submit and check if status polling works
   - Verify batch progress is displayed correctly
   - Verify completed batch results are shown

## API TEST SCRIPT
Create a Python script that tests all endpoints programmatically:

```python
import requests
import asyncio
import time
import json

API_BASE = "http://localhost:8000"
TEST_DOMAIN = "example.com"
TEST_DOMAINS = ["example.com", "example.org", "example.net"]
DEFAULT_HEADERS = {
    "Content-Type": "application/json",
    "Authorization": "Bearer scraper_sky_2024"
}

def test_single_domain():
    """Test the single domain analysis endpoint"""
    print("\n📋 TESTING SINGLE DOMAIN ANALYSIS")
    
    # Test valid domain
    payload = {
        "domain": TEST_DOMAIN,
        "tenant_id": "550e8400-e29b-41d4-a716-446655440000",
        "follow_robots_txt": True,
        "extract_urls": True,
        "max_urls_per_sitemap": 10000
    }
    
    response = requests.post(
        f"{API_BASE}/api/v1/sitemap-analyzer/analyze",
        headers=DEFAULT_HEADERS,
        json=payload
    )
    
    print(f"Status Code: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"Response: {json.dumps(data, indent=2)}")
        
        # Now test status endpoint
        job_id = data.get("job_id")
        if job_id:
            test_job_status(job_id)
    else:
        print(f"Error: {response.text}")

def test_job_status(job_id):
    """Test the job status endpoint with polling"""
    print(f"\n📋 TESTING JOB STATUS FOR: {job_id}")
    
    max_attempts = 30
    attempts = 0
    
    while attempts < max_attempts:
        response = requests.get(
            f"{API_BASE}/api/v1/sitemap-analyzer/status/{job_id}",
            headers=DEFAULT_HEADERS
        )
        
        if response.status_code == 200:
            data = response.json()
            status = data.get("status")
            print(f"Status: {status} - Progress: {data.get('progress', 0)}")
            
            if status in ["completed", "failed"]:
                print(f"Final Status: {json.dumps(data, indent=2)}")
                break
        else:
            print(f"Error checking status: {response.text}")
            break
        
        attempts += 1
        time.sleep(2)  # Poll every 2 seconds

def test_batch_analysis():
    """Test the batch domain analysis endpoint"""
    print("\n📋 TESTING BATCH DOMAIN ANALYSIS")
    
    payload = {
        "domains": TEST_DOMAINS,
        "tenant_id": "550e8400-e29b-41d4-a716-446655440000",
        "follow_robots_txt": True,
        "extract_urls": True,
        "max_urls_per_sitemap": 10000,
        "max_concurrent_jobs": 3
    }
    
    response = requests.post(
        f"{API_BASE}/api/v1/sitemap-analyzer/batch",
        headers=DEFAULT_HEADERS,
        json=payload
    )
    
    print(f"Status Code: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"Response: {json.dumps(data, indent=2)}")
        
        # Now test batch status endpoint
        batch_id = data.get("batch_id")
        if batch_id:
            test_batch_status(batch_id)
    else:
        print(f"Error: {response.text}")

def test_batch_status(batch_id):
    """Test the batch status endpoint with polling"""
    print(f"\n📋 TESTING BATCH STATUS FOR: {batch_id}")
    
    max_attempts = 30
    attempts = 0
    
    while attempts < max_attempts:
        response = requests.get(
            f"{API_BASE}/api/v1/sitemap-analyzer/batch-status/{batch_id}",
            headers=DEFAULT_HEADERS
        )
        
        if response.status_code == 200:
            data = response.json()
            status = data.get("status")
            completed = data.get("completed_domains", 0)
            total = data.get("total_domains", 0)
            
            print(f"Status: {status} - Progress: {data.get('progress', 0)} - Completed: {completed}/{total}")
            
            if status in ["completed", "failed", "partial"]:
                print(f"Final Status: {json.dumps(data, indent=2)}")
                break
        else:
            print(f"Error checking batch status: {response.text}")
            break
        
        attempts += 1
        time.sleep(2)  # Poll every 2 seconds

if __name__ == "__main__":
    print("🚀 SITEMAP ANALYZER API TEST SCRIPT")
    print(f"Base URL: {API_BASE}")
    
    # Test individual endpoints
    test_single_domain()
    test_batch_analysis()
    
    print("\n✅ ALL TESTS COMPLETED")
```

## BROWSER CONSOLE DEBUGGING
While testing the frontend, monitor browser console for JavaScript errors:

1. Open Developer Tools (F12 or Ctrl+Shift+I)
2. Go to Console tab
3. Check for any errors during form submission or status polling
4. If errors occur, examine network requests to identify the specific failing API calls

## SERVER-SIDE LOGGING
Monitor the server logs for detailed error information:

1. Start the server with extra verbose logging:
   ```
   LOGLEVEL=DEBUG python -m src.main
   ```
2. Watch for any error messages related to the sitemap analyzer
3. Check transaction boundaries in logs
4. Verify successful database operations

## DATABASE VERIFICATION
Verify data is properly stored in the database:

1. Connect to the database and check the relevant tables:
   - Check job tracking tables for newly created jobs
   - Verify that job status is updated correctly
   - Check that results are stored properly for completed jobs

## ERROR SCENARIOS TO TEST
Test all these error cases to ensure proper handling:

1. Invalid domain formats
2. Non-existent domains
3. Domains without sitemaps
4. Unauthorized access (invalid/missing API key)
5. Malformed request payloads
6. Connection timeouts to target domains
7. Extremely large sitemaps
8. Concurrent requests to same domain

## DOCUMENTATION VERIFICATION
Make sure API documentation matches implementation:

1. Check that OpenAPI documentation is correctly generated
2. Verify response models match actual responses
3. Ensure all parameters are properly documented

## FINAL VERIFICATION CHECKLIST
Complete this checklist when testing is done:

- [ ] Single domain analysis works end-to-end
- [ ] Batch domain analysis works end-to-end
- [ ] Status polling works correctly
- [ ] Results are displayed properly on the frontend
- [ ] Error handling is robust for all scenarios
- [ ] Backend logs show proper transaction management
- [ ] Data is properly stored in database
- [ ] No JavaScript console errors
- [ ] Performance is acceptable
- [ ] Documentation matches implementation

## NOTES
- DO NOT stop testing until the page is fully functional
- Document any issues found in detail
- Focus on fixing critical path functionality first
- Remember the frontend is expecting specific response formats