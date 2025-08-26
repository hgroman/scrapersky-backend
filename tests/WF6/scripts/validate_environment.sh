#!/bin/bash
# WF6 Environment Validation Script
# Test Sentinel: Layer 7 Testing Guardian
# Version: 1.0

set -e

echo "🔍 WF6 Environment Validation Starting..."
echo "================================================"

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print status
print_status() {
    local status=$1
    local message=$2
    if [ "$status" = "OK" ]; then
        echo -e "${GREEN}✅ $message${NC}"
    elif [ "$status" = "WARN" ]; then
        echo -e "${YELLOW}⚠️  $message${NC}"
    else
        echo -e "${RED}❌ $message${NC}"
    fi
}

# Function to check command exists
check_command() {
    if command -v $1 &> /dev/null; then
        print_status "OK" "$1 is installed"
        return 0
    else
        print_status "FAIL" "$1 is not installed"
        return 1
    fi
}

# 1. Check required commands
echo -e "${BLUE}1. Checking Required Commands${NC}"
echo "--------------------------------"
check_command "docker" || { echo "Install Docker Desktop"; exit 1; }
check_command "docker-compose" || { echo "Install docker-compose"; exit 1; }
check_command "curl" || { echo "Install curl"; exit 1; }
check_command "jq" || { echo "Install jq for JSON parsing"; exit 1; }

# 2. Check Docker status
echo -e "\n${BLUE}2. Checking Docker Status${NC}"
echo "----------------------------"
if docker info &> /dev/null; then
    print_status "OK" "Docker daemon is running"
else
    print_status "FAIL" "Docker daemon is not running"
    echo "Start Docker Desktop and try again"
    exit 1
fi

# 3. Check Docker Compose services
echo -e "\n${BLUE}3. Checking Docker Compose Services${NC}"
echo "-------------------------------------"
if [ -f "../../docker-compose.yml" ]; then
    print_status "OK" "docker-compose.yml found"
    
    # Check if services are running
    cd ../..
    if docker-compose ps | grep -q "Up"; then
        print_status "OK" "Docker services are running"
        
        # List running services
        echo "Running services:"
        docker-compose ps --format "table {{.Name}}\t{{.Status}}\t{{.Ports}}"
    else
        print_status "WARN" "Docker services are not running"
        echo "Starting services..."
        docker-compose up -d
        sleep 10
    fi
    cd tests/WF6
else
    print_status "FAIL" "docker-compose.yml not found in project root"
    exit 1
fi

# 4. Check application health
echo -e "\n${BLUE}4. Checking Application Health${NC}"
echo "--------------------------------"
max_attempts=30
attempt=1

while [ $attempt -le $max_attempts ]; do
    if curl -s http://localhost:8000/health &> /dev/null; then
        health_response=$(curl -s http://localhost:8000/health)
        print_status "OK" "Application health check passed"
        echo "Health response: $health_response"
        break
    else
        if [ $attempt -eq $max_attempts ]; then
            print_status "FAIL" "Application health check failed after $max_attempts attempts"
            echo "Check application logs: docker-compose logs app"
            exit 1
        else
            echo "Attempt $attempt/$max_attempts: Waiting for application to start..."
            sleep 2
            ((attempt++))
        fi
    fi
done

# 5. Check database health
echo -e "\n${BLUE}5. Checking Database Health${NC}"
echo "-----------------------------"
if curl -s http://localhost:8000/health/db &> /dev/null; then
    db_health=$(curl -s http://localhost:8000/health/db)
    print_status "OK" "Database health check passed"
    echo "Database response: $db_health"
else
    print_status "FAIL" "Database health check failed"
    echo "Check database logs: docker-compose logs postgres"
    exit 1
fi

# 6. Check database connectivity
echo -e "\n${BLUE}6. Checking Database Connectivity${NC}"
echo "-----------------------------------"
cd ../..
if docker-compose exec -T postgres psql -U scrapersky_user -d scrapersky_db -c "SELECT 1;" &> /dev/null; then
    print_status "OK" "Database connection successful"
else
    print_status "FAIL" "Database connection failed"
    echo "Check database configuration and credentials"
    exit 1
fi
cd tests/WF6

# 7. Check required tables exist
echo -e "\n${BLUE}7. Checking Required Tables${NC}"
echo "-----------------------------"
cd ../..
required_tables=("domains" "sitemap_files" "pages")
for table in "${required_tables[@]}"; do
    if docker-compose exec -T postgres psql -U scrapersky_user -d scrapersky_db -c "SELECT 1 FROM $table LIMIT 1;" &> /dev/null; then
        print_status "OK" "Table '$table' exists and accessible"
    else
        print_status "FAIL" "Table '$table' does not exist or is not accessible"
        echo "Run database migrations: docker-compose exec app alembic upgrade head"
        exit 1
    fi
done
cd tests/WF6

# 8. Check test data directory
echo -e "\n${BLUE}8. Checking Test Environment${NC}"
echo "------------------------------"
if [ -d "data" ]; then
    print_status "OK" "Test data directory exists"
else
    print_status "WARN" "Test data directory missing, creating..."
    mkdir -p data
fi

if [ -d "results" ]; then
    print_status "OK" "Test results directory exists"
else
    print_status "WARN" "Test results directory missing, creating..."
    mkdir -p results
fi

if [ -d "scripts" ]; then
    print_status "OK" "Test scripts directory exists"
else
    print_status "FAIL" "Test scripts directory missing"
    exit 1
fi

# 9. Check YAML configuration
echo -e "\n${BLUE}9. Checking Test Configuration${NC}"
echo "--------------------------------"
if [ -f "wf6_test_tracking.yaml" ]; then
    print_status "OK" "WF6 test tracking YAML found"
    
    # Validate YAML syntax
    if python3 -c "import yaml; yaml.safe_load(open('wf6_test_tracking.yaml'))" 2>/dev/null; then
        print_status "OK" "YAML syntax is valid"
    else
        print_status "FAIL" "YAML syntax is invalid"
        exit 1
    fi
else
    print_status "FAIL" "WF6 test tracking YAML not found"
    exit 1
fi

# 10. Environment summary
echo -e "\n${BLUE}10. Environment Summary${NC}"
echo "------------------------"
echo "Docker version: $(docker --version)"
echo "Docker Compose version: $(docker-compose --version)"
echo "Application URL: http://localhost:8000"
echo "Health endpoint: http://localhost:8000/health"
echo "Database health: http://localhost:8000/health/db"
echo "Test directory: $(pwd)"

echo -e "\n${GREEN}🎉 Environment validation completed successfully!${NC}"
echo "================================================"
echo "Ready to run WF6 tests. Use: ./scripts/run_all_tests.sh"
