"""
API routes for workflow and approval management

Endpoints:
- Workflow Management (3 endpoints)
- Approval Management (5 endpoints)
- Approval Comments (2 endpoints)
- Escalation (3 endpoints)
"""

from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.orm import Session
from uuid import UUID
from datetime import datetime
from typing import Optional

from app.database import get_db
from app.services.workflow_service import (
    WorkflowService,
    ApprovalService,
    ApprovalCommentService,
    EscalationService,
)

router = APIRouter(prefix="/api/v1", tags=["workflow"])


# ============================================================================
# Workflow Management Endpoints
# ============================================================================


@router.post("/workflows")
async def create_workflow(
    entity_id: str,
    entity_type: str,
    db: Session = Depends(get_db),
    x_user_id: str = Header(None),
):
    """Create new workflow"""
    try:
        service = WorkflowService(db)
        result = service.create_workflow(
            entity_id=UUID(entity_id),
            entity_type=entity_type,
            initial_state="draft",
            changed_by=UUID(x_user_id),
        )
        return {"success": True, "data": result}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/workflows/{entity_id}/{entity_type}")
async def get_workflow(
    entity_id: str,
    entity_type: str,
    db: Session = Depends(get_db),
):
    """Get workflow status"""
    try:
        service = WorkflowService(db)
        result = service.get_workflow(UUID(entity_id), entity_type)
        return {"success": True, "data": result}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/workflows/{entity_id}/{entity_type}/history")
async def get_workflow_history(
    entity_id: str,
    entity_type: str,
    db: Session = Depends(get_db),
):
    """Get workflow state history"""
    try:
        service = WorkflowService(db)
        result = service.get_workflow_history(UUID(entity_id), entity_type)
        return {"success": True, "data": result}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# ============================================================================
# Approval Management Endpoints
# ============================================================================


@router.post("/approvals")
async def create_approval(
    entity_id: str,
    entity_type: str,
    approval_stage: str,
    required_role: str,
    assigned_to: Optional[str] = None,
    due_date: Optional[str] = None,
    db: Session = Depends(get_db),
):
    """Create approval step"""
    try:
        service = ApprovalService(db)
        due_dt = datetime.fromisoformat(due_date) if due_date else None
        result = service.create_approval(
            entity_id=UUID(entity_id),
            entity_type=entity_type,
            approval_stage=approval_stage,
            required_role=required_role,
            assigned_to=UUID(assigned_to) if assigned_to else None,
            due_date=due_dt,
        )
        return {"success": True, "data": result}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/approvals/pending")
async def list_pending_approvals(
    assigned_to: Optional[str] = None,
    entity_type: Optional[str] = None,
    db: Session = Depends(get_db),
):
    """List pending approvals"""
    try:
        service = ApprovalService(db)
        assigned_uuid = UUID(assigned_to) if assigned_to else None
        result = service.get_pending_approvals(assigned_uuid, entity_type)
        return {"success": True, "data": result}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.patch("/approvals/{approval_id}")
async def submit_approval(
    approval_id: str,
    decision: str,
    comment: Optional[str] = None,
    db: Session = Depends(get_db),
    x_user_id: str = Header(None),
):
    """Submit approval decision"""
    try:
        service = ApprovalService(db)
        result = service.submit_approval(
            approval_id=UUID(approval_id),
            decision=decision,
            comment=comment,
            completed_by=UUID(x_user_id),
        )
        return {"success": True, "data": result}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/approvals/{approval_id}/assign")
async def assign_approval(
    approval_id: str,
    assign_to: str,
    db: Session = Depends(get_db),
):
    """Assign approval to user"""
    try:
        service = ApprovalService(db)
        result = service.assign_approval(UUID(approval_id), UUID(assign_to))
        return {"success": True, "data": result}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/approvals/{approval_id}/due-date")
async def set_approval_due_date(
    approval_id: str,
    due_date: str,
    db: Session = Depends(get_db),
):
    """Set approval due date"""
    try:
        service = ApprovalService(db)
        due_dt = datetime.fromisoformat(due_date)
        result = service.set_due_date(UUID(approval_id), due_dt)
        return {"success": True, "data": result}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# ============================================================================
# Approval Comments Endpoints
# ============================================================================


@router.post("/approvals/{approval_id}/comments")
async def add_approval_comment(
    approval_id: str,
    comment_text: str,
    comment_type: str = "comment",
    db: Session = Depends(get_db),
    x_user_id: str = Header(None),
):
    """Add comment to approval"""
    try:
        service = ApprovalCommentService(db)
        result = service.add_comment(
            approval_id=UUID(approval_id),
            comment_text=comment_text,
            commented_by=UUID(x_user_id),
            comment_type=comment_type,
        )
        return {"success": True, "data": result}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/approvals/{approval_id}/comments")
async def get_approval_comments(
    approval_id: str,
    db: Session = Depends(get_db),
):
    """Get approval discussion thread"""
    try:
        service = ApprovalCommentService(db)
        result = service.get_discussion_thread(UUID(approval_id))
        return {"success": True, "data": result}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# ============================================================================
# Escalation Endpoints
# ============================================================================


@router.get("/approvals/overdue")
async def get_overdue_approvals(
    days: int = 0,
    db: Session = Depends(get_db),
):
    """Get overdue approvals"""
    try:
        service = EscalationService(db)
        result = service.get_overdue_approvals(days)
        return {"success": True, "data": result}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/approvals/{approval_id}/escalate")
async def escalate_approval(
    approval_id: str,
    escalate_to: str,
    reason: str,
    db: Session = Depends(get_db),
):
    """Escalate approval"""
    try:
        service = EscalationService(db)
        result = service.escalate_approval(
            approval_id=UUID(approval_id),
            escalate_to=UUID(escalate_to),
            reason=reason,
        )
        return {"success": True, "data": result}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/approvals/escalation-check")
async def check_escalations(
    days: int = 7,
    db: Session = Depends(get_db),
    x_tenant_id: str = Header(None),
):
    """Check for approvals needing escalation"""
    try:
        service = EscalationService(db)
        result = service.check_approvals_for_escalation(UUID(x_tenant_id), days)
        return {"success": True, "data": result}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
