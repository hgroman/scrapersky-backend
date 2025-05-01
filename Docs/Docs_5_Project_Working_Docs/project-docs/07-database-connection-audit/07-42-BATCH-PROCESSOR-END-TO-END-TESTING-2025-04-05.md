# 07-42-BATCH-PROCESSOR-END-TO-END-TESTING-2025-04-05

## Overview

This document establishes a comprehensive testing protocol for the batch processor service, focusing on end-to-end validation from CSV input through final database storage. Following the recent modernization work (ref: 07-41-BATCH-PROCESSOR-SERVICE-MODERNIZATION-IMPLEMENTATION-2025-04-01), we need to verify that the entire processing pipeline functions correctly with the new UUID standardization.

**Date**: April 5, 2025
**Component**: Batch Processor Service
**Test Environment**: Development Environment (`localhost:8001`)

## Testing Objectives

1. Verify the complete data flow from CSV submission to database storage
2. Confirm UUID handling throughout the pipeline
3. Trace SQL queries at each processing stage
4. Validate data integrity across all database tables
5. Ensure error handling for invalid inputs

## Prerequisites

- Development environment with running API server (`localhost:8001`)
- Database inspection tools (`simple_inspect.py`)
- Prepared test CSV files (valid and invalid samples)
- curl or Postman for API testing
- SQL query logging enabled for tracing

## Test Environment Setup

### 1. Enable SQL Query Logging

First, enable detailed SQL query logging to trace all database operations:

```python
# Add to src/session/async_session.py temporarily during testing
import logging
logging.basicConfig()
logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)
```

### 2. Prepare Test CSV Files

Create test CSV files with the following characteristics:

**valid_domains.csv**:

```csv
domain
example.com
test-domain.org
valid-site.net
```

**invalid_domains.csv**:

```csv
domain
example..com
not@valid
test-domain.org
```

**large_batch.csv**:
At least 50 domains to test batch processing behavior

### 3. Verify Database Initial State

Check relevant tables before testing:

```bash
python scripts/db/simple_inspect.py batch_jobs
python scripts/db/simple_inspect.py domains
python scripts/db/simple_inspect.py jobs
```

Record the counts and UUIDs of existing records for comparison after tests.

## Test Case 1: Valid Batch Submission

### Step 1: Submit CSV File

```bash
curl -X POST http://localhost:8001/api/v3/batch_page_scraper/upload \
  -F "file=@valid_domains.csv" \
  -H "Content-Type: multipart/form-data" \
  -v > submission_response.json
```

**Verification Points**:

- Response contains a valid UUID for `batch_id`
- Response includes status URL for batch
- Status code is 200
- Response time is acceptable

Extract the `batch_id` for later steps:

```bash
BATCH_ID=$(cat submission_response.json | jq -r .batch_id)
echo "Testing with batch_id: $BATCH_ID"
```

### Step 2: Verify Database Insertion - First Stage

Immediately check the database to verify the batch was created with correct UUID format:

```bash
python scripts/db/simple_inspect.py batch_jobs --limit 1
```

**SQL Verification Query**:

```sql
SELECT * FROM batch_jobs
WHERE batch_id = '$BATCH_ID'::uuid;
```

**Verification Points**:

- `batch_id` is stored as a UUID type (not VARCHAR)
- `total_domains` matches CSV file count (3)
- `status` is set to "pending" initially
- `tenant_id` is set correctly

### Step 3: Check Initial Status via API

```bash
curl -X GET "http://localhost:8001/api/v3/batch_page_scraper/batch/$BATCH_ID/status" \
  -H "Content-Type: application/json" \
  -v > initial_status.json
```

**Verification Points**:

- Status response JSON contains proper UUID format for `batch_id`
- Initial status shows as "pending"
- `completed_domains` is 0
- `total_domains` matches expected count

### Step 4: Wait for Processing to Begin

```bash
# Sleep for 5 seconds to allow background processing to start
sleep 5

curl -X GET "http://localhost:8001/api/v3/batch_page_scraper/batch/$BATCH_ID/status" \
  -H "Content-Type: application/json" \
  -v > processing_status.json
```

**Verification Points**:

- Status should either be "running" or show progress > 0
- `domain_statuses` should contain entries for the domains

### Step 5: Trace Domain Job Creation

Check the jobs table to verify jobs were created for each domain:

```bash
python scripts/db/simple_inspect.py jobs --limit 10
```

**SQL Verification Query**:

```sql
SELECT * FROM jobs
WHERE batch_id = '$BATCH_ID'::uuid
ORDER BY created_at DESC;
```

**Verification Points**:

- Job entries exist for each domain in the CSV
- Each job has the correct `batch_id` as UUID
- Job statuses are appropriate (pending, running, or complete)

### Step 6: Wait for Completion and Verify Final Status

```bash
# Poll status every 5 seconds until complete or timeout after 2 minutes
TIMEOUT=120
ELAPSED=0
STATUS="pending"

while [[ "$STATUS" == "pending" || "$STATUS" == "running" ]] && [[ $ELAPSED -lt $TIMEOUT ]]; do
  sleep 5
  ELAPSED=$((ELAPSED+5))

  curl -s -X GET "http://localhost:8001/api/v3/batch_page_scraper/batch/$BATCH_ID/status" \
    -H "Content-Type: application/json" > current_status.json

  STATUS=$(cat current_status.json | jq -r .status)
  echo "Current status: $STATUS ($ELAPSED seconds elapsed)"
done

cat current_status.json | jq > final_status.json
```

**Verification Points**:

- Final status is "complete" or "partial" (if some domains failed)
- `progress` is 1.0 (100%)
- `completed_domains` plus `failed_domains` equals `total_domains`
- `processing_time` is recorded

### Step 7: Verify Domain Table Data

Check that domain data was properly inserted:

```bash
python scripts/db/simple_inspect.py domains --limit 10
```

**SQL Verification Query**:

```sql
SELECT * FROM domains
WHERE batch_id = '$BATCH_ID'::uuid;
```

**Verification Points**:

- Domains from CSV are present in the table
- Each domain record has the correct `batch_id` as UUID
- Domain records contain expected metadata
- No duplicate domain entries for this batch

## Test Case 2: Invalid Input Handling

Repeat the test with `invalid_domains.csv` to verify error handling:

### Step 1: Submit Invalid CSV

```bash
curl -X POST http://localhost:8001/api/v3/batch_page_scraper/upload \
  -F "file=@invalid_domains.csv" \
  -H "Content-Type: multipart/form-data" \
  -v > invalid_submission_response.json
```

Extract the new batch ID:

```bash
INVALID_BATCH_ID=$(cat invalid_submission_response.json | jq -r .batch_id)
```

### Step 2: Verify Error Handling

```bash
# Wait for processing to complete
sleep 30

curl -X GET "http://localhost:8001/api/v3/batch_page_scraper/batch/$INVALID_BATCH_ID/status" \
  -H "Content-Type: application/json" \
  -v > invalid_status.json
```

**Verification Points**:

- Valid domains are processed successfully
- Invalid domains show appropriate error messages
- Final status reflects partial completion
- Error details are logged in domain_statuses

### Step 3: Check Database Error Records

```bash
python scripts/db/simple_inspect.py batch_jobs --limit 1
```

**SQL Verification Query**:

```sql
SELECT * FROM batch_jobs
WHERE batch_id = '$INVALID_BATCH_ID'::uuid;
```

**Verification Points**:

- `failed_domains` count matches number of invalid domains
- Error information is stored appropriately
- Valid domains from the CSV are still processed

## Test Case 3: Large Batch Processing

Test with a larger CSV file to verify scaling:

### Step 1: Submit Large Batch

```bash
curl -X POST http://localhost:8001/api/v3/batch_page_scraper/upload \
  -F "file=@large_batch.csv" \
  -H "Content-Type: multipart/form-data" \
  -v > large_submission_response.json
```

Extract the batch ID:

```bash
LARGE_BATCH_ID=$(cat large_submission_response.json | jq -r .batch_id)
```

### Step 2: Monitor Processing

```bash
# Monitor status every 15 seconds for up to 5 minutes
TIMEOUT=300
ELAPSED=0
LAST_PROGRESS=0

while [[ $ELAPSED -lt $TIMEOUT ]]; do
  sleep 15
  ELAPSED=$((ELAPSED+15))

  curl -s -X GET "http://localhost:8001/api/v3/batch_page_scraper/batch/$LARGE_BATCH_ID/status" \
    -H "Content-Type: application/json" > large_current_status.json

  CURRENT_PROGRESS=$(cat large_current_status.json | jq -r .progress)
  CURRENT_STATUS=$(cat large_current_status.json | jq -r .status)

  echo "Progress: $CURRENT_PROGRESS, Status: $CURRENT_STATUS ($ELAPSED seconds elapsed)"

  if [[ "$CURRENT_STATUS" == "complete" || "$CURRENT_STATUS" == "failed" ]]; then
    break
  fi

  # Verify progress is increasing
  if (( $(echo "$CURRENT_PROGRESS > $LAST_PROGRESS" | bc -l) )); then
    LAST_PROGRESS=$CURRENT_PROGRESS
  else
    # If progress is stuck, capture diagnostic information
    echo "Progress appears stuck at $CURRENT_PROGRESS"
    python scripts/db/simple_inspect.py batch_jobs --limit 1
    break
  fi
done
```

**Verification Points**:

- Progress increases steadily over time
- Concurrency limits are respected (check processing patterns)
- System remains responsive during processing
- Final result reflects proper batch completion

### Step 3: Verify Database Load

```bash
# Count total domains processed for this batch
python scripts/db/simple_inspect.py domains
```

**SQL Verification Query**:

```sql
SELECT COUNT(*) FROM domains
WHERE batch_id = '$LARGE_BATCH_ID'::uuid;
```

**Verification Points**:

- Domain count matches CSV input
- Database performance remains acceptable under load
- No duplicate entries or data corruption

## Database Correlation Verification

After completing all tests, perform cross-table verifications:

### UUID Consistency Check

```bash
# Create verification script to check UUID consistency across tables
cat > uuid_verification.sql << 'EOF'
-- Check batch_jobs table
SELECT batch_id, COUNT(*)
FROM batch_jobs
WHERE batch_id IS NOT NULL
GROUP BY batch_id
HAVING COUNT(*) > 1;

-- Check domains table
SELECT batch_id, COUNT(*)
FROM domains
WHERE batch_id IS NOT NULL
GROUP BY batch_id;

-- Check jobs table
SELECT batch_id, COUNT(*)
FROM jobs
WHERE batch_id IS NOT NULL
GROUP BY batch_id;

-- Cross-reference batch_ids between tables
SELECT 'Orphaned domains' AS issue, COUNT(*)
FROM domains d
LEFT JOIN batch_jobs b ON d.batch_id = b.batch_id
WHERE b.batch_id IS NULL AND d.batch_id IS NOT NULL;

SELECT 'Orphaned jobs' AS issue, COUNT(*)
FROM jobs j
LEFT JOIN batch_jobs b ON j.batch_id = b.batch_id
WHERE b.batch_id IS NULL AND j.batch_id IS NOT NULL;

-- Check domain counts match expected totals
SELECT b.batch_id, b.total_domains, COUNT(d.id) AS actual_domains,
       CASE WHEN b.total_domains = COUNT(d.id) THEN 'OK' ELSE 'MISMATCH' END AS status
FROM batch_jobs b
LEFT JOIN domains d ON b.batch_id = d.batch_id
GROUP BY b.batch_id, b.total_domains;
EOF

# Execute verification script
psql -h $DB_HOST -U $DB_USER -d $DB_NAME -f uuid_verification.sql > uuid_verification_results.txt
```

**Verification Points**:

- No duplicate UUIDs in batch_jobs
- No orphaned domains or jobs without a parent batch
- Domain counts match expected totals in batch_jobs

### Comprehensive UUID Verification Script

For more detailed verification, we've created a Python-based verification tool that provides deeper insights and better error reporting:

```bash
# Run the comprehensive UUID verification script
python scripts/tests/verify_batch_uuids.py
```

This script (`verify_batch_uuids.py`) performs the following checks:

1. **Type Verification**: Confirms that all `batch_id` columns are actually UUID type in PostgreSQL
2. **Object Type Verification**: Verifies that UUID values are properly represented as Python UUID objects
3. **Relationship Integrity**: Identifies orphaned records across all related tables
4. **Count Validation**: Ensures domain counts match the expected totals
5. **Detailed Logging**: Provides comprehensive logging with specific error messages

**Advantages over SQL-only verification**:

- Automated checks for UUID object types (not just string format)
- Better error reporting with detailed logs
- Consolidated verification in a single run
- Built-in session management using the application's actual connection pool
- Reusable for regression testing

**Sample output**:

```
2025-04-05 10:23:45,123 - __main__ - INFO - Database connection established
2025-04-05 10:23:45,234 - __main__ - INFO - Checking batch_jobs table for UUID consistency...
2025-04-05 10:23:45,345 - __main__ - INFO - ✓ batch_jobs.batch_id is correctly of type UUID
2025-04-05 10:23:45,456 - __main__ - INFO - ✓ No duplicate batch_ids in batch_jobs
2025-04-05 10:23:45,567 - __main__ - INFO - Found 42 unique batch_ids in batch_jobs table
2025-04-05 10:23:45,678 - __main__ - INFO - Checking domains table for UUID consistency...
2025-04-05 10:23:45,789 - __main__ - INFO - ✓ domains.batch_id is correctly of type UUID
2025-04-05 10:23:45,890 - __main__ - INFO - Found 42 unique batch_ids in domains table
2025-04-05 10:23:45,901 - __main__ - INFO - ✓ No orphaned batch_ids in domains
2025-04-05 10:23:46,012 - __main__ - INFO - Checking jobs table for UUID consistency...
2025-04-05 10:23:46,123 - __main__ - INFO - ✓ jobs.batch_id is correctly of type UUID
2025-04-05 10:23:46,234 - __main__ - INFO - Found 42 unique batch_ids in jobs table
2025-04-05 10:23:46,345 - __main__ - INFO - ✓ No orphaned batch_ids in jobs
2025-04-05 10:23:46,456 - __main__ - INFO - Verifying domain counts against expected totals...
2025-04-05 10:23:46,567 - __main__ - INFO - ✓ All domain counts match expected totals
2025-04-05 10:23:46,678 - __main__ - INFO - ✅ VERIFICATION PASSED: All UUID and relationship checks passed
2025-04-05 10:23:46,789 - __main__ - INFO - Database connection closed
2025-04-05 10:23:46,890 - __main__ - INFO - UUID verification completed successfully
```

The script source code is located at `scripts/tests/verify_batch_uuids.py` and can be modified to add additional verification checks as needed.

## Performance and Tracing Analysis

Review the SQL logs to analyze query patterns:

```bash
# Extract SQL queries from log file
grep -i "sqlalchemy.engine.Engine" application.log > sql_queries.log

# Count queries by type
grep -i "SELECT" sql_queries.log | wc -l
grep -i "INSERT" sql_queries.log | wc -l
grep -i "UPDATE" sql_queries.log | wc -l
```

Analyze for:

- Unnecessary repeated queries
- Missing indexes
- Transaction boundaries
- Query performance

## Final Verification

Create a test report summarizing all verification points:

```bash
cat > batch_processor_test_report.md << EOF
# Batch Processor End-to-End Test Results

Test Date: $(date)

## Test Cases Summary

1. Valid Batch Test: $(cat final_status.json | jq -r .status)
   - Total Domains: $(cat final_status.json | jq -r .total_domains)
   - Completed: $(cat final_status.json | jq -r .completed_domains)
   - Failed: $(cat final_status.json | jq -r .failed_domains)
   - Processing Time: $(cat final_status.json | jq -r .processing_time) seconds

2. Invalid Input Test: $(cat invalid_status.json | jq -r .status)
   - Total Domains: $(cat invalid_status.json | jq -r .total_domains)
   - Completed: $(cat invalid_status.json | jq -r .completed_domains)
   - Failed: $(cat invalid_status.json | jq -r .failed_domains)

3. Large Batch Test: $(cat large_current_status.json | jq -r .status)
   - Total Domains: $(cat large_current_status.json | jq -r .total_domains)
   - Processed: $(cat large_current_status.json | jq -r .completed_domains)
   - Processing Time: $(cat large_current_status.json | jq -r .processing_time) seconds

## Database Verification

- UUID Consistency: [PASS/FAIL]
- Data Integrity: [PASS/FAIL]
- Error Handling: [PASS/FAIL]

## Performance Metrics

- Average processing time per domain: [CALCULATED VALUE]
- Database query count: [CALCULATED VALUE]
- Peak memory usage: [OBSERVED VALUE]

## Issues Identified

- [List any issues found]

## Conclusion

- [PASS/FAIL]
EOF
```

## Regression Test Automation

To ensure these tests can be repeated for future changes, create an automation script:

```bash
cat > batch_processor_regression_test.sh << 'EOF'
#!/bin/bash
# Automated regression test for batch processor

# Setup
echo "Starting batch processor regression testing..."
DATE=$(date +%Y%m%d_%H%M%S)
mkdir -p test_results/$DATE
cd $(git rev-parse --show-toplevel) # Change to project root directory

# Enable SQL logging for the test
cp src/session/async_session.py src/session/async_session.py.bak
echo '
# Temporary SQL logging for tests
import logging
logging.basicConfig()
logging.getLogger("sqlalchemy.engine").setLevel(logging.INFO)
' >> src/session/async_session.py

# Prepare test CSV files
echo "Preparing test files..."
mkdir -p tests/data/
cat > tests/data/valid_domains.csv << 'CSV'
domain
example.com
test-domain.org
valid-site.net
samplecontent.io
developer.mozilla.org
CSV

cat > tests/data/invalid_domains.csv << 'CSV'
domain
example..com
not@valid
test-domain.org
invalid domain with spaces
http://missing-tld
valid-site.net
CSV

# Run tests in sequence
echo "Test 1: Valid Batch Submission"
curl -X POST http://localhost:8001/api/v3/batch_page_scraper/upload \
  -F "file=@tests/data/valid_domains.csv" \
  -H "Content-Type: multipart/form-data" \
  -v > test_results/$DATE/submission_response.json

BATCH_ID=$(cat test_results/$DATE/submission_response.json | jq -r .batch_id)
echo "Testing with batch_id: $BATCH_ID"

python scripts/db/simple_inspect.py batch_jobs --limit 1 > test_results/$DATE/batch_jobs_initial.txt

# Poll status until complete
TIMEOUT=120
ELAPSED=0
STATUS="pending"

while [[ "$STATUS" == "pending" || "$STATUS" == "running" ]] && [[ $ELAPSED -lt $TIMEOUT ]]; do
  sleep 5
  ELAPSED=$((ELAPSED+5))

  curl -s -X GET "http://localhost:8001/api/v3/batch_page_scraper/batch/$BATCH_ID/status" \
    -H "Content-Type: application/json" > test_results/$DATE/current_status.json

  STATUS=$(cat test_results/$DATE/current_status.json | jq -r .status)
  echo "Current status: $STATUS ($ELAPSED seconds elapsed)"
done

cat test_results/$DATE/current_status.json | jq > test_results/$DATE/final_status.json

echo "Test 2: Invalid Input Handling"
curl -X POST http://localhost:8001/api/v3/batch_page_scraper/upload \
  -F "file=@tests/data/invalid_domains.csv" \
  -H "Content-Type: multipart/form-data" \
  -v > test_results/$DATE/invalid_submission_response.json

INVALID_BATCH_ID=$(cat test_results/$DATE/invalid_submission_response.json | jq -r .batch_id)
echo "Testing with invalid batch_id: $INVALID_BATCH_ID"

# Wait for processing to complete
sleep 30
curl -X GET "http://localhost:8001/api/v3/batch_page_scraper/batch/$INVALID_BATCH_ID/status" \
  -H "Content-Type: application/json" \
  -v > test_results/$DATE/invalid_status.json

echo "Running comprehensive UUID verification..."
# Run the Python verification script and capture its output
python scripts/tests/verify_batch_uuids.py > test_results/$DATE/uuid_verification.log 2>&1
UUID_VERIFY_STATUS=$?
if [ $UUID_VERIFY_STATUS -eq 0 ]; then
  echo "UUID verification PASSED ✅"
else
  echo "UUID verification FAILED ❌"
fi

echo "Generating test report..."
cat > test_results/$DATE/test_report.md << REPORT
# Batch Processor End-to-End Test Results

Test Date: $(date)

## Test Cases Summary

1. Valid Batch Test: $(cat test_results/$DATE/final_status.json | jq -r .status)
   - Total Domains: $(cat test_results/$DATE/final_status.json | jq -r .total_domains)
   - Completed: $(cat test_results/$DATE/final_status.json | jq -r .completed_domains)
   - Failed: $(cat test_results/$DATE/final_status.json | jq -r .failed_domains)
   - Processing Time: $(cat test_results/$DATE/final_status.json | jq -r .processing_time) seconds

2. Invalid Input Test: $(cat test_results/$DATE/invalid_status.json | jq -r .status)
   - Total Domains: $(cat test_results/$DATE/invalid_status.json | jq -r .total_domains)
   - Completed: $(cat test_results/$DATE/invalid_status.json | jq -r .completed_domains)
   - Failed: $(cat test_results/$DATE/invalid_status.json | jq -r .failed_domains)

## Database Verification

- UUID Verification: $([ $UUID_VERIFY_STATUS -eq 0 ] && echo "PASS" || echo "FAIL")
- Full verification log: [uuid_verification.log](./uuid_verification.log)

## Conclusion

$([ $UUID_VERIFY_STATUS -eq 0 ] && echo "✅ ALL TESTS PASSED" || echo "❌ TESTS FAILED")
REPORT

# Restore original session file
mv src/session/async_session.py.bak src/session/async_session.py

echo "Tests completed. Results in test_results/$DATE/"
EOF

chmod +x batch_processor_regression_test.sh
```

This automation script:

1. Creates test data files automatically
2. Runs both the valid and invalid batch tests
3. Executes the comprehensive UUID verification script
4. Generates a detailed test report with results
5. Preserves all output in a timestamped directory

To run the regression tests:

```bash
./batch_processor_regression_test.sh
```

## Conclusion

This comprehensive testing protocol ensures that the batch processor service correctly handles the CSV-to-database workflow with proper UUID standardization. Only after successfully passing all verification steps should the system be considered validated for production use.

The tests verify:

1. Data flow integrity from CSV input to database storage
2. Proper UUID handling throughout all layers
3. Accurate tracking of processing status
4. Robust error handling for invalid inputs
5. Performance under various load conditions

## Appendix: SQL Query Tracing Reference

Common query patterns to look for in the SQL trace logs:

1. Batch creation:

```sql
INSERT INTO batch_jobs (batch_id, tenant_id, ...) VALUES (...)
```

2. Domain insertion:

```sql
INSERT INTO domains (domain, batch_id, ...) VALUES (...)
```

3. Status updates:

```sql
UPDATE batch_jobs SET status = ..., progress = ..., completed_domains = ... WHERE batch_id = ...
```

4. Job creation:

```sql
INSERT INTO jobs (job_id, batch_id, domain, ...) VALUES (...)
```

These query patterns should demonstrate proper UUID type handling throughout the system.

---

End of Document
