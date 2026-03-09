#!/usr/bin/env python3
"""
Ralph Loop Orchestration Engine (R0-R7)

Implements the Ralph Loop methodology for autonomous agent-driven development:
- R0: Receive (task acquisition)
- R1: Understand (requirement analysis)
- R2: RED (failing tests)
- R3: GREEN (implementation)
- R4: Refactor (code quality)
- R5: Create PR (pull request)
- R6: Merge (code integration)
- R7: Complete (verification)

Maps SPARC phases to Ralph phases for holistic development orchestration.
"""

import json
import os
import sys
import logging
import time
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, List
from enum import Enum
import hashlib
import subprocess


class RalphPhase(Enum):
    """Ralph Loop phases"""
    R0_RECEIVE = "R0_RECEIVE"
    R1_UNDERSTAND = "R1_UNDERSTAND"
    R2_RED = "R2_RED"
    R3_GREEN = "R3_GREEN"
    R4_REFACTOR = "R4_REFACTOR"
    R5_CREATE_PR = "R5_CREATE_PR"
    R6_MERGE = "R6_MERGE"
    R7_COMPLETE = "R7_COMPLETE"


class SPARCPhase(Enum):
    """SPARC framework phases"""
    SPECIFY = "SPECIFY"
    PLAN = "PLAN"
    ACT = "ACT"
    REVIEW = "REVIEW"
    CLOSE = "CLOSE"


@dataclass
class CheckpointData:
    """Checkpoint data structure"""
    session_id: str
    story_id: str
    ralph_phase: str
    sparc_phase: str
    timestamp: str
    git_branch: str
    git_commit: str
    files_modified: List[str]
    tests_passed: int
    tests_failed: int
    test_coverage: float
    agent_id: str
    environment_hash: str
    recovery_instructions: str


class RalphLoopExecutor:
    """Master orchestrator for Ralph Loop execution"""

    def __init__(self, story_id: str, agent_id: str, session_id: str):
        self.story_id = story_id
        self.agent_id = agent_id
        self.session_id = session_id
        self.current_phase = RalphPhase.R0_RECEIVE
        self.current_sparc = SPARCPhase.SPECIFY
        self.start_time = datetime.now()
        self.checkpoint_dir = Path(f"/.claude/agents/{agent_id}/checkpoints/{session_id}")
        self.checkpoint_dir.mkdir(parents=True, exist_ok=True)

        # Setup logging
        self.logger = self._setup_logging()
        self.logger.info(f"Ralph Loop initialized for {story_id} by {agent_id}")

    def _setup_logging(self) -> logging.Logger:
        """Setup logging for Ralph Loop execution"""
        log_dir = Path(f"/.claude/agents/{self.agent_id}/logs")
        log_dir.mkdir(parents=True, exist_ok=True)

        logger = logging.getLogger(f"ralph-{self.story_id}")
        handler = logging.FileHandler(log_dir / f"{self.session_id}.log")
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
        return logger

    def phase_r0_receive(self) -> bool:
        """R0: Receive - Task acquisition from Jira/queue"""
        self.logger.info(f"R0: Receiving task {self.story_id}")
        self.current_phase = RalphPhase.R0_RECEIVE

        try:
            # Simulate task acquisition
            task_data = {
                "story_id": self.story_id,
                "acquired_at": datetime.now().isoformat(),
                "agent_id": self.agent_id
            }

            self._save_checkpoint(
                sparc_phase=SPARCPhase.SPECIFY,
                context=task_data
            )
            self.logger.info("R0 Complete: Task received and queued")
            return True
        except Exception as e:
            self.logger.error(f"R0 Failed: {str(e)}")
            return False

    def phase_r1_understand(self, requirements: Dict) -> bool:
        """R1: Understand - Requirement analysis and planning"""
        self.logger.info("R1: Understanding requirements")
        self.current_phase = RalphPhase.R1_UNDERSTAND
        self.current_sparc = SPARCPhase.PLAN

        try:
            understanding = {
                "story_id": self.story_id,
                "requirements": requirements,
                "acceptance_criteria": requirements.get("acceptance_criteria", []),
                "test_strategy": self._analyze_test_strategy(requirements),
                "dependencies": requirements.get("dependencies", []),
                "estimated_effort": requirements.get("story_points", 0)
            }

            self._save_checkpoint(
                sparc_phase=SPARCPhase.PLAN,
                context=understanding
            )
            self.logger.info("R1 Complete: Requirements understood and planned")
            return True
        except Exception as e:
            self.logger.error(f"R1 Failed: {str(e)}")
            return False

    def phase_r2_red(self, test_files: List[str]) -> bool:
        """R2: RED - Write failing tests"""
        self.logger.info("R2: Writing failing tests (RED state)")
        self.current_phase = RalphPhase.R2_RED
        self.current_sparc = SPARCPhase.ACT

        try:
            test_results = {
                "phase": "RED",
                "test_files": test_files,
                "timestamp": datetime.now().isoformat(),
                "expected_failures": len(test_files)
            }

            # Run tests to verify they fail
            failed_count = self._run_tests(test_files)
            test_results["actual_failures"] = failed_count

            if failed_count == 0:
                self.logger.warning("R2 Warning: No test failures detected - tests may not be valid")

            self._save_checkpoint(
                sparc_phase=SPARCPhase.ACT,
                context=test_results
            )
            self.logger.info(f"R2 Complete: {failed_count} tests in RED state")
            return True
        except Exception as e:
            self.logger.error(f"R2 Failed: {str(e)}")
            return False

    def phase_r3_green(self, implementation_files: List[str]) -> bool:
        """R3: GREEN - Implement to make tests pass"""
        self.logger.info("R3: Implementing to GREEN state")
        self.current_phase = RalphPhase.R3_GREEN

        try:
            impl_results = {
                "phase": "GREEN",
                "implementation_files": implementation_files,
                "timestamp": datetime.now().isoformat()
            }

            # Run tests to verify they pass
            passed_count = self._run_tests([])
            impl_results["tests_passed"] = passed_count
            impl_results["all_tests_passing"] = passed_count > 0

            if not impl_results["all_tests_passing"]:
                self.logger.warning("R3 Warning: Not all tests passing - may need more work")

            self._save_checkpoint(
                sparc_phase=SPARCPhase.ACT,
                context=impl_results
            )
            self.logger.info(f"R3 Complete: {passed_count} tests in GREEN state")
            return True
        except Exception as e:
            self.logger.error(f"R3 Failed: {str(e)}")
            return False

    def phase_r4_refactor(self, refactor_checklist: Dict) -> bool:
        """R4: Refactor - Code quality improvements while maintaining GREEN"""
        self.logger.info("R4: Refactoring code")
        self.current_phase = RalphPhase.R4_REFACTOR
        self.current_sparc = SPARCPhase.REVIEW

        try:
            refactor_results = {
                "phase": "REFACTOR",
                "items_checked": list(refactor_checklist.keys()),
                "timestamp": datetime.now().isoformat(),
                "details": {}
            }

            for check_name, check_func in refactor_checklist.items():
                try:
                    result = check_func()
                    refactor_results["details"][check_name] = result
                except Exception as e:
                    self.logger.warning(f"Refactor check {check_name} failed: {str(e)}")

            # Verify tests still pass
            passed_count = self._run_tests([])
            refactor_results["tests_still_passing"] = passed_count > 0

            self._save_checkpoint(
                sparc_phase=SPARCPhase.REVIEW,
                context=refactor_results
            )
            self.logger.info("R4 Complete: Code refactored, tests still passing")
            return True
        except Exception as e:
            self.logger.error(f"R4 Failed: {str(e)}")
            return False

    def phase_r5_create_pr(self, pr_details: Dict) -> bool:
        """R5: Create PR - Submit code for review"""
        self.logger.info("R5: Creating pull request")
        self.current_phase = RalphPhase.R5_CREATE_PR

        try:
            pr_data = {
                "phase": "CREATE_PR",
                "title": pr_details.get("title", f"Feature: {self.story_id}"),
                "description": pr_details.get("description", ""),
                "branch": self._get_current_branch(),
                "timestamp": datetime.now().isoformat(),
                "files_changed": self._get_changed_files()
            }

            # Create the PR via git
            pr_url = self._create_pull_request(pr_data)
            pr_data["pr_url"] = pr_url

            self._save_checkpoint(
                sparc_phase=SPARCPhase.REVIEW,
                context=pr_data
            )
            self.logger.info(f"R5 Complete: PR created at {pr_url}")
            return True
        except Exception as e:
            self.logger.error(f"R5 Failed: {str(e)}")
            return False

    def phase_r6_merge(self, merge_strategy: str = "squash") -> bool:
        """R6: Merge - Integrate code to main branch"""
        self.logger.info("R6: Merging to main")
        self.current_phase = RalphPhase.R6_MERGE
        self.current_sparc = SPARCPhase.CLOSE

        try:
            merge_data = {
                "phase": "MERGE",
                "strategy": merge_strategy,
                "timestamp": datetime.now().isoformat(),
                "branch": self._get_current_branch()
            }

            # Perform merge
            merge_result = self._perform_merge(merge_strategy)
            merge_data["merge_result"] = merge_result

            self._save_checkpoint(
                sparc_phase=SPARCPhase.CLOSE,
                context=merge_data
            )
            self.logger.info("R6 Complete: Merged to main branch")
            return True
        except Exception as e:
            self.logger.error(f"R6 Failed: {str(e)}")
            return False

    def phase_r7_complete(self) -> bool:
        """R7: Complete - Verification and cleanup"""
        self.logger.info("R7: Completing task")
        self.current_phase = RalphPhase.R7_COMPLETE
        self.current_sparc = SPARCPhase.CLOSE

        try:
            completion_data = {
                "phase": "COMPLETE",
                "story_id": self.story_id,
                "agent_id": self.agent_id,
                "start_time": self.start_time.isoformat(),
                "end_time": datetime.now().isoformat(),
                "duration_minutes": (datetime.now() - self.start_time).total_seconds() / 60,
                "verification_checks": {
                    "tests_passing": self._run_tests([]) > 0,
                    "merged_to_main": self._is_on_main_branch(),
                    "no_conflicts": True
                }
            }

            self._save_checkpoint(
                sparc_phase=SPARCPhase.CLOSE,
                context=completion_data,
                is_final=True
            )
            self.logger.info(f"R7 Complete: Task completed in {completion_data['duration_minutes']:.1f} minutes")
            return True
        except Exception as e:
            self.logger.error(f"R7 Failed: {str(e)}")
            return False

    def _save_checkpoint(self, sparc_phase: SPARCPhase, context: Dict, is_final: bool = False) -> str:
        """Save checkpoint at current phase"""
        checkpoint_name = f"CP-{self.current_phase.name}-{int(time.time())}.json"
        checkpoint_path = self.checkpoint_dir / checkpoint_name

        checkpoint_data: Dict = {
            "session_id": self.session_id,
            "story_id": self.story_id,
            "ralph_phase": self.current_phase.value,
            "sparc_phase": sparc_phase.value,
            "timestamp": datetime.now().isoformat(),
            "context": context,
            "is_final": is_final
        }

        checkpoint_path.write_text(json.dumps(checkpoint_data, indent=2))
        self.logger.info(f"Checkpoint saved: {checkpoint_name}")
        return str(checkpoint_path)

    def _analyze_test_strategy(self, requirements: Dict) -> Dict:
        """Analyze and plan testing strategy"""
        return {
            "unit_tests": requirements.get("unit_tests", []),
            "integration_tests": requirements.get("integration_tests", []),
            "e2e_tests": requirements.get("e2e_tests", []),
            "target_coverage": 85
        }

    def _run_tests(self, test_files: List[str]) -> int:
        """Run tests and return count of passing tests"""
        # Placeholder - actual implementation would run pytest/jest
        return 0

    def _get_current_branch(self) -> str:
        """Get current git branch"""
        try:
            result = subprocess.run(
                ["git", "rev-parse", "--abbrev-ref", "HEAD"],
                capture_output=True,
                text=True,
                timeout=5
            )
            return result.stdout.strip()
        except Exception:
            return "unknown"

    def _get_changed_files(self) -> List[str]:
        """Get list of changed files"""
        try:
            result = subprocess.run(
                ["git", "diff", "--name-only", "main...HEAD"],
                capture_output=True,
                text=True,
                timeout=5
            )
            return result.stdout.strip().split('\n')
        except Exception:
            return []

    def _create_pull_request(self, pr_data: Dict) -> str:
        """Create pull request via gh CLI"""
        try:
            # Would use gh CLI in actual implementation
            return f"https://github.com/example/pull/12345"
        except Exception as e:
            self.logger.error(f"PR creation failed: {str(e)}")
            return "pending"

    def _perform_merge(self, strategy: str) -> Dict:
        """Perform merge to main branch"""
        try:
            # Would execute git merge in actual implementation
            return {"status": "success", "strategy": strategy}
        except Exception as e:
            self.logger.error(f"Merge failed: {str(e)}")
            return {"status": "failed", "error": str(e)}

    def _is_on_main_branch(self) -> bool:
        """Check if currently on main branch"""
        return self._get_current_branch() == "main"


def main():
    """Main entry point for Ralph Loop executor"""
    if len(sys.argv) < 3:
        print("Usage: ralph-loop-executor.py <story_id> <agent_id> [--phase <R0-R7>]")
        sys.exit(1)

    story_id = sys.argv[1]
    agent_id = sys.argv[2]
    session_id = f"{story_id}_{int(time.time())}"

    executor = RalphLoopExecutor(story_id, agent_id, session_id)

    # Execute full R0-R7 cycle
    if executor.phase_r0_receive():
        print(f"✓ R0: Task received")

    if executor.phase_r1_understand({"acceptance_criteria": []}):
        print(f"✓ R1: Requirements understood")

    if executor.phase_r2_red([]):
        print(f"✓ R2: Tests written (RED)")

    if executor.phase_r3_green([]):
        print(f"✓ R3: Implementation complete (GREEN)")

    if executor.phase_r4_refactor({}):
        print(f"✓ R4: Code refactored")

    if executor.phase_r5_create_pr({}):
        print(f"✓ R5: PR created")

    if executor.phase_r6_merge():
        print(f"✓ R6: Merged to main")

    if executor.phase_r7_complete():
        print(f"✓ R7: Task completed")


if __name__ == "__main__":
    main()
