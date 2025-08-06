"""
WebSocket API for Real-time Updates
==================================

FastAPI WebSocket endpoint for real-time dashboard updates,
notifications, and live data synchronization.
"""

import json
import logging
import asyncio
from datetime import datetime, timezone
from typing import Dict, List, Set, Any
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from fastapi.websockets import WebSocketState
from pydantic import BaseModel
import uuid

logger = logging.getLogger(__name__)

router = APIRouter()

# WebSocket connection manager


class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
        # user_id -> connection_ids
        self.user_connections: Dict[str, Set[str]] = {}
        self.connection_metadata: Dict[str, Dict[str, Any]] = {}

    async def connect(self, websocket: WebSocket, client_id: str = None) -> str:
        """Accept WebSocket connection and assign unique ID"""
        await websocket.accept()

        connection_id = client_id or str(uuid.uuid4())
        self.active_connections[connection_id] = websocket

        # Store connection metadata
        self.connection_metadata[connection_id] = {
            'connected_at': datetime.now(timezone.utc),
            'last_heartbeat': datetime.now(timezone.utc),
            'user_agent': websocket.headers.get('user-agent', ''),
            'ip_address': websocket.client.host if websocket.client else 'unknown'
        }

        logger.info(f"🔌 WebSocket client connected: {connection_id}")

        # Notify other clients about new connection
        await self.broadcast_user_activity({
            'type': 'user_activity',
            'action': 'connected',
            'connection_id': connection_id,
            'online_users': len(self.active_connections),
            'timestamp': datetime.now(timezone.utc).isoformat()
        }, exclude_connection=connection_id)

        return connection_id

    def disconnect(self, connection_id: str):
        """Remove WebSocket connection"""
        if connection_id in self.active_connections:
            del self.active_connections[connection_id]

        if connection_id in self.connection_metadata:
            del self.connection_metadata[connection_id]

        logger.info(f"🔌 WebSocket client disconnected: {connection_id}")

    async def send_personal_message(self, message: dict, connection_id: str):
        """Send message to specific connection"""
        if connection_id in self.active_connections:
            websocket = self.active_connections[connection_id]
            try:
                if websocket.application_state == WebSocketState.CONNECTED:
                    await websocket.send_text(json.dumps(message))
                    return True
            except Exception as e:
                logger.error(f"Error sending message to {connection_id}: {e}")
                self.disconnect(connection_id)
        return False

    async def broadcast(self, message: dict, exclude_connection: str = None):
        """Broadcast message to all connected clients"""
        if not self.active_connections:
            return

        disconnected = []

        for connection_id, websocket in self.active_connections.items():
            if connection_id == exclude_connection:
                continue

            try:
                if websocket.application_state == WebSocketState.CONNECTED:
                    await websocket.send_text(json.dumps(message))
                else:
                    disconnected.append(connection_id)
            except Exception as e:
                logger.error(f"Error broadcasting to {connection_id}: {e}")
                disconnected.append(connection_id)

        # Clean up disconnected clients
        for connection_id in disconnected:
            self.disconnect(connection_id)

    async def broadcast_user_activity(self, message: dict, exclude_connection: str = None):
        """Broadcast user activity updates"""
        message.update({
            'online_users': len(self.active_connections),
            'timestamp': datetime.now(timezone.utc).isoformat()
        })
        await self.broadcast(message, exclude_connection)

    def get_connection_stats(self) -> Dict[str, Any]:
        """Get connection statistics"""
        return {
            'total_connections': len(self.active_connections),
            'connections': [
                {
                    'id': conn_id,
                    'connected_at': metadata['connected_at'].isoformat(),
                    'last_heartbeat': metadata['last_heartbeat'].isoformat(),
                    'user_agent': metadata['user_agent']
                }
                for conn_id, metadata in self.connection_metadata.items()
            ]
        }


# Global connection manager
manager = ConnectionManager()

# Message models


class WebSocketMessage(BaseModel):
    type: str
    data: Dict[str, Any] = {}
    timestamp: str = None

    def __init__(self, **data):
        if 'timestamp' not in data:
            data['timestamp'] = datetime.now(timezone.utc).isoformat()
        super().__init__(**data)

# WebSocket endpoint


@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """Main WebSocket endpoint for real-time communication"""
    connection_id = None

    try:
        connection_id = await manager.connect(websocket)

        # Send welcome message
        welcome_message = WebSocketMessage(
            type="connected",
            data={
                "connection_id": connection_id,
                "message": "اتصال WebSocket برقرار شد",
                "server_time": datetime.now(timezone.utc).isoformat()
            }
        )
        await websocket.send_text(welcome_message.json())

        # Start listening for messages
        while True:
            try:
                # Receive message from client
                data = await websocket.receive_text()
                message = json.loads(data)

                # Handle different message types
                await handle_client_message(websocket, connection_id, message)

            except WebSocketDisconnect:
                logger.info(f"Client {connection_id} disconnected normally")
                break
            except Exception as e:
                logger.error(
                    f"Error handling message from {connection_id}: {e}")
                # Send error message to client
                error_message = WebSocketMessage(
                    type="error",
                    data={
                        "message": "خطا در پردازش پیام",
                        "error": str(e)
                    }
                )
                await websocket.send_text(error_message.json())

    except WebSocketDisconnect:
        logger.info(f"Client {connection_id} disconnected")
    except Exception as e:
        logger.error(f"WebSocket error for {connection_id}: {e}")
    finally:
        if connection_id:
            manager.disconnect(connection_id)

            # Notify remaining clients
            await manager.broadcast_user_activity({
                'type': 'user_activity',
                'action': 'disconnected',
                'connection_id': connection_id
            })


async def handle_client_message(websocket: WebSocket, connection_id: str, message: dict):
    """Handle incoming messages from clients"""
    message_type = message.get('type', 'unknown')

    try:
        if message_type == 'heartbeat':
            await handle_heartbeat(websocket, connection_id, message)
        elif message_type == 'subscribe':
            await handle_subscription(websocket, connection_id, message)
        elif message_type == 'unsubscribe':
            await handle_unsubscription(websocket, connection_id, message)
        elif message_type == 'ping':
            await handle_ping(websocket, connection_id, message)
        else:
            logger.warning(
                f"Unknown message type from {connection_id}: {message_type}")

    except Exception as e:
        logger.error(
            f"Error handling {message_type} from {connection_id}: {e}")


async def handle_heartbeat(websocket: WebSocket, connection_id: str, message: dict):
    """Handle heartbeat messages"""
    # Update last heartbeat time
    if connection_id in manager.connection_metadata:
        manager.connection_metadata[connection_id]['last_heartbeat'] = datetime.now(
            timezone.utc)

    # Send heartbeat response
    response = WebSocketMessage(
        type="heartbeat",
        data={
            "status": "alive",
            "server_time": datetime.now(timezone.utc).isoformat()
        }
    )
    await websocket.send_text(response.json())


async def handle_subscription(websocket: WebSocket, connection_id: str, message: dict):
    """Handle subscription requests"""
    channels = message.get('data', {}).get('channels', [])

    # Store subscription info in metadata
    if connection_id in manager.connection_metadata:
        manager.connection_metadata[connection_id]['subscriptions'] = channels

    logger.info(f"Client {connection_id} subscribed to: {channels}")

    # Send subscription confirmation
    response = WebSocketMessage(
        type="subscribed",
        data={
            "channels": channels,
            "message": f"اشتراک در {len(channels)} کانال فعال شد"
        }
    )
    await websocket.send_text(response.json())


async def handle_unsubscription(websocket: WebSocket, connection_id: str, message: dict):
    """Handle unsubscription requests"""
    channels = message.get('data', {}).get('channels', [])

    # Remove subscription info from metadata
    if connection_id in manager.connection_metadata:
        current_subs = manager.connection_metadata[connection_id].get(
            'subscriptions', [])
        new_subs = [ch for ch in current_subs if ch not in channels]
        manager.connection_metadata[connection_id]['subscriptions'] = new_subs

    logger.info(f"Client {connection_id} unsubscribed from: {channels}")

    # Send unsubscription confirmation
    response = WebSocketMessage(
        type="unsubscribed",
        data={
            "channels": channels,
            "message": f"اشتراک از {len(channels)} کانال لغو شد"
        }
    )
    await websocket.send_text(response.json())


async def handle_ping(websocket: WebSocket, connection_id: str, message: dict):
    """Handle ping messages"""
    response = WebSocketMessage(
        type="pong",
        data={
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "latency_ms": 0  # Calculate actual latency if needed
        }
    )
    await websocket.send_text(response.json())

# Utility functions for broadcasting specific events


async def broadcast_document_update(document_data: dict):
    """Broadcast document upload/update events"""
    message = WebSocketMessage(
        type="document_uploaded",
        data={
            "document_id": document_data.get('id'),
            "filename": document_data.get('filename'),
            "status": document_data.get('status', 'uploaded'),
            "file_size": document_data.get('file_size'),
            "message": f"فایل {document_data.get('filename')} آپلود شد"
        }
    )
    await manager.broadcast(message.dict())


async def broadcast_document_processed(document_data: dict):
    """Broadcast document processing completion"""
    message = WebSocketMessage(
        type="document_processed",
        data={
            "document_id": document_data.get('id'),
            "filename": document_data.get('filename'),
            "ocr_text": document_data.get('ocr_text', ''),
            "quality_score": document_data.get('quality_score', 0),
            "processing_time": document_data.get('processing_time', 0),
            "message": f"پردازش {document_data.get('filename')} تکمیل شد"
        }
    )
    await manager.broadcast(message.dict())


async def broadcast_scraping_update(job_data: dict):
    """Broadcast scraping job updates"""
    message = WebSocketMessage(
        type="scraping_update",
        data={
            "job_id": job_data.get('job_id'),
            "status": job_data.get('status'),
            "progress": job_data.get('progress', 0),
            "total_items": job_data.get('total_items', 0),
            "completed_items": job_data.get('completed_items', 0),
            "failed_items": job_data.get('failed_items', 0),
            "message": f"وضعیت scraping: {job_data.get('status')}"
        }
    )
    await manager.broadcast(message.dict())


async def broadcast_system_health(health_data: dict):
    """Broadcast system health updates"""
    message = WebSocketMessage(
        type="system_health",
        data={
            "status": health_data.get('status'),
            "services": health_data.get('services', {}),
            "metrics": health_data.get('metrics', {}),
            "message": f"وضعیت سیستم: {health_data.get('status')}"
        }
    )
    await manager.broadcast(message.dict())


async def broadcast_analytics_update(analytics_data: dict):
    """Broadcast analytics updates"""
    message = WebSocketMessage(
        type="analytics_update",
        data={
            "metrics": analytics_data,
            "message": "آمار سیستم به‌روزرسانی شد"
        }
    )
    await manager.broadcast(message.dict())


async def broadcast_notification(notification_data: dict):
    """Broadcast general notifications"""
    message = WebSocketMessage(
        type="notification",
        data={
            "message": notification_data.get('message'),
            "type": notification_data.get('type', 'info'),
            "duration": notification_data.get('duration', 3000),
            "title": notification_data.get('title', 'اعلان')
        }
    )
    await manager.broadcast(message.dict())

# Health endpoint for WebSocket connections


@router.get("/ws/stats")
async def get_websocket_stats():
    """Get WebSocket connection statistics"""
    return {
        "status": "healthy",
        "stats": manager.get_connection_stats(),
        "timestamp": datetime.now(timezone.utc).isoformat()
    }

# Export manager for use in other modules
__all__ = [
    'manager',
    'broadcast_document_update',
    'broadcast_document_processed',
    'broadcast_scraping_update',
    'broadcast_system_health',
    'broadcast_analytics_update',
    'broadcast_notification'
]
