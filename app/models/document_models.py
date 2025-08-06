"""
Document Models for Legal Dashboard OCR
=====================================

Pydantic models and dataclasses for legal document data structures.
"""

from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
from datetime import datetime
import uuid
from pydantic import BaseModel, Field


@dataclass
class LegalDocument:
    """Enhanced data class for legal documents with AI scoring"""
    id: Optional[str] = None
    title: str = ""
    document_number: str = ""
    publication_date: str = ""
    source: str = ""
    full_text: str = ""
    url: str = ""
    extracted_at: str = ""
    source_credibility: float = 0.0
    document_quality: float = 0.0
    final_score: float = 0.0
    category: str = ""
    status: str = "pending"
    ai_confidence: float = 0.0
    user_feedback: Optional[str] = None
    keywords: List[str] = field(default_factory=list)
    references: List[str] = field(default_factory=list)
    recency_score: float = 0.0
    ocr_confidence: float = 0.0
    language: str = "fa"  # Persian by default
    file_path: Optional[str] = None
    file_size: Optional[int] = None
    processing_time: Optional[float] = None

    def __post_init__(self):
        if self.id is None:
            self.id = str(uuid.uuid4())
        if self.extracted_at == "":
            self.extracted_at = datetime.now().isoformat()

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "id": self.id,
            "title": self.title,
            "document_number": self.document_number,
            "publication_date": self.publication_date,
            "source": self.source,
            "full_text": self.full_text,
            "url": self.url,
            "extracted_at": self.extracted_at,
            "source_credibility": self.source_credibility,
            "document_quality": self.document_quality,
            "final_score": self.final_score,
            "category": self.category,
            "status": self.status,
            "ai_confidence": self.ai_confidence,
            "user_feedback": self.user_feedback,
            "keywords": self.keywords,
            "references": self.references,
            "recency_score": self.recency_score,
            "ocr_confidence": self.ocr_confidence,
            "language": self.language,
            "file_path": self.file_path,
            "file_size": self.file_size,
            "processing_time": self.processing_time
        }


# Pydantic Models for API
class DocumentCreate(BaseModel):
    """Model for creating a new document"""
    title: str = Field(..., description="Document title")
    document_number: str = Field("", description="Document number")
    publication_date: str = Field("", description="Publication date")
    source: str = Field("", description="Document source")
    full_text: str = Field("", description="Extracted text content")
    url: str = Field("", description="Document URL")
    category: str = Field("", description="Document category")
    language: str = Field("fa", description="Document language")


class DocumentUpdate(BaseModel):
    """Model for updating a document"""
    title: Optional[str] = None
    document_number: Optional[str] = None
    publication_date: Optional[str] = None
    source: Optional[str] = None
    full_text: Optional[str] = None
    url: Optional[str] = None
    category: Optional[str] = None
    status: Optional[str] = None
    user_feedback: Optional[str] = None
    keywords: Optional[List[str]] = None
    references: Optional[List[str]] = None


class DocumentResponse(BaseModel):
    """Model for document API responses"""
    id: str
    title: str
    document_number: str
    publication_date: str
    source: str
    full_text: str
    url: str
    extracted_at: str
    source_credibility: float
    document_quality: float
    final_score: float
    category: str
    status: str
    ai_confidence: float
    user_feedback: Optional[str]
    keywords: List[str]
    references: List[str]
    recency_score: float
    ocr_confidence: float
    language: str
    file_path: Optional[str]
    file_size: Optional[int]
    processing_time: Optional[float]


class OCRRequest(BaseModel):
    """Model for OCR processing requests"""
    file_path: str = Field(..., description="Path to the PDF file")
    language: str = Field("fa", description="Document language")
    model_name: Optional[str] = Field(None, description="OCR model to use")


class OCRResponse(BaseModel):
    """Model for OCR processing responses"""
    success: bool
    extracted_text: str
    confidence: float
    processing_time: float
    language_detected: str
    page_count: int
    error_message: Optional[str] = None


class DashboardSummary(BaseModel):
    """Model for dashboard summary data"""
    total_documents: int
    processed_today: int
    average_score: float
    top_categories: List[Dict[str, Any]]
    recent_activity: List[Dict[str, Any]]
    system_status: Dict[str, bool]


class AIFeedback(BaseModel):
    """Model for AI training feedback"""
    document_id: str = Field(..., description="Document ID")
    feedback_type: str = Field(..., description="Type of feedback")
    feedback_score: float = Field(..., description="Feedback score")
    feedback_text: str = Field("", description="Feedback text")


class SearchFilters(BaseModel):
    """Model for document search filters"""
    category: Optional[str] = None
    status: Optional[str] = None
    min_score: Optional[float] = None
    max_score: Optional[float] = None
    source: Optional[str] = None
    date_from: Optional[str] = None
    date_to: Optional[str] = None
    language: Optional[str] = None
    limit: int = Field(50, description="Number of results to return")
    offset: int = Field(0, description="Number of results to skip")


class PaginatedResponse(BaseModel):
    """Model for paginated API responses"""
    items: List[DocumentResponse]
    total: int
    page: int
    size: int
    pages: int
