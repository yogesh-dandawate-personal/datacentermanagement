#!/bin/bash
#
# Sprint 10 Parallel Execution Setup
# Creates tmux session with 5 worktrees (one per task)
# Each worktree has dedicated agent team
#

set -e

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_DIR"

echo -e "${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║  SPRINT 10 - PARALLEL EXECUTION SETUP (tmux + worktrees)   ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""

# Kill existing session if it exists
if tmux has-session -t sprint-10 2>/dev/null; then
  echo -e "${YELLOW}Killing existing tmux session 'sprint-10'${NC}"
  tmux kill-session -t sprint-10
fi

# Create main tmux session
echo -e "${YELLOW}Creating tmux session: sprint-10${NC}"
tmux new-session -d -s sprint-10 -x 240 -y 50

# Array of tasks
declare -a TASKS=(
  "10.1:Models:Backend_Database_01"
  "10.2:Ingestion:Backend_Services_01"
  "10.3:Calculation:Backend_Services_01"
  "10.4:Analytics:Backend_Analytics_01"
  "10.5:Dashboard:Frontend_React_01"
)

# Create worktrees and windows
for task in "${TASKS[@]}"; do
  IFS=':' read -r TASK_ID TASK_NAME AGENT <<< "$task"
  WORKTREE_NAME="sprint-10-task-${TASK_ID//./-}"
  BRANCH_NAME="sprint/10-task-${TASK_ID//./-}"
  
  echo -e "${GREEN}Setting up: Task $TASK_ID ($TASK_NAME) - Agent: $AGENT${NC}"
  
  # Create git worktree
  if [ -d ".git/worktrees/$WORKTREE_NAME" ]; then
    echo "  Removing existing worktree..."
    git worktree remove "$WORKTREE_NAME" 2>/dev/null || true
  fi
  
  echo "  Creating worktree: $WORKTREE_NAME"
  git worktree add -b "$BRANCH_NAME" "$WORKTREE_NAME" main 2>/dev/null || git worktree add "$WORKTREE_NAME" main
  
  # Create tmux window
  WINDOW_NAME="task-${TASK_ID//./-}"
  echo "  Creating tmux window: $WINDOW_NAME"
  tmux new-window -t sprint-10 -n "$WINDOW_NAME"
  
  # Setup window
  tmux send-keys -t "sprint-10:$WINDOW_NAME" "cd '$PROJECT_DIR/$WORKTREE_NAME'" Enter
  sleep 1
  
  # Create task info file
  cat > "$WORKTREE_NAME/.task-info.txt" << EOF
╔═══════════════════════════════════════════════════════════════╗
║  SPRINT 10 - TASK $TASK_ID                                      ║
╚═══════════════════════════════════════════════════════════════╝

Task Name:    $TASK_NAME
Agent Lead:   $AGENT
Worktree:     $WORKTREE_NAME
Branch:       $BRANCH_NAME
Working Dir:  $(pwd)/$WORKTREE_NAME

═══════════════════════════════════════════════════════════════

Agent Instructions:
1. cd $WORKTREE_NAME  (already done)
2. Review task requirements in .task-${TASK_ID}.md
3. Implement solution in this worktree
4. Run tests: pytest tests/
5. Commit changes: git add . && git commit -m "Sprint 10 Task $TASK_ID"
6. Push when ready: git push origin $BRANCH_NAME

═══════════════════════════════════════════════════════════════
EOF
  
  # Create task requirements file
  cat > "$WORKTREE_NAME/.task-${TASK_ID}.md" << EOF
# Sprint 10 Task $TASK_ID: $TASK_NAME

**Agent**: $AGENT  
**Status**: 🔄 IN_PROGRESS  
**Worktree**: $WORKTREE_NAME  
**Timeline**: See .claude/SPRINT_10_DETAILED_STATUS.md

## What to Build

See parent directory: ../.claude/SPRINT_10_DETAILED_STATUS.md for full details

Task 10.$((${TASK_ID##*.})) breakdown includes:
- Specific deliverables
- Code structure
- Tests required
- Success criteria

## Commands

\`\`\`bash
# Build
npm run build        # Frontend
python -m pytest     # Backend tests

# Run locally
npm run dev          # Frontend dev server
uvicorn app.main:app --reload  # Backend

# Commit work
git add .
git commit -m "Sprint 10 Task $TASK_ID: [description]"
git push origin $BRANCH_NAME
\`\`\`

## Status
- Current: Check task status in parent SPRINT_10_DETAILED_STATUS.md
- Progress: Update this as you work
- Blockers: Report in tmux if stuck

EOF

  echo "  ✓ Setup complete for Task $TASK_ID"
  echo ""
done

# Create status dashboard window
echo -e "${GREEN}Creating status dashboard window${NC}"
tmux new-window -t sprint-10 -n "status"
tmux send-keys -t "sprint-10:status" "cd '$PROJECT_DIR' && watch -n 5 'echo \"\\n=== SPRINT 10 STATUS ===\\n\" && git branch -a | grep sprint/10 && echo \"\\n\" && ls -la .git/worktrees/'" Enter

# Create main coordination window
echo -e "${GREEN}Creating coordinator window${NC}"
tmux new-window -t sprint-10 -n "coord"
tmux send-keys -t "sprint-10:coord" "cd '$PROJECT_DIR'" Enter

# Display session layout
echo ""
echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}✓ Sprint 10 tmux session created!${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
echo ""
echo "Session Name: sprint-10"
echo "Windows:"
echo "  1. task-10-1   → Task 10.1: Models (Backend_Database_01)"
echo "  2. task-10-2   → Task 10.2: Ingestion (Backend_Services_01)"
echo "  3. task-10-3   → Task 10.3: Calculation (Backend_Services_01)"
echo "  4. task-10-4   → Task 10.4: Analytics (Backend_Analytics_01)"
echo "  5. task-10-5   → Task 10.5: Dashboard (Frontend_React_01)"
echo "  6. status      → Live git worktree status"
echo "  7. coord       → Coordinator console"
echo ""
echo -e "${YELLOW}Attach to session:${NC}"
echo "  tmux attach -t sprint-10"
echo ""
echo -e "${YELLOW}Attach to specific window:${NC}"
echo "  tmux attach -t sprint-10:task-10-2  # Task 10.2"
echo ""
echo -e "${YELLOW}View all windows:${NC}"
echo "  tmux list-windows -t sprint-10"
echo ""
echo -e "${YELLOW}Send command to window:${NC}"
echo "  tmux send-keys -t sprint-10:task-10-2 'pytest tests/' Enter"
echo ""

