#!/bin/bash
# tmux Agent Session Startup Script
#
# Creates detached tmux session per agent with 6 windows:
# 0: Agent control (logs, metrics)
# 1: Backend service (if applicable)
# 2: Frontend service (if applicable)
# 3: Testing (continuous watch mode)
# 4: Database (migrations, schema)
# 5: Monitoring (health checks every 30s)

set -e

# Arguments
AGENT_ID=${1:-"Backend_FastAPI_01"}
SESSION_ID=${2:-"default"}
STORY_ID=${3:-"ICARBON-TEST"}
SPRINT=${4:-1}

SESSION_NAME="agent-${AGENT_ID}-${SESSION_ID}"
LOG_DIR="/.claude/agents/${AGENT_ID}/logs"
STATE_DIR="/.claude/agents/${AGENT_ID}/state"

# Colors
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
NC='\033[0m'

echo -e "${GREEN}Starting agent session: ${SESSION_NAME}${NC}"

# Create directories
mkdir -p "${LOG_DIR}"
mkdir -p "${STATE_DIR}"

# Check if session already exists
if tmux has-session -t "${SESSION_NAME}" 2>/dev/null; then
    echo -e "${YELLOW}Session already exists: ${SESSION_NAME}${NC}"
    tmux attach-session -t "${SESSION_NAME}"
    exit 0
fi

# Create new detached session
tmux new-session -d -s "${SESSION_NAME}" -x 200 -y 50

# Window 0: Agent Control
tmux send-keys -t "${SESSION_NAME}:0" "cd /Users/yogesh/00_MyCode/01_PersonalProjects/datacentermanagement" C-m
tmux send-keys -t "${SESSION_NAME}:0" "echo 'Agent: ${AGENT_ID} | Story: ${STORY_ID} | Sprint: ${SPRINT}'" C-m
tmux send-keys -t "${SESSION_NAME}:0" "echo 'Logs: ${LOG_DIR}'" C-m
tmux send-keys -t "${SESSION_NAME}:0" "echo 'Session: ${SESSION_NAME}'" C-m
tmux send-keys -t "${SESSION_NAME}:0" "tail -f ${LOG_DIR}/*.log 2>/dev/null || echo 'Waiting for logs...'" C-m

# Window 1: Backend Service
tmux new-window -t "${SESSION_NAME}" -n backend
tmux send-keys -t "${SESSION_NAME}:1" "cd ./backend && npm run dev" C-m

# Window 2: Frontend Service
tmux new-window -t "${SESSION_NAME}" -n frontend
tmux send-keys -t "${SESSION_NAME}:2" "cd ./frontend && npm start" C-m

# Window 3: Testing (watch mode)
tmux new-window -t "${SESSION_NAME}" -n testing
tmux send-keys -t "${SESSION_NAME}:3" "cd ./backend && npm run test:watch -- --coverage" C-m

# Window 4: Database
tmux new-window -t "${SESSION_NAME}" -n database
tmux send-keys -t "${SESSION_NAME}:4" "echo 'Database console (run migrations, etc.)'" C-m
tmux send-keys -t "${SESSION_NAME}:4" "cd ./backend && npm run migrate:watch || true" C-m

# Window 5: Monitoring
tmux new-window -t "${SESSION_NAME}" -n monitoring
tmux send-keys -t "${SESSION_NAME}:5" "watch -n 30 'echo \"=== Health Check ===\"; \
  echo \"Backend: \$(curl -s -o /dev/null -w '%{http_code}' http://localhost:3000/health)\"; \
  echo \"Frontend: \$(curl -s -o /dev/null -w '%{http_code}' http://localhost:3001)\"; \
  echo \"Database: \$(pg_isready -h localhost 2>&1 || echo \\\"down\\\")\"; \
  echo \"Services: \$(docker-compose ps | grep -c Up || echo 0) running\"'" C-m

# Rename window 0
tmux rename-window -t "${SESSION_NAME}:0" "control"

echo -e "${GREEN}✓ Agent session created: ${SESSION_NAME}${NC}"
echo ""
echo "Available windows:"
echo "  0: control    - Agent control and logs"
echo "  1: backend    - Backend API service"
echo "  2: frontend   - Frontend web app"
echo "  3: testing    - Test watch mode"
echo "  4: database   - Database migrations"
echo "  5: monitoring - Health checks"
echo ""
echo "Commands:"
echo "  tmux attach-session -t ${SESSION_NAME}"
echo "  tmux send-keys -t ${SESSION_NAME}:0 'command' C-m"
echo "  tmux kill-session -t ${SESSION_NAME}"
echo ""

# Save session info
cat > "${STATE_DIR}/session_${SESSION_ID}.json" << EOF
{
  "agent_id": "${AGENT_ID}",
  "session_id": "${SESSION_ID}",
  "story_id": "${STORY_ID}",
  "sprint": ${SPRINT},
  "tmux_session": "${SESSION_NAME}",
  "created_at": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
  "log_dir": "${LOG_DIR}",
  "windows": {
    "0": "control",
    "1": "backend",
    "2": "frontend",
    "3": "testing",
    "4": "database",
    "5": "monitoring"
  }
}
EOF

echo -e "${GREEN}Session info saved to: ${STATE_DIR}/session_${SESSION_ID}.json${NC}"
