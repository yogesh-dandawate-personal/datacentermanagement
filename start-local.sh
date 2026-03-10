#!/bin/bash

# Sprint 8 Local Deployment Script
# Starts both backend and frontend servers

set -e

PROJECT_DIR="/Users/yogesh/00_MyCode/01_PersonalProjects/datacentermanagement"

echo "🚀 Starting Sprint 8 Local Deployment"
echo "======================================"
echo ""

# Check if Node/npm is available
if ! command -v npm &> /dev/null; then
    echo "❌ npm not found. Please install Node.js"
    exit 1
fi

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 not found. Please install Python 3"
    exit 1
fi

echo "✅ Environment checks passed"
echo ""

# Kill any existing processes on ports 8000 and 5173
echo "🔍 Checking for existing processes..."
lsof -i :8000 2>/dev/null && kill -9 $(lsof -ti :8000) && echo "   Killed process on port 8000" || echo "   Port 8000 clear"
lsof -i :5173 2>/dev/null && kill -9 $(lsof -ti :5173) && echo "   Killed process on port 5173" || echo "   Port 5173 clear"
echo ""

echo "📦 Checking dependencies..."
cd "$PROJECT_DIR/frontend"
if [ ! -d "node_modules" ]; then
    echo "   Installing npm packages..."
    npm install --silent
else
    echo "   npm packages already installed"
fi
echo ""

echo "✅ Ready to start servers!"
echo ""
echo "Starting servers in background..."
echo ""

# Start backend in background
echo "📡 Starting Backend API (Port 8000)..."
cd "$PROJECT_DIR"
python3 -m uvicorn backend.app.main:app --reload --host 127.0.0.1 --port 8000 > /tmp/backend.log 2>&1 &
BACKEND_PID=$!
echo "   Backend PID: $BACKEND_PID"

# Wait for backend to start
sleep 3

# Start frontend in background
echo "🎨 Starting Frontend (Port 5173)..."
cd "$PROJECT_DIR/frontend"
npm run dev > /tmp/frontend.log 2>&1 &
FRONTEND_PID=$!
echo "   Frontend PID: $FRONTEND_PID"

# Wait for frontend to start
sleep 3

echo ""
echo "======================================"
echo "✅ SPRINT 8 IS NOW RUNNING LOCALLY!"
echo "======================================"
echo ""
echo "🌐 Frontend:  http://localhost:5173"
echo "📡 Backend:   http://127.0.0.1:8000"
echo "📚 API Docs:  http://127.0.0.1:8000/api/docs"
echo ""
echo "📝 Test Pages:"
echo "   - Marketplace: /marketplace"
echo "   - Portfolio:   /portfolio"
echo "   - Trading:     /trading"
echo ""
echo "📊 Backend Tests:"
echo "   python3 -m pytest backend/tests/test_marketplace_service.py -v"
echo ""
echo "🛑 To stop servers:"
echo "   kill $BACKEND_PID  # Stop backend"
echo "   kill $FRONTEND_PID # Stop frontend"
echo ""
echo "📋 Logs:"
echo "   Backend:  tail -f /tmp/backend.log"
echo "   Frontend: tail -f /tmp/frontend.log"
echo ""
echo "Press Ctrl+C to view this menu again"
echo ""

# Save PIDs for easy cleanup
echo "$BACKEND_PID" > /tmp/sprint8-backend.pid
echo "$FRONTEND_PID" > /tmp/sprint8-frontend.pid

# Keep script running
wait
