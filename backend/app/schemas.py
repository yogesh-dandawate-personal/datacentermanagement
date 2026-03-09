"""Pydantic schemas for request/response validation"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, Field


# Tenant Schemas
class TenantCreate(BaseModel):
    """Request schema for creating tenant"""
    name: str = Field(..., min_length=1, max_length=255, description="Organization name")
    slug: str = Field(..., min_length=1, max_length=100, description="URL-friendly slug")
    email: EmailStr = Field(..., description="Organization email")

    class Config:
        json_schema_extra = {
            "example": {
                "name": "Acme Corporation",
                "slug": "acme-corp",
                "email": "admin@acme.com"
            }
        }


class TenantResponse(BaseModel):
    """Response schema for tenant"""
    id: str
    name: str
    slug: str
    email: str
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


# User Schemas
class UserCreate(BaseModel):
    """Request schema for creating user"""
    email: EmailStr = Field(..., description="User email address")
    tenant_id: str = Field(..., description="Tenant ID")
    roles: list[str] = Field(default=["viewer"], description="User roles")

    class Config:
        json_schema_extra = {
            "example": {
                "email": "user@example.com",
                "tenant_id": "550e8400-e29b-41d4-a716-446655440000",
                "roles": ["editor"]
            }
        }


class UserResponse(BaseModel):
    """Response schema for user"""
    id: str
    tenant_id: str
    email: str
    created_at: datetime

    class Config:
        from_attributes = True


# Authentication Schemas
class LoginRequest(BaseModel):
    """Request schema for login"""
    email: EmailStr = Field(..., description="User email")
    password: str = Field(..., min_length=8, description="User password")

    class Config:
        json_schema_extra = {
            "example": {
                "email": "user@example.com",
                "password": "your-secure-password"
            }
        }


class LoginResponse(BaseModel):
    """Response schema for login"""
    access_token: str = Field(..., description="JWT access token")
    token_type: str = Field(default="bearer", description="Token type")
    user_id: str = Field(..., description="User ID")
    tenant_id: str = Field(..., description="Tenant ID")
    roles: list[str] = Field(default=[], description="User roles")

    class Config:
        json_schema_extra = {
            "example": {
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "token_type": "bearer",
                "user_id": "550e8400-e29b-41d4-a716-446655440000",
                "tenant_id": "550e8400-e29b-41d4-a716-446655440001",
                "roles": ["admin", "editor"]
            }
        }


class TokenData(BaseModel):
    """JWT token payload"""
    sub: str  # user_id
    tenant_id: str
    roles: list[str]
    exp: datetime


# Error Response Schemas
class ErrorResponse(BaseModel):
    """Standard error response"""
    error: str = Field(..., description="Error type/code")
    message: str = Field(..., description="Error message")
    status_code: int = Field(..., description="HTTP status code")
    detail: dict = Field(default_factory=dict, description="Additional error details")

    class Config:
        json_schema_extra = {
            "example": {
                "error": "validation_error",
                "message": "Invalid input provided",
                "status_code": 422,
                "detail": {"field": "email", "reason": "Invalid email format"}
            }
        }


class HealthCheckResponse(BaseModel):
    """Health check response"""
    status: str = Field(..., description="Service status")
    service: str = Field(..., description="Service name")
    version: str = Field(..., description="API version")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Response timestamp")

    class Config:
        json_schema_extra = {
            "example": {
                "status": "healthy",
                "service": "NetZero API",
                "version": "1.0.0",
                "timestamp": "2026-03-09T15:30:00"
            }
        }
