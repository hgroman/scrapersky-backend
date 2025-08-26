#!/bin/bash
# WF6 Complete Test Suite Execution Script
# Test Sentinel: Layer 7 Testing Guardian
# Version: 1.0

set -e

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
NC='\033[0m' # No Color

# Test configuration
TEST_RUN_ID=$(date +%s)
RESULTS_DIR="results"
TEST_DATA_DIR="data"
TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%SZ")

echo -e "${PURPLE}🧪 WF6 Complete Test Suite${NC}"
echo "=================================="
echo "Test Run ID: $TEST_RUN_ID"
echo "Timestamp: $TIMESTAMP"
echo "Results Directory: $RESULTS_DIR"
echo ""

# Create results directory
mkdir -p $RESULTS_DIR

# Initialize test results
cat > $RESULTS_DIR/wf6_test_results.json << EOF
{
  "test_run_id": "$TEST_RUN_ID",
  "timestamp": "$TIMESTAMP",
  "environment": "docker",
  "workflow": "WF6",
  "workflow_name": "The Recorder",
  "phases": {},
  "summary": {
    "total_tests": 0,
    "passed": 0,
    "failed": 0,
    "skipped": 0
  }
}
EOF

# Function to update test results
update_results() {
    local phase=$1
    local test_name=$2
    local status=$3
    local message=$4
    
    # Use jq to update JSON results
    jq --arg phase "$phase" --arg test "$test_name" --arg status "$status" --arg msg "$message" \
       '.phases[$phase] = (.phases[$phase] // {}) | .phases[$phase][$test] = {"status": $status, "message": $msg}' \
       $RESULTS_DIR/wf6_test_results.json > $RESULTS_DIR/temp.json && mv $RESULTS_DIR/temp.json $RESULTS_DIR/wf6_test_results.json
}

# Function to print test status
print_test_status() {
    local status=$1
    local message=$2
    if [ "$status" = "PASS" ]; then
        echo -e "${GREEN}✅ $message${NC}"
    elif [ "$status" = "SKIP" ]; then
        echo -e "${YELLOW}⏭️  $message${NC}"
    else
        echo -e "${RED}❌ $message${NC}"
    fi
}

# Function to run test and capture result
run_test() {
    local phase=$1
    local test_name=$2
    local test_command=$3
    local description=$4
    
    echo -e "${BLUE}Running: $description${NC}"
    
    if eval "$test_command" 2>&1 | tee -a $RESULTS_DIR/wf6_test_errors.log; then
        print_test_status "PASS" "$test_name"
        update_results "$phase" "$test_name" "PASS" "$description"
        return 0
    else
        print_test_status "FAIL" "$test_name"
        update_results "$phase" "$test_name" "FAIL" "$description"
        return 1
    fi
}

# PHASE 1: Environment Setup
echo -e "\n${PURPLE}Phase 1: Environment Setup${NC}"
echo "============================"

run_test "environment_setup" "validate_environment" "./scripts/validate_environment.sh" "Environment validation"

# Generate JWT token for API tests
echo -e "\n${BLUE}Generating JWT token for API tests...${NC}"
JWT_RESPONSE=$(curl -s -X POST "http://localhost:8000/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"username":"test_user","password":"test_pass"}' || echo '{"error":"auth_failed"}')

if echo "$JWT_RESPONSE" | jq -e '.access_token' > /dev/null 2>&1; then
    export JWT_TOKEN=$(echo "$JWT_RESPONSE" | jq -r '.access_token')
    print_test_status "PASS" "JWT token generated"
    update_results "environment_setup" "jwt_generation" "PASS" "JWT token generated successfully"
else
    print_test_status "FAIL" "JWT token generation failed"
    update_results "environment_setup" "jwt_generation" "FAIL" "JWT token generation failed"
    echo "Continuing with mock token for testing..."
    export JWT_TOKEN="mock_token_for_testing"
fi

# PHASE 2: Component Testing
echo -e "\n${PURPLE}Phase 2: Component Testing${NC}"
echo "============================"

# Test 2.1: Model Validation
echo -e "\n${BLUE}2.1 Model Validation${NC}"
echo "--------------------"

# Check SitemapFile model structure
run_test "component_testing" "sitemap_model_structure" \
    "cd ../.. && docker-compose exec -T app python -c \"from src.models.sitemap import SitemapFile, SitemapImportProcessStatusEnum; print('SitemapFile model loaded successfully')\"" \
    "SitemapFile model structure validation"

# Check Page model structure
run_test "component_testing" "page_model_structure" \
    "cd ../.. && docker-compose exec -T app python -c \"from src.models.page import Page; print('Page model loaded successfully')\"" \
    "Page model structure validation"

# Test 2.2: Service Validation
echo -e "\n${BLUE}2.2 Service Validation${NC}"
echo "----------------------"

# Check SitemapImportService
run_test "component_testing" "sitemap_import_service" \
    "cd ../.. && docker-compose exec -T app python -c \"from src.services.sitemap_import_service import SitemapImportService; print('SitemapImportService loaded successfully')\"" \
    "SitemapImportService validation"

# Check scheduler function
run_test "component_testing" "sitemap_scheduler" \
    "cd ../.. && docker-compose exec -T app python -c \"from src.services.sitemap_import_scheduler import process_pending_sitemap_imports; print('Scheduler function loaded successfully')\"" \
    "Sitemap scheduler validation"

# Test 2.3: Router Validation
echo -e "\n${BLUE}2.3 Router Validation${NC}"
echo "---------------------"

# Test sitemap files router endpoints
run_test "component_testing" "sitemap_router_health" \
    "curl -s -f http://localhost:8000/api/v3/sitemap-files/ -H \"Authorization: Bearer \$JWT_TOKEN\" > /dev/null" \
    "Sitemap files router accessibility"

# Test dev tools router
run_test "component_testing" "dev_tools_router_health" \
    "curl -s -f http://localhost:8000/api/v3/dev-tools/scheduler_status -H \"Authorization: Bearer \$JWT_TOKEN\" > /dev/null" \
    "Dev tools router accessibility"

# PHASE 3: Integration Testing
echo -e "\n${PURPLE}Phase 3: Integration Testing${NC}"
echo "================================"

# Test 3.1: Database Integration
echo -e "\n${BLUE}3.1 Database Integration${NC}"
echo "------------------------"

# Create test domain
TEST_DOMAIN_ID=$(uuidgen | tr '[:upper:]' '[:lower:]')
TEST_TENANT_ID=$(uuidgen | tr '[:upper:]' '[:lower:]')

run_test "integration_testing" "create_test_domain" \
    "cd ../.. && docker-compose exec -T postgres psql -U scrapersky_user -d scrapersky_db -c \"INSERT INTO domains (id, domain, status, tenant_id) VALUES ('$TEST_DOMAIN_ID', 'test-example.com', 'active', '$TEST_TENANT_ID') ON CONFLICT DO NOTHING;\"" \
    "Test domain creation"

# Test 3.2: API Integration
echo -e "\n${BLUE}3.2 API Integration${NC}"
echo "-------------------"

# Create sitemap file via API
SITEMAP_CREATE_PAYLOAD=$(cat << EOF
{
  "domain_id": "$TEST_DOMAIN_ID",
  "url": "https://test-example.com/sitemap.xml",
  "sitemap_type": "Standard",
  "discovery_method": "test"
}
EOF
)

SITEMAP_RESPONSE=$(curl -s -X POST "http://localhost:8000/api/v3/sitemap-files/" \
  -H "Authorization: Bearer $JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d "$SITEMAP_CREATE_PAYLOAD" || echo '{"error":"api_failed"}')

if echo "$SITEMAP_RESPONSE" | jq -e '.id' > /dev/null 2>&1; then
    SITEMAP_FILE_ID=$(echo "$SITEMAP_RESPONSE" | jq -r '.id')
    print_test_status "PASS" "Sitemap file creation via API"
    update_results "integration_testing" "api_sitemap_creation" "PASS" "Sitemap file created successfully"
else
    print_test_status "FAIL" "Sitemap file creation via API"
    update_results "integration_testing" "api_sitemap_creation" "FAIL" "Sitemap file creation failed"
    # Use a mock ID for remaining tests
    SITEMAP_FILE_ID=$(uuidgen | tr '[:upper:]' '[:lower:]')
fi

# PHASE 4: Error Handling
echo -e "\n${PURPLE}Phase 4: Error Handling${NC}"
echo "==========================="

# Test 4.1: Invalid URL Handling
echo -e "\n${BLUE}4.1 Invalid URL Handling${NC}"
echo "------------------------"

# Create sitemap file with invalid URL
INVALID_SITEMAP_PAYLOAD=$(cat << EOF
{
  "domain_id": "$TEST_DOMAIN_ID",
  "url": "https://invalid-nonexistent-domain-12345.com/sitemap.xml",
  "sitemap_type": "Standard",
  "discovery_method": "test"
}
EOF
)

INVALID_RESPONSE=$(curl -s -X POST "http://localhost:8000/api/v3/sitemap-files/" \
  -H "Authorization: Bearer $JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d "$INVALID_SITEMAP_PAYLOAD" || echo '{"error":"api_failed"}')

if echo "$INVALID_RESPONSE" | jq -e '.id' > /dev/null 2>&1; then
    print_test_status "PASS" "Invalid URL sitemap creation"
    update_results "error_handling" "invalid_url_creation" "PASS" "Invalid URL sitemap created for error testing"
else
    print_test_status "SKIP" "Invalid URL sitemap creation (API validation prevented)"
    update_results "error_handling" "invalid_url_creation" "SKIP" "API validation prevented invalid URL creation"
fi

# PHASE 5: End-to-End Testing
echo -e "\n${PURPLE}Phase 5: End-to-End Testing${NC}"
echo "==============================="

# Test 5.1: Manual Trigger Test
echo -e "\n${BLUE}5.1 Manual Trigger Test${NC}"
echo "-----------------------"

if [ "$SITEMAP_FILE_ID" != "" ]; then
    # Trigger manual processing
    TRIGGER_RESPONSE=$(curl -s -X POST "http://localhost:8000/api/v3/dev-tools/trigger-sitemap-import/$SITEMAP_FILE_ID" \
      -H "Authorization: Bearer $JWT_TOKEN" || echo '{"error":"trigger_failed"}')
    
    if echo "$TRIGGER_RESPONSE" | jq -e '.message' > /dev/null 2>&1; then
        print_test_status "PASS" "Manual sitemap import trigger"
        update_results "end_to_end" "manual_trigger" "PASS" "Manual trigger executed successfully"
        
        # Wait a moment and check status
        sleep 3
        
        # Check sitemap file status
        STATUS_CHECK=$(cd ../.. && docker-compose exec -T postgres psql -U scrapersky_user -d scrapersky_db -c "SELECT sitemap_import_status FROM sitemap_files WHERE id = '$SITEMAP_FILE_ID';" -t | tr -d ' ')
        
        if [ "$STATUS_CHECK" != "" ]; then
            print_test_status "PASS" "Status check after trigger"
            update_results "end_to_end" "status_verification" "PASS" "Status: $STATUS_CHECK"
        else
            print_test_status "FAIL" "Status check after trigger"
            update_results "end_to_end" "status_verification" "FAIL" "Could not retrieve status"
        fi
    else
        print_test_status "FAIL" "Manual sitemap import trigger"
        update_results "end_to_end" "manual_trigger" "FAIL" "Manual trigger failed"
    fi
else
    print_test_status "SKIP" "Manual trigger test (no sitemap file ID)"
    update_results "end_to_end" "manual_trigger" "SKIP" "No sitemap file ID available"
fi

# PHASE 6: Cleanup
echo -e "\n${PURPLE}Phase 6: Cleanup${NC}"
echo "=================="

# Clean up test data
echo -e "\n${BLUE}Cleaning up test data...${NC}"

run_test "cleanup" "remove_test_pages" \
    "cd ../.. && docker-compose exec -T postgres psql -U scrapersky_user -d scrapersky_db -c \"DELETE FROM pages WHERE sitemap_file_id IN (SELECT id FROM sitemap_files WHERE discovery_method = 'test');\"" \
    "Remove test pages"

run_test "cleanup" "remove_test_sitemaps" \
    "cd ../.. && docker-compose exec -T postgres psql -U scrapersky_user -d scrapersky_db -c \"DELETE FROM sitemap_files WHERE discovery_method = 'test';\"" \
    "Remove test sitemap files"

run_test "cleanup" "remove_test_domains" \
    "cd ../.. && docker-compose exec -T postgres psql -U scrapersky_user -d scrapersky_db -c \"DELETE FROM domains WHERE domain LIKE 'test-%';\"" \
    "Remove test domains"

# Generate final test summary
echo -e "\n${PURPLE}Test Summary${NC}"
echo "============="

# Calculate totals and update summary
TOTAL_TESTS=$(jq '[.phases[] | to_entries[]] | length' $RESULTS_DIR/wf6_test_results.json)
PASSED_TESTS=$(jq '[.phases[] | to_entries[] | select(.value.status == "PASS")] | length' $RESULTS_DIR/wf6_test_results.json)
FAILED_TESTS=$(jq '[.phases[] | to_entries[] | select(.value.status == "FAIL")] | length' $RESULTS_DIR/wf6_test_results.json)
SKIPPED_TESTS=$(jq '[.phases[] | to_entries[] | select(.value.status == "SKIP")] | length' $RESULTS_DIR/wf6_test_results.json)

# Update summary in results file
jq --argjson total "$TOTAL_TESTS" --argjson passed "$PASSED_TESTS" --argjson failed "$FAILED_TESTS" --argjson skipped "$SKIPPED_TESTS" \
   '.summary = {"total_tests": $total, "passed": $passed, "failed": $failed, "skipped": $skipped}' \
   $RESULTS_DIR/wf6_test_results.json > $RESULTS_DIR/temp.json && mv $RESULTS_DIR/temp.json $RESULTS_DIR/wf6_test_results.json

echo "Total Tests: $TOTAL_TESTS"
echo -e "${GREEN}Passed: $PASSED_TESTS${NC}"
echo -e "${RED}Failed: $FAILED_TESTS${NC}"
echo -e "${YELLOW}Skipped: $SKIPPED_TESTS${NC}"

# Calculate success rate
if [ "$TOTAL_TESTS" -gt 0 ]; then
    SUCCESS_RATE=$(echo "scale=1; $PASSED_TESTS * 100 / $TOTAL_TESTS" | bc)
    echo "Success Rate: ${SUCCESS_RATE}%"
else
    SUCCESS_RATE=0
fi

# Final status
echo -e "\n${PURPLE}Final Results${NC}"
echo "=============="
echo "Test Run ID: $TEST_RUN_ID"
echo "Results File: $RESULTS_DIR/wf6_test_results.json"
echo "Error Log: $RESULTS_DIR/wf6_test_errors.log"

if [ "$FAILED_TESTS" -eq 0 ]; then
    echo -e "${GREEN}🎉 All tests completed successfully!${NC}"
    exit 0
else
    echo -e "${RED}⚠️  Some tests failed. Check the error log for details.${NC}"
    exit 1
fi
