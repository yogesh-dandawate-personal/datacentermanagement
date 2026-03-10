#!/bin/bash

# Google Cloud Run Deployment Script for iNetZero

set -e

echo "🚀 Google Cloud Run Deployment Script"
echo "========================================"
echo ""

# Configuration
PROJECT_ID=${PROJECT_ID:-""}
REGION=${REGION:-"us-central1"}
FRONTEND_SERVICE="inetze ro-frontend"
BACKEND_SERVICE="inetze ro-backend"

# Verify gcloud CLI
if ! command -v gcloud &> /dev/null; then
    echo "❌ gcloud CLI not found. Please install it:"
    echo "   brew install --cask google-cloud-sdk"
    exit 1
fi

# Get project ID if not provided
if [ -z "$PROJECT_ID" ]; then
    PROJECT_ID=$(gcloud config get-value project)
    if [ -z "$PROJECT_ID" ]; then
        echo "❌ No project ID found. Please set it:"
        echo "   gcloud config set project YOUR_PROJECT_ID"
        exit 1
    fi
fi

echo "📋 Configuration:"
echo "  Project: $PROJECT_ID"
echo "  Region: $REGION"
echo ""

# Step 1: Enable APIs
echo "Step 1: Enabling required APIs..."
gcloud services enable containerregistry.googleapis.com \
    cloudbuild.googleapis.com \
    run.googleapis.com \
    --project=$PROJECT_ID
echo "✅ APIs enabled"

# Step 2: Configure Docker authentication
echo ""
echo "Step 2: Configuring Docker authentication..."
gcloud auth configure-docker
echo "✅ Docker configured"

# Step 3: Build and push Frontend
echo ""
echo "Step 3: Building and pushing Frontend..."
docker build -t gcr.io/$PROJECT_ID/$FRONTEND_SERVICE:latest ./frontend
docker push gcr.io/$PROJECT_ID/$FRONTEND_SERVICE:latest
echo "✅ Frontend pushed"

# Step 4: Build and push Backend
echo ""
echo "Step 4: Building and pushing Backend..."
docker build -t gcr.io/$PROJECT_ID/$BACKEND_SERVICE:latest ./backend
docker push gcr.io/$PROJECT_ID/$BACKEND_SERVICE:latest
echo "✅ Backend pushed"

# Step 5: Deploy to Cloud Run
echo ""
echo "Step 5: Deploying to Cloud Run..."

echo "  Deploying Frontend..."
gcloud run deploy $FRONTEND_SERVICE \
    --image gcr.io/$PROJECT_ID/$FRONTEND_SERVICE:latest \
    --platform managed \
    --region $REGION \
    --port 3000 \
    --allow-unauthenticated \
    --project=$PROJECT_ID

echo "  Deploying Backend..."
gcloud run deploy $BACKEND_SERVICE \
    --image gcr.io/$PROJECT_ID/$BACKEND_SERVICE:latest \
    --platform managed \
    --region $REGION \
    --port 8000 \
    --allow-unauthenticated \
    --project=$PROJECT_ID

# Step 6: Get service URLs
echo ""
echo "=============================="
echo "✅ Deployment Complete!"
echo "=============================="
echo ""

FRONTEND_URL=$(gcloud run services describe $FRONTEND_SERVICE \
    --platform managed \
    --region $REGION \
    --project=$PROJECT_ID \
    --format='value(status.address.url)')

BACKEND_URL=$(gcloud run services describe $BACKEND_SERVICE \
    --platform managed \
    --region $REGION \
    --project=$PROJECT_ID \
    --format='value(status.address.url)')

echo "📋 Service URLs:"
echo "  Frontend: $FRONTEND_URL"
echo "  Backend:  $BACKEND_URL"
echo "  API Docs: ${BACKEND_URL}/api/docs"
echo ""
echo "📚 Next Steps:"
echo "  1. Test the endpoints above"
echo "  2. Configure environment variables (Cloud Run console)"
echo "  3. Set up custom domain (optional)"
echo "  4. Configure CI/CD for auto-deployment"
echo ""
echo "📖 Docs: https://cloud.google.com/run/docs"
echo ""
