"""Authentication API routes - Login, Refresh Token, Register"""
import logging
from datetime import timedelta
from fastapi import APIRouter, HTTPException, Depends, Header
from sqlalchemy import and_
from sqlalchemy.orm import Session
from typing import Optional

from app.database import get_db
from app.auth.auth_service import (
    AuthService,
    get_current_user_from_token
)
from app.models import User, Tenant
from app.schemas import LoginRequest, LoginResponse, RefreshTokenRequest, UserCreate, UserResponse
from app.exceptions import AuthenticationError

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/auth", tags=["authentication"])


@router.post("/login", response_model=LoginResponse, status_code=200)
async def login(
    credentials: LoginRequest,
    db = Depends(get_db)
):
    """
    Login with email and password

    This endpoint validates user credentials against the database and returns JWT tokens.

    Args:
        credentials: Email and password

    Returns:
        LoginResponse with access_token, refresh_token, user_id, tenant_id, and roles

    Raises:
        HTTPException: 401 if credentials are invalid
        HTTPException: 400 if email/password missing
    """
    logger.info(f"Login attempt for email: {credentials.email}")

    try:
        # Query user by email - must be active
        user = db.query(User).filter(
            and_(
                User.email == credentials.email.lower(),
                User.is_active == True
            )
        ).first()

        if not user:
            logger.warning(f"Login failed: user not found - {credentials.email}")
            raise HTTPException(
                status_code=401,
                detail="Invalid email or password"
            )

        # Verify password
        if not user.password_hash:
            logger.warning(
                f"Login failed: user has no password set - {credentials.email}"
            )
            raise HTTPException(
                status_code=401,
                detail="Invalid email or password"
            )

        if not AuthService.validate_credentials(
            credentials.password,
            user.password_hash
        ):
            logger.warning(f"Login failed: invalid password - {credentials.email}")
            raise HTTPException(
                status_code=401,
                detail="Invalid email or password"
            )

        # Get user roles
        roles = [role.name for role in user.roles]

        # Generate tokens
        access_token = AuthService.create_access_token(
            user_id=str(user.id),
            tenant_id=str(user.tenant_id),
            roles=roles,
            expires_delta=timedelta(hours=24)
        )

        refresh_token = AuthService.create_refresh_token(
            user_id=str(user.id),
            tenant_id=str(user.tenant_id),
            expires_delta=timedelta(days=7)
        )

        # Update last_login timestamp
        user.last_login = datetime.utcnow()
        db.commit()

        logger.info(f"Login successful for user: {user.id}")

        return LoginResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
            user_id=str(user.id),
            tenant_id=str(user.tenant_id),
            roles=roles
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error during login: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Internal server error"
        )


@router.post("/refresh-token", response_model=LoginResponse, status_code=200)
async def refresh_token_endpoint(
    request: RefreshTokenRequest,
    db = Depends(get_db)
):
    """
    Refresh access token using refresh token

    This endpoint validates the refresh token and returns a new access token.

    Args:
        request: RefreshTokenRequest with refresh_token

    Returns:
        LoginResponse with new access_token

    Raises:
        HTTPException: 401 if refresh token is invalid or expired
    """
    logger.info("Refresh token request")

    try:
        # Verify refresh token
        token_data = AuthService.verify_token(request.refresh_token)

        # Get user to ensure they still exist and are active
        user = db.query(User).filter(
            and_(
                User.id == token_data.sub,
                User.tenant_id == token_data.tenant_id,
                User.is_active == True
            )
        ).first()

        if not user:
            logger.warning(f"Refresh token failed: user not found - {token_data.sub}")
            raise HTTPException(
                status_code=401,
                detail="Invalid or expired refresh token"
            )

        # Get user roles
        roles = [role.name for role in user.roles]

        # Generate new access token
        new_access_token = AuthService.create_access_token(
            user_id=str(user.id),
            tenant_id=str(user.tenant_id),
            roles=roles,
            expires_delta=timedelta(hours=24)
        )

        logger.info(f"Token refreshed for user: {user.id}")

        return LoginResponse(
            access_token=new_access_token,
            refresh_token=request.refresh_token,  # Return same refresh token
            token_type="bearer",
            user_id=str(user.id),
            tenant_id=str(user.tenant_id),
            roles=roles
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error during token refresh: {str(e)}")
        raise HTTPException(
            status_code=401,
            detail="Invalid or expired refresh token"
        )


@router.post("/register", response_model=UserResponse, status_code=201)
async def register(
    user_data: UserCreate,
    password: str,
    db = Depends(get_db)
):
    """
    Register a new user with email, password, and tenant

    Args:
        user_data: User creation data (email, tenant_id, roles)
        password: Plain text password (must be 8+ characters)

    Returns:
        UserResponse with created user details

    Raises:
        HTTPException: 400 if validation fails
        HTTPException: 409 if user already exists
        HTTPException: 404 if tenant doesn't exist
    """
    logger.info(f"Register request for email: {user_data.email}")

    try:
        # Validate password
        if not password or len(password) < 8:
            raise HTTPException(
                status_code=400,
                detail="Password must be at least 8 characters long"
            )

        # Check if tenant exists
        tenant = db.query(Tenant).filter_by(id=user_data.tenant_id).first()
        if not tenant:
            raise HTTPException(
                status_code=404,
                detail="Tenant not found"
            )

        # Check if user already exists
        existing_user = db.query(User).filter(
            and_(
                User.email == user_data.email.lower(),
                User.tenant_id == user_data.tenant_id
            )
        ).first()

        if existing_user:
            logger.warning(f"Register failed: user already exists - {user_data.email}")
            raise HTTPException(
                status_code=409,
                detail="User with this email already exists in tenant"
            )

        # Hash password
        password_hash = AuthService.hash_password(password)

        # Create user
        new_user = User(
            tenant_id=user_data.tenant_id,
            email=user_data.email.lower(),
            password_hash=password_hash,
            is_active=True
        )

        db.add(new_user)
        db.commit()
        db.refresh(new_user)

        logger.info(f"User registered successfully: {new_user.id}")

        return UserResponse(
            id=str(new_user.id),
            tenant_id=str(new_user.tenant_id),
            email=new_user.email,
            created_at=new_user.created_at
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error during registration: {str(e)}")
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail="Failed to register user"
        )


@router.post("/logout", status_code=204)
async def logout(
    authorization: Optional[str] = Header(None),
    db = Depends(get_db)
):
    """
    Logout (invalidate current session)

    This is a client-side logout that doesn't require server-side action since
    we're using stateless JWT tokens. The client should discard the token.

    Args:
        authorization: Authorization header (for validation)

    Returns:
        204 No Content
    """
    try:
        # Validate token exists and is valid
        user = await get_current_user_from_token(authorization=authorization, db=db)
        logger.info(f"User logout: {user['user_id']}")
        return None

    except Exception as e:
        logger.error(f"Error during logout: {str(e)}")
        # Even if token is invalid, return 204 since client is trying to logout
        return None


@router.get("/me", response_model=UserResponse)
async def get_current_user(
    current_user: dict = Depends(get_current_user_from_token),
    db = Depends(get_db)
):
    """
    Get current authenticated user details

    Args:
        current_user: Current user context from token

    Returns:
        UserResponse with user details

    Raises:
        HTTPException: 401 if not authenticated
        HTTPException: 404 if user not found
    """
    try:
        user = db.query(User).filter_by(id=current_user['user_id']).first()

        if not user:
            logger.warning(f"Current user not found: {current_user['user_id']}")
            raise HTTPException(
                status_code=404,
                detail="User not found"
            )

        return UserResponse(
            id=str(user.id),
            tenant_id=str(user.tenant_id),
            email=user.email,
            created_at=user.created_at
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting current user: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Failed to get user details"
        )


# Import datetime for last_login update
from datetime import datetime
