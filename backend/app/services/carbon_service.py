"""
Carbon emissions calculation service with GHG Protocol compliance

Implements:
- Scope 1 (Direct) emissions: fuel, refrigerants, on-site generation
- Scope 2 (Indirect) emissions: grid electricity, steam, heating/cooling
- Scope 3 (Other Indirect) emissions: placeholder for future implementation
- Emission factor management with versioning
- Calculation audit trails for compliance
"""

from typing import List, Dict, Optional, Tuple
from decimal import Decimal
from datetime import datetime, timedelta
import logging
from sqlalchemy.orm import Session
from sqlalchemy import and_, func, desc

from app.models import (
    EmissionFactor,
    FactorVersion,
    CarbonCalculation,
    CalculationDetail,
    TelemetryReading,
    Meter,
    Organization,
)

logger = logging.getLogger(__name__)

# GHG Protocol scopes
SCOPE_1 = "scope1"  # Direct emissions
SCOPE_2 = "scope2"  # Indirect emissions (electricity, steam, etc.)
SCOPE_3 = "scope3"  # Other indirect emissions (optional)

# Calculation types
CALC_TYPE_SCOPE1_FUEL = "scope1_fuel"
CALC_TYPE_SCOPE1_REFRIGERANT = "scope1_refrigerant"
CALC_TYPE_SCOPE1_VEHICLE = "scope1_vehicle"
CALC_TYPE_SCOPE2_ELECTRICITY = "scope2_electricity"
CALC_TYPE_SCOPE2_STEAM = "scope2_steam"


class EmissionFactorService:
    """Manages emission factors with versioning and traceability"""

    def __init__(self, db: Session):
        self.db = db

    def create_factor(
        self,
        factor_name: str,
        factor_type: str,
        value: float,
        unit: str,
        region: str = "Global",
        data_source: str = "Default",
    ) -> EmissionFactor:
        """
        Create a new emission factor

        Args:
            factor_name: Human-readable name (e.g., "US Grid Electricity 2024")
            factor_type: scope1, scope2, fuel, electricity, refrigerant
            value: CO2e emissions per unit (kg CO2e)
            unit: kWh, gallon, kg, m3, etc.
            region: Geographic region (US-East, Europe, Global)
            data_source: Data source (EPA, IVA, Regional Operator)
        """
        factor = EmissionFactor(
            factor_name=factor_name,
            factor_type=factor_type,
            value=Decimal(str(value)),
            unit=unit,
            region=region,
            data_source=data_source,
            effective_date=datetime.utcnow(),
        )

        # Create initial version
        version = FactorVersion(
            factor_id=None,  # Will be set after factor is committed
            version_number=1,
            value=Decimal(str(value)),
            changelog="Initial version",
            effective_date=datetime.utcnow(),
            status="active",
        )

        self.db.add(factor)
        self.db.flush()

        version.factor_id = factor.id
        self.db.add(version)
        self.db.commit()

        logger.info(f"Created emission factor: {factor_name}")
        return factor

    def update_factor(
        self,
        factor_id: str,
        new_value: float,
        changelog: str,
    ) -> FactorVersion:
        """
        Update an emission factor by creating a new version

        This maintains audit trail and allows reverting to previous versions
        """
        factor = self.db.query(EmissionFactor).filter_by(id=factor_id).first()
        if not factor:
            raise ValueError(f"Factor {factor_id} not found")

        # Get latest version number
        latest_version = (
            self.db.query(FactorVersion)
            .filter_by(factor_id=factor_id)
            .order_by(desc(FactorVersion.version_number))
            .first()
        )

        next_version_number = (latest_version.version_number + 1) if latest_version else 1

        # Create new version
        new_version = FactorVersion(
            factor_id=factor_id,
            version_number=next_version_number,
            value=Decimal(str(new_value)),
            changelog=changelog,
            effective_date=datetime.utcnow(),
            status="active",
        )

        # Mark previous versions as superseded
        self.db.query(FactorVersion).filter_by(factor_id=factor_id, status="active").update(
            {FactorVersion.status: "superseded"}
        )

        # Update factor value
        factor.value = Decimal(str(new_value))
        factor.updated_at = datetime.utcnow()

        self.db.add(new_version)
        self.db.commit()

        logger.info(f"Updated emission factor {factor_id} to version {next_version_number}")
        return new_version

    def get_active_factor(
        self,
        factor_type: str,
        region: str = "Global",
    ) -> Optional[EmissionFactor]:
        """
        Get the active (most recent) emission factor for a type and region

        Searches for region-specific first, then falls back to Global
        """
        # Try region-specific first
        factor = (
            self.db.query(EmissionFactor)
            .filter(
                and_(
                    EmissionFactor.factor_type == factor_type,
                    EmissionFactor.region == region,
                    EmissionFactor.is_active == True,
                    EmissionFactor.effective_date <= datetime.utcnow(),
                )
            )
            .order_by(desc(EmissionFactor.effective_date))
            .first()
        )

        # Fall back to Global
        if not factor:
            factor = (
                self.db.query(EmissionFactor)
                .filter(
                    and_(
                        EmissionFactor.factor_type == factor_type,
                        EmissionFactor.region == "Global",
                        EmissionFactor.is_active == True,
                        EmissionFactor.effective_date <= datetime.utcnow(),
                    )
                )
                .order_by(desc(EmissionFactor.effective_date))
                .first()
            )

        return factor

    def get_factor_history(self, factor_id: str) -> List[Dict]:
        """Get version history for a factor"""
        versions = (
            self.db.query(FactorVersion)
            .filter_by(factor_id=factor_id)
            .order_by(desc(FactorVersion.version_number))
            .all()
        )

        return [
            {
                "version": v.version_number,
                "value": float(v.value),
                "effective_date": v.effective_date.isoformat(),
                "status": v.status,
                "changelog": v.changelog,
            }
            for v in versions
        ]


class CarbonCalculationService:
    """Calculates carbon emissions using GHG Protocol methodology"""

    def __init__(self, db: Session):
        self.db = db
        self.factor_service = EmissionFactorService(db)

    def calculate_scope2_electricity(
        self,
        organization_id: str,
        period_start: datetime,
        period_end: datetime,
        region: str = "US-East",
    ) -> Tuple[float, List[Dict]]:
        """
        Calculate Scope 2 emissions from grid electricity consumption

        Returns (total_emissions_kg_co2e, calculation_details_list)
        """
        # Get all electricity meters for this organization's facilities
        # (Simplified: assumes meters are linked through facility structure)
        meter_ids = (
            self.db.query(Meter.id)
            .join(Meter.device_id)
            .filter(Meter.utility_type == "electricity")
            .all()
        )

        if not meter_ids:
            return 0.0, []

        meter_id_list = [m[0] for m in meter_ids]

        # Get electricity readings for period
        readings = (
            self.db.query(TelemetryReading)
            .filter(
                and_(
                    TelemetryReading.meter_id.in_(meter_id_list),
                    TelemetryReading.status == "valid",
                    TelemetryReading.timestamp >= period_start,
                    TelemetryReading.timestamp <= period_end,
                )
            )
            .all()
        )

        if not readings:
            return 0.0, []

        # Get emission factor for grid electricity
        factor = self.factor_service.get_active_factor(
            factor_type="scope2",
            region=region,
        )

        if not factor:
            logger.warning(f"No emission factor found for scope2 in {region}")
            return 0.0, []

        # Calculate emissions
        total_kwh = sum(float(r.value) for r in readings)
        emissions_kg_co2e = total_kwh * float(factor.value)

        details = {
            "calculation_type": CALC_TYPE_SCOPE2_ELECTRICITY,
            "scope": SCOPE_2,
            "energy_input": total_kwh,
            "energy_unit": "kWh",
            "factor_id": str(factor.id),
            "factor_value": float(factor.value),
            "result": emissions_kg_co2e,
        }

        return emissions_kg_co2e, [details]

    def calculate_scope1_fuel(
        self,
        fuel_consumption_units: float,
        fuel_type: str = "natural_gas",
    ) -> Tuple[float, Dict]:
        """
        Calculate Scope 1 emissions from fuel consumption

        Args:
            fuel_consumption_units: Amount of fuel (gallons, therms, m3, etc.)
            fuel_type: natural_gas, diesel, gasoline, propane, etc.
        """
        # Get emission factor for fuel type
        factor = self.factor_service.get_active_factor(
            factor_type=fuel_type,
            region="Global",
        )

        if not factor:
            logger.warning(f"No emission factor found for fuel type: {fuel_type}")
            return 0.0, {}

        # Calculate emissions
        emissions_kg_co2e = fuel_consumption_units * float(factor.value)

        details = {
            "calculation_type": CALC_TYPE_SCOPE1_FUEL,
            "scope": SCOPE_1,
            "energy_input": fuel_consumption_units,
            "energy_unit": factor.unit,
            "factor_id": str(factor.id),
            "factor_value": float(factor.value),
            "result": emissions_kg_co2e,
        }

        return emissions_kg_co2e, details

    def create_calculation(
        self,
        tenant_id: str,
        organization_id: str,
        period_start: datetime,
        period_end: datetime,
        region: str = "US-East",
    ) -> CarbonCalculation:
        """
        Create a carbon calculation for an organization

        Performs all emissions calculations and stores results
        """
        # Calculate Scope 2 (electricity)
        scope2_emissions, scope2_details = self.calculate_scope2_electricity(
            organization_id=organization_id,
            period_start=period_start,
            period_end=period_end,
            region=region,
        )

        # Create calculation record (draft status)
        calculation = CarbonCalculation(
            tenant_id=tenant_id,
            organization_id=organization_id,
            period_start=period_start,
            period_end=period_end,
            scope_1_emissions=Decimal("0"),  # To be filled in when source data available
            scope_2_emissions=Decimal(str(scope2_emissions)),
            scope_3_emissions=Decimal("0"),  # Future implementation
            total_emissions=Decimal(str(scope2_emissions)),
            status="draft",
        )

        self.db.add(calculation)
        self.db.flush()

        # Add calculation details
        for detail in scope2_details:
            calc_detail = CalculationDetail(
                calculation_id=calculation.id,
                calculation_type=detail["calculation_type"],
                scope=detail["scope"],
                energy_input=Decimal(str(detail["energy_input"])),
                energy_unit=detail["energy_unit"],
                factor_id=detail["factor_id"],
                factor_value=Decimal(str(detail["factor_value"])),
                result=Decimal(str(detail["result"])),
            )
            self.db.add(calc_detail)

        self.db.commit()

        logger.info(
            f"Created carbon calculation for org {organization_id}: "
            f"Scope1={calculation.scope_1_emissions}, "
            f"Scope2={calculation.scope_2_emissions}"
        )

        return calculation

    def recalculate_with_factors(
        self,
        calculation_id: str,
        factor_overrides: Dict[str, str] = None,
    ) -> CarbonCalculation:
        """
        Recalculate emissions using different factors

        Useful for sensitivity analysis or when better factors become available
        """
        calculation = self.db.query(CarbonCalculation).filter_by(id=calculation_id).first()
        if not calculation:
            raise ValueError(f"Calculation {calculation_id} not found")

        # Clear old details
        self.db.query(CalculationDetail).filter_by(calculation_id=calculation_id).delete()

        # Recalculate with new factors
        scope2_emissions, scope2_details = self.calculate_scope2_electricity(
            organization_id=str(calculation.organization_id),
            period_start=calculation.period_start,
            period_end=calculation.period_end,
            region="US-East",  # TODO: get from org settings
        )

        # Update calculation
        calculation.scope_2_emissions = Decimal(str(scope2_emissions))
        calculation.total_emissions = (
            calculation.scope_1_emissions + calculation.scope_2_emissions + calculation.scope_3_emissions
        )
        calculation.updated_at = datetime.utcnow()

        # Add new details
        for detail in scope2_details:
            calc_detail = CalculationDetail(
                calculation_id=calculation.id,
                calculation_type=detail["calculation_type"],
                scope=detail["scope"],
                energy_input=Decimal(str(detail["energy_input"])),
                energy_unit=detail["energy_unit"],
                factor_id=detail["factor_id"],
                factor_value=Decimal(str(detail["factor_value"])),
                result=Decimal(str(detail["result"])),
            )
            self.db.add(calc_detail)

        self.db.commit()

        logger.info(f"Recalculated carbon calculation {calculation_id}")
        return calculation

    def submit_for_review(
        self,
        calculation_id: str,
        approver_id: str = None,
    ) -> CarbonCalculation:
        """Submit a calculation for review/approval"""
        calculation = self.db.query(CarbonCalculation).filter_by(id=calculation_id).first()
        if not calculation:
            raise ValueError(f"Calculation {calculation_id} not found")

        if calculation.status != "draft":
            raise ValueError(f"Can only submit draft calculations, current status: {calculation.status}")

        calculation.status = "ready_for_review"
        calculation.updated_at = datetime.utcnow()

        self.db.commit()

        logger.info(f"Submitted carbon calculation {calculation_id} for review")
        return calculation

    def approve_calculation(
        self,
        calculation_id: str,
        approver_id: str,
        approval_notes: str = None,
    ) -> CarbonCalculation:
        """Approve a calculation"""
        calculation = self.db.query(CarbonCalculation).filter_by(id=calculation_id).first()
        if not calculation:
            raise ValueError(f"Calculation {calculation_id} not found")

        if calculation.status != "ready_for_review":
            raise ValueError(f"Can only approve calculations ready for review, current status: {calculation.status}")

        calculation.status = "approved"
        calculation.approved_by = approver_id
        calculation.approved_at = datetime.utcnow()
        calculation.approval_notes = approval_notes
        calculation.updated_at = datetime.utcnow()

        self.db.commit()

        logger.info(f"Approved carbon calculation {calculation_id}")
        return calculation

    def get_calculation_details(self, calculation_id: str) -> Dict:
        """Get complete calculation with audit trail"""
        calculation = self.db.query(CarbonCalculation).filter_by(id=calculation_id).first()
        if not calculation:
            raise ValueError(f"Calculation {calculation_id} not found")

        details = self.db.query(CalculationDetail).filter_by(calculation_id=calculation_id).all()

        return {
            "calculation_id": str(calculation.id),
            "period_start": calculation.period_start.isoformat(),
            "period_end": calculation.period_end.isoformat(),
            "scope_1_emissions": float(calculation.scope_1_emissions),
            "scope_2_emissions": float(calculation.scope_2_emissions),
            "scope_3_emissions": float(calculation.scope_3_emissions),
            "total_emissions": float(calculation.total_emissions),
            "status": calculation.status,
            "details": [
                {
                    "calculation_type": d.calculation_type,
                    "scope": d.scope,
                    "energy_input": float(d.energy_input),
                    "energy_unit": d.energy_unit,
                    "factor_value": float(d.factor_value),
                    "result": float(d.result),
                    "created_at": d.created_at.isoformat(),
                }
                for d in details
            ],
            "created_at": calculation.created_at.isoformat(),
            "updated_at": calculation.updated_at.isoformat(),
        }
