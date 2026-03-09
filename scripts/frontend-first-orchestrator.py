#!/usr/bin/env python3
"""
Frontend-First Orchestrator

Implements frontend-first development strategy:
- Build frontend with mock APIs first
- Get stakeholder buy-in before backend implementation
- Mock APIs match planned backend contracts
- Reduces rework by validating UX early
"""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List
import subprocess


class MockAPIGenerator:
    """Generates mock API specifications and implementations"""

    def __init__(self):
        self.logger = logging.getLogger("mock-api-generator")

    def generate_mock_spec(self, api_name: str, endpoints: List[Dict]) -> Dict:
        """Generate mock API specification"""
        spec = {
            "api_name": api_name,
            "version": "1.0.0",
            "base_url": f"http://localhost:3001/api/mock/{api_name}",
            "endpoints": endpoints,
            "generated_at": datetime.now().isoformat()
        }
        return spec

    def generate_mock_data(self, endpoint: Dict) -> Dict:
        """Generate sample data for endpoint"""
        samples = {
            "org_crud": {
                "create": {"id": "org-123", "name": "Sample Org", "created_at": "2026-03-09"},
                "read": {"id": "org-123", "name": "Sample Org"},
                "update": {"id": "org-123", "name": "Updated Org"},
                "delete": {"status": "success"}
            },
            "facility_hierarchy": {
                "list": [
                    {"id": "fac-1", "name": "Facility 1", "parent_id": "org-123"},
                    {"id": "fac-2", "name": "Facility 2", "parent_id": "org-123"}
                ]
            },
            "energy_metrics": {
                "current": {"total_consumption_kwh": 1523.5, "timestamp": "2026-03-09T10:00:00Z"},
                "daily": [
                    {"date": "2026-03-09", "consumption_kwh": 1523.5},
                    {"date": "2026-03-08", "consumption_kwh": 1421.2}
                ]
            },
            "emissions_calculation": {
                "total_emissions_mtco2e": 542.3,
                "scope_1": 123.4,
                "scope_2": 342.1,
                "scope_3": 76.8
            }
        }
        return samples.get(endpoint.get("api_name"), {})


class FrontendFirstOrchestrator:
    """Frontend-first development orchestrator"""

    def __init__(self):
        self.logger = self._setup_logging()
        self.mock_generator = MockAPIGenerator()

    def _setup_logging(self) -> logging.Logger:
        """Setup logging"""
        log_dir = Path("./.claude/orchestrator/logs")
        log_dir.mkdir(parents=True, exist_ok=True)

        logger = logging.getLogger("frontend-first")
        handler = logging.FileHandler(log_dir / "frontend-first.log")
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
        return logger

    def generate_sprint_mocks(self, sprint_num: int) -> Dict:
        """Generate mock APIs for entire sprint"""
        self.logger.info(f"Generating mocks for Sprint {sprint_num}")

        # Load sprint assignments
        assignments_path = Path("./.claude/config/agent-assignments.json")
        if not assignments_path.exists():
            return {"error": "Agent assignments not found"}

        try:
            assignments = json.loads(assignments_path.read_text())
            sprint_key = f"sprint_{sprint_num}_*"

            # Find sprint
            sprint_config = None
            for key, config in assignments.get("sprints", {}).items():
                if key.startswith(f"sprint_{sprint_num}_"):
                    sprint_config = config
                    break

            if not sprint_config:
                return {"error": f"Sprint {sprint_num} not found"}

            mocks = {
                "sprint": sprint_num,
                "sprint_name": sprint_config.get("name"),
                "mock_apis": []
            }

            # Generate mocks for each API
            for api_name in sprint_config.get("mock_apis", []):
                mock_spec = self.mock_generator.generate_mock_spec(
                    api_name=api_name,
                    endpoints=[
                        {"name": "create", "method": "POST"},
                        {"name": "read", "method": "GET"},
                        {"name": "update", "method": "PUT"},
                        {"name": "delete", "method": "DELETE"},
                        {"name": "list", "method": "GET"}
                    ]
                )
                mocks["mock_apis"].append(mock_spec)

            self.logger.info(f"Generated {len(mocks['mock_apis'])} mocks for Sprint {sprint_num}")
            return mocks

        except Exception as e:
            self.logger.error(f"Failed to generate mocks: {str(e)}")
            return {"error": str(e)}

    def create_demo_environment(self, sprint_num: int) -> Dict:
        """Create demonstration environment for sprint"""
        self.logger.info(f"Creating demo environment for Sprint {sprint_num}")

        demo_info = {
            "sprint": sprint_num,
            "demo_url": f"http://localhost:3001/demo/sprint-{sprint_num}",
            "features": [],
            "created_at": datetime.now().isoformat()
        }

        # Placeholder features based on sprint
        features_by_sprint = {
            1: ["Authentication UI", "Tenant Selection", "Organization Setup"],
            2: ["Org Tree View", "Hierarchy Editor", "Member Management"],
            5: ["Energy Dashboard", "Consumption Charts", "Trend Analysis"],
        }

        demo_info["features"] = features_by_sprint.get(sprint_num, [])

        self.logger.info(f"Demo environment created: {demo_info['demo_url']}")
        return demo_info

    def generate_frontend_first_plan(self, sprint_num: int) -> Dict:
        """Generate frontend-first implementation plan"""
        plan = {
            "sprint": sprint_num,
            "strategy": "Frontend-First",
            "phases": [
                {
                    "phase": 1,
                    "name": "Frontend Design & Mockups",
                    "duration_hours": 16,
                    "agents": ["Frontend_React_01", "Frontend_UX_01"],
                    "deliverables": ["Figma designs", "Component library"]
                },
                {
                    "phase": 2,
                    "name": "Mock API Implementation",
                    "duration_hours": 8,
                    "agents": ["Backend_FastAPI_01"],
                    "deliverables": ["Mock API endpoints", "Sample data"]
                },
                {
                    "phase": 3,
                    "name": "Frontend Components",
                    "duration_hours": 24,
                    "agents": ["Frontend_React_01", "Frontend_React_02"],
                    "deliverables": ["React components", "Pages", "State management"]
                },
                {
                    "phase": 4,
                    "name": "Mock Integration Testing",
                    "duration_hours": 12,
                    "agents": ["QA_E2E_01"],
                    "deliverables": ["E2E tests", "Demo scenarios"]
                },
                {
                    "phase": 5,
                    "name": "Stakeholder Demo & Feedback",
                    "duration_hours": 4,
                    "agents": ["Frontend_UX_01"],
                    "deliverables": ["Demo recording", "Feedback document"]
                },
                {
                    "phase": 6,
                    "name": "Backend Implementation",
                    "duration_hours": 40,
                    "agents": ["Backend_FastAPI_01", "Backend_FastAPI_02", "Backend_Database_01"],
                    "deliverables": ["API endpoints", "Database schema", "Business logic"]
                }
            ],
            "total_duration_hours": 104,
            "stakeholder_approval_gate": "phase_5",
            "created_at": datetime.now().isoformat()
        }

        return plan

    def save_mocks(self, sprint_num: int, mocks: Dict):
        """Save mock specifications to file"""
        output_dir = Path(f"./frontend/src/api/mocks/sprint-{sprint_num}")
        output_dir.mkdir(parents=True, exist_ok=True)

        output_file = output_dir / "mocks.json"
        output_file.write_text(json.dumps(mocks, indent=2))

        self.logger.info(f"Mocks saved to {output_file}")

    def save_plan(self, sprint_num: int, plan: Dict):
        """Save frontend-first plan to file"""
        output_dir = Path("./docs/implementation/frontend-first")
        output_dir.mkdir(parents=True, exist_ok=True)

        output_file = output_dir / f"sprint-{sprint_num}-plan.md"

        markdown = f"""# Frontend-First Plan: Sprint {sprint_num}

## Strategy
Implement frontend with mock APIs first to get stakeholder buy-in before backend development.

## Phases

"""
        for phase in plan.get("phases", []):
            markdown += f"### Phase {phase['phase']}: {phase['name']}\n\n"
            markdown += f"**Duration**: {phase['duration_hours']} hours\n\n"
            markdown += f"**Team**: {', '.join(phase['agents'])}\n\n"
            markdown += f"**Deliverables**:\n"
            for deliverable in phase['deliverables']:
                markdown += f"- {deliverable}\n"
            markdown += "\n"

        markdown += f"\n## Total Duration\n{plan['total_duration_hours']} hours\n\n"
        markdown += f"## Approval Gate\n{plan['stakeholder_approval_gate']}\n"

        output_file.write_text(markdown)
        self.logger.info(f"Plan saved to {output_file}")


def main():
    """Main entry point"""
    import sys

    if len(sys.argv) < 2:
        print("Usage: frontend-first-orchestrator.py <command> [sprint]")
        print("Commands:")
        print("  generate-mocks <sprint>   - Generate mock APIs for sprint")
        print("  demo <sprint>             - Create demo environment")
        print("  plan <sprint>             - Generate frontend-first plan")
        sys.exit(1)

    command = sys.argv[1]
    sprint = int(sys.argv[2]) if len(sys.argv) > 2 else 1

    orchestrator = FrontendFirstOrchestrator()

    if command == "generate-mocks":
        mocks = orchestrator.generate_sprint_mocks(sprint)
        orchestrator.save_mocks(sprint, mocks)
        print(json.dumps(mocks, indent=2))

    elif command == "demo":
        demo = orchestrator.create_demo_environment(sprint)
        print(json.dumps(demo, indent=2))

    elif command == "plan":
        plan = orchestrator.generate_frontend_first_plan(sprint)
        orchestrator.save_plan(sprint, plan)
        print(json.dumps(plan, indent=2))

    else:
        print(f"Unknown command: {command}")
        sys.exit(1)


if __name__ == "__main__":
    main()
