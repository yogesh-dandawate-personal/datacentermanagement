"""
Real-Time WebSocket Routes
SPRINT 10 - AGENT 1: WebSocket Endpoints

Endpoints:
- WebSocket /api/v1/ws - Main WebSocket connection
- GET /api/v1/realtime/status - Connection status
- POST /api/v1/realtime/broadcast - Manual broadcast (admin)
"""
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, HTTPException, Header
from typing import Optional
import uuid
import json
import logging
from datetime import datetime

from app.services.realtime_service import (
    connection_manager,
    metric_streamer,
)
from app.auth.jwt_handler import verify_token
from app.auth.utils import extract_token_from_header

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1", tags=["realtime"])


async def get_current_user_from_ws(token: str):
    """
    Authenticate WebSocket connection from token

    Args:
        token: JWT token

    Returns:
        Token data with user_id and tenant_id

    Raises:
        ValueError: If authentication fails
    """
    try:
        token_data = verify_token(token)
        return {
            "user_id": token_data.sub,
            "tenant_id": token_data.tenant_id,
            "roles": token_data.roles,
        }
    except Exception as e:
        logger.error(f"WebSocket authentication failed: {str(e)}")
        raise ValueError("Authentication failed")


@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket, token: Optional[str] = None):
    """
    Main WebSocket endpoint for real-time metric streaming

    Connection flow:
    1. Client connects with JWT token as query parameter
    2. Server authenticates and accepts connection
    3. Client sends subscription messages
    4. Server streams metric updates to subscribed rooms
    5. Client can send heartbeat pings
    6. Connection closes on disconnect or error

    Message formats:

    Client -> Server:
    {
        "action": "subscribe",
        "room_id": "facility:uuid" | "org:uuid" | "metric:energy"
    }
    {
        "action": "unsubscribe",
        "room_id": "facility:uuid"
    }
    {
        "action": "ping"
    }

    Server -> Client:
    {
        "type": "connected",
        "connection_id": "uuid",
        "timestamp": "2024-03-11T12:00:00Z"
    }
    {
        "type": "metric_update",
        "metric_type": "energy",
        "facility_id": "uuid",
        "data": {...},
        "timestamp": "2024-03-11T12:00:00Z"
    }
    {
        "type": "threshold_breach",
        "severity": "critical",
        "data": {...},
        "timestamp": "2024-03-11T12:00:00Z"
    }
    """
    connection_id = str(uuid.uuid4())

    # Authenticate connection
    if not token:
        await websocket.close(code=1008, reason="Missing authentication token")
        return

    try:
        user_data = await get_current_user_from_ws(token)
        tenant_id = user_data["tenant_id"]
        user_id = user_data["user_id"]
    except ValueError as e:
        await websocket.close(code=1008, reason=str(e))
        return

    # Accept connection
    await connection_manager.connect(websocket, connection_id, tenant_id, user_id)

    try:
        while True:
            # Receive message from client
            data = await websocket.receive_text()

            try:
                message = json.loads(data)
                action = message.get("action")

                if action == "subscribe":
                    room_id = message.get("room_id")
                    if room_id:
                        # Validate room access (basic tenant isolation)
                        if room_id.startswith("tenant:") and not room_id.endswith(tenant_id):
                            await connection_manager.send_to_connection(connection_id, {
                                "type": "error",
                                "message": "Unauthorized room access",
                            })
                        else:
                            await connection_manager.subscribe_to_room(connection_id, room_id)

                elif action == "unsubscribe":
                    room_id = message.get("room_id")
                    if room_id:
                        await connection_manager.unsubscribe_from_room(connection_id, room_id)

                elif action == "ping":
                    await connection_manager.heartbeat(connection_id)
                    await connection_manager.send_to_connection(connection_id, {
                        "type": "pong",
                        "timestamp": datetime.utcnow().isoformat(),
                    })

                else:
                    await connection_manager.send_to_connection(connection_id, {
                        "type": "error",
                        "message": f"Unknown action: {action}",
                    })

            except json.JSONDecodeError:
                await connection_manager.send_to_connection(connection_id, {
                    "type": "error",
                    "message": "Invalid JSON message",
                })

    except WebSocketDisconnect:
        logger.info(f"WebSocket disconnected normally: {connection_id}")
        connection_manager.disconnect(connection_id)

    except Exception as e:
        logger.error(f"WebSocket error: {str(e)}")
        connection_manager.disconnect(connection_id)


@router.get("/realtime/status")
async def get_realtime_status(authorization: str = Header(None)):
    """
    Get real-time connection status and metrics

    Returns:
        Connection statistics and metrics

    Raises:
        HTTPException: If authentication fails
    """
    try:
        token = extract_token_from_header(authorization)
        token_data = verify_token(token)

        status = connection_manager.get_connection_status()

        return {
            "status": "ok",
            "data": status,
        }

    except Exception as e:
        logger.error(f"Error getting realtime status: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/realtime/broadcast")
async def manual_broadcast(
    room_id: str,
    message: dict,
    authorization: str = Header(None)
):
    """
    Manual broadcast to a room (admin only)

    Args:
        room_id: Target room
        message: Message to broadcast
        authorization: JWT token

    Returns:
        Broadcast confirmation

    Raises:
        HTTPException: If authentication fails or user is not admin
    """
    try:
        token = extract_token_from_header(authorization)
        token_data = verify_token(token)

        # Check admin role
        if "admin" not in token_data.roles:
            raise HTTPException(status_code=403, detail="Admin access required")

        # Add timestamp
        message["timestamp"] = datetime.utcnow().isoformat()
        message["type"] = message.get("type", "manual_broadcast")

        # Broadcast
        await connection_manager.broadcast_to_room(room_id, message)

        return {
            "status": "ok",
            "room_id": room_id,
            "message": "Broadcast sent successfully",
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error broadcasting: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/realtime/test-metric")
async def test_metric_stream(
    facility_id: str,
    org_id: str,
    metric_type: str = "energy",
    authorization: str = Header(None)
):
    """
    Test endpoint to stream a sample metric update

    Args:
        facility_id: Facility ID
        org_id: Organization ID
        metric_type: Metric type
        authorization: JWT token

    Returns:
        Test confirmation
    """
    try:
        token = extract_token_from_header(authorization)
        token_data = verify_token(token)
        tenant_id = token_data.tenant_id

        # Stream test metric
        await metric_streamer.stream_metric_update(
            metric_type=metric_type,
            facility_id=facility_id,
            org_id=org_id,
            tenant_id=tenant_id,
            metric_data={
                "value": 1234.56,
                "unit": "kWh",
                "status": "normal",
                "is_test": True,
            }
        )

        return {
            "status": "ok",
            "message": "Test metric streamed successfully",
        }

    except Exception as e:
        logger.error(f"Error streaming test metric: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
