"""
Documents API Router
===================

CRUD operations for legal documents.
"""

from fastapi import APIRouter, HTTPException, Query, Depends
from typing import List, Optional
from ..models.document_models import (
    DocumentCreate, DocumentUpdate, DocumentResponse,
    SearchFilters, PaginatedResponse
)
from ..services.database_service import DatabaseManager
from ..services.ai_service import AIScoringEngine
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

# Dependency injection


def get_db():
    return DatabaseManager()


def get_ai_engine():
    return AIScoringEngine()


@router.get("/", response_model=PaginatedResponse)
async def get_documents(
    limit: int = Query(50, description="Number of results to return"),
    offset: int = Query(0, description="Number of results to skip"),
    category: Optional[str] = Query(None, description="Filter by category"),
    status: Optional[str] = Query(None, description="Filter by status"),
    min_score: Optional[float] = Query(
        None, description="Minimum score filter"),
    max_score: Optional[float] = Query(
        None, description="Maximum score filter"),
    source: Optional[str] = Query(None, description="Filter by source"),
    db: DatabaseManager = Depends(get_db)
):
    """Get documents with pagination and filters"""
    try:
        documents = db.get_documents(
            limit=limit,
            offset=offset,
            category=category,
            status=status,
            min_score=min_score,
            max_score=max_score,
            source=source
        )

        # Get total count for pagination
        total_docs = db.get_documents(limit=10000)  # Get all for count
        total = len(total_docs)

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


@router.get("/{document_id}", response_model=DocumentResponse)
async def get_document(
    document_id: str,
    db: DatabaseManager = Depends(get_db)
):
    """Get a single document by ID"""
    try:
        document = db.get_document_by_id(document_id)
        if not document:
            raise HTTPException(status_code=404, detail="Document not found")

        return DocumentResponse(**document)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting document {document_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/", response_model=DocumentResponse)
async def create_document(
    document: DocumentCreate,
    db: DatabaseManager = Depends(get_db),
    ai_engine: AIScoringEngine = Depends(get_ai_engine)
):
    """Create a new document"""
    try:
        # Convert to dict
        document_data = document.dict()

        # Add AI scoring
        final_score = ai_engine.calculate_score(document_data)
        document_data['final_score'] = final_score

        # Predict category if not provided
        if not document_data.get('category'):
            document_data['category'] = ai_engine.predict_category(
                document_data.get('title', ''),
                document_data.get('full_text', '')
            )

        # Extract keywords
        keywords = ai_engine.extract_keywords(
            document_data.get('full_text', ''))
        document_data['keywords'] = keywords

        # Insert into database
        document_id = db.insert_document(document_data)

        # Get the created document
        created_document = db.get_document_by_id(document_id)

        return DocumentResponse(**created_document)

    except Exception as e:
        logger.error(f"Error creating document: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.put("/{document_id}", response_model=DocumentResponse)
async def update_document(
    document_id: str,
    document_update: DocumentUpdate,
    db: DatabaseManager = Depends(get_db),
    ai_engine: AIScoringEngine = Depends(get_ai_engine)
):
    """Update a document"""
    try:
        # Check if document exists
        existing_document = db.get_document_by_id(document_id)
        if not existing_document:
            raise HTTPException(status_code=404, detail="Document not found")

        # Prepare update data
        update_data = document_update.dict(exclude_unset=True)

        # Recalculate score if text was updated
        if 'full_text' in update_data or 'title' in update_data:
            # Merge existing data with updates
            merged_data = {**existing_document, **update_data}
            final_score = ai_engine.calculate_score(merged_data)
            update_data['final_score'] = final_score

            # Update keywords if text changed
            if 'full_text' in update_data:
                keywords = ai_engine.extract_keywords(update_data['full_text'])
                update_data['keywords'] = keywords

        # Update document
        success = db.update_document(document_id, update_data)
        if not success:
            raise HTTPException(
                status_code=500, detail="Failed to update document")

        # Get updated document
        updated_document = db.get_document_by_id(document_id)

        return DocumentResponse(**updated_document)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating document {document_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.delete("/{document_id}")
async def delete_document(
    document_id: str,
    db: DatabaseManager = Depends(get_db)
):
    """Delete a document"""
    try:
        # Check if document exists
        existing_document = db.get_document_by_id(document_id)
        if not existing_document:
            raise HTTPException(status_code=404, detail="Document not found")

        # Delete document
        success = db.delete_document(document_id)
        if not success:
            raise HTTPException(
                status_code=500, detail="Failed to delete document")

        return {"message": "Document deleted successfully"}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting document {document_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/search/", response_model=List[DocumentResponse])
async def search_documents(
    q: str = Query(..., description="Search query"),
    limit: int = Query(20, description="Number of results to return"),
    db: DatabaseManager = Depends(get_db)
):
    """Search documents by text content"""
    try:
        # Get all documents (for now, implement proper search later)
        all_documents = db.get_documents(limit=1000)

        # Simple text search
        results = []
        query_lower = q.lower()

        for doc in all_documents:
            # Search in title and text
            title_match = query_lower in doc.get('title', '').lower()
            text_match = query_lower in doc.get('full_text', '').lower()

            if title_match or text_match:
                results.append(doc)

                if len(results) >= limit:
                    break

        return [DocumentResponse(**doc) for doc in results]

    except Exception as e:
        logger.error(f"Error searching documents: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/categories/")
async def get_categories(db: DatabaseManager = Depends(get_db)):
    """Get all document categories"""
    try:
        documents = db.get_documents(limit=10000)

        # Extract unique categories
        categories = set()
        for doc in documents:
            if doc.get('category'):
                categories.add(doc['category'])

        return {"categories": list(categories)}

    except Exception as e:
        logger.error(f"Error getting categories: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/sources/")
async def get_sources(db: DatabaseManager = Depends(get_db)):
    """Get all document sources"""
    try:
        documents = db.get_documents(limit=10000)

        # Extract unique sources
        sources = set()
        for doc in documents:
            if doc.get('source'):
                sources.add(doc['source'])

        return {"sources": list(sources)}

    except Exception as e:
        logger.error(f"Error getting sources: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
