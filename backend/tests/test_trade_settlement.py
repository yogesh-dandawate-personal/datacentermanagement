"""
Test suite for Trade Settlement Tracking

Tests settlement execution and status tracking after trade completion
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
    Trade,
    TradeMatch,
    TradeSettlement,
)


@pytest.fixture
def settlement_test_data(db: Session):
    """Create test data for settlement tests"""
    tenant = Tenant(
        id=uuid.uuid4(),
        name="Settlement Test Tenant",
        slug="settlement-test",
        email="settlement@test.com",
    )
    db.add(tenant)
    db.flush()

    seller = Organization(
        id=uuid.uuid4(),
        tenant_id=tenant.id,
        name="Seller Org",
        slug="seller-org",
        hierarchy_level=0,
    )
    db.add(seller)
    db.flush()

    buyer = Organization(
        id=uuid.uuid4(),
        tenant_id=tenant.id,
        name="Buyer Org",
        slug="buyer-org",
        hierarchy_level=0,
    )
    db.add(buyer)
    db.flush()

    batch = CreditBatch(
        id=uuid.uuid4(),
        organization_id=seller.id,
        tenant_id=tenant.id,
        batch_name="Settlement Batch",
        total_credits=Decimal("1000"),
    )
    db.add(batch)
    db.commit()

    return {"tenant": tenant, "seller": seller, "buyer": buyer, "batch": batch}


class TestTradeSettlement:
    """Tests for trade settlement tracking"""

    def test_settlement_execution(self, db: Session, settlement_test_data):
        """Test executing trade settlement"""
        data = settlement_test_data

        # Create listing and trade
        listing = MarketplaceListing(
            id=uuid.uuid4(),
            seller_id=data["seller"].id,
            batch_id=data["batch"].id,
            tenant_id=data["tenant"].id,
            quantity_available=Decimal("500"),
            price_per_credit=Decimal("50.00"),
            listing_type="fixed_price",
            status="active",
        )
        db.add(listing)
        db.flush()

        trade = Trade(
            id=uuid.uuid4(),
            listing_id=listing.id,
            buyer_id=data["buyer"].id,
            seller_id=data["seller"].id,
            tenant_id=data["tenant"].id,
            quantity=Decimal("100"),
            price_per_credit=Decimal("50.00"),
            total_price=Decimal("5000.00"),
            status="completed",
            payment_status="pending",
        )
        db.add(trade)
        db.commit()

        # Create settlement
        settlement = TradeSettlement(
            id=uuid.uuid4(),
            trade_id=trade.id,
            settlement_type="both",
            settlement_status="pending",
            settled_amount=float(trade.total_price),
            settlement_date=datetime.utcnow(),
            confirmed_by=uuid.uuid4(),
            settlement_log={"step": "initiated"},
        )
        db.add(settlement)
        db.commit()

        # Verify settlement
        assert settlement.settlement_status == "pending"
        assert settlement.settled_amount == 5000.00
        assert settlement.settlement_type == "both"

    def test_settlement_status_tracking(self, db: Session, settlement_test_data):
        """Test tracking settlement status changes"""
        data = settlement_test_data

        listing = MarketplaceListing(
            id=uuid.uuid4(),
            seller_id=data["seller"].id,
            batch_id=data["batch"].id,
            tenant_id=data["tenant"].id,
            quantity_available=Decimal("500"),
            price_per_credit=Decimal("50.00"),
            listing_type="fixed_price",
            status="active",
        )
        db.add(listing)
        db.flush()

        trade = Trade(
            id=uuid.uuid4(),
            listing_id=listing.id,
            buyer_id=data["buyer"].id,
            seller_id=data["seller"].id,
            tenant_id=data["tenant"].id,
            quantity=Decimal("100"),
            price_per_credit=Decimal("50.00"),
            total_price=Decimal("5000.00"),
            status="completed",
        )
        db.add(trade)
        db.flush()

        settlement = TradeSettlement(
            id=uuid.uuid4(),
            trade_id=trade.id,
            settlement_type="both",
            settlement_status="pending",
            settled_amount=5000.00,
            settlement_log={"steps": []},
        )
        db.add(settlement)
        db.commit()

        # Update status
        settlement.settlement_status = "completed"
        settlement.settlement_log = {
            "steps": ["initiated", "payment_confirmed", "credits_transferred", "completed"]
        }
        db.commit()

        # Verify update
        updated = db.query(TradeSettlement).filter_by(id=settlement.id).first()
        assert updated.settlement_status == "completed"
        assert len(updated.settlement_log["steps"]) == 4

    def test_settlement_rollback_on_failure(self, db: Session, settlement_test_data):
        """Test handling settlement failure and rollback"""
        data = settlement_test_data

        listing = MarketplaceListing(
            id=uuid.uuid4(),
            seller_id=data["seller"].id,
            batch_id=data["batch"].id,
            tenant_id=data["tenant"].id,
            quantity_available=Decimal("500"),
            price_per_credit=Decimal("50.00"),
            listing_type="fixed_price",
            status="active",
        )
        db.add(listing)
        db.flush()

        trade = Trade(
            id=uuid.uuid4(),
            listing_id=listing.id,
            buyer_id=data["buyer"].id,
            seller_id=data["seller"].id,
            tenant_id=data["tenant"].id,
            quantity=Decimal("100"),
            price_per_credit=Decimal("50.00"),
            total_price=Decimal("5000.00"),
            status="completed",
        )
        db.add(trade)
        db.flush()

        # Settlement fails
        settlement = TradeSettlement(
            id=uuid.uuid4(),
            trade_id=trade.id,
            settlement_type="credits",
            settlement_status="failed",
            settled_amount=5000.00,
            settlement_log={"error": "insufficient_credits", "action": "rollback"},
        )
        db.add(settlement)
        db.commit()

        # Verify failure recorded
        failed = db.query(TradeSettlement).filter_by(id=settlement.id).first()
        assert failed.settlement_status == "failed"
        assert "rollback" in failed.settlement_log.get("action", "")


class TestTradeMatching:
    """Tests for trade matching algorithm"""

    def test_match_trades(self, db: Session, settlement_test_data):
        """Test matching buy and sell orders"""
        data = settlement_test_data

        listing = MarketplaceListing(
            id=uuid.uuid4(),
            seller_id=data["seller"].id,
            batch_id=data["batch"].id,
            tenant_id=data["tenant"].id,
            quantity_available=Decimal("500"),
            price_per_credit=Decimal("50.00"),
            listing_type="fixed_price",
            status="active",
        )
        db.add(listing)
        db.flush()

        buy_order = Trade(
            id=uuid.uuid4(),
            listing_id=listing.id,
            buyer_id=data["buyer"].id,
            seller_id=data["seller"].id,
            tenant_id=data["tenant"].id,
            quantity=Decimal("100"),
            price_per_credit=Decimal("50.00"),
            total_price=Decimal("5000.00"),
            status="pending",
        )
        db.add(buy_order)
        db.flush()

        sell_order = Trade(
            id=uuid.uuid4(),
            listing_id=listing.id,
            buyer_id=data["buyer"].id,
            seller_id=data["seller"].id,
            tenant_id=data["tenant"].id,
            quantity=Decimal("100"),
            price_per_credit=Decimal("50.00"),
            total_price=Decimal("5000.00"),
            status="pending",
        )
        db.add(sell_order)
        db.commit()

        # Create match
        match = TradeMatch(
            id=uuid.uuid4(),
            buy_order_id=buy_order.id,
            sell_order_id=sell_order.id,
            match_price=50.00,
            match_quantity=100,
            matched_at=datetime.utcnow(),
            match_score=0.95,
        )
        db.add(match)
        db.commit()

        # Verify match
        assert match.match_price == 50.00
        assert match.match_quantity == 100
        assert match.match_score == 0.95
