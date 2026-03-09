#!/usr/bin/env python3
"""
Live Progress Reporter - Real-time progress bars like pip install

Shows:
- Sprint progress bars (visual progress with percentage)
- Agent utilization
- Task completion status
- ETA for completion
"""

import json
import time
import sys
import os
from pathlib import Path
from datetime import datetime
from typing import Dict, List
import threading


class LiveProgressReporter:
    """Real-time progress reporting with pip-style bars"""

    def __init__(self):
        self.state_path = Path("./.claude/orchestrator/state.json")
        self.execution_log_path = Path("./.claude/EXECUTION_LOG.md")
        self.start_time = time.time()

    def load_state(self) -> Dict:
        """Load current orchestrator state"""
        if self.state_path.exists():
            return json.loads(self.state_path.read_text())
        return {"agents": {}, "task_assignments": {}}

    def format_progress_bar(self, progress: float, width: int = 50, label: str = "") -> str:
        """Format a progress bar like pip install"""
        progress = min(100, max(0, progress))
        filled = int(width * progress / 100)
        bar = "█" * filled + "░" * (width - filled)
        percent = f"{progress:6.1f}%"
        return f"{label:30s} [{bar}] {percent}"

    def get_sprint_progress(self, state: Dict) -> Dict[str, float]:
        """Calculate progress for each sprint"""
        assignments = state.get("task_assignments", {})

        # Group tasks by sprint
        sprint_progress = {}
        for task_id, assignment in assignments.items():
            sprint = assignment.get("sprint", 0)
            phase = assignment.get("phase", "R0_RECEIVE")

            if sprint not in sprint_progress:
                sprint_progress[sprint] = {
                    "total": 0,
                    "completed": 0,
                    "phases": {}
                }

            sprint_progress[sprint]["total"] += 1

            # Calculate progress based on phase
            phase_progress = {
                "R0_RECEIVE": 10,
                "R1_UNDERSTAND": 20,
                "R2_RED": 30,
                "R3_GREEN": 50,
                "R4_REFACTOR": 70,
                "R5_CREATE_PR": 85,
                "R6_MERGE": 95,
                "R7_COMPLETE": 100
            }

            progress = phase_progress.get(phase, 0)
            sprint_progress[sprint]["phases"][task_id] = progress

            if progress == 100:
                sprint_progress[sprint]["completed"] += 1

        # Calculate percentages
        result = {}
        for sprint, data in sprint_progress.items():
            total = data["total"]
            if total > 0:
                avg_progress = sum(data["phases"].values()) / total
                result[f"Sprint {sprint}"] = {
                    "progress": avg_progress,
                    "completed": data["completed"],
                    "total": total
                }

        return result

    def get_agent_status(self, state: Dict) -> List[tuple]:
        """Get agent status summary"""
        agents = state.get("agents", {})

        status_list = []
        for agent_id, agent_data in agents.items():
            status = agent_data.get("status", "IDLE")
            utilization = agent_data.get("utilization", 0)
            status_list.append((agent_id, status, utilization))

        return sorted(status_list, key=lambda x: x[2], reverse=True)

    def display_sprints(self, state: Dict):
        """Display sprint progress bars"""
        sprint_progress = self.get_sprint_progress(state)

        print("\n" + "=" * 90)
        print("📊 SPRINT PROGRESS - Real-time Status")
        print("=" * 90)

        for sprint_name in sorted(sprint_progress.keys(),
                                  key=lambda x: int(x.split()[-1])):
            data = sprint_progress[sprint_name]
            progress = data["progress"]
            completed = data["completed"]
            total = data["total"]

            label = f"{sprint_name} ({completed}/{total} tasks)"
            bar = self.format_progress_bar(progress, label=label)
            print(bar)

        print("=" * 90)

    def display_agents(self, state: Dict):
        """Display agent status and utilization"""
        agents = self.get_agent_status(state)

        print("\n" + "=" * 90)
        print("🤖 AGENT UTILIZATION - Live Status")
        print("=" * 90)

        # Group by status
        by_status = {}
        for agent_id, status, util in agents:
            if status not in by_status:
                by_status[status] = []
            by_status[status].append((agent_id, util))

        # Display IN_PROGRESS first
        for status in ["IN_PROGRESS", "ASSIGNED", "IDLE", "BLOCKED"]:
            if status in by_status:
                count = len(by_status[status])
                status_emoji = {
                    "IN_PROGRESS": "🟢",
                    "ASSIGNED": "🟡",
                    "IDLE": "⚪",
                    "BLOCKED": "🔴"
                }
                print(f"\n{status_emoji.get(status, '❓')} {status} ({count} agents):")

                for agent_id, util in by_status[status][:5]:  # Show top 5
                    bar = self.format_progress_bar(
                        util,
                        width=40,
                        label=agent_id[:35]
                    )
                    print(f"  {bar}")

        print("=" * 90)

    def display_overall_metrics(self, state: Dict):
        """Display overall system metrics"""
        assignments = state.get("task_assignments", {})
        agents = state.get("agents", {})

        completed = sum(1 for a in assignments.values()
                       if a.get("phase") == "R7_COMPLETE")
        total = len(assignments)
        in_progress = sum(1 for a in agents.values()
                         if a.get("status") == "IN_PROGRESS")

        overall_progress = (completed / total * 100) if total > 0 else 0

        print("\n" + "=" * 90)
        print("📈 SYSTEM METRICS - Overall Progress")
        print("=" * 90)

        bar = self.format_progress_bar(overall_progress, label="Overall Progress")
        print(bar)

        elapsed = (time.time() - self.start_time) / 60
        print(f"\n📊 Statistics:")
        print(f"  ✅ Completed:    {completed:3d}/{total} tasks ({completed/total*100:5.1f}%)")
        print(f"  🟢 In Progress:  {in_progress:3d} agents")
        print(f"  ⏱️  Elapsed Time: {elapsed:6.1f} minutes")

        if total > 0 and completed > 0:
            rate = completed / elapsed if elapsed > 0 else 0
            remaining = (total - completed) / rate if rate > 0 else 0
            print(f"  ⚡ Rate:         {rate:5.2f} tasks/min")
            print(f"  ⏳ ETA:          {remaining:6.1f} minutes remaining")

        print("=" * 90)

    def clear_screen(self):
        """Clear terminal screen"""
        os.system("clear" if os.name != "nt" else "cls")

    def run_live(self, interval: int = 5):
        """Run live progress reporting"""
        print("🚀 Starting live progress monitoring...")
        print(f"⏰ Updates every {interval} seconds")
        print("📍 Press Ctrl+C to exit\n")

        try:
            iteration = 0
            while True:
                self.clear_screen()

                # Print header
                now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                print(f"\n🔴 LIVE PROGRESS - iNetZero Autonomous Development")
                print(f"⏰ {now} | Update #{iteration}\n")

                # Load state and display
                state = self.load_state()

                self.display_sprints(state)
                self.display_agents(state)
                self.display_overall_metrics(state)

                # Footer
                print(f"\n⏳ Next update in {interval} seconds... (Ctrl+C to exit)")

                iteration += 1
                time.sleep(interval)

        except KeyboardInterrupt:
            print("\n\n✅ Progress monitoring stopped.")
            sys.exit(0)

    def run_once(self):
        """Run progress reporting once and exit"""
        state = self.load_state()

        print("\n" + "=" * 90)
        print("📊 iNetZero Autonomous Development - Current Status")
        print("=" * 90)

        self.display_sprints(state)
        self.display_agents(state)
        self.display_overall_metrics(state)


def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(description="Live progress reporter")
    parser.add_argument(
        "--watch",
        action="store_true",
        help="Watch live updates (updates every 5 seconds)"
    )
    parser.add_argument(
        "--interval",
        type=int,
        default=5,
        help="Update interval in seconds (default: 5)"
    )

    args = parser.parse_args()

    reporter = LiveProgressReporter()

    if args.watch:
        reporter.run_live(interval=args.interval)
    else:
        reporter.run_once()


if __name__ == "__main__":
    main()
