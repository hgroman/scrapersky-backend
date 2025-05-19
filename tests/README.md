# ScraperSky Batch Processor Testing

This directory contains test scripts for validating the batch processing system after architectural changes. These scripts implement the incremental testing methodology described in `methodologies/incremental_testing_methodology.md`.

## Test Scripts

### Database Connection Test

Tests basic database connectivity with Supabase Supavisor.

```bash
python test_db_connection.py
```

### Batch Creation Test

Tests the creation of batch records in the database.

```bash
python test_batch_create.py
```

### Batch Processing Test

Tests the background task processing functionality.

```bash
python test_batch_process.py
```

### Batch Status Monitoring

Tests batch status tracking and updates.

```bash
python monitor_test.py [batch_id]
```

### End-to-End Test

Tests the complete batch processing workflow from creation to completion.

```bash
python test_batch_e2e.py
```

### Original Comprehensive Test (may require fixes)

The original comprehensive test script.

```bash
python test_batch_processor.py [--verbose] [--user USER_ID]
```

## Methodologies & Documentation

Detailed documentation on the testing approach can be found in:

- `methodologies/incremental_testing_methodology.md` - The systematic approach to testing complex systems
- `methodologies/batch_processor_test_plan.md` - Comprehensive test plan for batch processing

## Using These Tests

1. **First-time Setup**:

   - Ensure the database is properly configured
   - Verify environment variables are set correctly
   - Make sure the server is running

2. **Run Tests in Order**:

   1. Database connection test
   2. Batch creation test
   3. Batch processing test
   4. End-to-end test

3. **Interpreting Results**:
   - Tests return 0 on success, non-zero on failure
   - Check logs for detailed information
   - Successful tests will display success messages

## Advanced Usage

### Monitoring Specific Batches

You can monitor the status of a specific batch:

```bash
python monitor_test.py YOUR_BATCH_ID --interval 2 --timeout 60
```

### Running the Original Comprehensive Test

The original test script (`test_batch_processor.py`) runs all test cases in sequence:

```bash
python test_batch_processor.py --verbose
```

### Debugging Issues

1. Check database connection parameters in `.env`
2. Verify server is running (`docker-compose ps`)
3. Check server logs (`docker-compose logs -f scrapersky`)
4. Run tests with verbose logging enabled

## Extending the Test Suite

When adding new tests:

1. Follow the incremental testing methodology
2. Create isolated test scripts for new components
3. Add comprehensive logging
4. Include clear success/failure criteria
5. Update this README

## Architectural Notes

These tests validate crucial aspects of the batch processor architecture:

- Proper Supavisor connection parameters
- Correct transaction boundaries
- Background task execution
- Status tracking and updates
- Error handling

For more details on the architectural changes, see the work orders in `project-docs/07-database-connection-audit/`.
