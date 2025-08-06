"""
Notification Service for Legal Dashboard
======================================

Provides real-time notifications, email alerts, and WebSocket communication for system events.
"""

import os
import json
import logging
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from enum import Enum
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from fastapi import WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
import sqlite3
from contextlib import contextmanager

logger = logging.getLogger(__name__)


class NotificationType(Enum):
    """Notification types"""
    INFO = "info"
    SUCCESS = "success"
    WARNING = "warning"
    ERROR = "error"
    UPLOAD_COMPLETE = "upload_complete"
    OCR_COMPLETE = "ocr_complete"
    SCRAPING_COMPLETE = "scraping_complete"
    SYSTEM_ERROR = "system_error"
    USER_ACTIVITY = "user_activity"


class NotificationPriority(Enum):
    """Notification priorities"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class NotificationService:
    """Comprehensive notification service"""

    def __init__(self):
        self.email_enabled = os.getenv(
            "EMAIL_ENABLED", "false").lower() == "true"
        self.smtp_server = os.getenv("SMTP_SERVER", "smtp.gmail.com")
        self.smtp_port = int(os.getenv("SMTP_PORT", "587"))
        self.smtp_username = os.getenv("SMTP_USERNAME")
        self.smtp_password = os.getenv("SMTP_PASSWORD")
        self.from_email = os.getenv(
            "FROM_EMAIL", "noreply@legal-dashboard.com")

        # WebSocket connections
        self.active_connections: Dict[int, List[WebSocket]] = {}

        # Initialize database
        self._init_notification_tables()

    def _init_notification_tables(self):
        """Initialize notification database tables"""
        with self._get_db_connection() as conn:
            cursor = conn.cursor()

            # Notifications table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS notifications (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    type TEXT NOT NULL,
                    title TEXT NOT NULL,
                    message TEXT NOT NULL,
                    priority TEXT NOT NULL DEFAULT 'medium',
                    read BOOLEAN NOT NULL DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    expires_at TIMESTAMP,
                    metadata TEXT,
                    FOREIGN KEY (user_id) REFERENCES users (id)
                )
            """)

            # Notification settings table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS notification_settings (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER UNIQUE NOT NULL,
                    email_enabled BOOLEAN NOT NULL DEFAULT 1,
                    push_enabled BOOLEAN NOT NULL DEFAULT 1,
                    notification_types TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (id)
                )
            """)

            conn.commit()

    @contextmanager
    def _get_db_connection(self):
        """Get database connection"""
        db_path = os.getenv("DATABASE_PATH", "legal_documents.db")
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
        finally:
            conn.close()

    async def create_notification(
        self,
        user_id: Optional[int],
        notification_type: NotificationType,
        title: str,
        message: str,
        priority: NotificationPriority = NotificationPriority.MEDIUM,
        metadata: Optional[Dict[str, Any]] = None,
        expires_in_hours: int = 24
    ) -> bool:
        """Create a new notification"""
        try:
            expires_at = datetime.utcnow() + timedelta(hours=expires_in_hours)

            with self._get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO notifications (user_id, type, title, message, priority, expires_at, metadata)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    user_id,
                    notification_type.value,
                    title,
                    message,
                    priority.value,
                    expires_at.isoformat(),
                    json.dumps(metadata) if metadata else None
                ))
                notification_id = cursor.lastrowid
                conn.commit()

            # Send real-time notification
            await self._send_realtime_notification(user_id, {
                'id': notification_id,
                'type': notification_type.value,
                'title': title,
                'message': message,
                'priority': priority.value,
                'created_at': datetime.utcnow().isoformat(),
                'metadata': metadata
            })

            # Send email notification if enabled
            if self.email_enabled and user_id:
                await self._send_email_notification(user_id, title, message, notification_type)

            logger.info(f"Notification created: {title} for user {user_id}")
            return True

        except Exception as e:
            logger.error(f"Error creating notification: {e}")
            return False

    async def _send_realtime_notification(self, user_id: Optional[int], notification_data: Dict[str, Any]):
        """Send real-time notification via WebSocket"""
        try:
            if user_id and user_id in self.active_connections:
                for connection in self.active_connections[user_id]:
                    try:
                        await connection.send_text(json.dumps(notification_data))
                    except WebSocketDisconnect:
                        # Remove disconnected connection
                        self.active_connections[user_id].remove(connection)
                    except Exception as e:
                        logger.error(
                            f"Error sending WebSocket notification: {e}")

            # Also send to admin connections
            if None in self.active_connections:
                for connection in self.active_connections[None]:
                    try:
                        await connection.send_text(json.dumps(notification_data))
                    except WebSocketDisconnect:
                        self.active_connections[None].remove(connection)
                    except Exception as e:
                        logger.error(
                            f"Error sending admin WebSocket notification: {e}")

        except Exception as e:
            logger.error(f"Error in real-time notification: {e}")

    async def _send_email_notification(self, user_id: int, title: str, message: str, notification_type: NotificationType):
        """Send email notification"""
        try:
            # Get user email
            with self._get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT email FROM users WHERE id = ?", (user_id,))
                user = cursor.fetchone()
                if not user:
                    return

                user_email = user['email']

            # Check if user has email notifications enabled
            cursor.execute("""
                SELECT email_enabled FROM notification_settings 
                WHERE user_id = ? AND email_enabled = 1
            """, (user_id,))
            if not cursor.fetchone():
                return

            # Create email message
            msg = MIMEMultipart()
            msg['From'] = self.from_email
            msg['To'] = user_email
            msg['Subject'] = f"Legal Dashboard: {title}"

            # Create HTML body
            html_body = f"""
            <html>
            <body>
                <h2>{title}</h2>
                <p>{message}</p>
                <p><strong>Type:</strong> {notification_type.value}</p>
                <p><strong>Time:</strong> {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')}</p>
                <hr>
                <p><small>This is an automated notification from Legal Dashboard.</small></p>
            </body>
            </html>
            """

            msg.attach(MIMEText(html_body, 'html'))

            # Send email
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_username, self.smtp_password)
                server.send_message(msg)

            logger.info(f"Email notification sent to {user_email}")

        except Exception as e:
            logger.error(f"Error sending email notification: {e}")

    async def connect_websocket(self, websocket: WebSocket, user_id: Optional[int] = None):
        """Connect a WebSocket for real-time notifications"""
        await websocket.accept()

        if user_id not in self.active_connections:
            self.active_connections[user_id] = []

        self.active_connections[user_id].append(websocket)

        try:
            # Send connection confirmation
            await websocket.send_text(json.dumps({
                'type': 'connection_established',
                'message': 'Connected to notification service',
                'user_id': user_id
            }))

            # Keep connection alive
            while True:
                data = await websocket.receive_text()
                # Handle any client messages if needed

        except WebSocketDisconnect:
            if user_id in self.active_connections:
                self.active_connections[user_id].remove(websocket)
                if not self.active_connections[user_id]:
                    del self.active_connections[user_id]
        except Exception as e:
            logger.error(f"WebSocket error: {e}")

    def get_user_notifications(self, user_id: int, limit: int = 50, unread_only: bool = False) -> List[Dict[str, Any]]:
        """Get notifications for a user"""
        try:
            with self._get_db_connection() as conn:
                cursor = conn.cursor()

                query = """
                    SELECT * FROM notifications 
                    WHERE (user_id = ? OR user_id IS NULL)
                    AND (expires_at IS NULL OR expires_at > ?)
                """
                params = [user_id, datetime.utcnow().isoformat()]

                if unread_only:
                    query += " AND read = 0"

                query += " ORDER BY created_at DESC LIMIT ?"
                params.append(limit)

                cursor.execute(query, params)
                notifications = [dict(row) for row in cursor.fetchall()]

                # Parse metadata
                for notification in notifications:
                    if notification.get('metadata'):
                        try:
                            notification['metadata'] = json.loads(
                                notification['metadata'])
                        except:
                            notification['metadata'] = {}

                return notifications

        except Exception as e:
            logger.error(f"Error getting user notifications: {e}")
            return []

    def mark_notification_read(self, notification_id: int, user_id: int) -> bool:
        """Mark a notification as read"""
        try:
            with self._get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    UPDATE notifications 
                    SET read = 1 
                    WHERE id = ? AND user_id = ?
                """, (notification_id, user_id))
                conn.commit()
                return cursor.rowcount > 0
        except Exception as e:
            logger.error(f"Error marking notification read: {e}")
            return False

    def mark_all_notifications_read(self, user_id: int) -> bool:
        """Mark all notifications as read for a user"""
        try:
            with self._get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    UPDATE notifications 
                    SET read = 1 
                    WHERE user_id = ?
                """, (user_id,))
                conn.commit()
                return True
        except Exception as e:
            logger.error(f"Error marking all notifications read: {e}")
            return False

    def delete_notification(self, notification_id: int, user_id: int) -> bool:
        """Delete a notification"""
        try:
            with self._get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    DELETE FROM notifications 
                    WHERE id = ? AND user_id = ?
                """, (notification_id, user_id))
                conn.commit()
                return cursor.rowcount > 0
        except Exception as e:
            logger.error(f"Error deleting notification: {e}")
            return False

    def get_notification_stats(self, user_id: int) -> Dict[str, Any]:
        """Get notification statistics for a user"""
        try:
            with self._get_db_connection() as conn:
                cursor = conn.cursor()

                # Total notifications
                cursor.execute("""
                    SELECT COUNT(*) FROM notifications 
                    WHERE user_id = ? AND (expires_at IS NULL OR expires_at > ?)
                """, (user_id, datetime.utcnow().isoformat()))
                total = cursor.fetchone()[0]

                # Unread notifications
                cursor.execute("""
                    SELECT COUNT(*) FROM notifications 
                    WHERE user_id = ? AND read = 0 AND (expires_at IS NULL OR expires_at > ?)
                """, (user_id, datetime.utcnow().isoformat()))
                unread = cursor.fetchone()[0]

                # Notifications by type
                cursor.execute("""
                    SELECT type, COUNT(*) FROM notifications 
                    WHERE user_id = ? AND (expires_at IS NULL OR expires_at > ?)
                    GROUP BY type
                """, (user_id, datetime.utcnow().isoformat()))
                by_type = dict(cursor.fetchall())

                return {
                    'total': total,
                    'unread': unread,
                    'read': total - unread,
                    'by_type': by_type
                }

        except Exception as e:
            logger.error(f"Error getting notification stats: {e}")
            return {'total': 0, 'unread': 0, 'read': 0, 'by_type': {}}

    def update_notification_settings(self, user_id: int, settings: Dict[str, Any]) -> bool:
        """Update user notification settings"""
        try:
            with self._get_db_connection() as conn:
                cursor = conn.cursor()

                # Check if settings exist
                cursor.execute(
                    "SELECT id FROM notification_settings WHERE user_id = ?", (user_id,))
                exists = cursor.fetchone()

                if exists:
                    cursor.execute("""
                        UPDATE notification_settings 
                        SET email_enabled = ?, push_enabled = ?, notification_types = ?, updated_at = ?
                        WHERE user_id = ?
                    """, (
                        settings.get('email_enabled', True),
                        settings.get('push_enabled', True),
                        json.dumps(settings.get('notification_types', [])),
                        datetime.utcnow().isoformat(),
                        user_id
                    ))
                else:
                    cursor.execute("""
                        INSERT INTO notification_settings (user_id, email_enabled, push_enabled, notification_types)
                        VALUES (?, ?, ?, ?)
                    """, (
                        user_id,
                        settings.get('email_enabled', True),
                        settings.get('push_enabled', True),
                        json.dumps(settings.get('notification_types', []))
                    ))

                conn.commit()
                return True

        except Exception as e:
            logger.error(f"Error updating notification settings: {e}")
            return False

    def get_notification_settings(self, user_id: int) -> Dict[str, Any]:
        """Get user notification settings"""
        try:
            with self._get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT * FROM notification_settings WHERE user_id = ?", (user_id,))
                settings = cursor.fetchone()

                if settings:
                    return {
                        'email_enabled': bool(settings['email_enabled']),
                        'push_enabled': bool(settings['push_enabled']),
                        'notification_types': json.loads(settings['notification_types']) if settings['notification_types'] else [],
                        'updated_at': settings['updated_at']
                    }
                else:
                    return {
                        'email_enabled': True,
                        'push_enabled': True,
                        'notification_types': [],
                        'updated_at': None
                    }

        except Exception as e:
            logger.error(f"Error getting notification settings: {e}")
            return {
                'email_enabled': True,
                'push_enabled': True,
                'notification_types': [],
                'updated_at': None
            }

    def cleanup_expired_notifications(self) -> int:
        """Clean up expired notifications"""
        try:
            with self._get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    DELETE FROM notifications 
                    WHERE expires_at IS NOT NULL AND expires_at < ?
                """, (datetime.utcnow().isoformat(),))
                deleted_count = cursor.rowcount
                conn.commit()
                return deleted_count
        except Exception as e:
            logger.error(f"Error cleaning up expired notifications: {e}")
            return 0


# Global notification service instance
notification_service = NotificationService()
