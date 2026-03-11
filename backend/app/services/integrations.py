"""
Third-Party API Integrations Service
Sprint 12 - Task 1: External API integrations
Handles OAuth 2.0, credential management, rate limiting
"""

import asyncio
import hashlib
import hmac
import json
import time
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional
from uuid import UUID

import aiohttp
import requests
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update

from app.models import APIIntegration, APILog, Tenant
from app.exceptions import ValidationError, NotFoundError


class RateLimiter:
    """Token bucket rate limiter"""

    def __init__(self, rate: int = 100, per: int = 60):
        """
        Args:
            rate: Number of requests allowed
            per: Time period in seconds
        """
        self.rate = rate
        self.per = per
        self.allowance = rate
        self.last_check = time.time()

    async def acquire(self) -> bool:
        """Check if request is allowed"""
        current = time.time()
        time_passed = current - self.last_check
        self.last_check = current

        # Refill tokens
        self.allowance += time_passed * (self.rate / self.per)

        if self.allowance > self.rate:
            self.allowance = self.rate

        if self.allowance < 1.0:
            return False

        self.allowance -= 1.0
        return True


class IntegrationService:
    """External API integration service"""

    SUPPORTED_INTEGRATIONS = {
        "salesforce": {
            "base_url": "https://login.salesforce.com",
            "token_endpoint": "/services/oauth2/token",
            "api_version": "v54.0"
        },
        "slack": {
            "base_url": "https://slack.com",
            "token_endpoint": "/api/oauth.v2.access",
            "api_version": "v1"
        },
        "github": {
            "base_url": "https://api.github.com",
            "token_endpoint": "/login/oauth/access_token",
            "api_version": "2022-11-28"
        },
        "aws": {
            "base_url": "https://monitoring.us-east-1.amazonaws.com",
            "auth_method": "aws_signature_v4"
        },
        "datadog": {
            "base_url": "https://api.datadoghq.com",
            "api_version": "v1"
        }
    }

    def __init__(self):
        self.rate_limiters: Dict[str, RateLimiter] = {}
        self.oauth_tokens: Dict[str, Dict[str, Any]] = {}

    async def create_integration(
        self,
        db: AsyncSession,
        tenant_id: UUID,
        integration_type: str,
        credentials: Dict[str, str],
        endpoint: Optional[str] = None
    ) -> APIIntegration:
        """
        Create new API integration

        Args:
            db: Database session
            tenant_id: Tenant ID
            integration_type: Type of integration (salesforce, slack, etc.)
            credentials: API credentials (api_key, api_secret, etc.)
            endpoint: Custom API endpoint (optional)
        """
        if integration_type not in self.SUPPORTED_INTEGRATIONS:
            raise ValidationError(
                f"Unsupported integration type: {integration_type}. "
                f"Supported: {', '.join(self.SUPPORTED_INTEGRATIONS.keys())}"
            )

        # Encrypt credentials before storage
        encrypted_key = self._encrypt_credential(credentials.get("api_key", ""))
        encrypted_secret = self._encrypt_credential(credentials.get("api_secret", ""))

        config = self.SUPPORTED_INTEGRATIONS[integration_type]
        api_endpoint = endpoint or config["base_url"]

        integration = APIIntegration(
            tenant_id=tenant_id,
            integration_type=integration_type,
            api_key=encrypted_key,
            api_secret=encrypted_secret,
            api_endpoint=api_endpoint,
            is_active=True
        )

        db.add(integration)
        await db.commit()
        await db.refresh(integration)

        # Initialize rate limiter for this integration
        self.rate_limiters[str(integration.id)] = RateLimiter()

        return integration

    async def get_integration(
        self,
        db: AsyncSession,
        tenant_id: UUID,
        integration_id: UUID
    ) -> Optional[APIIntegration]:
        """Get integration by ID"""
        result = await db.execute(
            select(APIIntegration).where(
                APIIntegration.id == integration_id,
                APIIntegration.tenant_id == tenant_id
            )
        )
        return result.scalar_one_or_none()

    async def list_integrations(
        self,
        db: AsyncSession,
        tenant_id: UUID,
        integration_type: Optional[str] = None,
        is_active: Optional[bool] = None
    ) -> List[APIIntegration]:
        """List all integrations for tenant"""
        query = select(APIIntegration).where(
            APIIntegration.tenant_id == tenant_id
        )

        if integration_type:
            query = query.where(APIIntegration.integration_type == integration_type)

        if is_active is not None:
            query = query.where(APIIntegration.is_active == is_active)

        result = await db.execute(query)
        return result.scalars().all()

    async def delete_integration(
        self,
        db: AsyncSession,
        tenant_id: UUID,
        integration_id: UUID
    ) -> bool:
        """Delete integration"""
        integration = await self.get_integration(db, tenant_id, integration_id)

        if not integration:
            raise NotFoundError(f"Integration {integration_id} not found")

        await db.delete(integration)
        await db.commit()

        # Clean up rate limiter
        if str(integration_id) in self.rate_limiters:
            del self.rate_limiters[str(integration_id)]

        return True

    async def exchange_oauth_code(
        self,
        db: AsyncSession,
        integration_id: UUID,
        code: str,
        redirect_uri: str
    ) -> Dict[str, Any]:
        """
        Exchange OAuth authorization code for access token

        Args:
            db: Database session
            integration_id: Integration ID
            code: OAuth authorization code
            redirect_uri: Redirect URI used in authorization
        """
        integration = await db.get(APIIntegration, integration_id)

        if not integration:
            raise NotFoundError(f"Integration {integration_id} not found")

        config = self.SUPPORTED_INTEGRATIONS[integration.integration_type]
        token_url = config["base_url"] + config["token_endpoint"]

        # Decrypt credentials
        client_id = self._decrypt_credential(integration.api_key)
        client_secret = self._decrypt_credential(integration.api_secret)

        payload = {
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": redirect_uri,
            "client_id": client_id,
            "client_secret": client_secret
        }

        start_time = time.time()

        try:
            response = requests.post(token_url, data=payload, timeout=30)
            response_time = int((time.time() - start_time) * 1000)

            # Log API call
            await self._log_api_call(
                db,
                integration.tenant_id,
                integration_id,
                "POST",
                token_url,
                response.status_code,
                response_time
            )

            response.raise_for_status()
            token_data = response.json()

            # Cache token
            self.oauth_tokens[str(integration_id)] = {
                "access_token": token_data.get("access_token"),
                "refresh_token": token_data.get("refresh_token"),
                "expires_at": datetime.utcnow() + timedelta(
                    seconds=token_data.get("expires_in", 3600)
                )
            }

            return token_data

        except requests.exceptions.RequestException as e:
            raise ValidationError(f"OAuth exchange failed: {str(e)}")

    async def refresh_oauth_token(
        self,
        db: AsyncSession,
        integration_id: UUID
    ) -> Dict[str, Any]:
        """Refresh OAuth access token"""
        integration = await db.get(APIIntegration, integration_id)

        if not integration:
            raise NotFoundError(f"Integration {integration_id} not found")

        cached_token = self.oauth_tokens.get(str(integration_id))

        if not cached_token or not cached_token.get("refresh_token"):
            raise ValidationError("No refresh token available")

        config = self.SUPPORTED_INTEGRATIONS[integration.integration_type]
        token_url = config["base_url"] + config["token_endpoint"]

        client_id = self._decrypt_credential(integration.api_key)
        client_secret = self._decrypt_credential(integration.api_secret)

        payload = {
            "grant_type": "refresh_token",
            "refresh_token": cached_token["refresh_token"],
            "client_id": client_id,
            "client_secret": client_secret
        }

        start_time = time.time()

        try:
            response = requests.post(token_url, data=payload, timeout=30)
            response_time = int((time.time() - start_time) * 1000)

            await self._log_api_call(
                db,
                integration.tenant_id,
                integration_id,
                "POST",
                token_url,
                response.status_code,
                response_time
            )

            response.raise_for_status()
            token_data = response.json()

            # Update cached token
            self.oauth_tokens[str(integration_id)] = {
                "access_token": token_data.get("access_token"),
                "refresh_token": token_data.get("refresh_token", cached_token["refresh_token"]),
                "expires_at": datetime.utcnow() + timedelta(
                    seconds=token_data.get("expires_in", 3600)
                )
            }

            return token_data

        except requests.exceptions.RequestException as e:
            raise ValidationError(f"Token refresh failed: {str(e)}")

    async def make_api_call(
        self,
        db: AsyncSession,
        integration_id: UUID,
        method: str,
        endpoint: str,
        data: Optional[Dict] = None,
        params: Optional[Dict] = None,
        max_retries: int = 3
    ) -> Dict[str, Any]:
        """
        Make API call with retry logic and rate limiting

        Args:
            db: Database session
            integration_id: Integration ID
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint path
            data: Request body data
            params: Query parameters
            max_retries: Maximum retry attempts
        """
        integration = await db.get(APIIntegration, integration_id)

        if not integration:
            raise NotFoundError(f"Integration {integration_id} not found")

        if not integration.is_active:
            raise ValidationError("Integration is not active")

        # Check rate limit
        rate_limiter = self.rate_limiters.get(
            str(integration_id),
            RateLimiter()
        )

        if not await rate_limiter.acquire():
            raise ValidationError("Rate limit exceeded. Please try again later.")

        # Get or refresh access token
        token = await self._get_valid_token(db, integration_id)

        url = f"{integration.api_endpoint}{endpoint}"
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }

        # Add integration-specific headers
        if integration.integration_type == "github":
            headers["X-GitHub-Api-Version"] = "2022-11-28"

        retries = 0
        last_exception = None

        while retries < max_retries:
            start_time = time.time()

            try:
                async with aiohttp.ClientSession() as session:
                    async with session.request(
                        method,
                        url,
                        headers=headers,
                        json=data,
                        params=params,
                        timeout=aiohttp.ClientTimeout(total=30)
                    ) as response:
                        response_time = int((time.time() - start_time) * 1000)

                        # Log API call
                        await self._log_api_call(
                            db,
                            integration.tenant_id,
                            integration_id,
                            method,
                            url,
                            response.status,
                            response_time
                        )

                        if response.status == 429:  # Rate limited
                            retry_after = int(response.headers.get("Retry-After", 60))
                            await asyncio.sleep(retry_after)
                            retries += 1
                            continue

                        response.raise_for_status()
                        return await response.json()

            except aiohttp.ClientError as e:
                last_exception = e
                retries += 1

                if retries < max_retries:
                    # Exponential backoff
                    await asyncio.sleep(2 ** retries)

        raise ValidationError(
            f"API call failed after {max_retries} retries: {str(last_exception)}"
        )

    async def sync_salesforce_data(
        self,
        db: AsyncSession,
        integration_id: UUID,
        object_type: str = "Account"
    ) -> Dict[str, Any]:
        """Sync data from Salesforce"""
        endpoint = f"/services/data/v54.0/sobjects/{object_type}"

        return await self.make_api_call(
            db,
            integration_id,
            "GET",
            endpoint
        )

    async def send_slack_notification(
        self,
        db: AsyncSession,
        integration_id: UUID,
        channel: str,
        message: str
    ) -> Dict[str, Any]:
        """Send notification to Slack"""
        endpoint = "/api/chat.postMessage"

        data = {
            "channel": channel,
            "text": message
        }

        return await self.make_api_call(
            db,
            integration_id,
            "POST",
            endpoint,
            data=data
        )

    async def get_github_deployments(
        self,
        db: AsyncSession,
        integration_id: UUID,
        owner: str,
        repo: str
    ) -> Dict[str, Any]:
        """Get GitHub deployments"""
        endpoint = f"/repos/{owner}/{repo}/deployments"

        return await self.make_api_call(
            db,
            integration_id,
            "GET",
            endpoint
        )

    async def get_aws_metrics(
        self,
        db: AsyncSession,
        integration_id: UUID,
        namespace: str,
        metric_name: str,
        start_time: datetime,
        end_time: datetime
    ) -> Dict[str, Any]:
        """Get AWS CloudWatch metrics"""
        # Note: AWS requires signature v4, simplified for demo
        params = {
            "Namespace": namespace,
            "MetricName": metric_name,
            "StartTime": start_time.isoformat(),
            "EndTime": end_time.isoformat()
        }

        return await self.make_api_call(
            db,
            integration_id,
            "GET",
            "/",
            params=params
        )

    async def get_datadog_metrics(
        self,
        db: AsyncSession,
        integration_id: UUID,
        query: str,
        start: int,
        end: int
    ) -> Dict[str, Any]:
        """Get Datadog metrics"""
        endpoint = "/api/v1/query"

        params = {
            "query": query,
            "from": start,
            "to": end
        }

        return await self.make_api_call(
            db,
            integration_id,
            "GET",
            endpoint,
            params=params
        )

    def _encrypt_credential(self, credential: str) -> str:
        """Encrypt credential (simplified - use proper encryption in production)"""
        # In production, use Fernet or AWS KMS
        return hashlib.sha256(credential.encode()).hexdigest()

    def _decrypt_credential(self, encrypted: str) -> str:
        """Decrypt credential (simplified)"""
        # In production, use proper decryption
        return encrypted

    async def _get_valid_token(self, db: AsyncSession, integration_id: UUID) -> str:
        """Get valid access token, refresh if needed"""
        cached_token = self.oauth_tokens.get(str(integration_id))

        if not cached_token:
            # For non-OAuth integrations, use API key
            integration = await db.get(APIIntegration, integration_id)
            return self._decrypt_credential(integration.api_key)

        # Check if token is expired
        if datetime.utcnow() >= cached_token["expires_at"]:
            token_data = await self.refresh_oauth_token(db, integration_id)
            return token_data["access_token"]

        return cached_token["access_token"]

    async def _log_api_call(
        self,
        db: AsyncSession,
        tenant_id: UUID,
        integration_id: UUID,
        method: str,
        endpoint: str,
        status_code: int,
        response_time_ms: int
    ):
        """Log API call"""
        log = APILog(
            tenant_id=tenant_id,
            integration_id=integration_id,
            method=method,
            endpoint=endpoint,
            status_code=status_code,
            response_time_ms=response_time_ms
        )

        db.add(log)
        await db.commit()


# Singleton instance
integration_service = IntegrationService()
