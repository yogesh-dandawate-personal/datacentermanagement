"""Custom exceptions for NetZero API"""
from typing import Any, Optional


class NetZeroException(Exception):
    """Base exception for NetZero API"""
    def __init__(self, message: str, status_code: int = 500, detail: Optional[dict] = None):
        self.message = message
        self.status_code = status_code
        self.detail = detail or {}
        super().__init__(self.message)


class AuthenticationError(NetZeroException):
    """Authentication failed"""
    def __init__(self, message: str = "Authentication failed", detail: Optional[dict] = None):
        super().__init__(message, status_code=401, detail=detail)


class AuthorizationError(NetZeroException):
    """Authorization failed - insufficient permissions"""
    def __init__(self, message: str = "Insufficient permissions", detail: Optional[dict] = None):
        super().__init__(message, status_code=403, detail=detail)


class InvalidTokenError(AuthenticationError):
    """JWT token is invalid"""
    def __init__(self, message: str = "Invalid or expired token"):
        super().__init__(message, detail={"error": "token_invalid"})


class TokenExpiredError(AuthenticationError):
    """JWT token has expired"""
    def __init__(self, message: str = "Token has expired"):
        super().__init__(message, detail={"error": "token_expired"})


class TenantNotFoundError(NetZeroException):
    """Tenant not found"""
    def __init__(self, tenant_id: str):
        super().__init__(
            f"Tenant {tenant_id} not found",
            status_code=404,
            detail={"resource": "tenant", "id": tenant_id}
        )


class UserNotFoundError(NetZeroException):
    """User not found"""
    def __init__(self, user_id: str):
        super().__init__(
            f"User {user_id} not found",
            status_code=404,
            detail={"resource": "user", "id": user_id}
        )


class DuplicateResourceError(NetZeroException):
    """Resource already exists"""
    def __init__(self, resource: str, field: str, value: Any):
        super().__init__(
            f"{resource} with {field}='{value}' already exists",
            status_code=409,
            detail={"resource": resource, "field": field, "value": str(value)}
        )


class ValidationError(NetZeroException):
    """Validation error"""
    def __init__(self, message: str, detail: Optional[dict] = None):
        super().__init__(message, status_code=422, detail=detail)
