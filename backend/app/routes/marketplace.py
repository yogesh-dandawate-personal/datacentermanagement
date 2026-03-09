"""
Carbon Credit Marketplace and Trading API Routes

Endpoints for:
- Carbon credit management and batching
- Marketplace listing creation and discovery
- Trade execution and settlement
- Market analytics and insights
"""

from fastapi import APIRouter, HTTPException, Depends, Header, Query
from sqlalchemy.orm import Session
from typing import Optional
from decimal import Decimal
import logging

from app.database import get_db
from app.auth.jwt_handler import verify_token
from app.auth.utils import extract_token_from_header
from app.services.marketplace_service import (
    CarbonCreditService,
    MarketplaceListingService,
    TradeExecutionService,
    MarketplaceAnalyticsService,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1", tags=["marketplace"])


def get_current_user(authorization: str = Header(None)):
    """Extract and verify current user from token"""
    try:
        token = extract_token_from_header(authorization)
        token_data = verify_token(token)
        return {
            "user_id": token_data.sub,
            "tenant_id": token_data.tenant_id,
            "roles": token_data.roles,
        }
    except Exception as e:
        logger.error(f"Authentication error: {str(e)}")
        raise HTTPException(status_code=401, detail="Invalid token")


# ============================================================================
# CARBON CREDIT MANAGEMENT ENDPOINTS
# ============================================================================


@router.post("/organizations/{org_id}/credits/create-batch")
async def create_credit_batch(
    org_id: str,
    batch_name: str = Query(...),
    total_quantity: float = Query(...),
    credit_type: str = Query("verified"),
    vintage_year: int = Query(...),
    description: Optional[str] = Query(None),
    quality_score: float = Query(100),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """
    Create a new batch of carbon credits

    Credits are generated from carbon calculations and grouped into batches
    for marketplace listing
    """
    try:
        if total_quantity <= 0:
            raise ValueError("Quantity must be positive")

        service = CarbonCreditService(db)

        # Create credits data
        credits = [
            {
                "credit_type": credit_type,
                "vintage_year": vintage_year,
                "quantity": total_quantity,
            }
        ]

        batch = service.create_credit_batch(
            organization_id=org_id,
            tenant_id=current_user["tenant_id"],
            batch_name=batch_name,
            credits=credits,
            description=description,
            quality_score=Decimal(str(quality_score)),
        )

        return {
            "id": str(batch.id),
            "batch_name": batch.batch_name,
            "total_credits": float(batch.total_credits),
            "quality_score": float(batch.quality_score),
            "created_at": batch.created_at.isoformat(),
        }

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error creating credit batch: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/organizations/{org_id}/credits")
async def list_organization_credits(
    org_id: str,
    status: str = Query("active"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """
    List all carbon credits owned by an organization

    Optionally filter by status: active, traded, retired, expired
    """
    try:
        service = CarbonCreditService(db)
        credits = service.get_organization_credits(org_id, status=status)

        return {
            "organization_id": org_id,
            "status": status,
            "count": len(credits),
            "credits": credits,
        }

    except Exception as e:
        logger.error(f"Error listing credits: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/organizations/{org_id}/credits/{credit_id}/retire")
async def retire_credits(
    org_id: str,
    credit_id: str,
    quantity: float = Query(...),
    reason: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """
    Retire (use) carbon credits

    Retiring credits removes them from marketplace availability
    """
    try:
        service = CarbonCreditService(db)
        retirement = service.retire_credits(
            organization_id=org_id,
            tenant_id=current_user["tenant_id"],
            quantity=Decimal(str(quantity)),
            reason=reason,
        )

        return {
            "id": str(retirement.id),
            "retired_credits": float(retirement.retired_credits),
            "reason": retirement.retirement_reason,
            "retirement_date": retirement.retirement_date.isoformat(),
        }

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error retiring credits: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# MARKETPLACE LISTING ENDPOINTS
# ============================================================================


@router.post("/organizations/{org_id}/marketplace/listings")
async def create_listing(
    org_id: str,
    batch_id: str = Query(...),
    quantity: float = Query(...),
    price_per_credit: float = Query(...),
    listing_type: str = Query("fixed_price"),
    expires_in_days: int = Query(30),
    minimum_bid: Optional[float] = Query(None),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """
    Create a marketplace listing for carbon credits

    Listing types:
    - fixed_price: Sell at a fixed price
    - auction: Auction to highest bidder
    - negotiable: Allow buyers to make offers
    """
    try:
        service = MarketplaceListingService(db)
        listing = service.create_listing(
            seller_id=org_id,
            batch_id=batch_id,
            tenant_id=current_user["tenant_id"],
            quantity=Decimal(str(quantity)),
            price_per_credit=Decimal(str(price_per_credit)),
            listing_type=listing_type,
            expires_in_days=expires_in_days,
            minimum_bid=Decimal(str(minimum_bid)) if minimum_bid else None,
        )

        return {
            "id": str(listing.id),
            "quantity": float(listing.quantity_available),
            "price_per_credit": float(listing.price_per_credit),
            "type": listing.listing_type,
            "status": listing.status,
            "expires_at": listing.expires_at.isoformat() if listing.expires_at else None,
        }

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error creating listing: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/marketplace/listings")
async def list_marketplace_listings(
    min_price: Optional[float] = Query(None),
    max_price: Optional[float] = Query(None),
    limit: int = Query(100),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """
    List all active marketplace listings

    Optionally filter by price range
    """
    try:
        service = MarketplaceListingService(db)
        listings = service.list_active_listings(
            tenant_id=current_user["tenant_id"],
            min_price=Decimal(str(min_price)) if min_price else None,
            max_price=Decimal(str(max_price)) if max_price else None,
            limit=limit,
        )

        return {
            "count": len(listings),
            "listings": listings,
        }

    except Exception as e:
        logger.error(f"Error listing marketplace: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/marketplace/listings/{listing_id}")
async def get_listing(
    listing_id: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """Get detailed information about a specific listing"""
    try:
        from app.models import MarketplaceListing

        listing = db.query(MarketplaceListing).filter_by(id=listing_id).first()
        if not listing:
            raise HTTPException(status_code=404, detail="Listing not found")

        return {
            "id": str(listing.id),
            "seller_id": str(listing.seller_id),
            "quantity_available": float(listing.quantity_available),
            "price_per_credit": float(listing.price_per_credit),
            "total_value": float(listing.quantity_available * listing.price_per_credit),
            "type": listing.listing_type,
            "status": listing.status,
            "created_at": listing.created_at.isoformat(),
            "expires_at": listing.expires_at.isoformat() if listing.expires_at else None,
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving listing: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# TRADING ENDPOINTS
# ============================================================================


@router.post("/trades/execute")
async def execute_trade(
    listing_id: str = Query(...),
    quantity: float = Query(...),
    agreed_price: Optional[float] = Query(None),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """
    Execute a carbon credit trade

    Buyer initiates trade, seller's marketplace listing is debited
    """
    try:
        service = TradeExecutionService(db)
        trade = service.execute_trade(
            listing_id=listing_id,
            buyer_id=current_user["tenant_id"],
            quantity=Decimal(str(quantity)),
            agreed_price=Decimal(str(agreed_price)) if agreed_price else None,
        )

        return {
            "id": str(trade.id),
            "listing_id": str(trade.listing_id),
            "quantity": float(trade.quantity),
            "price_per_credit": float(trade.price_per_credit),
            "total_price": float(trade.total_price),
            "status": trade.status,
            "trade_date": trade.trade_date.isoformat(),
        }

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error executing trade: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/organizations/{org_id}/trades")
async def get_trade_history(
    org_id: str,
    role: str = Query("all"),  # buyer, seller, all
    limit: int = Query(100),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """
    Get trade history for an organization

    Roles: buyer (purchases), seller (sales), all (both)
    """
    try:
        service = TradeExecutionService(db)
        trades = service.get_trade_history(org_id, role=role, limit=limit)

        return {
            "organization_id": org_id,
            "role": role,
            "count": len(trades),
            "trades": trades,
        }

    except Exception as e:
        logger.error(f"Error retrieving trade history: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/trades/{trade_id}/complete")
async def complete_trade(
    trade_id: str,
    payment_confirmed: bool = Query(True),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """Complete a trade and update its status"""
    try:
        service = TradeExecutionService(db)
        trade = service.complete_trade(trade_id, payment_confirmed=payment_confirmed)

        return {
            "id": str(trade.id),
            "status": trade.status,
            "payment_status": trade.payment_status,
            "completion_date": trade.completion_date.isoformat(),
        }

    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error completing trade: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# MARKETPLACE ANALYTICS ENDPOINTS
# ============================================================================


@router.get("/marketplace/analytics/price-history")
async def get_price_history(
    days: int = Query(30),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """Get historical price data for market trend analysis"""
    try:
        service = MarketplaceAnalyticsService(db)
        history = service.get_market_price(current_user["tenant_id"])

        listing_service = MarketplaceListingService(db)
        price_trend = listing_service.get_price_history(
            current_user["tenant_id"], days=days
        )

        return {
            "period_days": days,
            "current_price": float(history),
            "price_trend": price_trend,
        }

    except Exception as e:
        logger.error(f"Error retrieving price history: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/marketplace/analytics/volume")
async def get_trading_volume(
    days: int = Query(30),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """Get trading volume and activity metrics"""
    try:
        service = MarketplaceAnalyticsService(db)
        volume = service.get_trading_volume(current_user["tenant_id"], days=days)

        return volume

    except Exception as e:
        logger.error(f"Error retrieving trading volume: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/marketplace/analytics/market-insights")
async def get_market_insights(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """Get comprehensive market insights and recommendations"""
    try:
        service = MarketplaceAnalyticsService(db)

        current_price = service.get_market_price(current_user["tenant_id"])
        volume_30d = service.get_trading_volume(current_user["tenant_id"], days=30)

        return {
            "current_market_price": float(current_price),
            "monthly_volume": volume_30d,
            "market_status": "active",
            "recommendations": [
                "Monitor price trends for optimal selling",
                "Consider batch consolidation for better liquidity",
            ],
        }

    except Exception as e:
        logger.error(f"Error generating market insights: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
