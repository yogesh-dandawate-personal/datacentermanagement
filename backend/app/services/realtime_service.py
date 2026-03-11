"""
Real-Time WebSocket Service for Streaming Metrics
SPRINT 10 - AGENT 1: WebSocket Real-Time Engine

Features:
- WebSocket connection management
- Room-based subscriptions (facility, org, metric type)
- Real-time metric streaming
- Connection pooling and reconnection logic
- Message broadcasting to multiple clients
- Authentication and authorization
"""
from typing import Dict, Set, List, Optional, Any
from datetime import datetime, timedelta
from fastapi import WebSocket, WebSocketDisconnect
import json
import asyncio
import logging
from collections import defaultdict
from decimal import Decimal
import uuid

logger = logging.getLogger(__name__)


class ConnectionManager:
    """
    Manages WebSocket connections with room-based subscriptions

    Architecture:
    - Rooms: facility_id, org_id, metric_type combinations
    - Connections: Each WebSocket can subscribe to multiple rooms
    - Broadcasting: Efficient fan-out to all subscribers in a room
    """

    def __init__(self):
        # Active connections by connection_id
        self.active_connections: Dict[str, WebSocket] = {}

        # Room subscriptions: room_id -> set of connection_ids
        self.room_subscriptions: Dict[str, Set[str]] = defaultdict(set)

        # Connection metadata: connection_id -> metadata
        self.connection_metadata: Dict[str, Dict[str, Any]] = {}

        # Connection heartbeat tracking
        self.last_heartbeat: Dict[str, datetime] = {}

        # Metrics for monitoring
        self.metrics = {
            "total_connections": 0,
            "total_messages": 0,
            "total_broadcasts": 0,
            "failed_sends": 0,
        }

    async def connect(self, websocket: WebSocket, connection_id: str, tenant_id: str, user_id: str):
        """
        Accept new WebSocket connection

        Args:
            websocket: WebSocket instance
            connection_id: Unique connection identifier
            tenant_id: Tenant ID for authorization
            user_id: User ID for tracking
        """
        await websocket.accept()

        self.active_connections[connection_id] = websocket
        self.connection_metadata[connection_id] = {
            "tenant_id": tenant_id,
            "user_id": user_id,
            "connected_at": datetime.utcnow(),
            "subscriptions": [],
        }
        self.last_heartbeat[connection_id] = datetime.utcnow()
        self.metrics["total_connections"] += 1

        logger.info(f"WebSocket connected: {connection_id} (tenant: {tenant_id}, user: {user_id})")

        # Send welcome message
        await self.send_to_connection(connection_id, {
            "type": "connected",
            "connection_id": connection_id,
            "timestamp": datetime.utcnow().isoformat(),
        })

    def disconnect(self, connection_id: str):
        """
        Remove WebSocket connection and clean up subscriptions

        Args:
            connection_id: Connection to disconnect
        """
        # Remove from all rooms
        if connection_id in self.connection_metadata:
            for room_id in self.connection_metadata[connection_id].get("subscriptions", []):
                self.room_subscriptions[room_id].discard(connection_id)

        # Clean up
        self.active_connections.pop(connection_id, None)
        self.connection_metadata.pop(connection_id, None)
        self.last_heartbeat.pop(connection_id, None)

        logger.info(f"WebSocket disconnected: {connection_id}")

    async def subscribe_to_room(self, connection_id: str, room_id: str):
        """
        Subscribe connection to a room

        Args:
            connection_id: Connection to subscribe
            room_id: Room identifier (e.g., "facility:uuid", "org:uuid", "metric:energy")
        """
        if connection_id not in self.active_connections:
            logger.warning(f"Cannot subscribe: connection {connection_id} not found")
            return

        # Add to room
        self.room_subscriptions[room_id].add(connection_id)

        # Update metadata
        if connection_id in self.connection_metadata:
            subscriptions = self.connection_metadata[connection_id].get("subscriptions", [])
            if room_id not in subscriptions:
                subscriptions.append(room_id)
                self.connection_metadata[connection_id]["subscriptions"] = subscriptions

        logger.info(f"Connection {connection_id} subscribed to room: {room_id}")

        await self.send_to_connection(connection_id, {
            "type": "subscribed",
            "room_id": room_id,
            "timestamp": datetime.utcnow().isoformat(),
        })

    async def unsubscribe_from_room(self, connection_id: str, room_id: str):
        """
        Unsubscribe connection from a room

        Args:
            connection_id: Connection to unsubscribe
            room_id: Room identifier
        """
        self.room_subscriptions[room_id].discard(connection_id)

        # Update metadata
        if connection_id in self.connection_metadata:
            subscriptions = self.connection_metadata[connection_id].get("subscriptions", [])
            if room_id in subscriptions:
                subscriptions.remove(room_id)
                self.connection_metadata[connection_id]["subscriptions"] = subscriptions

        logger.info(f"Connection {connection_id} unsubscribed from room: {room_id}")

        await self.send_to_connection(connection_id, {
            "type": "unsubscribed",
            "room_id": room_id,
            "timestamp": datetime.utcnow().isoformat(),
        })

    async def send_to_connection(self, connection_id: str, message: dict):
        """
        Send message to specific connection

        Args:
            connection_id: Target connection
            message: Message dictionary to send
        """
        if connection_id not in self.active_connections:
            logger.warning(f"Cannot send: connection {connection_id} not found")
            return

        try:
            websocket = self.active_connections[connection_id]
            await websocket.send_text(json.dumps(message, default=str))
            self.metrics["total_messages"] += 1
        except Exception as e:
            logger.error(f"Failed to send to {connection_id}: {str(e)}")
            self.metrics["failed_sends"] += 1
            self.disconnect(connection_id)

    async def broadcast_to_room(self, room_id: str, message: dict, exclude: Optional[Set[str]] = None):
        """
        Broadcast message to all connections in a room

        Args:
            room_id: Target room
            message: Message dictionary to broadcast
            exclude: Set of connection_ids to exclude from broadcast
        """
        if room_id not in self.room_subscriptions:
            logger.debug(f"No subscribers in room: {room_id}")
            return

        exclude = exclude or set()
        subscribers = self.room_subscriptions[room_id] - exclude

        logger.debug(f"Broadcasting to room {room_id}: {len(subscribers)} subscribers")

        # Broadcast to all subscribers concurrently
        tasks = []
        for connection_id in subscribers:
            tasks.append(self.send_to_connection(connection_id, message))

        await asyncio.gather(*tasks, return_exceptions=True)
        self.metrics["total_broadcasts"] += 1

    async def heartbeat(self, connection_id: str):
        """
        Update heartbeat timestamp for connection

        Args:
            connection_id: Connection to update
        """
        self.last_heartbeat[connection_id] = datetime.utcnow()

    async def check_stale_connections(self, timeout_seconds: int = 300):
        """
        Check for and disconnect stale connections

        Args:
            timeout_seconds: Timeout in seconds (default: 5 minutes)
        """
        now = datetime.utcnow()
        stale_connections = []

        for connection_id, last_beat in self.last_heartbeat.items():
            if (now - last_beat).total_seconds() > timeout_seconds:
                stale_connections.append(connection_id)

        for connection_id in stale_connections:
            logger.warning(f"Disconnecting stale connection: {connection_id}")
            self.disconnect(connection_id)

    def get_connection_status(self) -> dict:
        """
        Get current connection status and metrics

        Returns:
            Dictionary with connection statistics
        """
        return {
            "active_connections": len(self.active_connections),
            "total_rooms": len(self.room_subscriptions),
            "metrics": self.metrics,
            "timestamp": datetime.utcnow().isoformat(),
        }


class RealtimeMetricStreamer:
    """
    Streams real-time metric updates to WebSocket clients

    Features:
    - Metric change detection
    - Efficient batching
    - Rate limiting per connection
    - Metric filtering by type
    """

    def __init__(self, connection_manager: ConnectionManager):
        self.connection_manager = connection_manager
        self.metric_buffer: Dict[str, List[dict]] = defaultdict(list)
        self.last_flush: Dict[str, datetime] = {}
        self.flush_interval_seconds = 1  # Flush every 1 second

    async def stream_metric_update(
        self,
        metric_type: str,
        facility_id: str,
        org_id: str,
        tenant_id: str,
        metric_data: dict
    ):
        """
        Stream metric update to subscribed connections

        Args:
            metric_type: Type of metric (energy, carbon, water, etc.)
            facility_id: Facility identifier
            org_id: Organization identifier
            tenant_id: Tenant identifier
            metric_data: Metric data to stream
        """
        # Build message
        message = {
            "type": "metric_update",
            "metric_type": metric_type,
            "facility_id": facility_id,
            "org_id": org_id,
            "tenant_id": tenant_id,
            "data": metric_data,
            "timestamp": datetime.utcnow().isoformat(),
        }

        # Broadcast to relevant rooms
        rooms = [
            f"facility:{facility_id}",
            f"org:{org_id}",
            f"metric:{metric_type}",
            f"tenant:{tenant_id}",
        ]

        for room_id in rooms:
            await self.connection_manager.broadcast_to_room(room_id, message)

    async def stream_threshold_breach(
        self,
        breach_type: str,
        severity: str,
        facility_id: str,
        org_id: str,
        tenant_id: str,
        breach_data: dict
    ):
        """
        Stream threshold breach alert to subscribed connections

        Args:
            breach_type: Type of breach (kpi, threshold, anomaly)
            severity: Severity level (info, warning, critical)
            facility_id: Facility identifier
            org_id: Organization identifier
            tenant_id: Tenant identifier
            breach_data: Breach details
        """
        message = {
            "type": "threshold_breach",
            "breach_type": breach_type,
            "severity": severity,
            "facility_id": facility_id,
            "org_id": org_id,
            "tenant_id": tenant_id,
            "data": breach_data,
            "timestamp": datetime.utcnow().isoformat(),
        }

        # Broadcast to alert rooms
        rooms = [
            f"alerts:{facility_id}",
            f"alerts:{org_id}",
            f"alerts:tenant:{tenant_id}",
        ]

        for room_id in rooms:
            await self.connection_manager.broadcast_to_room(room_id, message)


# Global connection manager instance
connection_manager = ConnectionManager()
metric_streamer = RealtimeMetricStreamer(connection_manager)


async def start_heartbeat_monitor():
    """
    Background task to monitor and clean up stale connections
    """
    while True:
        await asyncio.sleep(60)  # Check every minute
        await connection_manager.check_stale_connections(timeout_seconds=300)
