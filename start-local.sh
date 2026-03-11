#!/bin/bash

# Local Development Server Startup Script for iNetZero
# Starts both Frontend (React) and Backend (FastAPI) servers

set -e

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$PROJECT_DIR"

# Colors for output
CYAN='\033[0;36m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${CYAN}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${CYAN}║  iNetZero - Local Development Server Startup                ║${NC}"
echo -e "${CYAN}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""

# Check Node.js
echo -e "${YELLOW}[1/5] Checking Node.js...${NC}"
if ! command -v node &> /dev/null; then
    echo -e "${RED}✗ Node.js not found. Please install Node.js 18+${NC}"
    exit 1
fi
NODE_VERSION=$(node -v)
echo -e "${GREEN}✓ Node.js ${NODE_VERSION}${NC}"
echo ""

# Check Python
echo -e "${YELLOW}[2/5] Checking Python 3...${NC}"
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}✗ Python 3 not found. Please install Python 3.9+${NC}"
    exit 1
fi
PYTHON_VERSION=$(python3 --version)
echo -e "${GREEN}✓ ${PYTHON_VERSION}${NC}"
echo ""

# Check/Install frontend dependencies
echo -e "${YELLOW}[3/5] Checking frontend dependencies...${NC}"
if [ ! -d "frontend/node_modules" ]; then
    echo -e "${YELLOW}Installing frontend dependencies...${NC}"
    cd frontend && npm install && cd ..
fi
echo -e "${GREEN}✓ Frontend dependencies ready${NC}"
echo ""

# Check/Install backend dependencies
echo -e "${YELLOW}[4/5] Checking backend dependencies...${NC}"
if ! python3 -c "import fastapi" 2>/dev/null; then
    echo -e "${YELLOW}Installing backend dependencies...${NC}"
    cd backend && python3 -m pip install -q -r requirements.txt && cd ..
fi
echo -e "${GREEN}✓ Backend dependencies ready${NC}"
echo ""

# Start services
echo -e "${YELLOW}[5/5] Starting services...${NC}"
echo ""

echo -e "${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║  Services Starting                                         ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""

echo -e "${GREEN}Frontend:${NC} http://localhost:3000"
echo -e "${GREEN}Backend:${NC}  http://localhost:8000"
echo -e "${GREEN}API Docs:${NC} http://localhost:8000/api/docs"
echo ""
echo -e "${YELLOW}Press Ctrl+C to stop all services${NC}"
echo ""

# Function to cleanup on exit
cleanup() {
    echo ""
    echo -e "${YELLOW}Stopping services...${NC}"
    kill %1 %2 2>/dev/null || true
    echo -e "${GREEN}✓ Services stopped${NC}"
    exit 0
}

# Set up trap to handle Ctrl+C
trap cleanup SIGINT SIGTERM

# Start backend in background
echo -e "${YELLOW}Starting Backend (FastAPI)...${NC}"
cd backend && python3 -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!
cd ..

# Give backend a moment to start
sleep 3

# Start frontend in background
echo -e "${YELLOW}Starting Frontend (React)...${NC}"
cd frontend && BROWSER=none npm start &
FRONTEND_PID=$!
cd ..

echo ""
echo -e "${GREEN}✓ All services started${NC}"
echo ""

# Wait for both processes
wait %1 %2 2>/dev/null || true
