#!/bin/bash

# Heroku Deployment Script for iNetZero

set -e

echo "🚀 Heroku Deployment Script"
echo "=============================="
echo ""

# Configuration
FRONTEND_APP=${FRONTEND_APP:-"inetze ro-frontend"}
BACKEND_APP=${BACKEND_APP:-"inetze ro-backend"}
REGION=${REGION:-"us"}

# Verify Heroku CLI
if ! command -v heroku &> /dev/null; then
    echo "❌ Heroku CLI not found. Please install it:"
    echo "   brew tap heroku/brew && brew install heroku"
    exit 1
fi

# Check if logged in
if ! heroku auth:whoami &> /dev/null; then
    echo "❌ Not logged in to Heroku. Please run:"
    echo "   heroku login"
    exit 1
fi

echo "✅ Logged in to Heroku"
echo ""

# Step 1: Enable Container Registry
echo "Step 1: Enabling Heroku Container Registry..."
heroku container:login
echo "✅ Container registry enabled"

# Step 2: Create Heroku apps
echo ""
echo "Step 2: Creating Heroku apps..."

if heroku apps:info $FRONTEND_APP 2>/dev/null; then
    echo "  ✅ Frontend app '$FRONTEND_APP' already exists"
else
    echo "  📝 Creating frontend app..."
    heroku create $FRONTEND_APP --region $REGION
    echo "  ✅ Created"
fi

if heroku apps:info $BACKEND_APP 2>/dev/null; then
    echo "  ✅ Backend app '$BACKEND_APP' already exists"
else
    echo "  📝 Creating backend app..."
    heroku create $BACKEND_APP --region $REGION
    echo "  ✅ Created"
fi

# Step 3: Build and push Frontend
echo ""
echo "Step 3: Building and pushing Frontend..."
docker build -t registry.heroku.com/$FRONTEND_APP/web ./frontend
docker push registry.heroku.com/$FRONTEND_APP/web
heroku container:release web --app $FRONTEND_APP
echo "✅ Frontend deployed"

# Step 4: Build and push Backend
echo ""
echo "Step 4: Building and pushing Backend..."
docker build -t registry.heroku.com/$BACKEND_APP/web ./backend
docker push registry.heroku.com/$BACKEND_APP/web
heroku container:release web --app $BACKEND_APP
echo "✅ Backend deployed"

# Step 5: Configure environment variables
echo ""
echo "Step 5: Configuring environment variables..."

BACKEND_URL="https://$BACKEND_APP.herokuapp.com"

heroku config:set REACT_APP_API_URL=$BACKEND_URL \
    --app $FRONTEND_APP
echo "✅ Frontend environment configured"

heroku config:set DATABASE_URL=sqlite:///./inetze ro.db \
    --app $BACKEND_APP
echo "✅ Backend environment configured"

# Step 6: Get app URLs
echo ""
echo "=============================="
echo "✅ Deployment Complete!"
echo "=============================="
echo ""

FRONTEND_DOMAIN="https://$FRONTEND_APP.herokuapp.com"
BACKEND_DOMAIN="https://$BACKEND_APP.herokuapp.com"

echo "📋 Application URLs:"
echo "  Frontend: $FRONTEND_DOMAIN"
echo "  Backend:  $BACKEND_DOMAIN"
echo "  API Docs: ${BACKEND_DOMAIN}/api/docs"
echo ""
echo "📚 Next Steps:"
echo "  1. Open frontend: heroku open --app $FRONTEND_APP"
echo "  2. Test API: curl $BACKEND_DOMAIN/api/v1/health"
echo "  3. View logs: heroku logs --tail --app $FRONTEND_APP"
echo "  4. Configure custom domain (optional)"
echo "  5. Set up auto-deploy from GitHub"
echo ""
echo "📖 Docs: https://devcenter.heroku.com"
echo ""
