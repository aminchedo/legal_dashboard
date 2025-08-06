"""
AI Service for Legal Dashboard
=============================

Advanced AI-powered features for legal document analysis including:
- Intelligent document scoring and classification
- Legal entity extraction and recognition
- Sentiment analysis for legal documents
- Smart search and recommendation engine
- Document similarity analysis
"""

import re
import json
import logging
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime, timedelta
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.cluster import KMeans
import hashlib
import sqlite3
from pathlib import Path

logger = logging.getLogger(__name__)


class AIScoringEngine:
    """
    Advanced AI scoring engine for legal documents
    Provides intelligent analysis, classification, and recommendations
    """

    def __init__(self):
        """Initialize the AI scoring engine"""
        self.vectorizer = TfidfVectorizer(
            max_features=1000,
            stop_words=None,  # Keep Persian stop words for legal context
            ngram_range=(1, 3)
        )
        self.document_vectors = {}
        self.legal_keywords = self._load_legal_keywords()
        self.entity_patterns = self._load_entity_patterns()
        self.sentiment_indicators = self._load_sentiment_indicators()
        self.classification_categories = self._load_classification_categories()

    def _load_legal_keywords(self) -> Dict[str, List[str]]:
        """Load Persian legal keywords for different categories"""
        return {
            "قانون": [
                "قانون", "ماده", "تبصره", "بند", "فصل", "باب", "مصوبه", "تصویب",
                "مجلس", "شورای", "ملی", "اساسی", "مدنی", "جزایی", "تجاری"
            ],
            "قرارداد": [
                "قرارداد", "عقد", "مفاد", "طرفین", "متعاهدین", "شرایط", "ماده",
                "بند", "مبلغ", "پرداخت", "تعهد", "مسئولیت", "ضمانت"
            ],
            "احکام": [
                "حکم", "رای", "دادگاه", "قاضی", "شعبه", "دعوی", "خواهان",
                "خوانده", "شهادت", "دلیل", "اثبات", "قانونی", "محکوم"
            ],
            "مالی": [
                "مالیات", "درآمد", "سود", "زیان", "دارایی", "بدهی", "حساب",
                "ترازنامه", "صورت", "مالی", "دریافتی", "پرداختی"
            ],
            "اداری": [
                "اداره", "سازمان", "وزارت", "دولت", "مقام", "مسئول", "کارمند",
                "مقررات", "دستورالعمل", "بخشنامه", "آیین‌نامه"
            ]
        }

    def _load_entity_patterns(self) -> Dict[str, str]:
        """Load regex patterns for legal entity extraction"""
        return {
            "نام_شخص": r"([آ-ی]{2,}\s+){2,}",
            "نام_شرکت": r"(شرکت|موسسه|سازمان|بنیاد)\s+([آ-ی\s]+)",
            "شماره_قرارداد": r"شماره\s*:?\s*(\d+/\d+/\d+)",
            "تاریخ": r"(\d{1,2}/\d{1,2}/\d{2,4})",
            "مبلغ": r"(\d{1,3}(?:,\d{3})*)\s*(ریال|تومان|دلار|یورو)",
            "شماره_ملی": r"(\d{10})",
            "کد_پستی": r"(\d{10})",
            "شماره_تلفن": r"(\d{2,4}-\d{3,4}-\d{4})"
        }

    def _load_sentiment_indicators(self) -> Dict[str, List[str]]:
        """Load Persian sentiment indicators for legal documents"""
        return {
            "positive": [
                "موافق", "تایید", "قبول", "اجازه", "مجوز", "تصویب", "قانونی",
                "مشروع", "صحیح", "درست", "مناسب", "مطلوب", "سودمند"
            ],
            "negative": [
                "مخالف", "رد", "عدم", "ممنوع", "غیرقانونی", "نامشروع",
                "نادرست", "نامناسب", "مضر", "خطرناک", "ممنوع"
            ],
            "neutral": [
                "ماده", "بند", "تبصره", "قانون", "مقررات", "شرایط",
                "مفاد", "طرفین", "تاریخ", "مبلغ", "شماره"
            ]
        }

    def _load_classification_categories(self) -> Dict[str, Dict]:
        """Load document classification categories with weights"""
        return {
            "قرارداد": {
                "keywords": ["قرارداد", "عقد", "طرفین", "مفاد"],
                "weight": 0.4,
                "patterns": ["طرفین", "متعاهدین", "شرایط"]
            },
            "احکام_قضایی": {
                "keywords": ["حکم", "رای", "دادگاه", "قاضی"],
                "weight": 0.35,
                "patterns": ["شعبه", "خواهان", "خوانده"]
            },
            "قوانین": {
                "keywords": ["قانون", "ماده", "تبصره", "مجلس"],
                "weight": 0.3,
                "patterns": ["مصوبه", "تصویب", "اساسی"]
            },
            "مقررات_اداری": {
                "keywords": ["مقررات", "دستورالعمل", "آیین‌نامه"],
                "weight": 0.25,
                "patterns": ["اداره", "سازمان", "وزارت"]
            },
            "اسناد_مالی": {
                "keywords": ["مالی", "حساب", "ترازنامه", "صورت"],
                "weight": 0.2,
                "patterns": ["درآمد", "سود", "زیان"]
            }
        }

    def analyze_document(self, text: str, metadata: Dict = None) -> Dict[str, Any]:
        """
        Comprehensive document analysis including scoring, classification, and insights

        Args:
            text: Document text content
            metadata: Additional document metadata

        Returns:
            Dictionary containing analysis results
        """
        try:
            # Basic text preprocessing
            cleaned_text = self._preprocess_text(text)

            # Perform various analyses
            analysis = {
                "basic_metrics": self._calculate_basic_metrics(cleaned_text),
                "classification": self._classify_document(cleaned_text),
                "entities": self._extract_entities(cleaned_text),
                "sentiment": self._analyze_sentiment(cleaned_text),
                "keywords": self._extract_keywords(cleaned_text),
                "quality_score": self._calculate_quality_score(cleaned_text, metadata),
                "recommendations": self._generate_recommendations(cleaned_text, metadata),
                "timestamp": datetime.now().isoformat()
            }

            # Add similarity analysis if we have existing documents
            if self.document_vectors:
                analysis["similarity"] = self._find_similar_documents(
                    cleaned_text)

            return analysis

        except Exception as e:
            logger.error(f"Error in document analysis: {e}")
            return {
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }

    def _preprocess_text(self, text: str) -> str:
        """Clean and normalize Persian text"""
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text.strip())

        # Normalize Persian characters
        text = text.replace('ي', 'ی').replace('ك', 'ک')

        # Remove common noise characters
        text = re.sub(
            r'[^\u0600-\u06FF\u0750-\u077F\u08A0-\u08FF\uFB50-\uFDFF\uFE70-\uFEFF\s\d\-\.\/]', '', text)

        return text

    def _calculate_basic_metrics(self, text: str) -> Dict[str, Any]:
        """Calculate basic document metrics"""
        words = text.split()
        sentences = re.split(r'[.!?؟]', text)
        sentences = [s.strip() for s in sentences if s.strip()]

        return {
            "word_count": len(words),
            "sentence_count": len(sentences),
            "avg_sentence_length": len(words) / len(sentences) if sentences else 0,
            "unique_words": len(set(words)),
            "vocabulary_diversity": len(set(words)) / len(words) if words else 0,
            "legal_terms_count": self._count_legal_terms(text)
        }

    def _count_legal_terms(self, text: str) -> int:
        """Count legal terms in the document"""
        count = 0
        for category_terms in self.legal_keywords.values():
            for term in category_terms:
                count += text.count(term)
        return count

    def _classify_document(self, text: str) -> Dict[str, float]:
        """Classify document into legal categories"""
        scores = {}

        for category, config in self.classification_categories.items():
            score = 0
            weight = config["weight"]

            # Keyword matching
            for keyword in config["keywords"]:
                if keyword in text:
                    score += weight

            # Pattern matching
            for pattern in config["patterns"]:
                if pattern in text:
                    score += weight * 0.5

            scores[category] = min(score, 1.0)

        # Normalize scores
        total_score = sum(scores.values())
        if total_score > 0:
            scores = {k: v/total_score for k, v in scores.items()}

        return scores

    def _extract_entities(self, text: str) -> Dict[str, List[str]]:
        """Extract legal entities from text"""
        entities = {}

        for entity_type, pattern in self.entity_patterns.items():
            matches = re.findall(pattern, text)
            if matches:
                entities[entity_type] = list(set(matches))

        return entities

    def _analyze_sentiment(self, text: str) -> Dict[str, float]:
        """Analyze sentiment of legal document"""
        sentiment_scores = {"positive": 0, "negative": 0, "neutral": 0}
        total_words = len(text.split())

        if total_words == 0:
            return sentiment_scores

        for sentiment, indicators in self.sentiment_indicators.items():
            count = 0
            for indicator in indicators:
                count += text.count(indicator)
            sentiment_scores[sentiment] = count / total_words

        # Normalize scores
        total = sum(sentiment_scores.values())
        if total > 0:
            sentiment_scores = {k: v/total for k,
                                v in sentiment_scores.items()}

        return sentiment_scores

    def _extract_keywords(self, text: str) -> List[Tuple[str, float]]:
        """Extract important keywords with TF-IDF scores"""
        try:
            # Create document-term matrix
            tfidf_matrix = self.vectorizer.fit_transform([text])
            feature_names = self.vectorizer.get_feature_names_out()

            # Get TF-IDF scores
            scores = tfidf_matrix.toarray()[0]

            # Create keyword-score pairs
            keywords = [(feature_names[i], scores[i])
                        for i in range(len(feature_names))]

            # Sort by score and return top keywords
            keywords.sort(key=lambda x: x[1], reverse=True)
            return keywords[:20]  # Return top 20 keywords

        except Exception as e:
            logger.error(f"Error extracting keywords: {e}")
            return []

    def _calculate_quality_score(self, text: str, metadata: Dict = None) -> float:
        """Calculate overall document quality score"""
        score = 0.0

        # Text length factor (optimal length for legal documents)
        word_count = len(text.split())
        if 100 <= word_count <= 2000:
            score += 0.3
        elif word_count > 2000:
            score += 0.2
        else:
            score += 0.1

        # Legal terms density
        legal_terms = self._count_legal_terms(text)
        if legal_terms > 0:
            density = legal_terms / word_count
            if 0.01 <= density <= 0.1:
                score += 0.3
            elif density > 0.1:
                score += 0.2
            else:
                score += 0.1

        # Structure factor (presence of legal document structure)
        structure_indicators = ["ماده", "بند", "تبصره", "فصل", "باب"]
        structure_count = sum(text.count(indicator)
                              for indicator in structure_indicators)
        if structure_count > 0:
            score += 0.2

        # Completeness factor
        completeness_indicators = ["تاریخ", "شماره", "امضا", "مهر"]
        completeness_count = sum(text.count(indicator)
                                 for indicator in completeness_indicators)
        if completeness_count >= 2:
            score += 0.2

        return min(score, 1.0)

    def _generate_recommendations(self, text: str, metadata: Dict = None) -> List[str]:
        """Generate intelligent recommendations for the document"""
        recommendations = []

        # Check document completeness
        if len(text.split()) < 100:
            recommendations.append(
                "مستندات کافی نیست. پیشنهاد می‌شود جزئیات بیشتری اضافه شود.")

        # Check for legal structure
        if "ماده" not in text and "بند" not in text:
            recommendations.append(
                "ساختار حقوقی مشخص نیست. پیشنهاد می‌شود از ساختار ماده و بند استفاده شود.")

        # Check for dates and numbers
        if not re.search(r'\d{1,2}/\d{1,2}/\d{2,4}', text):
            recommendations.append(
                "تاریخ مشخص نشده است. پیشنهاد می‌شود تاریخ مستندات اضافه شود.")

        # Check for signatures
        if "امضا" not in text and "مهر" not in text:
            recommendations.append(
                "امضا یا مهر مشخص نشده است. پیشنهاد می‌شود امضا اضافه شود.")

        # Check for amounts
        if not re.search(r'\d{1,3}(?:,\d{3})*', text):
            recommendations.append(
                "مبالغ مشخص نشده است. پیشنهاد می‌شود مبالغ دقیق ذکر شود.")

        return recommendations

    def _find_similar_documents(self, text: str) -> List[Dict[str, Any]]:
        """Find similar documents using TF-IDF and cosine similarity"""
        try:
            # Vectorize current document
            current_vector = self.vectorizer.transform([text])

            similarities = []
            for doc_id, doc_vector in self.document_vectors.items():
                similarity = cosine_similarity(
                    current_vector, doc_vector)[0][0]
                similarities.append({
                    "document_id": doc_id,
                    "similarity_score": float(similarity),
                    "category": "similar_document"
                })

            # Sort by similarity and return top matches
            similarities.sort(
                key=lambda x: x["similarity_score"], reverse=True)
            return similarities[:5]  # Return top 5 similar documents

        except Exception as e:
            logger.error(f"Error finding similar documents: {e}")
            return []

    def update_document_vector(self, doc_id: str, text: str):
        """Update document vector for similarity analysis"""
        try:
            vector = self.vectorizer.transform([text])
            self.document_vectors[doc_id] = vector
        except Exception as e:
            logger.error(f"Error updating document vector: {e}")

    def get_ai_insights(self, documents: List[Dict]) -> Dict[str, Any]:
        """Generate AI insights from multiple documents"""
        try:
            insights = {
                "document_trends": self._analyze_trends(documents),
                "common_entities": self._find_common_entities(documents),
                "category_distribution": self._analyze_category_distribution(documents),
                "quality_metrics": self._calculate_overall_quality(documents),
                "recommendations": self._generate_system_recommendations(documents)
            }
            return insights
        except Exception as e:
            logger.error(f"Error generating AI insights: {e}")
            return {"error": str(e)}

    def _analyze_trends(self, documents: List[Dict]) -> Dict[str, Any]:
        """Analyze trends across documents"""
        # Implementation for trend analysis
        return {"trend_analysis": "Not implemented yet"}

    def _find_common_entities(self, documents: List[Dict]) -> Dict[str, List[str]]:
        """Find common entities across documents"""
        # Implementation for common entity analysis
        return {"common_entities": "Not implemented yet"}

    def _analyze_category_distribution(self, documents: List[Dict]) -> Dict[str, int]:
        """Analyze distribution of document categories"""
        # Implementation for category distribution
        return {"category_distribution": "Not implemented yet"}

    def _calculate_overall_quality(self, documents: List[Dict]) -> Dict[str, float]:
        """Calculate overall quality metrics"""
        # Implementation for overall quality calculation
        return {"overall_quality": "Not implemented yet"}

    def _generate_system_recommendations(self, documents: List[Dict]) -> List[str]:
        """Generate system-wide recommendations"""
        # Implementation for system recommendations
        return ["سیستم در حال بهبود است"]
