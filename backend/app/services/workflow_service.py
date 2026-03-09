"""
Service layer for workflow and approval management

Services:
- WorkflowService: Workflow state management and transitions
- ApprovalService: Approval creation, assignment, completion
- ApprovalCommentService: Discussion and comment threads
- EscalationService: Auto-escalation on deadlines
"""

from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from uuid import UUID
from typing import List, Dict, Optional

from app.models import (
    WorkflowState,
    Approval,
    ApprovalComment,
    WorkflowConfig,
    User,
)


class WorkflowService:
    """Service for workflow state management"""

    def __init__(self, db: Session):
        self.db = db

    def create_workflow(
        self,
        entity_id: UUID,
        entity_type: str,
        initial_state: str,
        changed_by: UUID,
    ) -> Dict:
        """Create new workflow state"""
        workflow = WorkflowState(
            entity_id=entity_id,
            entity_type=entity_type,
            current_state=initial_state,
            changed_by=changed_by,
            change_reason="Initial workflow creation",
        )
        self.db.add(workflow)
        self.db.commit()

        return {
            "id": str(workflow.id),
            "entity_id": str(entity_id),
            "entity_type": entity_type,
            "current_state": initial_state,
            "changed_at": workflow.state_changed_at.isoformat(),
        }

    def transition_state(
        self,
        entity_id: UUID,
        entity_type: str,
        new_state: str,
        changed_by: UUID,
        reason: Optional[str] = None,
    ) -> Dict:
        """Transition workflow to new state"""
        workflow = (
            self.db.query(WorkflowState)
            .filter(WorkflowState.entity_id == entity_id, WorkflowState.entity_type == entity_type)
            .first()
        )
        if not workflow:
            raise ValueError(f"Workflow not found for {entity_type} {entity_id}")

        previous_state = workflow.current_state
        workflow.previous_state = previous_state
        workflow.current_state = new_state
        workflow.changed_by = changed_by
        workflow.change_reason = reason or f"Transitioned from {previous_state} to {new_state}"
        workflow.state_changed_at = datetime.utcnow()

        self.db.commit()

        return {
            "entity_id": str(entity_id),
            "previous_state": previous_state,
            "current_state": new_state,
            "changed_at": workflow.state_changed_at.isoformat(),
        }

    def get_workflow(self, entity_id: UUID, entity_type: str) -> Dict:
        """Get workflow status"""
        workflow = (
            self.db.query(WorkflowState)
            .filter(WorkflowState.entity_id == entity_id, WorkflowState.entity_type == entity_type)
            .first()
        )
        if not workflow:
            raise ValueError(f"Workflow not found")

        return {
            "entity_id": str(entity_id),
            "entity_type": entity_type,
            "current_state": workflow.current_state,
            "previous_state": workflow.previous_state,
            "changed_at": workflow.state_changed_at.isoformat(),
            "changed_by": str(workflow.changed_by) if workflow.changed_by else None,
        }

    def get_workflow_history(self, entity_id: UUID, entity_type: str) -> List[Dict]:
        """Get workflow state history"""
        states = (
            self.db.query(WorkflowState)
            .filter(WorkflowState.entity_id == entity_id, WorkflowState.entity_type == entity_type)
            .order_by(WorkflowState.state_changed_at.desc())
            .all()
        )

        return [
            {
                "state": s.current_state,
                "previous_state": s.previous_state,
                "changed_at": s.state_changed_at.isoformat(),
                "changed_by": str(s.changed_by) if s.changed_by else None,
                "reason": s.change_reason,
            }
            for s in states
        ]


class ApprovalService:
    """Service for managing approvals"""

    def __init__(self, db: Session):
        self.db = db

    def create_approval(
        self,
        entity_id: UUID,
        entity_type: str,
        approval_stage: str,
        required_role: str,
        assigned_to: Optional[UUID] = None,
        due_date: Optional[datetime] = None,
    ) -> Dict:
        """Create approval step"""
        approval = Approval(
            entity_id=entity_id,
            entity_type=entity_type,
            approval_stage=approval_stage,
            required_role=required_role,
            assigned_to=assigned_to,
            due_date=due_date,
            status="pending",
        )
        self.db.add(approval)
        self.db.commit()

        return {
            "id": str(approval.id),
            "approval_stage": approval_stage,
            "status": "pending",
            "assigned_to": str(assigned_to) if assigned_to else None,
        }

    def submit_approval(
        self,
        approval_id: UUID,
        decision: str,
        comment: Optional[str] = None,
        completed_by: Optional[UUID] = None,
    ) -> Dict:
        """Submit approval decision"""
        approval = self.db.query(Approval).filter(Approval.id == approval_id).first()
        if not approval:
            raise ValueError(f"Approval {approval_id} not found")

        approval.status = decision  # approve, reject, request_changes
        approval.decision = decision
        approval.comment_summary = comment
        approval.completed_date = datetime.utcnow()
        approval.completed_by = completed_by

        self.db.commit()

        return {
            "id": str(approval.id),
            "status": decision,
            "completed_at": approval.completed_date.isoformat(),
        }

    def get_pending_approvals(
        self,
        assigned_to: Optional[UUID] = None,
        entity_type: Optional[str] = None,
    ) -> List[Dict]:
        """Get pending approvals"""
        query = self.db.query(Approval).filter(Approval.status == "pending")

        if assigned_to:
            query = query.filter(Approval.assigned_to == assigned_to)
        if entity_type:
            query = query.filter(Approval.entity_type == entity_type)

        approvals = query.order_by(Approval.due_date).all()

        return [
            {
                "id": str(a.id),
                "entity_id": str(a.entity_id),
                "entity_type": a.entity_type,
                "approval_stage": a.approval_stage,
                "assigned_to": str(a.assigned_to) if a.assigned_to else None,
                "due_date": a.due_date.isoformat() if a.due_date else None,
                "created_at": a.created_at.isoformat(),
            }
            for a in approvals
        ]

    def assign_approval(self, approval_id: UUID, assign_to: UUID) -> Dict:
        """Assign approval to user"""
        approval = self.db.query(Approval).filter(Approval.id == approval_id).first()
        if not approval:
            raise ValueError(f"Approval {approval_id} not found")

        approval.assigned_to = assign_to
        self.db.commit()

        return {
            "id": str(approval.id),
            "assigned_to": str(assign_to),
        }

    def set_due_date(self, approval_id: UUID, due_date: datetime) -> Dict:
        """Set approval due date"""
        approval = self.db.query(Approval).filter(Approval.id == approval_id).first()
        if not approval:
            raise ValueError(f"Approval {approval_id} not found")

        approval.due_date = due_date
        self.db.commit()

        return {
            "id": str(approval.id),
            "due_date": due_date.isoformat(),
        }


class ApprovalCommentService:
    """Service for approval comments and discussion"""

    def __init__(self, db: Session):
        self.db = db

    def add_comment(
        self,
        approval_id: UUID,
        comment_text: str,
        commented_by: UUID,
        comment_type: str = "comment",
    ) -> Dict:
        """Add comment to approval"""
        comment = ApprovalComment(
            approval_id=approval_id,
            comment_text=comment_text,
            comment_type=comment_type,
            commented_by=commented_by,
        )
        self.db.add(comment)
        self.db.commit()

        return {
            "id": str(comment.id),
            "approval_id": str(approval_id),
            "comment_type": comment_type,
            "created_at": comment.created_at.isoformat(),
        }

    def get_approval_comments(self, approval_id: UUID) -> List[Dict]:
        """Get all comments for approval"""
        comments = (
            self.db.query(ApprovalComment)
            .filter(ApprovalComment.approval_id == approval_id)
            .order_by(ApprovalComment.created_at)
            .all()
        )

        return [
            {
                "id": str(c.id),
                "text": c.comment_text,
                "type": c.comment_type,
                "commented_by": str(c.commented_by) if c.commented_by else None,
                "created_at": c.created_at.isoformat(),
            }
            for c in comments
        ]

    def get_discussion_thread(self, approval_id: UUID) -> Dict:
        """Get complete discussion thread"""
        approval = self.db.query(Approval).filter(Approval.id == approval_id).first()
        if not approval:
            raise ValueError(f"Approval {approval_id} not found")

        comments = self.get_approval_comments(approval_id)

        return {
            "approval_id": str(approval_id),
            "entity_id": str(approval.entity_id),
            "approval_stage": approval.approval_stage,
            "status": approval.status,
            "comment_count": len(comments),
            "comments": comments,
        }


class EscalationService:
    """Service for approval escalation"""

    def __init__(self, db: Session):
        self.db = db

    def get_overdue_approvals(self, days_overdue: int = 0) -> List[Dict]:
        """Get approvals overdue by N days"""
        cutoff_date = datetime.utcnow() - timedelta(days=days_overdue)

        approvals = (
            self.db.query(Approval)
            .filter(
                Approval.status == "pending",
                Approval.due_date.isnot(None),
                Approval.due_date <= cutoff_date,
            )
            .order_by(Approval.due_date)
            .all()
        )

        return [
            {
                "id": str(a.id),
                "entity_id": str(a.entity_id),
                "approval_stage": a.approval_stage,
                "assigned_to": str(a.assigned_to) if a.assigned_to else None,
                "due_date": a.due_date.isoformat(),
                "days_overdue": (datetime.utcnow() - a.due_date).days,
            }
            for a in approvals
        ]

    def escalate_approval(
        self,
        approval_id: UUID,
        escalate_to: UUID,
        reason: str,
    ) -> Dict:
        """Escalate approval to different user"""
        approval = self.db.query(Approval).filter(Approval.id == approval_id).first()
        if not approval:
            raise ValueError(f"Approval {approval_id} not found")

        # Add escalation comment
        comment_service = ApprovalCommentService(self.db)
        comment_service.add_comment(
            approval_id=approval_id,
            comment_text=f"Escalated: {reason}",
            commented_by=escalate_to,
            comment_type="escalation",
        )

        # Reassign
        approval.assigned_to = escalate_to
        self.db.commit()

        return {
            "id": str(approval.id),
            "escalated_to": str(escalate_to),
            "escalation_reason": reason,
        }

    def check_approvals_for_escalation(self, tenant_id: UUID, auto_escalate_days: int = 7) -> List[Dict]:
        """Check for approvals needing escalation"""
        escalation_date = datetime.utcnow() - timedelta(days=auto_escalate_days)

        approvals = (
            self.db.query(Approval)
            .filter(
                Approval.status == "pending",
                Approval.created_at <= escalation_date,
            )
            .all()
        )

        escalations = []
        for approval in approvals:
            escalations.append({
                "approval_id": str(approval.id),
                "entity_id": str(approval.entity_id),
                "needs_escalation": True,
                "days_pending": (datetime.utcnow() - approval.created_at).days,
            })

        return escalations
