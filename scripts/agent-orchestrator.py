#!/usr/bin/env python3
"""
Agent Orchestrator - Master coordinator for 26 autonomous agents

Manages:
- Agent registry (26 agents with specializations)
- Jira story assignment and tracking
- Agent state transitions
- Dependency resolution
- Blocker detection and escalation
- Parallel task execution
- Real-time utilization monitoring
"""

import json
import logging
import time
from dataclasses import dataclass, asdict, field
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, List
from enum import Enum
import subprocess
from collections import defaultdict


class AgentType(Enum):
    """Agent specialization types"""
    # Governance (4)
    GOVERNANCE_ARCHITECT = "Governance_Architect"
    GOVERNANCE_ENFORCER = "Governance_Enforcer"
    GOVERNANCE_COMPLIANCE = "Governance_Compliance"
    GOVERNANCE_SECURITY = "Governance_Security"

    # Backend (6)
    BACKEND_FASTAPI = "Backend_FastAPI"
    BACKEND_DATABASE = "Backend_Database"
    BACKEND_CACHE = "Backend_Cache"
    BACKEND_QUEUE = "Backend_Queue"
    BACKEND_SEARCH = "Backend_Search"
    BACKEND_SECURITY = "Backend_Security"

    # Frontend (4)
    FRONTEND_REACT = "Frontend_React"
    FRONTEND_UX = "Frontend_UX"
    FRONTEND_PERFORMANCE = "Frontend_Performance"
    FRONTEND_TESTING = "Frontend_Testing"

    # QA (5)
    QA_UNIT = "QA_Unit"
    QA_INTEGRATION = "QA_Integration"
    QA_E2E = "QA_E2E"
    QA_PERFORMANCE = "QA_Performance"
    QA_SECURITY = "QA_Security"

    # DevOps (3)
    DEVOPS_CICD = "DevOps_CICD"
    DEVOPS_INFRASTRUCTURE = "DevOps_Infrastructure"
    DEVOPS_MONITORING = "DevOps_Monitoring"

    # Architecture (2)
    ARCHITECTURE_DESIGN = "Architecture_Design"
    ARCHITECTURE_ANALYSIS = "Architecture_Analysis"

    # Support (2)
    SUPPORT_DOCUMENTATION = "Support_Documentation"
    SUPPORT_INTEGRATION = "Support_Integration"


class AgentStatus(Enum):
    """Agent status states"""
    IDLE = "IDLE"
    ASSIGNED = "ASSIGNED"
    IN_PROGRESS = "IN_PROGRESS"
    BLOCKED = "BLOCKED"
    REVIEWING = "REVIEWING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


@dataclass
class Agent:
    """Agent configuration and state"""
    agent_id: str
    agent_type: AgentType
    max_parallel_tasks: int = 2
    status: AgentStatus = AgentStatus.IDLE
    current_tasks: List[str] = field(default_factory=list)
    completed_tasks: List[str] = field(default_factory=list)
    failed_tasks: List[str] = field(default_factory=list)
    total_task_time: float = 0.0
    last_heartbeat: str = ""
    health_status: str = "healthy"

    def is_available(self) -> bool:
        """Check if agent can accept new tasks"""
        return (
            self.status in [AgentStatus.IDLE, AgentStatus.REVIEWING]
            and len(self.current_tasks) < self.max_parallel_tasks
            and self.health_status == "healthy"
        )

    def utilization(self) -> float:
        """Get agent utilization percentage"""
        if self.max_parallel_tasks == 0:
            return 0.0
        return (len(self.current_tasks) / self.max_parallel_tasks) * 100

    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        data = asdict(self)
        data['agent_type'] = self.agent_type.value
        data['status'] = self.status.value
        return data


class AgentOrchestrator:
    """Master orchestrator for all 26 agents"""

    def __init__(self, config_path: str = "/.claude/config/agent-config.json"):
        self.config_path = Path(config_path)
        self.agents: Dict[str, Agent] = {}
        self.task_assignments: Dict[str, str] = {}  # story_id -> agent_id
        self.blockers: List[Dict] = []
        self.logger = self._setup_logging()

        self._initialize_agents()

    def _setup_logging(self) -> logging.Logger:
        """Setup logging for orchestrator"""
        log_dir = Path("/.claude/orchestrator/logs")
        log_dir.mkdir(parents=True, exist_ok=True)

        logger = logging.getLogger("orchestrator")
        handler = logging.FileHandler(log_dir / f"orchestrator_{int(time.time())}.log")
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
        return logger

    def _initialize_agents(self):
        """Initialize all 26 agents"""
        agent_definitions = [
            # Governance (4)
            ("Governance_Architect_01", AgentType.GOVERNANCE_ARCHITECT),
            ("Governance_Enforcer_01", AgentType.GOVERNANCE_ENFORCER),
            ("Governance_Compliance_01", AgentType.GOVERNANCE_COMPLIANCE),
            ("Governance_Security_01", AgentType.GOVERNANCE_SECURITY),

            # Backend (6)
            ("Backend_FastAPI_01", AgentType.BACKEND_FASTAPI),
            ("Backend_FastAPI_02", AgentType.BACKEND_FASTAPI),
            ("Backend_Database_01", AgentType.BACKEND_DATABASE),
            ("Backend_Cache_01", AgentType.BACKEND_CACHE),
            ("Backend_Queue_01", AgentType.BACKEND_QUEUE),
            ("Backend_Search_01", AgentType.BACKEND_SEARCH),

            # Frontend (4)
            ("Frontend_React_01", AgentType.FRONTEND_REACT),
            ("Frontend_React_02", AgentType.FRONTEND_REACT),
            ("Frontend_UX_01", AgentType.FRONTEND_UX),
            ("Frontend_Performance_01", AgentType.FRONTEND_PERFORMANCE),

            # QA (5)
            ("QA_Unit_01", AgentType.QA_UNIT),
            ("QA_Integration_01", AgentType.QA_INTEGRATION),
            ("QA_E2E_01", AgentType.QA_E2E),
            ("QA_Performance_01", AgentType.QA_PERFORMANCE),
            ("QA_Security_01", AgentType.QA_SECURITY),

            # DevOps (3)
            ("DevOps_CICD_01", AgentType.DEVOPS_CICD),
            ("DevOps_Infrastructure_01", AgentType.DEVOPS_INFRASTRUCTURE),
            ("DevOps_Monitoring_01", AgentType.DEVOPS_MONITORING),

            # Architecture (2)
            ("Architecture_Design_01", AgentType.ARCHITECTURE_DESIGN),
            ("Architecture_Analysis_01", AgentType.ARCHITECTURE_ANALYSIS),

            # Support (2)
            ("Support_Documentation_01", AgentType.SUPPORT_DOCUMENTATION),
            ("Support_Integration_01", AgentType.SUPPORT_INTEGRATION),
        ]

        for agent_id, agent_type in agent_definitions:
            self.agents[agent_id] = Agent(
                agent_id=agent_id,
                agent_type=agent_type,
                max_parallel_tasks=2,
                last_heartbeat=datetime.now().isoformat()
            )

        self.logger.info(f"Initialized {len(self.agents)} agents")

    def assign_story(self, story_id: str, story_points: int, required_agents: List[str]) -> Dict:
        """
        Assign a Jira story to appropriate agents.
        Returns assignment plan with timeline.
        """
        self.logger.info(f"Assigning story {story_id} ({story_points}pts) to {len(required_agents)} agents")

        assignments = {}
        timeline = []

        for agent_spec in required_agents:
            agent = self._find_best_agent(agent_spec)
            if agent:
                agent.current_tasks.append(story_id)
                agent.status = AgentStatus.ASSIGNED
                assignments[agent_spec] = agent.agent_id
                timeline.append({
                    "phase": agent_spec,
                    "agent": agent.agent_id,
                    "sequence": len(timeline) + 1
                })
                self.logger.info(f"Assigned {agent_spec} -> {agent.agent_id}")
            else:
                self.logger.warning(f"No available agent for {agent_spec}")

        self.task_assignments[story_id] = assignments
        return {
            "story_id": story_id,
            "assignments": assignments,
            "timeline": timeline,
            "estimated_duration_hours": (story_points / 5) * 2  # Rough estimate
        }

    def _find_best_agent(self, agent_spec: str) -> Optional[Agent]:
        """
        Find the best available agent matching specification.
        Considers: availability, utilization, health, experience.
        """
        candidates = []

        for agent_id, agent in self.agents.items():
            if agent_spec.split('_')[0] not in agent_id:
                continue

            if agent.is_available():
                candidates.append((agent_id, agent))

        if not candidates:
            return None

        # Sort by utilization (prefer less busy agents)
        candidates.sort(key=lambda x: x[1].utilization())
        return candidates[0][1]

    def handle_blocker(self, story_id: str, blocker_reason: str, blocking_stories: List[str]) -> Dict:
        """
        Handle task blocker with escalation path.
        Escalation: Peer agents (3 attempts) → Architect → Human
        """
        self.logger.warning(f"Blocker detected on {story_id}: {blocker_reason}")

        agent_id = next(
            (aid for sid, aid in self.task_assignments.items() if sid == story_id),
            None
        )
        if agent_id:
            agent = self.agents.get(agent_id)
            if agent:
                agent.status = AgentStatus.BLOCKED

        blocker = {
            "story_id": story_id,
            "reason": blocker_reason,
            "blocking_stories": blocking_stories,
            "detected_at": datetime.now().isoformat(),
            "escalation_path": [
                {"level": 1, "action": "notify_peer_agents", "agents": self._get_peer_agents(agent_id)},
                {"level": 2, "action": "escalate_to_architect", "agent": "Architecture_Design_01"},
                {"level": 3, "action": "escalate_to_human", "alert": "CRITICAL"}
            ]
        }

        self.blockers.append(blocker)
        return blocker

    def get_agent_status(self, agent_id: Optional[str] = None) -> Dict:
        """Get current status of agents"""
        if agent_id:
            agent = self.agents.get(agent_id)
            if agent:
                return agent.to_dict()
            return {"error": f"Agent {agent_id} not found"}

        # Return all agents status
        summary = {
            "total_agents": len(self.agents),
            "timestamp": datetime.now().isoformat(),
            "agents": {},
            "utilization": {}
        }

        total_util = 0
        for aid, agent in self.agents.items():
            summary["agents"][aid] = agent.to_dict()
            util = agent.utilization()
            summary["utilization"][aid] = util
            total_util += util

        summary["average_utilization"] = total_util / len(self.agents) if self.agents else 0
        return summary

    def _get_peer_agents(self, agent_id: str) -> List[str]:
        """Get peer agents of same type"""
        if not agent_id:
            return []

        agent = self.agents.get(agent_id)
        if not agent:
            return []

        peers = []
        for aid, other in self.agents.items():
            if aid != agent_id and other.agent_type == agent.agent_type:
                peers.append(aid)

        return peers[:3]  # Return up to 3 peers

    def generate_assignment_report(self) -> str:
        """Generate human-readable assignment report"""
        report = "=" * 60 + "\n"
        report += "AGENT ASSIGNMENT REPORT\n"
        report += "=" * 60 + "\n\n"

        report += f"Timestamp: {datetime.now().isoformat()}\n\n"

        # Utilization
        report += "UTILIZATION SUMMARY\n"
        report += "-" * 40 + "\n"
        for aid, agent in sorted(self.agents.items()):
            util = agent.utilization()
            bar = "█" * int(util / 5) + "░" * (20 - int(util / 5))
            report += f"{aid:30s} [{bar}] {util:5.1f}%\n"

        report += "\n"

        # Tasks
        report += "CURRENT ASSIGNMENTS\n"
        report += "-" * 40 + "\n"
        for story_id, assignments in self.task_assignments.items():
            report += f"{story_id}:\n"
            for phase, agent_id in assignments.items():
                report += f"  └─ {phase:25s} -> {agent_id}\n"

        report += "\n"

        # Blockers
        if self.blockers:
            report += "ACTIVE BLOCKERS\n"
            report += "-" * 40 + "\n"
            for blocker in self.blockers:
                report += f"Story: {blocker['story_id']}\n"
                report += f"Reason: {blocker['reason']}\n"
                report += f"Blocking: {', '.join(blocker['blocking_stories'])}\n\n"

        return report

    def save_state(self, output_path: str = "/.claude/orchestrator/state.json"):
        """Save orchestrator state for recovery"""
        state = {
            "timestamp": datetime.now().isoformat(),
            "agents": {aid: agent.to_dict() for aid, agent in self.agents.items()},
            "task_assignments": self.task_assignments,
            "blockers": self.blockers
        }

        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        Path(output_path).write_text(json.dumps(state, indent=2))
        self.logger.info(f"State saved to {output_path}")


def main():
    """Main entry point"""
    import sys

    orchestrator = AgentOrchestrator()

    if len(sys.argv) > 1:
        if sys.argv[1] == "--status":
            status = orchestrator.get_agent_status(sys.argv[2] if len(sys.argv) > 2 else None)
            print(json.dumps(status, indent=2))

        elif sys.argv[1] == "--assign":
            result = orchestrator.assign_story(
                story_id=sys.argv[2],
                story_points=int(sys.argv[3]),
                required_agents=sys.argv[4:]
            )
            print(json.dumps(result, indent=2))

        elif sys.argv[1] == "--report":
            print(orchestrator.generate_assignment_report())

        elif sys.argv[1] == "--save-state":
            orchestrator.save_state()
            print("State saved")

    else:
        # Daemon mode
        print("Orchestrator running in daemon mode (ctrl+c to stop)")
        try:
            while True:
                orchestrator.save_state()
                time.sleep(300)  # Save state every 5 minutes
        except KeyboardInterrupt:
            print("\nOrchestrator stopped")


if __name__ == "__main__":
    main()
