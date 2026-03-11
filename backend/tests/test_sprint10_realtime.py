"""
Tests for SPRINT 10: Real-Time Monitoring & Alerts
Tests all 4 agent deliverables:
- AGENT 1: WebSocket Real-Time Engine
- AGENT 2: Live Dashboard Updates (backend support)
- AGENT 3: Predictive Alerting
- AGENT 4: Threshold Monitoring
"""
import pytest
from datetime import datetime, timedelta
from decimal import Decimal
import uuid

from app.services.realtime_service import ConnectionManager, RealtimeMetricStreamer
from app.services.predictive_alerts import PredictiveAlertEngine
from app.services.threshold_monitor import ThresholdMonitor, ThresholdConfig
from app.models import (
    KPIDefinition,
    KPIThreshold,
    KPIThresholdBreach,
    KPISnapshot,
    Tenant,
    Organization,
)


# ============================================================================
# AGENT 1: WebSocket Real-Time Engine Tests
# ============================================================================


@pytest.mark.asyncio
class TestConnectionManager:
    """Test WebSocket connection management"""

    async def test_connection_lifecycle(self):
        """Test connecting and disconnecting"""
        manager = ConnectionManager()

        # Mock WebSocket
        class MockWebSocket:
            async def accept(self):
                pass

            async def send_text(self, text):
                pass

        websocket = MockWebSocket()
        conn_id = str(uuid.uuid4())
        tenant_id = str(uuid.uuid4())
        user_id = str(uuid.uuid4())

        # Connect
        await manager.connect(websocket, conn_id, tenant_id, user_id)

        assert conn_id in manager.active_connections
        assert manager.metrics["total_connections"] == 1

        # Disconnect
        manager.disconnect(conn_id)

        assert conn_id not in manager.active_connections

    async def test_room_subscriptions(self):
        """Test room subscription management"""
        manager = ConnectionManager()

        class MockWebSocket:
            async def accept(self):
                pass

            async def send_text(self, text):
                pass

        websocket = MockWebSocket()
        conn_id = str(uuid.uuid4())
        tenant_id = str(uuid.uuid4())
        user_id = str(uuid.uuid4())

        await manager.connect(websocket, conn_id, tenant_id, user_id)

        # Subscribe to room
        room_id = "facility:test-123"
        await manager.subscribe_to_room(conn_id, room_id)

        assert conn_id in manager.room_subscriptions[room_id]
        assert room_id in manager.connection_metadata[conn_id]["subscriptions"]

        # Unsubscribe
        await manager.unsubscribe_from_room(conn_id, room_id)

        assert conn_id not in manager.room_subscriptions[room_id]

    async def test_broadcast_to_room(self):
        """Test broadcasting to room subscribers"""
        manager = ConnectionManager()

        class MockWebSocket:
            def __init__(self):
                self.messages = []

            async def accept(self):
                pass

            async def send_text(self, text):
                self.messages.append(text)

        # Create multiple connections
        ws1 = MockWebSocket()
        ws2 = MockWebSocket()
        conn1 = str(uuid.uuid4())
        conn2 = str(uuid.uuid4())
        tenant_id = str(uuid.uuid4())

        await manager.connect(ws1, conn1, tenant_id, "user1")
        await manager.connect(ws2, conn2, tenant_id, "user2")

        # Subscribe both to same room
        room_id = "metric:energy"
        await manager.subscribe_to_room(conn1, room_id)
        await manager.subscribe_to_room(conn2, room_id)

        # Broadcast message
        message = {"type": "test", "data": "hello"}
        await manager.broadcast_to_room(room_id, message)

        # Both should have received message
        assert len(ws1.messages) > 0
        assert len(ws2.messages) > 0


# ============================================================================
# AGENT 3: Predictive Alerting Tests
# ============================================================================


class TestPredictiveAlertEngine:
    """Test predictive alerting engine"""

    def test_linear_regression_prediction(self):
        """Test linear regression prediction"""
        engine = PredictiveAlertEngine()

        # Create trending data (increasing)
        historical_data = [
            {'timestamp': datetime.utcnow() - timedelta(hours=i), 'value': 1000 + i * 10}
            for i in range(100, 0, -1)
        ]

        prediction = engine.predict_threshold_breach(
            historical_data=historical_data,
            threshold_value=2000.0,
            metric_name='Energy',
        )

        assert prediction is not None
        assert prediction.predicted_value > historical_data[-1]['value']
        assert 0.0 <= prediction.confidence <= 1.0
        assert 0.0 <= prediction.threshold_breach_probability <= 1.0

    def test_anomaly_detection(self):
        """Test anomaly detection"""
        engine = PredictiveAlertEngine()

        # Create normal data
        normal_data = [
            {'value': 1000 + i}
            for i in range(-5, 5)
        ]

        # Test normal value
        is_anomaly, score, factors = engine.detect_anomalies(normal_data, 1005.0)
        assert not is_anomaly
        assert score < 50.0

        # Test anomalous value
        is_anomaly, score, factors = engine.detect_anomalies(normal_data, 5000.0)
        assert is_anomaly
        assert score > 50.0
        assert 'z_score' in factors

    def test_alert_creation(self):
        """Test alert creation with priority scoring"""
        engine = PredictiveAlertEngine()

        # Create threshold breach alert
        historical_data = [
            {'timestamp': datetime.utcnow() - timedelta(hours=i), 'value': 1000 + i * 10}
            for i in range(50, 0, -1)
        ]

        prediction = engine.predict_threshold_breach(
            historical_data=historical_data,
            threshold_value=1500.0,
            metric_name='Energy',
        )

        alert = engine.create_alert(
            alert_type='threshold_breach',
            metric_name='Energy',
            current_value=1400.0,
            prediction=prediction,
            threshold_value=1500.0,
        )

        assert alert.alert_id is not None
        assert alert.alert_type == 'threshold_breach'
        assert alert.severity in ['info', 'warning', 'critical']
        assert 0.0 <= alert.priority_score <= 100.0
        assert alert.message is not None

    def test_anomaly_alert_creation(self):
        """Test anomaly alert creation"""
        engine = PredictiveAlertEngine()

        alert = engine.create_alert(
            alert_type='anomaly',
            metric_name='Temperature',
            current_value=95.0,
            anomaly_score=85.0,
        )

        assert alert.alert_id is not None
        assert alert.alert_type == 'anomaly'
        assert 'anomaly_score' in alert.factors


# ============================================================================
# AGENT 4: Threshold Monitoring Tests
# ============================================================================


class TestThresholdMonitor:
    """Test threshold monitoring"""

    def test_threshold_evaluation_operators(self, db_session):
        """Test threshold operator evaluation"""
        monitor = ThresholdMonitor(db_session)

        # Test > operator
        assert monitor._evaluate_threshold(150, Decimal("100"), ">") is True
        assert monitor._evaluate_threshold(50, Decimal("100"), ">") is False

        # Test < operator
        assert monitor._evaluate_threshold(50, Decimal("100"), "<") is True
        assert monitor._evaluate_threshold(150, Decimal("100"), "<") is False

        # Test >= operator
        assert monitor._evaluate_threshold(100, Decimal("100"), ">=") is True
        assert monitor._evaluate_threshold(150, Decimal("100"), ">=") is True

        # Test <= operator
        assert monitor._evaluate_threshold(100, Decimal("100"), "<=") is True
        assert monitor._evaluate_threshold(50, Decimal("100"), "<=") is True

    def test_configure_threshold(self, db_session, test_tenant, test_org):
        """Test threshold configuration"""
        monitor = ThresholdMonitor(db_session)

        # Create KPI definition
        kpi = KPIDefinition(
            id=uuid.uuid4(),
            organization_id=test_org.id,
            tenant_id=test_tenant.id,
            kpi_name='PUE',
            kpi_type='standard',
            formula='Total Facility Power / IT Equipment Power',
            unit='ratio',
            target_value=Decimal("1.5"),
            is_active=True,
        )
        db_session.add(kpi)
        db_session.commit()

        # Configure threshold
        config = ThresholdConfig(
            metric_name='PUE',
            threshold_value=2.0,
            operator='>',
            severity='critical',
            notify_email=True,
        )

        threshold_id = monitor.configure_threshold(
            kpi_id=str(kpi.id),
            threshold_config=config,
        )

        assert threshold_id is not None

        # Verify threshold was created
        threshold = db_session.query(KPIThreshold).filter(KPIThreshold.id == threshold_id).first()
        assert threshold is not None
        assert threshold.threshold_value == Decimal("2.0")
        assert threshold.operator == '>'
        assert threshold.alert_severity == 'critical'

    def test_breach_detection(self, db_session, test_tenant, test_org):
        """Test threshold breach detection"""
        monitor = ThresholdMonitor(db_session)

        # Create KPI and threshold
        kpi = KPIDefinition(
            id=uuid.uuid4(),
            organization_id=test_org.id,
            tenant_id=test_tenant.id,
            kpi_name='Energy',
            kpi_type='standard',
            formula='Total Energy',
            unit='kWh',
            target_value=Decimal("1000"),
            is_active=True,
        )
        db_session.add(kpi)

        threshold = KPIThreshold(
            id=uuid.uuid4(),
            kpi_id=kpi.id,
            threshold_name='Energy High',
            threshold_value=Decimal("1500"),
            operator='>',
            alert_severity='warning',
            is_enabled=True,
        )
        db_session.add(threshold)
        db_session.commit()

        # Check for breach (should breach)
        breaches = monitor.check_threshold_breach(
            metric_name='Energy',
            metric_value=1600.0,
            facility_id=str(uuid.uuid4()),
            org_id=str(test_org.id),
            tenant_id=str(test_tenant.id),
        )

        assert len(breaches) > 0
        assert breaches[0]['severity'] == 'warning'
        assert breaches[0]['metric_value'] == 1600.0

    def test_breach_cooldown(self, db_session, test_tenant, test_org):
        """Test breach alert cooldown"""
        monitor = ThresholdMonitor(db_session)

        # Set short cooldown for testing
        monitor.cooldown_minutes = 0.1  # 6 seconds

        # Create KPI and threshold
        kpi = KPIDefinition(
            id=uuid.uuid4(),
            organization_id=test_org.id,
            tenant_id=test_tenant.id,
            kpi_name='Temperature',
            kpi_type='standard',
            formula='Avg Temp',
            unit='°C',
            target_value=Decimal("25"),
            is_active=True,
        )
        db_session.add(kpi)

        threshold = KPIThreshold(
            id=uuid.uuid4(),
            kpi_id=kpi.id,
            threshold_name='Temp High',
            threshold_value=Decimal("30"),
            operator='>',
            alert_severity='critical',
            is_enabled=True,
        )
        db_session.add(threshold)
        db_session.commit()

        facility_id = str(uuid.uuid4())

        # First breach should be logged
        breaches1 = monitor.check_threshold_breach(
            metric_name='Temperature',
            metric_value=35.0,
            facility_id=facility_id,
            org_id=str(test_org.id),
            tenant_id=str(test_tenant.id),
        )
        assert len(breaches1) == 1

        # Second breach immediately should be in cooldown
        breaches2 = monitor.check_threshold_breach(
            metric_name='Temperature',
            metric_value=36.0,
            facility_id=facility_id,
            org_id=str(test_org.id),
            tenant_id=str(test_tenant.id),
        )
        assert len(breaches2) == 0  # Cooldown active

    def test_acknowledge_breach(self, db_session, test_tenant, test_org, test_user):
        """Test breach acknowledgement"""
        monitor = ThresholdMonitor(db_session)

        # Create breach
        kpi = KPIDefinition(
            id=uuid.uuid4(),
            organization_id=test_org.id,
            tenant_id=test_tenant.id,
            kpi_name='Carbon',
            kpi_type='standard',
            formula='Total CO2',
            unit='kg',
            target_value=Decimal("500"),
            is_active=True,
        )
        db_session.add(kpi)

        threshold = KPIThreshold(
            id=uuid.uuid4(),
            kpi_id=kpi.id,
            threshold_name='Carbon High',
            threshold_value=Decimal("1000"),
            operator='>',
            alert_severity='warning',
            is_enabled=True,
        )
        db_session.add(threshold)

        breach = KPIThresholdBreach(
            id=uuid.uuid4(),
            threshold_id=threshold.id,
            kpi_id=kpi.id,
            breach_value=Decimal("1200"),
            expected_value=Decimal("1000"),
            severity='warning',
            status='open',
        )
        db_session.add(breach)
        db_session.commit()

        # Acknowledge breach
        success = monitor.acknowledge_breach(
            breach_id=str(breach.id),
            user_id=str(test_user.id),
            notes='Investigating root cause',
        )

        assert success is True

        # Verify status changed
        db_session.refresh(breach)
        assert breach.status == 'acknowledged'
        assert breach.acknowledged_by == str(test_user.id)
        assert breach.resolution_notes == 'Investigating root cause'


# ============================================================================
# Integration Tests
# ============================================================================


class TestRealtimeIntegration:
    """Test integrated real-time monitoring flow"""

    def test_end_to_end_monitoring(self, db_session, test_tenant, test_org):
        """Test complete monitoring flow"""
        # 1. Configure threshold
        monitor = ThresholdMonitor(db_session)

        kpi = KPIDefinition(
            id=uuid.uuid4(),
            organization_id=test_org.id,
            tenant_id=test_tenant.id,
            kpi_name='Energy',
            kpi_type='standard',
            formula='Total Energy',
            unit='kWh',
            target_value=Decimal("1000"),
            is_active=True,
        )
        db_session.add(kpi)
        db_session.commit()

        config = ThresholdConfig(
            metric_name='Energy',
            threshold_value=1500.0,
            operator='>',
            severity='critical',
        )

        threshold_id = monitor.configure_threshold(
            kpi_id=str(kpi.id),
            threshold_config=config,
        )

        assert threshold_id is not None

        # 2. Generate predictive alert
        engine = PredictiveAlertEngine()

        historical_data = [
            {'timestamp': datetime.utcnow() - timedelta(hours=i), 'value': 1000 + i * 5}
            for i in range(100, 0, -1)
        ]

        prediction = engine.predict_threshold_breach(
            historical_data=historical_data,
            threshold_value=1500.0,
            metric_name='Energy',
        )

        assert prediction is not None

        # 3. Check for actual breach
        breaches = monitor.check_threshold_breach(
            metric_name='Energy',
            metric_value=1600.0,
            facility_id=str(uuid.uuid4()),
            org_id=str(test_org.id),
            tenant_id=str(test_tenant.id),
        )

        assert len(breaches) > 0
        assert breaches[0]['severity'] == 'critical'
