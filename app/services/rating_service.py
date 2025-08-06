"""
Advanced Data Rating Service
===========================

Production-grade rating service that evaluates scraped data quality,
source credibility, completeness, and OCR accuracy for the Legal Dashboard OCR system.
"""

import logging
import re
import json
import sqlite3
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from enum import Enum
import hashlib
from urllib.parse import urlparse
import asyncio
from pydantic import BaseModel, Field
import numpy as np
from collections import Counter

logger = logging.getLogger(__name__)


class RatingCriteria(Enum):
    """Available rating criteria"""
    SOURCE_CREDIBILITY = "source_credibility"
    CONTENT_COMPLETENESS = "content_completeness"
    OCR_ACCURACY = "ocr_accuracy"
    DATA_FRESHNESS = "data_freshness"
    CONTENT_RELEVANCE = "content_relevance"
    TECHNICAL_QUALITY = "technical_quality"


class RatingLevel(Enum):
    """Rating levels"""
    EXCELLENT = "excellent"
    GOOD = "good"
    AVERAGE = "average"
    POOR = "poor"
    UNRATED = "unrated"


@dataclass
class RatingResult:
    """Result of a rating evaluation"""
    item_id: str
    overall_score: float
    criteria_scores: Dict[str, float]
    rating_level: RatingLevel
    confidence: float
    timestamp: datetime
    evaluator: str
    notes: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for storage"""
        return {
            'item_id': self.item_id,
            'overall_score': self.overall_score,
            'criteria_scores': self.criteria_scores,
            'rating_level': self.rating_level.value,
            'confidence': self.confidence,
            'timestamp': self.timestamp.isoformat(),
            'evaluator': self.evaluator,
            'notes': self.notes
        }


class RatingConfig(BaseModel):
    """Configuration for rating evaluation"""
    source_credibility_weight: float = 0.25
    content_completeness_weight: float = 0.25
    ocr_accuracy_weight: float = 0.20
    data_freshness_weight: float = 0.15
    content_relevance_weight: float = 0.10
    technical_quality_weight: float = 0.05

    # Thresholds for rating levels
    excellent_threshold: float = 0.8
    good_threshold: float = 0.6
    average_threshold: float = 0.4
    poor_threshold: float = 0.2


class RatingService:
    """Advanced data rating service with multiple evaluation criteria"""

    def __init__(self, db_path: str = "legal_documents.db", config: Optional[RatingConfig] = None):
        self.db_path = db_path
        self.config = config or RatingConfig()
        self._initialize_database()

        # Credible domains for source credibility
        self.credible_domains = {
            'gov.ir', 'court.gov.ir', 'justice.gov.ir', 'mizanonline.ir',
            'irna.ir', 'isna.ir', 'mehrnews.com', 'tasnimnews.com',
            'farsnews.ir', 'entekhab.ir', 'khabaronline.ir'
        }

        # Legal document patterns
        self.legal_patterns = {
            'contract': r'\b(قرارداد|contract|agreement|عهدنامه)\b',
            'legal_document': r'\b(سند|document|legal|مدرک)\b',
            'court_case': r'\b(پرونده|case|court|دادگاه)\b',
            'law_article': r'\b(ماده|article|law|قانون)\b',
            'legal_notice': r'\b(اعلان|notice|announcement|آگهی)\b',
            'legal_decision': r'\b(رای|decision|verdict|حکم)\b',
            'legal_procedure': r'\b(رویه|procedure|process|فرآیند)\b'
        }

        # Quality indicators
        self.quality_indicators = {
            'structure': r'\b(فصل|بخش|ماده|تبصره|بند)\b',
            'formality': r'\b(مطابق|طبق|بر اساس|مطابق با)\b',
            'legal_terms': r'\b(حقوقی|قانونی|قضایی|دادگستری)\b',
            'official_language': r'\b(دولت|وزارت|سازمان|اداره)\b'
        }

    def _initialize_database(self):
        """Initialize database tables for rating data"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                # Create rating_results table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS rating_results (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        item_id TEXT NOT NULL,
                        overall_score REAL,
                        criteria_scores TEXT,
                        rating_level TEXT,
                        confidence REAL,
                        timestamp TEXT,
                        evaluator TEXT,
                        notes TEXT,
                        FOREIGN KEY (item_id) REFERENCES scraped_items (id)
                    )
                """)

                # Create rating_history table for tracking changes
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS rating_history (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        item_id TEXT NOT NULL,
                        old_score REAL,
                        new_score REAL,
                        change_reason TEXT,
                        timestamp TEXT,
                        evaluator TEXT
                    )
                """)

                conn.commit()
                logger.info("✅ Rating database initialized successfully")

        except Exception as e:
            logger.error(f"❌ Failed to initialize rating database: {e}")

    def _evaluate_source_credibility(self, domain: str, url: str, metadata: Dict[str, Any]) -> float:
        """Evaluate source credibility based on domain and metadata"""
        score = 0.0

        try:
            # Check if domain is in credible list
            if domain in self.credible_domains:
                score += 0.4

            # Check for government domains
            if '.gov.' in domain or domain.endswith('.gov.ir'):
                score += 0.3

            # Check for educational institutions
            if '.edu.' in domain or domain.endswith('.ac.ir'):
                score += 0.2

            # Check for HTTPS
            if url.startswith('https://'):
                score += 0.1

            # Check metadata for official indicators
            if metadata:
                title = metadata.get('title', '').lower()
                if any(indicator in title for indicator in ['دولت', 'وزارت', 'سازمان', 'اداره']):
                    score += 0.2

            return min(score, 1.0)

        except Exception as e:
            logger.error(f"Error evaluating source credibility: {e}")
            return 0.0

    def _evaluate_content_completeness(self, content: str, title: str, word_count: int) -> float:
        """Evaluate content completeness"""
        score = 0.0

        try:
            # Check word count (minimum 100 words for good content)
            if word_count >= 500:
                score += 0.3
            elif word_count >= 200:
                score += 0.2
            elif word_count >= 100:
                score += 0.1

            # Check for structured content
            if re.search(r'\b(فصل|بخش|ماده|تبصره)\b', content):
                score += 0.2

            # Check for legal document patterns
            legal_pattern_count = 0
            for pattern in self.legal_patterns.values():
                if re.search(pattern, content, re.IGNORECASE):
                    legal_pattern_count += 1

            if legal_pattern_count >= 3:
                score += 0.3
            elif legal_pattern_count >= 1:
                score += 0.2

            # Check for quality indicators
            quality_count = 0
            for pattern in self.quality_indicators.values():
                if re.search(pattern, content, re.IGNORECASE):
                    quality_count += 1

            if quality_count >= 2:
                score += 0.2

            return min(score, 1.0)

        except Exception as e:
            logger.error(f"Error evaluating content completeness: {e}")
            return 0.0

    def _evaluate_ocr_accuracy(self, content: str, language: str) -> float:
        """Evaluate OCR accuracy based on content quality"""
        score = 0.0

        try:
            # Check for common OCR errors
            ocr_errors = 0
            total_chars = len(content)

            # Check for repeated characters (common OCR error)
            repeated_chars = len(re.findall(r'(.)\1{2,}', content))
            if total_chars > 0:
                ocr_errors += repeated_chars / total_chars

            # Check for mixed scripts (indicates OCR issues)
            persian_chars = len(re.findall(r'[\u0600-\u06FF]', content))
            english_chars = len(re.findall(r'[a-zA-Z]', content))

            if persian_chars > 0 and english_chars > 0:
                # Mixed content is normal for legal documents
                if persian_chars / (persian_chars + english_chars) > 0.7:
                    score += 0.3
                else:
                    score += 0.1

            # Check for proper sentence structure
            sentences = re.split(r'[.!?]', content)
            proper_sentences = sum(1 for s in sentences if len(s.strip()) > 10)

            if len(sentences) > 0:
                sentence_quality = proper_sentences / len(sentences)
                score += sentence_quality * 0.3

            # Penalize for OCR errors
            if ocr_errors < 0.01:
                score += 0.2
            elif ocr_errors < 0.05:
                score += 0.1

            # Check for proper formatting
            if re.search(r'\n\s*\n', content):  # Paragraph breaks
                score += 0.1

            return min(score, 1.0)

        except Exception as e:
            logger.error(f"Error evaluating OCR accuracy: {e}")
            return 0.0

    def _evaluate_data_freshness(self, timestamp: str, metadata: Dict[str, Any]) -> float:
        """Evaluate data freshness"""
        score = 0.0

        try:
            # Parse timestamp
            if isinstance(timestamp, str):
                try:
                    item_time = datetime.fromisoformat(
                        timestamp.replace('Z', '+00:00'))
                except:
                    item_time = datetime.now(timezone.utc)
            else:
                item_time = timestamp

            current_time = datetime.now(timezone.utc)
            age_days = (current_time - item_time).days

            # Score based on age
            if age_days <= 30:
                score = 1.0
            elif age_days <= 90:
                score = 0.8
            elif age_days <= 365:
                score = 0.6
            elif age_days <= 1095:  # 3 years
                score = 0.4
            else:
                score = 0.2

            return score

        except Exception as e:
            logger.error(f"Error evaluating data freshness: {e}")
            return 0.5  # Default to average

    def _evaluate_content_relevance(self, content: str, title: str, strategy: str) -> float:
        """Evaluate content relevance to legal domain"""
        score = 0.0

        try:
            # Count legal terms
            legal_terms = 0
            for pattern in self.legal_patterns.values():
                matches = re.findall(pattern, content, re.IGNORECASE)
                legal_terms += len(matches)

            # Score based on legal term density
            if legal_terms >= 10:
                score += 0.4
            elif legal_terms >= 5:
                score += 0.3
            elif legal_terms >= 2:
                score += 0.2
            elif legal_terms >= 1:
                score += 0.1

            # Check title relevance
            title_legal_terms = 0
            for pattern in self.legal_patterns.values():
                if re.search(pattern, title, re.IGNORECASE):
                    title_legal_terms += 1

            if title_legal_terms >= 1:
                score += 0.3

            # Check for official language
            official_indicators = len(re.findall(
                r'\b(دولت|وزارت|سازمان|اداره|قانون|حقوق)\b', content))
            if official_indicators >= 3:
                score += 0.3
            elif official_indicators >= 1:
                score += 0.1

            return min(score, 1.0)

        except Exception as e:
            logger.error(f"Error evaluating content relevance: {e}")
            return 0.0

    def _evaluate_technical_quality(self, content: str, metadata: Dict[str, Any]) -> float:
        """Evaluate technical quality of the content"""
        score = 0.0

        try:
            # Check for proper structure
            if re.search(r'\b(ماده|بند|تبصره|فصل)\b', content):
                score += 0.3

            # Check for proper formatting
            if '\n\n' in content:  # Paragraph breaks
                score += 0.2

            # Check for consistent language
            persian_ratio = len(re.findall(
                r'[\u0600-\u06FF]', content)) / max(len(content), 1)
            if 0.3 <= persian_ratio <= 0.9:  # Good mix or mostly Persian
                score += 0.2

            # Check for metadata quality
            if metadata and len(metadata) >= 3:
                score += 0.1

            # Check for content length consistency
            if len(content) >= 200:
                score += 0.2

            return min(score, 1.0)

        except Exception as e:
            logger.error(f"Error evaluating technical quality: {e}")
            return 0.0

    def _calculate_confidence(self, criteria_scores: Dict[str, float]) -> float:
        """Calculate confidence level based on criteria consistency"""
        try:
            scores = list(criteria_scores.values())
            if not scores:
                return 0.0

            # Calculate standard deviation
            mean_score = np.mean(scores)
            variance = np.mean([(s - mean_score) ** 2 for s in scores])
            std_dev = np.sqrt(variance)

            # Higher confidence for consistent scores
            confidence = max(0.5, 1.0 - std_dev)
            return confidence

        except Exception as e:
            logger.error(f"Error calculating confidence: {e}")
            return 0.5

    def _determine_rating_level(self, overall_score: float) -> RatingLevel:
        """Determine rating level based on overall score"""
        if overall_score >= self.config.excellent_threshold:
            return RatingLevel.EXCELLENT
        elif overall_score >= self.config.good_threshold:
            return RatingLevel.GOOD
        elif overall_score >= self.config.average_threshold:
            return RatingLevel.AVERAGE
        elif overall_score >= self.config.poor_threshold:
            return RatingLevel.POOR
        else:
            return RatingLevel.UNRATED

    async def rate_item(self, item_data: Dict[str, Any], evaluator: str = "auto") -> RatingResult:
        """Rate a scraped item based on all criteria"""
        try:
            item_id = item_data['id']

            # Extract item properties
            url = item_data.get('url', '')
            title = item_data.get('title', '')
            content = item_data.get('content', '')
            metadata = item_data.get('metadata', {})
            timestamp = item_data.get('timestamp', '')
            domain = item_data.get('domain', '')
            word_count = item_data.get('word_count', 0)
            language = item_data.get('language', 'unknown')
            strategy = item_data.get('strategy_used', 'general')

            # Evaluate each criterion
            source_credibility = self._evaluate_source_credibility(
                domain, url, metadata)
            content_completeness = self._evaluate_content_completeness(
                content, title, word_count)
            ocr_accuracy = self._evaluate_ocr_accuracy(content, language)
            data_freshness = self._evaluate_data_freshness(timestamp, metadata)
            content_relevance = self._evaluate_content_relevance(
                content, title, strategy)
            technical_quality = self._evaluate_technical_quality(
                content, metadata)

            # Calculate weighted overall score
            criteria_scores = {
                'source_credibility': source_credibility,
                'content_completeness': content_completeness,
                'ocr_accuracy': ocr_accuracy,
                'data_freshness': data_freshness,
                'content_relevance': content_relevance,
                'technical_quality': technical_quality
            }

            overall_score = (
                source_credibility * self.config.source_credibility_weight +
                content_completeness * self.config.content_completeness_weight +
                ocr_accuracy * self.config.ocr_accuracy_weight +
                data_freshness * self.config.data_freshness_weight +
                content_relevance * self.config.content_relevance_weight +
                technical_quality * self.config.technical_quality_weight
            )

            # Calculate confidence
            confidence = self._calculate_confidence(criteria_scores)

            # Determine rating level
            rating_level = self._determine_rating_level(overall_score)

            # Create rating result
            rating_result = RatingResult(
                item_id=item_id,
                overall_score=round(overall_score, 3),
                criteria_scores={k: round(v, 3)
                                 for k, v in criteria_scores.items()},
                rating_level=rating_level,
                confidence=round(confidence, 3),
                timestamp=datetime.now(timezone.utc),
                evaluator=evaluator
            )

            # Store rating result
            await self._store_rating_result(rating_result)

            # Update item rating in scraped_items table
            await self._update_item_rating(item_id, overall_score)

            logger.info(
                f"✅ Rated item {item_id}: {rating_level.value} ({overall_score:.3f})")
            return rating_result

        except Exception as e:
            logger.error(
                f"Error rating item {item_data.get('id', 'unknown')}: {e}")
            raise

    async def _store_rating_result(self, rating_result: RatingResult):
        """Store rating result in database"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO rating_results 
                    (item_id, overall_score, criteria_scores, rating_level, 
                     confidence, timestamp, evaluator, notes)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    rating_result.item_id,
                    rating_result.overall_score,
                    json.dumps(rating_result.criteria_scores),
                    rating_result.rating_level.value,
                    rating_result.confidence,
                    rating_result.timestamp.isoformat(),
                    rating_result.evaluator,
                    rating_result.notes
                ))
                conn.commit()
        except Exception as e:
            logger.error(f"Error storing rating result: {e}")

    async def _update_item_rating(self, item_id: str, rating_score: float):
        """Update rating score in scraped_items table"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                # Get current rating for history
                cursor.execute(
                    "SELECT rating_score FROM scraped_items WHERE id = ?", (item_id,))
                result = cursor.fetchone()
                old_score = result[0] if result else 0.0

                # Update rating
                cursor.execute("""
                    UPDATE scraped_items 
                    SET rating_score = ?, processing_status = 'rated'
                    WHERE id = ?
                """, (rating_score, item_id))

                # Store in history if score changed
                if abs(old_score - rating_score) > 0.01:
                    cursor.execute("""
                        INSERT INTO rating_history 
                        (item_id, old_score, new_score, change_reason, timestamp, evaluator)
                        VALUES (?, ?, ?, ?, ?, ?)
                    """, (
                        item_id, old_score, rating_score, "Auto re-evaluation",
                        datetime.now(timezone.utc).isoformat(), "auto"
                    ))

                conn.commit()
        except Exception as e:
            logger.error(f"Error updating item rating: {e}")

    async def get_rating_summary(self) -> Dict[str, Any]:
        """Get comprehensive rating summary"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                # Overall statistics
                cursor.execute("""
                    SELECT 
                        COUNT(*) as total_rated,
                        AVG(overall_score) as avg_score,
                        MIN(overall_score) as min_score,
                        MAX(overall_score) as max_score,
                        AVG(confidence) as avg_confidence
                    FROM rating_results
                """)
                stats = cursor.fetchone()

                # Rating level distribution
                cursor.execute("""
                    SELECT rating_level, COUNT(*) 
                    FROM rating_results 
                    GROUP BY rating_level
                """)
                level_distribution = dict(cursor.fetchall())

                # Criteria averages
                cursor.execute("SELECT criteria_scores FROM rating_results")
                criteria_scores = cursor.fetchall()

                criteria_averages = {}
                if criteria_scores:
                    all_criteria = {}
                    for row in criteria_scores:
                        if row[0]:
                            criteria = json.loads(row[0])
                            for key, value in criteria.items():
                                if key not in all_criteria:
                                    all_criteria[key] = []
                                all_criteria[key].append(value)

                    for key, values in all_criteria.items():
                        criteria_averages[key] = round(np.mean(values), 3)

                # Recent ratings
                cursor.execute("""
                    SELECT COUNT(*) 
                    FROM rating_results 
                    WHERE timestamp > datetime('now', '-24 hours')
                """)
                recent_ratings = cursor.fetchone()[0]

                return {
                    'total_rated': stats[0] if stats else 0,
                    'average_score': round(stats[1], 3) if stats and stats[1] else 0,
                    'score_range': {
                        'min': round(stats[2], 3) if stats and stats[2] else 0,
                        'max': round(stats[3], 3) if stats and stats[3] else 0
                    },
                    'average_confidence': round(stats[4], 3) if stats and stats[4] else 0,
                    'rating_level_distribution': level_distribution,
                    'criteria_averages': criteria_averages,
                    'recent_ratings_24h': recent_ratings
                }

        except Exception as e:
            logger.error(f"Error getting rating summary: {e}")
            return {}

    async def get_item_rating_history(self, item_id: str) -> List[Dict[str, Any]]:
        """Get rating history for a specific item"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT old_score, new_score, change_reason, timestamp, evaluator
                    FROM rating_history 
                    WHERE item_id = ?
                    ORDER BY timestamp DESC
                """, (item_id,))

                history = []
                for row in cursor.fetchall():
                    history.append({
                        'old_score': row[0],
                        'new_score': row[1],
                        'change_reason': row[2],
                        'timestamp': row[3],
                        'evaluator': row[4]
                    })

                return history

        except Exception as e:
            logger.error(f"Error getting rating history: {e}")
            return []

    async def re_evaluate_item(self, item_id: str, evaluator: str = "manual") -> Optional[RatingResult]:
        """Re-evaluate a specific item"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT id, url, title, content, metadata, timestamp, source_url,
                           word_count, language, strategy_used, domain
                    FROM scraped_items 
                    WHERE id = ?
                """, (item_id,))

                row = cursor.fetchone()
                if not row:
                    logger.warning(
                        f"Item {item_id} not found for re-evaluation")
                    return None

                item_data = {
                    'id': row[0],
                    'url': row[1],
                    'title': row[2],
                    'content': row[3],
                    'metadata': json.loads(row[4]) if row[4] else {},
                    'timestamp': row[5],
                    'source_url': row[6],
                    'word_count': row[7],
                    'language': row[8],
                    'strategy_used': row[9],
                    'domain': row[10]
                }

                return await self.rate_item(item_data, evaluator)

        except Exception as e:
            logger.error(f"Error re-evaluating item {item_id}: {e}")
            return None

    async def get_low_quality_items(self, threshold: float = 0.4, limit: int = 50) -> List[Dict[str, Any]]:
        """Get items with low quality ratings"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT si.id, si.url, si.title, si.rating_score, 
                           si.processing_status, si.timestamp
                    FROM scraped_items si
                    WHERE si.rating_score < ? AND si.rating_score > 0
                    ORDER BY si.rating_score ASC
                    LIMIT ?
                """, (threshold, limit))

                items = []
                for row in cursor.fetchall():
                    items.append({
                        'id': row[0],
                        'url': row[1],
                        'title': row[2],
                        'rating_score': row[3],
                        'processing_status': row[4],
                        'timestamp': row[5]
                    })

                return items

        except Exception as e:
            logger.error(f"Error getting low quality items: {e}")
            return []
