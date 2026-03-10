"""
Emissions Calculation Service

Implements GHG Protocol Scope 1, 2, 3 calculations and emissions tracking.
Follows EPA and ISO 14064 standards.
"""

from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timedelta
from decimal import Decimal
from typing import Tuple, Dict, List, Optional
import logging
from uuid import UUID

from app.models import (
    EmissionsSource, EmissionsActivityData, EmissionsCalculation,
    EmissionsCalculationDetail, EmissionFactor, Tenant
)

logger = logging.getLogger(__name__)


class EmissionsCalculationService:
    """Service for calculating Scope 1, 2, 3 emissions"""

    def __init__(self, db: Session):
        self.db = db

    def calculate_scope_1_emissions(
        self,
        tenant_id: UUID,
        source_id: UUID,
        period_start: datetime,
        period_end: datetime,
        created_by_user_id: Optional[UUID] = None
    ) -> Dict:
        """
        Calculate Scope 1 (Direct) emissions

        Scope 1 includes:
        - Fuel combustion (natural gas, oil, coal)
        - Process emissions (refrigerant leakage, chemical reactions)
        - Backup generator emissions

        Formula: Activity Data × Emission Factor
        Unit: kg CO2e
        """
        try:
            # Get emission source
            source = self.db.query(EmissionsSource).filter(
                EmissionsSource.id == source_id,
                EmissionsSource.tenant_id == tenant_id
            ).first()

            if not source:
                raise ValueError(f"Emission source {source_id} not found")

            if source.scope != "scope1":
                raise ValueError(f"Source {source_id} is not a Scope 1 source")

            # Query activity data for period
            activity_data_records = self.db.query(EmissionsActivityData).filter(
                EmissionsActivityData.source_id == source_id,
                EmissionsActivityData.tenant_id == tenant_id,
                EmissionsActivityData.timestamp >= period_start,
                EmissionsActivityData.timestamp <= period_end,
                EmissionsActivityData.validation_status == "valid"
            ).all()

            if not activity_data_records:
                logger.warning(f"No valid activity data found for source {source_id} in period")
                return {
                    "total_emissions_kgco2e": Decimal("0"),
                    "calculation_details": [],
                    "records_processed": 0,
                    "status": "no_data"
                }

            # Get active emission factor
            factor = self.db.query(EmissionFactor).filter(
                EmissionFactor.id == source.emission_factor_id,
                EmissionFactor.is_active == True
            ).first()

            if not factor:
                raise ValueError(f"No active emission factor found for source {source_id}")

            # Calculate emissions
            total_emissions = Decimal("0")
            calculation_details = []

            for activity in activity_data_records:
                emissions = activity.activity_value * factor.value
                total_emissions += emissions

                calculation_details.append({
                    "activity_data_id": str(activity.id),
                    "activity_value": float(activity.activity_value),
                    "activity_unit": activity.activity_unit,
                    "factor_id": str(factor.id),
                    "factor_value": float(factor.value),
                    "emissions_kgco2e": float(emissions)
                })

            # Create calculation record
            calculation = EmissionsCalculation(
                tenant_id=tenant_id,
                source_id=source_id,
                organization_id=source.organization_id,
                calculation_period_start=period_start,
                calculation_period_end=period_end,
                scope="scope1",
                total_emissions_kgco2e=total_emissions,
                calculation_method="sum",
                factor_used_id=factor.id,
                status="draft",
                created_by=created_by_user_id
            )
            self.db.add(calculation)
            self.db.flush()

            # Create detail records
            for detail_data in calculation_details:
                activity = next(
                    a for a in activity_data_records
                    if str(a.id) == detail_data["activity_data_id"]
                )
                detail = EmissionsCalculationDetail(
                    calculation_id=calculation.id,
                    activity_data_id=activity.id,
                    factor_id=factor.id,
                    factor_value=factor.value,
                    activity_value=activity.activity_value,
                    activity_unit=activity.activity_unit,
                    emissions_kgco2e=detail_data["emissions_kgco2e"]
                )
                self.db.add(detail)

            self.db.commit()

            logger.info(
                f"Calculated Scope 1 emissions for source {source_id}: "
                f"{total_emissions} kgCO2e across {len(activity_data_records)} records"
            )

            return {
                "calculation_id": str(calculation.id),
                "total_emissions_kgco2e": float(total_emissions),
                "total_emissions_tco2e": float(total_emissions / Decimal("1000")),
                "calculation_details": calculation_details,
                "records_processed": len(activity_data_records),
                "status": "success"
            }

        except Exception as e:
            logger.error(f"Error calculating Scope 1 emissions: {str(e)}")
            self.db.rollback()
            raise

    def calculate_scope_2_location_based(
        self,
        tenant_id: UUID,
        source_id: UUID,
        period_start: datetime,
        period_end: datetime,
        created_by_user_id: Optional[UUID] = None
    ) -> Dict:
        """
        Calculate Scope 2 (Location-Based) emissions

        Uses regional grid mix emission factors
        Formula: Grid electricity consumption × Regional grid factor
        """
        try:
            source = self.db.query(EmissionsSource).filter(
                EmissionsSource.id == source_id,
                EmissionsSource.tenant_id == tenant_id
            ).first()

            if not source or source.scope != "scope2":
                raise ValueError(f"Invalid Scope 2 source: {source_id}")

            # Query electricity consumption data
            activity_data_records = self.db.query(EmissionsActivityData).filter(
                EmissionsActivityData.source_id == source_id,
                EmissionsActivityData.tenant_id == tenant_id,
                EmissionsActivityData.timestamp >= period_start,
                EmissionsActivityData.timestamp <= period_end,
                EmissionsActivityData.validation_status == "valid"
            ).all()

            if not activity_data_records:
                return {
                    "total_emissions_kgco2e": Decimal("0"),
                    "calculation_details": [],
                    "records_processed": 0,
                    "status": "no_data"
                }

            # Get location-based grid factor
            factor = self.db.query(EmissionFactor).filter(
                EmissionFactor.id == source.emission_factor_id,
                EmissionFactor.factor_type == "electricity",
                EmissionFactor.is_active == True
            ).first()

            if not factor:
                raise ValueError(f"No grid factor found for {source.location}")

            # Calculate emissions
            total_emissions = Decimal("0")
            calculation_details = []

            for activity in activity_data_records:
                # Electricity in kWh × Grid factor (kgCO2e/kWh)
                emissions = activity.activity_value * factor.value
                total_emissions += emissions
                calculation_details.append({
                    "activity_data_id": str(activity.id),
                    "activity_value": float(activity.activity_value),
                    "grid_location": source.location,
                    "factor_value": float(factor.value),
                    "emissions_kgco2e": float(emissions)
                })

            # Create calculation
            calculation = EmissionsCalculation(
                tenant_id=tenant_id,
                source_id=source_id,
                organization_id=source.organization_id,
                calculation_period_start=period_start,
                calculation_period_end=period_end,
                scope="scope2",
                total_emissions_kgco2e=total_emissions,
                calculation_method="location_based",
                factor_used_id=factor.id,
                status="draft",
                created_by=created_by_user_id
            )
            self.db.add(calculation)
            self.db.commit()

            logger.info(f"Calculated Scope 2 (location-based) emissions: {total_emissions} kgCO2e")

            return {
                "calculation_id": str(calculation.id),
                "total_emissions_kgco2e": float(total_emissions),
                "total_emissions_tco2e": float(total_emissions / Decimal("1000")),
                "calculation_details": calculation_details,
                "records_processed": len(activity_data_records),
                "method": "location_based",
                "status": "success"
            }

        except Exception as e:
            logger.error(f"Error calculating Scope 2 (location-based): {str(e)}")
            self.db.rollback()
            raise

    def calculate_scope_3_emissions(
        self,
        tenant_id: UUID,
        source_id: UUID,
        period_start: datetime,
        period_end: datetime,
        created_by_user_id: Optional[UUID] = None
    ) -> Dict:
        """
        Calculate Scope 3 (Indirect) emissions

        Includes:
        - Upstream transportation
        - Waste disposal
        - Business travel
        - Employee commuting
        - Supply chain emissions
        """
        try:
            source = self.db.query(EmissionsSource).filter(
                EmissionsSource.id == source_id,
                EmissionsSource.tenant_id == tenant_id
            ).first()

            if not source or source.scope != "scope3":
                raise ValueError(f"Invalid Scope 3 source: {source_id}")

            # Query activity data
            activity_data_records = self.db.query(EmissionsActivityData).filter(
                EmissionsActivityData.source_id == source_id,
                EmissionsActivityData.tenant_id == tenant_id,
                EmissionsActivityData.timestamp >= period_start,
                EmissionsActivityData.timestamp <= period_end,
                EmissionsActivityData.validation_status == "valid"
            ).all()

            if not activity_data_records:
                return {
                    "total_emissions_kgco2e": Decimal("0"),
                    "calculation_details": [],
                    "status": "no_data"
                }

            # Get Scope 3 factor
            factor = self.db.query(EmissionFactor).filter(
                EmissionFactor.id == source.emission_factor_id,
                EmissionFactor.factor_type.like("scope3%"),
                EmissionFactor.is_active == True
            ).first()

            if not factor:
                raise ValueError(f"No Scope 3 factor found for {source.source_type}")

            # Calculate
            total_emissions = Decimal("0")
            calculation_details = []

            for activity in activity_data_records:
                emissions = activity.activity_value * factor.value
                total_emissions += emissions
                calculation_details.append({
                    "activity_data_id": str(activity.id),
                    "source_type": source.source_type,
                    "activity_value": float(activity.activity_value),
                    "emissions_kgco2e": float(emissions)
                })

            # Create calculation
            calculation = EmissionsCalculation(
                tenant_id=tenant_id,
                source_id=source_id,
                organization_id=source.organization_id,
                calculation_period_start=period_start,
                calculation_period_end=period_end,
                scope="scope3",
                total_emissions_kgco2e=total_emissions,
                calculation_method="sum",
                factor_used_id=factor.id,
                status="draft",
                created_by=created_by_user_id
            )
            self.db.add(calculation)
            self.db.commit()

            logger.info(f"Calculated Scope 3 emissions: {total_emissions} kgCO2e")

            return {
                "calculation_id": str(calculation.id),
                "total_emissions_kgco2e": float(total_emissions),
                "total_emissions_tco2e": float(total_emissions / Decimal("1000")),
                "calculation_details": calculation_details,
                "records_processed": len(activity_data_records),
                "status": "success"
            }

        except Exception as e:
            logger.error(f"Error calculating Scope 3 emissions: {str(e)}")
            self.db.rollback()
            raise

    def get_portfolio_emissions(
        self,
        tenant_id: UUID,
        period_start: datetime,
        period_end: datetime
    ) -> Dict:
        """Get aggregate emissions across all sources for organization"""
        try:
            calculations = self.db.query(EmissionsCalculation).filter(
                EmissionsCalculation.tenant_id == tenant_id,
                EmissionsCalculation.calculation_period_end >= period_start,
                EmissionsCalculation.calculation_period_start <= period_end,
                EmissionsCalculation.status == "approved"
            ).all()

            if not calculations:
                return {
                    "scope_1": Decimal("0"),
                    "scope_2": Decimal("0"),
                    "scope_3": Decimal("0"),
                    "total": Decimal("0")
                }

            scope_1 = sum(c.total_emissions_kgco2e for c in calculations if c.scope == "scope1")
            scope_2 = sum(c.total_emissions_kgco2e for c in calculations if c.scope == "scope2")
            scope_3 = sum(c.total_emissions_kgco2e for c in calculations if c.scope == "scope3")
            total = scope_1 + scope_2 + scope_3

            return {
                "scope_1_kgco2e": float(scope_1),
                "scope_2_kgco2e": float(scope_2),
                "scope_3_kgco2e": float(scope_3),
                "total_kgco2e": float(total),
                "total_tco2e": float(total / Decimal("1000")),
                "scope_1_pct": float((scope_1 / total * 100) if total > 0 else 0),
                "scope_2_pct": float((scope_2 / total * 100) if total > 0 else 0),
                "scope_3_pct": float((scope_3 / total * 100) if total > 0 else 0),
            }

        except Exception as e:
            logger.error(f"Error getting portfolio emissions: {str(e)}")
            raise

    def approve_calculation(
        self,
        tenant_id: UUID,
        calculation_id: UUID,
        approved_by_user_id: UUID,
        approval_notes: Optional[str] = None
    ) -> Dict:
        """Approve a completed calculation"""
        try:
            calculation = self.db.query(EmissionsCalculation).filter(
                EmissionsCalculation.id == calculation_id,
                EmissionsCalculation.tenant_id == tenant_id
            ).first()

            if not calculation:
                raise ValueError(f"Calculation {calculation_id} not found")

            calculation.status = "approved"
            calculation.approved_by = approved_by_user_id
            calculation.approved_at = datetime.utcnow()
            calculation.approval_notes = approval_notes

            self.db.commit()

            logger.info(f"Approved calculation {calculation_id}")

            return {
                "calculation_id": str(calculation.id),
                "status": calculation.status,
                "total_emissions_tco2e": float(calculation.total_emissions_kgco2e / Decimal("1000"))
            }

        except Exception as e:
            logger.error(f"Error approving calculation: {str(e)}")
            self.db.rollback()
            raise
