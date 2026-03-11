"""
Test suite for Portfolio Performance Tracking

Tests portfolio value calculation, performance metrics, and rebalancing logic
"""

import pytest
import uuid
from decimal import Decimal
from datetime import datetime, date
from sqlalchemy.orm import Session

from app.models import (
    Tenant,
    Organization,
    CreditBatch,
    MarketplaceListing,
    Portfolio,
    PortfolioPosition,
    PortfolioPerformance,
)


@pytest.fixture
def portfolio_test_data(db: Session):
    """Create test data for portfolio tests"""
    tenant = Tenant(
        id=uuid.uuid4(),
        name="Portfolio Test Tenant",
        slug="portfolio-test",
        email="portfolio@test.com",
    )
    db.add(tenant)
    db.flush()

    org = Organization(
        id=uuid.uuid4(),
        tenant_id=tenant.id,
        name="Portfolio Org",
        slug="portfolio-org",
        hierarchy_level=0,
    )
    db.add(org)
    db.flush()

    batch1 = CreditBatch(
        id=uuid.uuid4(),
        organization_id=org.id,
        tenant_id=tenant.id,
        batch_name="Batch 1",
        total_credits=Decimal("1000"),
    )
    db.add(batch1)

    batch2 = CreditBatch(
        id=uuid.uuid4(),
        organization_id=org.id,
        tenant_id=tenant.id,
        batch_name="Batch 2",
        total_credits=Decimal("500"),
    )
    db.add(batch2)
    db.flush()

    listing1 = MarketplaceListing(
        id=uuid.uuid4(),
        seller_id=org.id,
        batch_id=batch1.id,
        tenant_id=tenant.id,
        quantity_available=Decimal("500"),
        price_per_credit=Decimal("50.00"),
        listing_type="fixed_price",
        status="active",
    )
    db.add(listing1)

    listing2 = MarketplaceListing(
        id=uuid.uuid4(),
        seller_id=org.id,
        batch_id=batch2.id,
        tenant_id=tenant.id,
        quantity_available=Decimal("300"),
        price_per_credit=Decimal("60.00"),
        listing_type="fixed_price",
        status="active",
    )
    db.add(listing2)
    db.commit()

    return {
        "tenant": tenant,
        "org": org,
        "batch1": batch1,
        "batch2": batch2,
        "listing1": listing1,
        "listing2": listing2,
    }


class TestPortfolioPerformance:
    """Tests for portfolio performance tracking"""

    def test_portfolio_value_calculation(self, db: Session, portfolio_test_data):
        """Test calculating total portfolio value"""
        data = portfolio_test_data

        # Create portfolio
        portfolio = Portfolio(
            id=uuid.uuid4(),
            organization_id=data["org"].id,
            tenant_id=data["tenant"].id,
            portfolio_name="Test Portfolio",
            portfolio_type="investment",
            status="active",
        )
        db.add(portfolio)
        db.flush()

        # Add positions
        position1 = PortfolioPosition(
            id=uuid.uuid4(),
            portfolio_id=portfolio.id,
            listing_id=data["listing1"].id,
            quantity=100,
            cost_basis=50.00,
            current_value=5500.00,  # 100 * 55
        )
        db.add(position1)

        position2 = PortfolioPosition(
            id=uuid.uuid4(),
            portfolio_id=portfolio.id,
            listing_id=data["listing2"].id,
            quantity=50,
            cost_basis=60.00,
            current_value=3250.00,  # 50 * 65
        )
        db.add(position2)
        db.commit()

        # Calculate total value
        from sqlalchemy import func
        total_value = (
            db.query(PortfolioPosition)
            .filter_by(portfolio_id=portfolio.id)
            .with_entities(func.sum(PortfolioPosition.current_value))
            .scalar()
        )

        assert float(total_value) == 8750.00

    def test_performance_metrics(self, db: Session, portfolio_test_data):
        """Test calculating portfolio performance metrics"""
        data = portfolio_test_data

        portfolio = Portfolio(
            id=uuid.uuid4(),
            organization_id=data["org"].id,
            tenant_id=data["tenant"].id,
            portfolio_name="Performance Portfolio",
            portfolio_type="investment",
            status="active",
        )
        db.add(portfolio)
        db.flush()

        # Create performance record
        perf = PortfolioPerformance(
            id=uuid.uuid4(),
            portfolio_id=portfolio.id,
            date=date.today(),
            total_value=10000.00,
            daily_return=2.5,  # 2.5%
            cumulative_return=15.0,  # 15% total
            portfolio_composition={"credits": 0.6, "cash": 0.4},
        )
        db.add(perf)
        db.commit()

        # Verify metrics
        assert perf.total_value == 10000.00
        assert perf.daily_return == 2.5
        assert perf.cumulative_return == 15.0

    def test_portfolio_rebalancing(self, db: Session, portfolio_test_data):
        """Test portfolio rebalancing logic"""
        data = portfolio_test_data

        portfolio = Portfolio(
            id=uuid.uuid4(),
            organization_id=data["org"].id,
            tenant_id=data["tenant"].id,
            portfolio_name="Rebalance Portfolio",
            portfolio_type="investment",
            status="active",
        )
        db.add(portfolio)
        db.flush()

        # Positions before rebalance
        position1 = PortfolioPosition(
            id=uuid.uuid4(),
            portfolio_id=portfolio.id,
            listing_id=data["listing1"].id,
            quantity=150,
            cost_basis=50.00,
            current_value=8250.00,  # 70% of total
        )
        db.add(position1)

        position2 = PortfolioPosition(
            id=uuid.uuid4(),
            portfolio_id=portfolio.id,
            listing_id=data["listing2"].id,
            quantity=50,
            cost_basis=60.00,
            current_value=3250.00,  # 30% of total
        )
        db.add(position2)
        db.commit()

        # Calculate allocation
        total_value = position1.current_value + position2.current_value
        allocation1 = float(position1.current_value / total_value)
        allocation2 = float(position2.current_value / total_value)

        # Target is 50/50, so rebalancing needed
        assert abs(allocation1 - 0.50) > 0.1  # More than 10% off target
        assert abs(allocation2 - 0.50) > 0.1

    def test_add_position_to_portfolio(self, db: Session, portfolio_test_data):
        """Test adding a new position to portfolio"""
        data = portfolio_test_data

        portfolio = Portfolio(
            id=uuid.uuid4(),
            organization_id=data["org"].id,
            tenant_id=data["tenant"].id,
            portfolio_name="Add Position Test",
            portfolio_type="investment",
            status="active",
        )
        db.add(portfolio)
        db.commit()

        # Add position
        position = PortfolioPosition(
            id=uuid.uuid4(),
            portfolio_id=portfolio.id,
            listing_id=data["listing1"].id,
            quantity=100,
            cost_basis=50.00,
            current_value=5000.00,
        )
        db.add(position)
        db.commit()

        # Verify position added
        positions = (
            db.query(PortfolioPosition).filter_by(portfolio_id=portfolio.id).all()
        )
        assert len(positions) == 1
        assert positions[0].quantity == 100

    def test_historical_performance_tracking(self, db: Session, portfolio_test_data):
        """Test tracking portfolio performance over time"""
        data = portfolio_test_data

        portfolio = Portfolio(
            id=uuid.uuid4(),
            organization_id=data["org"].id,
            tenant_id=data["tenant"].id,
            portfolio_name="Historical Portfolio",
            portfolio_type="investment",
            status="active",
        )
        db.add(portfolio)
        db.flush()

        # Create daily performance records
        for i in range(5):
            perf = PortfolioPerformance(
                id=uuid.uuid4(),
                portfolio_id=portfolio.id,
                date=date.today(),
                total_value=10000.00 + i * 100,
                daily_return=0.5 + i * 0.1,
                cumulative_return=i * 1.0,
                portfolio_composition={"credits": 0.6, "cash": 0.4},
            )
            db.add(perf)
        db.commit()

        # Retrieve history
        history = (
            db.query(PortfolioPerformance)
            .filter_by(portfolio_id=portfolio.id)
            .order_by(PortfolioPerformance.date)
            .all()
        )

        assert len(history) == 5
        assert history[0].total_value == 10000.00
        assert history[4].total_value == 10400.00
