#!/usr/bin/env python3
"""
Legal Dashboard FastAPI Main Application
========================================

Main FastAPI application with API routes and static file serving.
Enhanced with scraping and rating service integration.
"""

from .api import auth, reports
import os
import logging
import asyncio
from pathlib import Path
from contextlib import asynccontextmanager
from typing import Dict, List, Optional

from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect, BackgroundTasks
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware

# Import API routers
from .api import documents, ocr, dashboard, scraping, analytics, enhanced_analytics, websocket

# Import services for initialization
from .services.database_service import DatabaseManager
from .services.ocr_service import OCRPipeline
from .services.ai_service import AIScoringEngine
from .services.notification_service import notification_service
from .services.cache_service import cache_service
from .services.scraping_service import ScrapingService, ScrapingStrategy
from .services.rating_service import RatingService

# Import asyncio for background task management
import asyncio
from fastapi import BackgroundTasks

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Global service instances
db_manager = None
ocr_pipeline = None
ai_engine = None
scraping_service = None
rating_service = None

# Background task flags
background_scraping_running = False
background_rating_running = False

# Iranian Legal Sources Configuration - Enhanced with 10+ Sources
PERSIAN_LEGAL_SOURCES = [
    {
        "url": "https://www.mizanonline.ir",
        "name": "میزان آنلاین",
        "type": "news_legal",
        "strategy": ScrapingStrategy.LEGAL_DOCUMENTS,
        "priority": "high",
        "credibility": 0.9
    },
    {
        "url": "https://www.dotic.ir", 
        "name": "سامانه حقوقی دولت",
        "type": "government",
        "strategy": ScrapingStrategy.GOVERNMENT_SITES,
        "priority": "high",
        "credibility": 0.95
    },
    {
        "url": "https://rc.majlis.ir",
        "name": "مرکز پژوهش‌های مجلس", 
        "type": "research",
        "strategy": ScrapingStrategy.ACADEMIC_PAPERS,
        "priority": "high",
        "credibility": 0.9
    },
    {
        "url": "https://www.dadiran.ir",
        "name": "دادایران",
        "type": "judicial",
        "strategy": ScrapingStrategy.LEGAL_DOCUMENTS, 
        "priority": "medium",
        "credibility": 0.8
    },
    {
        "url": "https://www.lawdata.ir",
        "name": "بانک اطلاعات حقوقی",
        "type": "database",
        "strategy": ScrapingStrategy.LEGAL_DOCUMENTS,
        "priority": "high",
        "credibility": 0.85
    },
    {
        "url": "https://www.rrk.ir",
        "name": "مرکز تحقیقات راهبردی",
        "type": "research",
        "strategy": ScrapingStrategy.ACADEMIC_PAPERS,
        "priority": "medium",
        "credibility": 0.8
    },
    {
        "url": "https://www.lawbank.ir",
        "name": "بانک قوانین",
        "type": "legal_database", 
        "strategy": ScrapingStrategy.LEGAL_DOCUMENTS,
        "priority": "high",
        "credibility": 0.85
    },
    {
        "url": "https://www.ijlr.ir",
        "name": "مجله حقوق ایران",
        "type": "academic",
        "strategy": ScrapingStrategy.ACADEMIC_PAPERS,
        "priority": "medium",
        "credibility": 0.75
    },
    {
        "url": "https://www.hoghoogh.com",
        "name": "پایگاه حقوق",
        "type": "general_legal",
        "strategy": ScrapingStrategy.LEGAL_DOCUMENTS,
        "priority": "low",
        "credibility": 0.6
    },
    {
        "url": "https://www.qanoon.ir",
        "name": "قانون",
        "type": "legal_reference",
        "strategy": ScrapingStrategy.LEGAL_DOCUMENTS, 
        "priority": "medium",
        "credibility": 0.7
    },
    {
        "url": "https://www.irna.ir",
        "name": "خبرگزاری جمهوری اسلامی ایران",
        "type": "news_legal",
        "strategy": ScrapingStrategy.NEWS_ARTICLES,
        "priority": "high",
        "credibility": 0.9
    },
    {
        "url": "https://www.mehrnews.ir",
        "name": "خبرگزاری مهر",
        "type": "news_legal",
        "strategy": ScrapingStrategy.NEWS_ARTICLES,
        "priority": "medium",
        "credibility": 0.8
    },
    {
        "url": "https://www.tasnimnews.com",
        "name": "خبرگزاری تسنیم",
        "type": "news_legal",
        "strategy": ScrapingStrategy.NEWS_ARTICLES,
        "priority": "medium",
        "credibility": 0.8
    },
    {
        "url": "https://www.farsnews.ir",
        "name": "خبرگزاری فارس",
        "type": "news_legal",
        "strategy": ScrapingStrategy.NEWS_ARTICLES,
        "priority": "medium",
        "credibility": 0.8
    },
    {
        "url": "https://www.entekhab.ir",
        "name": "انتخاب",
        "type": "news_legal",
        "strategy": ScrapingStrategy.NEWS_ARTICLES,
        "priority": "low",
        "credibility": 0.7
    }
]

# Persian Legal Keywords for Content Filtering - Enhanced
PERSIAN_LEGAL_KEYWORDS = [
    # قوانین و مقررات
    "قانون", "مقررات", "دستورالعمل", "آیین‌نامه", "بخشنامه", "تصویب‌نامه",
    "لایحه", "مصوبه", "تبصره", "ماده", "فصل", "باب",
    
    # حقوق و قضایی
    "حقوق", "قضایی", "دادگاه", "وکیل", "قاضی", "دادستان",
    "شکایت", "دادخواست", "حکم", "رأی", "استیناف", "فرجام",
    "تجدید نظر", "اعتراض", "شکایت", "شکایت‌نامه",
    
    # حوزه‌های حقوقی
    "تجارت", "مدنی", "جزایی", "اداری", "مالیاتی", "کار",
    "تأمین اجتماعی", "بیمه", "مالکیت", "ارث", "طلاق", "ازدواج",
    "وصیت", "وقف", "شرکت", "سهام", "سرمایه", "سود", "زیان",
    
    # مجازات‌ها
    "جریمه", "حبس", "شلاق", "اعدام", "حبس تعزیری", "حبس تعلیقی",
    "مصادره", "توقیف", "تضمین", "رهن", "وام", "اجاره",
    
    # معاملات و قراردادها
    "فروش", "خرید", "معامله", "قرارداد", "عقد", "بیع",
    "اجاره", "رهن", "صلح", "هبه", "وصیت", "وقف",
    
    # نهادهای حقوقی
    "مجلس", "دولت", "وزارت", "استانداری", "شهرداری", "بانک",
    "بورس", "سازمان", "مؤسسه", "شرکت", "انجمن", "اتحادیه",
    
    # اصطلاحات حقوقی
    "مدعی", "مدعی‌علیه", "شاهد", "خبره", "کارشناس", "مأمور",
    "متصدی", "مسؤول", "متعهد", "متعهدله", "مؤجر", "مستأجر",
    
    # مراحل دادرسی
    "تحقیق", "رسیدگی", "دادرسی", "محاکمه", "محکومیت", "تبرئه",
    "صدور حکم", "اجرای حکم", "اعمال قانون", "تفسیر قانون",
    
    # اسناد و مدارک
    "سند", "مدرک", "گواهی", "تصدیق", "گواهی‌نامه", "پروانه",
    "مجوز", "جواز", "رأی", "حکم", "بخشنامه", "دستورالعمل"
]


async def start_background_scraping():
    """Background task for automatic scraping of Persian legal sources"""
    global background_scraping_running, scraping_service
    
    if background_scraping_running:
        logger.info("🔄 Background scraping already running")
        return
    
    background_scraping_running = True
    logger.info("🚀 Starting background scraping service...")
    
    try:
        # Wait 30 seconds for system initialization
        await asyncio.sleep(30)
        
        while background_scraping_running:
            try:
                logger.info("📡 Starting automatic scraping cycle...")
                
                # Process sources by priority
                high_priority_sources = [s for s in PERSIAN_LEGAL_SOURCES if s["priority"] == "high"]
                medium_priority_sources = [s for s in PERSIAN_LEGAL_SOURCES if s["priority"] == "medium"]
                low_priority_sources = [s for s in PERSIAN_LEGAL_SOURCES if s["priority"] == "low"]
                
                # Process high priority sources first
                for source in high_priority_sources:
                    if not background_scraping_running:
                        break
                    
                    try:
                        logger.info(f"🔍 Scraping {source['name']} ({source['url']}) - Credibility: {source.get('credibility', 0.5)}")
                        
                        # Create scraping job with Persian legal sources
                        job_id = await scraping_service.start_scraping_job(
                            urls=[source['url']],
                            strategy=source['strategy'],
                            keywords=PERSIAN_LEGAL_KEYWORDS,
                            delay=2.0,
                            max_depth=2,
                            content_types=["text/html", "application/pdf"]
                        )
                        
                        logger.info(f"✅ Scraping job started: {job_id}")
                        
                        # Wait between sources based on credibility
                        wait_time = 5 if source.get('credibility', 0.5) > 0.8 else 10
                        await asyncio.sleep(wait_time)
                        
                    except Exception as e:
                        logger.error(f"❌ Error scraping {source['name']}: {e}")
                        continue
                
                # Process medium priority sources
                for source in medium_priority_sources:
                    if not background_scraping_running:
                        break
                    
                    try:
                        logger.info(f"🔍 Scraping {source['name']} ({source['url']})")
                        
                        job_id = await scraping_service.start_scraping_job(
                            urls=[source['url']],
                            strategy=source['strategy'],
                            keywords=PERSIAN_LEGAL_KEYWORDS,
                            delay=3.0,
                            max_depth=1
                        )
                        
                        logger.info(f"✅ Scraping job started: {job_id}")
                        await asyncio.sleep(15)
                        
                    except Exception as e:
                        logger.error(f"❌ Error scraping {source['name']}: {e}")
                        continue
                
                # Process low priority sources (if time permits)
                if background_scraping_running:
                    for source in low_priority_sources[:3]:  # Limit to 3 low priority sources
                        if not background_scraping_running:
                            break
                        
                        try:
                            logger.info(f"🔍 Scraping {source['name']} ({source['url']})")
                            
                            job_id = await scraping_service.start_scraping_job(
                                urls=[source['url']],
                                strategy=source['strategy'],
                                keywords=PERSIAN_LEGAL_KEYWORDS,
                                delay=5.0,
                                max_depth=1
                            )
                            
                            logger.info(f"✅ Scraping job started: {job_id}")
                            await asyncio.sleep(20)
                            
                        except Exception as e:
                            logger.error(f"❌ Error scraping {source['name']}: {e}")
                            continue
                
                # Wait 5 minutes before next cycle
                logger.info("⏰ Waiting 5 minutes before next scraping cycle...")
                await asyncio.sleep(300)
                
            except Exception as e:
                logger.error(f"❌ Background scraping error: {e}")
                await asyncio.sleep(60)  # Wait 1 minute before retry
                
    except Exception as e:
        logger.error(f"❌ Fatal error in background scraping: {e}")
    finally:
        background_scraping_running = False
        logger.info("🛑 Background scraping stopped")


async def start_background_rating():
    """Background task for automatic rating of scraped items"""
    global background_rating_running, rating_service
    
    if background_rating_running:
        logger.info("🔄 Background rating already running")
        return
    
    background_rating_running = True
    logger.info("🚀 Starting background rating service...")
    
    try:
        # Wait 2 minutes for initial scraping
        await asyncio.sleep(120)
        
        while background_rating_running:
            try:
                logger.info("📊 Starting automatic rating cycle...")
                
                # Monitor for unrated items continuously
                unrated_items = await rating_service.get_unrated_items(limit=50)
                
                if unrated_items:
                    logger.info(f"📝 Found {len(unrated_items)} unrated items")
                    
                    # Process rating in batches
                    batch_size = 10
                    for i in range(0, len(unrated_items), batch_size):
                        if not background_rating_running:
                            break
                        
                        batch = unrated_items[i:i + batch_size]
                        logger.info(f"📦 Processing batch {i//batch_size + 1} ({len(batch)} items)")
                        
                        for item in batch:
                            if not background_rating_running:
                                break
                            
                            try:
                                # Rate the item with enhanced criteria
                                rating_result = await rating_service.rate_item(
                                    item_data=item,
                                    evaluator="auto_background"
                                )
                                
                                logger.info(f"✅ Rated item {item.get('id', 'unknown')}: {rating_result.overall_score:.2f} ({rating_result.rating_level.value})")
                                
                                # Small delay between ratings
                                await asyncio.sleep(0.5)
                                
                            except Exception as e:
                                logger.error(f"❌ Error rating item {item.get('id', 'unknown')}: {e}")
                                continue
                        
                        # Wait between batches
                        if background_rating_running:
                            await asyncio.sleep(2)
                else:
                    logger.info("📭 No unrated items found")
                
                # Loop every 5 minutes
                logger.info("⏰ Waiting 5 minutes before next rating cycle...")
                await asyncio.sleep(300)
                
            except Exception as e:
                logger.error(f"❌ Background rating error: {e}")
                await asyncio.sleep(60)  # Wait 1 minute before retry
                
    except Exception as e:
        logger.error(f"❌ Fatal error in background rating: {e}")
    finally:
        background_rating_running = False
        logger.info("🛑 Background rating stopped")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager with enhanced service integration"""
    global db_manager, ocr_pipeline, ai_engine, scraping_service, rating_service

    try:
        logger.info("🚀 Starting Legal Dashboard...")

        # Initialize services
        logger.info("📦 Initializing services...")

        # Database
        db_manager = DatabaseManager()
        db_manager.initialize()
        logger.info("✅ Database initialized")

        # OCR Pipeline
        ocr_pipeline = OCRPipeline()
        ocr_pipeline.initialize()
        logger.info("✅ OCR Pipeline initialized")

        # AI Engine
        ai_engine = AIScoringEngine()
        logger.info("✅ AI Engine initialized")

        # Scraping Service
        scraping_service = ScrapingService(db_path="legal_documents.db")
        logger.info("✅ Scraping Service initialized")

        # Rating Service
        rating_service = RatingService(db_path="legal_documents.db")
        logger.info("✅ Rating Service initialized")

        # Create required directories
        os.makedirs("/tmp/uploads", exist_ok=True)
        os.makedirs("/tmp/data", exist_ok=True)

        logger.info("🎉 All services initialized successfully!")

        # Start background tasks
        logger.info("🔄 Starting background tasks...")
        asyncio.create_task(start_background_scraping())
        asyncio.create_task(start_background_rating())
        logger.info("✅ Background tasks started")

        yield  # Application runs here

    except Exception as e:
        logger.error(f"❌ Initialization failed: {e}")
        raise
    finally:
        logger.info("🔄 Shutting down Legal Dashboard...")
        
        # Stop background tasks
        global background_scraping_running, background_rating_running
        background_scraping_running = False
        background_rating_running = False
        
        # Close services
        if scraping_service:
            await scraping_service.close_session()
        logger.info("✅ Services cleaned up")

# Create FastAPI application
app = FastAPI(
    title="Legal Dashboard API",
    description="AI-powered Persian legal document processing system",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    lifespan=lifespan
)

# Add middlewares
app.add_middleware(GZipMiddleware, minimum_size=1000)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure properly in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routers
app.include_router(
    documents.router, prefix="/api/documents", tags=["Documents"])
app.include_router(ocr.router, prefix="/api/ocr", tags=["OCR"])
app.include_router(
    dashboard.router, prefix="/api/dashboard", tags=["Dashboard"])
app.include_router(scraping.router, prefix="/api/scraping", tags=["Scraping"])
app.include_router(
    analytics.router, prefix="/api/analytics", tags=["Analytics"])
app.include_router(
    enhanced_analytics.router, prefix="/api/enhanced-analytics", tags=["Enhanced Analytics"])
app.include_router(
    websocket.router, prefix="", tags=["WebSocket"])

# Import and include new routers
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(reports.router, prefix="/api/reports",
                   tags=["Reports & Analytics"])

# Serve static files (Frontend)
frontend_dir = Path(__file__).parent.parent / "frontend"
if frontend_dir.exists():
    app.mount("/static", StaticFiles(directory=str(frontend_dir)), name="static")
    logger.info(f"📁 Static files mounted from: {frontend_dir}")
else:
    logger.warning("⚠️ Frontend directory not found")

# Root route - serve main dashboard
@app.get("/", response_class=HTMLResponse, include_in_schema=False)
async def read_root():
    """Serve main dashboard page"""
    try:
        html_file = frontend_dir / "index.html"
        if html_file.exists():
            return FileResponse(html_file, media_type="text/html")
        else:
            return HTMLResponse("""
            <html>
                <head><title>Legal Dashboard</title></head>
                <body>
                    <h1>🏛️ Legal Dashboard API</h1>
                    <p>Backend is running! Frontend files not found.</p>
                    <p><a href="/api/docs">📖 API Documentation</a></p>
                </body>
            </html>
            """)
    except Exception as e:
        logger.error(f"Error serving root: {e}")
        raise HTTPException(status_code=500, detail="Error serving homepage")

# Enhanced health check endpoint
@app.get("/api/health")
async def health_check():
    """Comprehensive system health check with detailed monitoring"""
    try:
        # Check database connection status
        db_healthy = db_manager.is_connected() if db_manager else False
        db_stats = {}
        if db_manager:
            try:
                db_stats = db_manager.get_statistics()
            except Exception as e:
                logger.error(f"Error getting database stats: {e}")

        # Check scraping service availability
        scraping_healthy = scraping_service is not None
        scraping_stats = {}
        if scraping_service:
            try:
                scraping_stats = await scraping_service.get_scraping_statistics()
            except Exception as e:
                logger.error(f"Error getting scraping stats: {e}")

        # Verify rating service functionality
        rating_healthy = rating_service is not None
        rating_stats = {}
        if rating_service:
            try:
                rating_stats = await rating_service.get_rating_summary()
            except Exception as e:
                logger.error(f"Error getting rating stats: {e}")

        # Report cache service status
        cache_healthy = cache_service is not None
        cache_stats = {}
        if cache_service:
            try:
                cache_stats = cache_service.get_statistics()
            except Exception as e:
                logger.error(f"Error getting cache stats: {e}")

        # Include WebSocket connection count
        websocket_connections = 0
        try:
            # This would need to be implemented in the WebSocket service
            websocket_connections = 0  # Placeholder
        except Exception as e:
            logger.error(f"Error getting WebSocket stats: {e}")

        # Check OCR pipeline
        ocr_healthy = ocr_pipeline.initialized if ocr_pipeline else False

        # Check background tasks
        background_tasks_healthy = background_scraping_running and background_rating_running

        # Provide comprehensive system statistics
        overall_healthy = all([
            db_healthy, 
            scraping_healthy, 
            rating_healthy, 
            cache_healthy, 
            ocr_healthy
        ])

        return {
            "status": "healthy" if overall_healthy else "unhealthy",
            "timestamp": "2024-01-01T00:00:00Z",
            "version": "1.0.0",
            "services": {
                "database": {
                    "status": "healthy" if db_healthy else "unhealthy",
                    "statistics": db_stats
                },
                "scraping": {
                    "status": "healthy" if scraping_healthy else "unhealthy",
                    "statistics": scraping_stats
                },
                "rating": {
                    "status": "healthy" if rating_healthy else "unhealthy",
                    "statistics": rating_stats
                },
                "cache": {
                    "status": "healthy" if cache_healthy else "unhealthy",
                    "statistics": cache_stats
                },
                "ocr": {
                    "status": "healthy" if ocr_healthy else "unhealthy"
                },
                "background_tasks": {
                    "status": "running" if background_tasks_healthy else "stopped",
                    "scraping": background_scraping_running,
                    "rating": background_rating_running
                },
                "websocket": {
                    "connections": websocket_connections
                }
            },
            "performance": {
                "memory_usage": "monitored",  # Would need actual implementation
                "cpu_usage": "monitored",      # Would need actual implementation
                "response_time": "optimized"   # Would need actual implementation
            }
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": "2024-01-01T00:00:00Z"
        }

# New system management endpoints
@app.post("/api/system/start-scraping")
async def start_manual_scraping(background_tasks: BackgroundTasks):
    """Manually trigger scraping process"""
    try:
        if not scraping_service:
            raise HTTPException(status_code=503, detail="Scraping service not available")
        
        # Start scraping in background
        background_tasks.add_task(start_background_scraping)
        
        return {
            "message": "Scraping process started",
            "status": "success"
        }
    except Exception as e:
        logger.error(f"Error starting manual scraping: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/system/start-rating")
async def start_manual_rating(background_tasks: BackgroundTasks):
    """Manually trigger rating process"""
    try:
        if not rating_service:
            raise HTTPException(status_code=503, detail="Rating service not available")
        
        # Start rating in background
        background_tasks.add_task(start_background_rating)
        
        return {
            "message": "Rating process started",
            "status": "success"
        }
    except Exception as e:
        logger.error(f"Error starting manual rating: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/system/status")
async def get_system_status():
    """Get comprehensive system status"""
    try:
        # Get scraping status
        scraping_status = {}
        if scraping_service:
            try:
                jobs = await scraping_service.get_all_jobs()
                scraping_status = {
                    "active_jobs": len([j for j in jobs if j.get("status") == "running"]),
                    "total_jobs": len(jobs),
                    "background_running": background_scraping_running
                }
            except Exception as e:
                scraping_status = {"error": str(e)}

        # Get rating status
        rating_status = {}
        if rating_service:
            try:
                summary = await rating_service.get_rating_summary()
                rating_status = {
                    "total_rated": summary.get("total_rated", 0),
                    "average_score": summary.get("average_score", 0),
                    "background_running": background_rating_running
                }
            except Exception as e:
                rating_status = {"error": str(e)}

        return {
            "system": {
                "status": "operational",
                "version": "1.0.0",
                "uptime": "running"
            },
            "scraping": scraping_status,
            "rating": rating_status,
            "background_tasks": {
                "scraping": background_scraping_running,
                "rating": background_rating_running
            }
        }
    except Exception as e:
        logger.error(f"Error getting system status: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/system/statistics")
async def get_system_statistics():
    """Get detailed system performance metrics"""
    try:
        stats = {}
        
        # Scraping statistics
        if scraping_service:
            try:
                scraping_stats = await scraping_service.get_scraping_statistics()
                stats["scraping"] = scraping_stats
            except Exception as e:
                stats["scraping"] = {"error": str(e)}

        # Rating statistics
        if rating_service:
            try:
                rating_stats = await rating_service.get_rating_summary()
                stats["rating"] = rating_stats
            except Exception as e:
                stats["rating"] = {"error": str(e)}

        # Database statistics
        if db_manager:
            try:
                db_stats = db_manager.get_statistics()
                stats["database"] = db_stats
            except Exception as e:
                stats["database"] = {"error": str(e)}

        return {
            "timestamp": "2024-01-01T00:00:00Z",
            "statistics": stats
        }
    except Exception as e:
        logger.error(f"Error getting system statistics: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Error handlers
@app.exception_handler(404)
async def not_found_handler(request, exc):
    """Custom 404 handler"""
    return HTMLResponse("""
    <html>
        <head><title>404 - صفحه یافت نشد</title></head>
        <body style="font-family: 'Tahoma', sans-serif; text-align: center; padding: 50px;">
            <h1>🔍 صفحه یافت نشد</h1>
            <p>صفحه مورد نظر شما وجود ندارد.</p>
            <a href="/">🏠 بازگشت به صفحه اصلی</a>
        </body>
    </html>
    """, status_code=404)

@app.exception_handler(500)
async def internal_error_handler(request, exc):
    """Custom 500 handler"""
    logger.error(f"Internal server error: {exc}")
    return HTMLResponse("""
    <html>
        <head><title>500 - خطای سرور</title></head>
        <body style="font-family: 'Tahoma', sans-serif; text-align: center; padding: 50px;">
            <h1>⚠️ خطای سرور</h1>
            <p>متأسفانه خطایی در سرور رخ داده است.</p>
            <a href="/">🏠 بازگشت به صفحه اصلی</a>
        </body>
    </html>
    """, status_code=500)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
