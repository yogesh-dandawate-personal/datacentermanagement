#!/usr/bin/env python3
"""
Task Assigner - Assigns stories to agents for parallel execution

Pulls stories from sprint queue and assigns to available agents.
Updates agent status (IDLE → ASSIGNED → IN_PROGRESS).
Manages parallel execution with auto-progression.
"""

import json
import time
import random
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional


class TaskAssigner:
    """Assigns tasks to agents and manages execution"""

    def __init__(self):
        self.state_path = Path("./.claude/orchestrator/state.json")
        self.config_path = Path("./.claude/config/agent-assignments.json")

    def load_state(self) -> Dict:
        """Load current orchestrator state"""
        if self.state_path.exists():
            return json.loads(self.state_path.read_text())
        return None

    def save_state(self, state: Dict):
        """Save updated state"""
        self.state_path.write_text(json.dumps(state, indent=2))

    def load_sprint_assignments(self) -> Dict:
        """Load sprint-to-agent assignments"""
        if self.config_path.exists():
            return json.loads(self.config_path.read_text())
        return None

    def assign_sprint_tasks(self, sprint_num: int, force: bool = False):
        """
        Assign all tasks for a sprint to agents.
        Agents transition: IDLE → ASSIGNED
        """
        print(f"\n📋 Assigning Sprint {sprint_num} tasks to agents...")

        state = self.load_state()
        if not state:
            print("❌ No state file found")
            return

        config = self.load_sprint_assignments()
        if not config:
            print("❌ No sprint config found")
            return

        # Find sprint config
        sprint_key = f"sprint_{sprint_num}_"
        sprint_config = None
        sprint_name = None

        for key, cfg in config.get("sprints", {}).items():
            if key.startswith(sprint_key):
                sprint_config = cfg
                sprint_name = cfg.get("name", f"Sprint {sprint_num}")
                break

        if not sprint_config:
            print(f"❌ Sprint {sprint_num} not found in config")
            return

        agents = state.get("agents", {})
        agent_assignments = state.get("task_assignments", {})

        # Assign agents from sprint config
        assigned_agents = sprint_config.get("agents", [])
        story_count = len(sprint_config.get("stories", []))
        story_points = sprint_config.get("story_points", 0)

        print(f"✅ Sprint: {sprint_name}")
        print(f"   Story Points: {story_points}")
        print(f"   Stories: {story_count}")
        print(f"   Assigned Agents: {len(assigned_agents)}")
        print()

        assignment_count = 0
        for agent_type in assigned_agents:
            # Find matching agent
            matching_agent = None
            for agent_id, agent_data in agents.items():
                if agent_type in agent_id and agent_data.get("status") == "IDLE":
                    matching_agent = agent_id
                    break

            if matching_agent:
                # Transition to ASSIGNED
                agents[matching_agent]["status"] = "ASSIGNED"

                # Create mock story assignment
                story_id = f"ICARBON-200{sprint_num}{assignment_count}"
                agents[matching_agent]["current_tasks"].append(story_id)

                agent_assignments[story_id] = {
                    "agent": matching_agent,
                    "sprint": sprint_num,
                    "phase": "R0_RECEIVE"
                }

                print(f"   ✅ {agent_type:30s} → {matching_agent:30s} | Story: {story_id}")
                assignment_count += 1

        print(f"\n✅ Assigned {assignment_count} agents to Sprint {sprint_num}")

        # Update and save state
        state["agents"] = agents
        state["task_assignments"] = agent_assignments
        self.save_state(state)

    def execute_parallel_sprints(self, sprint_numbers: List[int]):
        """
        Execute multiple sprints in parallel.
        Assigns tasks and simulates agent work.
        """
        print("\n" + "=" * 80)
        print("🚀 STARTING PARALLEL SPRINT EXECUTION")
        print("=" * 80)

        for sprint_num in sprint_numbers:
            self.assign_sprint_tasks(sprint_num)
            time.sleep(0.5)

        # Start progress simulation
        self._simulate_progress(sprint_numbers)

    def _simulate_progress(self, sprint_numbers: List[int]):
        """Simulate agent progress through Ralph Loop"""
        ralph_phases = [
            "R0_RECEIVE",
            "R1_UNDERSTAND",
            "R2_RED",
            "R3_GREEN",
            "R4_REFACTOR",
            "R5_CREATE_PR",
            "R6_MERGE",
            "R7_COMPLETE"
        ]

        print("\n" + "=" * 80)
        print("⏳ SIMULATING AGENT EXECUTION (Ralph Loop R0-R7)")
        print("=" * 80)

        # Simulate 60 iterations (300 seconds with 5-second updates)
        for iteration in range(60):
            state = self.load_state()
            if not state:
                break

            agents = state.get("agents", {})
            assignments = state.get("task_assignments", {})

            # Update agents through phases
            for agent_id, agent_data in agents.items():
                current_tasks = agent_data.get("current_tasks", [])

                if current_tasks and agent_data.get("status") != "IDLE":
                    # Transition to IN_PROGRESS
                    if agent_data.get("status") == "ASSIGNED":
                        agent_data["status"] = "IN_PROGRESS"

                    # Advance Ralph phase
                    story_id = current_tasks[0]
                    if story_id in assignments:
                        current_phase = assignments[story_id].get("phase", "R0_RECEIVE")
                        phase_idx = ralph_phases.index(current_phase)

                        # Progress through phases
                        if phase_idx < len(ralph_phases) - 1:
                            # Move to next phase
                            assignments[story_id]["phase"] = ralph_phases[phase_idx + 1]

                            # Update utilization
                            progress = (phase_idx + 1) / len(ralph_phases)
                            agent_data["utilization"] = progress * 100

                            # Simulate task completion
                            if phase_idx >= len(ralph_phases) - 2:
                                # Task complete - return to IDLE
                                agent_data["status"] = "IDLE"
                                agent_data["utilization"] = 0
                                agent_data["current_tasks"] = []
                                agent_data["completed_tasks"].append(story_id)
                                assignments[story_id]["status"] = "COMPLETED"

            # Update state
            state["agents"] = agents
            state["task_assignments"] = assignments
            state["iteration"] = iteration
            state["timestamp"] = datetime.now().isoformat()
            self.save_state(state)

            # Print progress every 12 iterations (60 seconds)
            if iteration % 12 == 0:
                completed = sum(
                    1 for s in assignments.values()
                    if s.get("status") == "COMPLETED"
                )
                in_progress = sum(
                    1 for a in agents.values()
                    if a.get("status") == "IN_PROGRESS"
                )
                total_util = sum(
                    a.get("utilization", 0) for a in agents.values()
                )
                avg_util = total_util / len(agents) if agents else 0

                elapsed_minutes = (iteration * 5) / 60
                print(
                    f"⏱️  {elapsed_minutes:6.1f}m | "
                    f"Completed: {completed:2d} | "
                    f"Working: {in_progress:2d} | "
                    f"Avg Util: {avg_util:5.1f}%"
                )

            time.sleep(5)

        print("\n" + "=" * 80)
        print("✅ SPRINT EXECUTION SIMULATION COMPLETE")
        print("=" * 80)


def main():
    """Main entry point"""
    import sys

    assigner = TaskAssigner()

    if len(sys.argv) > 1:
        if sys.argv[1] == "assign-sprint":
            sprint = int(sys.argv[2]) if len(sys.argv) > 2 else 1
            assigner.assign_sprint_tasks(sprint)

        elif sys.argv[1] == "parallel-execute":
            sprint_nums = [int(x) for x in sys.argv[2:]]
            assigner.execute_parallel_sprints(sprint_nums)

    else:
        # Default: Start Sprints 1 and 2 in parallel
        print("\n🚀 Starting default parallel sprint execution (Sprint 1 & 2)")
        assigner.execute_parallel_sprints([1, 2])


if __name__ == "__main__":
    main()
