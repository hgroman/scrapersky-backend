# ScraperSky Testing Framework Architecture

**Created From:** WF6 AI Pairing Session Success  
**Foundation:** Layer 7 Test Sentinel v1.6 - Anti-Stub Guardian  
**Status:** Production-Ready Framework  
**Extensibility:** Template for All ScraperSky Workflows (WF1-WF7+)  

---

## Framework Overview

The ScraperSky Testing Framework is a comprehensive, Docker-first testing architecture designed around the ScraperSky Layer Architecture (L1-L8) and Guardian Persona system. Born from the successful WF6 AI pairing session, it provides systematic, component-by-component testing with complete environment isolation and production safety.

## Core Architecture Principles

### **1. Layer-Driven Testing**
- **Layer 1 (L1) Data Sentinel:** Models, schemas, database validation
- **Layer 3 (L3) Router Guardian:** API endpoints, request/response validation
- **Layer 4 (L4) Service Arbiter:** Business logic, background processing
- **Layer 7 (L7) Test Sentinel:** Framework ownership and quality assurance

### **2. Guardian Persona Alignment**
Each component maps to its responsible Guardian Persona:
```yaml
test_components:
  layer_1_models:
    guardian_persona: "Layer 1 Data Sentinel"
    responsibilities: ["Field validation", "Relationships", "Constraints"]
  
  layer_3_routers:
    guardian_persona: "Layer 3 Router Guardian"
    responsibilities: ["API contracts", "Authentication", "Request handling"]
  
  layer_4_services:
    guardian_persona: "Layer 4 Service Arbiter"
    responsibilities: ["Business logic", "Background processing", "Integration"]
```

### **3. Anti-Stub Architecture**
Absolute prohibition against stub/mock/placeholder implementations:
- Real database connections via fixtures
- Actual API endpoints (not mocked)
- Production-equivalent environments
- Genuine error scenario testing

### **4. Docker-First Environment Isolation**
```bash
# Environment-aware configuration
DATABASE_URL_TEST = os.getenv(
    "DATABASE_URL_TEST",
    "postgresql+asyncpg://postgres:password@localhost:5433/test_db"
)
```

---

## Framework Directory Structure

### **Universal Template (`/tests/WF{N}/`)**

```
tests/WF{N}/
├── wf{n}_test_tracking.yaml      # Master test configuration and tracking
├── README.md                     # Workflow-specific documentation
├── scripts/                      # Executable automation
│   ├── validate_environment.sh   # Docker/health validation
│   ├── run_all_tests.sh         # Complete test suite execution
│   └── test_component.py        # Python component testing
├── data/                         # Test data and fixtures
│   ├── test_sitemaps.xml        # Valid test data
│   └── malformed_sitemap.xml    # Error scenario data
├── results/                      # Test execution outputs
│   ├── wf{n}_test_results.json  # Detailed test results
│   ├── wf{n}_coverage_report.html # Code coverage analysis
│   ├── wf{n}_performance.json   # Performance metrics
│   └── wf{n}_test_errors.log    # Error logs and debugging
└── docs/                         # Additional documentation
    ├── DATABASE_TABLE_SPECIFICATIONS.md
    ├── REACT_FRONTEND_API_REFERENCE.md
    └── TESTING_FRAMEWORK_FOUNDATION.md
```

### **WF6 Implementation Example**

**Complete structure as created in the AI pairing session:**
- **wf6_test_tracking.yaml:** 438 lines of comprehensive test configuration
- **README.md:** 354 lines of complete workflow documentation
- **3 executable scripts:** Environment validation, test execution, component testing
- **Test data files:** Valid and error scenario sitemaps
- **Documentation:** Database specs, API reference, framework foundation

---

## YAML-Driven Test Tracking System

### **Configuration Structure**

```yaml
metadata:
  workflow_id: "WF6"
  workflow_name: "The Recorder"
  version: "1.0"
  test_framework_version: "1.0"
  docker_required: true
  production_safe: true

workflow_config:
  dependencies:
    upstream: ["WF5"]  # Input dependencies
    downstream: ["WF7"] # Output consumers
  
  database_schema:
    input_tables: ["sitemap_files"]
    output_tables: ["pages"]
    supporting_tables: ["domains"]

test_components:
  # Layer 1 (L1): Data Sentinel
  layer_1_models:
    sitemap_model:
      file: "src/models/sitemap.py"
      class: "SitemapFile"
      guardian_persona: "Layer 1 Data Sentinel"
      validation_points:
        - "UUID primary key generation"
        - "Foreign key constraints"
        - "Enum value validation"
        - "Timestamp field behavior"
  
  # Layer 3 (L3): Router Guardian  
  layer_3_routers:
    sitemap_files_router:
      file: "src/routers/sitemap_files.py"
      guardian_persona: "Layer 3 Router Guardian"
      validation_points:
        - "CRUD operations"
        - "Authentication enforcement"
        - "Input validation"
        - "Batch operations"
  
  # Layer 4 (L4): Service Arbiter
  layer_4_services:
    sitemap_import_service:
      file: "src/services/sitemap_import_service.py"
      guardian_persona: "Layer 4 Service Arbiter"
      validation_points:
        - "HTTP request handling"
        - "XML parsing accuracy"
        - "Transaction integrity"
        - "Error handling"
```

### **Test Scenario Definitions**

```yaml
test_scenarios:
  happy_path:
    - name: "successful_sitemap_processing"
      steps:
        - "Create test domain"
        - "Create sitemap file via API"
        - "Trigger manual processing"
        - "Validate status transitions"
        - "Verify page records created"
      expected_outcome: "Pages created with Complete status"
  
  error_scenarios:
    - name: "invalid_sitemap_url"
      steps:
        - "Create sitemap with invalid URL"
        - "Trigger processing"
        - "Validate Error status"
      expected_outcome: "Status = Error with descriptive message"
  
  performance_scenarios:
    - name: "large_sitemap_processing"
      steps:
        - "Create sitemap with 10,000+ URLs"
        - "Monitor memory usage"
        - "Validate completion time"
      expected_outcome: "Processing within resource limits"
```

---

## Component Testing Methodology

### **Phase-Based Testing Approach**

**Phase 1: Environment Setup & Health Validation**
```bash
# Mandatory pre-test checks
curl http://localhost:8000/health
curl http://localhost:8000/health/db

# Docker service verification
docker-compose ps
docker-compose logs app
```

**Phase 2: Component Testing (Layer-by-Layer)**

**Layer 1 (L1) - Data Sentinel Testing:**
```python
# Model validation tests
def test_sitemap_file_model_validation():
    """Test field constraints and relationships"""
    # UUID generation validation
    # Foreign key constraint testing
    # Enum value validation
    # Default value assignment
```

**Layer 3 (L3) - Router Guardian Testing:**
```bash
# API endpoint testing
curl -X POST "http://localhost:8000/api/v3/sitemap-files/" \
  -H "Authorization: Bearer $JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"domain_id": "test-uuid", "url": "https://example.com/sitemap.xml"}'
```

**Layer 4 (L4) - Service Arbiter Testing:**
```python
# Business logic testing
async def test_sitemap_processing_service():
    """Test HTTP handling, XML parsing, data creation"""
    # HTTP request validation
    # XML parsing accuracy
    # Page record creation
    # Status transition management
```

**Phase 3: Integration Testing**
- Cross-component communication
- Database transaction integrity
- API workflow validation
- Status transition verification

**Phase 4: Error Handling**
- Invalid input scenarios
- Network failure simulation
- Timeout handling
- Transaction rollback validation

**Phase 5: End-to-End Testing**
- Complete workflow pipeline
- WF5→WF6→WF7 dependency flow
- Performance monitoring
- Resource usage validation

**Phase 6: Cleanup & Reporting**
- Test data removal
- Resource cleanup
- Result compilation
- Performance analysis

---

## Database Integration Architecture

### **Table Specifications and Validation**

**Complete SQL schemas for each layer:**

```sql
-- Layer 1 (L1) Data Sentinel Validation
-- Input Table: sitemap_files
CREATE TABLE sitemap_files (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    domain_id UUID REFERENCES domains(id),
    url TEXT NOT NULL,
    sitemap_import_status sitemap_import_process_status_enum DEFAULT 'Queued',
    sitemap_import_error TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Output Table: pages  
CREATE TABLE pages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    domain_id UUID REFERENCES domains(id),
    sitemap_file_id UUID REFERENCES sitemap_files(id),
    url TEXT NOT NULL,
    page_curation_status page_curation_status DEFAULT 'New',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

### **Validation Query Templates**

```sql
-- Status transition verification
SELECT id, sitemap_import_status, sitemap_import_error 
FROM sitemap_files WHERE id = ?;

-- Page creation validation
SELECT COUNT(*), sitemap_file_id 
FROM pages WHERE sitemap_file_id = ? 
GROUP BY sitemap_file_id;

-- Foreign key integrity check
SELECT p.id, p.sitemap_file_id, sf.id 
FROM pages p 
LEFT JOIN sitemap_files sf ON p.sitemap_file_id = sf.id 
WHERE p.sitemap_file_id = ?;
```

### **Test Data Management**

```yaml
data_setup:
  test_domains:
    - domain: "test-example.com"
      status: "active"
      id: "550e8400-e29b-41d4-a716-446655440000"
  
  cleanup_procedures:
    - "DELETE FROM pages WHERE sitemap_file_id IN (SELECT id FROM sitemap_files WHERE discovery_method = 'test')"
    - "DELETE FROM sitemap_files WHERE discovery_method = 'test'"
    - "DELETE FROM domains WHERE domain LIKE 'test-%'"
```

---

## API Integration Architecture

### **Endpoint Testing Framework**

**Consumer Endpoints:**
```typescript
interface ApiEndpoints {
  listSitemapFiles: '/api/v3/sitemap-files/',
  createSitemapFile: '/api/v3/sitemap-files/',
  updateBatchStatus: '/api/v3/sitemap-files/sitemap_import_curation/status',
  triggerImport: '/api/v3/dev-tools/trigger-sitemap-import/{id}'
}
```

**Authentication Testing:**
```bash
# JWT token generation and validation
export JWT_TOKEN=$(curl -X POST "http://localhost:8000/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"username":"test_user","password":"test_pass"}' | \
  jq -r '.access_token')
```

**Response Validation:**
```typescript
interface SitemapFile {
  id: string;
  url: string;
  sitemap_import_status: 'Queued' | 'Processing' | 'Complete' | 'Error';
  sitemap_import_error?: string;
  page_count?: number;
}
```

---

## Docker-First Environment Safety

### **Container Isolation Protocols**

```yaml
# Docker Compose Test Configuration
services:
  app:
    environment:
      - DATABASE_URL_TEST=postgresql://test_user@postgres:5432/test_db
      - ENVIRONMENT=test
      - JWT_SECRET_KEY=test_secret
  
  postgres:
    environment:
      - POSTGRES_DB=test_db
      - POSTGRES_USER=test_user
      - POSTGRES_PASSWORD=test_pass
```

### **Production Safety Guards**

```python
# Environment validation
if 'production' in os.environ.get('DATABASE_URL', ''):
    raise RuntimeError("FATAL: Tests attempting production access!")

# Test-specific configuration
class TestSettings(Settings):
    database_url: str = "postgresql://localhost/test_db"
    environment: str = "test"
```

### **Health Check Integration**

```bash
# Mandatory health validation before testing
function validate_health() {
    curl -f http://localhost:8000/health || exit 1
    curl -f http://localhost:8000/health/db || exit 1
}
```

---

## Framework Extensibility

### **Extension Protocol for New Workflows**

1. **Copy Structure:**
   ```bash
   cp -r tests/WF6 tests/WF{N}
   ```

2. **Update Configuration:**
   ```yaml
   metadata:
     workflow_id: "WF{N}"
     workflow_name: "The {Name}"
   ```

3. **Customize Components:**
   - Update database table mappings
   - Modify API endpoint specifications
   - Adapt test scenarios for workflow logic
   - Configure Guardian Persona assignments

4. **Validate Framework:**
   ```bash
   cd tests/WF{N}
   ./scripts/validate_environment.sh
   ./scripts/run_all_tests.sh
   ```

### **Guardian Persona Integration**

Each workflow test must map to appropriate Guardian Personas:

```yaml
component_guardian_mapping:
  models: "Layer 1 Data Sentinel"
  schemas: "Layer 2 Schema Guardian"  
  routers: "Layer 3 Router Guardian"
  services: "Layer 4 Service Arbiter"
  config: "Layer 5 Config Conductor"
  ui: "Layer 6 UI Virtuoso"
  testing: "Layer 7 Test Sentinel"
```

---

## Success Metrics and Quality Gates

### **Functional Requirements**
✅ All status transitions work correctly  
✅ Data records created with proper relationships  
✅ Error scenarios handled gracefully  
✅ API endpoints respond correctly  
✅ Authentication enforced properly  

### **Performance Requirements**
✅ HTTP requests complete within timeout limits (60s)  
✅ Database transactions commit/rollback properly  
✅ Memory usage remains stable  
✅ No resource leaks detected  

### **Security Requirements**
✅ JWT authentication required  
✅ Tenant isolation maintained  
✅ SQL injection prevention verified  
✅ Input validation enforced  

### **Architectural Requirements**
✅ Layer architecture compliance  
✅ Guardian Persona alignment  
✅ Anti-stub implementation  
✅ Docker-first environment isolation  

---

## Framework Ownership and Governance

### **Layer 7 Test Sentinel Responsibility**

The Layer 7 Test Sentinel persona owns and maintains this framework:
- Framework consistency across all workflows (WF1-WF7+)
- Docker-first testing compliance
- Environment safety protocols
- Layer-by-layer validation (L1-L8)
- Guardian Persona alignment
- Anti-stub enforcement
- Quality assurance standards

### **Framework Evolution Protocol**

1. **Version Control:** Framework version tracking in YAML configurations
2. **Backward Compatibility:** Maintain migration paths for framework updates
3. **Documentation:** Update guides for framework changes
4. **Validation:** Test framework changes against existing workflows
5. **Guardian Review:** Architectural changes reviewed by relevant Guardian Personas

---

## Conclusion

The ScraperSky Testing Framework represents a production-ready, comprehensive testing architecture built on real-world AI pairing success. It provides:

1. **Systematic Testing:** Component-by-component validation across all layers
2. **Environmental Safety:** Docker-first isolation with production protection
3. **Architectural Alignment:** Proper Layer and Guardian Persona integration
4. **Extensible Design:** Template pattern for all ScraperSky workflows
5. **Quality Assurance:** Anti-stub protocols and comprehensive validation

This framework serves as the foundation for all ScraperSky workflow testing, ensuring consistent quality, architectural compliance, and production safety across the entire ecosystem.

---

**Framework Status:** ✅ **PRODUCTION READY**  
**Extension Status:** ✅ **TEMPLATE AVAILABLE**  
**Quality Assurance:** ✅ **LAYER 7 TEST SENTINEL APPROVED**