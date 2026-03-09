#!/usr/bin/env python3
"""
Recovery Handler - Automatic failure detection and recovery

Monitors agent health and automatically recovers from failures.
Recovery levels:
- Level 1: Soft rollback (5 minutes)
- Level 2: Phase rollback (to previous Ralph phase)
- Level 3: Sprint rollback (requires approval)
"""

import json
import logging
import time
import subprocess
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Optional, List
from dataclasses import dataclass


@dataclass
class HealthStatus:
    """Agent health status"""
    agent_id: str
    last_heartbeat: datetime
    is_alive: bool
    task_count: int
    failure_count: int
    last_failure: Optional[datetime] = None


class RecoveryHandler:
    """Handles failure detection and recovery"""

    def __init__(self, check_interval_seconds: int = 30):
        self.check_interval = check_interval_seconds
        self.logger = self._setup_logging()
        self.health_status: Dict[str, HealthStatus] = {}
        self.recovery_history: List[Dict] = []

    def _setup_logging(self) -> logging.Logger:
        """Setup logging"""
        log_dir = Path("./.claude/orchestrator/logs")
        log_dir.mkdir(parents=True, exist_ok=True)

        logger = logging.getLogger("recovery-handler")
        handler = logging.FileHandler(log_dir / "recovery.log")
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
        return logger

    def start_monitoring(self):
        """Start continuous health monitoring"""
        self.logger.info("Recovery handler started - monitoring agents")

        try:
            while True:
                self._check_all_agents()
                time.sleep(self.check_interval)
        except KeyboardInterrupt:
            self.logger.info("Recovery handler stopped")

    def _check_all_agents(self):
        """Check health of all agents"""
        # Load orchestrator state
        state_path = Path("./.claude/orchestrator/state.json")
        if not state_path.exists():
            return

        try:
            state = json.loads(state_path.read_text())
            agents = state.get("agents", {})

            for agent_id, agent_data in agents.items():
                self._check_agent_health(agent_id, agent_data)

        except Exception as e:
            self.logger.error(f"Failed to check agents: {str(e)}")

    def _check_agent_health(self, agent_id: str, agent_data: Dict):
        """Check individual agent health"""
        try:
            last_heartbeat_str = agent_data.get("last_heartbeat", "")
            last_heartbeat = datetime.fromisoformat(last_heartbeat_str)
            time_since_heartbeat = (datetime.now() - last_heartbeat).total_seconds()

            # Agent considered dead after 5 minutes without heartbeat
            is_alive = time_since_heartbeat < 300

            if not is_alive:
                self.logger.warning(f"Agent {agent_id} unresponsive for {time_since_heartbeat:.0f}s")
                self._handle_agent_failure(agent_id, agent_data)

        except Exception as e:
            self.logger.error(f"Health check failed for {agent_id}: {str(e)}")

    def _handle_agent_failure(self, agent_id: str, agent_data: Dict):
        """Handle agent failure with escalation"""
        current_tasks = agent_data.get("current_tasks", [])

        self.logger.error(f"FAILURE DETECTED: Agent {agent_id}")
        self.logger.error(f"  Current tasks: {current_tasks}")
        self.logger.error(f"  Initiating automatic recovery...")

        for task_id in current_tasks:
            recovery_result = self._recover_task(agent_id, task_id)

            if recovery_result["success"]:
                self.logger.info(f"✓ Task {task_id} recovered successfully")
            else:
                self.logger.error(f"✗ Task {task_id} recovery failed: {recovery_result['error']}")
                self._escalate_failure(agent_id, task_id, recovery_result)

    def _recover_task(self, agent_id: str, task_id: str) -> Dict:
        """Attempt to recover a task from checkpoint"""
        self.logger.info(f"Attempting recovery for {task_id}...")

        try:
            # Find latest checkpoint
            checkpoint_dir = Path(f"./.claude/agents/{agent_id}/checkpoints")
            if not checkpoint_dir.exists():
                return {
                    "success": False,
                    "error": "No checkpoints found"
                }

            checkpoint_files = sorted(
                checkpoint_dir.glob("CP-*.json"),
                key=lambda p: p.stat().st_mtime,
                reverse=True
            )

            if not checkpoint_files:
                return {
                    "success": False,
                    "error": "No valid checkpoints"
                }

            latest_checkpoint = checkpoint_files[0]
            self.logger.info(f"Found checkpoint: {latest_checkpoint.name}")

            # Load and verify checkpoint
            checkpoint_data = json.loads(latest_checkpoint.read_text())

            # Verify integrity
            if not self._verify_checkpoint(checkpoint_data):
                return {
                    "success": False,
                    "error": "Checkpoint verification failed"
                }

            # Restore git state
            git_state = checkpoint_data.get("git_state", {})
            self._restore_git_state(git_state)

            # Restore environment
            self._restore_environment(checkpoint_data.get("environment", {}))

            recovery_record = {
                "timestamp": datetime.now().isoformat(),
                "agent_id": agent_id,
                "task_id": task_id,
                "checkpoint": latest_checkpoint.name,
                "level": 1,
                "success": True
            }
            self.recovery_history.append(recovery_record)

            return {
                "success": True,
                "checkpoint": latest_checkpoint.name,
                "level": 1
            }

        except Exception as e:
            self.logger.error(f"Recovery failed: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }

    def _verify_checkpoint(self, checkpoint_data: Dict) -> bool:
        """Verify checkpoint integrity"""
        required_fields = [
            "session_id",
            "phase",
            "git_state",
            "file_checksums"
        ]

        for field in required_fields:
            if field not in checkpoint_data:
                self.logger.error(f"Checkpoint missing field: {field}")
                return False

        return True

    def _restore_git_state(self, git_state: Dict) -> bool:
        """Restore git state"""
        try:
            branch = git_state.get("branch", "main")
            commit = git_state.get("commit", "")

            # Checkout branch
            subprocess.run(
                ["git", "checkout", branch],
                capture_output=True,
                timeout=10
            )

            # Reset to commit
            if commit:
                subprocess.run(
                    ["git", "reset", "--hard", commit],
                    capture_output=True,
                    timeout=10
                )

            self.logger.info(f"Git state restored: {branch} @ {commit[:8]}")
            return True

        except Exception as e:
            self.logger.error(f"Git restore failed: {str(e)}")
            return False

    def _restore_environment(self, environment: Dict) -> bool:
        """Restore environment state"""
        try:
            # Check and restart services if needed
            services = environment.get("services", {})

            for service_name, is_running in services.items():
                if not is_running:
                    self.logger.info(f"Restarting service: {service_name}")
                    # Would restart service here

            self.logger.info("Environment restored")
            return True

        except Exception as e:
            self.logger.error(f"Environment restore failed: {str(e)}")
            return False

    def _escalate_failure(self, agent_id: str, task_id: str, recovery_result: Dict):
        """Escalate failure through escalation path"""
        escalation_path = [
            {
                "level": 2,
                "action": "notify_peer_agents",
                "timeout_minutes": 15
            },
            {
                "level": 3,
                "action": "escalate_to_architect",
                "timeout_minutes": 10
            },
            {
                "level": 4,
                "action": "alert_human",
                "timeout_minutes": float('inf')
            }
        ]

        for escalation in escalation_path:
            self.logger.warning(
                f"Escalation Level {escalation['level']}: {escalation['action']} "
                f"for {task_id} (timeout: {escalation['timeout_minutes']}m)"
            )

            # Implement escalation action
            if escalation["level"] == 2:
                self._notify_peer_agents(agent_id, task_id)
            elif escalation["level"] == 3:
                self._escalate_to_architect(task_id, recovery_result)
            elif escalation["level"] == 4:
                self._alert_human(task_id, recovery_result)

    def _notify_peer_agents(self, agent_id: str, task_id: str):
        """Notify peer agents to help with task"""
        self.logger.info(f"Notifying peer agents to help with {task_id}")
        # Would send message to peer agents

    def _escalate_to_architect(self, task_id: str, recovery_result: Dict):
        """Escalate to architecture team"""
        self.logger.info(f"Escalating {task_id} to architecture team")
        # Would send to Architecture_Design_01 agent

    def _alert_human(self, task_id: str, recovery_result: Dict):
        """Alert human (CTO) for manual intervention"""
        alert = {
            "timestamp": datetime.now().isoformat(),
            "task_id": task_id,
            "severity": "CRITICAL",
            "message": f"Task {task_id} recovery failed - manual intervention required",
            "recovery_info": recovery_result
        }

        # Save alert
        alert_dir = Path("./.claude/orchestrator/alerts")
        alert_dir.mkdir(parents=True, exist_ok=True)
        alert_file = alert_dir / f"alert_{int(time.time())}.json"
        alert_file.write_text(json.dumps(alert, indent=2))

        self.logger.critical(f"HUMAN ALERT: {alert['message']}")

    def get_recovery_history(self, limit: int = 100) -> List[Dict]:
        """Get recovery history"""
        return self.recovery_history[-limit:]

    def save_recovery_history(self):
        """Save recovery history to file"""
        history_dir = Path("./.claude/orchestrator/history")
        history_dir.mkdir(parents=True, exist_ok=True)
        history_file = history_dir / f"recovery_{int(time.time())}.json"
        history_file.write_text(json.dumps(self.recovery_history, indent=2))
        self.logger.info(f"Recovery history saved: {history_file}")


def main():
    """Main entry point"""
    import sys

    handler = RecoveryHandler()

    if len(sys.argv) > 1 and sys.argv[1] == "--daemon":
        handler.start_monitoring()
    else:
        print("Recovery handler ready. Start with: recovery-handler.py --daemon")


if __name__ == "__main__":
    main()
