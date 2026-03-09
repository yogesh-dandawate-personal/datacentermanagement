from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from app.auth.jwt_handler import create_access_token, verify_token
from app.models import Tenant, User, Role, Base
from pydantic import BaseModel
import uuid

# Initialize FastAPI app
app = FastAPI(
    title="NetZero API",
    description="ESG & Carbon Credit Platform",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Pydantic models for API
class TenantCreate(BaseModel):
    name: str
    slug: str
    email: str


class TenantResponse(BaseModel):
    id: str
    name: str
    slug: str
    email: str
    is_active: bool


class LoginRequest(BaseModel):
    email: str
    password: str


class LoginResponse(BaseModel):
    access_token: str
    token_type: str
    user_id: str


class UserCreate(BaseModel):
    email: str
    first_name: str
    last_name: str
    role: str = "viewer"


# Routes
@app.post("/api/v1/tenants", response_model=TenantResponse, status_code=201)
async def create_tenant(tenant: TenantCreate):
    """Create new tenant"""
    # In production, this would be saved to database
    return TenantResponse(
        id=str(uuid.uuid4()),
        name=tenant.name,
        slug=tenant.slug,
        email=tenant.email,
        is_active=True
    )


@app.post("/api/v1/auth/login", response_model=LoginResponse)
async def login(credentials: LoginRequest):
    """User login endpoint"""
    # TODO: Validate against Keycloak or database
    user_id = str(uuid.uuid4())
    tenant_id = str(uuid.uuid4())
    
    token = create_access_token(
        user_id=user_id,
        tenant_id=tenant_id,
        roles=["admin", "editor"]
    )
    
    return LoginResponse(
        access_token=token,
        token_type="bearer",
        user_id=user_id
    )


@app.get("/api/v1/users/me")
async def get_current_user(authorization: str):
    """Get current authenticated user"""
    try:
        token = authorization.replace("Bearer ", "")
        token_data = verify_token(token)
        return {
            "id": token_data.sub,
            "tenant_id": token_data.tenant_id,
            "roles": token_data.roles
        }
    except:
        raise HTTPException(status_code=401, detail="Invalid token")


@app.get("/api/v1/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "ok", "service": "netzero-api"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
