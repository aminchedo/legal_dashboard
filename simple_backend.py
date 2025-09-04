#!/usr/bin/env python3
"""
Simple Legal Dashboard Backend
==============================
Minimal FastAPI backend to serve the frontend with essential endpoints.
"""

from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, FileResponse
from pathlib import Path
import uvicorn
import json
import uuid
import time
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import os

# Create FastAPI app
app = FastAPI(
    title="Legal Dashboard API",
    description="AI-powered Persian legal document processing system",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["*"]
)

# Create upload directory
UPLOAD_DIR = Path("/tmp/uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

# In-memory storage for demo
documents_db = []
upload_tasks = {}

# Mock data for dashboard
def generate_mock_dashboard_data():
    return {
        "total_documents": len(documents_db),
        "processing_queue": len([d for d in documents_db if d.get("status") == "processing"]),
        "completed_today": len([d for d in documents_db if d.get("status") == "completed"]),
        "system_health": "operational",
        "recent_activity": [
            {
                "id": str(uuid.uuid4()),
                "action": "document_uploaded",
                "document_name": "sample.pdf",
                "timestamp": datetime.now().isoformat()
            }
        ]
    }

def generate_mock_documents():
    if not documents_db:
        # Create some mock documents
        mock_docs = [
            {
                "id": str(uuid.uuid4()),
                "filename": "قرارداد_فروش.pdf",
                "size": 1024000,
                "upload_date": datetime.now().isoformat(),
                "status": "completed",
                "category": "contracts",
                "quality_score": 95,
                "extracted_text": "این یک نمونه متن استخراج شده است."
            },
            {
                "id": str(uuid.uuid4()),
                "filename": "دادخواست_حقوقی.pdf",
                "size": 2048000,
                "upload_date": (datetime.now() - timedelta(hours=2)).isoformat(),
                "status": "processing",
                "category": "legal_claims",
                "quality_score": 87,
                "extracted_text": "متن استخراج شده از دادخواست"
            }
        ]
        documents_db.extend(mock_docs)
    return documents_db

# Health check endpoint
@app.get("/api/health")
async def health_check():
    """System health check"""
    return {
        "status": "healthy",
        "services": {
            "database": "healthy",
            "ocr": "healthy",
            "ai": "healthy"
        },
        "version": "1.0.0",
        "timestamp": datetime.now().isoformat()
    }

# Dashboard summary endpoint
@app.get("/api/dashboard/summary")
async def get_dashboard_summary():
    """Get dashboard summary statistics"""
    data = generate_mock_dashboard_data()
    return {
        "success": True,
        "data": data,
        "message": "Dashboard data retrieved successfully"
    }

# Documents endpoints
@app.get("/api/documents/")
async def get_documents(
    skip: int = 0,
    limit: int = 50,
    status: Optional[str] = None,
    category: Optional[str] = None,
    search: Optional[str] = None
):
    """Get paginated list of documents"""
    docs = generate_mock_documents()
    
    # Apply filters
    if status:
        docs = [d for d in docs if d.get("status") == status]
    if category:
        docs = [d for d in docs if d.get("category") == category]
    if search:
        docs = [d for d in docs if search.lower() in d.get("filename", "").lower()]
    
    # Apply pagination
    total = len(docs)
    docs = docs[skip:skip + limit]
    
    return {
        "success": True,
        "data": {
            "documents": docs,
            "total": total,
            "skip": skip,
            "limit": limit
        },
        "message": "Documents retrieved successfully"
    }

@app.get("/api/documents/{document_id}")
async def get_document(document_id: str):
    """Get single document by ID"""
    docs = generate_mock_documents()
    doc = next((d for d in docs if d["id"] == document_id), None)
    
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    
    return {
        "success": True,
        "data": doc,
        "message": "Document retrieved successfully"
    }

@app.delete("/api/documents/{document_id}")
async def delete_document(document_id: str):
    """Delete document by ID"""
    global documents_db
    docs = generate_mock_documents()
    doc = next((d for d in docs if d["id"] == document_id), None)
    
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    
    documents_db = [d for d in documents_db if d["id"] != document_id]
    
    return {
        "success": True,
        "message": "Document deleted successfully"
    }

# OCR upload endpoint
@app.post("/api/ocr/upload")
async def upload_files(files: List[UploadFile] = File(...)):
    """Upload files for OCR processing"""
    results = []
    
    for file in files:
        if not file.filename:
            continue
            
        # Generate unique ID
        document_id = str(uuid.uuid4())
        task_id = str(uuid.uuid4())
        
        # Save file
        file_path = UPLOAD_DIR / f"{document_id}_{file.filename}"
        with open(file_path, "wb") as f:
            content = await file.read()
            f.write(content)
        
        # Create document record
        doc = {
            "id": document_id,
            "filename": file.filename,
            "size": len(content),
            "upload_date": datetime.now().isoformat(),
            "status": "uploaded",
            "category": "unknown",
            "quality_score": 0,
            "extracted_text": ""
        }
        
        documents_db.append(doc)
        
        # Store task info
        upload_tasks[task_id] = {
            "document_id": document_id,
            "status": "processing",
            "start_time": datetime.now().isoformat()
        }
        
        results.append({
            "document_id": document_id,
            "filename": file.filename,
            "status": "uploaded",
            "ocr_task_id": task_id
        })
    
    return {
        "success": True,
        "data": {
            "documents": results,
            "message": f"Successfully uploaded {len(results)} files"
        },
        "message": "Files uploaded successfully"
    }

# OCR extract endpoint
@app.post("/api/ocr/extract")
async def extract_text(file: UploadFile = File(...)):
    """Extract text from file immediately"""
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file provided")
    
    # Simulate OCR processing
    await file.read()  # Read the file
    
    # Mock extracted text
    extracted_text = "این یک نمونه متن استخراج شده از فایل است. متن شامل اطلاعات حقوقی و قانونی می‌باشد."
    
    return {
        "success": True,
        "data": {
            "extracted_text": extracted_text,
            "confidence": 0.95,
            "processing_time": 2.5
        },
        "message": "Text extracted successfully"
    }

# Dashboard charts endpoints
@app.get("/api/dashboard/charts/processing-trends")
async def get_processing_trends(period: str = "weekly"):
    """Get processing trends for charts"""
    # Mock trend data
    trends = {
        "labels": ["شنبه", "یکشنبه", "دوشنبه", "سه‌شنبه", "چهارشنبه", "پنج‌شنبه", "جمعه"],
        "datasets": [
            {
                "label": "اسناد آپلود شده",
                "data": [12, 19, 15, 25, 22, 18, 14],
                "borderColor": "rgb(75, 192, 192)",
                "backgroundColor": "rgba(75, 192, 192, 0.2)"
            }
        ]
    }
    
    return {
        "success": True,
        "data": trends,
        "message": "Processing trends retrieved successfully"
    }

@app.get("/api/dashboard/charts/status-distribution")
async def get_status_distribution():
    """Get status distribution for pie chart"""
    docs = generate_mock_documents()
    
    status_counts = {}
    for doc in docs:
        status = doc.get("status", "unknown")
        status_counts[status] = status_counts.get(status, 0) + 1
    
    return {
        "success": True,
        "data": {
            "labels": list(status_counts.keys()),
            "datasets": [{
                "data": list(status_counts.values()),
                "backgroundColor": [
                    "rgba(255, 99, 132, 0.8)",
                    "rgba(54, 162, 235, 0.8)",
                    "rgba(255, 205, 86, 0.8)",
                    "rgba(75, 192, 192, 0.8)"
                ]
            }]
        },
        "message": "Status distribution retrieved successfully"
    }

@app.get("/api/dashboard/charts/category-distribution")
async def get_category_distribution():
    """Get category distribution for pie chart"""
    docs = generate_mock_documents()
    
    category_counts = {}
    for doc in docs:
        category = doc.get("category", "unknown")
        category_counts[category] = category_counts.get(category, 0) + 1
    
    return {
        "success": True,
        "data": {
            "labels": list(category_counts.keys()),
            "datasets": [{
                "data": list(category_counts.values()),
                "backgroundColor": [
                    "rgba(255, 99, 132, 0.8)",
                    "rgba(54, 162, 235, 0.8)",
                    "rgba(255, 205, 86, 0.8)",
                    "rgba(75, 192, 192, 0.8)"
                ]
            }]
        },
        "message": "Category distribution retrieved successfully"
    }

# Serve static files (Frontend)
frontend_dir = Path(__file__).parent / "frontend"
if frontend_dir.exists():
    app.mount("/static", StaticFiles(directory=str(frontend_dir)), name="static")
    print(f"📁 Static files mounted from: {frontend_dir}")
else:
    print("⚠️ Frontend directory not found")

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
        return HTMLResponse(f"""
        <html>
            <head><title>Legal Dashboard</title></head>
            <body>
                <h1>🏛️ Legal Dashboard API</h1>
                <p>Backend is running!</p>
                <p><a href="/api/docs">📖 API Documentation</a></p>
                <p>Error: {str(e)}</p>
            </body>
        </html>
        """)

if __name__ == "__main__":
    print("🚀 Starting Simple Legal Dashboard Backend...")
    print(f"📁 Upload directory: {UPLOAD_DIR}")
    print(f"🌐 Server will be available at: http://localhost:7860")
    print(f"📖 API docs will be available at: http://localhost:7860/api/docs")
    
    uvicorn.run(app, host="0.0.0.0", port=7860, log_level="info")