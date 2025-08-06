#!/usr/bin/env python3
"""
Enhanced Analytics API for Legal Dashboard
=========================================

Advanced analytics endpoints providing:
- Real-time performance metrics
- Predictive analytics and forecasting
- Document clustering and similarity analysis
- Quality assessment and recommendations
- System health monitoring
"""

from fastapi import APIRouter, HTTPException, Query, Depends, BackgroundTasks
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import logging
from pydantic import BaseModel, Field
import json
import asyncio

from ..services.advanced_analytics_service import AdvancedAnalyticsService
from ..services.database_service import DatabaseManager
from ..services.cache_service import cache_service

logger = logging.getLogger(__name__)

router = APIRouter()

# Pydantic models for request/response


class RealTimeMetricsResponse(BaseModel):
    """Real-time metrics response model"""
    total_documents: int
    processed_today: int
    avg_processing_time: float
    success_rate: float
    error_rate: float
    cache_hit_rate: float
    quality_score: float
    system_health: float
    timestamp: str


class TrendAnalysisRequest(BaseModel):
    """Trend analysis request model"""
    metric: str = Field(
        ..., description="Metric to analyze (e.g., 'processing_time', 'quality_score')")
    time_period: str = Field(
        "7d", description="Time period for analysis (7d, 30d, 90d)")
    category: Optional[str] = Field(None, description="Category filter")
    confidence_threshold: float = Field(
        0.8, description="Minimum confidence for trend analysis")


class TrendAnalysisResponse(BaseModel):
    """Trend analysis response model"""
    period: str
    metric: str
    values: List[float]
    timestamps: List[str]
    trend_direction: str
    change_percentage: float
    confidence: float
    trend_strength: str
    recommendations: List[str]


class SimilarityRequest(BaseModel):
    """Document similarity request model"""
    document_id: int = Field(..., description="Target document ID")
    threshold: float = Field(0.7, description="Similarity threshold")
    limit: int = Field(10, description="Maximum number of results")
    include_metadata: bool = Field(
        True, description="Include document metadata")


class SimilarityResponse(BaseModel):
    """Document similarity response model"""
    target_document_id: int
    similar_documents: List[Dict[str, Any]]
    total_found: int
    average_similarity: float
    processing_time: float


class PredictiveInsightsResponse(BaseModel):
    """Predictive insights response model"""
    patterns: Dict[str, Any]
    predictions: Dict[str, Any]
    confidence_intervals: Dict[str, List[float]]
    recommendations: List[str]
    next_24h_forecast: Dict[str, Any]
    system_optimization_suggestions: List[str]


class ClusteringRequest(BaseModel):
    """Document clustering request model"""
    n_clusters: int = Field(5, description="Number of clusters")
    category: Optional[str] = Field(None, description="Category filter")
    min_cluster_size: int = Field(
        2, description="Minimum documents per cluster")


class ClusteringResponse(BaseModel):
    """Document clustering response model"""
    clusters: Dict[str, List[Dict[str, Any]]]
    centroids: List[List[float]]
    silhouette_score: float
    total_documents: int
    cluster_quality_metrics: Dict[str, float]


class QualityReportResponse(BaseModel):
    """Quality report response model"""
    overall_quality_score: float
    quality_distribution: Dict[str, int]
    common_issues: List[Dict[str, Any]]
    recommendations: List[str]
    quality_trends: Dict[str, Any]
    improvement_opportunities: List[Dict[str, Any]]
    next_actions: List[str]


class SystemHealthResponse(BaseModel):
    """System health response model"""
    overall_health: float
    component_health: Dict[str, float]
    performance_metrics: Dict[str, float]
    alerts: List[Dict[str, Any]]
    recommendations: List[str]
    last_updated: str


# Dependency injection


def get_analytics_service() -> AdvancedAnalyticsService:
    return AdvancedAnalyticsService()


def get_db_manager() -> DatabaseManager:
    return DatabaseManager()


@router.get("/real-time-metrics", response_model=RealTimeMetricsResponse)
async def get_real_time_metrics(
    analytics_service: AdvancedAnalyticsService = Depends(
        get_analytics_service)
):
    """Get real-time system metrics"""
    try:
        metrics = await analytics_service.get_real_time_metrics()

        return RealTimeMetricsResponse(
            total_documents=metrics.total_documents,
            processed_today=metrics.processed_today,
            avg_processing_time=metrics.avg_processing_time,
            success_rate=metrics.success_rate,
            error_rate=metrics.error_rate,
            cache_hit_rate=metrics.cache_hit_rate,
            quality_score=metrics.quality_score,
            system_health=metrics.system_health,
            timestamp=datetime.now().isoformat()
        )

    except Exception as e:
        logger.error(f"Error getting real-time metrics: {e}")
        raise HTTPException(
            status_code=500, detail=f"Failed to get real-time metrics: {str(e)}")


@router.post("/trends", response_model=TrendAnalysisResponse)
async def analyze_trends(
    request: TrendAnalysisRequest,
    analytics_service: AdvancedAnalyticsService = Depends(
        get_analytics_service)
):
    """Analyze trends for specific metrics"""
    try:
        trend_data = await analytics_service.analyze_trends(
            metric=request.metric,
            time_period=request.time_period,
            category=request.category
        )

        # Determine trend strength
        if trend_data.confidence >= 0.9:
            trend_strength = "strong"
        elif trend_data.confidence >= 0.7:
            trend_strength = "moderate"
        else:
            trend_strength = "weak"

        # Generate recommendations based on trend
        recommendations = _generate_trend_recommendations(trend_data)

        return TrendAnalysisResponse(
            period=trend_data.period,
            metric=trend_data.metric,
            values=trend_data.values,
            timestamps=trend_data.timestamps,
            trend_direction=trend_data.trend_direction,
            change_percentage=trend_data.change_percentage,
            confidence=trend_data.confidence,
            trend_strength=trend_strength,
            recommendations=recommendations
        )

    except Exception as e:
        logger.error(f"Error analyzing trends: {e}")
        raise HTTPException(
            status_code=500, detail=f"Failed to analyze trends: {str(e)}")


@router.post("/similarity", response_model=SimilarityResponse)
async def find_similar_documents(
    request: SimilarityRequest,
    analytics_service: AdvancedAnalyticsService = Depends(
        get_analytics_service),
    db_manager: DatabaseManager = Depends(get_db_manager)
):
    """Find similar documents using advanced similarity analysis"""
    try:
        start_time = datetime.now()

        similar_docs = await analytics_service.find_similar_documents(
            document_id=request.document_id,
            threshold=request.threshold,
            limit=request.limit
        )

        processing_time = (datetime.now() - start_time).total_seconds()

        # Prepare response data
        similar_documents = []
        total_similarity = 0

        for doc in similar_docs:
            doc_data = {
                "document_id": doc.document_id,
                "similarity_score": doc.similarity_score,
                "common_entities": doc.common_entities,
                "shared_topics": doc.shared_topics,
                "relevance_score": doc.relevance_score
            }

            if request.include_metadata:
                # Get document metadata
                metadata = db_manager.get_document_by_id(doc.document_id)
                if metadata:
                    doc_data["metadata"] = {
                        "title": metadata.get("title", ""),
                        "category": metadata.get("category", ""),
                        "created_at": metadata.get("created_at", ""),
                        "file_size": metadata.get("file_size", 0)
                    }

            similar_documents.append(doc_data)
            total_similarity += doc.similarity_score

        average_similarity = total_similarity / \
            len(similar_documents) if similar_documents else 0

        return SimilarityResponse(
            target_document_id=request.document_id,
            similar_documents=similar_documents,
            total_found=len(similar_documents),
            average_similarity=average_similarity,
            processing_time=processing_time
        )

    except Exception as e:
        logger.error(f"Error finding similar documents: {e}")
        raise HTTPException(
            status_code=500, detail=f"Failed to find similar documents: {str(e)}")


@router.get("/predictive-insights", response_model=PredictiveInsightsResponse)
async def get_predictive_insights(
    analytics_service: AdvancedAnalyticsService = Depends(
        get_analytics_service)
):
    """Get predictive insights for document processing"""
    try:
        insights = await analytics_service.generate_predictive_insights()

        # Generate next 24h forecast
        next_24h_forecast = _generate_24h_forecast(
            insights.get("predictions", {}))

        # Generate system optimization suggestions
        optimization_suggestions = _generate_optimization_suggestions(insights)

        return PredictiveInsightsResponse(
            patterns=insights.get("patterns", {}),
            predictions=insights.get("predictions", {}),
            confidence_intervals=insights.get("confidence_intervals", {}),
            recommendations=insights.get("recommendations", []),
            next_24h_forecast=next_24h_forecast,
            system_optimization_suggestions=optimization_suggestions
        )

    except Exception as e:
        logger.error(f"Error getting predictive insights: {e}")
        raise HTTPException(
            status_code=500, detail=f"Failed to get predictive insights: {str(e)}")


@router.post("/clustering", response_model=ClusteringResponse)
async def cluster_documents(
    request: ClusteringRequest,
    analytics_service: AdvancedAnalyticsService = Depends(
        get_analytics_service)
):
    """Cluster documents using advanced clustering algorithms"""
    try:
        clustering_result = await analytics_service.cluster_documents(
            n_clusters=request.n_clusters,
            category=request.category
        )

        # Calculate cluster quality metrics
        cluster_quality = _calculate_cluster_quality(
            clustering_result.get("clusters", {}))

        return ClusteringResponse(
            clusters=clustering_result.get("clusters", {}),
            centroids=clustering_result.get("centroids", []),
            silhouette_score=clustering_result.get("silhouette_score", 0),
            total_documents=clustering_result.get("total_documents", 0),
            cluster_quality_metrics=cluster_quality
        )

    except Exception as e:
        logger.error(f"Error clustering documents: {e}")
        raise HTTPException(
            status_code=500, detail=f"Failed to cluster documents: {str(e)}")


@router.get("/quality-report", response_model=QualityReportResponse)
async def get_quality_report(
    category: Optional[str] = Query(None, description="Category filter"),
    analytics_service: AdvancedAnalyticsService = Depends(
        get_analytics_service)
):
    """Generate comprehensive quality analysis report"""
    try:
        quality_report = await analytics_service.generate_quality_report(category)

        # Generate next actions based on quality issues
        next_actions = _generate_quality_actions(quality_report)

        return QualityReportResponse(
            overall_quality_score=quality_report.get(
                "overall_quality_score", 0),
            quality_distribution=quality_report.get(
                "quality_distribution", {}),
            common_issues=quality_report.get("common_issues", []),
            recommendations=quality_report.get("recommendations", []),
            quality_trends=quality_report.get("quality_trends", {}),
            improvement_opportunities=quality_report.get(
                "improvement_opportunities", []),
            next_actions=next_actions
        )

    except Exception as e:
        logger.error(f"Error generating quality report: {e}")
        raise HTTPException(
            status_code=500, detail=f"Failed to generate quality report: {str(e)}")


@router.get("/system-health", response_model=SystemHealthResponse)
async def get_system_health(
    analytics_service: AdvancedAnalyticsService = Depends(
        get_analytics_service),
    db_manager: DatabaseManager = Depends(get_db_manager)
):
    """Get comprehensive system health status"""
    try:
        # Get real-time metrics
        metrics = await analytics_service.get_real_time_metrics()

        # Calculate component health
        component_health = _calculate_component_health(metrics, db_manager)

        # Get performance metrics
        performance_metrics = _get_performance_metrics(db_manager)

        # Generate alerts
        alerts = _generate_system_alerts(metrics, component_health)

        # Generate recommendations
        recommendations = _generate_system_recommendations(metrics, alerts)

        return SystemHealthResponse(
            overall_health=metrics.system_health,
            component_health=component_health,
            performance_metrics=performance_metrics,
            alerts=alerts,
            recommendations=recommendations,
            last_updated=datetime.now().isoformat()
        )

    except Exception as e:
        logger.error(f"Error getting system health: {e}")
        raise HTTPException(
            status_code=500, detail=f"Failed to get system health: {str(e)}")


@router.get("/performance-dashboard")
async def get_performance_dashboard(
    time_range: str = Query(
        "24h", description="Time range for dashboard data"),
    analytics_service: AdvancedAnalyticsService = Depends(
        get_analytics_service)
):
    """Get comprehensive performance dashboard data"""
    try:
        # Get real-time metrics
        metrics = await analytics_service.get_real_time_metrics()

        # Get trend data for different metrics
        processing_trend = await analytics_service.analyze_trends("processing_time", time_range)
        quality_trend = await analytics_service.analyze_trends("quality_score", time_range)
        volume_trend = await analytics_service.analyze_trends("document_volume", time_range)

        # Get predictive insights
        insights = await analytics_service.generate_predictive_insights()

        return {
            "status": "success",
            "data": {
                "real_time_metrics": {
                    "total_documents": metrics.total_documents,
                    "processed_today": metrics.processed_today,
                    "avg_processing_time": metrics.avg_processing_time,
                    "success_rate": metrics.success_rate,
                    "system_health": metrics.system_health
                },
                "trends": {
                    "processing_time": {
                        "direction": processing_trend.trend_direction,
                        "change_percentage": processing_trend.change_percentage,
                        "confidence": processing_trend.confidence
                    },
                    "quality_score": {
                        "direction": quality_trend.trend_direction,
                        "change_percentage": quality_trend.change_percentage,
                        "confidence": quality_trend.confidence
                    },
                    "document_volume": {
                        "direction": volume_trend.trend_direction,
                        "change_percentage": volume_trend.change_percentage,
                        "confidence": volume_trend.confidence
                    }
                },
                "predictions": insights.get("predictions", {}),
                "recommendations": insights.get("recommendations", []),
                "timestamp": datetime.now().isoformat()
            }
        }

    except Exception as e:
        logger.error(f"Error getting performance dashboard: {e}")
        raise HTTPException(
            status_code=500, detail=f"Failed to get performance dashboard: {str(e)}")


# Helper functions


def _generate_trend_recommendations(trend_data) -> List[str]:
    """Generate recommendations based on trend analysis"""
    recommendations = []

    if trend_data.trend_direction == "up":
        if trend_data.metric == "processing_time":
            recommendations.append(
                "Processing times are increasing - consider optimizing the pipeline")
        elif trend_data.metric == "quality_score":
            recommendations.append(
                "Quality scores are improving - maintain current processes")
        elif trend_data.metric == "document_volume":
            recommendations.append(
                "Document volume is increasing - consider scaling infrastructure")
    elif trend_data.trend_direction == "down":
        if trend_data.metric == "quality_score":
            recommendations.append(
                "Quality scores are declining - investigate and implement quality improvements")
        elif trend_data.metric == "success_rate":
            recommendations.append(
                "Success rate is declining - investigate error patterns")

    if trend_data.confidence < 0.7:
        recommendations.append(
            "Low confidence in trend analysis - collect more data for reliable insights")

    return recommendations


def _generate_24h_forecast(predictions: Dict[str, Any]) -> Dict[str, Any]:
    """Generate 24-hour forecast based on predictions"""
    try:
        forecast = {
            "expected_documents": predictions.get("expected_volume", 0),
            "peak_hours": predictions.get("peak_hours", []),
            "avg_processing_time": predictions.get("processing_time_forecast", 0),
            "quality_forecast": predictions.get("quality_forecast", 0),
            "system_load": "medium"  # Default, can be enhanced with actual load prediction
        }

        # Adjust forecast based on historical patterns
        if forecast["expected_documents"] > 100:
            forecast["system_load"] = "high"
        elif forecast["expected_documents"] < 20:
            forecast["system_load"] = "low"

        return forecast

    except Exception as e:
        logger.error(f"Error generating 24h forecast: {e}")
        return {}


def _generate_optimization_suggestions(insights: Dict[str, Any]) -> List[str]:
    """Generate system optimization suggestions"""
    suggestions = []

    predictions = insights.get("predictions", {})

    if predictions.get("processing_time_forecast", 0) > 30:
        suggestions.append(
            "Optimize document processing pipeline for faster processing")

    if predictions.get("quality_forecast", 0) < 0.7:
        suggestions.append(
            "Implement additional quality checks and validation")

    if predictions.get("expected_volume", 0) > 1000:
        suggestions.append(
            "Consider scaling infrastructure to handle increased load")

    patterns = insights.get("patterns", {})
    if patterns.get("error_patterns"):
        suggestions.append("Investigate and resolve common error patterns")

    return suggestions


def _calculate_cluster_quality(clusters: Dict[str, List]) -> Dict[str, float]:
    """Calculate quality metrics for each cluster"""
    quality_metrics = {}

    for cluster_name, documents in clusters.items():
        if documents:
            # Calculate average similarity to centroid
            similarities = [doc.get("similarity_to_centroid", 0)
                            for doc in documents]
            avg_similarity = sum(similarities) / \
                len(similarities) if similarities else 0

            # Calculate cluster size score
            size_score = min(1.0, len(documents) / 10)  # Normalize to 0-1

            # Overall cluster quality
            quality_metrics[cluster_name] = (avg_similarity + size_score) / 2

    return quality_metrics


def _generate_quality_actions(quality_report: Dict[str, Any]) -> List[str]:
    """Generate next actions based on quality report"""
    actions = []

    overall_score = quality_report.get("overall_quality_score", 0)
    common_issues = quality_report.get("common_issues", [])

    if overall_score < 0.8:
        actions.append("Implement comprehensive quality improvement plan")

    for issue in common_issues:
        if issue.get("severity") == "high":
            actions.append(
                f"Address high-priority issue: {issue.get('type', 'Unknown')}")

    opportunities = quality_report.get("improvement_opportunities", [])
    if opportunities:
        actions.append("Focus on highest-impact improvement opportunities")

    return actions


def _calculate_component_health(metrics, db_manager) -> Dict[str, float]:
    """Calculate health scores for different system components"""
    try:
        components = {
            "database": 100.0,  # Default, can be enhanced with actual DB health checks
            "ocr_pipeline": 100.0,
            "ai_engine": 100.0,
            "cache_system": 100.0,
            "file_storage": 100.0
        }

        # Adjust based on metrics
        if metrics.success_rate < 90:
            components["ocr_pipeline"] = metrics.success_rate
            components["ai_engine"] = metrics.success_rate

        if metrics.cache_hit_rate < 80:
            components["cache_system"] = metrics.cache_hit_rate

        return components

    except Exception as e:
        logger.error(f"Error calculating component health: {e}")
        return {}


def _get_performance_metrics(db_manager) -> Dict[str, float]:
    """Get detailed performance metrics"""
    try:
        return {
            "avg_response_time": 0.5,  # Placeholder, should be calculated from actual data
            "throughput": 100,  # documents per hour
            "error_rate": 0.02,  # 2%
            "uptime": 99.9,  # 99.9%
            "memory_usage": 75.0,  # 75%
            "cpu_usage": 60.0  # 60%
        }

    except Exception as e:
        logger.error(f"Error getting performance metrics: {e}")
        return {}


def _generate_system_alerts(metrics, component_health) -> List[Dict[str, Any]]:
    """Generate system alerts based on metrics and component health"""
    alerts = []

    # Check success rate
    if metrics.success_rate < 90:
        alerts.append({
            "type": "warning",
            "component": "processing_pipeline",
            "message": f"Success rate below threshold: {metrics.success_rate:.1f}%",
            "severity": "medium"
        })

    # Check system health
    if metrics.system_health < 80:
        alerts.append({
            "type": "error",
            "component": "system",
            "message": f"System health critical: {metrics.system_health:.1f}%",
            "severity": "high"
        })

    # Check component health
    for component, health in component_health.items():
        if health < 80:
            alerts.append({
                "type": "warning",
                "component": component,
                "message": f"{component.replace('_', ' ').title()} health degraded: {health:.1f}%",
                "severity": "medium"
            })

    return alerts


def _generate_system_recommendations(metrics, alerts) -> List[str]:
    """Generate system recommendations based on metrics and alerts"""
    recommendations = []

    if metrics.success_rate < 90:
        recommendations.append("Investigate and resolve processing failures")

    if metrics.avg_processing_time > 30:
        recommendations.append("Optimize document processing pipeline")

    if metrics.cache_hit_rate < 80:
        recommendations.append("Optimize cache configuration and usage")

    if alerts:
        recommendations.append(
            "Address system alerts to improve overall health")

    return recommendations
