#!/bin/bash

################################################################################
# iNetZero Frontend - Production Deployment Script
# Deploys frontend to Vercel production
################################################################################

set -e

echo "╔════════════════════════════════════════════════════════════════╗"
echo "║     iNetZero Frontend - Production Deployment                  ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""

# Check if Vercel CLI is installed
if ! command -v vercel &> /dev/null; then
    echo "📦 Installing Vercel CLI..."
    npm install -g vercel
fi

echo "✅ Vercel CLI found"
echo ""

# Check if user is authenticated
echo "🔐 Checking Vercel authentication..."
if ! vercel whoami &> /dev/null; then
    echo "⚠️  Not authenticated with Vercel"
    echo "   Logging in now..."
    vercel login
fi

echo "✅ Authenticated with Vercel"
echo ""

# Verify frontend build exists
DIST_DIR="./frontend/dist"
if [ ! -d "$DIST_DIR" ]; then
    echo "❌ Error: Frontend dist directory not found"
    echo "   Run: npm run build"
    exit 1
fi

echo "✅ Frontend build found"
echo "   Directory: $DIST_DIR"
echo "   Size: $(du -sh $DIST_DIR | cut -f1)"
echo ""

# Get Vercel project info
VERCEL_PROJECT_ID=$(cat .vercel/project.json | grep projectId | cut -d'"' -f4)
VERCEL_ORG_ID=$(cat .vercel/project.json | grep orgId | cut -d'"' -f4)

echo "📋 Project Configuration:"
echo "   Project ID: $VERCEL_PROJECT_ID"
echo "   Org ID: $VERCEL_ORG_ID"
echo ""

# Deploy to production
echo "🚀 Deploying to production..."
echo ""

vercel deploy --prod --yes

echo ""
echo "╔════════════════════════════════════════════════════════════════╗"
echo "║     ✅ Deployment Complete!                                     ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""
echo "🎉 Your frontend is now live in production!"
echo ""
echo "📊 Deployment Summary:"
echo "   Build: frontend/dist"
echo "   Status: Production"
echo "   URL: Check console output above"
echo ""
echo "🔗 Next Steps:"
echo "   1. Visit your production URL"
echo "   2. Test login/signup"
echo "   3. Verify all pages load correctly"
echo "   4. Monitor error logs"
echo ""
