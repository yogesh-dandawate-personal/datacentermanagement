"""
Service layer for compliance reporting and auditing

Services:
- ComplianceReportService: Report creation, generation, export, approval
- AuditTrailService: Audit logging and compliance trail tracking
- ComplianceTargetService: Target setting, progress tracking, forecasting
- BenchmarkingService: Benchmark calculation and peer comparison
"""

from sqlalchemy.orm import Session
from decimal import Decimal
from datetime import datetime, timedelta
from uuid import UUID
from typing import List, Dict, Optional

from app.models import (
    ComplianceReport,
    ReportSection,
    ComplianceAuditTrail,
    ComplianceTarget,
    ReportingBenchmark,
    Organization,
    Tenant,
)


class ComplianceReportService:
    """Service for managing compliance reports"""

    def __init__(self, db: Session):
        self.db = db

    def create_report(
        self,
        organization_id: UUID,
        tenant_id: UUID,
        report_type: str,
        reporting_period: str,
        fiscal_year: int,
        created_by: UUID,
    ) -> Dict:
        """Create a new compliance report"""
        report = ComplianceReport(
            organization_id=organization_id,
            tenant_id=tenant_id,
            report_type=report_type,
            reporting_period=reporting_period,
            fiscal_year=fiscal_year,
            created_by=created_by,
            status="draft",
        )
        self.db.add(report)
        self.db.commit()

        return {
            "id": str(report.id),
            "organization_id": str(organization_id),
            "report_type": report_type,
            "status": "draft",
            "fiscal_year": fiscal_year,
            "created_at": report.created_at.isoformat(),
        }

    def generate_report_data(
        self, report_id: UUID, scope_1: Decimal, scope_2: Decimal, scope_3: Decimal
    ) -> Dict:
        """Generate report data with emissions calculations"""
        report = self.db.query(ComplianceReport).filter(ComplianceReport.id == report_id).first()
        if not report:
            raise ValueError(f"Report {report_id} not found")

        report.scope_1_emissions = scope_1
        report.scope_2_emissions = scope_2
        report.scope_3_emissions = scope_3
        self.db.commit()

        total_emissions = (scope_1 or Decimal(0)) + (scope_2 or Decimal(0)) + (scope_3 or Decimal(0))

        return {
            "report_id": str(report_id),
            "scope_1": float(scope_1) if scope_1 else 0,
            "scope_2": float(scope_2) if scope_2 else 0,
            "scope_3": float(scope_3) if scope_3 else 0,
            "total_emissions": float(total_emissions),
            "unit": "metric_tonnes_co2e",
        }

    def export_report(self, report_id: UUID, export_format: str) -> Dict:
        """Export report in specified format"""
        report = self.db.query(ComplianceReport).filter(ComplianceReport.id == report_id).first()
        if not report:
            raise ValueError(f"Report {report_id} not found")

        report_data = {
            "id": str(report.id),
            "report_type": report.report_type,
            "fiscal_year": report.fiscal_year,
            "status": report.status,
            "scope_1_emissions": float(report.scope_1_emissions) if report.scope_1_emissions else 0,
            "scope_2_emissions": float(report.scope_2_emissions) if report.scope_2_emissions else 0,
            "scope_3_emissions": float(report.scope_3_emissions) if report.scope_3_emissions else 0,
            "sections": [
                {
                    "name": s.section_name,
                    "completion": s.completion_percentage,
                    "reviewed": s.reviewed_at is not None,
                }
                for s in report.sections
            ],
        }

        return {
            "format": export_format,
            "status": "generated",
            "report_data": report_data,
            "export_timestamp": datetime.utcnow().isoformat(),
        }

    def submit_for_approval(self, report_id: UUID, submitted_by: UUID) -> Dict:
        """Submit report for approval"""
        report = self.db.query(ComplianceReport).filter(ComplianceReport.id == report_id).first()
        if not report:
            raise ValueError(f"Report {report_id} not found")

        report.status = "pending_review"
        report.submitted_by = submitted_by
        report.submitted_at = datetime.utcnow()
        self.db.commit()

        return {
            "id": str(report.id),
            "status": "pending_review",
            "submitted_at": report.submitted_at.isoformat(),
        }

    def approve_report(self, report_id: UUID, approved_by: UUID) -> Dict:
        """Approve report"""
        report = self.db.query(ComplianceReport).filter(ComplianceReport.id == report_id).first()
        if not report:
            raise ValueError(f"Report {report_id} not found")

        report.status = "approved"
        report.approved_by = approved_by
        report.approved_at = datetime.utcnow()
        self.db.commit()

        return {
            "id": str(report.id),
            "status": "approved",
            "approved_at": report.approved_at.isoformat(),
        }

    def get_report_history(self, organization_id: UUID) -> List[Dict]:
        """Get report history for organization"""
        reports = (
            self.db.query(ComplianceReport)
            .filter(ComplianceReport.organization_id == organization_id)
            .order_by(ComplianceReport.created_at.desc())
            .all()
        )

        return [
            {
                "id": str(r.id),
                "report_type": r.report_type,
                "fiscal_year": r.fiscal_year,
                "status": r.status,
                "created_at": r.created_at.isoformat(),
                "submitted_at": r.submitted_at.isoformat() if r.submitted_at else None,
            }
            for r in reports
        ]


class AuditTrailService:
    """Service for compliance audit trail tracking"""

    def __init__(self, db: Session):
        self.db = db

    def log_action(
        self,
        organization_id: UUID,
        tenant_id: UUID,
        action: str,
        action_category: str,
        entity_type: str,
        entity_id: Optional[UUID],
        changed_by_user_id: UUID,
        changed_values: Optional[Dict] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
    ) -> Dict:
        """Log an action to the audit trail"""
        audit_entry = ComplianceAuditTrail(
            organization_id=organization_id,
            tenant_id=tenant_id,
            action=action,
            action_category=action_category,
            entity_type=entity_type,
            entity_id=entity_id,
            changed_values=changed_values or {},
            changed_by_user_id=changed_by_user_id,
            ip_address=ip_address,
            user_agent=user_agent,
        )
        self.db.add(audit_entry)
        self.db.commit()

        return {
            "id": str(audit_entry.id),
            "action": action,
            "entity_type": entity_type,
            "timestamp": audit_entry.timestamp.isoformat(),
        }

    def get_audit_trail(self, organization_id: UUID, days: int = 90) -> List[Dict]:
        """Get audit trail for organization over specified days"""
        since = datetime.utcnow() - timedelta(days=days)

        entries = (
            self.db.query(ComplianceAuditTrail)
            .filter(
                ComplianceAuditTrail.organization_id == organization_id,
                ComplianceAuditTrail.timestamp >= since,
            )
            .order_by(ComplianceAuditTrail.timestamp.desc())
            .all()
        )

        return [
            {
                "id": str(e.id),
                "action": e.action,
                "entity_type": e.entity_type,
                "entity_id": str(e.entity_id) if e.entity_id else None,
                "changed_by_user_id": str(e.changed_by_user_id) if e.changed_by_user_id else None,
                "timestamp": e.timestamp.isoformat(),
                "changed_values": e.changed_values,
            }
            for e in entries
        ]

    def generate_compliance_certificate(self, organization_id: UUID, report_id: UUID) -> Dict:
        """Generate compliance certificate for approved report"""
        report = self.db.query(ComplianceReport).filter(ComplianceReport.id == report_id).first()
        if not report or report.status != "approved":
            raise ValueError("Report not found or not approved")

        certificate = {
            "certificate_id": f"CERT-{report.fiscal_year}-{organization_id}",
            "organization_id": str(organization_id),
            "report_id": str(report_id),
            "report_type": report.report_type,
            "fiscal_year": report.fiscal_year,
            "approved_at": report.approved_at.isoformat(),
            "valid_until": (report.approved_at + timedelta(days=365)).isoformat(),
            "total_emissions_mtco2e": float(
                (report.scope_1_emissions or Decimal(0))
                + (report.scope_2_emissions or Decimal(0))
                + (report.scope_3_emissions or Decimal(0))
            ),
            "status": "valid",
        }

        return certificate


class ComplianceTargetService:
    """Service for managing compliance targets"""

    def __init__(self, db: Session):
        self.db = db

    def set_target(
        self,
        organization_id: UUID,
        tenant_id: UUID,
        target_name: str,
        target_type: str,
        baseline_year: int,
        baseline_value: Decimal,
        target_year: int,
        target_value: Decimal,
    ) -> Dict:
        """Set a new compliance target"""
        target = ComplianceTarget(
            organization_id=organization_id,
            tenant_id=tenant_id,
            target_name=target_name,
            target_type=target_type,
            baseline_year=baseline_year,
            baseline_value=baseline_value,
            target_year=target_year,
            target_value=target_value,
            status="on_track",
            progress_percentage=0,
        )
        self.db.add(target)
        self.db.commit()

        return {
            "id": str(target.id),
            "target_name": target_name,
            "baseline_year": baseline_year,
            "target_year": target_year,
            "status": "on_track",
        }

    def track_progress(self, target_id: UUID, current_value: Decimal) -> Dict:
        """Track progress towards target"""
        target = self.db.query(ComplianceTarget).filter(ComplianceTarget.id == target_id).first()
        if not target:
            raise ValueError(f"Target {target_id} not found")

        # Calculate progress percentage
        if target.target_type == "absolute_reduction":
            reduction = target.baseline_value - current_value
            total_reduction = target.baseline_value - target.target_value
            progress = float((reduction / total_reduction * 100)) if total_reduction > 0 else 0
        else:  # intensity_reduction or net_zero
            progress = float((current_value / target.baseline_value * 100))

        progress_pct = min(100, max(0, int(progress)))
        target.progress_percentage = progress_pct

        # Update status based on actual progress (simplified: on_track if making progress)
        target.status = "on_track" if progress_pct > 0 else "at_risk"

        self.db.commit()

        return {
            "target_id": str(target_id),
            "progress_percentage": progress_pct,
            "status": target.status,
            "current_value": float(current_value),
        }

    def get_target_status(self, target_id: UUID) -> Dict:
        """Get target status"""
        target = self.db.query(ComplianceTarget).filter(ComplianceTarget.id == target_id).first()
        if not target:
            raise ValueError(f"Target {target_id} not found")

        return {
            "id": str(target.id),
            "target_name": target.target_name,
            "target_type": target.target_type,
            "baseline_year": target.baseline_year,
            "target_year": target.target_year,
            "progress_percentage": target.progress_percentage,
            "status": target.status,
            "verification_status": target.verification_status,
        }

    def forecast_achievement(self, target_id: UUID) -> Dict:
        """Forecast target achievement based on current progress"""
        target = self.db.query(ComplianceTarget).filter(ComplianceTarget.id == target_id).first()
        if not target:
            raise ValueError(f"Target {target_id} not found")

        years_remaining = target.target_year - datetime.utcnow().year
        current_progress_rate = target.progress_percentage / max(1, datetime.utcnow().year - target.baseline_year)
        projected_progress = target.progress_percentage + (current_progress_rate * years_remaining)

        will_achieve = projected_progress >= 100

        return {
            "target_id": str(target_id),
            "will_achieve": will_achieve,
            "projected_progress": min(100, int(projected_progress)),
            "years_remaining": years_remaining,
            "confidence": "high" if will_achieve else "medium" if projected_progress >= 80 else "low",
        }


class BenchmarkingService:
    """Service for benchmarking and peer comparison"""

    def __init__(self, db: Session):
        self.db = db

    def calculate_benchmarks(
        self, tenant_id: UUID, metric_name: str, benchmark_value: Decimal, organization_value: Decimal = None
    ) -> Dict:
        """Calculate and record benchmarks"""
        benchmark = ReportingBenchmark(
            tenant_id=tenant_id,
            benchmark_name="industry_average",
            metric_name=metric_name,
            benchmark_category="organization",
            benchmark_value=benchmark_value,
            organization_value=organization_value,
            data_year=datetime.utcnow().year,
        )
        self.db.add(benchmark)
        self.db.commit()

        # Calculate percentile if organization value provided
        percentile = None
        if organization_value:
            percentile = int((organization_value / benchmark_value * 100)) if benchmark_value > 0 else 0

        return {
            "id": str(benchmark.id),
            "metric_name": metric_name,
            "benchmark_value": float(benchmark_value),
            "organization_value": float(organization_value) if organization_value else None,
            "percentile_rank": percentile,
        }

    def get_peer_comparison(self, tenant_id: UUID, metric_name: str) -> Dict:
        """Get peer comparison data"""
        benchmarks = (
            self.db.query(ReportingBenchmark)
            .filter(
                ReportingBenchmark.tenant_id == tenant_id,
                ReportingBenchmark.metric_name == metric_name,
            )
            .all()
        )

        if not benchmarks:
            return {"metric_name": metric_name, "comparison": "No benchmark data available"}

        avg_benchmark = float(sum(float(b.benchmark_value) for b in benchmarks) / len(benchmarks))
        org_value = float(benchmarks[0].organization_value) if benchmarks[0].organization_value else None

        percentile = None
        if org_value and avg_benchmark > 0:
            percentile = int((org_value / avg_benchmark * 100))

        return {
            "metric_name": metric_name,
            "organization_value": org_value,
            "industry_average": avg_benchmark,
            "percentile_rank": percentile,
            "benchmark_count": len(benchmarks),
        }

    def generate_insights(self, tenant_id: UUID) -> Dict:
        """Generate benchmark insights and recommendations"""
        benchmarks = self.db.query(ReportingBenchmark).filter(ReportingBenchmark.tenant_id == tenant_id).all()

        if not benchmarks:
            return {"status": "insufficient_data", "insights": []}

        below_average = [b for b in benchmarks if b.organization_value and b.organization_value < b.benchmark_value]

        insights = {
            "total_metrics": len(set(b.metric_name for b in benchmarks)),
            "metrics_below_average": len(below_average),
            "top_improvement_areas": [b.metric_name for b in below_average[:3]],
            "recommendations": [f"Improve {b.metric_name} (currently {b.organization_value})" for b in below_average],
        }

        return insights
