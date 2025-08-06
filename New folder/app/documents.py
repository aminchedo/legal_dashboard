"""
Documents API Router
===================

CRUD operations and advanced search for legal documents.
* Updated with Natural Language Search powered by Gemini.
"""

from fastapi import APIRouter, HTTPException, Query, Depends
from typing import List, Optional
from pydantic import BaseModel

from ..models.document_models import DocumentResponse, PaginatedResponse
from ..services.database_service import DatabaseManager
from ..services.ai_service import AIScoringEngine, gemini_service # Import Gemini Service
import logging
import time

logger = logging.getLogger(__name__)
router = APIRouter()

# --- Pydantic Models ---
class NaturalSearchRequest(BaseModel):
    query: str

# --- Dependency Injection ---
def get_db():
    return DatabaseManager()

# --- Existing Endpoints (GET, POST, PUT, DELETE for /documents) ---
# ... (Your existing CRUD endpoints for documents remain here without changes) ...
@router.get("/", response_model=PaginatedResponse)
async def get_documents(
    limit: int = Query(50, description="Number of results to return"),
    offset: int = Query(0, description="Number of results to skip"),
    db: DatabaseManager = Depends(get_db)
):
    """Get documents with pagination and filters"""
    try:
        documents = db.get_documents(limit=limit, offset=offset)
        total = db.get_documents_count()
        return PaginatedResponse(
            items=documents,
            total=total,
            page=offset // limit + 1,
            size=limit,
            pages=(total + limit - 1) // limit
        )
    except Exception as e:
        logger.error(f"Error getting documents: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


# --- NEW GEMINI-POWERED ENDPOINTS ---

@router.post("/search/natural")
async def natural_language_search(
    request: NaturalSearchRequest,
    db: DatabaseManager = Depends(get_db)
):
    """
    Performs a search using a natural language query by converting it to structured filters with Gemini.
    """
    start_time = time.time()
    try:
        # 1. Use Gemini to parse the natural language query into structured filters
        filters_json = await gemini_service.parse_search_query(request.query)
        
        # 2. Perform the search using the filters extracted by Gemini
        # We assume database_service has a method `search_documents_with_filters`
        search_results = db.search_documents(
            query=filters_json.get("keywords", ""),
            filters=filters_json,
            limit=20, 
            offset=0
        )
        
        end_time = time.time()
        
        return {
            "items": search_results,
            "total": len(search_results),
            "search_time_seconds": end_time - start_time,
            "interpreted_filters": filters_json # For debugging/transparency
        }

    except Exception as e:
        logger.error(f"Error during natural language search: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/documents/{doc_id}/analyze")
async def analyze_document_with_gemini(
    doc_id: int,
    db: DatabaseManager = Depends(get_db)
):
    """
    Analyzes a single document using Gemini to extract key insights.
    """
    try:
        document = db.get_document(doc_id)
        if not document or not document.get('full_text'):
            raise HTTPException(status_code=404, detail="Document not found or has no content.")
        
        analysis = await gemini_service.analyze_legal_document(document['full_text'])
        
        return {"analysis": analysis, "document_id": doc_id}

    except Exception as e:
        logger.error(f"Error analyzing document {doc_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))
