"""
Energy metrics calculation and aggregation service

Provides:
- Energy consumption aggregation at site/facility/rack level
- Peak usage detection and analysis
- Efficiency metrics calculation
- Trend analysis over time periods
"""

from typing import List, Dict, Optional, Tuple
from datetime import datetime, timedelta
from decimal import Decimal
import logging
from sqlalchemy.orm import Session
from sqlalchemy import and_, func, desc

from app.models import (
    TelemetryReading,
    Meter,
    Device,
    Rack,
    Zone,
    Floor,
    Building,
    Facility,
    Organization,
)

logger = logging.getLogger(__name__)

# Constants
EFFICIENCY_METRICS = ["watts_per_server", "kwh_per_device", "pue"]  # Power Usage Effectiveness


class EnergyMetricsService:
    """
    Calculates and aggregates energy metrics from telemetry data

    Handles:
    - Total consumption at multiple hierarchy levels
    - Peak usage detection
    - Efficiency metrics calculation
    - Trend analysis
    """

    def __init__(self, db: Session):
        self.db = db

    def get_total_consumption(
        self,
        tenant_id: str,
        org_id: str,
        period: str = "day",
        days_back: int = 7,
    ) -> Dict:
        """
        Get total energy consumption for organization

        Args:
            tenant_id: Tenant UUID
            org_id: Organization UUID
            period: 'day', 'week', 'month'
            days_back: How many days of history to return

        Returns:
            {
                "current_kwh": float,
                "total_kwh": float,
                "average_kwh": float,
                "peak_kwh": float,
                "timestamp": datetime,
                "trend": [{timestamp, value}, ...]
            }
        """
        # Get all facility meter IDs for this organization
        facility_ids = (
            self.db.query(Facility.id)
            .filter_by(organization_id=org_id, tenant_id=tenant_id)
            .all()
        )

        if not facility_ids:
            return {
                "current_kwh": 0.0,
                "total_kwh": 0.0,
                "average_kwh": 0.0,
                "peak_kwh": 0.0,
                "timestamp": datetime.utcnow(),
                "trend": [],
            }

        facility_id_list = [f[0] for f in facility_ids]

        # Get all meters for these facilities
        meter_ids = (
            self.db.query(Meter.id)
            .join(Device, Device.id == Meter.device_id)
            .join(Rack, Rack.id == Device.rack_id)
            .join(Zone, Zone.id == Rack.zone_id)
            .join(Floor, Floor.id == Zone.floor_id)
            .join(Building, Building.id == Floor.building_id)
            .join(Facility, Facility.id == Building.facility_id)
            .filter(Facility.id.in_(facility_id_list))
            .all()
        )

        if not meter_ids:
            return {
                "current_kwh": 0.0,
                "total_kwh": 0.0,
                "average_kwh": 0.0,
                "peak_kwh": 0.0,
                "timestamp": datetime.utcnow(),
                "trend": [],
            }

        meter_id_list = [m[0] for m in meter_ids]

        # Calculate lookback period
        lookback = datetime.utcnow() - timedelta(days=days_back)

        # Get readings from database
        readings = (
            self.db.query(TelemetryReading)
            .filter(
                and_(
                    TelemetryReading.meter_id.in_(meter_id_list),
                    TelemetryReading.status == "valid",
                    TelemetryReading.timestamp >= lookback,
                )
            )
            .all()
        )

        if not readings:
            return {
                "current_kwh": 0.0,
                "total_kwh": 0.0,
                "average_kwh": 0.0,
                "peak_kwh": 0.0,
                "timestamp": datetime.utcnow(),
                "trend": [],
            }

        # Calculate metrics
        values = [float(r.value) for r in readings]
        total_kwh = sum(values)
        average_kwh = total_kwh / len(values) if values else 0
        peak_kwh = max(values) if values else 0
        current_kwh = float(readings[-1].value) if readings else 0

        # Build trend data (aggregate by hour)
        trend_dict = {}
        for reading in readings:
            hour_key = reading.timestamp.replace(minute=0, second=0, microsecond=0)
            if hour_key not in trend_dict:
                trend_dict[hour_key] = []
            trend_dict[hour_key].append(float(reading.value))

        trend = [
            {
                "timestamp": ts.isoformat(),
                "value": sum(values) / len(values),
            }
            for ts, values in sorted(trend_dict.items())
        ]

        return {
            "current_kwh": round(current_kwh, 2),
            "total_kwh": round(total_kwh, 2),
            "average_kwh": round(average_kwh, 2),
            "peak_kwh": round(peak_kwh, 2),
            "timestamp": datetime.utcnow().isoformat(),
            "trend": trend,
        }

    def get_facility_breakdown(
        self,
        tenant_id: str,
        org_id: str,
        days_back: int = 7,
    ) -> List[Dict]:
        """
        Get energy consumption breakdown by facility

        Returns:
            [{facility_id, facility_name, current_kwh, total_kwh, peak_kwh}, ...]
        """
        facilities = (
            self.db.query(Facility)
            .filter_by(organization_id=org_id, tenant_id=tenant_id, is_active=True)
            .all()
        )

        breakdown = []
        lookback = datetime.utcnow() - timedelta(days=days_back)

        for facility in facilities:
            # Get all meters for this facility
            meter_ids = (
                self.db.query(Meter.id)
                .join(Device, Device.id == Meter.device_id)
                .join(Rack, Rack.id == Device.rack_id)
                .join(Zone, Zone.id == Rack.zone_id)
                .join(Floor, Floor.id == Zone.floor_id)
                .join(Building, Building.id == Floor.building_id)
                .filter(Building.facility_id == facility.id)
                .all()
            )

            if meter_ids:
                meter_id_list = [m[0] for m in meter_ids]

                readings = (
                    self.db.query(TelemetryReading)
                    .filter(
                        and_(
                            TelemetryReading.meter_id.in_(meter_id_list),
                            TelemetryReading.status == "valid",
                            TelemetryReading.timestamp >= lookback,
                        )
                    )
                    .all()
                )

                if readings:
                    values = [float(r.value) for r in readings]
                    breakdown.append(
                        {
                            "facility_id": str(facility.id),
                            "facility_name": facility.name,
                            "current_kwh": round(values[-1], 2),
                            "total_kwh": round(sum(values), 2),
                            "average_kwh": round(sum(values) / len(values), 2),
                            "peak_kwh": round(max(values), 2),
                        }
                    )

        return breakdown

    def get_peak_usage(
        self,
        tenant_id: str,
        meter_id: str,
        days_back: int = 30,
        limit: int = 10,
    ) -> List[Dict]:
        """
        Get peak usage periods for a meter

        Returns:
            [{timestamp, value, hour}, ...] sorted by value descending
        """
        lookback = datetime.utcnow() - timedelta(days=days_back)

        readings = (
            self.db.query(TelemetryReading)
            .filter(
                and_(
                    TelemetryReading.meter_id == meter_id,
                    TelemetryReading.tenant_id == tenant_id,
                    TelemetryReading.status == "valid",
                    TelemetryReading.timestamp >= lookback,
                )
            )
            .order_by(desc(TelemetryReading.value))
            .limit(limit)
            .all()
        )

        return [
            {
                "timestamp": r.timestamp.isoformat(),
                "value": float(r.value),
                "hour": r.timestamp.strftime("%Y-%m-%d %H:00"),
            }
            for r in readings
        ]

    def get_efficiency_metrics(
        self,
        tenant_id: str,
        facility_id: str,
        days_back: int = 7,
    ) -> Dict:
        """
        Calculate efficiency metrics for a facility

        Returns:
            {
                "watts_per_server": float,
                "kwh_per_device": float,
                "pue": float (Power Usage Effectiveness)
            }
        """
        facility = (
            self.db.query(Facility)
            .filter_by(id=facility_id, tenant_id=tenant_id)
            .first()
        )

        if not facility:
            return {
                "watts_per_server": 0,
                "kwh_per_device": 0,
                "pue": 0,
            }

        # Count total devices in facility
        device_count = (
            self.db.query(func.count(Device.id))
            .join(Rack, Rack.id == Device.rack_id)
            .join(Zone, Zone.id == Rack.zone_id)
            .join(Floor, Floor.id == Zone.floor_id)
            .join(Building, Building.id == Floor.building_id)
            .filter(Building.facility_id == facility_id)
            .scalar()
        )

        lookback = datetime.utcnow() - timedelta(days=days_back)

        # Get all readings for this facility
        meter_ids = (
            self.db.query(Meter.id)
            .join(Device, Device.id == Meter.device_id)
            .join(Rack, Rack.id == Device.rack_id)
            .join(Zone, Zone.id == Rack.zone_id)
            .join(Floor, Floor.id == Zone.floor_id)
            .join(Building, Building.id == Floor.building_id)
            .filter(Building.facility_id == facility_id)
            .all()
        )

        if not meter_ids or device_count == 0:
            return {
                "watts_per_server": 0,
                "kwh_per_device": 0,
                "pue": 0,
            }

        meter_id_list = [m[0] for m in meter_ids]

        readings = (
            self.db.query(TelemetryReading)
            .filter(
                and_(
                    TelemetryReading.meter_id.in_(meter_id_list),
                    TelemetryReading.status == "valid",
                    TelemetryReading.timestamp >= lookback,
                )
            )
            .all()
        )

        if not readings:
            return {
                "watts_per_server": 0,
                "kwh_per_device": 0,
                "pue": 0,
            }

        values = [float(r.value) for r in readings]
        total_kwh = sum(values)
        avg_kw = (total_kwh / len(values)) if values else 0
        watts_per_server = (avg_kw * 1000) / device_count if device_count > 0 else 0
        kwh_per_device = total_kwh / device_count if device_count > 0 else 0

        # PUE = Total Energy / IT Equipment Energy (simplified: 1.2 - 2.0 range typical)
        pue = 1.5  # Placeholder - would need separate IT vs facility power meters

        return {
            "watts_per_server": round(watts_per_server, 2),
            "kwh_per_device": round(kwh_per_device, 2),
            "pue": pue,
        }

    def get_site_energy_breakdown(
        self,
        tenant_id: str,
        facility_id: str,
    ) -> List[Dict]:
        """
        Get energy breakdown by rack within a facility

        Returns:
            [{rack_id, rack_name, total_kwh, device_count}, ...]
        """
        # Get all racks for this facility
        racks = (
            self.db.query(Rack)
            .join(Zone, Zone.id == Rack.zone_id)
            .join(Floor, Floor.id == Zone.floor_id)
            .join(Building, Building.id == Floor.building_id)
            .filter(Building.facility_id == facility_id)
            .all()
        )

        breakdown = []
        lookback = datetime.utcnow() - timedelta(days=7)

        for rack in racks:
            # Count devices in rack
            device_count = self.db.query(func.count(Device.id)).filter_by(
                rack_id=rack.id
            ).scalar()

            # Get meter IDs for devices in rack
            meter_ids = (
                self.db.query(Meter.id)
                .join(Device, Device.id == Meter.device_id)
                .filter(Device.rack_id == rack.id)
                .all()
            )

            if meter_ids:
                meter_id_list = [m[0] for m in meter_ids]

                readings = (
                    self.db.query(TelemetryReading)
                    .filter(
                        and_(
                            TelemetryReading.meter_id.in_(meter_id_list),
                            TelemetryReading.status == "valid",
                            TelemetryReading.timestamp >= lookback,
                        )
                    )
                    .all()
                )

                if readings:
                    total_kwh = sum(float(r.value) for r in readings)
                    breakdown.append(
                        {
                            "rack_id": str(rack.id),
                            "rack_name": rack.name,
                            "total_kwh": round(total_kwh, 2),
                            "device_count": device_count,
                        }
                    )

        return breakdown

    def get_energy_dashboard(
        self,
        tenant_id: str,
        org_id: str,
    ) -> Dict:
        """
        Get complete dashboard data (all metrics combined)

        Returns comprehensive dashboard payload
        """
        consumption = self.get_total_consumption(tenant_id, org_id)
        facility_breakdown = self.get_facility_breakdown(tenant_id, org_id)

        return {
            "organization_id": org_id,
            "consumption": consumption,
            "facility_breakdown": facility_breakdown,
            "timestamp": datetime.utcnow().isoformat(),
        }
