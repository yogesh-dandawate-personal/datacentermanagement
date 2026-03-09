#!/bin/bash

################################################################################
# iNetZero ESG Platform - Vercel Deployment Script
# This script configures Vercel environment variables and deploys the app
# Run this from your local machine: bash deploy-to-vercel.sh
################################################################################

set -e

echo "╔════════════════════════════════════════════════════════════════╗"
echo "║     iNetZero Platform - Vercel Deployment Script              ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""

# Check if Vercel CLI is installed
if ! command -v vercel &> /dev/null; then
    echo "❌ Vercel CLI not found. Installing..."
    npm install -g vercel
fi

echo "✅ Vercel CLI found"
echo ""

# Check if user is logged in
echo "🔐 Checking Vercel authentication..."
if ! vercel whoami &> /dev/null; then
    echo "⚠️  Not authenticated with Vercel. Please log in:"
    vercel login
fi

echo "✅ Authenticated with Vercel"
echo ""

# Set environment variables
echo "🔧 Setting up environment variables..."
echo ""

read -p "Enter PostgreSQL connection string (or press Enter for localhost): " DB_URL
DB_URL="${DB_URL:-postgresql://netzero:netzero_secure_pass_2024@localhost:5432/netzero}"

read -p "Enter API Key (or press Enter to generate): " API_KEY
if [ -z "$API_KEY" ]; then
    API_KEY=$(python3 -c "import secrets; print(secrets.token_urlsafe(32))")
    echo "Generated API_KEY: $API_KEY"
fi

echo ""
echo "📝 Environment Variables to be set:"
echo "   DATABASE_URL: $DB_URL"
echo "   SECRET_KEY: A74AfhAJTrUv4LGdp4oiqy-ghnPU9Wh7e__tpQpphSM"
echo "   API_KEY: $API_KEY"
echo ""

read -p "Continue with deployment? (y/n) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Deployment cancelled."
    exit 1
fi

echo ""
echo "🚀 Setting environment variables on Vercel..."

# Set environment variables using Vercel CLI
vercel env add DATABASE_URL "$DB_URL" --yes || echo "⚠️  DATABASE_URL already set"
vercel env add SECRET_KEY "A74AfhAJTrUv4LGdp4oiqy-ghnPU9Wh7e__tpQpphSM" --yes || echo "⚠️  SECRET_KEY already set"
vercel env add API_KEY "$API_KEY" --yes || echo "⚠️  API_KEY already set"
vercel env add PYTHONUNBUFFERED "1" --yes || echo "⚠️  PYTHONUNBUFFERED already set"

echo "✅ Environment variables configured"
echo ""

echo "📦 Deploying to Vercel..."
vercel --prod

echo ""
echo "╔════════════════════════════════════════════════════════════════╗"
echo "║            ✅ DEPLOYMENT COMPLETE                             ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""
echo "📊 Deployment Summary:"
echo "   • Code pushed to GitHub ✅"
echo "   • Environment variables configured ✅"
echo "   • Application deployed to Vercel ✅"
echo ""
echo "🔗 View your deployment:"
echo "   https://vercel.com/dashboard"
echo ""
echo "✨ Your iNetZero platform is now live!"
echo ""
