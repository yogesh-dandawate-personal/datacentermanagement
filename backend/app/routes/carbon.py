"""Carbon emissions calculation and management API routes"""

from fastapi import APIRouter, HTTPException, Depends, Header, Query
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime
import logging

from app.database import get_db
from app.auth.jwt_handler import verify_token
from app.auth.utils import extract_token_from_header
from app.services.carbon_service import CarbonCalculationService, EmissionFactorService
from app.models import EmissionFactor

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1", tags=["carbon"])


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


@router.get("/tenants/{tenant_id}/factors")
async def list_emission_factors(
    tenant_id: str,
    factor_type: Optional[str] = Query(None),
    region: Optional[str] = Query("Global"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """
    List available emission factors

    Query parameters:
    - factor_type: Filter by type (scope1, scope2, fuel, electricity, refrigerant)
    - region: Filter by region (default: Global)
    """
    if current_user["tenant_id"] != tenant_id:
        raise HTTPException(status_code=403, detail="Tenant mismatch")

    try:
        query = db.query(EmissionFactor).filter_by(is_active=True)

        if factor_type:
            query = query.filter_by(factor_type=factor_type)

        if region:
            query = query.filter_by(region=region)

        factors = query.all()

        return {
            "count": len(factors),
            "factors": [
                {
                    "id": str(f.id),
                    "name": f.factor_name,
                    "type": f.factor_type,
                    "value": float(f.value),
                    "unit": f.unit,
                    "region": f.region,
                    "data_source": f.data_source,
                    "effective_date": f.effective_date.isoformat(),
                }
                for f in factors
            ],
        }

    except Exception as e:
        logger.error(f"Error retrieving emission factors: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/factors/{factor_id}/versions")
async def get_factor_versions(
    factor_id: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """
    Get version history for an emission factor

    Useful for understanding when factors changed and why
    """
    try:
        factor_service = EmissionFactorService(db)
        history = factor_service.get_factor_history(factor_id)

        if not history:
            raise HTTPException(status_code=404, detail="Factor not found")

        return {
            "factor_id": factor_id,
            "version_count": len(history),
            "versions": history,
        }

    except Exception as e:
        logger.error(f"Error retrieving factor versions: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/tenants/{tenant_id}/carbon/calculate")
async def calculate_emissions(
    tenant_id: str,
    org_id: str = Query(...),
    period_start: str = Query(...),
    period_end: str = Query(...),
    region: str = Query("US-East"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """
    Trigger carbon emissions calculation

    Creates a draft calculation that can be reviewed and approved

    Query parameters:
    - org_id: Organization UUID
    - period_start: Start date (ISO format)
    - period_end: End date (ISO format)
    - region: Emission factor region (default: US-East)
    """
    if current_user["tenant_id"] != tenant_id:
        raise HTTPException(status_code=403, detail="Tenant mismatch")

    try:
        start_dt = datetime.fromisoformat(period_start)
        end_dt = datetime.fromisoformat(period_end)

        service = CarbonCalculationService(db)
        calculation = service.create_calculation(
            tenant_id=tenant_id,
            organization_id=org_id,
            period_start=start_dt,
            period_end=end_dt,
            region=region,
        )

        return {
            "calculation_id": str(calculation.id),
            "status": calculation.status,
            "scope_1_emissions": float(calculation.scope_1_emissions),
            "scope_2_emissions": float(calculation.scope_2_emissions),
            "scope_3_emissions": float(calculation.scope_3_emissions),
            "total_emissions": float(calculation.total_emissions),
            "created_at": calculation.created_at.isoformat(),
        }

    except Exception as e:
        logger.error(f"Error calculating emissions: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/carbon-calculations/{calc_id}")
async def get_calculation(
    calc_id: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """
    Get complete calculation with audit trail

    Returns all details including energy inputs, factors used, and results
    """
    try:
        service = CarbonCalculationService(db)
        details = service.get_calculation_details(calc_id)

        return details

    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error retrieving calculation: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/carbon-calculations/{calc_id}/submit-for-review")
async def submit_for_review(
    calc_id: str,
    comments: str = Query(""),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """
    Submit a calculation for review and approval

    Transitions status from 'draft' to 'ready_for_review'
    """
    try:
        service = CarbonCalculationService(db)
        calculation = service.submit_for_review(calc_id)

        return {
            "calculation_id": str(calculation.id),
            "status": calculation.status,
            "message": "Calculation submitted for review",
        }

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error submitting calculation: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/carbon-calculations/{calc_id}/approve")
async def approve_calculation(
    calc_id: str,
    approval_notes: str = Query(""),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """
    Approve a calculation (admin only)

    Transitions status from 'ready_for_review' to 'approved'
    """
    # Check admin role
    if "admin" not in current_user.get("roles", []):
        raise HTTPException(status_code=403, detail="Only admins can approve calculations")

    try:
        service = CarbonCalculationService(db)
        calculation = service.approve_calculation(
            calc_id,
            approver_id=current_user["user_id"],
            approval_notes=approval_notes,
        )

        return {
            "calculation_id": str(calculation.id),
            "status": calculation.status,
            "approved_at": calculation.approved_at.isoformat(),
            "message": "Calculation approved",
        }

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error approving calculation: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/carbon-calculations/{calc_id}/recalculate")
async def recalculate_emissions(
    calc_id: str,
    region: str = Query("US-East"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """
    Recalculate emissions using different factors

    Useful for sensitivity analysis or when better factors become available
    """
    try:
        service = CarbonCalculationService(db)
        calculation = service.recalculate_with_factors(calc_id)

        return {
            "calculation_id": str(calculation.id),
            "status": calculation.status,
            "total_emissions": float(calculation.total_emissions),
            "message": "Calculation recalculated",
        }

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error recalculating emissions: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
