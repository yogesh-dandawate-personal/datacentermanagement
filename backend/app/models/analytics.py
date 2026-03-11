"""
Analytics Models for Sprint 9: Advanced Analytics & Reporting

Implements:
- EmissionsTrend: Historical emissions with forecasting
- EnergyAnalysis: Energy consumption patterns
- WaterUsage: Water metrics and trends
- WasteMetrics: Waste tracking
- SustainabilityScore: Composite ESG scoring
"""

from sqlalchemy import Column, String, DateTime, Boolean, ForeignKey, JSON, Integer, Text, Numeric
# from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

from app.models import Base,UUID


class EmissionsTrend(Base):
    """Historical emissions data with forecasting capabilities"""
    __tablename__ = "emissions_trends"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True)
    organization_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True)

    trend_date = Column(DateTime, nullable=False, index=True)
    period_type = Column(String(50), nullable=False, index=True)  # daily, weekly, monthly, yearly

    # Actual values
    scope_1 = Column(Numeric(18, 6), default=0)
    scope_2 = Column(Numeric(18, 6), default=0)
    scope_3 = Column(Numeric(18, 6), default=0)
    total_emissions = Column(Numeric(18, 6), default=0)

    # Forecasted values (ML-based)
    forecast_scope_1 = Column(Numeric(18, 6))
    forecast_scope_2 = Column(Numeric(18, 6))
    forecast_scope_3 = Column(Numeric(18, 6))
    forecast_total = Column(Numeric(18, 6))
    forecast_confidence = Column(Numeric(5, 2))  # 0-100%

    # Trend metadata
    trend_direction = Column(String(20))  # increasing, decreasing, stable
    percentage_change = Column(Numeric(8, 2))  # % change from previous period
    anomaly_detected = Column(Boolean, default=False)
    anomaly_severity = Column(String(20))  # low, medium, high

    created_at = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    tenant = relationship("Tenant")
    organization = relationship("Organization")


class EnergyAnalysis(Base):
    """Energy consumption pattern analysis"""
    __tablename__ = "energy_analysis"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True)
    organization_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True)

    analysis_date = Column(DateTime, nullable=False, index=True)
    period_start = Column(DateTime, nullable=False)
    period_end = Column(DateTime, nullable=False)

    # Energy metrics
    total_consumption = Column(Numeric(18, 6), nullable=False)  # kWh
    peak_demand = Column(Numeric(18, 6))  # kW
    average_demand = Column(Numeric(18, 6))  # kW
    load_factor = Column(Numeric(5, 2))  # Peak/Average ratio (%)

    # Pattern detection
    peak_hours = Column(JSON)  # [{"hour": 14, "avg_kwh": 1234}, ...]
    off_peak_hours = Column(JSON)
    seasonal_pattern = Column(String(50))  # summer_peak, winter_peak, stable

    # Anomaly detection
    anomalies_detected = Column(Integer, default=0)
    anomaly_details = Column(JSON)  # [{"timestamp": "...", "expected": 100, "actual": 200}, ...]

    # Optimization opportunities
    optimization_score = Column(Numeric(5, 2))  # 0-100, higher is better
    potential_savings_kwh = Column(Numeric(18, 6))
    potential_savings_usd = Column(Numeric(18, 2))

    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    tenant = relationship("Tenant")
    organization = relationship("Organization")


class WaterUsage(Base):
    """Water metrics and trends"""
    __tablename__ = "water_usage"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True)
    organization_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True)
    facility_id = Column(UUID(as_uuid=True), ForeignKey("facilities.id", ondelete="CASCADE"), nullable=True, index=True)

    measurement_date = Column(DateTime, nullable=False, index=True)
    period_type = Column(String(50), nullable=False)  # daily, weekly, monthly

    # Water consumption
    total_volume = Column(Numeric(18, 6), nullable=False)  # Liters
    cooling_water = Column(Numeric(18, 6))
    potable_water = Column(Numeric(18, 6))
    recycled_water = Column(Numeric(18, 6))

    # Efficiency metrics
    wue_ratio = Column(Numeric(8, 4))  # L/kWh
    recycling_rate = Column(Numeric(5, 2))  # % recycled
    waste_water_volume = Column(Numeric(18, 6))

    # Trends
    trend_direction = Column(String(20))  # increasing, decreasing, stable
    percentage_change = Column(Numeric(8, 2))

    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    tenant = relationship("Tenant")
    organization = relationship("Organization")
    facility = relationship("Facility")


class WasteMetrics(Base):
    """Waste tracking and management"""
    __tablename__ = "waste_metrics"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True)
    organization_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True)
    facility_id = Column(UUID(as_uuid=True), ForeignKey("facilities.id", ondelete="CASCADE"), nullable=True, index=True)

    measurement_date = Column(DateTime, nullable=False, index=True)
    period_type = Column(String(50), nullable=False)  # daily, weekly, monthly

    # Waste volumes
    total_waste = Column(Numeric(18, 6), nullable=False)  # kg
    e_waste = Column(Numeric(18, 6))  # Electronic waste
    general_waste = Column(Numeric(18, 6))
    hazardous_waste = Column(Numeric(18, 6))

    # Recycling metrics
    recycled_waste = Column(Numeric(18, 6))
    landfill_waste = Column(Numeric(18, 6))
    recycling_rate = Column(Numeric(5, 2))  # %
    diversion_rate = Column(Numeric(5, 2))  # % diverted from landfill

    # Costs
    disposal_cost = Column(Numeric(12, 2))  # USD
    recycling_revenue = Column(Numeric(12, 2))  # USD

    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    tenant = relationship("Tenant")
    organization = relationship("Organization")
    facility = relationship("Facility")


class SustainabilityScore(Base):
    """Composite sustainability scoring (ESG)"""
    __tablename__ = "sustainability_scores"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True)
    organization_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True)

    score_date = Column(DateTime, nullable=False, index=True)
    score_period = Column(String(50), nullable=False)  # monthly, quarterly, annual

    # Overall scores (0-100)
    overall_score = Column(Numeric(5, 2), nullable=False)
    environmental_score = Column(Numeric(5, 2))
    social_score = Column(Numeric(5, 2))
    governance_score = Column(Numeric(5, 2))

    # Component scores
    emissions_score = Column(Numeric(5, 2))  # Carbon performance
    energy_score = Column(Numeric(5, 2))  # Energy efficiency
    water_score = Column(Numeric(5, 2))  # Water efficiency
    waste_score = Column(Numeric(5, 2))  # Waste management

    # Score metadata
    score_calculation = Column(JSON)  # Details of how score was calculated
    improvement_areas = Column(JSON)  # [{"area": "energy", "current": 70, "target": 85}, ...]
    strengths = Column(JSON)  # [{"area": "recycling", "score": 95}, ...]

    # Benchmarking
    percentile_rank = Column(Integer)  # 0-100, compared to peers
    industry_average = Column(Numeric(5, 2))

    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    tenant = relationship("Tenant")
    organization = relationship("Organization")


class OptimizationOpportunity(Base):
    """ML-identified optimization opportunities"""
    __tablename__ = "optimization_opportunities"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True)
    organization_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True)

    opportunity_type = Column(String(100), nullable=False, index=True)  # energy_peak_shift, hvac_optimization, etc.
    category = Column(String(50), nullable=False)  # energy, water, waste, emissions

    title = Column(String(255), nullable=False)
    description = Column(Text)

    # Impact assessment
    priority = Column(String(20), nullable=False, index=True)  # critical, high, medium, low
    estimated_savings_usd = Column(Numeric(18, 2))
    estimated_savings_kwh = Column(Numeric(18, 6))
    estimated_emissions_reduction = Column(Numeric(18, 6))  # kg CO2e

    # Implementation
    implementation_effort = Column(String(20))  # easy, moderate, difficult
    implementation_cost = Column(Numeric(18, 2))
    payback_period_months = Column(Integer)

    # Status tracking
    status = Column(String(50), default="identified", index=True)  # identified, under_review, planned, implemented, rejected
    assigned_to = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)

    identified_at = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)
    implemented_at = Column(DateTime)

    implementation_notes = Column(Text)

    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    tenant = relationship("Tenant")
    organization = relationship("Organization")
    assigned_user = relationship("User", foreign_keys=[assigned_to])
