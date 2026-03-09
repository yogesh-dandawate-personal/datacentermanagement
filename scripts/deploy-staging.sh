#!/bin/bash

# Deployment script for Vercel staging
# Usage: ./scripts/deploy-staging.sh

echo "╔════════════════════════════════════════════════════════════════╗"
echo "║   DEPLOYING TO VERCEL STAGING                                  ║"
echo "║   Project: netzero                                             ║"
echo "║   URL: inetzero-staging.vercel.app                             ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""

# Check if Vercel CLI is installed
if ! command -v vercel &> /dev/null; then
    echo "❌ Vercel CLI not found. Installing..."
    npm install -g vercel
fi

echo "✅ Vercel CLI found"
echo ""

# Check if already logged in
echo "Checking Vercel authentication..."
vercel whoami > /dev/null 2>&1
if [ $? -ne 0 ]; then
    echo "❌ Not logged into Vercel. Please login first:"
    echo "   vercel login"
    exit 1
fi
echo "✅ Vercel authentication confirmed"
echo ""

# Get current project scope
SCOPE="yogesh-dandawates-projects"
echo "Using scope: $SCOPE"
echo ""

# Ask user for database URL
echo "════════════════════════════════════════════════════════════════"
echo "STEP 1: DATABASE CONFIGURATION"
echo "════════════════════════════════════════════════════════════════"
echo ""
echo "You need to provide a PostgreSQL connection string."
echo ""
echo "Options:"
echo "  1. Use Supabase (Free): https://supabase.com"
echo "  2. Use Railway ($5/mo): https://railway.app"
echo "  3. Use local database: postgresql://user:pass@host:5432/db"
echo "  4. Skip for now (API will work but can't persist data)"
echo ""
read -p "Enter DATABASE_URL (or press Enter to skip): " DATABASE_URL

if [ -z "$DATABASE_URL" ]; then
    echo "⚠️  Skipping database configuration"
    echo "   You can add DATABASE_URL later in Vercel UI"
    DATABASE_URL="postgresql://localhost:5432/netzero_staging"
fi

echo ""
echo "════════════════════════════════════════════════════════════════"
echo "STEP 2: VERCEL ENVIRONMENT VARIABLES"
echo "════════════════════════════════════════════════════════════════"
echo ""
echo "Setting environment variables in Vercel..."
echo ""

# Generate SECRET_KEY if not exists
SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_urlsafe(32))")

echo "Generated SECRET_KEY: $SECRET_KEY"
echo ""

# Deploy with environment variables
echo "Deploying to staging..."
echo ""

vercel deploy \
    --scope $SCOPE \
    --env DATABASE_URL="$DATABASE_URL" \
    --env SECRET_KEY="$SECRET_KEY" \
    --env API_TITLE="NetZero API" \
    --env API_VERSION="1.0.0" \
    --env DEBUG="false" \
    --env LOG_LEVEL="info" 2>&1 | tee /tmp/vercel-deploy.log

DEPLOY_STATUS=$?

echo ""
echo "════════════════════════════════════════════════════════════════"
echo "DEPLOYMENT RESULT"
echo "════════════════════════════════════════════════════════════════"
echo ""

if [ $DEPLOY_STATUS -eq 0 ]; then
    echo "✅ DEPLOYMENT SUCCESSFUL!"
    echo ""
    echo "Your staging environment is ready:"
    echo "  🌐 URL: https://inetzero-staging.vercel.app"
    echo ""
    echo "Next steps:"
    echo "  1. Test API: curl https://inetzero-staging.vercel.app/api/v1/health"
    echo "  2. View logs: vercel logs netzero --scope $SCOPE"
    echo "  3. Verify endpoints are working"
    echo "  4. Check database connectivity"
    echo ""
    echo "To view deployment:"
    echo "  vercel ls --scope $SCOPE"
    echo ""
else
    echo "❌ DEPLOYMENT FAILED"
    echo ""
    echo "Troubleshooting:"
    echo "  1. Check logs: tail -f /tmp/vercel-deploy.log"
    echo "  2. Verify DATABASE_URL is correct"
    echo "  3. Ensure SECRET_KEY is set"
    echo "  4. Check Vercel dashboard: https://vercel.com/dashboard"
    echo ""
fi

echo "════════════════════════════════════════════════════════════════"
