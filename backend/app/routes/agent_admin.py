"""
Agent Administration API Routes (Sprint 12)

Endpoints for reviewing and managing agent operations:
- GET /api/v1/admin/agents/runs - List agent runs
- GET /api/v1/admin/agents/runs/{run_id} - Get run details
- GET /api/v1/admin/agents/violations - List violations
- GET /api/v1/admin/agents/decisions-pending - Pending approvals
- PATCH /api/v1/admin/agents/decisions/{decision_id}/approve - Approve action
- PATCH /api/v1/admin/agents/decisions/{decision_id}/reject - Reject action
"""

from fastapi import APIRouter, HTTPException, Depends, Header, Query
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime
import logging
from uuid import UUID

from app.database import get_db
from app.auth.jwt_handler import verify_token
from app.auth.utils import extract_token_from_header
from app.services.agent_logger import AgentLoggerService
from app.models import AgentRun, AgentDecision, AgentGuardrailViolation

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/admin/agents", tags=["admin", "agents"])


def get_current_user(authorization: str = Header(None)):
    """Extract and verify current user from token"""
    try:
        token = extract_token_from_header(authorization)
        token_data = verify_token(token)
        return {
            "user_id": token_data.sub,
            "tenant_id": token_data.tenant_id,
            "roles": token_data.roles,
        }
    except Exception as e:
        logger.error(f"Authentication error: {str(e)}")
        raise HTTPException(status_code=401, detail="Invalid token")


def check_admin_role(current_user: dict):
    """Verify user has admin role"""
    if "admin" not in current_user.get("roles", []):
        raise HTTPException(status_code=403, detail="Admin role required")


@router.get("/runs")
async def list_agent_runs(
    db = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    agent_type: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    date_from: Optional[datetime] = Query(None),
    date_to: Optional[datetime] = Query(None),
    limit: int = Query(100, ge=1, le=1000),
):
    """
    List agent runs with optional filtering

    Query Parameters:
    - agent_type: Filter by agent type (carbon_agent, kpi_agent, etc.)
    - status: Filter by status (completed, failed, pending_approval)
    - date_from: Start date for range (ISO format)
    - date_to: End date for range (ISO format)
    - limit: Maximum results (default 100)

    Returns:
        List of agent runs with summary information
    """
    try:
        check_admin_role(current_user)

        tenant_id = current_user["tenant_id"]
        logger_service = AgentLoggerService(db)

        runs = logger_service.get_agent_audit_trail(
            tenant_id=UUID(tenant_id),
            agent_type=agent_type,
            date_from=date_from,
            date_to=date_to,
            status=status,
            limit=limit,
        )

        return {
            "success": True,
            "count": len(runs),
            "runs": runs,
        }

    except Exception as e:
        logger.error(f"Failed to list agent runs: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/runs/{run_id}")
async def get_agent_run(
    run_id: str,
    db = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """
    Get detailed information about a specific agent run

    Includes:
    - Full execution context
    - Input parameters
    - Tools used
    - Output produced
    - Associated decisions
    - Associated violations
    - Approval status

    Returns:
        Complete agent run details
    """
    try:
        check_admin_role(current_user)

        tenant_id = current_user["tenant_id"]
        logger_service = AgentLoggerService(db)

        run = logger_service.get_agent_run(
            run_id=UUID(run_id),
            tenant_id=UUID(tenant_id),
        )

        if not run:
            raise HTTPException(status_code=404, detail=f"Agent run {run_id} not found")

        return {
            "success": True,
            "run": run,
        }

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to get agent run: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/violations")
async def list_guardrail_violations(
    db = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    severity: Optional[str] = Query(None),
    resolved: bool = Query(False),
    limit: int = Query(50, ge=1, le=500),
):
    """
    List guardrail violations

    Query Parameters:
    - severity: Filter by severity (low, medium, high, critical)
    - resolved: Show only unresolved violations (default)
    - limit: Maximum results

    Returns:
        List of guardrail violations
    """
    try:
        check_admin_role(current_user)

        tenant_id = current_user["tenant_id"]
        logger_service = AgentLoggerService(db)

        violations = logger_service.get_open_violations(
            tenant_id=UUID(tenant_id),
            severity=severity,
            limit=limit,
        )

        return {
            "success": True,
            "count": len(violations),
            "violations": violations,
        }

    except Exception as e:
        logger.error(f"Failed to list violations: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/decisions-pending")
async def list_pending_decisions(
    db = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    impact_level: Optional[str] = Query(None),
    limit: int = Query(100, ge=1, le=1000),
):
    """
    List pending agent decision approvals

    Query Parameters:
    - impact_level: Filter by impact (low, medium, high, critical)
    - limit: Maximum results

    Returns:
        List of decisions awaiting approval
    """
    try:
        check_admin_role(current_user)

        tenant_id = current_user["tenant_id"]

        query = db.query(AgentDecision).filter(
            AgentDecision.tenant_id == UUID(tenant_id),
            AgentDecision.approval_status == "pending",
            AgentDecision.requires_approval == True,
        )

        if impact_level:
            query = query.filter(AgentDecision.impact_level == impact_level)

        decisions = query.order_by(
            AgentDecision.created_at.desc()
        ).limit(limit).all()

        result = [
            {
                "decision_id": str(d.id),
                "agent_run_id": str(d.agent_run_id),
                "decision_type": d.decision_type,
                "action": d.action,
                "impact_level": d.impact_level,
                "impact_description": d.impact_description,
                "action_entity_type": d.action_entity_type,
                "action_entity_id": str(d.action_entity_id) if d.action_entity_id else None,
                "created_at": d.created_at.isoformat(),
            }
            for d in decisions
        ]

        return {
            "success": True,
            "count": len(result),
            "pending_decisions": result,
        }

    except Exception as e:
        logger.error(f"Failed to list pending decisions: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.patch("/decisions/{decision_id}/approve")
async def approve_decision(
    decision_id: str,
    db = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    request_body: Optional[dict] = None,
):
    """
    Approve an agent decision

    Request Body (optional):
    {
        "approval_reason": "Metrics verified against audit",
        "execute": true  # Execute the decision immediately?
    }

    Returns:
        Updated decision record
    """
    try:
        check_admin_role(current_user)

        tenant_id = current_user["tenant_id"]
        user_id = current_user["user_id"]
        approval_reason = request_body.get("approval_reason") if request_body else None
        execute = request_body.get("execute", False) if request_body else False

        # Get decision
        decision = db.query(AgentDecision).filter(
            AgentDecision.id == UUID(decision_id),
            AgentDecision.tenant_id == UUID(tenant_id),
        ).first()

        if not decision:
            raise HTTPException(status_code=404, detail=f"Decision {decision_id} not found")

        if decision.approval_status != "pending":
            raise HTTPException(status_code=400, detail=f"Decision is not pending approval")

        # Approve decision
        decision.approval_status = "approved"
        decision.approved_by = UUID(user_id)
        decision.approved_at = datetime.utcnow()
        decision.approval_reason = approval_reason

        if execute:
            decision.executed = True
            decision.executed_at = datetime.utcnow()

        db.commit()

        logger.info(f"Decision {decision_id} approved by {user_id}")

        return {
            "success": True,
            "decision_id": str(decision.id),
            "approval_status": decision.approval_status,
            "approved_at": decision.approved_at.isoformat(),
            "executed": decision.executed,
        }

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        db.rollback()
        logger.error(f"Failed to approve decision: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.patch("/decisions/{decision_id}/reject")
async def reject_decision(
    decision_id: str,
    db = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    request_body: Optional[dict] = None,
):
    """
    Reject an agent decision

    Request Body (required):
    {
        "rejection_reason": "Data inconsistencies detected in source metrics"
    }

    Returns:
        Updated decision record
    """
    try:
        check_admin_role(current_user)

        tenant_id = current_user["tenant_id"]
        user_id = current_user["user_id"]
        rejection_reason = request_body.get("rejection_reason") if request_body else None

        if not rejection_reason:
            raise HTTPException(status_code=400, detail="rejection_reason is required")

        # Get decision
        decision = db.query(AgentDecision).filter(
            AgentDecision.id == UUID(decision_id),
            AgentDecision.tenant_id == UUID(tenant_id),
        ).first()

        if not decision:
            raise HTTPException(status_code=404, detail=f"Decision {decision_id} not found")

        if decision.approval_status != "pending":
            raise HTTPException(status_code=400, detail=f"Decision is not pending approval")

        # Reject decision
        decision.approval_status = "rejected"
        decision.rejected_by = UUID(user_id)
        decision.rejected_at = datetime.utcnow()
        decision.rejection_reason = rejection_reason

        db.commit()

        logger.info(f"Decision {decision_id} rejected by {user_id}: {rejection_reason}")

        return {
            "success": True,
            "decision_id": str(decision.id),
            "approval_status": decision.approval_status,
            "rejected_at": decision.rejected_at.isoformat(),
            "rejection_reason": rejection_reason,
        }

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        db.rollback()
        logger.error(f"Failed to reject decision: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.patch("/violations/{violation_id}/resolve")
async def resolve_violation(
    violation_id: str,
    db = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    request_body: Optional[dict] = None,
):
    """
    Mark a guardrail violation as resolved

    Request Body (required):
    {
        "resolution_notes": "Fabricated entities removed from input context"
    }

    Returns:
        Updated violation record
    """
    try:
        check_admin_role(current_user)

        tenant_id = current_user["tenant_id"]
        user_id = current_user["user_id"]
        resolution_notes = request_body.get("resolution_notes") if request_body else None

        if not resolution_notes:
            raise HTTPException(status_code=400, detail="resolution_notes are required")

        logger_service = AgentLoggerService(db)

        success = logger_service.resolve_violation(
            violation_id=UUID(violation_id),
            tenant_id=UUID(tenant_id),
            resolved_by=UUID(user_id),
            resolution_notes=resolution_notes,
        )

        if not success:
            raise HTTPException(status_code=404, detail=f"Violation {violation_id} not found")

        # Get updated violation
        violation = db.query(AgentGuardrailViolation).filter(
            AgentGuardrailViolation.id == UUID(violation_id),
            AgentGuardrailViolation.tenant_id == UUID(tenant_id),
        ).first()

        return {
            "success": True,
            "violation_id": str(violation.id),
            "status": violation.status,
            "resolved": violation.resolved,
            "resolved_at": violation.resolved_at.isoformat(),
        }

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        db.rollback()
        logger.error(f"Failed to resolve violation: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stats")
async def get_agent_stats(
    db = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    days: int = Query(30, ge=1, le=365),
):
    """
    Get agent statistics for the tenant

    Query Parameters:
    - days: Number of days to include in stats (default 30)

    Returns:
        Statistics on agent runs, violations, approvals
    """
    try:
        check_admin_role(current_user)

        tenant_id = current_user["tenant_id"]
        from datetime import timedelta

        date_from = datetime.utcnow() - timedelta(days=days)

        # Count agent runs
        run_count = db.query(AgentRun).filter(
            AgentRun.tenant_id == UUID(tenant_id),
            AgentRun.created_at >= date_from,
        ).count()

        # Count violations
        violation_count = db.query(AgentGuardrailViolation).filter(
            AgentGuardrailViolation.tenant_id == UUID(tenant_id),
            AgentGuardrailViolation.created_at >= date_from,
        ).count()

        # Count open violations
        open_violations = db.query(AgentGuardrailViolation).filter(
            AgentGuardrailViolation.tenant_id == UUID(tenant_id),
            AgentGuardrailViolation.resolved == False,
        ).count()

        # Count pending decisions
        pending_decisions = db.query(AgentDecision).filter(
            AgentDecision.tenant_id == UUID(tenant_id),
            AgentDecision.approval_status == "pending",
        ).count()

        # Violations by severity
        severity_counts = {}
        for severity in ["low", "medium", "high", "critical"]:
            count = db.query(AgentGuardrailViolation).filter(
                AgentGuardrailViolation.tenant_id == UUID(tenant_id),
                AgentGuardrailViolation.severity == severity,
                AgentGuardrailViolation.created_at >= date_from,
            ).count()
            severity_counts[severity] = count

        return {
            "success": True,
            "stats": {
                "period_days": days,
                "agent_runs": run_count,
                "violations": {
                    "total": violation_count,
                    "open": open_violations,
                    "by_severity": severity_counts,
                },
                "pending_approvals": pending_decisions,
            }
        }

    except Exception as e:
        logger.error(f"Failed to get agent stats: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
