"""
Carbon Credit Marketplace and Trading Service

Implements:
- Carbon credit creation and batch management
- Marketplace listing and discovery
- Trade execution with validation
- Market analytics and price tracking
"""

from typing import List, Dict, Optional, Tuple
from decimal import Decimal
from datetime import datetime, timedelta
import logging
from sqlalchemy.orm import Session
from sqlalchemy import and_, func, desc

from app.models import (
    CarbonCredit,
    CreditBatch,
    MarketplaceListing,
    Trade,
    CreditRetirement,
    MarketplaceAnalytics,
    Organization,
    CarbonCalculation,
)

logger = logging.getLogger(__name__)

# Trading constants
TRADING_FEE_PERCENTAGE = Decimal("2.0")  # 2% fee on trades
MIN_TRADE_QUANTITY = Decimal("0.1")
MAX_LISTING_PRICE = Decimal("99999.99")


class CarbonCreditService:
    """Manages carbon credit creation, tracking, and retirement"""

    def __init__(self, db: Session):
        self.db = db

    def create_credit_batch(
        self,
        organization_id: str,
        tenant_id: str,
        batch_name: str,
        credits: List[Dict],
        description: str = None,
        quality_score: Decimal = Decimal("100"),
    ) -> CreditBatch:
        """
        Create a batch of carbon credits from multiple sources

        Args:
            organization_id: Org generating credits
            tenant_id: Tenant ID
            batch_name: Name of credit batch
            credits: List of dicts with credit_type, vintage_year, quantity, source_calc_id
            description: Batch description
            quality_score: Data quality score (0-100)

        Returns:
            CreditBatch object
        """
        try:
            # Calculate total credits
            total_credits = Decimal("0")
            created_credits = []

            for credit_data in credits:
                credit = CarbonCredit(
                    tenant_id=tenant_id,
                    organization_id=organization_id,
                    credit_type=credit_data.get("credit_type", "verified"),
                    vintage_year=credit_data.get("vintage_year", datetime.utcnow().year),
                    quantity=Decimal(str(credit_data.get("quantity", 0))),
                    unit="metric_tons_co2e",
                    creation_date=datetime.utcnow(),
                    status="active",
                    source_calculation_id=credit_data.get("source_calculation_id"),
                )
                self.db.add(credit)
                created_credits.append(credit)
                total_credits += credit.quantity

            self.db.flush()

            # Create batch
            batch = CreditBatch(
                organization_id=organization_id,
                tenant_id=tenant_id,
                batch_name=batch_name,
                description=description,
                total_credits=total_credits,
                quality_score=quality_score,
            )

            self.db.add(batch)
            self.db.commit()

            logger.info(f"Created credit batch {batch_name} with {total_credits} credits")
            return batch

        except Exception as e:
            logger.error(f"Error creating credit batch: {str(e)}")
            raise

    def get_organization_credits(
        self,
        organization_id: str,
        status: str = "active",
    ) -> List[Dict]:
        """Get all credits owned by an organization"""
        try:
            credits = (
                self.db.query(CarbonCredit)
                .filter_by(organization_id=organization_id, status=status)
                .order_by(CarbonCredit.creation_date.desc())
                .all()
            )

            return [
                {
                    "id": str(c.id),
                    "batch_id": str(c.batch.id) if c.batch else None,
                    "type": c.credit_type,
                    "vintage_year": c.vintage_year,
                    "quantity": float(c.quantity),
                    "status": c.status,
                    "created_at": c.creation_date.isoformat(),
                }
                for c in credits
            ]

        except Exception as e:
            logger.error(f"Error retrieving credits: {str(e)}")
            raise

    def retire_credits(
        self,
        organization_id: str,
        tenant_id: str,
        quantity: Decimal,
        reason: str = None,
    ) -> CreditRetirement:
        """
        Retire (use) carbon credits

        Credits are marked as retired and no longer available for trading

        Args:
            organization_id: Org retiring credits
            tenant_id: Tenant ID
            quantity: Number of credits to retire
            reason: Reason for retirement

        Returns:
            CreditRetirement record
        """
        try:
            # Get available credits
            available = (
                self.db.query(func.sum(CarbonCredit.quantity))
                .filter_by(organization_id=organization_id, status="active")
                .scalar()
            )

            available_qty = Decimal(str(available)) if available else Decimal("0")

            if available_qty < quantity:
                raise ValueError(
                    f"Insufficient credits: available={available_qty}, requested={quantity}"
                )

            # Mark credits as retired
            self.db.query(CarbonCredit).filter_by(
                organization_id=organization_id, status="active"
            ).update({CarbonCredit.status: "retired"}, synchronize_session=False)

            # Create retirement record
            retirement = CreditRetirement(
                organization_id=organization_id,
                tenant_id=tenant_id,
                retired_credits=quantity,
                retirement_reason=reason,
                retirement_date=datetime.utcnow(),
            )

            self.db.add(retirement)
            self.db.commit()

            logger.info(f"Retired {quantity} credits for org {organization_id}")
            return retirement

        except ValueError:
            raise
        except Exception as e:
            logger.error(f"Error retiring credits: {str(e)}")
            raise

    def calculate_credit_value(
        self,
        batch_id: str,
    ) -> Dict:
        """
        Calculate the value of a credit batch based on market prices

        Returns current market value and potential earnings
        """
        try:
            batch = self.db.query(CreditBatch).filter_by(id=batch_id).first()
            if not batch:
                raise ValueError(f"Batch {batch_id} not found")

            # Get latest market price
            latest_price = (
                self.db.query(MarketplaceAnalytics)
                .filter_by(tenant_id=batch.tenant_id, metric_name="avg_price")
                .order_by(MarketplaceAnalytics.metric_date.desc())
                .first()
            )

            market_price = (
                Decimal(str(latest_price.metric_value))
                if latest_price
                else Decimal("50.00")
            )

            total_value = batch.total_credits * market_price

            return {
                "batch_id": str(batch.id),
                "total_credits": float(batch.total_credits),
                "market_price_per_credit": float(market_price),
                "total_value": float(total_value),
                "quality_score": float(batch.quality_score),
            }

        except Exception as e:
            logger.error(f"Error calculating credit value: {str(e)}")
            raise


class MarketplaceListingService:
    """Manages marketplace listings and discovery"""

    def __init__(self, db: Session):
        self.db = db

    def create_listing(
        self,
        seller_id: str,
        batch_id: str,
        tenant_id: str,
        quantity: Decimal,
        price_per_credit: Decimal,
        listing_type: str = "fixed_price",
        expires_in_days: int = 30,
        minimum_bid: Decimal = None,
    ) -> MarketplaceListing:
        """
        Create a marketplace listing for carbon credits

        Args:
            seller_id: Organization selling credits
            batch_id: Credit batch to list
            quantity: Quantity to list
            price_per_credit: Price per credit in USD
            listing_type: fixed_price, auction, negotiable
            expires_in_days: Days until listing expires
            minimum_bid: Minimum bid for auctions

        Returns:
            MarketplaceListing
        """
        try:
            if price_per_credit <= 0 or price_per_credit > MAX_LISTING_PRICE:
                raise ValueError(f"Invalid price: {price_per_credit}")

            batch = self.db.query(CreditBatch).filter_by(id=batch_id).first()
            if not batch:
                raise ValueError(f"Batch {batch_id} not found")

            if batch.total_credits < quantity:
                raise ValueError(
                    f"Insufficient credits: available={batch.total_credits}, requested={quantity}"
                )

            listing = MarketplaceListing(
                seller_id=seller_id,
                batch_id=batch_id,
                tenant_id=tenant_id,
                quantity_available=quantity,
                price_per_credit=price_per_credit,
                listing_type=listing_type,
                expires_at=datetime.utcnow() + timedelta(days=expires_in_days),
                minimum_bid=minimum_bid,
                status="active",
            )

            self.db.add(listing)
            self.db.commit()

            logger.info(
                f"Created listing: {quantity} credits @ ${price_per_credit} by seller {seller_id}"
            )
            return listing

        except ValueError:
            raise
        except Exception as e:
            logger.error(f"Error creating listing: {str(e)}")
            raise

    def list_active_listings(
        self,
        tenant_id: str,
        seller_id: str = None,
        min_price: Decimal = None,
        max_price: Decimal = None,
        limit: int = 100,
    ) -> List[Dict]:
        """
        List active marketplace listings with optional filters

        Returns:
            List of listing details
        """
        try:
            query = (
                self.db.query(MarketplaceListing)
                .filter(
                    and_(
                        MarketplaceListing.tenant_id == tenant_id,
                        MarketplaceListing.status == "active",
                        MarketplaceListing.expires_at > datetime.utcnow(),
                    )
                )
                .order_by(MarketplaceListing.price_per_credit)
            )

            if seller_id:
                query = query.filter_by(seller_id=seller_id)

            if min_price:
                query = query.filter(MarketplaceListing.price_per_credit >= min_price)

            if max_price:
                query = query.filter(MarketplaceListing.price_per_credit <= max_price)

            listings = query.limit(limit).all()

            return [
                {
                    "id": str(l.id),
                    "seller_id": str(l.seller_id),
                    "quantity": float(l.quantity_available),
                    "price_per_credit": float(l.price_per_credit),
                    "total_value": float(l.quantity_available * l.price_per_credit),
                    "type": l.listing_type,
                    "status": l.status,
                    "created_at": l.created_at.isoformat(),
                    "expires_at": l.expires_at.isoformat() if l.expires_at else None,
                }
                for l in listings
            ]

        except Exception as e:
            logger.error(f"Error listing active listings: {str(e)}")
            raise

    def get_price_history(
        self,
        tenant_id: str,
        days: int = 30,
    ) -> List[Dict]:
        """Get historical price data for market analysis"""
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=days)

            history = (
                self.db.query(MarketplaceAnalytics)
                .filter(
                    and_(
                        MarketplaceAnalytics.tenant_id == tenant_id,
                        MarketplaceAnalytics.metric_name == "avg_price",
                        MarketplaceAnalytics.metric_date >= cutoff_date,
                    )
                )
                .order_by(MarketplaceAnalytics.metric_date)
                .all()
            )

            return [
                {
                    "date": h.metric_date.isoformat(),
                    "price": float(h.metric_value),
                }
                for h in history
            ]

        except Exception as e:
            logger.error(f"Error retrieving price history: {str(e)}")
            raise


class TradeExecutionService:
    """Handles trade execution and settlement"""

    def __init__(self, db: Session):
        self.db = db

    def execute_trade(
        self,
        listing_id: str,
        buyer_id: str,
        quantity: Decimal,
        agreed_price: Decimal = None,
    ) -> Trade:
        """
        Execute a trade transaction

        Args:
            listing_id: Marketplace listing
            buyer_id: Buying organization
            quantity: Quantity to trade
            agreed_price: Final agreed price (for auctions/negotiable)

        Returns:
            Trade record
        """
        try:
            # Validate trade
            self.validate_trade(listing_id, buyer_id, quantity)

            listing = self.db.query(MarketplaceListing).filter_by(id=listing_id).first()

            if agreed_price is None:
                agreed_price = listing.price_per_credit

            total_price = quantity * agreed_price

            # Create trade
            trade = Trade(
                listing_id=listing_id,
                buyer_id=buyer_id,
                seller_id=listing.seller_id,
                tenant_id=listing.tenant_id,
                quantity=quantity,
                price_per_credit=agreed_price,
                total_price=total_price,
                status="pending",
                payment_status="pending",
                trade_date=datetime.utcnow(),
            )

            self.db.add(trade)

            # Update listing availability
            listing.quantity_available -= quantity
            if listing.quantity_available <= 0:
                listing.status = "sold"

            self.db.commit()

            logger.info(
                f"Executed trade: {quantity} credits @ ${agreed_price} from {listing.seller_id} to {buyer_id}"
            )
            return trade

        except ValueError:
            raise
        except Exception as e:
            logger.error(f"Error executing trade: {str(e)}")
            raise

    def validate_trade(
        self,
        listing_id: str,
        buyer_id: str,
        quantity: Decimal,
    ) -> bool:
        """Validate trade before execution"""
        listing = self.db.query(MarketplaceListing).filter_by(id=listing_id).first()

        if not listing:
            raise ValueError(f"Listing {listing_id} not found")

        if listing.status != "active":
            raise ValueError(f"Listing is not active: {listing.status}")

        if listing.seller_id == buyer_id:
            raise ValueError("Cannot buy from yourself")

        if quantity < MIN_TRADE_QUANTITY:
            raise ValueError(f"Minimum trade quantity is {MIN_TRADE_QUANTITY}")

        if quantity > listing.quantity_available:
            raise ValueError(
                f"Insufficient quantity: available={listing.quantity_available}, requested={quantity}"
            )

        return True

    def get_trade_history(
        self,
        organization_id: str,
        role: str = "all",  # buyer, seller, all
        limit: int = 100,
    ) -> List[Dict]:
        """Get trade history for an organization"""
        try:
            if role == "buyer":
                trades = (
                    self.db.query(Trade)
                    .filter_by(buyer_id=organization_id)
                    .order_by(Trade.trade_date.desc())
                    .limit(limit)
                    .all()
                )
            elif role == "seller":
                trades = (
                    self.db.query(Trade)
                    .filter_by(seller_id=organization_id)
                    .order_by(Trade.trade_date.desc())
                    .limit(limit)
                    .all()
                )
            else:
                from sqlalchemy import or_

                trades = (
                    self.db.query(Trade)
                    .filter(
                        or_(
                            Trade.buyer_id == organization_id,
                            Trade.seller_id == organization_id,
                        )
                    )
                    .order_by(Trade.trade_date.desc())
                    .limit(limit)
                    .all()
                )

            return [
                {
                    "id": str(t.id),
                    "buyer_id": str(t.buyer_id),
                    "seller_id": str(t.seller_id),
                    "quantity": float(t.quantity),
                    "price_per_credit": float(t.price_per_credit),
                    "total_price": float(t.total_price),
                    "status": t.status,
                    "payment_status": t.payment_status,
                    "trade_date": t.trade_date.isoformat(),
                }
                for t in trades
            ]

        except Exception as e:
            logger.error(f"Error retrieving trade history: {str(e)}")
            raise

    def complete_trade(
        self,
        trade_id: str,
        payment_confirmed: bool = True,
    ) -> Trade:
        """Complete a trade and update status"""
        try:
            trade = self.db.query(Trade).filter_by(id=trade_id).first()
            if not trade:
                raise ValueError(f"Trade {trade_id} not found")

            trade.status = "completed"
            trade.payment_status = "completed" if payment_confirmed else "pending"
            trade.completion_date = datetime.utcnow()

            self.db.commit()

            logger.info(f"Completed trade {trade_id}")
            return trade

        except Exception as e:
            logger.error(f"Error completing trade: {str(e)}")
            raise


class MarketplaceAnalyticsService:
    """Analyzes marketplace metrics and trends"""

    def __init__(self, db: Session):
        self.db = db

    def get_market_price(
        self,
        tenant_id: str,
    ) -> Decimal:
        """Get current average market price per credit"""
        try:
            # Get most recent average price
            latest = (
                self.db.query(MarketplaceAnalytics)
                .filter_by(tenant_id=tenant_id, metric_name="avg_price")
                .order_by(MarketplaceAnalytics.metric_date.desc())
                .first()
            )

            if latest:
                return Decimal(str(latest.metric_value))

            # If no history, calculate from active listings
            avg_price = (
                self.db.query(func.avg(MarketplaceListing.price_per_credit))
                .filter(
                    and_(
                        MarketplaceListing.tenant_id == tenant_id,
                        MarketplaceListing.status == "active",
                    )
                )
                .scalar()
            )

            return Decimal(str(avg_price)) if avg_price else Decimal("50.00")

        except Exception as e:
            logger.error(f"Error getting market price: {str(e)}")
            return Decimal("50.00")

    def get_trading_volume(
        self,
        tenant_id: str,
        days: int = 30,
    ) -> Dict:
        """Get trading volume metrics for period"""
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=days)

            volume = (
                self.db.query(func.sum(Trade.quantity))
                .filter(
                    and_(
                        Trade.tenant_id == tenant_id,
                        Trade.status == "completed",
                        Trade.trade_date >= cutoff_date,
                    )
                )
                .scalar()
            )

            trade_count = (
                self.db.query(func.count(Trade.id))
                .filter(
                    and_(
                        Trade.tenant_id == tenant_id,
                        Trade.status == "completed",
                        Trade.trade_date >= cutoff_date,
                    )
                )
                .scalar()
            )

            return {
                "period_days": days,
                "total_volume": float(volume) if volume else 0,
                "transaction_count": trade_count or 0,
            }

        except Exception as e:
            logger.error(f"Error calculating trading volume: {str(e)}")
            raise

    def record_market_metric(
        self,
        tenant_id: str,
        metric_name: str,
        metric_value: Decimal,
    ) -> MarketplaceAnalytics:
        """Record a market metric for historical tracking"""
        try:
            metric = MarketplaceAnalytics(
                tenant_id=tenant_id,
                metric_date=datetime.utcnow(),
                metric_name=metric_name,
                metric_value=metric_value,
            )

            self.db.add(metric)
            self.db.commit()

            logger.info(f"Recorded metric {metric_name} = {metric_value}")
            return metric

        except Exception as e:
            logger.error(f"Error recording market metric: {str(e)}")
            raise
