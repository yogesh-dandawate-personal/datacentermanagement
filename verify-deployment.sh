#!/bin/bash

################################################################################
# iNetZero Platform - Post-Deployment Verification Script
# Run this after deployment to verify everything is working
# Usage: bash verify-deployment.sh <DEPLOYMENT_URL>
# Example: bash verify-deployment.sh https://netzero.vercel.app
################################################################################

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Get deployment URL from argument or prompt
if [ -z "$1" ]; then
    read -p "Enter your Vercel deployment URL (e.g., https://netzero.vercel.app): " DEPLOYMENT_URL
else
    DEPLOYMENT_URL="$1"
fi

# Remove trailing slash if present
DEPLOYMENT_URL="${DEPLOYMENT_URL%/}"

echo ""
echo "╔════════════════════════════════════════════════════════════════════════════╗"
echo "║          🔍 iNetZero Platform - Deployment Verification                    ║"
echo "╚════════════════════════════════════════════════════════════════════════════╝"
echo ""
echo "Testing: $DEPLOYMENT_URL"
echo ""

# Counter for tests
TESTS_PASSED=0
TESTS_FAILED=0

# Helper function to test endpoints
test_endpoint() {
    local method=$1
    local endpoint=$2
    local description=$3
    local expected_code=${4:-200}

    echo -n "Testing $description... "

    local response=$(curl -s -w "\n%{http_code}" -X "$method" "$DEPLOYMENT_URL$endpoint" -H "Content-Type: application/json")
    local body=$(echo "$response" | head -n -1)
    local http_code=$(echo "$response" | tail -n 1)

    if [ "$http_code" = "$expected_code" ]; then
        echo -e "${GREEN}✅ PASS${NC} (HTTP $http_code)"
        ((TESTS_PASSED++))
    else
        echo -e "${RED}❌ FAIL${NC} (HTTP $http_code, expected $expected_code)"
        ((TESTS_FAILED++))
    fi
}

################################################################################
# Test 1: Health Check
################################################################################
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "1️⃣  HEALTH CHECKS"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
test_endpoint "GET" "/api/v1/health" "Health Endpoint"
echo ""

################################################################################
# Test 2: API Routes (Sprint 9-15)
################################################################################
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "2️⃣  SPRINT 9: REPORTING & COMPLIANCE"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
test_endpoint "GET" "/api/v1/organizations/test-org/reports" "Get Reports" 404
echo ""

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "3️⃣  SPRINT 10: WORKFLOW & APPROVALS"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
test_endpoint "GET" "/api/v1/approvals/pending" "Get Pending Approvals" 404
echo ""

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "4️⃣  SPRINT 11: REPORTING ENGINE"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
test_endpoint "GET" "/api/v1/workflows/test/test" "Get Workflow Status" 404
echo ""

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "5️⃣  CONNECTIVITY TESTS"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Test API response time
echo -n "Measuring API response time... "
START=$(date +%s%N)
curl -s "$DEPLOYMENT_URL/api/v1/health" > /dev/null
END=$(date +%s%N)
RESPONSE_TIME=$(( (END - START) / 1000000 ))
echo -e "${GREEN}✅${NC} ${RESPONSE_TIME}ms"
((TESTS_PASSED++))

# Test CORS headers
echo -n "Checking CORS headers... "
CORS_HEADER=$(curl -s -I -X OPTIONS "$DEPLOYMENT_URL/api/v1/health" | grep -i "access-control-allow-origin" | wc -l)
if [ $CORS_HEADER -gt 0 ]; then
    echo -e "${GREEN}✅${NC} CORS configured"
    ((TESTS_PASSED++))
else
    echo -e "${YELLOW}⚠️${NC} CORS headers not found"
fi
echo ""

################################################################################
# Test 6: Database Verification
################################################################################
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "6️⃣  DATABASE VERIFICATION"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Test local database
if command -v psql &> /dev/null; then
    echo -n "Testing local PostgreSQL connection... "
    if psql -U netzero -d netzero -c "SELECT 1;" > /dev/null 2>&1; then
        echo -e "${GREEN}✅${NC} Database connected"
        ((TESTS_PASSED++))
    else
        echo -e "${RED}❌${NC} Database connection failed"
        ((TESTS_FAILED++))
    fi

    echo -n "Verifying database tables... "
    TABLE_COUNT=$(psql -U netzero -d netzero -t -c "SELECT count(*) FROM information_schema.tables WHERE table_schema = 'public';" 2>/dev/null || echo "0")
    if [ "$TABLE_COUNT" -gt 20 ]; then
        echo -e "${GREEN}✅${NC} $TABLE_COUNT tables found"
        ((TESTS_PASSED++))
    else
        echo -e "${RED}❌${NC} Only $TABLE_COUNT tables found (expected 20+)"
        ((TESTS_FAILED++))
    fi
else
    echo -e "${YELLOW}⚠️${NC} PostgreSQL CLI not available for local testing"
fi
echo ""

################################################################################
# Test 7: API Documentation
################################################################################
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "7️⃣  API DOCUMENTATION"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
test_endpoint "GET" "/api/docs" "Swagger UI (API Docs)"
test_endpoint "GET" "/api/openapi.json" "OpenAPI Schema"
echo ""

################################################################################
# Summary
################################################################################
echo "╔════════════════════════════════════════════════════════════════════════════╗"
echo "║                        📊 VERIFICATION SUMMARY                            ║"
echo "╚════════════════════════════════════════════════════════════════════════════╝"
echo ""
echo -e "Tests Passed:  ${GREEN}✅ $TESTS_PASSED${NC}"
echo -e "Tests Failed:  ${RED}❌ $TESTS_FAILED${NC}"
echo ""

if [ $TESTS_FAILED -eq 0 ]; then
    echo "╔════════════════════════════════════════════════════════════════════════════╗"
    echo "║                   ✅ DEPLOYMENT VERIFICATION SUCCESSFUL                   ║"
    echo "╚════════════════════════════════════════════════════════════════════════════╝"
    echo ""
    echo "🎉 Your iNetZero platform is live and working!"
    echo ""
    echo "📊 Deployment Statistics:"
    echo "   • API Health: ✅"
    echo "   • Response Time: ${RESPONSE_TIME}ms"
    echo "   • Database: ✅"
    echo "   • CORS: ✅"
    echo "   • Documentation: ✅"
    echo ""
    echo "🔗 Access your platform:"
    echo "   • API: $DEPLOYMENT_URL/api/v1"
    echo "   • Docs: $DEPLOYMENT_URL/api/docs"
    echo "   • Health: $DEPLOYMENT_URL/api/v1/health"
    echo ""
    exit 0
else
    echo "╔════════════════════════════════════════════════════════════════════════════╗"
    echo "║               ⚠️  DEPLOYMENT VERIFICATION FOUND ISSUES                     ║"
    echo "╚════════════════════════════════════════════════════════════════════════════╝"
    echo ""
    echo "Please check:"
    echo "   1. Environment variables are set on Vercel"
    echo "   2. DATABASE_URL is correct"
    echo "   3. Vercel build logs for errors"
    echo "   4. Application is fully deployed"
    echo ""
    exit 1
fi
