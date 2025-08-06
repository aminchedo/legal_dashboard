"""
Analytics Models for Legal Dashboard
===================================
Pydantic models for analytics and AI feedback.
"""

from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from enum import Enum


class AnalyticsPeriod(str, Enum):
    """Analytics time periods"""
    DAY = "day"
    WEEK = "week"
    MONTH = "month"
    YEAR = "year"


class AIFeedbackType(str, Enum):
    """AI feedback types"""
    POSITIVE = "positive"
    NEGATIVE = "negative"
    NEUTRAL = "neutral"


class DashboardSummary(BaseModel):
    """Dashboard summary model"""
    total_documents: int
    documents_this_month: int
    documents_this_week: int
    documents_today: int
    total_size_mb: float
    average_ai_score: Optional[float] = None
    processing_queue: int
    completed_today: int
    failed_today: int
    top_document_types: Dict[str, int]
    recent_activity: List[Dict[str, Any]]


class AIFeedback(BaseModel):
    """AI feedback model"""
    document_id: int
    score: float = Field(..., ge=0.0, le=1.0)
    feedback_type: AIFeedbackType
    feedback_text: str
    confidence: float = Field(..., ge=0.0, le=1.0)
    generated_at: datetime
    model_version: Optional[str] = None
    processing_time: Optional[float] = None


class AnalyticsData(BaseModel):
    """Analytics data model"""
    period: AnalyticsPeriod
    start_date: datetime
    end_date: datetime
    document_uploads: List[Dict[str, Any]]
    processing_times: List[Dict[str, Any]]
    ai_scores: List[Dict[str, Any]]
    user_activity: List[Dict[str, Any]]
    error_rates: List[Dict[str, Any]]


class AnalyticsRequest(BaseModel):
    """Analytics request model"""
    period: AnalyticsPeriod = AnalyticsPeriod.MONTH
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    document_type: Optional[str] = None
    user_id: Optional[int] = None


class AnalyticsResponse(BaseModel):
    """Analytics response model"""
    summary: DashboardSummary
    analytics: AnalyticsData
    generated_at: datetime


class ProcessingStats(BaseModel):
    """Processing statistics model"""
    total_processed: int
    successful: int
    failed: int
    average_processing_time: float
    success_rate: float
    error_breakdown: Dict[str, int]


class UserActivity(BaseModel):
    """User activity model"""
    user_id: int
    username: str
    documents_uploaded: int
    last_activity: datetime
    total_size_uploaded: int
    average_ai_score: Optional[float] = None


class SystemHealth(BaseModel):
    """System health model"""
    status: str
    uptime: float
    memory_usage: float
    cpu_usage: float
    disk_usage: float
    active_connections: int
    queue_size: int
    last_backup: Optional[datetime] = None


class PerformanceMetrics(BaseModel):
    """Performance metrics model"""
    response_time_avg: float
    response_time_p95: float
    response_time_p99: float
    requests_per_minute: float
    error_rate: float
    active_users: int
    cache_hit_rate: Optional[float] = None


class DocumentAnalytics(BaseModel):
    """Document analytics model"""
    document_id: int
    title: str
    views: int
    downloads: int
    processing_time: float
    ai_score: Optional[float] = None
    user_feedback: Optional[str] = None
    last_accessed: Optional[datetime] = None


class SearchAnalytics(BaseModel):
    """Search analytics model"""
    query: str
    results_count: int
    search_time: float
    user_id: Optional[int] = None
    timestamp: datetime
    filters_used: Dict[str, Any]


class ErrorReport(BaseModel):
    """Error report model"""
    error_id: str
    error_type: str
    error_message: str
    stack_trace: Optional[str] = None
    user_id: Optional[int] = None
    document_id: Optional[int] = None
    timestamp: datetime
    resolved: bool = False
    resolution_notes: Optional[str] = None
