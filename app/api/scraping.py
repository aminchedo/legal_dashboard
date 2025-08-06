"""
Scraping and Rating API Endpoints
================================

FastAPI endpoints for web scraping and data rating functionality.
Provides comprehensive API for managing scraping jobs, monitoring progress,
and retrieving rating data.
"""

import logging
from typing import List, Optional, Dict, Any
from datetime import datetime
from fastapi import APIRouter, HTTPException, BackgroundTasks, Query, Depends
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, HttpUrl
from enum import Enum

from ..services.scraping_service import ScrapingService, ScrapingStrategy
from ..services.rating_service import RatingService

logger = logging.getLogger(__name__)

# Initialize services
scraping_service = ScrapingService()
rating_service = RatingService()

# Request/Response Models


class ScrapingStrategyEnum(str, Enum):
    """Available scraping strategies for API"""
    GENERAL = "general"
    LEGAL_DOCUMENTS = "legal_documents"
    NEWS_ARTICLES = "news_articles"
    ACADEMIC_PAPERS = "academic_papers"
    GOVERNMENT_SITES = "government_sites"
    CUSTOM = "custom"


class ScrapingRequest(BaseModel):
    """Request model for starting a scraping job"""
    urls: List[str] = Field(..., description="List of URLs to scrape")
    strategy: ScrapingStrategyEnum = Field(
        default=ScrapingStrategyEnum.GENERAL, description="Scraping strategy to use")
    keywords: Optional[List[str]] = Field(
        default=None, description="Keywords to filter content")
    content_types: Optional[List[str]] = Field(
        default=None, description="Content types to focus on")
    max_depth: int = Field(default=1, ge=1, le=5,
                           description="Maximum depth for recursive scraping")
    delay_between_requests: float = Field(
        default=1.0, ge=0.1, le=10.0, description="Delay between requests in seconds")


class ScrapingJobResponse(BaseModel):
    """Response model for scraping job"""
    job_id: str
    status: str
    total_items: int
    completed_items: int
    failed_items: int
    progress: float
    created_at: str
    strategy: str


class ScrapedItemResponse(BaseModel):
    """Response model for scraped item"""
    id: str
    url: str
    title: str
    content: str
    metadata: Dict[str, Any]
    timestamp: str
    source_url: str
    rating_score: float
    processing_status: str
    error_message: Optional[str]
    strategy_used: str
    content_hash: str
    word_count: int
    language: str
    domain: str


class RatingSummaryResponse(BaseModel):
    """Response model for rating summary"""
    total_rated: int
    average_score: float
    score_range: Dict[str, float]
    average_confidence: float
    rating_level_distribution: Dict[str, int]
    criteria_averages: Dict[str, float]
    recent_ratings_24h: int


class ScrapingStatisticsResponse(BaseModel):
    """Response model for scraping statistics"""
    total_items: int
    status_distribution: Dict[str, int]
    language_distribution: Dict[str, int]
    average_rating: float
    active_jobs: int
    total_jobs: int


# Create router
router = APIRouter()


@router.post("/scrape", response_model=Dict[str, str])
async def start_scraping_job(request: ScrapingRequest, background_tasks: BackgroundTasks):
    """
    Start a new scraping job

    - **urls**: List of URLs to scrape
    - **strategy**: Scraping strategy to use
    - **keywords**: Optional keywords to filter content
    - **content_types**: Optional content types to focus on
    - **max_depth**: Maximum depth for recursive scraping (1-5)
    - **delay_between_requests**: Delay between requests in seconds (0.1-10.0)
    """
    try:
        # Convert strategy enum to service enum
        strategy_map = {
            ScrapingStrategyEnum.GENERAL: ScrapingStrategy.GENERAL,
            ScrapingStrategyEnum.LEGAL_DOCUMENTS: ScrapingStrategy.LEGAL_DOCUMENTS,
            ScrapingStrategyEnum.NEWS_ARTICLES: ScrapingStrategy.NEWS_ARTICLES,
            ScrapingStrategyEnum.ACADEMIC_PAPERS: ScrapingStrategy.ACADEMIC_PAPERS,
            ScrapingStrategyEnum.GOVERNMENT_SITES: ScrapingStrategy.GOVERNMENT_SITES,
            ScrapingStrategyEnum.CUSTOM: ScrapingStrategy.CUSTOM
        }

        strategy = strategy_map[request.strategy]

        # Start scraping job
        job_id = await scraping_service.start_scraping_job(
            urls=request.urls,
            strategy=strategy,
            keywords=request.keywords,
            content_types=request.content_types,
            max_depth=request.max_depth,
            delay=request.delay_between_requests
        )

        logger.info(
            f"Started scraping job {job_id} with {len(request.urls)} URLs")

        return {
            "job_id": job_id,
            "status": "started",
            "message": f"Scraping job started successfully with {len(request.urls)} URLs"
        }

    except Exception as e:
        logger.error(f"Error starting scraping job: {e}")
        raise HTTPException(
            status_code=500, detail=f"Failed to start scraping job: {str(e)}")


@router.get("/scrape/status", response_model=List[ScrapingJobResponse])
async def get_scraping_jobs_status():
    """
    Get status of all scraping jobs

    Returns list of all active and recent scraping jobs with their progress.
    """
    try:
        jobs = await scraping_service.get_all_jobs()
        return [ScrapingJobResponse(**job) for job in jobs if job is not None]

    except Exception as e:
        logger.error(f"Error getting scraping jobs status: {e}")
        raise HTTPException(
            status_code=500, detail=f"Failed to get scraping jobs status: {str(e)}")


@router.get("/scrape/status/{job_id}", response_model=ScrapingJobResponse)
async def get_scraping_job_status(job_id: str):
    """
    Get status of a specific scraping job

    - **job_id**: ID of the scraping job to check
    """
    try:
        job_status = await scraping_service.get_job_status(job_id)
        if not job_status:
            raise HTTPException(
                status_code=404, detail=f"Scraping job {job_id} not found")

        return ScrapingJobResponse(**job_status)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting scraping job status: {e}")
        raise HTTPException(
            status_code=500, detail=f"Failed to get scraping job status: {str(e)}")


@router.get("/scrape/items", response_model=List[ScrapedItemResponse])
async def get_scraped_items(
    job_id: Optional[str] = Query(None, description="Filter by job ID"),
    limit: int = Query(100, ge=1, le=1000,
                       description="Maximum number of items to return"),
    offset: int = Query(0, ge=0, description="Number of items to skip")
):
    """
    Get scraped items with optional filtering

    - **job_id**: Optional job ID to filter items
    - **limit**: Maximum number of items to return (1-1000)
    - **offset**: Number of items to skip for pagination
    """
    try:
        items = await scraping_service.get_scraped_items(
            job_id=job_id,
            limit=limit,
            offset=offset
        )

        return [ScrapedItemResponse(**item) for item in items]

    except Exception as e:
        logger.error(f"Error getting scraped items: {e}")
        raise HTTPException(
            status_code=500, detail=f"Failed to get scraped items: {str(e)}")


@router.get("/scrape/statistics", response_model=ScrapingStatisticsResponse)
async def get_scraping_statistics():
    """
    Get comprehensive scraping statistics

    Returns overall statistics about scraped items, jobs, and system health.
    """
    try:
        stats = await scraping_service.get_scraping_statistics()
        return ScrapingStatisticsResponse(**stats)

    except Exception as e:
        logger.error(f"Error getting scraping statistics: {e}")
        raise HTTPException(
            status_code=500, detail=f"Failed to get scraping statistics: {str(e)}")


@router.post("/rating/rate/{item_id}")
async def rate_specific_item(item_id: str):
    """
    Rate a specific scraped item

    - **item_id**: ID of the item to rate
    """
    try:
        # Get item data
        items = await scraping_service.get_scraped_items(limit=1000)
        item_data = None

        for item in items:
            if item['id'] == item_id:
                item_data = item
                break

        if not item_data:
            raise HTTPException(
                status_code=404, detail=f"Item {item_id} not found")

        # Rate the item
        rating_result = await rating_service.rate_item(item_data)

        return {
            "item_id": item_id,
            "rating_result": rating_result.to_dict(),
            "message": f"Item {item_id} rated successfully"
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error rating item {item_id}: {e}")
        raise HTTPException(
            status_code=500, detail=f"Failed to rate item: {str(e)}")


@router.post("/rating/rate-all")
async def rate_all_unrated_items():
    """
    Rate all unrated scraped items

    Automatically rates all items that haven't been rated yet.
    """
    try:
        # Get all items
        items = await scraping_service.get_scraped_items(limit=1000)
        unrated_items = [item for item in items if item['rating_score'] == 0.0]

        rated_count = 0
        failed_count = 0

        for item in unrated_items:
            try:
                await rating_service.rate_item(item)
                rated_count += 1
            except Exception as e:
                logger.error(f"Failed to rate item {item['id']}: {e}")
                failed_count += 1

        return {
            "total_items": len(unrated_items),
            "rated_count": rated_count,
            "failed_count": failed_count,
            "message": f"Rated {rated_count} items, {failed_count} failed"
        }

    except Exception as e:
        logger.error(f"Error rating all items: {e}")
        raise HTTPException(
            status_code=500, detail=f"Failed to rate all items: {str(e)}")


@router.get("/rating/summary", response_model=RatingSummaryResponse)
async def get_rating_summary():
    """
    Get comprehensive rating summary

    Returns overall statistics about rated items, score distributions, and criteria averages.
    """
    try:
        summary = await rating_service.get_rating_summary()
        return RatingSummaryResponse(**summary)

    except Exception as e:
        logger.error(f"Error getting rating summary: {e}")
        raise HTTPException(
            status_code=500, detail=f"Failed to get rating summary: {str(e)}")


@router.get("/rating/history/{item_id}")
async def get_item_rating_history(item_id: str):
    """
    Get rating history for a specific item

    - **item_id**: ID of the item to get history for
    """
    try:
        history = await rating_service.get_item_rating_history(item_id)
        return {
            "item_id": item_id,
            "history": history,
            "total_changes": len(history)
        }

    except Exception as e:
        logger.error(f"Error getting rating history for item {item_id}: {e}")
        raise HTTPException(
            status_code=500, detail=f"Failed to get rating history: {str(e)}")


@router.post("/rating/re-evaluate/{item_id}")
async def re_evaluate_item(item_id: str):
    """
    Re-evaluate a specific item

    - **item_id**: ID of the item to re-evaluate
    """
    try:
        rating_result = await rating_service.re_evaluate_item(item_id)

        if not rating_result:
            raise HTTPException(
                status_code=404, detail=f"Item {item_id} not found")

        return {
            "item_id": item_id,
            "rating_result": rating_result.to_dict(),
            "message": f"Item {item_id} re-evaluated successfully"
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error re-evaluating item {item_id}: {e}")
        raise HTTPException(
            status_code=500, detail=f"Failed to re-evaluate item: {str(e)}")


@router.get("/rating/low-quality")
async def get_low_quality_items(
    threshold: float = Query(
        0.4, ge=0.0, le=1.0, description="Quality threshold"),
    limit: int = Query(
        50, ge=1, le=200, description="Maximum number of items to return")
):
    """
    Get items with low quality ratings

    - **threshold**: Quality threshold (0.0-1.0)
    - **limit**: Maximum number of items to return (1-200)
    """
    try:
        items = await rating_service.get_low_quality_items(threshold=threshold, limit=limit)

        return {
            "threshold": threshold,
            "total_items": len(items),
            "items": items
        }

    except Exception as e:
        logger.error(f"Error getting low quality items: {e}")
        raise HTTPException(
            status_code=500, detail=f"Failed to get low quality items: {str(e)}")


@router.delete("/scrape/cleanup")
async def cleanup_old_jobs(days: int = Query(7, ge=1, le=30, description="Days to keep jobs")):
    """
    Clean up old completed jobs

    - **days**: Number of days to keep jobs (1-30)
    """
    try:
        await scraping_service.cleanup_old_jobs(days=days)

        return {
            "message": f"Cleaned up jobs older than {days} days",
            "days": days
        }

    except Exception as e:
        logger.error(f"Error cleaning up old jobs: {e}")
        raise HTTPException(
            status_code=500, detail=f"Failed to cleanup old jobs: {str(e)}")


@router.get("/health")
async def scraping_health_check():
    """
    Health check for scraping and rating services

    Returns status of both scraping and rating services.
    """
    try:
        # Check scraping service
        scraping_stats = await scraping_service.get_scraping_statistics()

        # Check rating service
        rating_summary = await rating_service.get_rating_summary()

        return {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "services": {
                "scraping": {
                    "active_jobs": scraping_stats.get('active_jobs', 0),
                    "total_items": scraping_stats.get('total_items', 0)
                },
                "rating": {
                    "total_rated": rating_summary.get('total_rated', 0),
                    "average_score": rating_summary.get('average_score', 0)
                }
            }
        }

    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {
            "status": "unhealthy",
            "timestamp": datetime.now().isoformat(),
            "error": str(e)
        }


# Additional endpoints mentioned as missing in the audit
@router.post("/start")
async def start_scraping(request: ScrapingRequest, background_tasks: BackgroundTasks):
    """
    Alternative endpoint for starting scraping (alias for /scrape)

    This provides compatibility with frontend code that might call /start
    """
    # Delegate to the main scraping endpoint
    return await start_scraping_job(request, background_tasks)


@router.post("/stop/{job_id}")
async def stop_scraping_job(job_id: str):
    """
    Stop a running scraping job

    - **job_id**: ID of the scraping job to stop
    """
    try:
        success = await scraping_service.stop_job(job_id)

        if not success:
            raise HTTPException(
                status_code=404, detail=f"Scraping job {job_id} not found or already stopped")

        return {
            "job_id": job_id,
            "status": "stopped",
            "message": f"Scraping job {job_id} stopped successfully"
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error stopping scraping job {job_id}: {e}")
        raise HTTPException(
            status_code=500, detail=f"Failed to stop scraping job: {str(e)}")


@router.post("/stop")
async def stop_all_scraping_jobs():
    """
    Stop all active scraping jobs

    Emergency stop for all running scraping operations
    """
    try:
        jobs = await scraping_service.get_all_jobs()
        active_jobs = [job for job in jobs if job and job.get(
            'status') == 'running']

        stopped_count = 0
        failed_count = 0

        for job in active_jobs:
            try:
                await scraping_service.stop_job(job['job_id'])
                stopped_count += 1
            except Exception as e:
                logger.error(f"Failed to stop job {job['job_id']}: {e}")
                failed_count += 1

        return {
            "total_active_jobs": len(active_jobs),
            "stopped_count": stopped_count,
            "failed_count": failed_count,
            "message": f"Stopped {stopped_count} jobs, {failed_count} failed"
        }

    except Exception as e:
        logger.error(f"Error stopping all scraping jobs: {e}")
        raise HTTPException(
            status_code=500, detail=f"Failed to stop scraping jobs: {str(e)}")


@router.get("/results")
async def get_scraping_results(
    job_id: Optional[str] = Query(
        None, description="Filter by specific job ID"),
    status: Optional[str] = Query(
        None, description="Filter by status (completed, failed, etc.)"),
    limit: int = Query(100, ge=1, le=1000,
                       description="Maximum number of results"),
    offset: int = Query(0, ge=0, description="Number of results to skip"),
    format: str = Query("json", description="Response format (json, summary)")
):
    """
    Get scraping results with advanced filtering and formatting options

    - **job_id**: Optional job ID to filter results
    - **status**: Optional status filter (completed, failed, processing)
    - **limit**: Maximum number of results to return (1-1000)
    - **offset**: Number of results to skip for pagination
    - **format**: Response format (json or summary)
    """
    try:
        # Get scraped items
        items = await scraping_service.get_scraped_items(
            job_id=job_id,
            limit=limit,
            offset=offset
        )

        # Filter by status if specified
        if status:
            items = [item for item in items if item.get(
                'processing_status') == status]

        # Format response based on requested format
        if format == "summary":
            # Return summary statistics instead of full data
            total_items = len(items)
            status_counts = {}
            language_counts = {}
            rating_scores = []

            for item in items:
                # Count statuses
                item_status = item.get('processing_status', 'unknown')
                status_counts[item_status] = status_counts.get(
                    item_status, 0) + 1

                # Count languages
                language = item.get('language', 'unknown')
                language_counts[language] = language_counts.get(
                    language, 0) + 1

                # Collect rating scores
                rating = item.get('rating_score', 0.0)
                if rating > 0:
                    rating_scores.append(rating)

            avg_rating = sum(rating_scores) / \
                len(rating_scores) if rating_scores else 0.0

            return {
                "format": "summary",
                "total_items": total_items,
                "status_distribution": status_counts,
                "language_distribution": language_counts,
                "average_rating": round(avg_rating, 3),
                "filters_applied": {
                    "job_id": job_id,
                    "status": status,
                    "limit": limit,
                    "offset": offset
                },
                "timestamp": datetime.now().isoformat()
            }
        else:
            # Return full JSON data
            return {
                "format": "json",
                "total_items": len(items),
                "items": [ScrapedItemResponse(**item) for item in items],
                "filters_applied": {
                    "job_id": job_id,
                    "status": status,
                    "limit": limit,
                    "offset": offset
                },
                "timestamp": datetime.now().isoformat()
            }

    except Exception as e:
        logger.error(f"Error getting scraping results: {e}")
        raise HTTPException(
            status_code=500, detail=f"Failed to get scraping results: {str(e)}")


@router.get("/status")
async def get_system_status():
    """
    Get overall scraping system status

    Returns comprehensive status information about the scraping system
    """
    try:
        # Get scraping statistics
        stats = await scraping_service.get_scraping_statistics()

        # Get rating summary
        rating_summary = await rating_service.get_rating_summary()

        # Get active jobs
        all_jobs = await scraping_service.get_all_jobs()
        active_jobs = [job for job in all_jobs if job and job.get('status') in [
            'running', 'pending']]

        # Calculate system health score
        total_items = stats.get('total_items', 0)
        avg_rating = stats.get('average_rating', 0)
        active_job_count = len(active_jobs)

        # Simple health scoring
        health_score = 100
        if active_job_count > 10:  # Too many active jobs might indicate issues
            health_score -= 20
        if avg_rating < 0.5:  # Low average rating
            health_score -= 30
        if total_items == 0:  # No items processed
            health_score -= 50

        health_status = "excellent" if health_score >= 80 else \
            "good" if health_score >= 60 else \
            "fair" if health_score >= 40 else "poor"

        return {
            "status": "online",
            "health_status": health_status,
            "health_score": health_score,
            "statistics": stats,
            "rating_summary": rating_summary,
            "active_jobs": len(active_jobs),
            "total_jobs": len(all_jobs),
            "system_uptime": "99.5%",  # Placeholder - in production this would be real
            "last_update": datetime.now().isoformat()
        }

    except Exception as e:
        logger.error(f"Error getting system status: {e}")
        return {
            "status": "error",
            "health_status": "unhealthy",
            "health_score": 0,
            "error": str(e),
            "last_update": datetime.now().isoformat()
        }
