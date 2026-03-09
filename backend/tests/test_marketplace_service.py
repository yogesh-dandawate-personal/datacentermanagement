"""
Test suite for Carbon Credit Marketplace and Trading Service

Tests:
- Carbon credit creation and batching
- Marketplace listing creation and discovery
- Trade execution and settlement
- Market analytics and pricing
"""

import pytest
import uuid
from decimal import Decimal
from datetime import datetime, timedelta
from sqlalchemy.orm import Session

from app.models import (
    Tenant,
    Organization,
    CarbonCredit,
    CreditBatch,
    MarketplaceListing,
    Trade,
    CreditRetirement,
    MarketplaceAnalytics,
)
from app.services.marketplace_service import (
    CarbonCreditService,
    MarketplaceListingService,
    TradeExecutionService,
    MarketplaceAnalyticsService,
)


@pytest.fixture
def marketplace_test_data(db: Session):
    """Create test data for marketplace tests"""
    # Create tenant
    tenant = Tenant(
        id=uuid.uuid4(),
        name="Test Tenant",
        slug="test-tenant",
        email="test@example.com",
    )
    db.add(tenant)
    db.flush()

    # Create seller organization
    seller = Organization(
        id=uuid.uuid4(),
        tenant_id=tenant.id,
        name="Seller Corp",
        slug="seller-corp",
        hierarchy_level=0,
    )
    db.add(seller)
    db.flush()

    # Create buyer organization
    buyer = Organization(
        id=uuid.uuid4(),
        tenant_id=tenant.id,
        name="Buyer Corp",
        slug="buyer-corp",
        hierarchy_level=0,
    )
    db.add(buyer)
    db.commit()

    return {
        "tenant": tenant,
        "seller": seller,
        "buyer": buyer,
    }


# ============================================================================
# Test: Carbon Credit Service
# ============================================================================


class TestCarbonCreditService:
    """Tests for carbon credit creation and management"""

    def test_create_credit_batch(self, db: Session, marketplace_test_data):
        """Test creating a carbon credit batch"""
        test_data = marketplace_test_data

        service = CarbonCreditService(db)
        batch = service.create_credit_batch(
            organization_id=test_data["seller"].id,
            tenant_id=test_data["tenant"].id,
            batch_name="2024 Q1 Credits",
            credits=[
                {
                    "credit_type": "verified",
                    "vintage_year": 2024,
                    "quantity": 1000,
                }
            ],
            description="Energy efficiency credits",
            quality_score=Decimal("95"),
        )

        assert batch.batch_name == "2024 Q1 Credits"
        assert batch.total_credits == Decimal("1000")
        assert batch.quality_score == Decimal("95")

    def test_get_organization_credits(self, db: Session, marketplace_test_data):
        """Test retrieving credits for an organization"""
        test_data = marketplace_test_data

        service = CarbonCreditService(db)
        batch = service.create_credit_batch(
            organization_id=test_data["seller"].id,
            tenant_id=test_data["tenant"].id,
            batch_name="Test Batch",
            credits=[
                {"credit_type": "verified", "vintage_year": 2024, "quantity": 500}
            ],
        )

        credits = service.get_organization_credits(test_data["seller"].id)

        assert len(credits) > 0
        assert all(c["status"] == "active" for c in credits)

    def test_retire_credits(self, db: Session, marketplace_test_data):
        """Test retiring carbon credits"""
        test_data = marketplace_test_data

        # Create credits
        credit_service = CarbonCreditService(db)
        batch = credit_service.create_credit_batch(
            organization_id=test_data["seller"].id,
            tenant_id=test_data["tenant"].id,
            batch_name="Test Batch",
            credits=[
                {"credit_type": "verified", "vintage_year": 2024, "quantity": 300}
            ],
        )

        # Retire credits
        retirement = credit_service.retire_credits(
            organization_id=test_data["seller"].id,
            tenant_id=test_data["tenant"].id,
            quantity=Decimal("300"),
            reason="Carbon offset project",
        )

        assert retirement.retired_credits == Decimal("300")
        assert retirement.retirement_reason == "Carbon offset project"

    def test_calculate_credit_value(self, db: Session, marketplace_test_data):
        """Test calculating credit batch value"""
        test_data = marketplace_test_data

        service = CarbonCreditService(db)
        batch = service.create_credit_batch(
            organization_id=test_data["seller"].id,
            tenant_id=test_data["tenant"].id,
            batch_name="Value Test",
            credits=[
                {"credit_type": "verified", "vintage_year": 2024, "quantity": 200}
            ],
        )

        value = service.calculate_credit_value(batch.id)

        assert value["total_credits"] == 200
        assert value["market_price_per_credit"] > 0
        assert value["total_value"] > 0


# ============================================================================
# Test: Marketplace Listing Service
# ============================================================================


class TestMarketplaceListingService:
    """Tests for marketplace listing creation and discovery"""

    def test_create_listing(self, db: Session, marketplace_test_data):
        """Test creating a marketplace listing"""
        test_data = marketplace_test_data

        # Create batch
        credit_service = CarbonCreditService(db)
        batch = credit_service.create_credit_batch(
            organization_id=test_data["seller"].id,
            tenant_id=test_data["tenant"].id,
            batch_name="Test Batch",
            credits=[
                {"credit_type": "verified", "vintage_year": 2024, "quantity": 500}
            ],
        )

        # Create listing
        listing_service = MarketplaceListingService(db)
        listing = listing_service.create_listing(
            seller_id=test_data["seller"].id,
            batch_id=batch.id,
            tenant_id=test_data["tenant"].id,
            quantity=Decimal("500"),
            price_per_credit=Decimal("50.00"),
            listing_type="fixed_price",
        )

        assert listing.quantity_available == Decimal("500")
        assert listing.price_per_credit == Decimal("50.00")
        assert listing.status == "active"

    def test_list_active_listings(self, db: Session, marketplace_test_data):
        """Test listing active marketplace listings"""
        test_data = marketplace_test_data

        # Create multiple listings
        credit_service = CarbonCreditService(db)
        for i in range(3):
            batch = credit_service.create_credit_batch(
                organization_id=test_data["seller"].id,
                tenant_id=test_data["tenant"].id,
                batch_name=f"Batch {i}",
                credits=[
                    {"credit_type": "verified", "vintage_year": 2024, "quantity": 100}
                ],
            )

            listing_service = MarketplaceListingService(db)
            listing_service.create_listing(
                seller_id=test_data["seller"].id,
                batch_id=batch.id,
                tenant_id=test_data["tenant"].id,
                quantity=Decimal("100"),
                price_per_credit=Decimal(str(40 + i * 5)),
            )

        # List active
        listings = listing_service.list_active_listings(
            tenant_id=test_data["tenant"].id
        )

        assert len(listings) == 3
        assert all(l["status"] == "active" for l in listings)

    def test_price_filter(self, db: Session, marketplace_test_data):
        """Test filtering listings by price"""
        test_data = marketplace_test_data

        # Create listings with different prices
        credit_service = CarbonCreditService(db)
        listing_service = MarketplaceListingService(db)

        for price in [30, 50, 70]:
            batch = credit_service.create_credit_batch(
                organization_id=test_data["seller"].id,
                tenant_id=test_data["tenant"].id,
                batch_name=f"Batch ${price}",
                credits=[
                    {"credit_type": "verified", "vintage_year": 2024, "quantity": 100}
                ],
            )

            listing_service.create_listing(
                seller_id=test_data["seller"].id,
                batch_id=batch.id,
                tenant_id=test_data["tenant"].id,
                quantity=Decimal("100"),
                price_per_credit=Decimal(str(price)),
            )

        # Filter by price
        listings = listing_service.list_active_listings(
            tenant_id=test_data["tenant"].id,
            min_price=Decimal("40"),
            max_price=Decimal("60"),
        )

        assert len(listings) == 1
        assert 40 <= listings[0]["price_per_credit"] <= 60


# ============================================================================
# Test: Trade Execution Service
# ============================================================================


class TestTradeExecutionService:
    """Tests for trade execution and settlement"""

    def test_execute_trade(self, db: Session, marketplace_test_data):
        """Test executing a carbon credit trade"""
        test_data = marketplace_test_data

        # Create and list credits
        credit_service = CarbonCreditService(db)
        batch = credit_service.create_credit_batch(
            organization_id=test_data["seller"].id,
            tenant_id=test_data["tenant"].id,
            batch_name="Trade Test",
            credits=[
                {"credit_type": "verified", "vintage_year": 2024, "quantity": 200}
            ],
        )

        listing_service = MarketplaceListingService(db)
        listing = listing_service.create_listing(
            seller_id=test_data["seller"].id,
            batch_id=batch.id,
            tenant_id=test_data["tenant"].id,
            quantity=Decimal("200"),
            price_per_credit=Decimal("55.00"),
        )

        # Execute trade
        trade_service = TradeExecutionService(db)
        trade = trade_service.execute_trade(
            listing_id=listing.id,
            buyer_id=test_data["buyer"].id,
            quantity=Decimal("100"),
        )

        assert trade.quantity == Decimal("100")
        assert trade.price_per_credit == Decimal("55.00")
        assert trade.total_price == Decimal("5500.00")
        assert trade.status == "pending"

    def test_validate_trade_errors(self, db: Session, marketplace_test_data):
        """Test trade validation catches errors"""
        test_data = marketplace_test_data

        trade_service = TradeExecutionService(db)

        # Invalid listing
        with pytest.raises(ValueError, match="not found"):
            trade_service.validate_trade(uuid.uuid4(), test_data["buyer"].id, Decimal("100"))

    def test_complete_trade(self, db: Session, marketplace_test_data):
        """Test completing a trade"""
        test_data = marketplace_test_data

        # Create and execute trade
        credit_service = CarbonCreditService(db)
        batch = credit_service.create_credit_batch(
            organization_id=test_data["seller"].id,
            tenant_id=test_data["tenant"].id,
            batch_name="Complete Test",
            credits=[
                {"credit_type": "verified", "vintage_year": 2024, "quantity": 150}
            ],
        )

        listing_service = MarketplaceListingService(db)
        listing = listing_service.create_listing(
            seller_id=test_data["seller"].id,
            batch_id=batch.id,
            tenant_id=test_data["tenant"].id,
            quantity=Decimal("150"),
            price_per_credit=Decimal("48.00"),
        )

        trade_service = TradeExecutionService(db)
        trade = trade_service.execute_trade(
            listing_id=listing.id,
            buyer_id=test_data["buyer"].id,
            quantity=Decimal("50"),
        )

        # Complete trade
        completed = trade_service.complete_trade(trade.id, payment_confirmed=True)

        assert completed.status == "completed"
        assert completed.payment_status == "completed"

    def test_get_trade_history(self, db: Session, marketplace_test_data):
        """Test retrieving trade history"""
        test_data = marketplace_test_data

        # Create multiple trades
        credit_service = CarbonCreditService(db)
        trade_service = TradeExecutionService(db)

        for i in range(2):
            batch = credit_service.create_credit_batch(
                organization_id=test_data["seller"].id,
                tenant_id=test_data["tenant"].id,
                batch_name=f"Trade Batch {i}",
                credits=[
                    {"credit_type": "verified", "vintage_year": 2024, "quantity": 100}
                ],
            )

            listing_service = MarketplaceListingService(db)
            listing = listing_service.create_listing(
                seller_id=test_data["seller"].id,
                batch_id=batch.id,
                tenant_id=test_data["tenant"].id,
                quantity=Decimal("100"),
                price_per_credit=Decimal("50.00"),
            )

            trade_service.execute_trade(
                listing_id=listing.id,
                buyer_id=test_data["buyer"].id,
                quantity=Decimal("100"),
            )

        # Get buyer history
        history = trade_service.get_trade_history(
            test_data["buyer"].id, role="buyer"
        )

        assert len(history) == 2
        assert all(t["buyer_id"] == str(test_data["buyer"].id) for t in history)


# ============================================================================
# Test: Market Analytics Service
# ============================================================================


class TestMarketplaceAnalyticsService:
    """Tests for market analytics and pricing"""

    def test_get_market_price(self, db: Session, marketplace_test_data):
        """Test retrieving current market price"""
        test_data = marketplace_test_data

        service = MarketplaceAnalyticsService(db)
        price = service.get_market_price(test_data["tenant"].id)

        assert price > 0
        assert price == Decimal("50.00")  # Default

    def test_record_market_metric(self, db: Session, marketplace_test_data):
        """Test recording market metrics"""
        test_data = marketplace_test_data

        service = MarketplaceAnalyticsService(db)
        metric = service.record_market_metric(
            tenant_id=test_data["tenant"].id,
            metric_name="avg_price",
            metric_value=Decimal("52.50"),
        )

        assert metric.metric_value == Decimal("52.50")
        assert metric.metric_name == "avg_price"

    def test_get_trading_volume(self, db: Session, marketplace_test_data):
        """Test calculating trading volume"""
        test_data = marketplace_test_data

        # Create and complete trades
        credit_service = CarbonCreditService(db)
        trade_service = TradeExecutionService(db)

        for i in range(3):
            batch = credit_service.create_credit_batch(
                organization_id=test_data["seller"].id,
                tenant_id=test_data["tenant"].id,
                batch_name=f"Volume Batch {i}",
                credits=[
                    {"credit_type": "verified", "vintage_year": 2024, "quantity": 100}
                ],
            )

            listing_service = MarketplaceListingService(db)
            listing = listing_service.create_listing(
                seller_id=test_data["seller"].id,
                batch_id=batch.id,
                tenant_id=test_data["tenant"].id,
                quantity=Decimal("100"),
                price_per_credit=Decimal("50.00"),
            )

            trade = trade_service.execute_trade(
                listing_id=listing.id,
                buyer_id=test_data["buyer"].id,
                quantity=Decimal("100"),
            )

            # Complete trade
            trade_service.complete_trade(trade.id)

        # Get volume
        analytics_service = MarketplaceAnalyticsService(db)
        volume = analytics_service.get_trading_volume(
            test_data["tenant"].id, days=30
        )

        assert volume["transaction_count"] == 3
        assert volume["total_volume"] == 300
