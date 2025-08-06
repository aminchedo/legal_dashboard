"""
OCR Service for Legal Dashboard
==============================

Hugging Face OCR pipeline for Persian legal document processing.
Supports multiple OCR models and intelligent content detection.
"""

import io
import os
import sys
import fitz  # PyMuPDF
import cv2
import numpy as np
from PIL import Image
from typing import Dict, List, Optional, Tuple, Any
import logging
from pathlib import Path
import tempfile
import shutil
import requests
import time
from transformers import pipeline, AutoTokenizer, AutoModelForVision2Seq
import torch

logger = logging.getLogger(__name__)

# Hugging Face Token - Get from environment variable
HF_TOKEN = os.getenv("HF_TOKEN", "")


class OCRPipeline:
    """
    Advanced Persian OCR processor using Hugging Face models
    Supports both text-based and image-based PDFs
    """

    def __init__(self, model_name: str = "microsoft/trocr-base-stage1"):
        """
        Initialize the Hugging Face OCR processor

        Args:
            model_name: Hugging Face model name for OCR
        """
        self.model_name = model_name
        self.hf_token = HF_TOKEN
        self.initialized = False
        self.initialization_attempted = False
        self.ocr_pipeline = None

        # Don't initialize immediately - let it be called explicitly
        logger.info(f"OCR Pipeline created with model: {model_name}")

    def initialize(self):
        """Initialize the OCR pipeline - called explicitly"""
        if self.initialization_attempted:
            return

        self._setup_ocr_pipeline()

    def _setup_ocr_pipeline(self):
        """Setup Hugging Face OCR pipeline with improved error handling"""
        if self.initialization_attempted:
            return

        self.initialization_attempted = True

        # List of compatible models to try
        compatible_models = [
            "microsoft/trocr-base-stage1",
            "microsoft/trocr-base-handwritten",
            "microsoft/trocr-small-stage1",
            "microsoft/trocr-small-handwritten"
        ]

        for model in compatible_models:
            try:
                logger.info(f"Loading Hugging Face OCR model: {model}")

                # Use Hugging Face token from environment variable
                if not self.hf_token:
                    logger.warning(
                        "HF_TOKEN not found in environment variables")

                # Initialize the OCR pipeline with cache directory and error handling
                try:
                    if self.hf_token:
                        self.ocr_pipeline = pipeline(
                            "image-to-text",
                            model=model,
                            use_auth_token=self.hf_token,
                            cache_dir="/tmp/hf_cache"
                        )
                    else:
                        self.ocr_pipeline = pipeline(
                            "image-to-text",
                            model=model,
                            cache_dir="/tmp/hf_cache"
                        )

                    self.model_name = model
                    self.initialized = True
                    logger.info(
                        f"Hugging Face OCR pipeline initialized successfully with model: {model}")
                    return

                except Exception as pipeline_error:
                    logger.warning(
                        f"Pipeline initialization failed for {model}: {pipeline_error}")

                    # Try with slow tokenizer fallback
                    try:
                        logger.info(
                            f"Trying slow tokenizer fallback for {model}")
                        if self.hf_token:
                            self.ocr_pipeline = pipeline(
                                "image-to-text",
                                model=model,
                                use_auth_token=self.hf_token,
                                cache_dir="/tmp/hf_cache",
                                use_fast=False  # Force slow tokenizer
                            )
                        else:
                            self.ocr_pipeline = pipeline(
                                "image-to-text",
                                model=model,
                                cache_dir="/tmp/hf_cache",
                                use_fast=False  # Force slow tokenizer
                            )

                        self.model_name = model
                        self.initialized = True
                        logger.info(
                            f"OCR pipeline initialized with slow tokenizer: {model}")
                        return

                    except Exception as slow_error:
                        logger.warning(
                            f"Slow tokenizer also failed for {model}: {slow_error}")
                        continue

            except Exception as e:
                logger.warning(f"Failed to load model {model}: {e}")
                continue

        # If all models fail, use basic text extraction
        try:
            logger.info("All OCR models failed, using basic text extraction")
            self.initialized = True
            self.ocr_pipeline = None
            logger.info("Using basic text extraction as fallback")
        except Exception as e:
            logger.error(f"Error setting up basic OCR fallback: {e}")
            self.initialized = False

    def extract_text_from_pdf(self, pdf_path: str) -> Dict[str, Any]:
        """
        Extract text from PDF document with intelligent content detection

        Args:
            pdf_path: Path to the PDF file

        Returns:
            Dictionary containing extracted text and metadata
        """
        start_time = time.time()

        try:
            logger.info(f"Processing PDF with Hugging Face OCR: {pdf_path}")

            # Open PDF with PyMuPDF
            doc = fitz.open(pdf_path)

            if not doc:
                raise ValueError("Invalid PDF file")

            # Analyze PDF content type
            content_type = self._analyze_pdf_content(doc)
            logger.info(f"PDF content type detected: {content_type}")

            # Extract content based on type
            if content_type == "text":
                result = self._extract_text_content(doc)
            elif content_type == "image":
                result = self._extract_ocr_content(doc)
            else:  # mixed
                result = self._extract_mixed_content(doc)

            # Add metadata
            result["processing_time"] = time.time() - start_time
            result["content_type"] = content_type
            result["page_count"] = len(doc)
            result["file_path"] = pdf_path
            result["file_size"] = os.path.getsize(pdf_path)

            doc.close()
            return result

        except Exception as e:
            logger.error(f"Error processing PDF {pdf_path}: {e}")
            return {
                "success": False,
                "extracted_text": "",
                "confidence": 0.0,
                "processing_time": time.time() - start_time,
                "error_message": str(e),
                "content_type": "unknown",
                "page_count": 0,
                "file_path": pdf_path,
                "file_size": 0
            }

    def _analyze_pdf_content(self, doc) -> str:
        """Analyze PDF content to determine if it's text, image, or mixed"""
        text_pages = 0
        image_pages = 0
        total_pages = len(doc)

        for page_num in range(min(total_pages, 5)):  # Check first 5 pages
            page = doc[page_num]

            # Extract text
            text = page.get_text().strip()

            # Get images
            images = page.get_images()

            if len(text) > 100:  # Significant text content
                text_pages += 1
            elif len(images) > 0:  # Has images
                image_pages += 1

        # Determine content type
        if text_pages > image_pages:
            return "text"
        elif image_pages > text_pages:
            return "image"
        else:
            return "mixed"

    def _extract_text_content(self, doc) -> Dict:
        """Extract text from text-based PDF"""
        full_text = ""

        for page_num in range(len(doc)):
            page = doc[page_num]
            text = page.get_text()
            full_text += f"\n--- Page {page_num + 1} ---\n{text}\n"

        return {
            "success": True,
            "extracted_text": full_text.strip(),
            "confidence": 1.0,
            "language_detected": "fa"
        }

    def _extract_ocr_content(self, doc) -> Dict:
        """Extract text from image-based PDF using OCR"""
        full_text = ""
        total_confidence = 0.0
        processed_pages = 0

        for page_num in range(len(doc)):
            try:
                # Convert page to image
                page = doc[page_num]
                # Higher resolution
                pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))

                # Convert to PIL Image
                img_data = pix.tobytes("png")
                img = Image.open(io.BytesIO(img_data))

                # Preprocess image
                img = self._preprocess_image_for_ocr(img)

                # Perform OCR
                if self.initialized:
                    result = self.ocr_pipeline(img)
                    text = result[0]["generated_text"] if result else ""
                    confidence = result[0].get("score", 0.0) if result else 0.0
                else:
                    text = ""
                    confidence = 0.0

                full_text += f"\n--- Page {page_num + 1} ---\n{text}\n"
                total_confidence += confidence
                processed_pages += 1

            except Exception as e:
                logger.error(f"Error processing page {page_num}: {e}")
                full_text += f"\n--- Page {page_num + 1} ---\n[Error processing page]\n"

        avg_confidence = total_confidence / \
            processed_pages if processed_pages > 0 else 0.0

        return {
            "success": True,
            "extracted_text": full_text.strip(),
            "confidence": avg_confidence,
            "language_detected": "fa"
        }

    def _extract_mixed_content(self, doc) -> Dict:
        """Extract text from mixed content PDF"""
        full_text = ""
        total_confidence = 0.0
        processed_pages = 0

        for page_num in range(len(doc)):
            page = doc[page_num]

            # Try text extraction first
            text = page.get_text().strip()

            if len(text) < 50:  # Not enough text, try OCR
                try:
                    pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))
                    img_data = pix.tobytes("png")
                    img = Image.open(io.BytesIO(img_data))
                    img = self._preprocess_image_for_ocr(img)

                    if self.initialized:
                        result = self.ocr_pipeline(img)
                        ocr_text = result[0]["generated_text"] if result else ""
                        confidence = result[0].get(
                            "score", 0.0) if result else 0.0
                    else:
                        ocr_text = ""
                        confidence = 0.0

                    text = ocr_text
                    total_confidence += confidence
                except Exception as e:
                    logger.error(f"Error processing page {page_num}: {e}")
                    text = "[Error processing page]"

            full_text += f"\n--- Page {page_num + 1} ---\n{text}\n"
            processed_pages += 1

        avg_confidence = total_confidence / \
            processed_pages if processed_pages > 0 else 0.0

        return {
            "success": True,
            "extracted_text": full_text.strip(),
            "confidence": avg_confidence,
            "language_detected": "fa"
        }

    def _preprocess_image_for_ocr(self, img: Image.Image) -> Image.Image:
        """Preprocess image for better OCR results"""
        # Convert to RGB if needed
        if img.mode != 'RGB':
            img = img.convert('RGB')

        # Resize if too large
        max_size = 1024
        if max(img.size) > max_size:
            ratio = max_size / max(img.size)
            new_size = tuple(int(dim * ratio) for dim in img.size)
            img = img.resize(new_size, Image.Resampling.LANCZOS)

        # Enhance contrast
        img_array = np.array(img)
        img_gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
        img_enhanced = cv2.equalizeHist(img_gray)
        img_enhanced = cv2.cvtColor(img_enhanced, cv2.COLOR_GRAY2RGB)

        return Image.fromarray(img_enhanced)

    def process_document_batch(self, pdf_files: List[str]) -> List[Dict]:
        """Process multiple PDF files"""
        results = []

        for pdf_file in pdf_files:
            try:
                result = self.extract_text_from_pdf(pdf_file)
                results.append(result)
            except Exception as e:
                logger.error(f"Error processing {pdf_file}: {e}")
                results.append({
                    "success": False,
                    "extracted_text": "",
                    "confidence": 0.0,
                    "error_message": str(e),
                    "file_path": pdf_file
                })

        return results

    def get_ocr_quality_metrics(self, extraction_result: Dict) -> Dict:
        """Calculate OCR quality metrics"""
        text = extraction_result.get("extracted_text", "")
        confidence = extraction_result.get("confidence", 0.0)

        metrics = {
            "text_length": len(text),
            "word_count": len(text.split()),
            "confidence_score": confidence,
            "quality_score": min(confidence * 100, 100),
            "has_content": len(text.strip()) > 0,
            "avg_word_length": sum(len(word) for word in text.split()) / len(text.split()) if text.split() else 0
        }

        return metrics
