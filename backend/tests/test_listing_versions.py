"""
Test suite for Listing Version Tracking

Tests version history for marketplace listings with price/availability changes
"""

import pytest
import uuid
from decimal import Decimal
from datetime import datetime
from sqlalchemy.orm import Session

from app.models import (
    Tenant,
    Organization,
    CreditBatch,
    MarketplaceListing,
    ListingVersion,
)


@pytest.fixture
def version_test_data(db: Session):
    """Create test data for version tests"""
    tenant = Tenant(
        id=uuid.uuid4(),
        name="Version Test Tenant",
        slug="version-test",
        email="version@test.com",
    )
    db.add(tenant)
    db.flush()

    org = Organization(
        id=uuid.uuid4(),
        tenant_id=tenant.id,
        name="Version Test Org",
        slug="version-org",
        hierarchy_level=0,
    )
    db.add(org)
    db.flush()

    batch = CreditBatch(
        id=uuid.uuid4(),
        organization_id=org.id,
        tenant_id=tenant.id,
        batch_name="Version Test Batch",
        total_credits=Decimal("1000"),
    )
    db.add(batch)
    db.commit()

    return {"tenant": tenant, "org": org, "batch": batch}


class TestListingVersions:
    """Tests for listing version tracking"""

    def test_create_version_on_price_update(self, db: Session, version_test_data):
        """Test that version is created when listing price changes"""
        data = version_test_data

        # Create listing
        listing = MarketplaceListing(
            id=uuid.uuid4(),
            seller_id=data["org"].id,
            batch_id=data["batch"].id,
            tenant_id=data["tenant"].id,
            quantity_available=Decimal("500"),
            price_per_credit=Decimal("50.00"),
            listing_type="fixed_price",
            status="active",
        )
        db.add(listing)
        db.commit()

        # Create version for price change
        version = ListingVersion(
            id=uuid.uuid4(),
            listing_id=listing.id,
            version_number=1,
            price_snapshot=float(listing.price_per_credit),
            availability_snapshot=int(listing.quantity_available),
            change_type="price_update",
            changed_by=uuid.uuid4(),
            changed_at=datetime.utcnow(),
        )
        db.add(version)
        db.commit()

        # Verify version created
        versions = db.query(ListingVersion).filter_by(listing_id=listing.id).all()
        assert len(versions) == 1
        assert versions[0].price_snapshot == 50.00
        assert versions[0].change_type == "price_update"

    def test_version_history_retrieval(self, db: Session, version_test_data):
        """Test retrieving version history for a listing"""
        data = version_test_data

        listing = MarketplaceListing(
            id=uuid.uuid4(),
            seller_id=data["org"].id,
            batch_id=data["batch"].id,
            tenant_id=data["tenant"].id,
            quantity_available=Decimal("500"),
            price_per_credit=Decimal("50.00"),
            listing_type="fixed_price",
            status="active",
        )
        db.add(listing)
        db.commit()

        # Create multiple versions
        for i in range(3):
            version = ListingVersion(
                id=uuid.uuid4(),
                listing_id=listing.id,
                version_number=i + 1,
                price_snapshot=50.00 + i * 5,
                availability_snapshot=500 - i * 100,
                change_type="price_update",
                changed_by=uuid.uuid4(),
            )
            db.add(version)
        db.commit()

        # Retrieve all versions
        versions = (
            db.query(ListingVersion)
            .filter_by(listing_id=listing.id)
            .order_by(ListingVersion.version_number)
            .all()
        )

        assert len(versions) == 3
        assert versions[0].price_snapshot == 50.00
        assert versions[2].price_snapshot == 60.00

    def test_version_comparison(self, db: Session, version_test_data):
        """Test comparing two versions"""
        data = version_test_data

        listing = MarketplaceListing(
            id=uuid.uuid4(),
            seller_id=data["org"].id,
            batch_id=data["batch"].id,
            tenant_id=data["tenant"].id,
            quantity_available=Decimal("500"),
            price_per_credit=Decimal("50.00"),
            listing_type="fixed_price",
            status="active",
        )
        db.add(listing)
        db.commit()

        # Create v1 and v2
        v1 = ListingVersion(
            id=uuid.uuid4(),
            listing_id=listing.id,
            version_number=1,
            price_snapshot=50.00,
            availability_snapshot=500,
            change_type="initial",
            changed_by=uuid.uuid4(),
        )
        db.add(v1)

        v2 = ListingVersion(
            id=uuid.uuid4(),
            listing_id=listing.id,
            version_number=2,
            price_snapshot=60.00,
            availability_snapshot=400,
            change_type="price_update",
            changed_by=uuid.uuid4(),
        )
        db.add(v2)
        db.commit()

        # Compare versions
        price_change = v2.price_snapshot - v1.price_snapshot
        availability_change = v2.availability_snapshot - v1.availability_snapshot

        assert price_change == 10.00
        assert availability_change == -100
