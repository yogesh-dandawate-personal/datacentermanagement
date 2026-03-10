#!/bin/bash
#
# Launch Autonomous Sprint Queue System
# Starts Ralph Loop execution with Agent Teams in parallel
#
# Usage: ./launch-autonomous-sprints.sh [--duration-hours N] [--watch] [--headless]
#

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
LOG_DIR="$PROJECT_DIR/.claude/logs"
STATE_DIR="$PROJECT_DIR/.claude/state"
CONFIG_FILE="$PROJECT_DIR/.claude/config/sprint-queue-config.json"

# Parse arguments
DURATION_HOURS=48
WATCH_MODE=false
HEADLESS_MODE=false

while [[ $# -gt 0 ]]; do
  case $1 in
    --duration-hours)
      DURATION_HOURS="$2"
      shift 2
      ;;
    --watch)
      WATCH_MODE=true
      shift
      ;;
    --headless)
      HEADLESS_MODE=true
      shift
      ;;
    *)
      echo "Unknown option: $1"
      exit 1
      ;;
  esac
done

# Create necessary directories
mkdir -p "$LOG_DIR" "$STATE_DIR"

echo -e "${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║  AUTONOMOUS SPRINT QUEUE SYSTEM - LAUNCH SEQUENCE           ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""

# Verify configuration
echo -e "${YELLOW}[1/5] Verifying configuration...${NC}"
if [ ! -f "$CONFIG_FILE" ]; then
  echo -e "${RED}ERROR: Configuration file not found at $CONFIG_FILE${NC}"
  exit 1
fi
echo -e "${GREEN}✓ Configuration verified${NC}"
echo ""

# Initialize state directories
echo -e "${YELLOW}[2/5] Initializing state directories...${NC}"
touch "$STATE_DIR/sprint-queue-state.json"
touch "$LOG_DIR/sprint-queue.log"
echo -e "${GREEN}✓ State directories initialized${NC}"
echo ""

# Start sprint queue manager
echo -e "${YELLOW}[3/5] Starting Sprint Queue Manager...${NC}"
cd "$PROJECT_DIR"

# Create Python launch script
cat > "$STATE_DIR/launch-manager.py" << 'EOF'
import sys
sys.path.insert(0, '/Users/yogesh/00_MyCode/01_PersonalProjects/datacentermanagement')

from scripts.sprint_queue_manager import SprintQueueManager
import sys

duration = int(sys.argv[1]) if len(sys.argv) > 1 else 0

manager = SprintQueueManager()
manager.register_all_sprints()

print("\n" + "="*60)
print("AUTONOMOUS SPRINT QUEUE SYSTEM INITIALIZED")
print("="*60)
print(f"Total Sprints: 13")
print(f"Max Concurrent: 2")
print(f"Duration: {duration} minutes" if duration > 0 else "Duration: Unlimited")
print("Ralph Loop: Enabled")
print("Auto Recovery: Enabled")
print("="*60 + "\n")

try:
    manager.run_autonomous_loop(duration_minutes=duration)
except KeyboardInterrupt:
    print("\n[INTERRUPTED] Saving state...")
    manager.save_state()
except Exception as e:
    print(f"\n[ERROR] {str(e)}")
    manager.save_state()
    raise
EOF

# Convert duration to minutes
DURATION_MINUTES=$((DURATION_HOURS * 60))

# Run in background or foreground
if [ "$HEADLESS_MODE" = true ]; then
  echo -e "${GREEN}✓ Sprint Queue Manager started (headless mode)${NC}"
  python3 "$STATE_DIR/launch-manager.py" "$DURATION_MINUTES" > "$LOG_DIR/sprint-queue.log" 2>&1 &
  MANAGER_PID=$!
  echo "  PID: $MANAGER_PID"
else
  echo -e "${GREEN}✓ Sprint Queue Manager starting...${NC}"
  # Run in tmux session for better management
  if command -v tmux &> /dev/null; then
    tmux new-session -d -s "sprint-queue" -x 120 -y 40 \
      "cd $PROJECT_DIR && python3 $STATE_DIR/launch-manager.py $DURATION_MINUTES"
    MANAGER_PID=$(tmux list-panes -t sprint-queue -F '#{pane_pid}')
    echo "  Session: sprint-queue (PID: $MANAGER_PID)"
  else
    python3 "$STATE_DIR/launch-manager.py" "$DURATION_MINUTES" &
    MANAGER_PID=$!
    echo "  PID: $MANAGER_PID"
  fi
fi
echo ""

# Start live progress monitor (if watch mode)
echo -e "${YELLOW}[4/5] Starting progress monitoring...${NC}"
if [ "$WATCH_MODE" = true ]; then
  echo -e "${GREEN}✓ Live progress monitor started${NC}"

  # Create monitoring script
  cat > "$STATE_DIR/monitor.py" << 'EOF'
import json
import time
import os
from pathlib import Path
from datetime import datetime

state_file = Path('.claude/state/sprint-queue-state.json')

while True:
  try:
    if state_file.exists():
      with open(state_file, 'r') as f:
        state = json.load(f)
        summary = state.get('summary', {})

        print("\033[2J\033[H")  # Clear screen
        print("╔════════════════════════════════════════════════════════════╗")
        print("║            SPRINT QUEUE LIVE PROGRESS MONITOR              ║")
        print("╚════════════════════════════════════════════════════════════╝")
        print(f"Updated: {summary.get('timestamp', 'N/A')}\n")

        completed = summary.get('completed', 0)
        total = summary.get('total_sprints', 13)
        running = summary.get('running', 0)
        pending = summary.get('pending', 0)
        failed = summary.get('failed', 0)

        progress = (completed / total * 100) if total > 0 else 0
        bar_length = 50
        filled = int(bar_length * completed / total) if total > 0 else 0
        bar = '█' * filled + '░' * (bar_length - filled)

        print(f"Overall Progress: {progress:.1f}%")
        print(f"[{bar}]")
        print(f"\nSprints: {completed}/{total} | Running: {running} | Pending: {pending} | Failed: {failed}")

        story_points_completed = summary.get('completed_story_points', 0)
        story_points_total = summary.get('total_story_points', 0)
        sp_progress = (story_points_completed / story_points_total * 100) if story_points_total > 0 else 0
        print(f"Story Points: {story_points_completed}/{story_points_total} ({sp_progress:.1f}%)")

        print("\nPress Ctrl+C to stop monitoring")

    time.sleep(5)
  except KeyboardInterrupt:
    break
  except Exception as e:
    print(f"Error: {e}")
    time.sleep(5)
EOF

  if command -v tmux &> /dev/null; then
    tmux new-window -t sprint-queue -n "monitor" \
      "cd $PROJECT_DIR && python3 $STATE_DIR/monitor.py"
  fi
else
  echo -e "${GREEN}✓ Progress monitoring standby${NC}"
  echo "  Run 'make live-progress' to watch execution"
fi
echo ""

# Final status
echo -e "${YELLOW}[5/5] System ready${NC}"
echo -e "${GREEN}✓ Autonomous Sprint Queue System launched${NC}"
echo ""

echo -e "${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║  SYSTEM STATUS                                             ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════╝${NC}"
echo -e "Manager PID: ${GREEN}$MANAGER_PID${NC}"
echo -e "Duration: ${GREEN}$DURATION_HOURS hours ($DURATION_MINUTES minutes)${NC}"
echo -e "Config: ${GREEN}$CONFIG_FILE${NC}"
echo -e "Logs: ${GREEN}$LOG_DIR/sprint-queue.log${NC}"
echo -e "State: ${GREEN}$STATE_DIR/sprint-queue-state.json${NC}"
echo ""

if command -v tmux &> /dev/null; then
  echo -e "${YELLOW}Available tmux sessions:${NC}"
  tmux list-sessions | grep sprint-queue || true
  echo ""
  echo -e "${YELLOW}To attach to manager:${NC}"
  echo -e "  ${GREEN}tmux attach -t sprint-queue${NC}"
  echo ""
fi

echo -e "${YELLOW}To view logs:${NC}"
echo -e "  ${GREEN}tail -f $LOG_DIR/sprint-queue.log${NC}"
echo ""

echo -e "${YELLOW}To view report:${NC}"
echo -e "  ${GREEN}cat $STATE_DIR/sprint-queue-state.json | jq .${NC}"
echo ""

echo -e "${BLUE}════════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}System is now running autonomous sprints in Ralph Loop mode${NC}"
echo -e "${BLUE}════════════════════════════════════════════════════════════${NC}"
