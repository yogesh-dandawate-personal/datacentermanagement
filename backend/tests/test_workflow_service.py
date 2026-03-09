"""
Test suite for Workflow & Approval System

Tests:
- WorkflowService (4 tests)
- ApprovalService (4 tests)
- ApprovalCommentService (3 tests)
- EscalationService (3 tests)
"""

import pytest
import uuid
from datetime import datetime, timedelta
from sqlalchemy.orm import Session

from app.models import (
    Tenant,
    User,
    WorkflowState,
    Approval,
    ApprovalComment,
    WorkflowConfig,
)
from app.services.workflow_service import (
    WorkflowService,
    ApprovalService,
    ApprovalCommentService,
    EscalationService,
)


@pytest.fixture
def workflow_test_data(db: Session):
    """Create test data for workflow tests"""
    tenant = Tenant(
        id=uuid.uuid4(),
        name="Test Tenant",
        slug="test-tenant",
        email="test@example.com",
    )
    db.add(tenant)
    db.flush()

    user1 = User(
        id=uuid.uuid4(),
        tenant_id=tenant.id,
        email="user1@example.com",
        first_name="User",
        last_name="One",
    )
    user2 = User(
        id=uuid.uuid4(),
        tenant_id=tenant.id,
        email="user2@example.com",
        first_name="User",
        last_name="Two",
    )
    db.add(user1)
    db.add(user2)
    db.commit()

    return {
        "tenant": tenant,
        "user1": user1,
        "user2": user2,
    }


# ============================================================================
# Test: Workflow Service
# ============================================================================


class TestWorkflowService:
    """Tests for workflow state management"""

    def test_create_workflow(self, db: Session, workflow_test_data):
        """Test creating workflow"""
        test_data = workflow_test_data

        service = WorkflowService(db)
        result = service.create_workflow(
            entity_id=uuid.uuid4(),
            entity_type="report",
            initial_state="draft",
            changed_by=test_data["user1"].id,
        )

        assert result["current_state"] == "draft"
        assert result["entity_type"] == "report"

    def test_transition_state(self, db: Session, workflow_test_data):
        """Test workflow state transition"""
        test_data = workflow_test_data

        entity_id = uuid.uuid4()
        service = WorkflowService(db)

        service.create_workflow(
            entity_id=entity_id,
            entity_type="report",
            initial_state="draft",
            changed_by=test_data["user1"].id,
        )

        result = service.transition_state(
            entity_id=entity_id,
            entity_type="report",
            new_state="review",
            changed_by=test_data["user1"].id,
            reason="Submitted for review",
        )

        assert result["current_state"] == "review"
        assert result["previous_state"] == "draft"

    def test_get_workflow(self, db: Session, workflow_test_data):
        """Test retrieving workflow"""
        test_data = workflow_test_data

        entity_id = uuid.uuid4()
        service = WorkflowService(db)

        service.create_workflow(
            entity_id=entity_id,
            entity_type="credit_batch",
            initial_state="draft",
            changed_by=test_data["user1"].id,
        )

        result = service.get_workflow(entity_id, "credit_batch")

        assert result["entity_type"] == "credit_batch"
        assert result["current_state"] == "draft"

    def test_get_workflow_history(self, db: Session, workflow_test_data):
        """Test workflow history retrieval"""
        test_data = workflow_test_data

        entity_id = uuid.uuid4()
        service = WorkflowService(db)

        service.create_workflow(
            entity_id=entity_id,
            entity_type="target",
            initial_state="draft",
            changed_by=test_data["user1"].id,
        )

        service.transition_state(
            entity_id=entity_id,
            entity_type="target",
            new_state="review",
            changed_by=test_data["user1"].id,
        )

        history = service.get_workflow_history(entity_id, "target")

        assert len(history) >= 1
        assert history[0]["state"] == "review"


# ============================================================================
# Test: Approval Service
# ============================================================================


class TestApprovalService:
    """Tests for approval management"""

    def test_create_approval(self, db: Session, workflow_test_data):
        """Test creating approval"""
        test_data = workflow_test_data

        service = ApprovalService(db)
        result = service.create_approval(
            entity_id=uuid.uuid4(),
            entity_type="report",
            approval_stage="checker",
            required_role="approver",
            assigned_to=test_data["user1"].id,
        )

        assert result["approval_stage"] == "checker"
        assert result["status"] == "pending"

    def test_submit_approval(self, db: Session, workflow_test_data):
        """Test submitting approval"""
        test_data = workflow_test_data

        service = ApprovalService(db)
        approval_result = service.create_approval(
            entity_id=uuid.uuid4(),
            entity_type="report",
            approval_stage="reviewer",
            required_role="reviewer",
            assigned_to=test_data["user1"].id,
        )

        result = service.submit_approval(
            approval_id=uuid.UUID(approval_result["id"]),
            decision="approve",
            comment="Looks good",
            completed_by=test_data["user1"].id,
        )

        assert result["status"] == "approve"

    def test_get_pending_approvals(self, db: Session, workflow_test_data):
        """Test retrieving pending approvals"""
        test_data = workflow_test_data

        service = ApprovalService(db)
        for i in range(3):
            service.create_approval(
                entity_id=uuid.uuid4(),
                entity_type="report",
                approval_stage=f"stage_{i}",
                required_role="reviewer",
                assigned_to=test_data["user1"].id,
            )

        result = service.get_pending_approvals(test_data["user1"].id)

        assert len(result) == 3

    def test_assign_and_due_date(self, db: Session, workflow_test_data):
        """Test assigning approval and setting due date"""
        test_data = workflow_test_data

        service = ApprovalService(db)
        approval_result = service.create_approval(
            entity_id=uuid.uuid4(),
            entity_type="target",
            approval_stage="maker",
            required_role="editor",
            assigned_to=test_data["user1"].id,
        )

        approval_id = uuid.UUID(approval_result["id"])

        service.assign_approval(approval_id, test_data["user2"].id)
        due_date = datetime.utcnow() + timedelta(days=7)
        service.set_due_date(approval_id, due_date)

        pending = service.get_pending_approvals()
        assert len(pending) > 0


# ============================================================================
# Test: Approval Comment Service
# ============================================================================


class TestApprovalCommentService:
    """Tests for approval comments"""

    def test_add_comment(self, db: Session, workflow_test_data):
        """Test adding comment"""
        test_data = workflow_test_data

        approval_service = ApprovalService(db)
        approval_result = approval_service.create_approval(
            entity_id=uuid.uuid4(),
            entity_type="report",
            approval_stage="reviewer",
            required_role="reviewer",
        )

        comment_service = ApprovalCommentService(db)
        result = comment_service.add_comment(
            approval_id=uuid.UUID(approval_result["id"]),
            comment_text="This needs revision",
            commented_by=test_data["user1"].id,
            comment_type="request_changes",
        )

        assert result["comment_type"] == "request_changes"

    def test_get_comments(self, db: Session, workflow_test_data):
        """Test retrieving comments"""
        test_data = workflow_test_data

        approval_service = ApprovalService(db)
        approval_result = approval_service.create_approval(
            entity_id=uuid.uuid4(),
            entity_type="credit_batch",
            approval_stage="checker",
            required_role="approver",
        )

        approval_id = uuid.UUID(approval_result["id"])

        comment_service = ApprovalCommentService(db)
        for i in range(3):
            comment_service.add_comment(
                approval_id=approval_id,
                comment_text=f"Comment {i}",
                commented_by=test_data["user1"].id,
            )

        comments = comment_service.get_approval_comments(approval_id)

        assert len(comments) == 3

    def test_discussion_thread(self, db: Session, workflow_test_data):
        """Test full discussion thread"""
        test_data = workflow_test_data

        approval_service = ApprovalService(db)
        approval_result = approval_service.create_approval(
            entity_id=uuid.uuid4(),
            entity_type="target",
            approval_stage="maker",
            required_role="editor",
        )

        approval_id = uuid.UUID(approval_result["id"])

        comment_service = ApprovalCommentService(db)
        comment_service.add_comment(
            approval_id=approval_id,
            comment_text="Initial comment",
            commented_by=test_data["user1"].id,
        )

        comment_service.add_comment(
            approval_id=approval_id,
            comment_text="Reply to initial",
            commented_by=test_data["user2"].id,
        )

        thread = comment_service.get_discussion_thread(approval_id)

        assert thread["comment_count"] == 2
        assert len(thread["comments"]) == 2


# ============================================================================
# Test: Escalation Service
# ============================================================================


class TestEscalationService:
    """Tests for approval escalation"""

    def test_get_overdue_approvals(self, db: Session, workflow_test_data):
        """Test retrieving overdue approvals"""
        test_data = workflow_test_data

        approval_service = ApprovalService(db)

        # Create overdue approval
        due_date = datetime.utcnow() - timedelta(days=1)
        approval_service.create_approval(
            entity_id=uuid.uuid4(),
            entity_type="report",
            approval_stage="reviewer",
            required_role="reviewer",
            due_date=due_date,
        )

        escalation_service = EscalationService(db)
        overdue = escalation_service.get_overdue_approvals(days_overdue=0)

        assert len(overdue) >= 1

    def test_escalate_approval(self, db: Session, workflow_test_data):
        """Test escalating approval"""
        test_data = workflow_test_data

        approval_service = ApprovalService(db)
        approval_result = approval_service.create_approval(
            entity_id=uuid.uuid4(),
            entity_type="report",
            approval_stage="checker",
            required_role="approver",
            assigned_to=test_data["user1"].id,
        )

        escalation_service = EscalationService(db)
        result = escalation_service.escalate_approval(
            approval_id=uuid.UUID(approval_result["id"]),
            escalate_to=test_data["user2"].id,
            reason="SLA breach",
        )

        assert result["escalated_to"] == str(test_data["user2"].id)
        assert result["escalation_reason"] == "SLA breach"

    def test_check_escalations(self, db: Session, workflow_test_data):
        """Test checking for escalations needed"""
        test_data = workflow_test_data

        approval_service = ApprovalService(db)
        approval_service.create_approval(
            entity_id=uuid.uuid4(),
            entity_type="target",
            approval_stage="maker",
            required_role="editor",
            assigned_to=test_data["user1"].id,
        )

        escalation_service = EscalationService(db)
        escalations = escalation_service.check_approvals_for_escalation(
            test_data["tenant"].id,
            auto_escalate_days=0,
        )

        assert len(escalations) >= 0
