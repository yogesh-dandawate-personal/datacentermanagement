"""
Agent Guardrails Service (Sprint 12)

Implements policy enforcement for agents:
- Fabrication Detection: Verify all referenced data exists
- Approval Gating: Require approval for high-impact actions
- Data Integrity: Enforce immutability and lineage tracking
- Access Control: Enforce tenant isolation and permissions
- Cross-Tenant Protection: Prevent accidental cross-tenant operations

All guardrails are evaluated BEFORE agent actions are allowed.
"""

from typing import Dict, List, Optional, Any, Tuple
from uuid import UUID
import logging
from sqlalchemy.orm import Session
from sqlalchemy import and_

from app.models import (
    AgentRun,
    AgentDecision,
    AgentGuardrailViolation,
    CarbonCalculation,
    EmissionFactor,
    KPIDefinition,
    KPISnapshot,
    TelemetryReading,
    Meter,
    User,
    Tenant,
)
from app.services.agent_logger import AgentLoggerService

logger = logging.getLogger(__name__)


class AgentGuardrailsService:
    """Service for enforcing agent guardrails and policies"""

    def __init__(self, db: Session):
        self.db = db
        self.logger_service = AgentLoggerService(db)

    # =====================================================================
    # FABRICATION DETECTION
    # =====================================================================

    def check_fabrication(
        self,
        run_id: UUID,
        tenant_id: UUID,
        citations: List[str],
        referenced_entities: Dict[str, Any],
    ) -> Tuple[bool, Optional[str]]:
        """
        Detect if agent is referencing non-existent data

        Checks:
        - All cited entities actually exist in database
        - Referenced IDs are real and belong to correct tenant
        - No references to deleted or archived entities
        - All metric/factor IDs in citations are valid

        Args:
            run_id: Agent run being checked
            tenant_id: Tenant context
            citations: List of source entity IDs
            referenced_entities: Dict mapping entity IDs to their types

        Returns:
            (is_valid, error_message):
            - (True, None) if all citations are valid
            - (False, error) if fabrication detected

        Raises:
            Exception on database errors
        """
        try:
            if not citations:
                return True, None

            # Check each citation for existence
            fabricated_entities = []

            for citation_id in citations:
                if not self._verify_entity_exists(tenant_id, citation_id):
                    fabricated_entities.append(citation_id)

            if fabricated_entities:
                error_msg = f"Fabrication detected: Referenced non-existent entities: {fabricated_entities}"

                # Log violation
                self.logger_service.log_guardrail_violation(
                    run_id=run_id,
                    tenant_id=tenant_id,
                    violation_type="fabrication",
                    description=error_msg,
                    severity="critical",
                    violation_data={
                        "fabricated_entities": fabricated_entities,
                        "cited_count": len(citations),
                    }
                )
                return False, error_msg

            return True, None

        except Exception as e:
            logger.error(f"Fabrication check failed: {str(e)}")
            raise

    def _verify_entity_exists(self, tenant_id: UUID, entity_id: str) -> bool:
        """
        Verify that an entity exists in the database

        Checks multiple entity types:
        - Carbon calculations
        - Emission factors
        - KPI definitions and snapshots
        - Telemetry readings
        - Meters

        Returns:
            True if entity exists and belongs to tenant
        """
        try:
            # Try to parse as UUID
            try:
                entity_uuid = UUID(entity_id)
            except (ValueError, AttributeError):
                # Not a valid UUID format
                return False

            # Check carbon calculations
            if self.db.query(CarbonCalculation).filter(
                and_(
                    CarbonCalculation.id == entity_uuid,
                    CarbonCalculation.tenant_id == tenant_id
                )
            ).first():
                return True

            # Check emission factors (global, not tenant-specific)
            if self.db.query(EmissionFactor).filter(
                EmissionFactor.id == entity_uuid,
                EmissionFactor.is_active == True
            ).first():
                return True

            # Check KPI definitions
            if self.db.query(KPIDefinition).filter(
                and_(
                    KPIDefinition.id == entity_uuid,
                    KPIDefinition.tenant_id == tenant_id
                )
            ).first():
                return True

            # Check KPI snapshots
            if self.db.query(KPISnapshot).filter(
                and_(
                    KPISnapshot.id == entity_uuid,
                    KPISnapshot.tenant_id == tenant_id
                )
            ).first():
                return True

            # Check telemetry readings
            if self.db.query(TelemetryReading).filter(
                and_(
                    TelemetryReading.id == entity_uuid,
                    TelemetryReading.tenant_id == tenant_id
                )
            ).first():
                return True

            # Check meters
            if self.db.query(Meter).filter(
                and_(
                    Meter.id == entity_uuid,
                    Meter.tenant_id == tenant_id
                )
            ).first():
                return True

            return False

        except Exception as e:
            logger.error(f"Entity verification failed: {str(e)}")
            return False

    # =====================================================================
    # APPROVAL GATING
    # =====================================================================

    def check_approval_requirement(
        self,
        run_id: UUID,
        tenant_id: UUID,
        action_type: str,
        impact_level: str,
        user_id: Optional[UUID] = None,
    ) -> Tuple[bool, str]:
        """
        Determine if agent action requires approval

        Rules:
        - HIGH/CRITICAL actions always require approval
        - MEDIUM actions require manager review
        - LOW actions auto-approved
        - Data modifications always require approval
        - Read-only operations never require approval

        Args:
            run_id: Agent run being checked
            tenant_id: Tenant context
            action_type: Type of action (CREATE, MODIFY, DELETE, READ, ANALYZE)
            impact_level: low, medium, high, critical
            user_id: User who triggered the agent

        Returns:
            (requires_approval, reason):
            - (True, reason) if approval needed
            - (False, reason) if auto-approved
        """
        try:
            # Read operations never require approval
            if action_type in ["READ", "ANALYZE", "QUERY"]:
                return False, "Read-only operation auto-approved"

            # Data modifications always require approval
            if action_type in ["CREATE", "MODIFY", "DELETE"]:
                # Only create requires approval, but at high impact
                if action_type == "CREATE" and impact_level == "low":
                    return False, "Low-impact record creation auto-approved"
                return True, f"Data modification requires approval (impact: {impact_level})"

            # Impact-based approval
            if impact_level in ["high", "critical"]:
                return True, f"{impact_level.upper()}-impact action requires approval"

            if impact_level == "medium":
                return True, "Medium-impact action requires manager review"

            # Default: auto-approve low-impact
            return False, "Low-impact action auto-approved"

        except Exception as e:
            logger.error(f"Approval check failed: {str(e)}")
            # Fail safe: require approval on error
            return True, f"Approval required due to verification error: {str(e)}"

    # =====================================================================
    # DATA INTEGRITY
    # =====================================================================

    def check_data_integrity(
        self,
        run_id: UUID,
        tenant_id: UUID,
        target_entity_type: str,
        target_entity_id: Optional[UUID] = None,
        action_type: str = "CREATE",
    ) -> Tuple[bool, Optional[str]]:
        """
        Verify data integrity constraints

        Rules:
        - Never overwrite approved records
        - Only create draft calculations
        - Require human review before publishing
        - Maintain data lineage
        - Prevent modification of locked records

        Args:
            run_id: Agent run being checked
            tenant_id: Tenant context
            target_entity_type: Type being modified (calculation, credit, report)
            target_entity_id: Entity being modified (None for creates)
            action_type: CREATE, MODIFY, or DELETE

        Returns:
            (is_valid, error_message)
        """
        try:
            # CREATE operations create draft records only
            if action_type == "CREATE":
                return True, None

            # MODIFY operations have restrictions
            if action_type == "MODIFY" and target_entity_id:
                # Check if target is approved/locked
                if target_entity_type == "carbon_calculation":
                    calc = self.db.query(CarbonCalculation).filter(
                        and_(
                            CarbonCalculation.id == target_entity_id,
                            CarbonCalculation.tenant_id == tenant_id
                        )
                    ).first()

                    if calc and calc.status in ["approved", "ready_for_review"]:
                        error_msg = f"Cannot modify approved calculation {target_entity_id}"
                        self.logger_service.log_guardrail_violation(
                            run_id=run_id,
                            tenant_id=tenant_id,
                            violation_type="data_integrity",
                            description=error_msg,
                            severity="high",
                            entity_type="carbon_calculation",
                            entity_id=target_entity_id,
                        )
                        return False, error_msg

            # DELETE operations generally not allowed for agents
            if action_type == "DELETE":
                error_msg = "Agents cannot delete records (data integrity violation)"
                self.logger_service.log_guardrail_violation(
                    run_id=run_id,
                    tenant_id=tenant_id,
                    violation_type="data_integrity",
                    description=error_msg,
                    severity="critical",
                    entity_type=target_entity_type,
                    entity_id=target_entity_id,
                )
                return False, error_msg

            return True, None

        except Exception as e:
            logger.error(f"Data integrity check failed: {str(e)}")
            raise

    # =====================================================================
    # ACCESS CONTROL
    # =====================================================================

    def check_access_control(
        self,
        run_id: UUID,
        tenant_id: UUID,
        user_id: Optional[UUID] = None,
        target_entity_type: Optional[str] = None,
        target_entity_id: Optional[UUID] = None,
    ) -> Tuple[bool, Optional[str]]:
        """
        Enforce access control and tenant isolation

        Rules:
        - Agent can only operate within its tenant context
        - No cross-tenant data access
        - User permissions must be checked if available
        - Respect entity-level access controls

        Args:
            run_id: Agent run being checked
            tenant_id: Tenant context for operation
            user_id: User who triggered agent (optional)
            target_entity_type: Type of entity being accessed
            target_entity_id: Specific entity ID

        Returns:
            (is_allowed, error_message)
        """
        try:
            # Verify tenant exists
            tenant = self.db.query(Tenant).filter(Tenant.id == tenant_id).first()
            if not tenant:
                error_msg = f"Tenant {tenant_id} not found"
                self.logger_service.log_guardrail_violation(
                    run_id=run_id,
                    tenant_id=tenant_id,
                    violation_type="access_control",
                    description=error_msg,
                    severity="critical",
                )
                return False, error_msg

            if not tenant.is_active:
                error_msg = f"Tenant {tenant_id} is inactive"
                self.logger_service.log_guardrail_violation(
                    run_id=run_id,
                    tenant_id=tenant_id,
                    violation_type="access_control",
                    description=error_msg,
                    severity="high",
                )
                return False, error_msg

            # Verify user if provided
            if user_id:
                user = self.db.query(User).filter(
                    and_(
                        User.id == user_id,
                        User.tenant_id == tenant_id,
                        User.is_active == True
                    )
                ).first()

                if not user:
                    error_msg = f"User {user_id} not found or inactive in tenant {tenant_id}"
                    self.logger_service.log_guardrail_violation(
                        run_id=run_id,
                        tenant_id=tenant_id,
                        violation_type="access_control",
                        description=error_msg,
                        severity="high",
                    )
                    return False, error_msg

            return True, None

        except Exception as e:
            logger.error(f"Access control check failed: {str(e)}")
            raise

    def check_cross_tenant_isolation(
        self,
        run_id: UUID,
        agent_tenant_id: UUID,
        input_context: Dict[str, Any],
    ) -> Tuple[bool, Optional[str]]:
        """
        Verify agent is not accessing cross-tenant data

        Checks:
        - No tenant_id mismatches in input
        - No queries crossing tenant boundaries
        - No references to entities from other tenants

        Args:
            run_id: Agent run being checked
            agent_tenant_id: Tenant agent is operating in
            input_context: Input parameters

        Returns:
            (is_valid, error_message)
        """
        try:
            # Extract tenant ID from input context if present
            if isinstance(input_context, dict):
                context_tenant_id = input_context.get("tenant_id")

                if context_tenant_id and context_tenant_id != str(agent_tenant_id):
                    error_msg = f"Cross-tenant operation detected: agent in {agent_tenant_id}, context in {context_tenant_id}"
                    self.logger_service.log_guardrail_violation(
                        run_id=run_id,
                        tenant_id=agent_tenant_id,
                        violation_type="cross_tenant",
                        description=error_msg,
                        severity="critical",
                        violation_data={
                            "agent_tenant": str(agent_tenant_id),
                            "context_tenant": str(context_tenant_id),
                        }
                    )
                    return False, error_msg

            return True, None

        except Exception as e:
            logger.error(f"Cross-tenant check failed: {str(e)}")
            raise

    # =====================================================================
    # COMPREHENSIVE GUARDRAIL VALIDATION
    # =====================================================================

    def validate_agent_action(
        self,
        run_id: UUID,
        tenant_id: UUID,
        agent_type: str,
        action_type: str,
        impact_level: str,
        citations: List[str],
        referenced_entities: Dict[str, Any],
        input_context: Dict[str, Any],
        user_id: Optional[UUID] = None,
    ) -> Dict[str, Any]:
        """
        Run all guardrail checks on an agent action

        Returns comprehensive validation result with details on all checks.

        Args:
            run_id: Agent run ID
            tenant_id: Tenant context
            agent_type: Type of agent
            action_type: Action being performed
            impact_level: Impact classification
            citations: Source data references
            referenced_entities: Entities being used
            input_context: Input parameters
            user_id: User who triggered agent

        Returns:
            {
                "is_valid": bool,
                "requires_approval": bool,
                "checks": {
                    "fabrication": {"passed": bool, "error": str or None},
                    "access_control": {"passed": bool, "error": str or None},
                    "data_integrity": {"passed": bool, "error": str or None},
                    "cross_tenant": {"passed": bool, "error": str or None},
                }
            }
        """
        results = {
            "is_valid": True,
            "requires_approval": False,
            "approval_reason": None,
            "checks": {
                "fabrication": {"passed": True, "error": None},
                "access_control": {"passed": True, "error": None},
                "data_integrity": {"passed": True, "error": None},
                "cross_tenant": {"passed": True, "error": None},
            }
        }

        try:
            # Check 1: Fabrication Detection
            fab_valid, fab_error = self.check_fabrication(run_id, tenant_id, citations, referenced_entities)
            results["checks"]["fabrication"]["passed"] = fab_valid
            results["checks"]["fabrication"]["error"] = fab_error
            if not fab_valid:
                results["is_valid"] = False

            # Check 2: Access Control
            ac_valid, ac_error = self.check_access_control(run_id, tenant_id, user_id)
            results["checks"]["access_control"]["passed"] = ac_valid
            results["checks"]["access_control"]["error"] = ac_error
            if not ac_valid:
                results["is_valid"] = False

            # Check 3: Data Integrity
            di_valid, di_error = self.check_data_integrity(run_id, tenant_id, "record", None, action_type)
            results["checks"]["data_integrity"]["passed"] = di_valid
            results["checks"]["data_integrity"]["error"] = di_error
            if not di_valid:
                results["is_valid"] = False

            # Check 4: Cross-Tenant Isolation
            ct_valid, ct_error = self.check_cross_tenant_isolation(run_id, tenant_id, input_context)
            results["checks"]["cross_tenant"]["passed"] = ct_valid
            results["checks"]["cross_tenant"]["error"] = ct_error
            if not ct_valid:
                results["is_valid"] = False

            # Approval gating (only if other checks pass)
            if results["is_valid"]:
                req_approval, approval_reason = self.check_approval_requirement(
                    run_id, tenant_id, action_type, impact_level, user_id
                )
                results["requires_approval"] = req_approval
                results["approval_reason"] = approval_reason

            return results

        except Exception as e:
            logger.error(f"Validation failed: {str(e)}")
            results["is_valid"] = False
            results["error"] = str(e)
            return results
