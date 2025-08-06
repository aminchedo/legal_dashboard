"""
OCR API Router
=============

PDF processing and text extraction endpoints.
"""

from fastapi import APIRouter, HTTPException, UploadFile, File, Depends, BackgroundTasks
from typing import List, Dict, Any
import tempfile
import os
import logging
from pathlib import Path
from ..models.document_models import OCRRequest, OCRResponse
from ..services.ocr_service import OCRPipeline
from ..services.database_service import DatabaseManager
from ..services.ai_service import AIScoringEngine

logger = logging.getLogger(__name__)

router = APIRouter()

# Dependency injection


def get_ocr_pipeline():
    return OCRPipeline()


def get_db():
    return DatabaseManager()


def get_ai_engine():
    return AIScoringEngine()


@router.post("/process", response_model=OCRResponse)
async def process_pdf(
    file: UploadFile = File(...),
    language: str = "fa",
    model_name: str = None,
    ocr_pipeline: OCRPipeline = Depends(get_ocr_pipeline)
):
    """Process a PDF file and extract text"""
    try:
        # Validate file type
        if not file.filename.lower().endswith('.pdf'):
            raise HTTPException(
                status_code=400, detail="Only PDF files are supported")

        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as temp_file:
            content = await file.read()
            temp_file.write(content)
            temp_file_path = temp_file.name

        try:
            # Process PDF with OCR
            result = ocr_pipeline.extract_text_from_pdf(temp_file_path)

            # Create response
            response = OCRResponse(
                success=result.get('success', False),
                extracted_text=result.get('extracted_text', ''),
                confidence=result.get('confidence', 0.0),
                processing_time=result.get('processing_time', 0.0),
                language_detected=result.get('language_detected', language),
                page_count=result.get('page_count', 0),
                error_message=result.get('error_message')
            )

            return response

        finally:
            # Clean up temporary file
            if os.path.exists(temp_file_path):
                os.unlink(temp_file_path)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing PDF: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/process-and-save")
async def process_and_save_document(
    file: UploadFile = File(...),
    title: str = None,
    source: str = None,
    category: str = None,
    background_tasks: BackgroundTasks = None,
    ocr_pipeline: OCRPipeline = Depends(get_ocr_pipeline),
    db: DatabaseManager = Depends(get_db),
    ai_engine: AIScoringEngine = Depends(get_ai_engine)
):
    """Process PDF and save as document in database"""
    try:
        # Validate file type
        if not file.filename.lower().endswith('.pdf'):
            raise HTTPException(
                status_code=400, detail="Only PDF files are supported")

        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as temp_file:
            content = await file.read()
            temp_file.write(content)
            temp_file_path = temp_file.name

        try:
            # Process PDF with OCR
            ocr_result = ocr_pipeline.extract_text_from_pdf(temp_file_path)

            if not ocr_result.get('success', False):
                raise HTTPException(
                    status_code=400,
                    detail=f"OCR processing failed: {ocr_result.get('error_message', 'Unknown error')}"
                )

            # Prepare document data
            document_data = {
                'title': title or file.filename,
                'source': source or 'Uploaded',
                'category': category or 'عمومی',
                'full_text': ocr_result.get('extracted_text', ''),
                'ocr_confidence': ocr_result.get('confidence', 0.0),
                'processing_time': ocr_result.get('processing_time', 0.0),
                'file_path': temp_file_path,
                'file_size': os.path.getsize(temp_file_path),
                'language': ocr_result.get('language_detected', 'fa'),
                'page_count': ocr_result.get('page_count', 0)
            }

            # Calculate AI score
            final_score = ai_engine.calculate_score(document_data)
            document_data['final_score'] = final_score

            # Predict category if not provided
            if not document_data.get('category') or document_data['category'] == 'عمومی':
                document_data['category'] = ai_engine.predict_category(
                    document_data.get('title', ''),
                    document_data.get('full_text', '')
                )

            # Extract keywords
            keywords = ai_engine.extract_keywords(
                document_data.get('full_text', ''))
            document_data['keywords'] = keywords

            # Save to database
            document_id = db.insert_document(document_data)

            # Get the created document
            created_document = db.get_document_by_id(document_id)

            return {
                "message": "Document processed and saved successfully",
                "document_id": document_id,
                "document": created_document,
                "ocr_result": ocr_result
            }

        finally:
            # Clean up temporary file
            if os.path.exists(temp_file_path):
                os.unlink(temp_file_path)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing and saving document: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/batch-process")
async def batch_process_pdfs(
    files: List[UploadFile] = File(...),
    background_tasks: BackgroundTasks = None,
    ocr_pipeline: OCRPipeline = Depends(get_ocr_pipeline)
):
    """Process multiple PDF files"""
    try:
        results = []

        for file in files:
            try:
                # Validate file type
                if not file.filename.lower().endswith('.pdf'):
                    results.append({
                        "filename": file.filename,
                        "success": False,
                        "error": "Only PDF files are supported"
                    })
                    continue

                # Save uploaded file temporarily
                with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as temp_file:
                    content = await file.read()
                    temp_file.write(content)
                    temp_file_path = temp_file.name

                try:
                    # Process PDF with OCR
                    result = ocr_pipeline.extract_text_from_pdf(temp_file_path)

                    results.append({
                        "filename": file.filename,
                        "success": result.get('success', False),
                        "extracted_text": result.get('extracted_text', ''),
                        "confidence": result.get('confidence', 0.0),
                        "processing_time": result.get('processing_time', 0.0),
                        "page_count": result.get('page_count', 0),
                        "error_message": result.get('error_message')
                    })

                finally:
                    # Clean up temporary file
                    if os.path.exists(temp_file_path):
                        os.unlink(temp_file_path)

            except Exception as e:
                results.append({
                    "filename": file.filename,
                    "success": False,
                    "error": str(e)
                })

        return {
            "total_files": len(files),
            "processed_files": len([r for r in results if r.get('success', False)]),
            "results": results
        }

    except Exception as e:
        logger.error(f"Error in batch processing: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/quality-metrics")
async def get_ocr_quality_metrics(
    document_id: str,
    ocr_pipeline: OCRPipeline = Depends(get_ocr_pipeline),
    db: DatabaseManager = Depends(get_db)
):
    """Get OCR quality metrics for a document"""
    try:
        # Get document
        document = db.get_document_by_id(document_id)
        if not document:
            raise HTTPException(status_code=404, detail="Document not found")

        # Create extraction result for metrics
        extraction_result = {
            "extracted_text": document.get('full_text', ''),
            "confidence": document.get('ocr_confidence', 0.0)
        }

        # Calculate quality metrics
        metrics = ocr_pipeline.get_ocr_quality_metrics(extraction_result)

        return {
            "document_id": document_id,
            "metrics": metrics,
            "document_info": {
                "title": document.get('title'),
                "file_size": document.get('file_size'),
                "processing_time": document.get('processing_time'),
                "page_count": document.get('page_count', 0)
            }
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting OCR quality metrics: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/models")
async def get_available_models():
    """Get available OCR models"""
    return {
        "models": [
            {
                "name": "microsoft/trocr-base-stage1",
                "description": "Microsoft TrOCR base model for printed text",
                "language": "multilingual",
                "type": "printed"
            },
            {
                "name": "microsoft/trocr-base-handwritten",
                "description": "Microsoft TrOCR base model for handwritten text",
                "language": "multilingual",
                "type": "handwritten"
            },
            {
                "name": "microsoft/trocr-large-stage1",
                "description": "Microsoft TrOCR large model for better accuracy",
                "language": "multilingual",
                "type": "printed"
            }
        ],
        "current_model": "microsoft/trocr-base-stage1"
    }


@router.get("/status")
async def get_ocr_status(ocr_pipeline: OCRPipeline = Depends(get_ocr_pipeline)):
    """Get OCR pipeline status"""
    return {
        "initialized": ocr_pipeline.initialized,
        "model_name": ocr_pipeline.model_name,
        "initialization_attempted": ocr_pipeline.initialization_attempted
    }
