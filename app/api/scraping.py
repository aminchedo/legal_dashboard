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
