"""
KPI (Key Performance Indicator) Calculation and Alerting Service

Implements:
- Standard KPIs: PUE (Power Usage Effectiveness), CUE (Carbon Usage Effectiveness),
  WUE (Water Usage Effectiveness), ERE (Energy Reuse Effectiveness)
- Custom KPI formula evaluation
- Threshold breach detection and alerting
- Time-series snapshot management
- Historical trend analysis
"""

from typing import List, Dict, Optional, Tuple
from decimal import Decimal
from datetime import datetime, timedelta
import logging
from sqlalchemy.orm import Session
from sqlalchemy import and_, func, desc

from app.models import (
    KPIDefinition,
    KPISnapshot,
    KPIThreshold,
    KPIThresholdBreach,
    TelemetryReading,
    Meter,
    CarbonCalculation,
    Organization,
)

logger = logging.getLogger(__name__)

# Standard KPI formulas
STANDARD_KPIS = {
    "PUE": {
        "name": "Power Usage Effectiveness",
        "formula": "Total Facility Power / IT Equipment Power",
        "unit": "ratio",
        "target": 1.2,
        "lower_bound": 1.0,
        "upper_bound": 2.0,
    },
    "CUE": {
        "name": "Carbon Usage Effectiveness",
        "formula": "Carbon Emissions / Computing Power",
        "unit": "g CO2/kWh",
        "target": 50,
        "lower_bound": 0,
        "upper_bound": 200,
    },
    "WUE": {
        "name": "Water Usage Effectiveness",
        "formula": "Annual Water Consumption / Annual Energy Consumption",
        "unit": "L/kWh",
        "target": 1.8,
        "lower_bound": 0,
        "upper_bound": 5.0,
    },
    "ERE": {
        "name": "Energy Reuse Effectiveness",
        "formula": "Total Energy Used / Total Energy Reused",
        "unit": "ratio",
        "target": 1.5,
        "lower_bound": 1.0,
        "upper_bound": 2.0,
    },
}


class KPICalculationService:
    """Calculates KPI values from telemetry and carbon data"""

    def __init__(self, db: Session):
        self.db = db

    def calculate_pue(
        self,
        organization_id: str,
        period_start: datetime,
        period_end: datetime,
    ) -> Tuple[Decimal, Dict]:
        """
        Calculate Power Usage Effectiveness (PUE)

        PUE = Total Facility Power / IT Equipment Power
        Target: < 1.2 (meaning total power is <20% higher than IT power)

        Returns (pue_value, calculation_details)
        """
        try:
            # Get all electricity meters for organization
            total_power_kwh = self._get_total_facility_power(
                organization_id, period_start, period_end
            )
            it_power_kwh = self._get_it_equipment_power(
                organization_id, period_start, period_end
            )

            if it_power_kwh <= 0:
                logger.warning(f"No IT power data for org {organization_id}")
                return Decimal("0"), {}

            pue = Decimal(str(total_power_kwh)) / Decimal(str(it_power_kwh))

            return pue, {
                "total_facility_power_kwh": float(total_power_kwh),
                "it_equipment_power_kwh": float(it_power_kwh),
                "pue": float(pue),
            }

        except Exception as e:
            logger.error(f"Error calculating PUE: {str(e)}")
            return Decimal("0"), {}

    def calculate_cue(
        self,
        organization_id: str,
        period_start: datetime,
        period_end: datetime,
    ) -> Tuple[Decimal, Dict]:
        """
        Calculate Carbon Usage Effectiveness (CUE)

        CUE = Carbon Emissions (g CO2) / Computing Power (kWh)
        Target: < 50 g CO2/kWh

        Returns (cue_value, calculation_details)
        """
        try:
            # Get carbon emissions for period
            emissions_record = (
                self.db.query(CarbonCalculation)
                .filter(
                    and_(
                        CarbonCalculation.organization_id == organization_id,
                        CarbonCalculation.period_start >= period_start,
                        CarbonCalculation.period_end <= period_end,
                        CarbonCalculation.status == "approved",
                    )
                )
                .order_by(desc(CarbonCalculation.created_at))
                .first()
            )

            if not emissions_record:
                logger.warning(f"No carbon data for org {organization_id}")
                return Decimal("0"), {}

            # Get IT equipment power
            it_power_kwh = self._get_it_equipment_power(
                organization_id, period_start, period_end
            )

            if it_power_kwh <= 0:
                return Decimal("0"), {}

            # Convert kg CO2e to g CO2 (multiply by 1000)
            carbon_g = float(emissions_record.total_emissions) * 1000
            cue = Decimal(str(carbon_g)) / Decimal(str(it_power_kwh))

            return cue, {
                "total_emissions_kg_co2e": float(emissions_record.total_emissions),
                "carbon_emissions_g_co2": float(carbon_g),
                "it_equipment_power_kwh": float(it_power_kwh),
                "cue": float(cue),
            }

        except Exception as e:
            logger.error(f"Error calculating CUE: {str(e)}")
            return Decimal("0"), {}

    def calculate_wue(
        self,
        organization_id: str,
        period_start: datetime,
        period_end: datetime,
    ) -> Tuple[Decimal, Dict]:
        """
        Calculate Water Usage Effectiveness (WUE)

        WUE = Total Water Consumption (liters) / Total Energy (kWh)
        Target: < 1.8 L/kWh

        Returns (wue_value, calculation_details)
        """
        try:
            # Get water consumption from telemetry (assumed meter type = "water")
            water_readings = (
                self.db.query(func.sum(TelemetryReading.value))
                .join(Meter)
                .filter(
                    and_(
                        Meter.utility_type == "water",
                        TelemetryReading.timestamp >= period_start,
                        TelemetryReading.timestamp <= period_end,
                        TelemetryReading.status == "valid",
                    )
                )
                .scalar()
            )

            water_liters = float(water_readings) if water_readings else 0

            # Get total energy consumption
            total_energy_kwh = self._get_total_facility_power(
                organization_id, period_start, period_end
            )

            if total_energy_kwh <= 0:
                return Decimal("0"), {}

            wue = Decimal(str(water_liters)) / Decimal(str(total_energy_kwh))

            return wue, {
                "water_consumption_liters": float(water_liters),
                "total_energy_kwh": float(total_energy_kwh),
                "wue": float(wue),
            }

        except Exception as e:
            logger.error(f"Error calculating WUE: {str(e)}")
            return Decimal("0"), {}

    def calculate_ere(
        self,
        organization_id: str,
        period_start: datetime,
        period_end: datetime,
    ) -> Tuple[Decimal, Dict]:
        """
        Calculate Energy Reuse Effectiveness (ERE)

        ERE = Total Energy Used / Total Energy Reused
        This represents waste heat recovery efficiency
        Target: > 1.5 (meaning 67% of energy is reused)

        Note: Requires waste heat recovery system data
        For now, returns placeholder based on facility efficiency

        Returns (ere_value, calculation_details)
        """
        try:
            total_energy = self._get_total_facility_power(
                organization_id, period_start, period_end
            )

            if total_energy <= 0:
                return Decimal("0"), {}

            # Placeholder: Assume 40% energy reuse efficiency
            # In production, this would come from actual waste heat recovery meters
            energy_reused = total_energy * 0.40
            ere = Decimal(str(total_energy)) / Decimal(str(energy_reused)) if energy_reused > 0 else Decimal("0")

            return ere, {
                "total_energy_kwh": float(total_energy),
                "energy_reused_kwh": float(energy_reused),
                "ere": float(ere),
            }

        except Exception as e:
            logger.error(f"Error calculating ERE: {str(e)}")
            return Decimal("0"), {}

    def _get_total_facility_power(
        self,
        organization_id: str,
        period_start: datetime,
        period_end: datetime,
    ) -> float:
        """Get total facility electricity consumption in kWh"""
        total_kwh = (
            self.db.query(func.sum(TelemetryReading.value))
            .join(Meter)
            .filter(
                and_(
                    Meter.utility_type == "electricity",
                    TelemetryReading.timestamp >= period_start,
                    TelemetryReading.timestamp <= period_end,
                    TelemetryReading.status == "valid",
                )
            )
            .scalar()
        )

        return float(total_kwh) if total_kwh else 0

    def _get_it_equipment_power(
        self,
        organization_id: str,
        period_start: datetime,
        period_end: datetime,
    ) -> float:
        """
        Get IT equipment power consumption in kWh

        In production, this would query specific IT equipment meters.
        For now, assumes 70% of total facility power is IT equipment.
        """
        total_power = self._get_total_facility_power(
            organization_id, period_start, period_end
        )
        return total_power * 0.70

    def create_snapshot(
        self,
        kpi_id: str,
        organization_id: str,
        tenant_id: str,
        kpi_name: str,
        calculated_value: Decimal,
        target_value: Decimal,
        calculation_details: Dict,
        data_quality_score: Decimal = Decimal("100"),
    ) -> KPISnapshot:
        """Create a time-series snapshot for a KPI"""
        try:
            # Calculate variance from target
            if target_value > 0:
                variance_percent = (
                    (calculated_value - target_value) / target_value * 100
                )
            else:
                variance_percent = Decimal("0")

            # Determine status based on variance
            if abs(variance_percent) <= 10:
                status = "normal"
            elif abs(variance_percent) <= 20:
                status = "warning"
            else:
                status = "critical"

            snapshot = KPISnapshot(
                kpi_id=kpi_id,
                tenant_id=tenant_id,
                snapshot_date=datetime.utcnow(),
                calculated_value=calculated_value,
                target_value=target_value,
                variance_percent=variance_percent,
                status=status,
                calculation_details=calculation_details,
                data_quality_score=data_quality_score,
            )

            self.db.add(snapshot)
            self.db.commit()

            logger.info(f"Created KPI snapshot for {kpi_name}: {calculated_value}")
            return snapshot

        except Exception as e:
            logger.error(f"Error creating KPI snapshot: {str(e)}")
            raise

    def get_snapshot_trend(
        self,
        kpi_id: str,
        days: int = 30,
    ) -> List[Dict]:
        """Get historical KPI snapshots for trend analysis"""
        cutoff_date = datetime.utcnow() - timedelta(days=days)

        snapshots = (
            self.db.query(KPISnapshot)
            .filter(
                and_(
                    KPISnapshot.kpi_id == kpi_id,
                    KPISnapshot.snapshot_date >= cutoff_date,
                )
            )
            .order_by(KPISnapshot.snapshot_date)
            .all()
        )

        return [
            {
                "date": s.snapshot_date.isoformat(),
                "value": float(s.calculated_value),
                "target": float(s.target_value) if s.target_value else None,
                "variance_percent": float(s.variance_percent) if s.variance_percent else None,
                "status": s.status,
            }
            for s in snapshots
        ]


class KPIThresholdService:
    """Manages KPI thresholds and breach detection/alerting"""

    def __init__(self, db: Session):
        self.db = db

    def create_threshold(
        self,
        kpi_id: str,
        threshold_name: str,
        threshold_value: Decimal,
        operator: str,  # >, <, >=, <=, ==, !=
        alert_severity: str,  # info, warning, critical
        notify_email: bool = True,
        notify_slack: bool = False,
        notify_webhook: Optional[str] = None,
    ) -> KPIThreshold:
        """Create a new alerting threshold for a KPI"""
        try:
            threshold = KPIThreshold(
                kpi_id=kpi_id,
                threshold_name=threshold_name,
                threshold_value=threshold_value,
                operator=operator,
                alert_severity=alert_severity,
                notify_email=notify_email,
                notify_slack=notify_slack,
                notify_webhook=notify_webhook,
            )

            self.db.add(threshold)
            self.db.commit()

            logger.info(f"Created KPI threshold: {threshold_name}")
            return threshold

        except Exception as e:
            logger.error(f"Error creating KPI threshold: {str(e)}")
            raise

    def check_breaches(
        self,
        kpi_id: str,
        snapshot_id: str,
        calculated_value: Decimal,
        target_value: Decimal,
    ) -> List[KPIThresholdBreach]:
        """Check if any thresholds are breached and create breach records"""
        try:
            thresholds = (
                self.db.query(KPIThreshold)
                .filter(
                    and_(
                        KPIThreshold.kpi_id == kpi_id,
                        KPIThreshold.is_enabled == True,
                    )
                )
                .all()
            )

            breaches = []

            for threshold in thresholds:
                is_breached = self._evaluate_threshold(
                    calculated_value, threshold.operator, threshold.threshold_value
                )

                if is_breached:
                    breach = KPIThresholdBreach(
                        threshold_id=threshold.id,
                        kpi_id=kpi_id,
                        snapshot_id=snapshot_id,
                        breach_value=calculated_value,
                        expected_value=target_value,
                        severity=threshold.alert_severity,
                        status="open",
                    )

                    self.db.add(breach)
                    breaches.append(breach)

                    logger.warning(
                        f"KPI threshold breached: {threshold.threshold_name} "
                        f"(value={calculated_value}, threshold={threshold.threshold_value})"
                    )

            self.db.commit()
            return breaches

        except Exception as e:
            logger.error(f"Error checking breaches: {str(e)}")
            return []

    def _evaluate_threshold(
        self,
        value: Decimal,
        operator: str,
        threshold_value: Decimal,
    ) -> bool:
        """Evaluate if a threshold condition is met"""
        if operator == ">":
            return value > threshold_value
        elif operator == "<":
            return value < threshold_value
        elif operator == ">=":
            return value >= threshold_value
        elif operator == "<=":
            return value <= threshold_value
        elif operator == "==":
            return value == threshold_value
        elif operator == "!=":
            return value != threshold_value
        else:
            logger.error(f"Unknown operator: {operator}")
            return False

    def acknowledge_breach(
        self,
        breach_id: str,
        acknowledged_by: str,
        resolution_notes: str = None,
    ) -> KPIThresholdBreach:
        """Acknowledge a threshold breach"""
        try:
            breach = self.db.query(KPIThresholdBreach).filter_by(id=breach_id).first()
            if not breach:
                raise ValueError(f"Breach {breach_id} not found")

            breach.status = "acknowledged"
            breach.acknowledged_by = acknowledged_by
            breach.acknowledged_at = datetime.utcnow()
            breach.resolution_notes = resolution_notes

            self.db.commit()

            logger.info(f"Acknowledged KPI breach: {breach_id}")
            return breach

        except Exception as e:
            logger.error(f"Error acknowledging breach: {str(e)}")
            raise

    def get_breaches(
        self,
        kpi_id: str,
        status: str = None,
        limit: int = 100,
    ) -> List[Dict]:
        """Get breach history for a KPI"""
        query = self.db.query(KPIThresholdBreach).filter_by(kpi_id=kpi_id)

        if status:
            query = query.filter_by(status=status)

        breaches = query.order_by(desc(KPIThresholdBreach.created_at)).limit(limit).all()

        return [
            {
                "id": str(b.id),
                "threshold_id": str(b.threshold_id),
                "breach_value": float(b.breach_value),
                "expected_value": float(b.expected_value) if b.expected_value else None,
                "severity": b.severity,
                "status": b.status,
                "acknowledged_by": str(b.acknowledged_by) if b.acknowledged_by else None,
                "acknowledged_at": b.acknowledged_at.isoformat() if b.acknowledged_at else None,
                "resolution_notes": b.resolution_notes,
                "created_at": b.created_at.isoformat(),
            }
            for b in breaches
        ]
