#!/bin/bash

################################################################################
# iNetZero Frontend Staging Server Startup Script
# This script starts a simple HTTP server to serve the built frontend
# Run this from the project root: bash start-staging-server.sh
################################################################################

set -e

echo "╔════════════════════════════════════════════════════════════════╗"
echo "║     iNetZero Frontend - Staging Server Startup                ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""

# Check if dist directory exists
if [ ! -d "frontend/dist" ]; then
    echo "❌ Error: frontend/dist directory not found"
    echo "   Please run: npm run build"
    exit 1
fi

echo "✅ Frontend build artifacts found"
echo ""

# Detect OS and start appropriate server
OS=$(uname)
PORT=3000

echo "📦 Staging Server Configuration:"
echo "   Port: $PORT"
echo "   Root: frontend/dist"
echo "   URL: http://localhost:$PORT"
echo ""

# Check if port is already in use
if lsof -Pi :$PORT -sTCP:LISTEN -t >/dev/null 2>&1; then
    echo "⚠️  Port $PORT is already in use"
    read -p "   Use different port? (y/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        read -p "   Enter port number: " PORT
    else
        echo "   Exiting..."
        exit 1
    fi
fi

echo "🚀 Starting staging server on port $PORT..."
echo ""
echo "   Press Ctrl+C to stop the server"
echo ""

# Start HTTP server based on available tools
if command -v python3 &> /dev/null; then
    echo "✅ Using Python HTTP Server"
    cd frontend/dist
    python3 -m http.server $PORT --bind 127.0.0.1
elif command -v python &> /dev/null; then
    echo "✅ Using Python HTTP Server"
    cd frontend/dist
    python -m SimpleHTTPServer $PORT
elif command -v node &> /dev/null; then
    echo "✅ Using Node.js HTTP Server"
    cd frontend/dist
    npx http-server -p $PORT -a 127.0.0.1
else
    echo "❌ Error: No suitable HTTP server found"
    echo "   Install one of: Python, Node.js, or http-server"
    exit 1
fi
