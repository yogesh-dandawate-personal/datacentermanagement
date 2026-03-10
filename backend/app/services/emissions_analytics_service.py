"""
Emissions Analytics Service

Provides analytics, dashboards, and insights for emissions data:
- Facility-level dashboards
- Portfolio overview
- Trend analysis
- Benchmarking
- Carbon intensity metrics
"""

from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timedelta
from decimal import Decimal
from typing import Dict, List, Optional
import logging
from uuid import UUID

from app.models import (
    EmissionsCalculation, EmissionsActivityData, EmissionsSource,
    TelemetryReading, KPISnapshot, Organization, Facility
)

logger = logging.getLogger(__name__)


class EmissionsAnalyticsService:
    """Service for emissions analytics and dashboards"""

    def __init__(self, db: Session):
        self.db = db

    def get_facility_dashboard_data(
        self,
        tenant_id: UUID,
        facility_id: UUID,
        period: str = "current_month"
    ) -> Dict:
        """
        Get comprehensive facility emissions dashboard

        Returns:
        - Total emissions (MTD/YTD)
        - Emissions by scope
        - Carbon intensity
        - PUE
        - Renewable energy %
        - 30-day trend
        - Top emitting assets
        """
        try:
            # Determine period dates
            end_date = datetime.utcnow()
            if period == "current_month":
                start_date = datetime(end_date.year, end_date.month, 1)
            elif period == "current_year":
                start_date = datetime(end_date.year, 1, 1)
            elif period == "last_30_days":
                start_date = end_date - timedelta(days=30)
            elif period == "last_90_days":
                start_date = end_date - timedelta(days=90)
            else:
                start_date = datetime(end_date.year, end_date.month, 1)

            # Get all calculations for facility
            calculations = self.db.query(EmissionsCalculation).join(
                EmissionsSource
            ).filter(
                EmissionsSource.facility_id == facility_id,
                EmissionsSource.tenant_id == tenant_id,
                EmissionsCalculation.calculation_period_end >= start_date,
                EmissionsCalculation.calculation_period_start <= end_date,
                EmissionsCalculation.status == "approved"
            ).all()

            if not calculations:
                return self._get_empty_dashboard()

            # Aggregate by scope
            scope_1 = sum(c.total_emissions_kgco2e for c in calculations if c.scope == "scope1")
            scope_2 = sum(c.total_emissions_kgco2e for c in calculations if c.scope == "scope2")
            scope_3 = sum(c.total_emissions_kgco2e for c in calculations if c.scope == "scope3")
            total_emissions = scope_1 + scope_2 + scope_3

            # Convert to tCO2e
            scope_1_tco2e = float(scope_1 / Decimal("1000"))
            scope_2_tco2e = float(scope_2 / Decimal("1000"))
            scope_3_tco2e = float(scope_3 / Decimal("1000"))
            total_tco2e = float(total_emissions / Decimal("1000"))

            # Get energy consumption for carbon intensity
            energy_kwh = self._get_facility_energy(facility_id, start_date, end_date)
            carbon_intensity = (float(total_emissions) / energy_kwh) if energy_kwh > 0 else 0

            # Get PUE from KPI engine
            pue = self._get_latest_pue(facility_id)

            # Get renewable energy %
            renewable_pct = self._get_renewable_percentage(facility_id, start_date, end_date)

            # Get 30-day trend
            trend_30d = self._get_emissions_trend(tenant_id, facility_id, days=30)

            # Get top emitting sources
            top_sources = self._get_top_emitting_sources(facility_id, start_date, end_date, limit=10)

            # Month-over-month comparison
            prev_period_start = start_date - timedelta(days=30)
            prev_period_end = start_date
            prev_calculations = self.db.query(EmissionsCalculation).join(
                EmissionsSource
            ).filter(
                EmissionsSource.facility_id == facility_id,
                EmissionsCalculation.calculation_period_end >= prev_period_start,
                EmissionsCalculation.calculation_period_start <= prev_period_end,
                EmissionsCalculation.status == "approved"
            ).all()

            prev_total = sum(c.total_emissions_kgco2e for c in prev_calculations) / Decimal("1000")
            mom_change = ((total_tco2e - float(prev_total)) / float(prev_total) * 100) if prev_total > 0 else 0

            return {
                "facility_id": str(facility_id),
                "period": period,
                "date_range": {
                    "start": start_date.isoformat(),
                    "end": end_date.isoformat()
                },
                "emissions": {
                    "total_tco2e": total_tco2e,
                    "scope_1_tco2e": scope_1_tco2e,
                    "scope_2_tco2e": scope_2_tco2e,
                    "scope_3_tco2e": scope_3_tco2e,
                    "scope_1_pct": float((scope_1 / total_emissions * 100) if total_emissions > 0 else 0),
                    "scope_2_pct": float((scope_2 / total_emissions * 100) if total_emissions > 0 else 0),
                    "scope_3_pct": float((scope_3 / total_emissions * 100) if total_emissions > 0 else 0),
                },
                "metrics": {
                    "carbon_intensity_gco2e_kwh": round(carbon_intensity, 2),
                    "pue": round(pue, 2) if pue else None,
                    "renewable_pct": round(renewable_pct, 1),
                    "mom_change_pct": round(mom_change, 1)
                },
                "breakdown": [
                    {"scope": "Scope 1 (Direct)", "emissions_tco2e": scope_1_tco2e, "pct": float((scope_1 / total_emissions * 100) if total_emissions > 0 else 0)},
                    {"scope": "Scope 2 (Electricity)", "emissions_tco2e": scope_2_tco2e, "pct": float((scope_2 / total_emissions * 100) if total_emissions > 0 else 0)},
                    {"scope": "Scope 3 (Indirect)", "emissions_tco2e": scope_3_tco2e, "pct": float((scope_3 / total_emissions * 100) if total_emissions > 0 else 0)}
                ],
                "trend_30d": trend_30d,
                "top_sources": top_sources,
                "calculation_count": len(calculations)
            }

        except Exception as e:
            logger.error(f"Error getting facility dashboard: {str(e)}")
            raise

    def get_portfolio_overview(
        self,
        tenant_id: UUID,
        period: str = "current_year"
    ) -> Dict:
        """Get portfolio-wide emissions overview"""
        try:
            end_date = datetime.utcnow()
            if period == "current_year":
                start_date = datetime(end_date.year, 1, 1)
            elif period == "last_12_months":
                start_date = end_date - timedelta(days=365)
            else:
                start_date = datetime(end_date.year, 1, 1)

            # Get all approved calculations
            calculations = self.db.query(EmissionsCalculation).filter(
                EmissionsCalculation.tenant_id == tenant_id,
                EmissionsCalculation.calculation_period_end >= start_date,
                EmissionsCalculation.calculation_period_start <= end_date,
                EmissionsCalculation.status == "approved"
            ).all()

            if not calculations:
                return self._get_empty_portfolio()

            # Aggregate by scope and facility
            scope_1 = sum(c.total_emissions_kgco2e for c in calculations if c.scope == "scope1")
            scope_2 = sum(c.total_emissions_kgco2e for c in calculations if c.scope == "scope2")
            scope_3 = sum(c.total_emissions_kgco2e for c in calculations if c.scope == "scope3")
            total = scope_1 + scope_2 + scope_3

            # Convert to tCO2e
            total_tco2e = float(total / Decimal("1000"))

            # Get facility breakdown
            facilities_data = self.db.query(
                EmissionsSource.facility_id,
                func.sum(EmissionsCalculation.total_emissions_kgco2e).label("total")
            ).join(
                EmissionsSource
            ).filter(
                EmissionsCalculation.tenant_id == tenant_id,
                EmissionsCalculation.status == "approved"
            ).group_by(
                EmissionsSource.facility_id
            ).all()

            facility_breakdown = []
            for facility_id, emissions_kg in facilities_data:
                if facility_id:
                    facility = self.db.query(Facility).filter_by(id=facility_id).first()
                    facility_breakdown.append({
                        "facility_id": str(facility_id),
                        "facility_name": facility.name if facility else "Unknown",
                        "emissions_tco2e": float(emissions_kg / Decimal("1000")),
                        "pct_of_total": float((emissions_kg / total * 100) if total > 0 else 0)
                    })

            # Sort by emissions
            facility_breakdown.sort(key=lambda x: x["emissions_tco2e"], reverse=True)

            return {
                "tenant_id": str(tenant_id),
                "period": period,
                "date_range": {
                    "start": start_date.isoformat(),
                    "end": end_date.isoformat()
                },
                "total_emissions_tco2e": total_tco2e,
                "scope_breakdown": {
                    "scope_1_tco2e": float(scope_1 / Decimal("1000")),
                    "scope_2_tco2e": float(scope_2 / Decimal("1000")),
                    "scope_3_tco2e": float(scope_3 / Decimal("1000")),
                    "scope_1_pct": float((scope_1 / total * 100) if total > 0 else 0),
                    "scope_2_pct": float((scope_2 / total * 100) if total > 0 else 0),
                    "scope_3_pct": float((scope_3 / total * 100) if total > 0 else 0),
                },
                "facility_breakdown": facility_breakdown,
                "facility_count": len(facility_breakdown),
                "calculation_count": len(calculations)
            }

        except Exception as e:
            logger.error(f"Error getting portfolio overview: {str(e)}")
            raise

    def _get_facility_energy(
        self,
        facility_id: UUID,
        start_date: datetime,
        end_date: datetime
    ) -> float:
        """Get total facility energy consumption in kWh"""
        try:
            readings = self.db.query(
                func.sum(TelemetryReading.value)
            ).join(
                EmissionsSource,
                TelemetryReading.meter_id == EmissionsSource.id
            ).filter(
                EmissionsSource.facility_id == facility_id,
                TelemetryReading.timestamp >= start_date,
                TelemetryReading.timestamp <= end_date,
                TelemetryReading.unit == "kWh"
            ).scalar()

            return float(readings) if readings else 0

        except Exception as e:
            logger.warning(f"Error getting facility energy: {str(e)}")
            return 0

    def _get_latest_pue(self, facility_id: UUID) -> Optional[float]:
        """Get latest PUE value for facility"""
        try:
            pue_snapshot = self.db.query(KPISnapshot).join(
                KPISnapshot.kpi
            ).filter(
                KPISnapshot.kpi.has(kpi_name="PUE"),
                # Join condition for facility would be here
            ).order_by(
                KPISnapshot.snapshot_date.desc()
            ).first()

            if pue_snapshot:
                return float(pue_snapshot.calculated_value)

            return None

        except Exception as e:
            logger.warning(f"Error getting PUE: {str(e)}")
            return None

    def _get_renewable_percentage(
        self,
        facility_id: UUID,
        start_date: datetime,
        end_date: datetime
    ) -> float:
        """Get renewable energy percentage"""
        try:
            # This would depend on your data model for tracking renewable vs. non-renewable
            # For now, returning placeholder
            return 0.0

        except Exception as e:
            logger.warning(f"Error getting renewable percentage: {str(e)}")
            return 0.0

    def _get_emissions_trend(
        self,
        tenant_id: UUID,
        facility_id: UUID,
        days: int = 30
    ) -> List[Dict]:
        """Get daily emissions trend"""
        try:
            end_date = datetime.utcnow()
            start_date = end_date - timedelta(days=days)

            # Query calculations grouped by day
            calculations = self.db.query(
                func.date(EmissionsCalculation.calculation_period_start).label("date"),
                EmissionsCalculation.scope,
                func.sum(EmissionsCalculation.total_emissions_kgco2e).label("emissions")
            ).join(
                EmissionsSource
            ).filter(
                EmissionsSource.facility_id == facility_id,
                EmissionsSource.tenant_id == tenant_id,
                EmissionsCalculation.calculation_period_start >= start_date
            ).group_by(
                func.date(EmissionsCalculation.calculation_period_start),
                EmissionsCalculation.scope
            ).all()

            # Reorganize data for charting
            daily_data = {}
            for calc_date, scope, emissions in calculations:
                if calc_date not in daily_data:
                    daily_data[calc_date] = {"date": calc_date.isoformat(), "scope_1": 0, "scope_2": 0, "scope_3": 0, "total": 0}

                scope_key = scope.replace("scope", "scope_")
                daily_data[calc_date][scope_key] = float(emissions / Decimal("1000"))
                daily_data[calc_date]["total"] += float(emissions / Decimal("1000"))

            return sorted(daily_data.values(), key=lambda x: x["date"])

        except Exception as e:
            logger.warning(f"Error getting emissions trend: {str(e)}")
            return []

    def _get_top_emitting_sources(
        self,
        facility_id: UUID,
        start_date: datetime,
        end_date: datetime,
        limit: int = 10
    ) -> List[Dict]:
        """Get top emitting sources at a facility"""
        try:
            sources_data = self.db.query(
                EmissionsSource.id,
                EmissionsSource.source_name,
                EmissionsSource.source_type,
                func.sum(EmissionsCalculation.total_emissions_kgco2e).label("total_emissions")
            ).join(
                EmissionsCalculation
            ).filter(
                EmissionsSource.facility_id == facility_id,
                EmissionsCalculation.calculation_period_end >= start_date,
                EmissionsCalculation.calculation_period_start <= end_date
            ).group_by(
                EmissionsSource.id,
                EmissionsSource.source_name,
                EmissionsSource.source_type
            ).order_by(
                func.sum(EmissionsCalculation.total_emissions_kgco2e).desc()
            ).limit(limit).all()

            result = []
            for source_id, source_name, source_type, emissions in sources_data:
                result.append({
                    "source_id": str(source_id),
                    "source_name": source_name,
                    "source_type": source_type,
                    "emissions_tco2e": float(emissions / Decimal("1000")) if emissions else 0
                })

            return result

        except Exception as e:
            logger.warning(f"Error getting top emitting sources: {str(e)}")
            return []

    def _get_empty_dashboard(self) -> Dict:
        """Return empty dashboard structure"""
        return {
            "facility_id": None,
            "period": "current_month",
            "emissions": {
                "total_tco2e": 0,
                "scope_1_tco2e": 0,
                "scope_2_tco2e": 0,
                "scope_3_tco2e": 0,
            },
            "metrics": {
                "carbon_intensity_gco2e_kwh": 0,
                "pue": None,
                "renewable_pct": 0
            },
            "breakdown": [],
            "trend_30d": [],
            "top_sources": []
        }

    def _get_empty_portfolio(self) -> Dict:
        """Return empty portfolio structure"""
        return {
            "tenant_id": None,
            "period": "current_year",
            "total_emissions_tco2e": 0,
            "scope_breakdown": {
                "scope_1_tco2e": 0,
                "scope_2_tco2e": 0,
                "scope_3_tco2e": 0,
            },
            "facility_breakdown": [],
            "facility_count": 0
        }
