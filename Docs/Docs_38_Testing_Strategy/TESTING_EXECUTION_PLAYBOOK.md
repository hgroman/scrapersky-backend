# ScraperSky Testing Execution Playbook

**Based On:** WF6 Production-Ready Framework  
**Created By:** Layer 7 Test Sentinel v1.6 - Anti-Stub Guardian  
**Status:** Operational Guide for Immediate Use  
**Scope:** All ScraperSky Workflows (WF1-WF7+)  

---

## Overview

This playbook provides step-by-step instructions for executing the ScraperSky Testing Framework. All procedures are based on the working implementation created during the WF6 AI pairing session and are immediately usable for comprehensive workflow testing.

## Prerequisites

### **System Requirements**
- Docker Desktop running
- docker-compose available
- curl (HTTP testing)
- jq (JSON processing)  
- Python 3.8+ (component testing)
- PostgreSQL client (database validation)

### **Environment Setup**
```bash
# Verify Docker is running
docker --version
docker-compose --version

# Verify ScraperSky services
cd /path/to/scraper-sky-backend
docker-compose ps
```

---

## Quick Start Guide

### **1. Navigate to Test Directory**
```bash
cd tests/WF6  # Replace WF6 with target workflow
```

### **2. Validate Environment**
```bash
./scripts/validate_environment.sh
```
**Expected Output:**
```
✅ Docker services running
✅ Application health check passed
✅ Database connectivity verified
✅ Required tables exist
✅ Environment ready for testing
```

### **3. Execute Complete Test Suite**
```bash
./scripts/run_all_tests.sh
```

### **4. Review Results**
```bash
cat results/wf6_test_results.json  # Replace wf6 with workflow
```

---

## Detailed Execution Procedures

### **Phase 1: Environment Setup & Health Validation**

#### **Step 1.1: Docker Service Verification**
```bash
# Check Docker services status
docker-compose ps

# Expected output shows all services running:
# NAME               COMMAND             SERVICE   STATUS    PORTS
# app                "python run_ser..."  app      running   0.0.0.0:8000->8000/tcp
# postgres           "docker-entryp..."   db       running   0.0.0.0:5432->5432/tcp
```

#### **Step 1.2: Application Health Check**
```bash
# Verify application is responding
curl -f http://localhost:8000/health

# Expected response:
# {"status": "healthy", "timestamp": "2025-08-21T..."}
```

#### **Step 1.3: Database Health Validation**
```bash
# Verify database connectivity
curl -f http://localhost:8000/health/db

# Expected response:
# {"status": "healthy", "database": "connected", "timestamp": "2025-08-21T..."}
```

#### **Step 1.4: Table Existence Verification**
```bash
# Using validate_environment.sh script
./scripts/validate_environment.sh

# Manual verification (alternative):
docker-compose exec postgres psql -U scrapersky_user -d scrapersky_db -c "\dt"
```

### **Phase 2: Authentication Setup**

#### **Step 2.1: Generate JWT Token**
```bash
# Automated token generation (recommended)
export JWT_TOKEN=$(curl -s -X POST "http://localhost:8000/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"username":"test_user","password":"test_pass"}' | \
  jq -r '.access_token')

# Verify token was generated
echo $JWT_TOKEN | wc -c  # Should show token length > 100
```

#### **Step 2.2: Test Authentication**
```bash
# Test authenticated endpoint
curl -H "Authorization: Bearer $JWT_TOKEN" \
     -H "Content-Type: application/json" \
     http://localhost:8000/api/v3/sitemap-files/

# Expected: 200 status with JSON response (not 401 unauthorized)
```

### **Phase 3: Component Testing (Layer-by-Layer)**

#### **Layer 1 (L1) - Data Sentinel Testing**

**Step 3.1: Model Validation Testing**
```bash
# Execute Python component tests
python3 scripts/test_component.py --layer=L1 --component=models

# Manual testing approach:
docker-compose exec app python -c "
from src.models.sitemap import SitemapFile
from src.models.page import Page
print('✅ Models import successfully')
"
```

**Step 3.2: Database Schema Validation**
```sql
-- Using database specifications from docs/DATABASE_TABLE_SPECIFICATIONS.md
-- Verify sitemap_files table structure
\d+ sitemap_files;

-- Expected columns:
-- id | uuid | primary key
-- domain_id | uuid | foreign key
-- url | text | not null
-- sitemap_import_status | enum | default 'Queued'
-- sitemap_import_error | text | nullable
-- created_at | timestamp | default now()
-- updated_at | timestamp | default now()
```

**Step 3.3: Constraint and Relationship Testing**
```sql
-- Test foreign key constraints
INSERT INTO sitemap_files (domain_id, url) VALUES ('invalid-uuid', 'test-url');
-- Expected: Foreign key constraint violation error

-- Test enum validation  
INSERT INTO sitemap_files (domain_id, url, sitemap_import_status) 
VALUES ('550e8400-e29b-41d4-a716-446655440000', 'test-url', 'InvalidStatus');
-- Expected: Enum constraint violation error
```

#### **Layer 3 (L3) - Router Guardian Testing**

**Step 3.4: API Endpoint Testing**

**Create Sitemap File:**
```bash
curl -X POST "http://localhost:8000/api/v3/sitemap-files/" \
  -H "Authorization: Bearer $JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "domain_id": "550e8400-e29b-41d4-a716-446655440000",
    "url": "https://test-example.com/sitemap.xml",
    "sitemap_type": "Standard",
    "discovery_method": "manual_test"
  }'

# Expected response (201 Created):
# {"id": "new-uuid", "url": "https://test-example.com/sitemap.xml", ...}
```

**List Sitemap Files:**
```bash
curl -H "Authorization: Bearer $JWT_TOKEN" \
     "http://localhost:8000/api/v3/sitemap-files/"

# Expected response (200 OK):
# {"count": N, "results": [{"id": "...", "url": "...", ...}]}
```

**Update Batch Status:**
```bash
curl -X PUT "http://localhost:8000/api/v3/sitemap-files/sitemap_import_curation/status" \
  -H "Authorization: Bearer $JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "sitemap_file_ids": ["sitemap-file-uuid"],
    "status": "Queued",
    "user": "test_user"
  }'

# Expected response (200 OK):
# {"updated_count": 1, "status": "success"}
```

#### **Layer 4 (L4) - Service Arbiter Testing**

**Step 3.5: Manual Trigger Testing**
```bash
# Trigger sitemap import processing
curl -X POST "http://localhost:8000/api/v3/dev-tools/trigger-sitemap-import/{sitemap_file_id}" \
  -H "Authorization: Bearer $JWT_TOKEN"

# Expected response (200 OK):
# {"status": "triggered", "sitemap_file_id": "...", "message": "Processing initiated"}
```

**Step 3.6: Status Transition Verification**
```bash
# Monitor status changes
watch -n 2 "curl -s -H 'Authorization: Bearer $JWT_TOKEN' \
  'http://localhost:8000/api/v3/sitemap-files/{sitemap_file_id}' | \
  jq '.sitemap_import_status'"

# Expected progression:
# "Queued" → "Processing" → "Complete" (or "Error")
```

**Step 3.7: Service Logic Validation**
```bash
# Execute service component tests
python3 scripts/test_component.py --layer=L4 --component=services

# Manual service testing:
docker-compose exec app python -c "
from src.services.sitemap_import_service import SitemapImportService
print('✅ Service imports successfully')
"
```

### **Phase 4: Integration Testing**

#### **Step 4.1: End-to-End Workflow Testing**

**Complete Workflow Execution:**
```bash
# 1. Create test domain (if not exists)
DOMAIN_ID=$(curl -s -X POST "http://localhost:8000/api/v3/domains/" \
  -H "Authorization: Bearer $JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"domain": "test-integration.com", "status": "active"}' | \
  jq -r '.id')

# 2. Create sitemap file
SITEMAP_ID=$(curl -s -X POST "http://localhost:8000/api/v3/sitemap-files/" \
  -H "Authorization: Bearer $JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d "{\"domain_id\": \"$DOMAIN_ID\", \"url\": \"https://test-integration.com/sitemap.xml\"}" | \
  jq -r '.id')

# 3. Trigger processing
curl -X POST "http://localhost:8000/api/v3/dev-tools/trigger-sitemap-import/$SITEMAP_ID" \
  -H "Authorization: Bearer $JWT_TOKEN"

# 4. Wait for completion (or monitor)
sleep 30

# 5. Verify page records created
curl -H "Authorization: Bearer $JWT_TOKEN" \
  "http://localhost:8000/api/v3/pages/?sitemap_file_id=$SITEMAP_ID"
```

#### **Step 4.2: Database Integrity Validation**
```sql
-- Verify foreign key relationships
SELECT p.id, p.sitemap_file_id, sf.id as sitemap_id
FROM pages p 
LEFT JOIN sitemap_files sf ON p.sitemap_file_id = sf.id 
WHERE p.sitemap_file_id = '{sitemap_file_id}';

-- Expected: All pages have matching sitemap_file records

-- Verify page count accuracy
SELECT 
    sf.id,
    sf.url,
    COUNT(p.id) as actual_pages,
    sf.url_count as reported_pages
FROM sitemap_files sf
LEFT JOIN pages p ON sf.id = p.sitemap_file_id
WHERE sf.id = '{sitemap_file_id}'
GROUP BY sf.id, sf.url, sf.url_count;

-- Expected: actual_pages should match reported_pages
```

### **Phase 5: Error Handling & Edge Cases**

#### **Step 5.1: Invalid URL Testing**
```bash
# Test with non-existent URL
INVALID_SITEMAP_ID=$(curl -s -X POST "http://localhost:8000/api/v3/sitemap-files/" \
  -H "Authorization: Bearer $JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "domain_id": "550e8400-e29b-41d4-a716-446655440000",
    "url": "https://nonexistent-domain-12345.com/sitemap.xml"
  }' | jq -r '.id')

# Trigger processing
curl -X POST "http://localhost:8000/api/v3/dev-tools/trigger-sitemap-import/$INVALID_SITEMAP_ID" \
  -H "Authorization: Bearer $JWT_TOKEN"

# Wait and verify error status
sleep 30
curl -H "Authorization: Bearer $JWT_TOKEN" \
  "http://localhost:8000/api/v3/sitemap-files/$INVALID_SITEMAP_ID" | \
  jq '.sitemap_import_status, .sitemap_import_error'

# Expected: "Error" status with descriptive error message
```

#### **Step 5.2: Malformed XML Testing**
```bash
# Use malformed sitemap data from tests/WF6/data/malformed_sitemap.xml
# Create sitemap pointing to malformed XML endpoint
# Verify graceful error handling without database corruption
```

#### **Step 5.3: Network Timeout Testing**
```bash
# Test with slow-responding URL (if available)
# Monitor timeout behavior (60s limit)
# Verify proper error status assignment
```

### **Phase 6: Performance & Resource Validation**

#### **Step 6.1: Memory Usage Monitoring**
```bash
# Monitor Docker container resources during testing
docker stats --no-stream

# Expected: Memory usage should remain stable, no continuous growth
```

#### **Step 6.2: Database Performance**
```sql
-- Monitor query performance
EXPLAIN ANALYZE SELECT * FROM pages WHERE sitemap_file_id = '{uuid}';

-- Verify index usage and query efficiency
-- Expected: Index scans, not sequential scans for large datasets
```

#### **Step 6.3: Batch Processing Validation**
```bash
# Create multiple sitemap files
for i in {1..5}; do
  curl -X POST "http://localhost:8000/api/v3/sitemap-files/" \
    -H "Authorization: Bearer $JWT_TOKEN" \
    -H "Content-Type: application/json" \
    -d "{\"domain_id\": \"550e8400-e29b-41d4-a716-446655440000\", \"url\": \"https://test-$i.com/sitemap.xml\"}"
done

# Trigger batch processing via scheduler
# Monitor batch size compliance and processing efficiency
```

---

## Automated Test Execution

### **Using run_all_tests.sh Script**

```bash
cd tests/WF6
./scripts/run_all_tests.sh

# Script performs all phases automatically:
# 1. Environment validation
# 2. Authentication setup  
# 3. Component testing
# 4. Integration testing
# 5. Error scenario testing
# 6. Performance validation
# 7. Cleanup and reporting
```

### **Script Configuration Options**

```bash
# Run specific test phases
./scripts/run_all_tests.sh --phase=integration

# Run with verbose output
./scripts/run_all_tests.sh --verbose

# Skip cleanup (for debugging)
./scripts/run_all_tests.sh --no-cleanup

# Generate performance report
./scripts/run_all_tests.sh --performance
```

### **Python Component Testing**

```bash
# Test specific components
python3 scripts/test_component.py --component=models
python3 scripts/test_component.py --component=services  
python3 scripts/test_component.py --component=routers

# Test specific layers
python3 scripts/test_component.py --layer=L1
python3 scripts/test_component.py --layer=L3
python3 scripts/test_component.py --layer=L4

# Run with database validation
python3 scripts/test_component.py --validate-db

# Generate coverage report
python3 scripts/test_component.py --coverage
```

---

## Result Analysis

### **Success Criteria Validation**

**Functional Requirements:**
```bash
# Verify all required functionality working
grep -E "(PASS|FAIL)" results/wf6_test_results.json

# Expected: All critical tests showing PASS status
```

**Performance Requirements:**
```json
// From results/wf6_performance.json
{
  "http_request_avg_time": "< 60s",
  "database_transaction_time": "< 5s", 
  "memory_usage_stable": true,
  "resource_leaks_detected": false
}
```

**Security Requirements:**
```bash
# Verify authentication enforcement
grep "authentication_required" results/wf6_test_results.json

# Expected: All API endpoints require valid JWT tokens
```

### **Error Analysis**

**Common Issues and Solutions:**

1. **Docker Service Not Running**
   ```bash
   # Solution: Start Docker services
   docker-compose up -d
   ```

2. **Database Connection Failed**
   ```bash
   # Solution: Verify database health
   curl http://localhost:8000/health/db
   docker-compose restart postgres
   ```

3. **Authentication Failed**
   ```bash
   # Solution: Regenerate JWT token
   unset JWT_TOKEN
   # Re-run authentication setup
   ```

4. **Test Data Cleanup Issues**
   ```bash
   # Solution: Manual cleanup
   docker-compose exec postgres psql -U scrapersky_user -d scrapersky_db -c "
   DELETE FROM pages WHERE sitemap_file_id IN 
     (SELECT id FROM sitemap_files WHERE discovery_method = 'test');
   DELETE FROM sitemap_files WHERE discovery_method = 'test';
   DELETE FROM domains WHERE domain LIKE 'test-%';
   "
   ```

### **Report Generation**

```bash
# Generate comprehensive test report
./scripts/run_all_tests.sh --report

# View detailed results
less results/wf6_test_results.json
open results/wf6_coverage_report.html
cat results/wf6_test_errors.log
```

---

## Cleanup Procedures

### **Automated Cleanup**
```bash
# Included in run_all_tests.sh by default
# Removes all test data following proper dependency order
```

### **Manual Cleanup**
```sql
-- Execute in proper order to avoid foreign key violations
DELETE FROM pages WHERE sitemap_file_id IN 
  (SELECT id FROM sitemap_files WHERE discovery_method = 'test');
DELETE FROM sitemap_files WHERE discovery_method = 'test';
DELETE FROM domains WHERE domain LIKE 'test-%';
```

### **Docker Cleanup**
```bash
# Reset Docker environment (if needed)
docker-compose down
docker-compose up -d

# Verify clean state
curl http://localhost:8000/health
```

---

## Troubleshooting Guide

### **Common Issues**

1. **Tests Hanging**
   - Check Docker service status
   - Verify network connectivity
   - Review application logs: `docker-compose logs app`

2. **Database Connection Errors**
   - Verify database service: `docker-compose ps postgres`
   - Check database health: `curl http://localhost:8000/health/db`
   - Review database logs: `docker-compose logs postgres`

3. **Authentication Failures**
   - Regenerate JWT token
   - Verify user credentials in test configuration
   - Check auth service logs

4. **API Endpoint Errors**
   - Verify application is running: `curl http://localhost:8000/health`
   - Check endpoint paths match API documentation
   - Review request format and headers

### **Debug Commands**

```bash
# Check Docker status
docker-compose ps

# View application logs
docker-compose logs app

# View database logs  
docker-compose logs postgres

# Test database connectivity
docker-compose exec postgres psql -U scrapersky_user -d scrapersky_db -c "SELECT 1;"

# Validate API health
curl -v http://localhost:8000/health

# Check environment variables
docker-compose exec app env | grep -E "(DATABASE|JWT|ENVIRONMENT)"
```

---

## Framework Extension

### **Adapting for New Workflows**

1. **Copy Structure:**
   ```bash
   cp -r tests/WF6 tests/WF{N}
   cd tests/WF{N}
   ```

2. **Update Configuration:**
   - Edit `wf{n}_test_tracking.yaml`
   - Update workflow metadata
   - Modify component specifications
   - Adapt test scenarios

3. **Customize Scripts:**
   - Update endpoint URLs in scripts
   - Modify database table references  
   - Adapt test data for workflow
   - Configure cleanup procedures

4. **Validate Adaptation:**
   ```bash
   ./scripts/validate_environment.sh
   ./scripts/run_all_tests.sh --dry-run
   ```

---

## Conclusion

This playbook provides comprehensive, step-by-step procedures for executing the ScraperSky Testing Framework. All instructions are based on the production-ready implementation created during the WF6 AI pairing session and can be immediately applied to test any ScraperSky workflow.

The framework ensures:
- ✅ Complete workflow validation
- ✅ Docker-first environment safety
- ✅ Layer architecture compliance  
- ✅ Production-grade quality assurance
- ✅ Comprehensive error handling
- ✅ Performance monitoring
- ✅ Security validation

Follow these procedures to maintain the highest quality standards across all ScraperSky workflow implementations.

---

**Playbook Status:** ✅ **PRODUCTION READY**  
**Framework Support:** ✅ **ALL WORKFLOWS (WF1-WF7+)**  
**Quality Assurance:** ✅ **LAYER 7 TEST SENTINEL APPROVED**