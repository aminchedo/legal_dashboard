#!/usr/bin/env python3
"""
Simple test server to verify FastAPI setup without database dependencies
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

# Create a simple FastAPI app
app = FastAPI(title="Test Analytics Server", version="1.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Test analytics endpoints


@app.get("/api/analytics/realtime")
async def get_realtime_analytics():
    return {
        "status": "success",
        "data": {
            "total_documents": 150,
            "active_users": 25,
            "processing_queue": 3,
            "system_uptime": "2h 15m",
            "last_update": "2024-01-15T10:30:00Z"
        }
    }


@app.get("/api/analytics/trends")
async def get_trends():
    return {
        "status": "success",
        "data": {
            "daily_uploads": [12, 15, 8, 20, 18, 22, 16],
            "processing_times": [2.1, 1.8, 2.3, 1.9, 2.0, 1.7, 2.2],
            "popular_document_types": ["contract", "agreement", "policy"],
            "trend_period": "7 days"
        }
    }


@app.get("/api/analytics/predictions")
async def get_predictions():
    return {
        "status": "success",
        "data": {
            "predicted_uploads": 18,
            "confidence": 0.85,
            "factors": ["weekday", "recent_trend", "user_activity"],
            "next_week_forecast": [15, 18, 20, 17, 19, 16, 14]
        }
    }


@app.get("/api/analytics/similarity")
async def get_similarity():
    return {
        "status": "success",
        "data": {
            "similar_documents": [
                {"id": 1, "title": "Contract A", "similarity": 0.92},
                {"id": 2, "title": "Contract B", "similarity": 0.87},
                {"id": 3, "title": "Contract C", "similarity": 0.81}
            ],
            "total_analyzed": 45
        }
    }


@app.get("/api/analytics/clustering")
async def get_clustering():
    return {
        "status": "success",
        "data": {
            "clusters": [
                {"id": 1, "name": "Contracts", "size": 25, "avg_similarity": 0.78},
                {"id": 2, "name": "Policies", "size": 18, "avg_similarity": 0.82},
                {"id": 3, "name": "Agreements", "size": 12, "avg_similarity": 0.75}
            ],
            "total_clusters": 3
        }
    }


@app.get("/api/analytics/quality")
async def get_quality():
    return {
        "status": "success",
        "data": {
            "overall_score": 8.5,
            "readability": 7.8,
            "completeness": 9.2,
            "accuracy": 8.7,
            "issues_found": 3,
            "recommendations": ["Improve formatting", "Add missing clauses"]
        }
    }


@app.get("/api/analytics/health")
async def get_health():
    return {
        "status": "success",
        "data": {
            "system_status": "healthy",
            "uptime": "2h 15m",
            "memory_usage": "45%",
            "cpu_usage": "23%",
            "disk_usage": "67%",
            "active_connections": 12
        }
    }


@app.get("/api/analytics/performance")
async def get_performance():
    return {
        "status": "success",
        "data": {
            "avg_response_time": 0.15,
            "requests_per_minute": 45,
            "error_rate": 0.02,
            "throughput": 120,
            "peak_load": 85,
            "optimization_score": 8.8
        }
    }


@app.get("/")
async def root():
    return {"message": "Test Analytics Server is running!"}


@app.get("/docs")
async def docs():
    return {"message": "API documentation available at /docs"}

if __name__ == "__main__":
    print("🚀 Starting Test Analytics Server...")
    print("📡 Server will be available at: http://localhost:8001")
    print("📊 Analytics endpoints available at: /api/analytics/*")
    print("📚 API docs available at: http://localhost:8001/docs")
    print("=" * 60)

    uvicorn.run(app, host="0.0.0.0", port=8001, reload=True)
