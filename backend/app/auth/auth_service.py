"""
Consolidated authentication service - SINGLE SOURCE OF TRUTH

This module consolidates all authentication logic that was previously duplicated
across 6 different route files. This is the central point for:
- Token generation and validation
- User context extraction
- Tenant context management
- Credential validation
"""
import logging
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from fastapi import HTTPException, Header, Depends
from sqlalchemy.orm import Session

from app.auth.jwt_handler import create_access_token, verify_token
from app.auth.utils import extract_token_from_header
from app.schemas import TokenData
from app.services.password_service import get_password_service

logger = logging.getLogger(__name__)


class AuthService:
    """Central authentication service"""

    @staticmethod
    def create_access_token(
        user_id: str,
        tenant_id: str,
        roles: Optional[list[str]] = None,
        expires_delta: Optional[timedelta] = None
    ) -> str:
        """
        Create JWT access token for user

        This is the SINGLE SOURCE OF TRUTH for token creation.
        All code should use this method instead of calling create_access_token directly.

        Args:
            user_id: UUID of the user
            tenant_id: UUID of the tenant
            roles: List of user roles
            expires_delta: Custom expiration time delta (default: 24 hours)

        Returns:
            JWT token string

        Raises:
            ValueError: If user_id or tenant_id is empty
        """
        return create_access_token(
            user_id=user_id,
            tenant_id=tenant_id,
            roles=roles or [],
            expires_delta=expires_delta or timedelta(hours=24)
        )

    @staticmethod
    def create_refresh_token(
        user_id: str,
        tenant_id: str,
        expires_delta: Optional[timedelta] = None
    ) -> str:
        """
        Create JWT refresh token for user

        Refresh tokens are longer-lived (7 days default) and used to obtain new access tokens.

        Args:
            user_id: UUID of the user
            tenant_id: UUID of the tenant
            expires_delta: Custom expiration time delta (default: 7 days)

        Returns:
            JWT refresh token string
        """
        return create_access_token(
            user_id=user_id,
            tenant_id=tenant_id,
            roles=["refresh"],
            expires_delta=expires_delta or timedelta(days=7)
        )

    @staticmethod
    def verify_token(token: str) -> TokenData:
        """
        Verify JWT token and extract claims

        This is the SINGLE SOURCE OF TRUTH for token validation.
        All code should use this method instead of calling verify_token directly.

        Args:
            token: JWT token string

        Returns:
            TokenData object with user_id, tenant_id, roles

        Raises:
            TokenExpiredError: If token has expired
            InvalidTokenError: If token is invalid
        """
        return verify_token(token)

    @staticmethod
    def validate_credentials(password: str, password_hash: str) -> bool:
        """
        Validate user credentials using Argon2

        Args:
            password: Plain text password from login request
            password_hash: Hashed password from database

        Returns:
            True if credentials match, False otherwise

        Raises:
            ValueError: If inputs are invalid
        """
        password_service = get_password_service()
        return password_service.verify_password(password, password_hash)

    @staticmethod
    def hash_password(password: str) -> str:
        """
        Hash a password using Argon2

        Args:
            password: Plain text password to hash

        Returns:
            Argon2 hash string

        Raises:
            ValueError: If password is invalid
        """
        password_service = get_password_service()
        return password_service.hash_password(password)


async def get_current_user_from_token(
    authorization: Optional[str] = Header(None)
) -> Dict[str, Any]:
    """
    Extract and verify current user from Authorization header

    This is the SINGLE SOURCE OF TRUTH for getting current user context.
    All routes should use this dependency instead of implementing it locally.

    Args:
        authorization: Authorization header value

    Returns:
        Dictionary with user_id, tenant_id, and roles

    Raises:
        HTTPException: 401 if token is missing, invalid, or expired
    """
    try:
        token = extract_token_from_header(authorization)
        token_data = AuthService.verify_token(token)
        return {
            "user_id": token_data.sub,
            "tenant_id": token_data.tenant_id,
            "roles": token_data.roles,
            "exp": token_data.exp
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Authentication error: {str(e)}")
        raise HTTPException(
            status_code=401,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"}
        )


async def get_current_user_with_role(
    required_role: str,
    authorization: Optional[str] = Header(None)
) -> Dict[str, Any]:
    """
    Get current user and verify they have required role

    Args:
        required_role: Role required for access (e.g., "admin", "editor")
        authorization: Authorization header value

    Returns:
        User context dictionary

    Raises:
        HTTPException: 403 if user doesn't have required role
    """
    user = await get_current_user_from_token(authorization=authorization)

    if required_role not in user.get("roles", []):
        logger.warning(
            f"User {user['user_id']} lacks required role: {required_role}"
        )
        raise HTTPException(
            status_code=403,
            detail=f"User lacks required role: {required_role}"
        )

    return user
