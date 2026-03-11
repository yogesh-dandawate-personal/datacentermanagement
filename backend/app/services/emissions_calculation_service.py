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
        created_by_user_id: Optional[UUID] = None,
        scope_3_category: Optional[str] = None
    ) -> Dict:
        """
        Calculate Scope 3 (Indirect) emissions with category support

        Scope 3 Categories:
        - supply_chain: Upstream transportation and supply chain
        - business_travel: Employee business travel (air, rail, car)
        - employee_commute: Employee commuting emissions
        - waste_disposal: Waste management and disposal
        - purchased_goods: Lifecycle of purchased goods
        - franchises: Franchisee operations
        - investments: Downstream investments
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

            # Get Scope 3 factor (by category if specified)
            factor_query = self.db.query(EmissionFactor).filter(
                EmissionFactor.id == source.emission_factor_id,
                EmissionFactor.factor_type.like("scope3%"),
                EmissionFactor.is_active == True
            )

            if scope_3_category:
                factor_query = factor_query.filter(
                    EmissionFactor.factor_type.like(f"%{scope_3_category}%")
                )

            factor = factor_query.first()

            if not factor:
                raise ValueError(f"No Scope 3 factor found for {source.source_type}")

            # Calculate based on category
            if scope_3_category == "supply_chain":
                result = self._calculate_scope_3_supply_chain(
                    activity_data_records, source, factor, period_start, period_end,
                    tenant_id, created_by_user_id
                )
            elif scope_3_category == "business_travel":
                result = self._calculate_scope_3_business_travel(
                    activity_data_records, source, factor, period_start, period_end,
                    tenant_id, created_by_user_id
                )
            else:
                # Default generic calculation
                result = self._calculate_scope_3_generic(
                    activity_data_records, source, factor, period_start, period_end,
                    tenant_id, created_by_user_id
                )

            return result

        except Exception as e:
            logger.error(f"Error calculating Scope 3 emissions: {str(e)}")
            self.db.rollback()
            raise

    def _calculate_scope_3_supply_chain(
        self,
        activity_data: List,
        source: EmissionsSource,
        factor: EmissionFactor,
        period_start: datetime,
        period_end: datetime,
        tenant_id: UUID,
        created_by_user_id: Optional[UUID] = None
    ) -> Dict:
        """
        Calculate Scope 3 supply chain emissions

        Includes:
        - Purchased goods and services (kg or units)
        - Capital goods (equipment, facilities)
        - Upstream transportation (kg-miles, ton-miles)
        - Business travel (miles, kg)
        - Waste disposal (kg waste)
        - Employee commuting (miles, kg)
        """
        total_emissions = Decimal("0")
        calculation_details = []
        supplier_breakdown = {}

        for activity in activity_data:
            # Extract supplier info from metadata if available
            supplier_id = getattr(activity, 'source_metadata', {}).get('supplier_id', 'unknown')

            # Calculate emissions with lifecycle factors
            base_emissions = activity.activity_value * factor.value

            # Apply intensity multipliers based on supply chain stage
            supply_stage = getattr(activity, 'source_metadata', {}).get('supply_stage', 'manufacturing')
            stage_multiplier = {
                'raw_material': Decimal('1.5'),  # +50% for extraction
                'manufacturing': Decimal('1.0'),  # Base
                'transportation': Decimal('0.3'),  # -70% transport is separate
                'distribution': Decimal('0.2'),  # -80% distribution is separate
                'retail': Decimal('0.1'),   # -90% retail markup
            }.get(supply_stage, Decimal('1.0'))

            final_emissions = base_emissions * stage_multiplier
            total_emissions += final_emissions

            if supplier_id not in supplier_breakdown:
                supplier_breakdown[supplier_id] = Decimal('0')
            supplier_breakdown[supplier_id] += final_emissions

            calculation_details.append({
                "activity_data_id": str(activity.id),
                "source_type": source.source_type,
                "supplier_id": supplier_id,
                "supply_stage": supply_stage,
                "activity_value": float(activity.activity_value),
                "base_emissions_kgco2e": float(base_emissions),
                "adjusted_emissions_kgco2e": float(final_emissions),
                "stage_multiplier": float(stage_multiplier)
            })

        # Create calculation
        calculation = EmissionsCalculation(
            tenant_id=tenant_id,
            source_id=source.id,
            organization_id=source.organization_id,
            calculation_period_start=period_start,
            calculation_period_end=period_end,
            scope="scope3",
            scope_3_category="supply_chain",
            total_emissions_kgco2e=total_emissions,
            calculation_method="supply_chain_lifecycle",
            factor_used_id=factor.id,
            status="draft",
            created_by=created_by_user_id,
            calculation_breakdown={"suppliers": {str(k): float(v) for k, v in supplier_breakdown.items()}}
        )
        self.db.add(calculation)
        self.db.commit()

        logger.info(f"Calculated Scope 3 supply chain emissions: {total_emissions} kgCO2e from {len(supplier_breakdown)} suppliers")

        return {
            "calculation_id": str(calculation.id),
            "category": "supply_chain",
            "total_emissions_kgco2e": float(total_emissions),
            "total_emissions_tco2e": float(total_emissions / Decimal("1000")),
            "suppliers_count": len(supplier_breakdown),
            "top_suppliers": sorted(
                [(k, float(v)) for k, v in supplier_breakdown.items()],
                key=lambda x: x[1], reverse=True
            )[:5],
            "calculation_details": calculation_details,
            "records_processed": len(activity_data),
            "status": "success"
        }

    def _calculate_scope_3_business_travel(
        self,
        activity_data: List,
        source: EmissionsSource,
        factor: EmissionFactor,
        period_start: datetime,
        period_end: datetime,
        tenant_id: UUID,
        created_by_user_id: Optional[UUID] = None
    ) -> Dict:
        """
        Calculate Scope 3 business travel emissions

        Travel modes:
        - Air travel (short/medium/long haul)
        - Rail travel
        - Car rental
        - Personal vehicle reimbursement
        - Hotel stays (indirect)

        Formula: Distance/Duration × Mode-specific emission factor
        """
        total_emissions = Decimal("0")
        calculation_details = []
        travel_breakdown = {"air": Decimal("0"), "rail": Decimal("0"), "car": Decimal("0"), "other": Decimal("0")}

        for activity in activity_data:
            travel_mode = getattr(activity, 'source_metadata', {}).get('travel_mode', 'other').lower()
            distance_km = float(activity.activity_value)

            # Mode-specific emission factors (gCO2e per km)
            mode_factors = {
                'air_short_haul': Decimal('0.255'),  # Short haul: <463 km
                'air_medium_haul': Decimal('0.195'),  # Medium haul: 463-3700 km
                'air_long_haul': Decimal('0.195'),   # Long haul: >3700 km
                'rail': Decimal('0.041'),  # Rail: very low emissions
                'car_petrol': Decimal('0.192'),  # Petrol car
                'car_diesel': Decimal('0.171'),  # Diesel car
                'car_hybrid': Decimal('0.089'),  # Hybrid car
                'car_electric': Decimal('0.050'),  # EV (grid-dependent)
                'bus': Decimal('0.089'),  # Bus
                'taxi': Decimal('0.192'),  # Taxi
            }

            # Determine emission factor based on travel mode
            if travel_mode.startswith('air'):
                if distance_km < 463:
                    ef = mode_factors.get('air_short_haul', factor.value)
                    haul_type = 'short_haul'
                elif distance_km < 3700:
                    ef = mode_factors.get('air_medium_haul', factor.value)
                    haul_type = 'medium_haul'
                else:
                    ef = mode_factors.get('air_long_haul', factor.value)
                    haul_type = 'long_haul'

                category = 'air'
            elif travel_mode == 'rail':
                ef = mode_factors.get('rail', factor.value)
                category = 'rail'
                haul_type = None
            elif travel_mode.startswith('car'):
                car_type = getattr(activity, 'source_metadata', {}).get('car_type', 'petrol')
                ef = mode_factors.get(f'car_{car_type}', mode_factors['car_petrol'])
                category = 'car'
                haul_type = car_type
            else:
                ef = factor.value
                category = 'other'
                haul_type = travel_mode

            # Calculate emissions: distance (km) × factor (gCO2e/km) = gCO2e → kgCO2e
            emissions_kgco2e = Decimal(str(distance_km)) * ef / Decimal('1000')
            total_emissions += emissions_kgco2e
            travel_breakdown[category] += emissions_kgco2e

            # Add radiative forcing index (RFI) for air travel (multiplier for altitude effects)
            if category == 'air':
                rfi_multiplier = Decimal('2.7')  # Average RFI from ICAO
                rfi_additional = emissions_kgco2e * (rfi_multiplier - 1)
                total_emissions += rfi_additional
                travel_breakdown['air'] += rfi_additional

                calculation_details.append({
                    "activity_data_id": str(activity.id),
                    "travel_mode": f"air_{haul_type}",
                    "distance_km": distance_km,
                    "base_emissions_kgco2e": float(emissions_kgco2e),
                    "rfi_additional_kgco2e": float(rfi_additional),
                    "total_with_rfi_kgco2e": float(emissions_kgco2e + rfi_additional),
                    "emission_factor_gco2e_per_km": float(ef)
                })
            else:
                calculation_details.append({
                    "activity_data_id": str(activity.id),
                    "travel_mode": category if not haul_type else f"{category}_{haul_type}",
                    "distance_km": distance_km,
                    "emissions_kgco2e": float(emissions_kgco2e),
                    "emission_factor_gco2e_per_km": float(ef)
                })

        # Create calculation
        calculation = EmissionsCalculation(
            tenant_id=tenant_id,
            source_id=source.id,
            organization_id=source.organization_id,
            calculation_period_start=period_start,
            calculation_period_end=period_end,
            scope="scope3",
            scope_3_category="business_travel",
            total_emissions_kgco2e=total_emissions,
            calculation_method="business_travel_distance_based",
            factor_used_id=factor.id,
            status="draft",
            created_by=created_by_user_id,
            calculation_breakdown={
                "by_mode": {str(k): float(v) for k, v in travel_breakdown.items()}
            }
        )
        self.db.add(calculation)
        self.db.commit()

        logger.info(f"Calculated Scope 3 business travel emissions: {total_emissions} kgCO2e")

        return {
            "calculation_id": str(calculation.id),
            "category": "business_travel",
            "total_emissions_kgco2e": float(total_emissions),
            "total_emissions_tco2e": float(total_emissions / Decimal("1000")),
            "breakdown_by_mode": {k: float(v) for k, v in travel_breakdown.items()},
            "calculation_details": calculation_details,
            "records_processed": len(activity_data),
            "status": "success",
            "note": "Includes radiative forcing index (RFI) multiplier of 2.7x for air travel altitude effects"
        }

    def _calculate_scope_3_generic(
        self,
        activity_data: List,
        source: EmissionsSource,
        factor: EmissionFactor,
        period_start: datetime,
        period_end: datetime,
        tenant_id: UUID,
        created_by_user_id: Optional[UUID] = None
    ) -> Dict:
        """Generic Scope 3 calculation (fallback)"""
        total_emissions = Decimal("0")
        calculation_details = []

        for activity in activity_data:
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
            source_id=source.id,
            organization_id=source.organization_id,
            calculation_period_start=period_start,
            calculation_period_end=period_end,
            scope="scope3",
            total_emissions_kgco2e=total_emissions,
            calculation_method="generic_scope3",
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
            "records_processed": len(activity_data),
            "status": "success"
        }

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
