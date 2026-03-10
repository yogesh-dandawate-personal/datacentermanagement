#!/usr/bin/env python3
"""
Sprint Queue Manager - Autonomous Sprint Execution System

Manages a queue of all project sprints (1-13) and executes them through
Ralph Loop phases (R0-R7) with parallel execution of 2 sprints at a time.

Features:
- Central task dispatcher for all sprints
- Parallel execution with intelligent scheduling
- Agent Team assignment and routing
- Ralph Loop phase progression (R0-R7)
- Autonomous failure recovery
- Real-time progress tracking
- Status reporting and notifications
"""

import json
import time
import logging
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from enum import Enum
from dataclasses import dataclass, asdict
import threading
from queue import PriorityQueue
import uuid

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('.claude/logs/sprint-queue.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)


class RalphPhase(Enum):
    """Ralph Loop phases for sprint execution"""
    R0_CONTEXT = 0  # Understand requirements
    R1_ANALYSIS = 1  # Analyze scope and complexity
    R2_PLANNING = 2  # Create implementation plan
    R3_SETUP = 3  # Setup project structure
    R4_DEVELOPMENT = 4  # Core development
    R5_INTEGRATION = 5  # Component integration
    R6_TESTING = 6  # Testing and validation
    R7_DEPLOYMENT = 7  # Deployment and cleanup


class SprintStatus(Enum):
    """Sprint execution status"""
    PENDING = "pending"
    QUEUED = "queued"
    IN_PROGRESS = "in_progress"
    BLOCKED = "blocked"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class SprintTask:
    """Sprint task definition"""
    sprint_id: int
    title: str
    description: str
    story_points: int
    agent_team_id: str
    priority: int = 1
    dependencies: List[int] = None
    ralph_phase: RalphPhase = RalphPhase.R0_CONTEXT
    status: SprintStatus = SprintStatus.PENDING
    created_at: str = None
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    error_message: Optional[str] = None
    retry_count: int = 0
    max_retries: int = 3

    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.utcnow().isoformat()
        if self.dependencies is None:
            self.dependencies = []

    def __lt__(self, other):
        """For priority queue comparison"""
        return self.priority < other.priority


class SprintQueueManager:
    """Main sprint queue manager with autonomous execution"""

    def __init__(self, config_path: str = '.claude/config/sprint-queue-config.json'):
        """Initialize the sprint queue manager"""
        self.config_path = config_path
        self.config = self._load_config()

        # Sprint registry
        self.sprints: Dict[int, SprintTask] = {}
        self.queue: PriorityQueue = PriorityQueue()

        # Execution tracking
        self.running_sprints: Dict[int, SprintTask] = {}
        self.completed_sprints: List[SprintTask] = []
        self.failed_sprints: List[SprintTask] = []

        # Execution state
        self.max_concurrent = self.config.get('max_concurrent_sprints', 2)
        self.ralph_phases = list(RalphPhase)
        self.is_running = False

        # Agent teams
        self.agent_teams = self.config.get('agent_teams', {})

        logger.info(f"Sprint Queue Manager initialized with max concurrent: {self.max_concurrent}")

    def _load_config(self) -> Dict:
        """Load configuration from file"""
        try:
            with open(self.config_path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            logger.warning(f"Config file not found at {self.config_path}, using defaults")
            return {
                'max_concurrent_sprints': 2,
                'ralph_loop_enabled': True,
                'auto_recovery_enabled': True,
                'phase_timeout_minutes': 480,  # 8 hours per phase
                'agent_teams': self._create_default_agent_teams()
            }

    def _create_default_agent_teams(self) -> Dict:
        """Create default agent teams for sprints"""
        return {
            f'team-{i}': {
                'name': f'Sprint {i} Team',
                'agents': [f'agent-{i}-1', f'agent-{i}-2', f'agent-{i}-3'],
                'leader': f'leader-{i}'
            }
            for i in range(1, 14)
        }

    def register_sprint(
        self,
        sprint_id: int,
        title: str,
        description: str,
        story_points: int,
        dependencies: Optional[List[int]] = None
    ) -> SprintTask:
        """Register a new sprint in the queue"""
        agent_team_id = f'team-{sprint_id}'

        task = SprintTask(
            sprint_id=sprint_id,
            title=title,
            description=description,
            story_points=story_points,
            agent_team_id=agent_team_id,
            priority=sprint_id,
            dependencies=dependencies or []
        )

        self.sprints[sprint_id] = task
        self.queue.put((sprint_id, task))

        logger.info(f"Sprint {sprint_id} registered: {title}")
        return task

    def register_all_sprints(self) -> List[SprintTask]:
        """Register all 13 project sprints"""
        sprints_config = [
            (1, "Vercel Migration & Setup", "Fix Vercel deployment and environment setup", 13),
            (2, "Telemetry System", "Real-time energy telemetry collection", 21),
            (3, "Energy Dashboards", "Create energy monitoring dashboards", 18),
            (4, "Carbon Accounting", "CO2 emissions calculation system", 21),
            (5, "Energy Metrics", "Advanced energy metrics and analysis", 16),
            (6, "Carbon Calculations", "Scope 1/2/3 carbon calculations", 20),
            (7, "KPI Engine", "Performance metrics and KPI tracking", 18),
            (8, "Marketplace & Trading", "Carbon credit marketplace", 24),
            (9, "Advanced Analytics", "Deep analytics and reporting", 22),
            (10, "Emissions Module", "Comprehensive emissions tracking", 26),
            (11, "Compliance Dashboard", "Regulatory compliance tracking", 20),
            (12, "Integration & APIs", "Third-party integrations", 18),
            (13, "Copilot & Automation", "AI copilot and workflow automation", 24),
        ]

        registered = []
        for sprint_id, title, description, story_points in sprints_config:
            # Determine dependencies
            dependencies = []
            if sprint_id > 1:
                # Most sprints depend on previous setup sprints
                if sprint_id <= 4:
                    dependencies = [i for i in range(1, sprint_id)]
                elif sprint_id <= 7:
                    dependencies = [i for i in range(1, 5)]  # Depend on first 4 sprints
                else:
                    dependencies = [i for i in range(1, 8)]  # Depend on first 7 sprints

            task = self.register_sprint(
                sprint_id=sprint_id,
                title=title,
                description=description,
                story_points=story_points,
                dependencies=dependencies
            )
            registered.append(task)

        logger.info(f"Registered all {len(registered)} sprints")
        return registered

    def check_dependencies(self, sprint_id: int) -> bool:
        """Check if all sprint dependencies are completed"""
        sprint = self.sprints.get(sprint_id)
        if not sprint or not sprint.dependencies:
            return True

        for dep_id in sprint.dependencies:
            dep_sprint = self.sprints.get(dep_id)
            if not dep_sprint or dep_sprint.status != SprintStatus.COMPLETED:
                return False

        return True

    def get_ready_sprints(self) -> List[int]:
        """Get sprints ready to execute (dependencies satisfied, not running)"""
        ready = []

        for sprint_id, sprint in self.sprints.items():
            if (sprint.status == SprintStatus.PENDING and
                self.check_dependencies(sprint_id)):
                ready.append(sprint_id)

        return sorted(ready)

    def assign_agents_to_sprint(self, sprint_id: int) -> Dict:
        """Assign agent team to sprint execution"""
        agent_team_id = f'team-{sprint_id}'
        team_info = self.agent_teams.get(agent_team_id, {})

        assignment = {
            'sprint_id': sprint_id,
            'team_id': agent_team_id,
            'agents': team_info.get('agents', []),
            'leader': team_info.get('leader', f'leader-{sprint_id}'),
            'assigned_at': datetime.utcnow().isoformat()
        }

        logger.info(f"Assigned {agent_team_id} to Sprint {sprint_id}")
        return assignment

    def execute_ralph_phase(
        self,
        sprint_id: int,
        phase: RalphPhase
    ) -> Tuple[bool, Optional[str]]:
        """Execute a Ralph Loop phase for a sprint"""
        sprint = self.sprints.get(sprint_id)
        if not sprint:
            return False, f"Sprint {sprint_id} not found"

        logger.info(f"Executing Sprint {sprint_id} - Phase {phase.name}")

        try:
            # Simulate phase execution
            # In real implementation, this would trigger agent tasks
            phase_config = {
                RalphPhase.R0_CONTEXT: {'duration': 30, 'task': 'Gather requirements'},
                RalphPhase.R1_ANALYSIS: {'duration': 45, 'task': 'Analyze scope'},
                RalphPhase.R2_PLANNING: {'duration': 60, 'task': 'Create plan'},
                RalphPhase.R3_SETUP: {'duration': 45, 'task': 'Setup infrastructure'},
                RalphPhase.R4_DEVELOPMENT: {'duration': 480, 'task': 'Develop features'},
                RalphPhase.R5_INTEGRATION: {'duration': 240, 'task': 'Integrate components'},
                RalphPhase.R6_TESTING: {'duration': 180, 'task': 'Test and validate'},
                RalphPhase.R7_DEPLOYMENT: {'duration': 120, 'task': 'Deploy and cleanup'},
            }

            config = phase_config.get(phase, {})
            logger.info(f"  Task: {config.get('task', 'Unknown')}")
            logger.info(f"  Est. Duration: {config.get('duration', 'N/A')} minutes")

            # Update sprint phase
            sprint.ralph_phase = phase

            return True, None

        except Exception as e:
            error_msg = f"Phase {phase.name} failed: {str(e)}"
            logger.error(error_msg)
            return False, error_msg

    def advance_sprint_phase(self, sprint_id: int) -> bool:
        """Advance sprint to next Ralph phase"""
        sprint = self.sprints.get(sprint_id)
        if not sprint:
            return False

        current_phase_idx = sprint.ralph_phase.value
        if current_phase_idx < len(self.ralph_phases) - 1:
            next_phase = self.ralph_phases[current_phase_idx + 1]
            success, error = self.execute_ralph_phase(sprint_id, next_phase)

            if success:
                sprint.ralph_phase = next_phase
                logger.info(f"Sprint {sprint_id} advanced to {next_phase.name}")
                return True
            else:
                logger.error(f"Failed to advance Sprint {sprint_id}: {error}")
                sprint.status = SprintStatus.BLOCKED
                return False
        else:
            # All phases complete
            sprint.status = SprintStatus.COMPLETED
            sprint.completed_at = datetime.utcnow().isoformat()
            self.completed_sprints.append(sprint)
            logger.info(f"Sprint {sprint_id} completed all phases")
            return True

    def start_sprint_execution(self, sprint_id: int) -> bool:
        """Start execution of a sprint"""
        sprint = self.sprints.get(sprint_id)
        if not sprint:
            return False

        if len(self.running_sprints) >= self.max_concurrent:
            logger.warning(f"Cannot start Sprint {sprint_id}: max concurrent limit reached")
            return False

        # Assign agents
        assignment = self.assign_agents_to_sprint(sprint_id)

        # Mark as running
        sprint.status = SprintStatus.IN_PROGRESS
        sprint.started_at = datetime.utcnow().isoformat()
        self.running_sprints[sprint_id] = sprint

        logger.info(f"Started execution of Sprint {sprint_id}")
        return True

    def handle_sprint_failure(self, sprint_id: int, error: str) -> bool:
        """Handle sprint execution failure with retry logic"""
        sprint = self.sprints.get(sprint_id)
        if not sprint:
            return False

        sprint.retry_count += 1
        sprint.error_message = error

        if sprint.retry_count < sprint.max_retries:
            logger.info(f"Sprint {sprint_id} failed, retrying ({sprint.retry_count}/{sprint.max_retries})")
            sprint.status = SprintStatus.QUEUED
            self.queue.put((sprint.priority, sprint))
            return True
        else:
            logger.error(f"Sprint {sprint_id} failed permanently after {sprint.max_retries} retries")
            sprint.status = SprintStatus.FAILED
            self.failed_sprints.append(sprint)

            if sprint_id in self.running_sprints:
                del self.running_sprints[sprint_id]

            return False

    def get_status_summary(self) -> Dict:
        """Get overall execution status summary"""
        total = len(self.sprints)
        completed = len(self.completed_sprints)
        running = len(self.running_sprints)
        pending = len([s for s in self.sprints.values() if s.status == SprintStatus.PENDING])
        failed = len(self.failed_sprints)

        total_story_points = sum(s.story_points for s in self.sprints.values())
        completed_story_points = sum(s.story_points for s in self.completed_sprints)

        return {
            'total_sprints': total,
            'completed': completed,
            'running': running,
            'pending': pending,
            'failed': failed,
            'completion_percentage': (completed / total * 100) if total > 0 else 0,
            'total_story_points': total_story_points,
            'completed_story_points': completed_story_points,
            'story_point_completion': (completed_story_points / total_story_points * 100) if total_story_points > 0 else 0,
            'timestamp': datetime.utcnow().isoformat()
        }

    def run_autonomous_loop(self, duration_minutes: int = 0) -> None:
        """Run autonomous sprint execution loop"""
        self.is_running = True
        start_time = time.time()
        duration_seconds = duration_minutes * 60 if duration_minutes > 0 else float('inf')

        logger.info("Starting autonomous sprint execution loop")

        try:
            while self.is_running:
                elapsed_seconds = time.time() - start_time

                if elapsed_seconds > duration_seconds:
                    logger.info("Duration limit reached, stopping execution")
                    break

                # Get sprints ready to execute
                ready_sprints = self.get_ready_sprints()

                # Start sprints up to concurrent limit
                for sprint_id in ready_sprints[:self.max_concurrent - len(self.running_sprints)]:
                    self.start_sprint_execution(sprint_id)

                # Advance running sprints through phases
                completed_ids = []
                for sprint_id, sprint in list(self.running_sprints.items()):
                    if not self.advance_sprint_phase(sprint_id):
                        if sprint.status == SprintStatus.FAILED:
                            completed_ids.append(sprint_id)

                # Remove completed sprints from running
                for sprint_id in completed_ids:
                    if sprint_id in self.running_sprints:
                        del self.running_sprints[sprint_id]

                # Log status
                status = self.get_status_summary()
                logger.info(
                    f"Status: {status['completed']}/{status['total']} complete | "
                    f"Running: {status['running']} | "
                    f"Progress: {status['completion_percentage']:.1f}%"
                )

                # Sleep before next iteration
                time.sleep(5)

        except KeyboardInterrupt:
            logger.info("Execution interrupted by user")
        finally:
            self.is_running = False
            logger.info("Autonomous execution loop stopped")

    def save_state(self, filepath: str = '.claude/state/sprint-queue-state.json') -> None:
        """Save execution state to file"""
        state = {
            'timestamp': datetime.utcnow().isoformat(),
            'sprints': {
                str(sid): {
                    'sprint_id': s.sprint_id,
                    'title': s.title,
                    'status': s.status.value,
                    'ralph_phase': s.ralph_phase.name,
                    'story_points': s.story_points,
                    'started_at': s.started_at,
                    'completed_at': s.completed_at,
                    'error_message': s.error_message,
                    'retry_count': s.retry_count
                }
                for sid, s in self.sprints.items()
            },
            'summary': self.get_status_summary()
        }

        with open(filepath, 'w') as f:
            json.dump(state, f, indent=2)

        logger.info(f"State saved to {filepath}")

    def generate_report(self) -> str:
        """Generate execution report"""
        status = self.get_status_summary()

        report = f"""
╔══════════════════════════════════════════════════════════════╗
║          SPRINT QUEUE EXECUTION REPORT                       ║
║          Generated: {datetime.utcnow().isoformat()}           ║
╚══════════════════════════════════════════════════════════════╝

OVERALL PROGRESS
  Total Sprints: {status['total_sprints']}
  Completed: {status['completed']}
  Running: {status['running']}
  Pending: {status['pending']}
  Failed: {status['failed']}
  Progress: {status['completion_percentage']:.1f}%

STORY POINTS
  Total: {status['total_story_points']} points
  Completed: {status['completed_story_points']} points
  Progress: {status['story_point_completion']:.1f}%

SPRINT DETAILS
"""
        for sprint_id in sorted(self.sprints.keys()):
            sprint = self.sprints[sprint_id]
            report += f"""
  Sprint {sprint_id}: {sprint.title}
    Status: {sprint.status.value}
    Phase: {sprint.ralph_phase.name}
    Story Points: {sprint.story_points}
    Started: {sprint.started_at or 'Not started'}
    Completed: {sprint.completed_at or 'In progress'}
"""

        return report


def main():
    """Main execution function"""
    manager = SprintQueueManager()

    # Register all sprints
    manager.register_all_sprints()

    # Start autonomous execution
    logger.info("=" * 60)
    logger.info("AUTONOMOUS SPRINT QUEUE SYSTEM STARTING")
    logger.info("=" * 60)

    # Run for extended duration (48 hours = 2880 minutes)
    manager.run_autonomous_loop(duration_minutes=2880)

    # Save final state
    manager.save_state()

    # Generate and print report
    print(manager.generate_report())


if __name__ == '__main__':
    main()
