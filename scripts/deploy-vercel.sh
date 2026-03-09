#!/bin/bash
# Vercel Deployment Script for iNetZero
#
# Automatically deploys frontend and backend to Vercel
# Supports staging (auto) and production (manual approval)

set -e

ENVIRONMENT=${1:-staging}
FORCE_DEPLOY=${2:-false}

GREEN='\033[0;32m'
YELLOW='\033[0;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${GREEN}iNetZero Vercel Deployment${NC}"
echo "Environment: $ENVIRONMENT"
echo ""

# Check if Vercel CLI is installed
if ! command -v vercel &> /dev/null; then
    echo -e "${RED}Vercel CLI not found. Install with: npm install -g vercel${NC}"
    exit 1
fi

# Check environment variables
if [ -z "$VERCEL_TOKEN" ]; then
    echo -e "${RED}VERCEL_TOKEN not set${NC}"
    exit 1
fi

# Load configuration
CONFIG_FILE=".claude/config/parallel-sprints-config.json"
if [ ! -f "$CONFIG_FILE" ]; then
    echo -e "${RED}Config file not found: $CONFIG_FILE${NC}"
    exit 1
fi

# Parse config
PROJECT_NAME=$(jq -r '.vercel_deployment.project_name' "$CONFIG_FILE")
AUTO_DEPLOY=$(jq -r ".vercel_deployment.environments.$ENVIRONMENT.auto_deploy" "$CONFIG_FILE")
URL=$(jq -r ".vercel_deployment.environments.$ENVIRONMENT.url" "$CONFIG_FILE")

echo "Project: $PROJECT_NAME"
echo "URL: $URL"
echo ""

# Production requires approval
if [ "$ENVIRONMENT" = "production" ] && [ "$FORCE_DEPLOY" != "true" ]; then
    echo -e "${YELLOW}⚠ Production deployment requires approval${NC}"
    echo "Verify all tests pass and staging is stable:"
    echo ""
    echo "  ✓ Sprint 1-12 completed and deployed to staging"
    echo "  ✓ All automated tests passing (>95%)"
    echo "  ✓ Performance benchmarks meet targets (1000+ users)"
    echo "  ✓ Security scans show no critical issues"
    echo ""
    read -p "Proceed with production deployment? (type 'yes' to confirm): " confirm
    if [ "$confirm" != "yes" ]; then
        echo "Deployment cancelled"
        exit 0
    fi
fi

# Build frontend
echo -e "${GREEN}Building frontend...${NC}"
cd frontend
npm install --production
npm run build
cd ..

# Build backend
echo -e "${GREEN}Building backend...${NC}"
cd backend
npm install --production
npm run build
cd ..

# Deploy to Vercel
echo -e "${GREEN}Deploying to Vercel ($ENVIRONMENT)...${NC}"

DEPLOY_ARGS="--token $VERCEL_TOKEN --project $PROJECT_NAME"

if [ "$ENVIRONMENT" = "staging" ]; then
    DEPLOY_ARGS="$DEPLOY_ARGS --build-env NODE_ENV=staging"
    vercel deploy --prebuilt $DEPLOY_ARGS
    echo -e "${GREEN}✓ Staging deployment complete${NC}"
    echo "  URL: $URL"

elif [ "$ENVIRONMENT" = "production" ]; then
    DEPLOY_ARGS="$DEPLOY_ARGS --prod --build-env NODE_ENV=production"
    echo -e "${RED}Deploying to PRODUCTION${NC}"
    vercel deploy --prebuilt $DEPLOY_ARGS
    echo -e "${GREEN}✓ Production deployment complete${NC}"
    echo "  URL: $URL"

    # Post-deployment verification
    echo ""
    echo -e "${GREEN}Running post-deployment checks...${NC}"

    # Health check
    if curl -f "$URL/health" &> /dev/null; then
        echo -e "${GREEN}✓ Health check passed${NC}"
    else
        echo -e "${RED}✗ Health check failed${NC}"
        exit 1
    fi

    # Log deployment
    TIMESTAMP=$(date -u +%Y-%m-%dT%H:%M:%SZ)
    cat >> deploy-log.json << EOF
{
  "timestamp": "$TIMESTAMP",
  "environment": "production",
  "status": "success",
  "url": "$URL"
}
EOF

fi

echo ""
echo -e "${GREEN}Deployment complete!${NC}"
echo "View logs: vercel logs $PROJECT_NAME"
echo "Manage project: https://vercel.com/$PROJECT_NAME"
