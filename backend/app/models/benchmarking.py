"""
Benchmarking Models for Sprint 9

Implements:
- Benchmark: Industry benchmarks by sector and size
- ComparisonResult: Peer comparison results
- BenchmarkGap: Gap analysis to targets
- PeerGroup: Peer group definitions
"""

from sqlalchemy import Column, String, DateTime, Boolean, ForeignKey, JSON, Integer, Text, Numeric
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

from app.models import Base, UUID


class Benchmark(Base):
    """Industry and regional benchmarks"""
    __tablename__ = "benchmarks"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True)

    benchmark_name = Column(String(255), nullable=False, index=True)
    metric_type = Column(String(100), nullable=False, index=True)  # pue, cue, wue, emissions_intensity

    # Segmentation
    industry = Column(String(100), index=True)  # data_center, manufacturing, healthcare
    sector = Column(String(100))  # cloud, colocation, enterprise
    region = Column(String(100), index=True)  # north_america, europe, apac, global
    organization_size = Column(String(50))  # small, medium, large, enterprise

    # Benchmark values
    average_value = Column(Numeric(18, 6), nullable=False)
    median_value = Column(Numeric(18, 6))
    best_in_class = Column(Numeric(18, 6))  # Top 10%
    worst_in_class = Column(Numeric(18, 6))  # Bottom 10%

    # Percentile distribution
    percentile_25 = Column(Numeric(18, 6))
    percentile_50 = Column(Numeric(18, 6))  # Same as median
    percentile_75 = Column(Numeric(18, 6))
    percentile_90 = Column(Numeric(18, 6))

    # Metadata
    unit = Column(String(50))
    sample_size = Column(Integer)  # Number of organizations in benchmark
    data_year = Column(Integer, nullable=False, index=True)
    data_quarter = Column(Integer)  # 1-4

    # Data source
    source_name = Column(String(255))  # Uptime Institute, Green Grid, EPA
    source_url = Column(String(500))
    confidence_level = Column(Numeric(5, 2))  # 0-100%

    is_active = Column(Boolean, default=True, index=True)

    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    tenant = relationship("Tenant")


class ComparisonResult(Base):
    """Peer comparison results"""
    __tablename__ = "comparison_results"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True)
    organization_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True)
    benchmark_id = Column(UUID(as_uuid=True), ForeignKey("benchmarks.id", ondelete="CASCADE"), nullable=False, index=True)

    comparison_date = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)
    period_start = Column(DateTime, nullable=False)
    period_end = Column(DateTime, nullable=False)

    # Organization's value
    organization_value = Column(Numeric(18, 6), nullable=False)
    organization_percentile = Column(Integer)  # 0-100, where organization ranks

    # Comparison to benchmark
    vs_average_delta = Column(Numeric(18, 6))  # Difference from average
    vs_average_percent = Column(Numeric(8, 2))  # % difference from average
    vs_median_delta = Column(Numeric(18, 6))
    vs_median_percent = Column(Numeric(8, 2))
    vs_best_in_class_delta = Column(Numeric(18, 6))
    vs_best_in_class_percent = Column(Numeric(8, 2))

    # Performance rating
    performance_rating = Column(String(50), index=True)  # excellent, good, average, below_average, poor
    rating_description = Column(Text)

    # Peer group comparison
    peer_group_id = Column(UUID(as_uuid=True), ForeignKey("peer_groups.id", ondelete="SET NULL"), nullable=True)
    peer_rank = Column(Integer)  # Rank within peer group (1 = best)
    peer_count = Column(Integer)  # Total peers in group

    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    tenant = relationship("Tenant")
    organization = relationship("Organization")
    benchmark = relationship("Benchmark")
    peer_group = relationship("PeerGroup")


class BenchmarkGap(Base):
    """Gap analysis to benchmark targets"""
    __tablename__ = "benchmark_gaps"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True)
    organization_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True)
    comparison_result_id = Column(UUID(as_uuid=True), ForeignKey("comparison_results.id", ondelete="CASCADE"), nullable=False, index=True)

    gap_type = Column(String(100), nullable=False, index=True)  # to_average, to_best_in_class, to_target

    # Gap metrics
    current_value = Column(Numeric(18, 6), nullable=False)
    target_value = Column(Numeric(18, 6), nullable=False)
    gap_value = Column(Numeric(18, 6), nullable=False)  # Absolute gap
    gap_percentage = Column(Numeric(8, 2), nullable=False)  # % gap

    # Closure plan
    improvement_required = Column(Numeric(18, 6))  # Amount of improvement needed
    estimated_timeline_months = Column(Integer)  # Estimated time to close gap
    difficulty_level = Column(String(20))  # easy, moderate, difficult, very_difficult

    # Improvement recommendations
    recommendations = Column(JSON)  # [{"action": "...", "impact": "high", "effort": "medium"}, ...]

    # Financial impact
    estimated_investment = Column(Numeric(18, 2))  # USD
    estimated_annual_savings = Column(Numeric(18, 2))  # USD
    roi_months = Column(Integer)  # Return on investment period

    # Progress tracking
    status = Column(String(50), default="identified", index=True)  # identified, planned, in_progress, closed
    progress_percentage = Column(Integer, default=0)  # 0-100%

    assigned_to = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)

    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    tenant = relationship("Tenant")
    organization = relationship("Organization")
    comparison_result = relationship("ComparisonResult")
    assigned_user = relationship("User", foreign_keys=[assigned_to])


class PeerGroup(Base):
    """Peer group definitions for comparison"""
    __tablename__ = "peer_groups"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True)

    group_name = Column(String(255), nullable=False, index=True)
    description = Column(Text)

    # Criteria for inclusion
    industry = Column(String(100))
    sector = Column(String(100))
    region = Column(String(100))
    size_range = Column(String(50))  # small, medium, large

    # Custom filters
    custom_criteria = Column(JSON)  # {"annual_revenue": {"min": 10000000, "max": 50000000}, ...}

    # Member organizations
    member_organizations = Column(JSON)  # [{"org_id": "...", "joined_at": "..."}, ...]
    member_count = Column(Integer, default=0)

    # Group statistics
    avg_performance = Column(JSON)  # {"pue": 1.45, "cue": 75, ...}

    is_active = Column(Boolean, default=True)
    is_public = Column(Boolean, default=False)

    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    tenant = relationship("Tenant")
    creator = relationship("User", foreign_keys=[created_by])


class BenchmarkAlert(Base):
    """Alerts when performance deviates from benchmark"""
    __tablename__ = "benchmark_alerts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True)
    organization_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True)
    comparison_result_id = Column(UUID(as_uuid=True), ForeignKey("comparison_results.id", ondelete="CASCADE"), nullable=False, index=True)

    alert_type = Column(String(100), nullable=False, index=True)  # below_average, bottom_quartile, deteriorating_trend

    alert_severity = Column(String(20), nullable=False, index=True)  # info, warning, critical
    alert_message = Column(Text, nullable=False)

    # Alert context
    metric_name = Column(String(100))
    current_value = Column(Numeric(18, 6))
    benchmark_value = Column(Numeric(18, 6))
    deviation_percent = Column(Numeric(8, 2))

    # Notification status
    is_sent = Column(Boolean, default=False)
    sent_at = Column(DateTime)
    acknowledged_at = Column(DateTime)
    acknowledged_by = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)

    resolution_notes = Column(Text)

    created_at = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)

    # Relationships
    tenant = relationship("Tenant")
    organization = relationship("Organization")
    comparison_result = relationship("ComparisonResult")
    acknowledged_by_user = relationship("User", foreign_keys=[acknowledged_by])
