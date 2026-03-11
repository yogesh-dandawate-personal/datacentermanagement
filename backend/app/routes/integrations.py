"""
Integration API Routes
Sprint 12 - External integrations endpoints
"""

from typing import Dict, List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.jwt_handler import get_current_user
from app.database import get_db
from app.services.integrations import integration_service
from app.exceptions import ValidationError, NotFoundError


router = APIRouter(prefix="/api/v1/integrations", tags=["integrations"])


class IntegrationCreate(BaseModel):
    integration_type: str = Field(..., description="Integration type (salesforce, slack, github, etc.)")
    credentials: Dict[str, str] = Field(..., description="API credentials")
    endpoint: Optional[str] = Field(None, description="Custom API endpoint")


class IntegrationResponse(BaseModel):
    id: str
    tenant_id: str
    integration_type: str
    api_endpoint: str
    is_active: bool
    created_at: str


class OAuthExchange(BaseModel):
    code: str = Field(..., description="OAuth authorization code")
    redirect_uri: str = Field(..., description="Redirect URI")


class APICallRequest(BaseModel):
    method: str = Field(..., description="HTTP method")
    endpoint: str = Field(..., description="API endpoint")
    data: Optional[Dict] = None
    params: Optional[Dict] = None


@router.post("/", response_model=IntegrationResponse)
async def create_integration(
    request: IntegrationCreate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Create new API integration"""
    try:
        integration = await integration_service.create_integration(
            db,
            UUID(current_user["tenant_id"]),
            request.integration_type,
            request.credentials,
            request.endpoint
        )

        return IntegrationResponse(
            id=str(integration.id),
            tenant_id=str(integration.tenant_id),
            integration_type=integration.integration_type,
            api_endpoint=integration.api_endpoint,
            is_active=integration.is_active,
            created_at=integration.created_at.isoformat()
        )

    except ValidationError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/", response_model=List[IntegrationResponse])
async def list_integrations(
    integration_type: Optional[str] = None,
    is_active: Optional[bool] = None,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """List all integrations"""
    integrations = await integration_service.list_integrations(
        db,
        UUID(current_user["tenant_id"]),
        integration_type,
        is_active
    )

    return [
        IntegrationResponse(
            id=str(i.id),
            tenant_id=str(i.tenant_id),
            integration_type=i.integration_type,
            api_endpoint=i.api_endpoint,
            is_active=i.is_active,
            created_at=i.created_at.isoformat()
        )
        for i in integrations
    ]


@router.get("/{integration_id}", response_model=IntegrationResponse)
async def get_integration(
    integration_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get integration by ID"""
    integration = await integration_service.get_integration(
        db,
        UUID(current_user["tenant_id"]),
        integration_id
    )

    if not integration:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Integration not found")

    return IntegrationResponse(
        id=str(integration.id),
        tenant_id=str(integration.tenant_id),
        integration_type=integration.integration_type,
        api_endpoint=integration.api_endpoint,
        is_active=integration.is_active,
        created_at=integration.created_at.isoformat()
    )


@router.delete("/{integration_id}")
async def delete_integration(
    integration_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Delete integration"""
    try:
        await integration_service.delete_integration(
            db,
            UUID(current_user["tenant_id"]),
            integration_id
        )

        return {"message": "Integration deleted successfully"}

    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.post("/{integration_id}/oauth/exchange")
async def exchange_oauth_code(
    integration_id: UUID,
    request: OAuthExchange,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Exchange OAuth authorization code for access token"""
    try:
        token_data = await integration_service.exchange_oauth_code(
            db,
            integration_id,
            request.code,
            request.redirect_uri
        )

        return {
            "access_token": token_data.get("access_token"),
            "token_type": token_data.get("token_type", "Bearer"),
            "expires_in": token_data.get("expires_in")
        }

    except (ValidationError, NotFoundError) as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/{integration_id}/oauth/refresh")
async def refresh_oauth_token(
    integration_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Refresh OAuth access token"""
    try:
        token_data = await integration_service.refresh_oauth_token(
            db,
            integration_id
        )

        return {
            "access_token": token_data.get("access_token"),
            "token_type": token_data.get("token_type", "Bearer"),
            "expires_in": token_data.get("expires_in")
        }

    except (ValidationError, NotFoundError) as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/{integration_id}/call")
async def make_api_call(
    integration_id: UUID,
    request: APICallRequest,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Make API call to integration"""
    try:
        result = await integration_service.make_api_call(
            db,
            integration_id,
            request.method,
            request.endpoint,
            request.data,
            request.params
        )

        return result

    except (ValidationError, NotFoundError) as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/{integration_id}/salesforce/sync")
async def sync_salesforce(
    integration_id: UUID,
    object_type: str = "Account",
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Sync data from Salesforce"""
    try:
        result = await integration_service.sync_salesforce_data(
            db,
            integration_id,
            object_type
        )

        return result

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/{integration_id}/slack/notify")
async def send_slack_notification(
    integration_id: UUID,
    channel: str,
    message: str,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Send Slack notification"""
    try:
        result = await integration_service.send_slack_notification(
            db,
            integration_id,
            channel,
            message
        )

        return result

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/{integration_id}/github/deployments")
async def get_github_deployments(
    integration_id: UUID,
    owner: str,
    repo: str,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get GitHub deployments"""
    try:
        result = await integration_service.get_github_deployments(
            db,
            integration_id,
            owner,
            repo
        )

        return result

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
