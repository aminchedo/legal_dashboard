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
    'PORT': '7860',
    'JWT_SECRET_KEY': 'your-super-secret-key-here',
    'CORS_ORIGINS': '*',
    'MAX_UPLOAD_SIZE': '50MB',
    'UPLOAD_DIR': '/tmp/uploads',
    'CACHE_TTL': '3600'
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

logger.info("🚀 شروع سیستم داشبورد حقوقی برای Hugging Face Spaces...")
logger.info(f"📁 مسیر داده‌ها: {os.environ.get('DATABASE_DIR', '/app/data')}")
logger.info(f"💾 مسیر کش: {os.environ.get('TRANSFORMERS_CACHE', '/app/cache')}")
logger.info(f"🌐 پورت: {os.environ.get('PORT', '7860')}")
logger.info(f"🔧 محیط: {os.environ.get('ENVIRONMENT', 'production')}")

try:
    # Import FastAPI application
    from fastapi import FastAPI
    from fastapi.middleware.cors import CORSMiddleware
    
    # Try to import the main application
    try:
        from app.main import app as core_app
        logger.info("✅ برنامه اصلی با موفقیت وارد شد")
    except ImportError as e:
        logger.error(f"❌ خطا در وارد کردن برنامه اصلی: {e}")
        # Create a fallback app
        core_app = FastAPI(
            title="داشبورد حقوقی - حالت پشتیبان",
            description="سیستم پردازش اسناد حقوقی (حالت پشتیبان)",
            version="1.0.0"
        )
        
        @core_app.get("/")
        async def fallback_root():
            return {
                "message": "داشبورد حقوقی در حال راه‌اندازی است...",
                "status": "initializing",
                "error": str(e)
            }
        
        @core_app.get("/health")
        async def fallback_health():
            return {
                "status": "starting",
                "message": "سیستم در حال راه‌اندازی است، لطفاً صبر کنید..."
            }

    # Create the main application
    app = FastAPI(
        title="داشبورد حقوقی - اسناد حقوقی ایران",
        description="سیستم پردازش و تحلیل اسناد حقوقی فارسی با هوش مصنوعی",
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

    logger.info("✅ برنامه با موفقیت پیکربندی شد")

except Exception as e:
    logger.error(f"❌ خطای بحرانی در راه‌اندازی برنامه: {e}")
    
    # Create emergency app
    from fastapi import FastAPI, HTTPException
    from fastapi.responses import HTMLResponse
    
    app = FastAPI(
        title="داشبورد حقوقی - حالت اضطراری",
        description="سیستم در حالت اضطراری به دلیل خطاهای راه‌اندازی",
        version="1.0.0"
    )
    
    @app.get("/")
    async def emergency_root():
        return HTMLResponse("""
        <html>
            <head><title>داشبورد حقوقی - خطای سیستم</title></head>
            <body style="font-family: 'Tahoma', sans-serif; text-align: center; padding: 50px; direction: rtl;">
                <h1>⚠️ خطای سیستم</h1>
                <p>متأسفانه خطایی در راه‌اندازی سیستم رخ داده است.</p>
                <p>لطفاً چند لحظه صبر کنید و دوباره تلاش کنید.</p>
                <p>خطا: """ + str(e) + """</p>
                <p><a href="/health">🔍 بررسی وضعیت سیستم</a></p>
            </body>
        </html>
        """)
    
    @app.get("/health")
    async def emergency_health():
        raise HTTPException(status_code=503, detail="سیستم در حالت اضطراری است")

# Main execution
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 7860))
    host = "0.0.0.0"
    
    logger.info(f"🌐 شروع سرور روی {host}:{port}")
    logger.info("📖 مستندات API در دسترس در /docs")
    logger.info("🔍 بررسی وضعیت در دسترس در /health")
    logger.info("🚀 سیستم آماده استفاده است!")
    
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
        logger.error(f"❌ خطا در شروع سرور: {e}")
        sys.exit(1)
