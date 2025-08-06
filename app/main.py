#!/usr/bin/env python3
"""
Legal Dashboard FastAPI Main Application
========================================

Production-ready FastAPI application for Hugging Face Spaces deployment.
"""

import os
import logging
import sqlite3
from pathlib import Path
from contextlib import asynccontextmanager
from typing import List, Dict, Any

from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from pydantic import BaseModel
import uvicorn

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Global variables
UPLOAD_DIR = Path("/app/uploads")
DATA_DIR = Path("/app/data")
CACHE_DIR = Path("/app/cache")
LOGS_DIR = Path("/app/logs")
DATABASE_PATH = DATA_DIR / "legal_dashboard.db"

# Pydantic models
class HealthResponse(BaseModel):
    status: str
    services: Dict[str, str]
    version: str

class ReportResponse(BaseModel):
    id: str
    filename: str
    status: str
    created_at: str
    analysis_results: Dict[str, Any] = {}

class UploadResponse(BaseModel):
    filename: str
    status: str
    message: str

# Database initialization
def init_database():
    """Initialize SQLite database with required tables"""
    try:
        os.makedirs(DATA_DIR, exist_ok=True)
        
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        
        # Create reports table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS reports (
                id TEXT PRIMARY KEY,
                filename TEXT NOT NULL,
                file_path TEXT NOT NULL,
                status TEXT DEFAULT 'uploaded',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                analysis_results TEXT DEFAULT '{}'
            )
        ''')
        
        # Create documents table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS documents (
                id TEXT PRIMARY KEY,
                filename TEXT NOT NULL,
                content TEXT,
                status TEXT DEFAULT 'processed',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
        logger.info("✅ Database initialized successfully")
        
    except Exception as e:
        logger.error(f"❌ Database initialization failed: {e}")
        raise

# File processing functions
def extract_text_from_pdf(file_path: Path) -> str:
    """Extract text from PDF using PyPDF2"""
    try:
        import PyPDF2
        with open(file_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"
        return text.strip()
    except Exception as e:
        logger.error(f"PDF text extraction failed: {e}")
        return ""

def extract_text_from_txt(file_path: Path) -> str:
    """Extract text from TXT file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read().strip()
    except Exception as e:
        logger.error(f"TXT text extraction failed: {e}")
        return ""

def analyze_document_content(content: str) -> Dict[str, Any]:
    """Simple document analysis"""
    try:
        words = content.split()
        sentences = content.split('.')
        
        analysis = {
            "word_count": len(words),
            "sentence_count": len(sentences),
            "avg_sentence_length": len(words) / len(sentences) if sentences else 0,
            "language": "Persian" if any('\u0600' <= char <= '\u06FF' for char in content) else "English",
            "has_legal_terms": any(term in content.lower() for term in ['قانون', 'ماده', 'حقوق', 'قضایی', 'law', 'legal', 'court']),
            "document_type": "legal" if any(term in content.lower() for term in ['قانون', 'ماده', 'حقوق', 'قضایی', 'law', 'legal', 'court']) else "general"
        }
        
        return analysis
    except Exception as e:
        logger.error(f"Document analysis failed: {e}")
        return {"error": "Analysis failed"}

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    try:
        logger.info("🚀 Starting Legal Dashboard...")
        
        # Create required directories
        for directory in [UPLOAD_DIR, DATA_DIR, CACHE_DIR, LOGS_DIR]:
            os.makedirs(directory, exist_ok=True)
            logger.info(f"📁 Created directory: {directory}")
        
        # Initialize database
        init_database()
        
        logger.info("🎉 Legal Dashboard initialized successfully!")
        
        yield  # Application runs here
        
    except Exception as e:
        logger.error(f"❌ Initialization failed: {e}")
        raise
    finally:
        logger.info("🔄 Shutting down Legal Dashboard...")

# Create FastAPI application
app = FastAPI(
    title="Legal Dashboard API",
    description="AI-powered legal document processing system",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    lifespan=lifespan
)

# Add middlewares
app.add_middleware(GZipMiddleware, minimum_size=1000)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API Routes
@app.get("/api/health", response_model=HealthResponse)
async def health_check():
    """System health check"""
    try:
        # Check database
        db_healthy = DATABASE_PATH.exists()
        
        # Check upload directory
        upload_healthy = UPLOAD_DIR.exists()
        
        return HealthResponse(
            status="healthy" if db_healthy and upload_healthy else "unhealthy",
            services={
                "database": "healthy" if db_healthy else "unhealthy",
                "uploads": "healthy" if upload_healthy else "unhealthy",
                "api": "healthy"
            },
            version="1.0.0"
        )
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return HealthResponse(
            status="unhealthy",
            services={"error": str(e)},
            version="1.0.0"
        )

@app.post("/api/upload", response_model=UploadResponse)
async def upload_document(
    file: UploadFile = File(...),
    description: str = Form("")
):
    """Upload and process document"""
    try:
        # Validate file type
        if not file.filename:
            raise HTTPException(status_code=400, detail="No file provided")
        
        allowed_extensions = {'.pdf', '.txt'}
        file_ext = Path(file.filename).suffix.lower()
        
        if file_ext not in allowed_extensions:
            raise HTTPException(
                status_code=400, 
                detail=f"File type not supported. Allowed: {', '.join(allowed_extensions)}"
            )
        
        # Save file
        file_path = UPLOAD_DIR / file.filename
        with open(file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        
        # Extract text based on file type
        if file_ext == '.pdf':
            text_content = extract_text_from_pdf(file_path)
        else:  # .txt
            text_content = extract_text_from_txt(file_path)
        
        # Analyze content
        analysis = analyze_document_content(text_content)
        
        # Save to database
        import uuid
        import json
        from datetime import datetime
        
        report_id = str(uuid.uuid4())
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO reports (id, filename, file_path, status, analysis_results)
            VALUES (?, ?, ?, ?, ?)
        ''', (report_id, file.filename, str(file_path), 'processed', json.dumps(analysis)))
        
        # Save document content
        doc_id = str(uuid.uuid4())
        cursor.execute('''
            INSERT INTO documents (id, filename, content, status)
            VALUES (?, ?, ?, ?)
        ''', (doc_id, file.filename, text_content, 'processed'))
        
        conn.commit()
        conn.close()
        
        logger.info(f"✅ File uploaded and processed: {file.filename}")
        
        return UploadResponse(
            filename=file.filename,
            status="success",
            message="Document uploaded and processed successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Upload failed: {e}")
        raise HTTPException(status_code=500, detail="Upload failed")

@app.get("/api/reports", response_model=List[ReportResponse])
async def get_reports():
    """Get all processed reports"""
    try:
        import json
        from datetime import datetime
        
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, filename, status, created_at, analysis_results
            FROM reports
            ORDER BY created_at DESC
        ''')
        
        reports = []
        for row in cursor.fetchall():
            report_id, filename, status, created_at, analysis_results = row
            
            # Parse analysis results
            try:
                analysis = json.loads(analysis_results) if analysis_results else {}
            except:
                analysis = {}
            
            reports.append(ReportResponse(
                id=report_id,
                filename=filename,
                status=status,
                created_at=created_at,
                analysis_results=analysis
            ))
        
        conn.close()
        return reports
        
    except Exception as e:
        logger.error(f"Failed to get reports: {e}")
        raise HTTPException(status_code=500, detail="Failed to get reports")

@app.delete("/api/clear")
async def clear_all_data():
    """Clear all uploaded files and reset database"""
    try:
        # Clear upload directory
        for file_path in UPLOAD_DIR.glob("*"):
            if file_path.is_file():
                file_path.unlink()
        
        # Reset database
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        
        cursor.execute("DELETE FROM reports")
        cursor.execute("DELETE FROM documents")
        
        conn.commit()
        conn.close()
        
        logger.info("✅ All data cleared successfully")
        
        return {"message": "All data cleared successfully"}
        
    except Exception as e:
        logger.error(f"Failed to clear data: {e}")
        raise HTTPException(status_code=500, detail="Failed to clear data")

# Serve static files
frontend_dir = Path(__file__).parent.parent / "frontend"
if frontend_dir.exists():
    app.mount("/static", StaticFiles(directory=str(frontend_dir)), name="static")
    logger.info(f"📁 Static files mounted from: {frontend_dir}")

# Root route - serve main dashboard
@app.get("/", response_class=HTMLResponse)
async def read_root():
    """Serve main dashboard page"""
    try:
        html_file = frontend_dir / "index.html"
        if html_file.exists():
            return FileResponse(html_file, media_type="text/html")
        else:
            return HTMLResponse("""
            <html>
                <head>
                    <title>Legal Dashboard</title>
                    <meta charset="UTF-8">
                    <meta name="viewport" content="width=device-width, initial-scale=1.0">
                    <style>
                        body { font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }
                        .container { max-width: 800px; margin: 0 auto; background: white; padding: 40px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
                        h1 { color: #333; text-align: center; }
                        .status { padding: 20px; margin: 20px 0; border-radius: 5px; }
                        .healthy { background: #d4edda; color: #155724; }
                        .unhealthy { background: #f8d7da; color: #721c24; }
                        .api-link { text-align: center; margin: 20px 0; }
                        .api-link a { color: #007bff; text-decoration: none; }
                    </style>
                </head>
                <body>
                    <div class="container">
                        <h1>🏛️ Legal Dashboard API</h1>
                        <p>Backend is running! Frontend files not found.</p>
                        <div class="api-link">
                            <a href="/api/docs">📖 API Documentation</a>
                        </div>
                        <div class="api-link">
                            <a href="/api/health">🔍 Health Check</a>
                        </div>
                    </div>
                </body>
            </html>
            """)
    except Exception as e:
        logger.error(f"Error serving root: {e}")
        raise HTTPException(status_code=500, detail="Error serving homepage")

# Error handlers
@app.exception_handler(404)
async def not_found_handler(request, exc):
    """Custom 404 handler"""
    return HTMLResponse("""
    <html>
        <head><title>404 - Page Not Found</title></head>
        <body style="font-family: Arial, sans-serif; text-align: center; padding: 50px;">
            <h1>🔍 Page Not Found</h1>
            <p>The requested page was not found.</p>
            <a href="/">🏠 Back to Home</a>
        </body>
    </html>
    """, status_code=404)

@app.exception_handler(500)
async def internal_error_handler(request, exc):
    """Custom 500 handler"""
    logger.error(f"Internal server error: {exc}")
    return HTMLResponse("""
    <html>
        <head><title>500 - Server Error</title></head>
        <body style="font-family: Arial, sans-serif; text-align: center; padding: 50px;">
            <h1>⚠️ Server Error</h1>
            <p>An internal server error occurred.</p>
            <a href="/">🏠 Back to Home</a>
        </body>
    </html>
    """, status_code=500)

if __name__ == "__main__":
    # Use PORT from environment for Hugging Face Spaces
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port, workers=1)
