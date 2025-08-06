"""
Dashboard API Router
==================

Dashboard statistics and analytics endpoints.
"""

from fastapi import APIRouter, HTTPException, Depends
from typing import List, Dict, Any
import logging
from ..models.document_models import DashboardSummary, AIFeedback
from ..services.database_service import DatabaseManager
from ..services.ai_service import AIScoringEngine

logger = logging.getLogger(__name__)

router = APIRouter()

# Dependency injection


def get_db():
    return DatabaseManager()


def get_ai_engine():
    return AIScoringEngine()


@router.get("/summary", response_model=DashboardSummary)
async def get_dashboard_summary(db: DatabaseManager = Depends(get_db)):
    """Get dashboard summary statistics"""
    try:
        summary = db.get_dashboard_summary()

        # Add system status
        summary['system_status'] = {
            'database_connected': db.is_connected(),
            'ai_engine_available': True,
            'ocr_pipeline_available': True  # This would be checked from OCR service
        }

        return DashboardSummary(**summary)

    except Exception as e:
        logger.error(f"Error getting dashboard summary: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/charts-data")
async def get_charts_data(db: DatabaseManager = Depends(get_db)):
    """Get data for dashboard charts"""
    try:
        # Get documents for analysis
        documents = db.get_documents(limit=1000)

        # Category distribution
        category_counts = {}
        source_counts = {}
        score_ranges = {
            '0-20': 0,
            '21-40': 0,
            '41-60': 0,
            '61-80': 0,
            '81-100': 0
        }

        for doc in documents:
            # Category counts
            category = doc.get('category', 'نامشخص')
            category_counts[category] = category_counts.get(category, 0) + 1

            # Source counts
            source = doc.get('source', 'نامشخص')
            source_counts[source] = source_counts.get(source, 0) + 1

            # Score ranges
            score = doc.get('final_score', 0)
            if score <= 20:
                score_ranges['0-20'] += 1
            elif score <= 40:
                score_ranges['21-40'] += 1
            elif score <= 60:
                score_ranges['41-60'] += 1
            elif score <= 80:
                score_ranges['61-80'] += 1
            else:
                score_ranges['81-100'] += 1

        # Recent activity (last 30 days)
        recent_docs = [doc for doc in documents if doc.get('created_at')]
        recent_activity = recent_docs[:10]  # Last 10 documents

        return {
            "category_distribution": [
                {"category": cat, "count": count}
                for cat, count in category_counts.items()
            ],
            "source_distribution": [
                {"source": src, "count": count}
                for src, count in source_counts.items()
            ],
            "score_distribution": [
                {"range": range_name, "count": count}
                for range_name, count in score_ranges.items()
            ],
            "recent_activity": recent_activity,
            "total_documents": len(documents)
        }

    except Exception as e:
        logger.error(f"Error getting charts data: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/ai-suggestions")
async def get_ai_suggestions(
    limit: int = 10,
    db: DatabaseManager = Depends(get_db),
    ai_engine: AIScoringEngine = Depends(get_ai_engine)
):
    """Get AI-powered document suggestions"""
    try:
        # Get recent documents
        documents = db.get_documents(limit=50)

        # Sort by score and get top suggestions
        scored_docs = []
        for doc in documents:
            if doc.get('final_score', 0) > 0:
                scored_docs.append(doc)

        # Sort by score (descending)
        scored_docs.sort(key=lambda x: x.get('final_score', 0), reverse=True)

        suggestions = scored_docs[:limit]

        return {
            "suggestions": suggestions,
            "total_suggestions": len(suggestions),
            "criteria": "Based on AI scoring and document quality"
        }

    except Exception as e:
        logger.error(f"Error getting AI suggestions: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/ai-training-stats")
async def get_ai_training_stats(
    db: DatabaseManager = Depends(get_db),
    ai_engine: AIScoringEngine = Depends(get_ai_engine)
):
    """Get AI training statistics"""
    try:
        # Get database training stats
        db_stats = db.get_ai_training_stats()

        # Get AI engine stats
        ai_stats = ai_engine.get_training_stats()

        # Combine stats
        combined_stats = {
            "database_stats": db_stats,
            "ai_engine_stats": ai_stats,
            "total_feedback": db_stats.get('total_feedback', 0) + ai_stats.get('total_feedback', 0)
        }

        return combined_stats

    except Exception as e:
        logger.error(f"Error getting AI training stats: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/ai-feedback")
async def submit_ai_feedback(
    feedback: AIFeedback,
    db: DatabaseManager = Depends(get_db),
    ai_engine: AIScoringEngine = Depends(get_ai_engine)
):
    """Submit AI training feedback"""
    try:
        # Add feedback to database
        success = db.add_ai_feedback(
            feedback.document_id,
            feedback.feedback_type,
            feedback.feedback_score,
            feedback.feedback_text
        )

        if not success:
            raise HTTPException(
                status_code=500, detail="Failed to save feedback")

        # Update AI engine weights
        ai_engine.update_weights_from_feedback(
            feedback.document_id,
            feedback.feedback_text,
            feedback.feedback_score
        )

        return {
            "message": "Feedback submitted successfully",
            "document_id": feedback.document_id,
            "feedback_type": feedback.feedback_type,
            "feedback_score": feedback.feedback_score
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error submitting AI feedback: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/performance-metrics")
async def get_performance_metrics(db: DatabaseManager = Depends(get_db)):
    """Get system performance metrics"""
    try:
        documents = db.get_documents(limit=1000)

        # Calculate metrics
        total_docs = len(documents)
        avg_score = sum(doc.get('final_score', 0)
                        for doc in documents) / total_docs if total_docs > 0 else 0
        avg_processing_time = sum(doc.get('processing_time', 0)
                                  for doc in documents) / total_docs if total_docs > 0 else 0

        # Quality metrics
        high_quality_docs = len(
            [doc for doc in documents if doc.get('final_score', 0) >= 80])
        medium_quality_docs = len(
            [doc for doc in documents if 50 <= doc.get('final_score', 0) < 80])
        low_quality_docs = len(
            [doc for doc in documents if doc.get('final_score', 0) < 50])

        return {
            "total_documents": total_docs,
            "average_score": round(avg_score, 2),
            "average_processing_time": round(avg_processing_time, 2),
            "quality_distribution": {
                "high_quality": high_quality_docs,
                "medium_quality": medium_quality_docs,
                "low_quality": low_quality_docs
            },
            "quality_percentages": {
                "high_quality": round(high_quality_docs / total_docs * 100, 2) if total_docs > 0 else 0,
                "medium_quality": round(medium_quality_docs / total_docs * 100, 2) if total_docs > 0 else 0,
                "low_quality": round(low_quality_docs / total_docs * 100, 2) if total_docs > 0 else 0
            }
        }

    except Exception as e:
        logger.error(f"Error getting performance metrics: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/trends")
async def get_trends(db: DatabaseManager = Depends(get_db)):
    """Get document processing trends"""
    try:
        documents = db.get_documents(limit=1000)

        # Group by month (simplified)
        monthly_counts = {}
        monthly_scores = {}

        for doc in documents:
            created_at = doc.get('created_at', '')
            if created_at:
                # Extract month from ISO format
                try:
                    month = created_at[:7]  # YYYY-MM
                    monthly_counts[month] = monthly_counts.get(month, 0) + 1

                    # Average score for month
                    if month not in monthly_scores:
                        monthly_scores[month] = []
                    monthly_scores[month].append(doc.get('final_score', 0))
                except:
                    pass

        # Calculate average scores per month
        monthly_trends = []
        for month in sorted(monthly_counts.keys()):
            avg_score = sum(
                monthly_scores[month]) / len(monthly_scores[month]) if monthly_scores[month] else 0
            monthly_trends.append({
                "month": month,
                "document_count": monthly_counts[month],
                "average_score": round(avg_score, 2)
            })

        return {
            "monthly_trends": monthly_trends,
            "total_months": len(monthly_trends)
        }

    except Exception as e:
        logger.error(f"Error getting trends: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
