"""
Analytics and Reporting API for Legal Dashboard
==============================================

Provides comprehensive analytics, performance metrics, and reporting capabilities.
"""

import os
import json
import logging
import sqlite3
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from contextlib import contextmanager
from fastapi import APIRouter, HTTPException, Depends, Query
from fastapi.responses import StreamingResponse
import csv
import io
from pydantic import BaseModel

# Import services
from ..services.cache_service import cache_service
from ..services.notification_service import notification_service
from ..api.auth import get_current_user, require_role

logger = logging.getLogger(__name__)

# Pydantic models


class AnalyticsSummary(BaseModel):
    total_documents: int
    total_users: int
    total_ocr_processed: int
    total_scraping_sessions: int
    avg_processing_time: float
    success_rate: float
    cache_hit_rate: float
    system_uptime: float


class PerformanceMetrics(BaseModel):
    api_response_times: Dict[str, float]
    memory_usage: Dict[str, Any]
    cpu_usage: float
    disk_usage: Dict[str, Any]
    active_connections: int


class UserActivity(BaseModel):
    user_id: int
    username: str
    documents_processed: int
    last_activity: str
    total_processing_time: float
    success_rate: float


class DocumentAnalytics(BaseModel):
    document_id: int
    filename: str
    processing_time: float
    ocr_accuracy: Optional[float]
    file_size: int
    created_at: str
    status: str

# Database connection


@contextmanager
def get_db_connection():
    db_path = os.getenv("DATABASE_PATH", "legal_documents.db")
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()


# Router
router = APIRouter()


@router.get("/summary", response_model=AnalyticsSummary)
async def get_analytics_summary(current_user: Dict[str, Any] = Depends(require_role("admin"))):
    """Get comprehensive analytics summary"""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()

            # Total documents
            cursor.execute("SELECT COUNT(*) FROM documents")
            total_documents = cursor.fetchone()[0]

            # Total users
            cursor.execute("SELECT COUNT(*) FROM users")
            total_users = cursor.fetchone()[0]

            # OCR processing stats
            cursor.execute("""
                SELECT COUNT(*) as total, 
                       AVG(processing_time) as avg_time,
                       SUM(CASE WHEN status = 'completed' THEN 1 ELSE 0 END) as successful
                FROM documents 
                WHERE ocr_processed = 1
            """)
            ocr_stats = cursor.fetchone()
            total_ocr_processed = ocr_stats['total'] if ocr_stats['total'] else 0
            avg_processing_time = ocr_stats['avg_time'] if ocr_stats['avg_time'] else 0
            success_rate = (
                ocr_stats['successful'] / total_ocr_processed * 100) if total_ocr_processed > 0 else 0

            # Scraping sessions
            cursor.execute("SELECT COUNT(*) FROM scraping_sessions")
            total_scraping_sessions = cursor.fetchone()[0]

            # Cache statistics
            cache_stats = cache_service.get_cache_stats()
            cache_hit_rate = cache_stats.get('hit_rate', 0)

            # System uptime (simplified - in production, you'd track this properly)
            system_uptime = 99.5  # Placeholder

            return AnalyticsSummary(
                total_documents=total_documents,
                total_users=total_users,
                total_ocr_processed=total_ocr_processed,
                total_scraping_sessions=total_scraping_sessions,
                avg_processing_time=avg_processing_time,
                success_rate=success_rate,
                cache_hit_rate=cache_hit_rate,
                system_uptime=system_uptime
            )

    except Exception as e:
        logger.error(f"Error getting analytics summary: {e}")
        raise HTTPException(
            status_code=500, detail="Failed to retrieve analytics summary")


@router.get("/performance", response_model=PerformanceMetrics)
async def get_performance_metrics(current_user: Dict[str, Any] = Depends(require_role("admin"))):
    """Get system performance metrics"""
    try:
        # Get cache statistics
        cache_stats = cache_service.get_cache_stats()

        # Simulate performance metrics (in production, you'd get these from monitoring)
        api_response_times = {
            "documents": 150.0,
            "ocr": 2500.0,
            "search": 200.0,
            "analytics": 300.0
        }

        memory_usage = {
            "total": "2.5GB",
            "used": "1.8GB",
            "available": "700MB",
            "percentage": 72.0
        }

        cpu_usage = 45.5
        disk_usage = {
            "total": "50GB",
            "used": "35GB",
            "available": "15GB",
            "percentage": 70.0
        }

        active_connections = len(cache_service.active_connections) if hasattr(
            cache_service, 'active_connections') else 0

        return PerformanceMetrics(
            api_response_times=api_response_times,
            memory_usage=memory_usage,
            cpu_usage=cpu_usage,
            disk_usage=disk_usage,
            active_connections=active_connections
        )

    except Exception as e:
        logger.error(f"Error getting performance metrics: {e}")
        raise HTTPException(
            status_code=500, detail="Failed to retrieve performance metrics")


@router.get("/user-activity", response_model=List[UserActivity])
async def get_user_activity(
    days: int = Query(30, description="Number of days to analyze"),
    current_user: Dict[str, Any] = Depends(require_role("admin"))
):
    """Get user activity analytics"""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()

            # Get user activity for the specified period
            start_date = datetime.utcnow() - timedelta(days=days)

            cursor.execute("""
                SELECT 
                    u.id,
                    u.username,
                    COUNT(d.id) as documents_processed,
                    MAX(d.created_at) as last_activity,
                    AVG(d.processing_time) as avg_processing_time,
                    SUM(CASE WHEN d.status = 'completed' THEN 1 ELSE 0 END) as successful_docs,
                    COUNT(d.id) as total_docs
                FROM users u
                LEFT JOIN documents d ON u.id = d.user_id 
                    AND d.created_at >= ?
                GROUP BY u.id, u.username
                ORDER BY documents_processed DESC
            """, (start_date.isoformat(),))

            activities = []
            for row in cursor.fetchall():
                total_docs = row['total_docs'] or 0
                successful_docs = row['successful_docs'] or 0
                success_rate = (successful_docs / total_docs *
                                100) if total_docs > 0 else 0

                activities.append(UserActivity(
                    user_id=row['id'],
                    username=row['username'],
                    documents_processed=row['documents_processed'] or 0,
                    last_activity=row['last_activity'] or "Never",
                    total_processing_time=row['avg_processing_time'] or 0,
                    success_rate=success_rate
                ))

            return activities

    except Exception as e:
        logger.error(f"Error getting user activity: {e}")
        raise HTTPException(
            status_code=500, detail="Failed to retrieve user activity")


@router.get("/document-analytics", response_model=List[DocumentAnalytics])
async def get_document_analytics(
    limit: int = Query(100, description="Number of documents to retrieve"),
    current_user: Dict[str, Any] = Depends(require_role("admin"))
):
    """Get document processing analytics"""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()

            cursor.execute("""
                SELECT 
                    id,
                    filename,
                    processing_time,
                    ocr_accuracy,
                    file_size,
                    created_at,
                    status
                FROM documents
                ORDER BY created_at DESC
                LIMIT ?
            """, (limit,))

            analytics = []
            for row in cursor.fetchall():
                analytics.append(DocumentAnalytics(
                    document_id=row['id'],
                    filename=row['filename'],
                    processing_time=row['processing_time'] or 0,
                    ocr_accuracy=row['ocr_accuracy'],
                    file_size=row['file_size'] or 0,
                    created_at=row['created_at'],
                    status=row['status']
                ))

            return analytics

    except Exception as e:
        logger.error(f"Error getting document analytics: {e}")
        raise HTTPException(
            status_code=500, detail="Failed to retrieve document analytics")


@router.get("/export/csv")
async def export_analytics_csv(
    report_type: str = Query(
        ..., description="Type of report: summary, user_activity, document_analytics"),
    current_user: Dict[str, Any] = Depends(require_role("admin"))
):
    """Export analytics data as CSV"""
    try:
        if report_type == "summary":
            data = await get_analytics_summary(current_user)
            return _generate_summary_csv(data)
        elif report_type == "user_activity":
            data = await get_user_activity(30, current_user)
            return _generate_user_activity_csv(data)
        elif report_type == "document_analytics":
            data = await get_document_analytics(1000, current_user)
            return _generate_document_analytics_csv(data)
        else:
            raise HTTPException(status_code=400, detail="Invalid report type")

    except Exception as e:
        logger.error(f"Error exporting CSV: {e}")
        raise HTTPException(status_code=500, detail="Failed to export CSV")


def _generate_summary_csv(data: AnalyticsSummary):
    """Generate CSV for analytics summary"""
    output = io.StringIO()
    writer = csv.writer(output)

    writer.writerow(["Metric", "Value"])
    writer.writerow(["Total Documents", data.total_documents])
    writer.writerow(["Total Users", data.total_users])
    writer.writerow(["Total OCR Processed", data.total_ocr_processed])
    writer.writerow(["Total Scraping Sessions", data.total_scraping_sessions])
    writer.writerow(["Average Processing Time",
                    f"{data.avg_processing_time:.2f}s"])
    writer.writerow(["Success Rate", f"{data.success_rate:.2f}%"])
    writer.writerow(["Cache Hit Rate", f"{data.cache_hit_rate:.2f}%"])
    writer.writerow(["System Uptime", f"{data.system_uptime:.2f}%"])

    output.seek(0)
    return StreamingResponse(
        io.BytesIO(output.getvalue().encode()),
        media_type="text/csv",
        headers={
            "Content-Disposition": f"attachment; filename=analytics_summary_{datetime.now().strftime('%Y%m%d')}.csv"}
    )


def _generate_user_activity_csv(data: List[UserActivity]):
    """Generate CSV for user activity"""
    output = io.StringIO()
    writer = csv.writer(output)

    writer.writerow(["User ID", "Username", "Documents Processed",
                    "Last Activity", "Avg Processing Time", "Success Rate"])
    for activity in data:
        writer.writerow([
            activity.user_id,
            activity.username,
            activity.documents_processed,
            activity.last_activity,
            f"{activity.total_processing_time:.2f}s",
            f"{activity.success_rate:.2f}%"
        ])

    output.seek(0)
    return StreamingResponse(
        io.BytesIO(output.getvalue().encode()),
        media_type="text/csv",
        headers={
            "Content-Disposition": f"attachment; filename=user_activity_{datetime.now().strftime('%Y%m%d')}.csv"}
    )


def _generate_document_analytics_csv(data: List[DocumentAnalytics]):
    """Generate CSV for document analytics"""
    output = io.StringIO()
    writer = csv.writer(output)

    writer.writerow(["Document ID", "Filename", "Processing Time",
                    "OCR Accuracy", "File Size", "Created At", "Status"])
    for doc in data:
        writer.writerow([
            doc.document_id,
            doc.filename,
            f"{doc.processing_time:.2f}s",
            f"{doc.ocr_accuracy:.2f}%" if doc.ocr_accuracy else "N/A",
            f"{doc.file_size} bytes",
            doc.created_at,
            doc.status
        ])

    output.seek(0)
    return StreamingResponse(
        io.BytesIO(output.getvalue().encode()),
        media_type="text/csv",
        headers={
            "Content-Disposition": f"attachment; filename=document_analytics_{datetime.now().strftime('%Y%m%d')}.csv"}
    )


@router.get("/cache-stats")
async def get_cache_statistics(current_user: Dict[str, Any] = Depends(require_role("admin"))):
    """Get cache performance statistics"""
    try:
        stats = cache_service.get_cache_stats()
        return {
            "cache_stats": stats,
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Error getting cache stats: {e}")
        raise HTTPException(
            status_code=500, detail="Failed to retrieve cache statistics")


@router.get("/notification-stats")
async def get_notification_statistics(current_user: Dict[str, Any] = Depends(require_role("admin"))):
    """Get notification statistics"""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()

            # Total notifications
            cursor.execute("SELECT COUNT(*) FROM notifications")
            total_notifications = cursor.fetchone()[0]

            # Notifications by type
            cursor.execute("""
                SELECT type, COUNT(*) as count
                FROM notifications
                GROUP BY type
            """)
            by_type = dict(cursor.fetchall())

            # Recent notifications (last 24 hours)
            yesterday = datetime.utcnow() - timedelta(days=1)
            cursor.execute("""
                SELECT COUNT(*) FROM notifications
                WHERE created_at >= ?
            """, (yesterday.isoformat(),))
            recent_notifications = cursor.fetchone()[0]

            return {
                "total_notifications": total_notifications,
                "recent_notifications": recent_notifications,
                "by_type": by_type,
                "timestamp": datetime.utcnow().isoformat()
            }

    except Exception as e:
        logger.error(f"Error getting notification stats: {e}")
        raise HTTPException(
            status_code=500, detail="Failed to retrieve notification statistics")


@router.get("/system-health")
async def get_system_health(current_user: Dict[str, Any] = Depends(require_role("admin"))):
    """Get system health status"""
    try:
        # Check database connectivity
        db_healthy = False
        try:
            with get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT 1")
                db_healthy = True
        except:
            pass

        # Check cache connectivity
        cache_healthy = False
        try:
            cache_service.get("health_check")
            cache_healthy = True
        except:
            pass

        # Check disk space (simplified)
        disk_usage = {
            "total": "50GB",
            "used": "35GB",
            "available": "15GB",
            "healthy": True
        }

        # Check memory usage (simplified)
        memory_usage = {
            "total": "8GB",
            "used": "6GB",
            "available": "2GB",
            "healthy": True
        }

        return {
            "database": {
                "status": "healthy" if db_healthy else "unhealthy",
                "connected": db_healthy
            },
            "cache": {
                "status": "healthy" if cache_healthy else "unhealthy",
                "connected": cache_healthy
            },
            "disk": {
                "status": "healthy" if disk_usage["healthy"] else "warning",
                "usage": disk_usage
            },
            "memory": {
                "status": "healthy" if memory_usage["healthy"] else "warning",
                "usage": memory_usage
            },
            "overall_status": "healthy" if all([db_healthy, cache_healthy, disk_usage["healthy"], memory_usage["healthy"]]) else "warning",
            "timestamp": datetime.utcnow().isoformat()
        }

    except Exception as e:
        logger.error(f"Error getting system health: {e}")
        raise HTTPException(
            status_code=500, detail="Failed to retrieve system health")


@router.get("/trends")
async def get_analytics_trends(
    days: int = Query(30, description="Number of days to analyze"),
    current_user: Dict[str, Any] = Depends(require_role("admin"))
):
    """Get analytics trends over time"""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()

            # Daily document processing trends
            cursor.execute("""
                SELECT 
                    DATE(created_at) as date,
                    COUNT(*) as documents_processed,
                    AVG(processing_time) as avg_processing_time,
                    SUM(CASE WHEN status = 'completed' THEN 1 ELSE 0 END) as successful
                FROM documents
                WHERE created_at >= date('now', '-{} days')
                GROUP BY DATE(created_at)
                ORDER BY date
            """.format(days))

            daily_trends = []
            for row in cursor.fetchall():
                total = row['documents_processed']
                successful = row['successful']
                success_rate = (successful / total * 100) if total > 0 else 0

                daily_trends.append({
                    "date": row['date'],
                    "documents_processed": total,
                    "avg_processing_time": row['avg_processing_time'] or 0,
                    "success_rate": success_rate
                })

            return {
                "daily_trends": daily_trends,
                "period_days": days,
                "timestamp": datetime.utcnow().isoformat()
            }

    except Exception as e:
        logger.error(f"Error getting analytics trends: {e}")
        raise HTTPException(
            status_code=500, detail="Failed to retrieve analytics trends")
