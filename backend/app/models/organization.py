"""Organization models for multi-level hierarchy"""
from sqlalchemy import Column, String, Integer, Boolean, DateTime, ForeignKey, JSON, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

# Base will be set by models/__init__.py after import
Base = None


class Organization(Base):
    """Organization entity representing hierarchical organizational units"""

    __tablename__ = "organizations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False)
    parent_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id", ondelete="SET NULL"), nullable=True)

    name = Column(String(255), nullable=False, index=True)
    slug = Column(String(100), nullable=False)
    description = Column(Text)

    hierarchy_level = Column(Integer, nullable=False, default=0, index=True)
    display_order = Column(Integer, default=0)
    is_active = Column(Boolean, default=True, index=True)

    org_metadata = Column(JSON, default=dict)

    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)

    # Relationships
    tenant = relationship("Tenant", back_populates="organizations")
    parent = relationship("Organization", remote_side=[id], backref="children")
    users = relationship("User", secondary="user_organizations", back_populates="organizations")

    def __repr__(self):
        return f"<Organization {self.name} (level={self.hierarchy_level})>"

    def to_dict(self, include_children=False):
        """Convert organization to dictionary"""
        data = {
            "id": str(self.id),
            "tenant_id": str(self.tenant_id),
            "parent_id": str(self.parent_id) if self.parent_id else None,
            "name": self.name,
            "slug": self.slug,
            "description": self.description,
            "hierarchy_level": self.hierarchy_level,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }

        if include_children:
            data["children"] = [child.to_dict(include_children=True) for child in self.children]

        return data


class Department(Base):
    """Department entity for organizing sub-units within organizations"""

    __tablename__ = "departments"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organization_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False)

    name = Column(String(255), nullable=False, index=True)
    description = Column(Text)

    manager_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)

    budget = Column(String(20))  # Store as string to avoid floating point issues
    is_active = Column(Boolean, default=True)

    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    organization = relationship("Organization")
    tenant = relationship("Tenant")
    manager = relationship("User")

    def __repr__(self):
        return f"<Department {self.name}>"


class Position(Base):
    """Position entity for defining roles within organizations"""

    __tablename__ = "positions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organization_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False)

    name = Column(String(255), nullable=False, index=True)
    description = Column(Text)
    level = Column(Integer)

    is_active = Column(Boolean, default=True)

    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    organization = relationship("Organization")
    tenant = relationship("Tenant")

    def __repr__(self):
        return f"<Position {self.name}>"


class UserOrganization(Base):
    """Association table for users assigned to organizations with roles"""

    __tablename__ = "user_organizations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    organization_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False)

    position_id = Column(UUID(as_uuid=True), ForeignKey("positions.id", ondelete="SET NULL"), nullable=True)
    role_id = Column(UUID(as_uuid=True), ForeignKey("roles.id", ondelete="CASCADE"), nullable=False)

    assigned_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="organizations")
    organization = relationship("Organization", back_populates="users")
    position = relationship("Position")
    role = relationship("Role")

    def __repr__(self):
        return f"<UserOrganization user={self.user_id} org={self.organization_id}>"
