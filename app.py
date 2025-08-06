#!/usr/bin/env python3
"""
Hugging Face Spaces Entry Point
===============================

Entry point for Hugging Face Spaces deployment with proper environment
configuration and error handling for the Legal Dashboard system.
"""

import os
import sys
import logging
import uvicorn
from pathlib import Path

# Configure environment variables for HF Spaces
REQUIRED_ENV_VARS = {
    'ENVIRONMENT': 'production',
    'LOG_LEVEL': 'INFO', 
    'DATABASE_DIR': '/app/data',
    'TRANSFORMERS_CACHE': '/app/cache',
    'HF_HOME': '/app/cache',
    'PORT': '7860'
}

# Set environment variables if not already set
for key, default_value in REQUIRED_ENV_VARS.items():
    if key not in os.environ:
        os.environ[key] = default_value

# Configure logging
logging.basicConfig(
    level=getattr(logging, os.environ.get('LOG_LEVEL', 'INFO')),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('/tmp/legal_dashboard.log')
    ]
)

logger = logging.getLogger(__name__)

# Create required directories
os.makedirs('/app/data', exist_ok=True)
os.makedirs('/app/cache', exist_ok=True)
os.makedirs('/tmp/uploads', exist_ok=True)

logger.info("🚀 Starting Legal Dashboard for Hugging Face Spaces...")
logger.info(f"📁 Data directory: {os.environ.get('DATABASE_DIR', '/app/data')}")
logger.info(f"💾 Cache directory: {os.environ.get('TRANSFORMERS_CACHE', '/app/cache')}")

try:
    # Import FastAPI application
    from fastapi import FastAPI
    from fastapi.middleware.cors import CORSMiddleware
    
    # Try to import the main application
    try:
        from app.main import app as core_app
        logger.info("✅ Successfully imported main application")
    except ImportError as e:
        logger.error(f"❌ Failed to import main application: {e}")
        # Create a fallback app
        core_app = FastAPI(
            title="Legal Dashboard - Fallback",
            description="Legal document processing system (fallback mode)",
            version="1.0.0"
        )
        
        @core_app.get("/")
        async def fallback_root():
            return {
                "message": "Legal Dashboard is starting up...",
                "status": "initializing",
                "error": str(e)
            }
        
        @core_app.get("/health")
        async def fallback_health():
            return {
                "status": "starting",
                "message": "System is initializing, please wait..."
            }

    # Create the main application
    app = FastAPI(
        title="Legal Dashboard - Iranian Legal Documents",
        description="AI-powered Persian legal document processing and analysis system",
        version="1.0.0",
        docs_url="/docs",
        redoc_url="/redoc"
    )

    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Mount the core application
    app.mount("/", core_app)

    logger.info("✅ Application configured successfully")

except Exception as e:
    logger.error(f"❌ Critical error during application setup: {e}")
    
    # Create emergency app
    from fastapi import FastAPI, HTTPException
    from fastapi.responses import HTMLResponse
    
    app = FastAPI(
        title="Legal Dashboard - Emergency Mode",
        description="System is in emergency mode due to initialization errors",
        version="1.0.0"
    )
    
    @app.get("/")
    async def emergency_root():
        return HTMLResponse("""
        <html>
            <head><title>Legal Dashboard - خطای سیستم</title></head>
            <body style="font-family: 'Tahoma', sans-serif; text-align: center; padding: 50px;">
                <h1>⚠️ خطای سیستم</h1>
                <p>متأسفانه خطایی در راه‌اندازی سیستم رخ داده است.</p>
                <p>لطفاً چند لحظه صبر کنید و دوباره تلاش کنید.</p>
                <p>Error: """ + str(e) + """</p>
            </body>
        </html>
        """)
    
    @app.get("/health")
    async def emergency_health():
        raise HTTPException(status_code=503, detail="System is in emergency mode")

# Main execution
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 7860))
    host = "0.0.0.0"
    
    logger.info(f"🌐 Starting server on {host}:{port}")
    logger.info("📖 API Documentation available at /docs")
    logger.info("🔍 Health check available at /health")
    
    try:
        uvicorn.run(
            app,
            host=host,
            port=port,
            log_level=os.environ.get('LOG_LEVEL', 'info').lower(),
            access_log=True,
            reload=False  # Disable reload for production
        )
    except Exception as e:
        logger.error(f"❌ Failed to start server: {e}")
        sys.exit(1)
