# 07-64-Single-Domain-Scanner-Standardization-Requirements

## Overview

This document outlines the standardization requirements for the Single Domain Scanner implementation to ensure consistency with the batch implementation patterns that were successfully established. These requirements should be applied after the core functionality of the Single Domain Scanner has been fixed and verified as described in document `07-63-Prompt for Completing Single Domain Scanner Implementation.md`.

## Reference Implementation

The batch implementation has been thoroughly verified and documented in the following verification results:

1. `batch_scraper_verification.md` - Initial verification findings
2. `implementation_summary.md` - Summary of changes implemented
3. `batch_verification_script.py` - Testing script for batch implementation
4. `PR_DESCRIPTION.md` - Description of changes made

These documents contain valuable insights into the patterns and approaches that should be replicated in the Single Domain Scanner implementation.

## Standardization Requirements

To ensure consistency with the batch implementation patterns established previously, apply the following standardization requirements:

1. **Function Signatures and Naming**:

   - The Single Domain Scanner functions should follow the same naming patterns as batch functions
   - Use `process_domain_with_own_session()` to mirror `process_batch_with_own_session()`
   - Ensure parameter naming is consistent across both implementations

2. **Status Management**:

   - Apply identical status transition patterns as implemented in batch processing
   - Use the same status values: "pending" → "processing" → "completed"/"error"
   - Ensure status updates use isolated sessions with proper error handling

3. **Metadata Handling**:

   - Store processing details in a consistent format matching the batch implementation
   - Track timing metrics (start time, end time, processing duration)
   - Record error details in the same format as batch processing

4. **Transaction Pattern**:

   - Implement the same transaction boundary patterns established in batch processing
   - Use identical session context management approach
   - Apply the same pattern for status updates after error conditions

5. **Error Recovery Pattern**:

   - Implement consistent error recovery approach across both implementations
   - Handle database errors, network failures, and validation errors uniformly
   - Use the same pattern for recording errors in job metadata

6. **Session Execution Options**:

   - Apply consistent execution options for SQL queries
   - Use `execution_options(prepared=False)` for all raw SQL operations
   - Maintain identical parameter binding approaches

7. **Response Format Standardization**:

   - Ensure status response format matches batch status responses
   - Include the same fields for consistency across APIs
   - Maintain consistent structure for domain processing details

8. **Code Structure**:

   - Maintain parallel code structure between batch and single domain implementations
   - Keep helper functions organized similarly
   - Follow consistent error handling patterns at each level

9. **Documentation**:
   - Document the Single Domain Scanner implementation using the same format as batch
   - Highlight where patterns are reused from batch implementation
   - Maintain consistent API documentation format

## Key Lessons from Batch Implementation

Based on the verification results from the batch implementation, pay special attention to:

1. **Status URL Consistency**:

   - Ensure status URLs follow a consistent format across all endpoints
   - Standardize on the format `/api/v3/modernized_page_scraper/status/{job_id}`

2. **Domain Processing Feedback**:

   - Implement comprehensive result tracking for domain processing
   - Store detailed error information when processing fails
   - Include processing metrics (time, resources used)

3. **Input Validation**:

   - Add explicit domain validation before processing
   - Handle invalid domains gracefully with appropriate error responses

4. **Transaction Boundaries**:
   - Keep transaction scope narrow and focused
   - Ensure timely commits/rollbacks to prevent connection pool issues
   - Avoid spanning transactions across multiple operations

## Implementation Approach

1. First verify that the core Single Domain Scanner functionality is working correctly
2. Review the batch implementation to understand the established patterns
3. Apply standardization requirements systematically
4. Verify consistency between batch and Single Domain implementations
5. Document any deviations from batch patterns with clear justification

## Expected Outcome

By following these standardization requirements, we will achieve:

1. Consistent developer experience across different parts of the codebase
2. Reusable patterns for future route implementations
3. Easier maintenance and troubleshooting
4. More reliable error recovery across all routes

## Verification Criteria

The standardization will be considered successful if:

1. The Single Domain Scanner follows the same patterns as the batch implementation
2. API responses match the established format
3. Transaction handling follows the established pattern
4. Error handling mirrors the batch implementation
5. Status transitions are consistent with batch processing
6. Code organization parallels the batch implementation

---

These standardization requirements build upon the core implementation specified in `07-63-Prompt for Completing Single Domain Scanner Implementation.md` and should be applied after the core functionality is verified as working correctly.
