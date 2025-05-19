# Batch Processor Test Plan

## Objective

This test plan outlines a comprehensive strategy for validating the batch processing system after significant architectural changes. The goal is to ensure the system properly:

1. Creates batch records
2. Processes domains in background tasks
3. Updates batch statuses correctly
4. Manages errors and edge cases
5. Complies with Supavisor connection requirements

## Test Components

### 1. Database Connection Testing

**Purpose**: Verify that connections to the Supabase database work correctly with Supavisor.

**Test Cases**:

- Establish a database connection using `get_session()`
- Execute a simple query using SQLAlchemy
- Verify session cleanup works properly

**Success Criteria**:

- Connection established without errors
- Query returns expected results
- No connection leaks

**Implementation**: `test_db_connection.py`

### 2. Batch Creation Testing

**Purpose**: Verify that batches can be created properly in the database.

**Test Cases**:

- Create a batch with a single domain
- Create a batch with multiple domains
- Create a batch with no domains
- Create a batch with invalid domains

**Success Criteria**:

- Batch record created in database
- Proper batch ID returned
- Status set to "pending"
- Domain count accurate

**Implementation**: `test_batch_create.py`

### 3. Batch Processing Testing

**Purpose**: Verify that the background task properly processes domain batches.

**Test Cases**:

- Process a batch with a single domain
- Process a batch with multiple domains
- Process a batch with invalid domains
- Process a batch with a mix of valid and invalid domains

**Success Criteria**:

- Background task executes without errors
- Batch status updated to "processing" then "completed"
- Domain statuses tracked correctly
- Error handling functions correctly

**Implementation**: `test_batch_process.py`

### 4. Status Monitoring Testing

**Purpose**: Verify that batch status can be reliably tracked.

**Test Cases**:

- Monitor a new batch
- Monitor an in-progress batch
- Monitor a completed batch
- Monitor a failed batch

**Success Criteria**:

- Status correctly reflects batch state
- Progress percentage calculations accurate
- Domain statuses properly aggregated
- Error conditions properly reported

**Implementation**: `monitor_test.py`

### 5. End-to-End Testing

**Purpose**: Verify the complete batch processing workflow.

**Test Cases**:

- Full workflow from creation to completion
- Error handling for invalid domains
- Timeouts and resource constraints

**Success Criteria**:

- Batch progresses through all expected states
- Final status accurately reflects processing results
- Domain-level results are accurate
- Error handling is appropriate

**Implementation**: `test_batch_e2e.py`

## Test Implementation Approach

### Step 1: Test Script Development

Create isolated test scripts for each component:

```
scripts/testing/
  ├── test_db_connection.py
  ├── test_batch_create.py
  ├── test_batch_process.py
  ├── monitor_test.py
  └── test_batch_e2e.py
```

Each script should:

- Be executable on its own
- Include comprehensive logging
- Have clear success/failure criteria
- Clean up after itself

### Step 2: Execution Order

Execute tests in order of dependency:

1. `test_db_connection.py`
2. `test_batch_create.py`
3. `test_batch_process.py`
4. `monitor_test.py`
5. `test_batch_e2e.py`

### Step 3: Result Analysis

For each test:

- Check exit codes (0 = success, non-zero = failure)
- Review logs for errors or warnings
- Verify success criteria are met
- Document any issues found

## Edge Cases and Special Scenarios

### Error Handling

- Test with intentionally invalid domains
- Test with network failures (if possible)
- Test with database errors
- Test with resource limitations

### Performance Considerations

- Test with large batches (10+ domains)
- Test with limited resources
- Monitor for memory leaks during extended operation

### Specific Architectural Concerns

- Verify proper Supavisor connection parameters
- Verify session lifecycle management
- Verify transaction boundaries
- Verify error recovery

## Test Results Documentation

Document test results including:

- Test environment details
- Test execution timestamps
- Success/failure status for each test
- Detailed logs for any failures
- Performance metrics
- Recommendations for further improvements

## Ongoing Testing Strategy

- Implement CI/CD integration of key tests
- Add regression testing to change workflow
- Schedule periodic validation of key functionality
- Update tests as system evolves

## Conclusion

This test plan provides a systematic approach to validating the batch processing system. By following the incremental testing methodology and executing the test scripts in order, we can verify that the system functions correctly after the significant architectural changes.
