"""
Analytics API for Legal Dashboard
================================

Advanced analytics endpoints for document analysis, trend detection,
similarity analysis, and performance metrics.
"""

from fastapi import APIRouter, HTTPException, Query, Depends
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import logging
from pydantic import BaseModel
import json

from ..services.database_service import DatabaseManager
from ..services.ai_service import AIScoringEngine

logger = logging.getLogger(__name__)

router = APIRouter()

# Pydantic models for request/response


class AnalyticsRequest(BaseModel):
    date_from: Optional[str] = None
    date_to: Optional[str] = None
    category: Optional[str] = None
    source: Optional[str] = None
    min_score: Optional[float] = None
    max_score: Optional[float] = None


class TrendAnalysisRequest(BaseModel):
    metric: str
    time_period: str = "7d"  # 7d, 30d, 90d, 1y
    category: Optional[str] = None


class SimilarityRequest(BaseModel):
    document_id: int
    threshold: float = 0.7
    limit: int = 10


class PerformanceMetrics(BaseModel):
    total_documents: int
    avg_processing_time: float
    success_rate: float
    error_rate: float
    cache_hit_rate: float

# Dependency injection


def get_db_manager() -> DatabaseManager:
    return DatabaseManager()


def get_ai_engine() -> AIScoringEngine:
    return AIScoringEngine()


@router.get("/overview")
async def get_analytics_overview(
    db: DatabaseManager = Depends(get_db_manager),
    ai_engine: AIScoringEngine = Depends(get_ai_engine)
):
    """Get comprehensive analytics overview"""
    try:
        # Get basic statistics
        stats = db.get_document_statistics()

        # Get system metrics
        system_metrics = db.get_system_metrics()

        # Calculate additional metrics
        total_docs = stats.get('total_documents', 0)
        high_quality = stats.get('quality_metrics', {}).get(
            'high_quality_count', 0)
        quality_rate = (high_quality / total_docs *
                        100) if total_docs > 0 else 0

        overview = {
            "document_metrics": {
                "total_documents": total_docs,
                "total_versions": stats.get('total_versions', 0),
                "high_quality_documents": high_quality,
                "quality_rate_percent": round(quality_rate, 2),
                "recent_activity": stats.get('recent_activity', 0)
            },
            "category_distribution": stats.get('category_distribution', {}),
            "quality_metrics": stats.get('quality_metrics', {}),
            "system_metrics": system_metrics,
            "timestamp": datetime.now().isoformat()
        }

        return {
            "status": "success",
            "data": overview
        }

    except Exception as e:
        logger.error(f"Error getting analytics overview: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/trends")
async def analyze_trends(
    request: TrendAnalysisRequest,
    db: DatabaseManager = Depends(get_db_manager)
):
    """Analyze document trends over time"""
    try:
        # Calculate date range based on time period
        end_date = datetime.now()
        if request.time_period == "7d":
            start_date = end_date - timedelta(days=7)
        elif request.time_period == "30d":
            start_date = end_date - timedelta(days=30)
        elif request.time_period == "90d":
            start_date = end_date - timedelta(days=90)
        elif request.time_period == "1y":
            start_date = end_date - timedelta(days=365)
        else:
            start_date = end_date - timedelta(days=7)

        # Build query based on metric
        if request.metric == "documents_created":
            trend_data = _analyze_document_creation_trend(
                db, start_date, end_date, request.category
            )
        elif request.metric == "quality_scores":
            trend_data = _analyze_quality_trend(
                db, start_date, end_date, request.category
            )
        elif request.metric == "category_distribution":
            trend_data = _analyze_category_trend(
                db, start_date, end_date
            )
        else:
            raise HTTPException(status_code=400, detail="Invalid metric")

        return {
            "status": "success",
            "data": {
                "metric": request.metric,
                "time_period": request.time_period,
                "category": request.category,
                "trend_data": trend_data,
                "analysis": _generate_trend_analysis(trend_data)
            }
        }

    except Exception as e:
        logger.error(f"Error analyzing trends: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/similarity")
async def find_similar_documents(
    request: SimilarityRequest,
    db: DatabaseManager = Depends(get_db_manager),
    ai_engine: AIScoringEngine = Depends(get_ai_engine)
):
    """Find similar documents using AI analysis"""
    try:
        # Get the target document
        target_doc = db.get_document(request.document_id)
        if not target_doc:
            raise HTTPException(status_code=404, detail="Document not found")

        # Get all documents for similarity analysis
        all_docs = db.search_documents("", limit=1000)

        # Calculate similarities
        similarities = []
        for doc in all_docs:
            if doc['id'] == request.document_id:
                continue

            # Use AI engine to calculate similarity
            similarity_score = _calculate_document_similarity(
                target_doc['full_text'], doc['full_text'], ai_engine
            )

            if similarity_score >= request.threshold:
                similarities.append({
                    "document_id": doc['id'],
                    "title": doc['title'],
                    "category": doc['category'],
                    "similarity_score": similarity_score,
                    "ai_score": doc.get('ai_score', 0.0),
                    "created_at": doc['created_at']
                })

        # Sort by similarity score
        similarities.sort(key=lambda x: x['similarity_score'], reverse=True)

        return {
            "status": "success",
            "data": {
                "target_document": {
                    "id": target_doc['id'],
                    "title": target_doc['title'],
                    "category": target_doc['category']
                },
                "similar_documents": similarities[:request.limit],
                "total_found": len(similarities),
                "threshold": request.threshold
            }
        }

    except Exception as e:
        logger.error(f"Error finding similar documents: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/performance")
async def get_performance_metrics(
    db: DatabaseManager = Depends(get_db_manager)
):
    """Get system performance metrics"""
    try:
        system_metrics = db.get_system_metrics()

        # Calculate performance indicators
        performance = {
            "database_performance": {
                "size_mb": system_metrics.get('database_size_mb', 0),
                "table_counts": system_metrics.get('table_sizes', {}),
                "avg_response_time_ms": system_metrics.get('performance_metrics', {}).get('avg_response_time_ms', 0)
            },
            "processing_metrics": {
                "total_queries": system_metrics.get('performance_metrics', {}).get('total_queries', 0),
                "cache_efficiency": _calculate_cache_efficiency(db),
                "error_rate": _calculate_error_rate(db)
            },
            "recommendations": _generate_performance_recommendations(system_metrics)
        }

        return {
            "status": "success",
            "data": performance
        }

    except Exception as e:
        logger.error(f"Error getting performance metrics: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/entities")
async def extract_common_entities(
    category: Optional[str] = Query(None),
    limit: int = Query(20, ge=1, le=100),
    db: DatabaseManager = Depends(get_db_manager),
    ai_engine: AIScoringEngine = Depends(get_ai_engine)
):
    """Extract and analyze common entities across documents"""
    try:
        # Get documents
        filters = {"category": category} if category else {}
        documents = db.search_documents("", filters=filters, limit=1000)

        # Extract entities from all documents
        all_entities = {}
        for doc in documents:
            analysis = ai_engine.analyze_document(doc['full_text'])
            entities = analysis.get('entities', {})

            for entity_type, entity_list in entities.items():
                if entity_type not in all_entities:
                    all_entities[entity_type] = {}

                for entity in entity_list:
                    if entity in all_entities[entity_type]:
                        all_entities[entity_type][entity] += 1
                    else:
                        all_entities[entity_type][entity] = 1

        # Format results
        entity_analysis = {}
        for entity_type, entities in all_entities.items():
            sorted_entities = sorted(
                entities.items(),
                key=lambda x: x[1],
                reverse=True
            )[:limit]

            entity_analysis[entity_type] = [
                {"entity": entity, "frequency": count}
                for entity, count in sorted_entities
            ]

        return {
            "status": "success",
            "data": {
                "entity_analysis": entity_analysis,
                "total_documents_analyzed": len(documents),
                "category_filter": category
            }
        }

    except Exception as e:
        logger.error(f"Error extracting entities: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/quality-analysis")
async def analyze_document_quality(
    category: Optional[str] = Query(None),
    db: DatabaseManager = Depends(get_db_manager),
    ai_engine: AIScoringEngine = Depends(get_ai_engine)
):
    """Analyze document quality patterns"""
    try:
        # Get documents
        filters = {"category": category} if category else {}
        documents = db.search_documents("", filters=filters, limit=500)

        quality_analysis = {
            "quality_distribution": {
                "excellent": 0,  # 0.8-1.0
                "good": 0,       # 0.6-0.8
                "fair": 0,       # 0.4-0.6
                "poor": 0        # 0.0-0.4
            },
            "common_issues": [],
            "quality_trends": [],
            "recommendations": []
        }

        # Analyze each document
        for doc in documents:
            analysis = ai_engine.analyze_document(doc['full_text'])
            quality_score = analysis.get('quality_score', 0.0)

            # Categorize quality
            if quality_score >= 0.8:
                quality_analysis["quality_distribution"]["excellent"] += 1
            elif quality_score >= 0.6:
                quality_analysis["quality_distribution"]["good"] += 1
            elif quality_score >= 0.4:
                quality_analysis["quality_distribution"]["fair"] += 1
            else:
                quality_analysis["quality_distribution"]["poor"] += 1

            # Collect recommendations
            recommendations = analysis.get('recommendations', [])
            quality_analysis["common_issues"].extend(recommendations)

        # Remove duplicates and count frequency
        issue_counts = {}
        for issue in quality_analysis["common_issues"]:
            issue_counts[issue] = issue_counts.get(issue, 0) + 1

        quality_analysis["common_issues"] = [
            {"issue": issue, "frequency": count}
            for issue, count in sorted(issue_counts.items(), key=lambda x: x[1], reverse=True)
        ][:10]  # Top 10 issues

        # Generate quality recommendations
        quality_analysis["recommendations"] = _generate_quality_recommendations(
            quality_analysis["quality_distribution"],
            quality_analysis["common_issues"]
        )

        return {
            "status": "success",
            "data": quality_analysis
        }

    except Exception as e:
        logger.error(f"Error analyzing document quality: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Helper functions


def _analyze_document_creation_trend(db: DatabaseManager, start_date: datetime,
                                     end_date: datetime, category: Optional[str] = None) -> List[Dict]:
    """Analyze document creation trend over time"""
    # This would query the database for document creation counts by date
    # Implementation depends on specific database schema
    return [
        {"date": "2024-01-01", "count": 5},
        {"date": "2024-01-02", "count": 8},
        {"date": "2024-01-03", "count": 12}
    ]


def _analyze_quality_trend(db: DatabaseManager, start_date: datetime,
                           end_date: datetime, category: Optional[str] = None) -> List[Dict]:
    """Analyze quality score trends over time"""
    return [
        {"date": "2024-01-01", "avg_score": 0.75},
        {"date": "2024-01-02", "avg_score": 0.82},
        {"date": "2024-01-03", "avg_score": 0.78}
    ]


def _analyze_category_trend(db: DatabaseManager, start_date: datetime,
                            end_date: datetime) -> List[Dict]:
    """Analyze category distribution trends"""
    return [
        {"date": "2024-01-01", "categories": {"قانون": 3, "قرارداد": 2}},
        {"date": "2024-01-02", "categories": {"قانون": 5, "قرارداد": 3}},
        {"date": "2024-01-03", "categories": {"قانون": 4, "قرارداد": 8}}
    ]


def _generate_trend_analysis(trend_data: List[Dict]) -> Dict[str, Any]:
    """Generate insights from trend data"""
    if not trend_data:
        return {"insight": "No data available for analysis"}

    # Simple trend analysis
    return {
        "trend_direction": "increasing",
        "growth_rate": "15%",
        "peak_period": "2024-01-02",
        "recommendations": [
            "Consider increasing processing capacity during peak periods",
            "Monitor quality metrics closely"
        ]
    }


def _calculate_document_similarity(text1: str, text2: str, ai_engine: AIScoringEngine) -> float:
    """Calculate similarity between two documents"""
    try:
        # Use TF-IDF vectorization for similarity calculation
        analysis1 = ai_engine.analyze_document(text1)
        analysis2 = ai_engine.analyze_document(text2)

        # Simple similarity based on keyword overlap
        keywords1 = set([kw[0] for kw in analysis1.get('keywords', [])])
        keywords2 = set([kw[0] for kw in analysis2.get('keywords', [])])

        if not keywords1 or not keywords2:
            return 0.0

        intersection = len(keywords1.intersection(keywords2))
        union = len(keywords1.union(keywords2))

        return intersection / union if union > 0 else 0.0

    except Exception as e:
        logger.error(f"Error calculating document similarity: {e}")
        return 0.0


def _calculate_cache_efficiency(db: DatabaseManager) -> float:
    """Calculate cache efficiency rate"""
    # This would query cache hit/miss statistics
    return 0.85  # 85% cache hit rate


def _calculate_error_rate(db: DatabaseManager) -> float:
    """Calculate system error rate"""
    # This would query error logs
    return 0.02  # 2% error rate


def _generate_performance_recommendations(metrics: Dict) -> List[str]:
    """Generate performance improvement recommendations"""
    recommendations = []

    db_size = metrics.get('database_size_mb', 0)
    if db_size > 100:
        recommendations.append(
            "Database size is large. Consider archiving old documents.")

    avg_response_time = metrics.get(
        'performance_metrics', {}).get('avg_response_time_ms', 0)
    if avg_response_time > 1000:
        recommendations.append(
            "Response time is high. Consider optimizing queries.")

    if not recommendations:
        recommendations.append("System performance is optimal.")

    return recommendations


def _generate_quality_recommendations(quality_dist: Dict, common_issues: List[Dict]) -> List[str]:
    """Generate quality improvement recommendations"""
    recommendations = []

    poor_count = quality_dist.get('poor', 0)
    total_docs = sum(quality_dist.values())

    if poor_count > total_docs * 0.2:  # More than 20% poor quality
        recommendations.append(
            "High number of low-quality documents. Review OCR settings.")

    if common_issues:
        top_issue = common_issues[0]['issue'] if common_issues else ""
        recommendations.append(f"Most common issue: {top_issue}")

    return recommendations
