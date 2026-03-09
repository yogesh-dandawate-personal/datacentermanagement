"""JWT token handler"""
from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt, ExpiredSignatureError
import os
import logging
from app.exceptions import InvalidTokenError, TokenExpiredError
from app.schemas import TokenData

logger = logging.getLogger(__name__)

# JWT Configuration
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))


def create_access_token(
    user_id: str,
    tenant_id: str,
    roles: Optional[list[str]] = None,
    expires_delta: Optional[timedelta] = None
) -> str:
    """
    Create JWT access token for user

    Args:
        user_id: UUID of the user
        tenant_id: UUID of the tenant
        roles: List of user roles (e.g., ["admin", "editor"])
        expires_delta: Custom expiration time delta

    Returns:
        JWT token string

    Raises:
        ValueError: If user_id or tenant_id is empty
    """
    if not user_id or not tenant_id:
        raise ValueError("user_id and tenant_id are required")

    roles = roles or []
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))

    to_encode = {
        "sub": str(user_id),
        "tenant_id": str(tenant_id),
        "roles": roles,
        "exp": expire,
        "iat": datetime.utcnow()
    }

    try:
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        logger.info(f"Created token for user {user_id} in tenant {tenant_id}")
        return encoded_jwt
    except Exception as e:
        logger.error(f"Failed to create token: {str(e)}")
        raise


def verify_token(token: str) -> TokenData:
    """
    Verify JWT token and extract claims

    Args:
        token: JWT token string

    Returns:
        TokenData object with user_id, tenant_id, roles

    Raises:
        TokenExpiredError: If token has expired
        InvalidTokenError: If token is invalid or malformed
    """
    if not token:
        raise InvalidTokenError("Token is required")

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        tenant_id: str = payload.get("tenant_id")
        roles: list = payload.get("roles", [])

        if not user_id or not tenant_id:
            logger.warning("Token missing required claims (sub or tenant_id)")
            raise InvalidTokenError("Token missing required claims")

        return TokenData(
            sub=user_id,
            tenant_id=tenant_id,
            roles=roles,
            exp=datetime.fromtimestamp(payload.get("exp"))
        )

    except ExpiredSignatureError:
        logger.warning("Token verification failed: token expired")
        raise TokenExpiredError()
    except JWTError as e:
        logger.warning(f"Token verification failed: {str(e)}")
        raise InvalidTokenError(f"Invalid token: {str(e)}")
    except Exception as e:
        logger.error(f"Unexpected error verifying token: {str(e)}")
        raise InvalidTokenError("Failed to verify token")
