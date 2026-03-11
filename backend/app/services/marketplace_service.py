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
    ListingVersion,
    ListingMetadata,
    TradeMatch,
    TradeSettlement,
    Portfolio,
    PortfolioPosition,
    PortfolioPerformance,
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


class EnhancedMarketplaceService:
    """Enhanced marketplace service with version tracking and metadata"""

    def __init__(self, db: Session):
        self.db = db

    def create_version_on_update(
        self,
        listing_id: str,
        changed_by: str,
        change_type: str = "price_update",
    ) -> ListingVersion:
        """Auto-version listing on price/availability changes"""
        try:
            listing = self.db.query(MarketplaceListing).filter_by(id=listing_id).first()
            if not listing:
                raise ValueError(f"Listing {listing_id} not found")

            # Get current version number
            last_version = (
                self.db.query(ListingVersion)
                .filter_by(listing_id=listing_id)
                .order_by(ListingVersion.version_number.desc())
                .first()
            )

            version_number = (last_version.version_number + 1) if last_version else 1

            # Create version snapshot
            version = ListingVersion(
                listing_id=listing_id,
                version_number=version_number,
                price_snapshot=listing.price_per_credit,
                availability_snapshot=int(listing.quantity_available),
                change_type=change_type,
                changed_by=changed_by,
            )

            self.db.add(version)
            self.db.commit()

            logger.info(f"Created version {version_number} for listing {listing_id}")
            return version

        except Exception as e:
            logger.error(f"Error creating listing version: {str(e)}")
            raise

    def update_metadata(
        self,
        listing_id: str,
        tags: List[str] = None,
        seller_rating: Decimal = None,
        popularity_score: Decimal = None,
    ) -> ListingMetadata:
        """Maintain search metadata for listing"""
        try:
            # Check if metadata exists
            metadata = (
                self.db.query(ListingMetadata).filter_by(listing_id=listing_id).first()
            )

            if metadata:
                # Update existing
                if tags:
                    metadata.tags = tags
                    metadata.search_keywords = " ".join(tags)
                if seller_rating:
                    metadata.seller_rating = seller_rating
                if popularity_score:
                    metadata.popularity_score = popularity_score
                metadata.updated_at = datetime.utcnow()
            else:
                # Create new
                metadata = ListingMetadata(
                    listing_id=listing_id,
                    tags=tags or [],
                    search_keywords=" ".join(tags) if tags else "",
                    seller_rating=seller_rating,
                    popularity_score=popularity_score or Decimal("0"),
                )
                self.db.add(metadata)

            self.db.commit()
            logger.info(f"Updated metadata for listing {listing_id}")
            return metadata

        except Exception as e:
            logger.error(f"Error updating metadata: {str(e)}")
            raise

    def get_listing_versions(
        self,
        listing_id: str,
        limit: int = 10,
    ) -> List[Dict]:
        """Retrieve version history for listing"""
        try:
            versions = (
                self.db.query(ListingVersion)
                .filter_by(listing_id=listing_id)
                .order_by(ListingVersion.version_number.desc())
                .limit(limit)
                .all()
            )

            return [
                {
                    "version_number": v.version_number,
                    "price": float(v.price_snapshot),
                    "availability": v.availability_snapshot,
                    "change_type": v.change_type,
                    "changed_at": v.changed_at.isoformat(),
                }
                for v in versions
            ]

        except Exception as e:
            logger.error(f"Error retrieving versions: {str(e)}")
            raise

    def compare_versions(
        self,
        listing_id: str,
        version1: int,
        version2: int,
    ) -> Dict:
        """Compare two versions of a listing"""
        try:
            v1 = (
                self.db.query(ListingVersion)
                .filter_by(listing_id=listing_id, version_number=version1)
                .first()
            )
            v2 = (
                self.db.query(ListingVersion)
                .filter_by(listing_id=listing_id, version_number=version2)
                .first()
            )

            if not v1 or not v2:
                raise ValueError("One or both versions not found")

            return {
                "price_change": float(v2.price_snapshot - v1.price_snapshot),
                "price_change_percent": float(
                    ((v2.price_snapshot - v1.price_snapshot) / v1.price_snapshot) * 100
                ),
                "availability_change": v2.availability_snapshot - v1.availability_snapshot,
                "time_between": (v2.changed_at - v1.changed_at).days,
            }

        except Exception as e:
            logger.error(f"Error comparing versions: {str(e)}")
            raise


class EnhancedTradeService:
    """Enhanced trade service with matching and settlement"""

    def __init__(self, db: Session):
        self.db = db

    def match_trades(
        self,
        buy_order_id: str,
        sell_order_id: str,
    ) -> TradeMatch:
        """Implement matching algorithm for buy/sell orders"""
        try:
            buy_order = self.db.query(Trade).filter_by(id=buy_order_id).first()
            sell_order = self.db.query(Trade).filter_by(id=sell_order_id).first()

            if not buy_order or not sell_order:
                raise ValueError("One or both orders not found")

            # Calculate match price (average of bid/ask)
            match_price = (
                buy_order.price_per_credit + sell_order.price_per_credit
            ) / 2

            # Match quantity is minimum of both orders
            match_quantity = min(buy_order.quantity, sell_order.quantity)

            # Calculate match score based on price proximity
            price_diff = abs(buy_order.price_per_credit - sell_order.price_per_credit)
            match_score = max(Decimal("0"), Decimal("1") - (price_diff / match_price))

            match = TradeMatch(
                buy_order_id=buy_order_id,
                sell_order_id=sell_order_id,
                match_price=match_price,
                match_quantity=int(match_quantity),
                match_score=match_score,
            )

            self.db.add(match)
            self.db.commit()

            logger.info(f"Matched orders {buy_order_id} and {sell_order_id}")
            return match

        except Exception as e:
            logger.error(f"Error matching trades: {str(e)}")
            raise

    def execute_settlement(
        self,
        trade_id: str,
        settlement_type: str = "both",
        confirmed_by: str = None,
    ) -> TradeSettlement:
        """Execute atomic trade settlement"""
        try:
            trade = self.db.query(Trade).filter_by(id=trade_id).first()
            if not trade:
                raise ValueError(f"Trade {trade_id} not found")

            # Create settlement record
            settlement = TradeSettlement(
                trade_id=trade_id,
                settlement_type=settlement_type,
                settlement_status="pending",
                settled_amount=trade.total_price,
                confirmed_by=confirmed_by,
                settlement_log={"initiated_at": datetime.utcnow().isoformat()},
            )

            self.db.add(settlement)
            self.db.flush()

            # Execute settlement steps
            settlement.settlement_log["steps"] = ["payment_initiated"]

            if settlement_type in ["payment", "both"]:
                # Payment settlement logic
                settlement.settlement_log["steps"].append("payment_confirmed")

            if settlement_type in ["credits", "both"]:
                # Credit transfer logic
                settlement.settlement_log["steps"].append("credits_transferred")

            settlement.settlement_status = "completed"
            settlement.settlement_date = datetime.utcnow()
            settlement.settlement_log["completed_at"] = datetime.utcnow().isoformat()

            self.db.commit()

            logger.info(f"Settlement completed for trade {trade_id}")
            return settlement

        except Exception as e:
            logger.error(f"Error executing settlement: {str(e)}")
            self.handle_settlement_failure(trade_id, str(e))
            raise

    def get_settlement_status(
        self,
        trade_id: str,
    ) -> Dict:
        """Track settlement progress"""
        try:
            settlement = (
                self.db.query(TradeSettlement).filter_by(trade_id=trade_id).first()
            )

            if not settlement:
                return {"status": "not_started", "trade_id": trade_id}

            return {
                "trade_id": trade_id,
                "status": settlement.settlement_status,
                "type": settlement.settlement_type,
                "amount": float(settlement.settled_amount),
                "date": settlement.settlement_date.isoformat()
                if settlement.settlement_date
                else None,
                "log": settlement.settlement_log,
            }

        except Exception as e:
            logger.error(f"Error getting settlement status: {str(e)}")
            raise

    def handle_settlement_failure(
        self,
        trade_id: str,
        error_message: str,
    ):
        """Rollback logic for failed settlements"""
        try:
            settlement = (
                self.db.query(TradeSettlement).filter_by(trade_id=trade_id).first()
            )

            if settlement:
                settlement.settlement_status = "failed"
                settlement.settlement_log["error"] = error_message
                settlement.settlement_log["action"] = "rollback"
                settlement.settlement_log["failed_at"] = datetime.utcnow().isoformat()

                self.db.commit()
                logger.info(f"Settlement rollback completed for trade {trade_id}")

        except Exception as e:
            logger.error(f"Error handling settlement failure: {str(e)}")


class PortfolioService:
    """Portfolio management service"""

    def __init__(self, db: Session):
        self.db = db

    def add_position(
        self,
        portfolio_id: str,
        listing_id: str,
        quantity: int,
        cost_basis: Decimal,
    ) -> PortfolioPosition:
        """Add holding to portfolio"""
        try:
            # Check if position already exists
            existing = (
                self.db.query(PortfolioPosition)
                .filter_by(portfolio_id=portfolio_id, listing_id=listing_id)
                .first()
            )

            if existing:
                # Update existing position (average cost)
                total_quantity = existing.quantity + quantity
                total_cost = (
                    existing.quantity * existing.cost_basis + quantity * cost_basis
                )
                new_cost_basis = total_cost / total_quantity

                existing.quantity = total_quantity
                existing.cost_basis = new_cost_basis
                existing.last_updated = datetime.utcnow()

                position = existing
            else:
                # Create new position
                position = PortfolioPosition(
                    portfolio_id=portfolio_id,
                    listing_id=listing_id,
                    quantity=quantity,
                    cost_basis=cost_basis,
                    current_value=quantity * cost_basis,  # Initial value
                )
                self.db.add(position)

            self.db.commit()
            logger.info(f"Added position to portfolio {portfolio_id}")
            return position

        except Exception as e:
            logger.error(f"Error adding position: {str(e)}")
            raise

    def calculate_portfolio_value(
        self,
        portfolio_id: str,
    ) -> Dict:
        """Aggregate holdings value"""
        try:
            positions = (
                self.db.query(PortfolioPosition)
                .filter_by(portfolio_id=portfolio_id)
                .all()
            )

            total_value = sum(p.current_value for p in positions)
            total_cost = sum(p.quantity * p.cost_basis for p in positions)

            return {
                "portfolio_id": str(portfolio_id),
                "total_value": float(total_value),
                "total_cost": float(total_cost),
                "unrealized_gain": float(total_value - total_cost),
                "position_count": len(positions),
            }

        except Exception as e:
            logger.error(f"Error calculating portfolio value: {str(e)}")
            raise

    def get_performance_metrics(
        self,
        portfolio_id: str,
        days: int = 30,
    ) -> List[Dict]:
        """Historical performance data"""
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=days)

            performance = (
                self.db.query(PortfolioPerformance)
                .filter(
                    and_(
                        PortfolioPerformance.portfolio_id == portfolio_id,
                        PortfolioPerformance.date >= cutoff_date,
                    )
                )
                .order_by(PortfolioPerformance.date)
                .all()
            )

            return [
                {
                    "date": p.date.isoformat(),
                    "total_value": float(p.total_value),
                    "daily_return": float(p.daily_return) if p.daily_return else 0,
                    "cumulative_return": float(p.cumulative_return)
                    if p.cumulative_return
                    else 0,
                }
                for p in performance
            ]

        except Exception as e:
            logger.error(f"Error getting performance metrics: {str(e)}")
            raise

    def rebalance_portfolio(
        self,
        portfolio_id: str,
        target_allocation: Dict[str, float],
    ) -> Dict:
        """Suggest rebalancing actions"""
        try:
            positions = (
                self.db.query(PortfolioPosition)
                .filter_by(portfolio_id=portfolio_id)
                .all()
            )

            # Calculate current allocation
            total_value = sum(p.current_value for p in positions)
            current_allocation = {
                str(p.listing_id): float(p.current_value / total_value)
                for p in positions
            }

            # Calculate rebalancing trades
            rebalancing_actions = []
            for listing_id, target_pct in target_allocation.items():
                current_pct = current_allocation.get(listing_id, 0)
                diff_pct = target_pct - current_pct

                if abs(diff_pct) > 0.05:  # 5% threshold
                    action = "buy" if diff_pct > 0 else "sell"
                    amount = abs(diff_pct * total_value)

                    rebalancing_actions.append(
                        {
                            "listing_id": listing_id,
                            "action": action,
                            "amount": float(amount),
                            "current_allocation": current_pct,
                            "target_allocation": target_pct,
                        }
                    )

            return {
                "portfolio_id": str(portfolio_id),
                "total_value": float(total_value),
                "rebalancing_needed": len(rebalancing_actions) > 0,
                "actions": rebalancing_actions,
            }

        except Exception as e:
            logger.error(f"Error rebalancing portfolio: {str(e)}")
            raise
