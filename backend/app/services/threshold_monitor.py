"""
Threshold Monitoring Service
SPRINT 10 - AGENT 4: Threshold Monitoring

Features:
- Configurable thresholds per metric
- Cross-facility threshold comparisons
- Threshold breach detection and logging
- Escalation rules based on severity
- Historical threshold tracking
"""
from typing import List, Dict, Optional
from datetime import datetime, timedelta
from decimal import Decimal
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc
import logging
import uuid

from app.models import (
    KPIThreshold,
    KPIThresholdBreach,
    KPISnapshot,
    KPIDefinition,
    FacilityMetrics,
    Tenant,
)

logger = logging.getLogger(__name__)


class ThresholdConfig:
    """Threshold configuration"""

    def __init__(
        self,
        metric_name: str,
        threshold_value: float,
        operator: str,
        severity: str,
        notify_email: bool = True,
        notify_slack: bool = False,
    ):
        self.metric_name = metric_name
        self.threshold_value = threshold_value
        self.operator = operator  # >, <, >=, <=, ==, !=
        self.severity = severity  # info, warning, critical
        self.notify_email = notify_email
        self.notify_slack = notify_slack


class ThresholdMonitor:
    """
    Monitor metrics against configured thresholds

    Features:
    - Threshold evaluation
    - Breach detection and logging
    - Cross-facility comparisons
    - Escalation handling
    """

    def __init__(self, db: Session):
        self.db = db
        self.breach_cache: Dict[str, datetime] = {}  # Prevent duplicate alerts
        self.cooldown_minutes = 15  # Minimum time between duplicate alerts

    def check_threshold_breach(
        self,
        metric_name: str,
        metric_value: float,
        facility_id: str,
        org_id: str,
        tenant_id: str,
    ) -> List[Dict[str, any]]:
        """
        Check if metric value breaches any thresholds

        Args:
            metric_name: Name of the metric
            metric_value: Current metric value
            facility_id: Facility ID
            org_id: Organization ID
            tenant_id: Tenant ID

        Returns:
            List of breach dictionaries
        """
        breaches = []

        try:
            # Get all active thresholds for this metric
            # Join with KPIDefinition to filter by metric name
            thresholds = (
                self.db.query(KPIThreshold)
                .join(KPIDefinition, KPIThreshold.kpi_id == KPIDefinition.id)
                .filter(
                    and_(
                        KPIDefinition.kpi_name == metric_name,
                        KPIDefinition.tenant_id == tenant_id,
                        KPIThreshold.is_enabled == True,
                    )
                )
                .all()
            )

            for threshold in thresholds:
                is_breach = self._evaluate_threshold(
                    metric_value, threshold.threshold_value, threshold.operator
                )

                if is_breach:
                    # Check cooldown to prevent duplicate alerts
                    cache_key = f"{threshold.id}:{facility_id}"
                    if self._is_in_cooldown(cache_key):
                        logger.debug(f"Breach cooldown active for {cache_key}")
                        continue

                    # Log breach
                    breach = self._log_breach(
                        threshold_id=threshold.id,
                        kpi_id=threshold.kpi_id,
                        metric_value=metric_value,
                        tenant_id=tenant_id,
                    )

                    breaches.append({
                        'threshold_id': str(threshold.id),
                        'threshold_name': threshold.threshold_name,
                        'severity': threshold.alert_severity,
                        'metric_name': metric_name,
                        'metric_value': metric_value,
                        'threshold_value': float(threshold.threshold_value),
                        'operator': threshold.operator,
                        'breach_id': str(breach.id),
                        'facility_id': facility_id,
                        'org_id': org_id,
                    })

                    # Update cooldown cache
                    self.breach_cache[cache_key] = datetime.utcnow()

                    logger.info(
                        f"Threshold breach detected: {metric_name} = {metric_value} "
                        f"{threshold.operator} {threshold.threshold_value}"
                    )

            return breaches

        except Exception as e:
            logger.error(f"Error checking threshold breach: {str(e)}")
            return []

    def configure_threshold(
        self,
        kpi_id: str,
        threshold_config: ThresholdConfig,
    ) -> Optional[str]:
        """
        Configure a new threshold or update existing

        Args:
            kpi_id: KPI Definition ID
            threshold_config: Threshold configuration

        Returns:
            Threshold ID if successful, None otherwise
        """
        try:
            # Check if threshold already exists
            existing = (
                self.db.query(KPIThreshold)
                .filter(
                    and_(
                        KPIThreshold.kpi_id == kpi_id,
                        KPIThreshold.threshold_name == threshold_config.metric_name,
                    )
                )
                .first()
            )

            if existing:
                # Update existing threshold
                existing.threshold_value = Decimal(str(threshold_config.threshold_value))
                existing.operator = threshold_config.operator
                existing.alert_severity = threshold_config.severity
                existing.notify_email = threshold_config.notify_email
                existing.notify_slack = threshold_config.notify_slack
                threshold_id = existing.id
            else:
                # Create new threshold
                threshold = KPIThreshold(
                    id=uuid.uuid4(),
                    kpi_id=kpi_id,
                    threshold_name=threshold_config.metric_name,
                    threshold_value=Decimal(str(threshold_config.threshold_value)),
                    operator=threshold_config.operator,
                    alert_severity=threshold_config.severity,
                    is_enabled=True,
                    notify_email=threshold_config.notify_email,
                    notify_slack=threshold_config.notify_slack,
                    created_at=datetime.utcnow(),
                )
                self.db.add(threshold)
                threshold_id = threshold.id

            self.db.commit()
            logger.info(f"Threshold configured: {threshold_config.metric_name}")
            return str(threshold_id)

        except Exception as e:
            logger.error(f"Error configuring threshold: {str(e)}")
            self.db.rollback()
            return None

    def get_active_breaches(
        self, tenant_id: str, facility_id: Optional[str] = None, severity: Optional[str] = None
    ) -> List[Dict[str, any]]:
        """
        Get all active (unresolved) threshold breaches

        Args:
            tenant_id: Tenant ID
            facility_id: Optional facility filter
            severity: Optional severity filter

        Returns:
            List of active breaches
        """
        try:
            query = (
                self.db.query(KPIThresholdBreach, KPIThreshold, KPIDefinition)
                .join(KPIThreshold, KPIThresholdBreach.threshold_id == KPIThreshold.id)
                .join(KPIDefinition, KPIThresholdBreach.kpi_id == KPIDefinition.id)
                .filter(
                    and_(
                        KPIDefinition.tenant_id == tenant_id,
                        KPIThresholdBreach.status == 'open',
                    )
                )
            )

            if severity:
                query = query.filter(KPIThresholdBreach.severity == severity)

            # Note: facility_id would need to be added to KPISnapshot or tracked separately
            # For now, we'll return all breaches for the tenant

            query = query.order_by(desc(KPIThresholdBreach.created_at))

            results = query.all()

            breaches = []
            for breach, threshold, kpi_def in results:
                breaches.append({
                    'breach_id': str(breach.id),
                    'threshold_id': str(threshold.id),
                    'threshold_name': threshold.threshold_name,
                    'kpi_name': kpi_def.kpi_name,
                    'severity': breach.severity,
                    'status': breach.status,
                    'breach_value': float(breach.breach_value),
                    'expected_value': float(breach.expected_value) if breach.expected_value else None,
                    'created_at': breach.created_at.isoformat(),
                    'resolution_notes': breach.resolution_notes,
                })

            return breaches

        except Exception as e:
            logger.error(f"Error getting active breaches: {str(e)}")
            return []

    def acknowledge_breach(
        self, breach_id: str, user_id: str, notes: Optional[str] = None
    ) -> bool:
        """
        Acknowledge a threshold breach

        Args:
            breach_id: Breach ID
            user_id: User acknowledging the breach
            notes: Optional resolution notes

        Returns:
            True if successful, False otherwise
        """
        try:
            breach = self.db.query(KPIThresholdBreach).filter(KPIThresholdBreach.id == breach_id).first()

            if not breach:
                logger.warning(f"Breach not found: {breach_id}")
                return False

            breach.status = 'acknowledged'
            breach.acknowledged_by = user_id
            breach.acknowledged_at = datetime.utcnow()
            if notes:
                breach.resolution_notes = notes

            self.db.commit()
            logger.info(f"Breach acknowledged: {breach_id} by user {user_id}")
            return True

        except Exception as e:
            logger.error(f"Error acknowledging breach: {str(e)}")
            self.db.rollback()
            return False

    def resolve_breach(
        self, breach_id: str, user_id: str, notes: str
    ) -> bool:
        """
        Resolve a threshold breach

        Args:
            breach_id: Breach ID
            user_id: User resolving the breach
            notes: Resolution notes

        Returns:
            True if successful, False otherwise
        """
        try:
            breach = self.db.query(KPIThresholdBreach).filter(KPIThresholdBreach.id == breach_id).first()

            if not breach:
                logger.warning(f"Breach not found: {breach_id}")
                return False

            breach.status = 'resolved'
            breach.acknowledged_by = user_id
            breach.acknowledged_at = datetime.utcnow()
            breach.resolution_notes = notes

            self.db.commit()
            logger.info(f"Breach resolved: {breach_id} by user {user_id}")
            return True

        except Exception as e:
            logger.error(f"Error resolving breach: {str(e)}")
            self.db.rollback()
            return False

    def get_breach_history(
        self,
        tenant_id: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        limit: int = 100,
    ) -> List[Dict[str, any]]:
        """
        Get historical threshold breaches

        Args:
            tenant_id: Tenant ID
            start_date: Optional start date filter
            end_date: Optional end date filter
            limit: Maximum number of results

        Returns:
            List of historical breaches
        """
        try:
            query = (
                self.db.query(KPIThresholdBreach, KPIThreshold, KPIDefinition)
                .join(KPIThreshold, KPIThresholdBreach.threshold_id == KPIThreshold.id)
                .join(KPIDefinition, KPIThresholdBreach.kpi_id == KPIDefinition.id)
                .filter(KPIDefinition.tenant_id == tenant_id)
            )

            if start_date:
                query = query.filter(KPIThresholdBreach.created_at >= start_date)
            if end_date:
                query = query.filter(KPIThresholdBreach.created_at <= end_date)

            query = query.order_by(desc(KPIThresholdBreach.created_at)).limit(limit)

            results = query.all()

            history = []
            for breach, threshold, kpi_def in results:
                history.append({
                    'breach_id': str(breach.id),
                    'threshold_name': threshold.threshold_name,
                    'kpi_name': kpi_def.kpi_name,
                    'severity': breach.severity,
                    'status': breach.status,
                    'breach_value': float(breach.breach_value),
                    'expected_value': float(breach.expected_value) if breach.expected_value else None,
                    'created_at': breach.created_at.isoformat(),
                    'acknowledged_at': breach.acknowledged_at.isoformat() if breach.acknowledged_at else None,
                    'resolution_notes': breach.resolution_notes,
                })

            return history

        except Exception as e:
            logger.error(f"Error getting breach history: {str(e)}")
            return []

    def _evaluate_threshold(
        self, metric_value: float, threshold_value: Decimal, operator: str
    ) -> bool:
        """
        Evaluate if metric value breaches threshold

        Args:
            metric_value: Current metric value
            threshold_value: Threshold value
            operator: Comparison operator

        Returns:
            True if breach detected, False otherwise
        """
        threshold = float(threshold_value)

        if operator == '>':
            return metric_value > threshold
        elif operator == '<':
            return metric_value < threshold
        elif operator == '>=':
            return metric_value >= threshold
        elif operator == '<=':
            return metric_value <= threshold
        elif operator == '==':
            return abs(metric_value - threshold) < 0.001  # Floating point equality
        elif operator == '!=':
            return abs(metric_value - threshold) >= 0.001
        else:
            logger.warning(f"Unknown operator: {operator}")
            return False

    def _log_breach(
        self,
        threshold_id: str,
        kpi_id: str,
        metric_value: float,
        tenant_id: str,
        snapshot_id: Optional[str] = None,
    ) -> KPIThresholdBreach:
        """
        Log a threshold breach to database

        Args:
            threshold_id: Threshold ID
            kpi_id: KPI Definition ID
            metric_value: Breached metric value
            tenant_id: Tenant ID
            snapshot_id: Optional KPI Snapshot ID

        Returns:
            Created KPIThresholdBreach instance
        """
        threshold = self.db.query(KPIThreshold).filter(KPIThreshold.id == threshold_id).first()

        breach = KPIThresholdBreach(
            id=uuid.uuid4(),
            threshold_id=threshold_id,
            kpi_id=kpi_id,
            snapshot_id=snapshot_id,
            breach_value=Decimal(str(metric_value)),
            expected_value=threshold.threshold_value if threshold else None,
            severity=threshold.alert_severity if threshold else 'warning',
            status='open',
            created_at=datetime.utcnow(),
        )

        self.db.add(breach)
        self.db.commit()
        self.db.refresh(breach)

        return breach

    def _is_in_cooldown(self, cache_key: str) -> bool:
        """
        Check if breach alert is in cooldown period

        Args:
            cache_key: Cache key for breach

        Returns:
            True if in cooldown, False otherwise
        """
        if cache_key not in self.breach_cache:
            return False

        last_alert = self.breach_cache[cache_key]
        elapsed = (datetime.utcnow() - last_alert).total_seconds() / 60  # Minutes

        return elapsed < self.cooldown_minutes
