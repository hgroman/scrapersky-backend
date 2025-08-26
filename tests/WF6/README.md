# WF6 (The Recorder) - Comprehensive Testing Documentation

## Overview

This directory contains the complete testing framework for WF6 (The Recorder), designed as a foundational testing approach for ALL ScraperSky workflows. The testing framework emphasizes Docker-first, environment-safe testing with zero production risk, following the ScraperSky Layer Architecture (L1-L8) and Guardian Persona system.

## Quick Start

```bash
# 1. Navigate to test directory
cd tests/WF6

# 2. Validate environment
./scripts/validate_environment.sh

# 3. Run complete test suite
./scripts/run_all_tests.sh

# 4. View results
cat results/wf6_test_results.json
```

## Architecture

### WF6 Workflow Components
- **Input**: `sitemap_files` table with status tracking
- **Processing**: Background service with HTTP fetching and XML parsing
- **Output**: `pages` table with extracted URLs
- **Status Flow**: Queued → Processing → Complete/Error

### Dependencies
- **Upstream**: WF5 (The Flight Planner) - Currently broken, requires simulation
- **Downstream**: WF7 (The Extractor) - Status unknown

## Test Framework Structure

### Core Files
- `wf6_test_tracking.yaml` - Master test configuration and tracking
- `README.md` - This documentation
- `active/` - Current work orders and layer review tracking
- `scripts/` - Executable test scripts
- `data/` - Test data and fixtures
- `results/` - Test execution results

### Related Documentation
- `/Docs/Docs_38_Testing_Strategy/` - Comprehensive testing framework documentation
- `/Docs/Docs_38_Testing_Strategy/completed_work_orders/` - Historical work order records

### Test Phases
1. **Environment Setup** - Docker validation and health checks
2. **Component Testing** - Individual component validation
3. **Integration Testing** - Cross-component integration
4. **Error Handling** - Error scenarios and edge cases
5. **End-to-End** - Complete workflow pipeline
6. **Performance Validation** - Resource usage and performance

## Component-by-Component Testing (ScraperSky Layer Architecture)

### Layer 1 (L1): Data Sentinel - Models and Data Layer
**Guardian Persona**: Layer 1 Data Sentinel
- **SitemapFile Model** (`src/models/sitemap.py`)
  - Field validation and constraints
  - Status enum validation
  - Foreign key relationships
- **Page Model** (`src/models/page.py`)
  - Relationship to sitemap_files
  - URL field validation
  - Status defaults

### Layer 4 (L4): Service Arbiter - Business Logic and Services
**Guardian Persona**: Layer 4 Service Arbiter
- **SitemapImportService** (`src/services/sitemap_import_service.py`)
  - HTTP request handling
  - XML parsing accuracy
  - Page record creation
  - Transaction integrity
  - Error handling and rollback
- **SitemapImportScheduler** (`src/services/sitemap_import_scheduler.py`)
  - Background job execution
  - Batch processing
  - Error isolation

### Layer 3 (L3): Router Guardian - API Endpoints and Request Handling
**Guardian Persona**: Layer 3 Router Guardian
- **SitemapFiles Router** (`src/routers/sitemap_files.py`)
  - CRUD operations
  - Authentication enforcement
  - Input validation
  - Batch status updates
- **DevTools Router** (`src/routers/dev_tools.py`)
  - Manual trigger endpoint
  - Parameter validation
  - Error handling

## Test Scenarios

### Happy Path
- Successful sitemap processing
- Status transitions
- Page record creation
- Foreign key integrity

### Error Scenarios
- Invalid sitemap URLs
- Malformed XML content
- Network timeouts
- Transaction rollbacks

### Performance Scenarios
- Large sitemap processing
- Memory usage monitoring
- Resource leak detection

## API Endpoints

### Consumer Endpoints
- `POST /api/v3/sitemap-files/` - Create sitemap file
- `GET /api/v3/sitemap-files/` - List with pagination
- `PUT /api/v3/sitemap-files/{id}` - Update sitemap file
- `PUT /api/v3/sitemap-files/sitemap_import_curation/status` - Batch status update

### Dev Tools Endpoints
- `POST /api/v3/dev-tools/trigger-sitemap-import/{id}` - Manual trigger

### Health Endpoints
- `GET /health` - Application health
- `GET /health/database` - Database health

## Database Schema

### Primary Tables
```sql
-- Input table
sitemap_files (
  id UUID PRIMARY KEY,
  domain_id UUID REFERENCES domains(id),
  url TEXT NOT NULL,
  sitemap_import_status sitemap_import_process_status_enum,
  sitemap_import_error TEXT
);

-- Output table
pages (
  id UUID PRIMARY KEY,
  domain_id UUID REFERENCES domains(id),
  sitemap_file_id UUID REFERENCES sitemap_files(id),
  url TEXT NOT NULL,
  page_curation_status page_curation_status
);
```

### Status Enums
- `SitemapImportProcessStatusEnum`: Queued, Processing, Complete, Error
- `PageCurationStatus`: New, Selected, Rejected

## Environment Requirements

### Docker Setup
```yaml
# Required services
services:
  - app (FastAPI application)
  - postgres (Database)
  - redis (Optional for caching)
```

### Environment Variables
```bash
ENVIRONMENT=development
POSTGRES_HOST=localhost
POSTGRES_DB=scrapersky_test
POSTGRES_USER=test_user
POSTGRES_PASSWORD=test_pass
JWT_SECRET_KEY=test_secret
```

### Health Check Requirements
- Application must respond to `/health`
- Database must respond to `/health/database`
- All services must be "Up" before testing

## Authentication

### JWT Token Setup
```bash
# Generate test token
export JWT_TOKEN=$(curl -X POST "http://localhost:8000/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"username":"test_user","password":"test_pass"}' | \
  jq -r '.access_token')
```

### Required Headers
```bash
Authorization: Bearer $JWT_TOKEN
Content-Type: application/json
```

## Test Data Management

### Test Domain Creation
```sql
INSERT INTO domains (id, domain, status, tenant_id) 
VALUES ('test-domain-uuid', 'test-example.com', 'active', 'test-tenant-uuid');
```

### Test Sitemap URLs
- `https://test-example.com/sitemap.xml` (Valid)
- `https://invalid-domain.com/sitemap.xml` (Error testing)
- `https://slow-response.com/sitemap.xml` (Timeout testing)

### Cleanup Procedures
```sql
-- Clean test data
DELETE FROM pages WHERE sitemap_file_id IN 
  (SELECT id FROM sitemap_files WHERE discovery_method = 'test');
DELETE FROM sitemap_files WHERE discovery_method = 'test';
DELETE FROM domains WHERE domain LIKE 'test-%';
```

## Validation Queries

### Status Verification
```sql
-- Check sitemap status
SELECT id, sitemap_import_status, sitemap_import_error 
FROM sitemap_files WHERE id = ?;

-- Check pages created
SELECT COUNT(*), sitemap_file_id 
FROM pages WHERE sitemap_file_id = ? 
GROUP BY sitemap_file_id;

-- Check foreign key integrity
SELECT p.id, p.sitemap_file_id, sf.id 
FROM pages p 
LEFT JOIN sitemap_files sf ON p.sitemap_file_id = sf.id 
WHERE p.sitemap_file_id = ?;
```

## Success Criteria

### Functional Requirements
✅ All status transitions work correctly  
✅ Page records created with proper relationships  
✅ Error scenarios handled gracefully  
✅ API endpoints respond correctly  
✅ Authentication enforced properly  

### Performance Requirements
✅ HTTP requests complete within 60s timeout  
✅ Database transactions commit/rollback properly  
✅ Memory usage remains stable  
✅ No resource leaks detected  

### Security Requirements
✅ JWT authentication required  
✅ Tenant isolation maintained  
✅ SQL injection prevention verified  
✅ Input validation enforced  

## Reporting

### Test Results
- `results/wf6_test_results.json` - Detailed test results
- `results/wf6_coverage_report.html` - Code coverage
- `results/wf6_performance.json` - Performance metrics
- `results/wf6_test_errors.log` - Error logs

### Result Format
```json
{
  "test_run_id": "uuid",
  "timestamp": "2025-08-18T09:57:05-04:00",
  "environment": "docker",
  "total_tests": 45,
  "passed": 42,
  "failed": 3,
  "skipped": 0,
  "components": {
    "models": {"passed": 8, "failed": 0},
    "services": {"passed": 15, "failed": 2},
    "routers": {"passed": 12, "failed": 1},
    "integration": {"passed": 7, "failed": 0}
  }
}
```

## Extension Framework

This testing framework serves as the foundation for ALL ScraperSky workflow testing. Key extension points:

### Workflow Template
```yaml
metadata:
  workflow_id: "WF{N}"
  workflow_name: "The {Name}"
  dependencies:
    upstream: []
    downstream: []

test_components:
  models: {}
  services: {}
  routers: {}
  schedulers: {}
```

### Required Test Categories
- Environment setup and validation
- Component-by-component testing
- Integration testing
- Error handling and edge cases
- End-to-end pipeline validation
- Performance and resource validation

### Standard Validations
- Database integrity
- API functionality
- Error handling
- Authentication
- Performance metrics

## Troubleshooting

### Common Issues
1. **Docker not running**: Ensure Docker Desktop is running
2. **Database connection failed**: Check postgres service status
3. **Authentication failed**: Verify JWT token generation
4. **Tests hanging**: Check for network connectivity issues

### Debug Commands
```bash
# Check Docker status
docker-compose ps

# View application logs
docker-compose logs app

# Check database connectivity
docker-compose exec postgres psql -U test_user -d scrapersky_test -c "SELECT 1;"

# Validate API health
curl http://localhost:8000/health
```

## Support

For questions or issues with the testing framework:
1. Check the test tracking YAML for component status
2. Review error logs in `results/wf6_test_errors.log`
3. Consult the Layer 7 Test Sentinel documentation
4. Contact The Architect for framework extensions

---

**Layer 7 (L7) Test Sentinel Ownership**: This testing framework is owned and maintained by the Layer 7 Test Sentinel persona, ensuring comprehensive, Docker-first, environment-safe testing for all ScraperSky workflows. The L7 Test Sentinel coordinates testing across all layers (L1-L8) and workflows (WF1-WF7+) in the ScraperSky ecosystem.
