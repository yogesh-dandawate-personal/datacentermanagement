# ============================================================================
# SPRINT 15: GENERIC HIERARCHY FRAMEWORK MODELS
# ============================================================================
"""
Generic hierarchy models supporting multiple industry patterns:
- IT/DataCenter: Region → Campus → DataCenter → Building → Floor → Room → Rack → Device
- Corporate: Organization → Division → Department → Team → Individual
- Energy: Portfolio → Plant → Facility → Unit → Equipment
- Real Estate: Portfolio → Region → Campus → Building → Floor → Space
- Supply Chain: Company → Supplier → Site → Department → Process

This framework allows each tenant to select and configure their hierarchy pattern.
"""

from sqlalchemy import Column, String, DateTime, Boolean, ForeignKey, Table, JSON, Integer, Text, Numeric
from . import Base, UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid as uuid_lib


class HierarchyPattern(Base):
    """Configuration for supported hierarchy patterns"""
    __tablename__ = "hierarchy_patterns"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid_lib.uuid4)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True)

    pattern_name = Column(String(100), nullable=False, index=True)  # it_datacenter, corporate, energy, real_estate, supply_chain
    pattern_type = Column(String(50), nullable=False)  # system (predefined), custom (user-created)
    description = Column(Text)

    # Hierarchy structure definition
    levels = Column(JSON, default=list)  # [{level: 1, name: "Region", singular: "region"}, ...]

    is_active = Column(Boolean, default=True, index=True)
    is_default = Column(Boolean, default=False)  # Default for this tenant

    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)

    # Relationships
    tenant = relationship("Tenant")
    creator = relationship("User", foreign_keys=[created_by])
    hierarchy_levels = relationship("HierarchyLevel", back_populates="pattern", cascade="all, delete-orphan")


class HierarchyLevel(Base):
    """Definition of a level within a hierarchy pattern"""
    __tablename__ = "hierarchy_levels"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid_lib.uuid4)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True)
    pattern_id = Column(UUID(as_uuid=True), ForeignKey("hierarchy_patterns.id", ondelete="CASCADE"), nullable=False, index=True)

    level_number = Column(Integer, nullable=False, index=True)  # 1 (root) to N (leaf)
    level_name = Column(String(100), nullable=False)  # Region, Campus, DataCenter, Building, Floor, Room, Rack, Device
    level_singular = Column(String(100), nullable=False)  # region, campus, datacenter (for API naming)

    description = Column(Text)

    # Constraints for this level
    min_children = Column(Integer, default=0)  # Minimum required child entities
    max_children = Column(Integer)  # Maximum allowed (NULL = unlimited)

    # Metadata configuration for this level
    level_metadata = Column(JSON, default=dict)  # Custom fields, validations, etc.

    # Icons and UI configuration
    icon_name = Column(String(50))  # For UI display
    color_code = Column(String(7))  # Hex color for hierarchy visualization

    is_active = Column(Boolean, default=True, index=True)

    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    tenant = relationship("Tenant")
    pattern = relationship("HierarchyPattern", back_populates="hierarchy_levels")
    entities = relationship("HierarchyEntity", back_populates="level", cascade="all, delete-orphan", foreign_keys="HierarchyEntity.hierarchy_level_id")

    __table_args__ = (
        # Ensure level_number is unique within a pattern
        __import__('sqlalchemy').UniqueConstraint('pattern_id', 'level_number', name='uq_pattern_level_number'),
    )


class HierarchyEntity(Base):
    """Generic organizational entity that can represent any level in the hierarchy"""
    __tablename__ = "hierarchy_entities"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid_lib.uuid4)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True)
    hierarchy_pattern_id = Column(UUID(as_uuid=True), ForeignKey("hierarchy_patterns.id", ondelete="CASCADE"), nullable=False, index=True)
    hierarchy_level_id = Column(UUID(as_uuid=True), ForeignKey("hierarchy_levels.id", ondelete="SET NULL"), nullable=False, index=True)

    # Self-referential relationship (parent-child tree)
    parent_id = Column(UUID(as_uuid=True), ForeignKey("hierarchy_entities.id", ondelete="SET NULL"), nullable=True, index=True)

    # Entity details
    name = Column(String(255), nullable=False, index=True)
    slug = Column(String(100), nullable=False)  # URL-friendly identifier
    description = Column(Text)

    # Hierarchy tracking
    hierarchy_level = Column(Integer, nullable=False, index=True)  # Denormalized level_number for performance
    hierarchy_path = Column(String(500), nullable=False, index=True)  # e.g., "region/campus/datacenter" (for queries)
    hierarchy_depth = Column(Integer, nullable=False)  # Distance from root (0 for root)

    # Organization link (for backward compatibility with existing system)
    organization_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id", ondelete="SET NULL"), nullable=True, index=True)

    # Facility link (for backward compatibility)
    facility_id = Column(UUID(as_uuid=True), ForeignKey("facilities.id", ondelete="SET NULL"), nullable=True, index=True)

    # Status tracking
    is_active = Column(Boolean, default=True, index=True)
    status = Column(String(50), default="active", index=True)  # active, inactive, archived, planned

    # Custom attributes (flexible JSON storage)
    entity_metadata = Column(JSON, default=dict)  # {location: {lat: 37.7749, lng: -122.4194}, contact: {...}, etc.}

    # Audit tracking
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    updated_by = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)

    # Relationships
    tenant = relationship("Tenant")
    pattern = relationship("HierarchyPattern")
    level = relationship("HierarchyLevel", back_populates="entities", foreign_keys=[hierarchy_level_id])

    # Self-referential: parent and children
    parent = relationship("HierarchyEntity", remote_side=[id], backref="children", foreign_keys=[parent_id])

    # Backward compatibility relationships
    organization = relationship("Organization", foreign_keys=[organization_id])
    facility = relationship("Facility", foreign_keys=[facility_id])

    creator = relationship("User", foreign_keys=[created_by], backref="hierarchy_entities_created")
    updater = relationship("User", foreign_keys=[updated_by], backref="hierarchy_entities_updated")

    __table_args__ = (
        # Ensure slug is unique within same parent (siblings)
        __import__('sqlalchemy').UniqueConstraint('parent_id', 'slug', name='uq_parent_slug'),
        # Composite index for common queries
        __import__('sqlalchemy').Index('idx_tenant_pattern_level_active', 'tenant_id', 'hierarchy_pattern_id', 'hierarchy_level', 'is_active'),
        # Index for recursive queries
        __import__('sqlalchemy').Index('idx_hierarchy_path', 'hierarchy_path'),
        # Index for organization lookups
        __import__('sqlalchemy').Index('idx_organization_link', 'organization_id'),
    )

    def __repr__(self):
        return f"<HierarchyEntity(id={self.id}, name={self.name}, level={self.hierarchy_level}, parent_id={self.parent_id})>"


class HierarchyMigration(Base):
    """Tracks hierarchy migrations (e.g., Facility → DataCenter rename)"""
    __tablename__ = "hierarchy_migrations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid_lib.uuid4)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True)

    migration_name = Column(String(255), nullable=False, index=True)  # "Facility to DataCenter", etc.
    migration_type = Column(String(50), nullable=False)  # rename, restructure, merge, split
    description = Column(Text)

    from_pattern_id = Column(UUID(as_uuid=True), ForeignKey("hierarchy_patterns.id", ondelete="SET NULL"), nullable=True)
    to_pattern_id = Column(UUID(as_uuid=True), ForeignKey("hierarchy_patterns.id", ondelete="SET NULL"), nullable=True)

    # Migration details (what changed)
    migration_details = Column(JSON, default=dict)  # {old_structure: {...}, new_structure: {...}, mapping: {...}}

    # Progress tracking
    status = Column(String(50), default="planned", index=True)  # planned, in_progress, completed, failed, rolled_back
    entities_affected = Column(Integer, default=0)
    entities_migrated = Column(Integer, default=0)
    entities_failed = Column(Integer, default=0)

    # Timing
    planned_at = Column(DateTime, nullable=True)
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)

    # Audit
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    executed_by = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)

    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    tenant = relationship("Tenant")
    from_pattern = relationship("HierarchyPattern", foreign_keys=[from_pattern_id])
    to_pattern = relationship("HierarchyPattern", foreign_keys=[to_pattern_id])
    creator = relationship("User", foreign_keys=[created_by])
    executor = relationship("User", foreign_keys=[executed_by])
    errors = relationship("HierarchyMigrationError", back_populates="migration", cascade="all, delete-orphan")


class HierarchyMigrationError(Base):
    """Records errors during hierarchy migrations"""
    __tablename__ = "hierarchy_migration_errors"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid_lib.uuid4)
    migration_id = Column(UUID(as_uuid=True), ForeignKey("hierarchy_migrations.id", ondelete="CASCADE"), nullable=False, index=True)

    entity_id = Column(UUID(as_uuid=True), ForeignKey("hierarchy_entities.id", ondelete="SET NULL"), nullable=True, index=True)

    error_type = Column(String(100), nullable=False)  # validation_error, constraint_violation, data_integrity, etc.
    error_message = Column(Text, nullable=False)
    error_context = Column(JSON, default=dict)  # Additional context about the error

    status = Column(String(50), default="open", index=True)  # open, fixed, acknowledged, ignored

    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    resolved_at = Column(DateTime, nullable=True)

    # Relationships
    migration = relationship("HierarchyMigration", back_populates="errors")
    entity = relationship("HierarchyEntity")


class HierarchyAuditLog(Base):
    """Audit trail for all hierarchy changes"""
    __tablename__ = "hierarchy_audit_logs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid_lib.uuid4)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True)

    action = Column(String(50), nullable=False, index=True)  # CREATE, UPDATE, DELETE, RESTRUCTURE, MIGRATE
    entity_type = Column(String(100), nullable=False, index=True)  # hierarchy_entity, hierarchy_level, hierarchy_pattern
    entity_id = Column(UUID(as_uuid=True), nullable=False, index=True)

    # Change details
    old_values = Column(JSON, default=dict)  # Previous state
    new_values = Column(JSON, default=dict)  # New state

    # Actor
    changed_by = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    ip_address = Column(String(45))
    user_agent = Column(String(500))

    reason = Column(Text)  # Why the change was made

    timestamp = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)

    # Relationships
    tenant = relationship("Tenant")
    changed_by_user = relationship("User", foreign_keys=[changed_by])

    __table_args__ = (
        # Index for common queries
        __import__('sqlalchemy').Index('idx_audit_tenant_entity', 'tenant_id', 'entity_type', 'entity_id'),
    )
