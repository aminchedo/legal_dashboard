#!/usr/bin/env python3
"""
Legal Dashboard FastAPI Main Application
========================================

Main FastAPI application with API routes and static file serving.
"""

from .api import auth, reports
import os
import logging
from pathlib import Path
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
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


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    global db_manager, ocr_pipeline, ai_engine

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

        # Create required directories
        os.makedirs("/tmp/uploads", exist_ok=True)
        os.makedirs("/tmp/data", exist_ok=True)

        logger.info("🎉 All services initialized successfully!")

        yield  # Application runs here

    except Exception as e:
        logger.error(f"❌ Initialization failed: {e}")
        raise
    finally:
        logger.info("🔄 Shutting down Legal Dashboard...")

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

# Health check endpoint


@app.get("/api/health")
async def health_check():
    """System health check"""
    try:
        # Check database connection
        db_healthy = db_manager.is_connected() if db_manager else False

        # Check OCR pipeline
        ocr_healthy = ocr_pipeline.initialized if ocr_pipeline else False

        return {
            "status": "healthy" if db_healthy and ocr_healthy else "unhealthy",
            "services": {
                "database": "healthy" if db_healthy else "unhealthy",
                "ocr": "healthy" if ocr_healthy else "unhealthy",
                "ai": "healthy" if ai_engine else "unhealthy"
            },
            "version": "1.0.0"
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {
            "status": "unhealthy",
            "error": str(e)
        }

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
