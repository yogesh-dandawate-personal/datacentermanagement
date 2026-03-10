#!/bin/bash

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
API_URL="${1:-http://localhost:8000}"
TIMEOUT=30
RETRIES=5

echo -e "${BLUE}=== Deployment Verification Script ===${NC}"
echo -e "API URL: ${BLUE}${API_URL}${NC}"
echo "Timeout: ${TIMEOUT}s per request"
echo "Max retries: ${RETRIES}"
echo ""

# Function to test API endpoint
test_endpoint() {
    local endpoint=$1
    local expected_status=$2
    local description=$3

    echo -n "Testing ${description}... "

    for attempt in $(seq 1 $RETRIES); do
        response=$(curl -s -w "\n%{http_code}" -m $TIMEOUT "${API_URL}${endpoint}" 2>/dev/null || echo "error")
        http_code=$(echo "$response" | tail -n1)

        if [ "$http_code" = "$expected_status" ]; then
            echo -e "${GREEN}✓${NC} (HTTP $http_code)"
            return 0
        fi

        if [ $attempt -lt $RETRIES ]; then
            echo -n "."
            sleep 3
        fi
    done

    echo -e "${RED}✗${NC} (HTTP $http_code, expected $expected_status)"
    return 1
}

# Function to check service health
check_health() {
    local service=$1
    local endpoint=$2

    echo ""
    echo -e "${BLUE}Checking ${service}...${NC}"

    for attempt in $(seq 1 $RETRIES); do
        if curl -s -m $TIMEOUT "${API_URL}${endpoint}" > /dev/null 2>&1; then
            echo -e "${GREEN}✓${NC} ${service} is responding"
            return 0
        fi

        if [ $attempt -lt $RETRIES ]; then
            echo -n "."
            sleep 3
        fi
    done

    echo -e "${RED}✗${NC} ${service} is not responding"
    return 1
}

# Initialize counters
passed=0
failed=0

# Test core endpoints
echo -e "${BLUE}=== Testing Core Endpoints ===${NC}"
echo ""

if test_endpoint "/api/organizations" "200" "GET /api/organizations"; then
    ((passed++))
else
    ((failed++))
fi

if test_endpoint "/api/health" "200" "GET /api/health"; then
    ((passed++))
else
    ((failed++))
fi

# Test health check
echo ""
echo -e "${BLUE}=== Health Checks ===${NC}"
echo ""

if check_health "API Server" "/api/health"; then
    ((passed++))
else
    ((failed++))
fi

# Additional verification
echo ""
echo -e "${BLUE}=== Additional Verification ===${NC}"
echo ""

# Check if service is accepting connections
echo -n "Checking port connectivity... "
if timeout 3 bash -c "cat < /dev/null > /dev/tcp/${API_URL#http*//*}:${API_URL##*:}" 2>/dev/null; then
    echo -e "${GREEN}✓${NC}"
    ((passed++))
else
    echo -e "${YELLOW}⊘${NC} (May be normal if running behind proxy)"
fi

# Summary
echo ""
echo -e "${BLUE}=== Verification Summary ===${NC}"
echo ""
echo "Tests passed: $passed"
echo "Tests failed: $failed"
echo ""

if [ $failed -eq 0 ]; then
    echo -e "${GREEN}✓ All verifications passed!${NC}"
    echo "Deployment is healthy and ready for use."
    exit 0
else
    echo -e "${RED}✗ Some verifications failed.${NC}"
    echo "Please check the logs above and verify deployment status."
    exit 1
fi
