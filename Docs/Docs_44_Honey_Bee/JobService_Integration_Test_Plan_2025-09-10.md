# JobService Integration Test Plan

**Date:** 2025-09-10  
**Feature:** Deep Scan Job Status Tracking  
**Implementation:** PlacesDeepService + JobService Integration  
**Status:** READY FOR TESTING  

---

## Test Overview

**Objective**: Verify JobService integration properly tracks deep scan operations with progress updates and status changes.

**Components**:
- `PlacesDeepService.process_single_deep_scan()` - Modified with job tracking
- `JobService` - Handles job creation, status updates, progress tracking
- `jobs` database table - Stores job records

---

## Testing Methods

### **Method 1: Database Query Testing (Recommended)**

**Test Flow**:
1. Trigger deep scan operations 
2. Query jobs table to verify job creation and status progression
3. Validate job metadata and error handling

**SQL Queries for Testing**:

```sql
-- 1. Check recent deep scan jobs created
SELECT 
    id,
    job_id,
    job_type,
    status,
    progress,
    created_at,
    updated_at,
    job_metadata,
    error
FROM jobs 
WHERE job_type = 'places_deep_scan'
ORDER BY created_at DESC 
LIMIT 10;

-- 2. Monitor job status progression for specific job
SELECT 
    job_id,
    status,
    progress,
    updated_at,
    error
FROM jobs 
WHERE job_id = 'your-job-uuid-here'
ORDER BY updated_at DESC;

-- 3. Check job success/failure rates
SELECT 
    status,
    COUNT(*) as count,
    AVG(progress) as avg_progress
FROM jobs 
WHERE job_type = 'places_deep_scan'
AND created_at > NOW() - INTERVAL '1 hour'
GROUP BY status;
```

### **Method 2: Log Analysis Testing**

**Log Patterns to Look For**:

**Successful Job Flow**:
```
INFO - JobService initialized successfully for deep scan status tracking
INFO - Created deep scan job {job_id} for place_id: {place_id}
INFO - Deep scan job {job_id} completed successfully
```

**Error Handling**:
```
WARNING - Failed to create job record: {error}. Continuing without job tracking
WARNING - Failed to update job progress: {error}
WARNING - Failed to update job failure status: {error}
```

### **Method 3: API Endpoint Testing** (if available)

Check if there are job status API endpoints:
```bash
# Check for job-related endpoints
curl -X GET "http://localhost:8000/api/v3/jobs" \
  -H "Authorization: Bearer your-jwt-token"

# Get specific job status
curl -X GET "http://localhost:8000/api/v3/jobs/{job_id}" \
  -H "Authorization: Bearer your-jwt-token"
```

---

## Test Scenarios

### **Scenario 1: Successful Deep Scan**

**Setup**: Trigger deep scan for valid place_id with working Google API key

**Expected Job Progression**:
1. **Job Creation**: `status="running"`, `progress=0.0`
2. **API Call Start**: `status="running"`, `progress=0.2`  
3. **DB Upsert Start**: `status="running"`, `progress=0.8`
4. **Completion**: `status="completed"`, `progress=1.0`, `error=null`

**Test Command**:
```sql
-- Run this after triggering a successful deep scan
SELECT job_id, status, progress, error, created_at, updated_at 
FROM jobs 
WHERE job_type = 'places_deep_scan' 
AND created_at > NOW() - INTERVAL '5 minutes'
ORDER BY created_at DESC LIMIT 5;
```

### **Scenario 2: Google API Failure**

**Setup**: Trigger deep scan with invalid place_id or expired API key

**Expected Job Progression**:
1. **Job Creation**: `status="running"`, `progress=0.0`
2. **API Call Start**: `status="running"`, `progress=0.2`  
3. **API Failure**: `status="failed"`, `progress=1.0`, `error="Google Maps API error..."`

**Test Command**:
```sql
-- Check for failed jobs with API errors
SELECT job_id, status, progress, error 
FROM jobs 
WHERE job_type = 'places_deep_scan' 
AND status = 'failed'
AND error LIKE '%Google Maps API error%'
ORDER BY created_at DESC LIMIT 3;
```

### **Scenario 3: Database Failure**

**Setup**: Trigger deep scan with database connectivity issues or constraint violations

**Expected Job Progression**:
1. **Job Creation**: `status="running"`, `progress=0.0`
2. **API Success**: `status="running"`, `progress=0.8`
3. **DB Failure**: `status="failed"`, `progress=1.0`, `error="Database error..."`

### **Scenario 4: JobService Unavailable**

**Setup**: Test with JobService initialization failure

**Expected Behavior**:
- Deep scan continues normally (non-blocking)
- No job records created
- Warning logs about JobService unavailability
- Service returns LocalBusiness object as before

---

## Test Data Setup

### **Trigger Deep Scans**

**Option A: Via WF1 Workflow** (Recommended)
```sql
-- Queue places for deep scan processing
UPDATE places 
SET deep_scan_status = 'queued'
WHERE place_id IN (
    'ChIJPT5ThDBI0IkRy8c3YwQxHy0',  -- Known working place_id
    'ChIJInvalidPlace12345',         -- Invalid place_id for error testing
    'ChIJyX1hDUpI0IkR_Prz-yEVG84'   -- Previously working place_id
);
```

**Option B: Direct Service Call** (if accessible)
- Call `PlacesDeepService.process_single_deep_scan()` directly with test place IDs

---

## Success Criteria

### **✅ JobService Integration Successful If**:

1. **Job Creation**: New jobs appear in jobs table with `job_type="places_deep_scan"`
2. **Progress Tracking**: Jobs show progression through 0.0 → 0.2 → 0.8 → 1.0
3. **Success Handling**: Successful scans result in `status="completed"`
4. **Error Handling**: Failed scans result in `status="failed"` with error messages
5. **Non-blocking**: Deep scan functionality works even if JobService fails
6. **Metadata Tracking**: Job metadata includes place_id and tenant_id

### **✅ Bonus Success Indicators**:

1. **Performance**: No significant slowdown in deep scan operations
2. **Reliability**: Job status accurately reflects actual operation results
3. **Debugging**: Error messages in job.error field match log entries
4. **Scalability**: Multiple concurrent deep scans create separate job records

---

## Quick Test Commands

### **1. Pre-Test Setup**
```sql
-- Check current job count baseline
SELECT COUNT(*) as current_job_count FROM jobs WHERE job_type = 'places_deep_scan';
```

### **2. Trigger Test**
```sql
-- Queue a few places for deep scan
UPDATE places 
SET deep_scan_status = 'queued'
WHERE place_id IN (
    'ChIJPT5ThDBI0IkRy8c3YwQxHy0',
    'ChIJyX1hDUpI0IkR_Prz-yEVG84'
)
LIMIT 2;
```

### **3. Monitor Results**
```sql
-- Watch job creation and progression (run every 30 seconds)
SELECT 
    job_id,
    status,
    progress,
    error,
    job_metadata->>'place_id' as place_id,
    created_at,
    updated_at
FROM jobs 
WHERE job_type = 'places_deep_scan'
AND created_at > NOW() - INTERVAL '10 minutes'
ORDER BY created_at DESC;
```

### **4. Validate Integration**
```sql
-- Final validation query
SELECT 
    status,
    COUNT(*) as count,
    AVG(progress) as avg_progress,
    COUNT(CASE WHEN error IS NOT NULL THEN 1 END) as error_count
FROM jobs 
WHERE job_type = 'places_deep_scan'
AND created_at > NOW() - INTERVAL '1 hour'
GROUP BY status;
```

---

## Expected Results

**After running the test**:
- ✅ 2+ new job records with `job_type="places_deep_scan"`
- ✅ Jobs progress from 0.0 to 1.0 
- ✅ At least 1 job reaches `status="completed"`
- ✅ Job metadata contains correct place_id values
- ✅ Deep scan operations complete successfully (check local_businesses table)

**If tests pass**: JobService integration is working correctly  
**If tests fail**: Check logs for JobService initialization or SQL errors

---

**Implementation Status**: DEPLOYED  
**Commit**: `a98c00c`  
**Ready for Production Testing**: YES