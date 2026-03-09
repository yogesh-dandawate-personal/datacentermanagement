"""Authentication utilities"""
from typing import Optional
from fastapi import Header
from app.exceptions import InvalidTokenError, AuthenticationError


def extract_token_from_header(authorization: Optional[str] = Header(None)) -> str:
    """Extract JWT token from Authorization header"""
    if not authorization:
        raise AuthenticationError("Missing Authorization header")

    parts = authorization.split()
    if len(parts) != 2 or parts[0].lower() != "bearer":
        raise AuthenticationError("Invalid Authorization header format. Expected: Bearer <token>")

    return parts[1]


def validate_token_format(token: str) -> bool:
    """Validate token format (basic checks)"""
    if not token or len(token) < 10:
        return False

    parts = token.split(".")
    return len(parts) == 3  # JWT has 3 parts: header.payload.signature
