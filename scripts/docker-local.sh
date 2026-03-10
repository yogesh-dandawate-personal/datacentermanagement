#!/bin/bash

# Local Docker Testing Script for iNetZero

set -e

echo "🐳 iNetZero Local Docker Testing"
echo "===================================="
echo ""

# Check for docker-compose.yml
if [ ! -f "docker-compose.yml" ]; then
    echo "❌ docker-compose.yml not found in project root"
    exit 1
fi

# Available commands
COMMAND=${1:-"help"}

case $COMMAND in
    start)
        echo "Starting services..."
        docker-compose up -d
        echo ""
        echo "✅ Services started!"
        echo ""
        echo "📋 Access Points:"
        echo "  Frontend: http://localhost:3000"
        echo "  Backend:  http://localhost:8000"
        echo "  API Docs: http://localhost:8000/api/docs"
        echo ""
        echo "📊 View logs:"
        echo "  docker-compose logs -f"
        ;;

    stop)
        echo "Stopping services..."
        docker-compose down
        echo "✅ Services stopped"
        ;;

    restart)
        echo "Restarting services..."
        docker-compose restart
        echo "✅ Services restarted"
        ;;

    logs)
        echo "Showing logs (Ctrl+C to exit)..."
        docker-compose logs -f
        ;;

    build)
        echo "Building Docker images..."
        docker-compose build
        echo "✅ Images built"
        ;;

    status)
        echo "Service Status:"
        docker-compose ps
        ;;

    shell-frontend)
        echo "Opening shell in frontend container..."
        docker-compose exec frontend sh
        ;;

    shell-backend)
        echo "Opening shell in backend container..."
        docker-compose exec backend bash
        ;;

    test-frontend)
        echo "Testing frontend..."
        curl -s http://localhost:3000 | head -20
        echo ""
        echo "✅ Frontend responding"
        ;;

    test-backend)
        echo "Testing backend..."
        curl -s http://localhost:8000/api/v1/health
        echo ""
        echo "✅ Backend responding"
        ;;

    clean)
        echo "Cleaning up Docker resources..."
        docker-compose down -v
        docker system prune -f
        echo "✅ Cleanup complete"
        ;;

    help)
        echo "Available commands:"
        echo ""
        echo "  start           - Start all services"
        echo "  stop            - Stop all services"
        echo "  restart         - Restart all services"
        echo "  logs            - View service logs"
        echo "  build           - Build Docker images"
        echo "  status          - Show service status"
        echo "  shell-frontend  - Open shell in frontend"
        echo "  shell-backend   - Open shell in backend"
        echo "  test-frontend   - Test frontend connectivity"
        echo "  test-backend    - Test backend connectivity"
        echo "  clean           - Clean up all Docker resources"
        echo "  help            - Show this help message"
        echo ""
        echo "Examples:"
        echo "  ./scripts/docker-local.sh start"
        echo "  ./scripts/docker-local.sh logs"
        echo "  ./scripts/docker-local.sh test-frontend"
        ;;

    *)
        echo "❌ Unknown command: $COMMAND"
        echo "Run './scripts/docker-local.sh help' for available commands"
        exit 1
        ;;
esac
