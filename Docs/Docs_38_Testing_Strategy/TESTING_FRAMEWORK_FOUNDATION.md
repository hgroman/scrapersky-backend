# ScraperSky Testing Framework Foundation

## Overview

This document establishes the foundational testing framework for ALL ScraperSky workflows, starting with WF6 (The Recorder) as the reference implementation. This framework ensures consistent, Docker-first, environment-safe testing across all workflow components.

## Framework Architecture

### Core Principles
1. **Docker-First**: All tests run in isolated Docker containers
2. **Environment-Safe**: Zero production risk with isolated test databases
3. **Layer-Driven**: Test each ScraperSky layer (L1-L8) independently and in integration
4. **Guardian-Aligned**: Testing follows Guardian Persona responsibilities
5. **YAML-Tracked**: Comprehensive test tracking via YAML configuration
6. **Executable**: Fully automated test execution with detailed reporting

### Framework Structure
```
tests/
├── WF{N}/                          # Per-workflow test directory
│   ├── wf{n}_test_tracking.yaml    # Master test configuration
│   ├── README.md                   # Workflow-specific documentation
│   ├── scripts/                    # Executable test scripts
│   │   ├── validate_environment.sh # Environment validation
│   │   ├── run_all_tests.sh       # Complete test suite
│   │   └── test_component.py       # Component-specific testing
│   ├── data/                       # Test data and fixtures
│   ├── results/                    # Test execution results
│   └── docs/                       # Additional documentation
```

## Test Phases (Universal)

### Phase 1: Environment Setup
- Docker service validation
- Health check verification
- Database connectivity
- Authentication setup
- Test data preparation

### Phase 2: Component Testing
- **Models**: ORM validation, field constraints, relationships
- **Services**: Business logic, HTTP handling, data processing
- **Routers**: API endpoints, authentication, input validation
- **Schedulers**: Background jobs, batch processing

### Phase 3: Integration Testing
- Cross-component communication
- Database transaction integrity
- API workflow validation
- Authentication enforcement

### Phase 4: Error Handling
- Invalid input scenarios
- Network failure simulation
- Timeout handling
- Transaction rollback validation

### Phase 5: End-to-End Testing
- Complete workflow pipeline
- Status transition verification
- Data integrity validation
- Performance monitoring

### Phase 6: Cleanup
- Test data removal
- Resource cleanup
- Result compilation

## YAML Configuration Standard

### Required Sections
```yaml
metadata:
  workflow_id: "WF{N}"
  workflow_name: "The {Name}"
  version: "1.0"
  test_framework_version: "1.0"
  docker_required: true
  production_safe: true

workflow_config:
  dependencies:
    upstream: []
    downstream: []
  database_tables:
    input: []
    output: []
    supporting: []
  api_endpoints:
    consumer: []
    dev_tools: []
    health: []

test_components:
  models: {}
  services: {}
  routers: {}
  schedulers: {}

test_scenarios:
  happy_path: []
  error_scenarios: []
  performance_scenarios: []

validation_queries: {}
success_criteria: {}
```

## Component Testing Standards (ScraperSky Layer Architecture)

### Layer 1 (L1): Data Sentinel - Models Layer
**Guardian Persona**: Layer 1 Data Sentinel
- Field validation and constraints
- Enum value validation
- Foreign key relationships
- Default value behavior
- Timestamp field functionality

### Layer 4 (L4): Service Arbiter - Services Layer
**Guardian Persona**: Layer 4 Service Arbiter
- Core business logic validation
- HTTP client behavior
- Data processing accuracy
- Error handling and rollback
- Transaction integrity

### Layer 3 (L3): Router Guardian - Routers Layer
**Guardian Persona**: Layer 3 Router Guardian
- CRUD operation validation
- Authentication enforcement
- Input validation
- Error response formatting
- Batch operation handling

### Layer 4 (L4): Service Arbiter - Schedulers Layer
**Guardian Persona**: Layer 4 Service Arbiter
- Background job execution
- Batch processing compliance
- Error isolation
- Status update accuracy
- Job completion logging

## Test Data Management

### Test Data Principles
- Deterministic UUIDs for reproducibility
- Isolated test domains (test-*.com pattern)
- Discovery method tagging for cleanup
- Foreign key integrity maintenance
- Complete cleanup procedures

### Cleanup Standards
```sql
-- Standard cleanup order (reverse dependency)
DELETE FROM {child_tables} WHERE {parent_id} IN (SELECT id FROM {parent_table} WHERE {test_condition});
DELETE FROM {parent_table} WHERE {test_condition};
```

## Authentication Standards

### JWT Token Management
- Automated token generation
- Mock token fallback for testing
- Header standardization
- Token validation testing

### Required Headers
```bash
Authorization: Bearer {JWT_TOKEN}
Content-Type: application/json
```

## Validation Standards

### Database Validation
- Status transition verification
- Foreign key integrity checks
- Record creation validation
- Transaction rollback verification

### API Validation
- Endpoint accessibility
- Response format validation
- Status code verification
- Error message accuracy

### Performance Validation
- Timeout compliance (60s standard)
- Memory usage monitoring
- Resource leak detection
- Batch processing efficiency

## Reporting Standards

### Result Format
```json
{
  "test_run_id": "uuid",
  "timestamp": "ISO-8601",
  "environment": "docker",
  "workflow": "WF{N}",
  "phases": {},
  "summary": {
    "total_tests": 0,
    "passed": 0,
    "failed": 0,
    "skipped": 0
  }
}
```

### Required Reports
- `wf{n}_test_results.json` - Detailed test results
- `wf{n}_coverage_report.html` - Code coverage analysis
- `wf{n}_performance.json` - Performance metrics
- `wf{n}_test_errors.log` - Error logs and debugging

## Extension Guidelines

### New Workflow Integration
1. Copy WF6 directory structure
2. Update YAML configuration for new workflow
3. Modify component tests for workflow-specific logic
4. Update API endpoints and database tables
5. Customize test scenarios for workflow requirements
6. Validate against framework standards

### Required Customizations
- Workflow metadata
- Database table mappings
- API endpoint specifications
- Component-specific test logic
- Error scenario definitions
- Performance criteria

## Tool Requirements

### System Dependencies
- Docker Desktop
- docker-compose
- curl (HTTP testing)
- jq (JSON processing)
- Python 3.8+ (component testing)
- PostgreSQL client (database validation)

### Python Dependencies
```
asyncio
asyncpg
httpx
pyyaml
```

## Success Criteria Framework

### Functional Requirements
- All status transitions work correctly
- Data records created with proper relationships
- Error scenarios handled gracefully
- API endpoints respond correctly
- Authentication enforced properly

### Performance Requirements
- HTTP requests complete within timeout limits
- Database transactions commit/rollback properly
- Memory usage remains stable
- No resource leaks detected

### Security Requirements
- JWT authentication required
- Tenant isolation maintained
- SQL injection prevention verified
- Input validation enforced

## Framework Ownership

**Layer 7 (L7) Test Sentinel Responsibility**: The Layer 7 Test Sentinel persona owns and maintains this testing framework, ensuring:
- Framework consistency across all workflows (WF1-WF7+)
- Docker-first testing compliance
- Environment safety protocols
- Layer-by-layer validation (L1-L8)
- Guardian Persona alignment
- Comprehensive error handling
- Performance monitoring
- Security validation

## Framework Evolution

### Version Control
- Framework version tracking in YAML
- Backward compatibility maintenance
- Migration guides for framework updates
- Change documentation

### Continuous Improvement
- Test coverage analysis
- Performance optimization
- Error scenario expansion
- Tool integration enhancement
- Documentation updates

---

**This framework serves as the foundation for all ScraperSky workflow testing, ensuring consistent, reliable, and safe testing practices across the entire system. The framework is designed to work seamlessly with the ScraperSky Layer Architecture (L1-L8) and Guardian Persona system, providing comprehensive testing coverage for all workflows (WF1-WF7+).**
