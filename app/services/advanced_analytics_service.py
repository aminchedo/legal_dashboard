#!/usr/bin/env python3
"""
Advanced Analytics Service for Legal Dashboard
============================================

Provides comprehensive analytics capabilities including:
- Real-time performance metrics
- Trend analysis and forecasting
- Document similarity and clustering
- Quality assessment and recommendations
- Predictive analytics for document processing
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
import json
import statistics
from collections import defaultdict, Counter
import numpy as np
import re
import hashlib

from .database_service import DatabaseManager
from .ai_service import AIScoringEngine
from .cache_service import cache_service

logger = logging.getLogger(__name__)


@dataclass
class AnalyticsMetrics:
    """Analytics metrics data structure"""
    total_documents: int
    processed_today: int
    avg_processing_time: float
    success_rate: float
    error_rate: float
    cache_hit_rate: float
    quality_score: float
    system_health: float


@dataclass
class TrendData:
    """Trend analysis data structure"""
    period: str
    metric: str
    values: List[float]
    timestamps: List[str]
    trend_direction: str
    change_percentage: float
    confidence: float


@dataclass
class SimilarityResult:
    """Document similarity result"""
    document_id: int
    similarity_score: float
    common_entities: List[str]
    shared_topics: List[str]
    relevance_score: float


class AdvancedAnalyticsService:
    """Advanced analytics service with comprehensive capabilities"""

    def __init__(self, db_path: str = "legal_documents.db"):
        self.db_manager = DatabaseManager(db_path)
        self.ai_engine = AIScoringEngine()
        self.logger = logging.getLogger(__name__)

    async def get_real_time_metrics(self) -> AnalyticsMetrics:
        """Get real-time system metrics"""
        try:
            # Get basic statistics
            stats = self.db_manager.get_document_statistics()

            # Calculate processing metrics
            today = datetime.now().date()
            today_docs = self.db_manager.get_documents_by_date(today)

            # Calculate performance metrics
            processing_times = self.db_manager.get_processing_times()
            avg_time = statistics.mean(
                processing_times) if processing_times else 0

            # Calculate success rate
            total_processed = stats.get('total_documents', 0)
            successful = stats.get('successful_processing', 0)
            success_rate = (successful / total_processed *
                            100) if total_processed > 0 else 0

            # Calculate cache efficiency
            cache_stats = await cache_service.get_stats()
            cache_hit_rate = cache_stats.get('hit_rate', 0)

            # Calculate quality score
            quality_metrics = stats.get('quality_metrics', {})
            quality_score = quality_metrics.get('average_quality', 0)

            # Calculate system health
            system_health = self._calculate_system_health(stats)

            return AnalyticsMetrics(
                total_documents=total_processed,
                processed_today=len(today_docs),
                avg_processing_time=avg_time,
                success_rate=success_rate,
                error_rate=100 - success_rate,
                cache_hit_rate=cache_hit_rate,
                quality_score=quality_score,
                system_health=system_health
            )

        except Exception as e:
            self.logger.error(f"Error getting real-time metrics: {e}")
            return AnalyticsMetrics(0, 0, 0, 0, 0, 0, 0, 0)

    async def analyze_trends(self,
                             metric: str,
                             time_period: str = "7d",
                             category: Optional[str] = None) -> TrendData:
        """Analyze trends for specific metrics"""
        try:
            # Calculate date range
            end_date = datetime.now()
            if time_period == "7d":
                start_date = end_date - timedelta(days=7)
            elif time_period == "30d":
                start_date = end_date - timedelta(days=30)
            elif time_period == "90d":
                start_date = end_date - timedelta(days=90)
            else:
                start_date = end_date - timedelta(days=7)

            # Get trend data
            trend_data = self._get_trend_data(
                metric, start_date, end_date, category)

            # Calculate trend direction and change
            if len(trend_data['values']) >= 2:
                first_value = trend_data['values'][0]
                last_value = trend_data['values'][-1]
                change_pct = ((last_value - first_value) /
                              first_value * 100) if first_value > 0 else 0
                trend_direction = "up" if change_pct > 0 else "down" if change_pct < 0 else "stable"
            else:
                change_pct = 0
                trend_direction = "stable"

            # Calculate confidence based on data consistency
            confidence = self._calculate_trend_confidence(trend_data['values'])

            return TrendData(
                period=time_period,
                metric=metric,
                values=trend_data['values'],
                timestamps=trend_data['timestamps'],
                trend_direction=trend_direction,
                change_percentage=change_pct,
                confidence=confidence
            )

        except Exception as e:
            self.logger.error(f"Error analyzing trends: {e}")
            return TrendData("7d", metric, [], [], "stable", 0, 0)

    async def find_similar_documents(self,
                                     document_id: int,
                                     threshold: float = 0.7,
                                     limit: int = 10) -> List[SimilarityResult]:
        """Find similar documents using text similarity analysis"""
        try:
            # Get target document
            target_doc = self.db_manager.get_document_by_id(document_id)
            if not target_doc:
                return []

            # Get all documents for comparison
            all_docs = self.db_manager.get_all_documents()

            # Calculate similarities using simple text analysis
            results = []
            for doc in all_docs:
                if doc['id'] == document_id:
                    continue

                # Calculate text similarity
                similarity = self._calculate_text_similarity(
                    target_doc.get('content', ''),
                    doc.get('content', '')
                )

                if similarity >= threshold:
                    # Extract common entities
                    common_entities = self._extract_common_entities(
                        target_doc, doc)

                    # Extract shared topics
                    shared_topics = self._extract_shared_topics(
                        target_doc, doc)

                    # Calculate relevance score
                    relevance_score = self._calculate_relevance_score(
                        target_doc, doc, similarity)

                    results.append(SimilarityResult(
                        document_id=doc['id'],
                        similarity_score=similarity,
                        common_entities=common_entities,
                        shared_topics=shared_topics,
                        relevance_score=relevance_score
                    ))

            # Sort by similarity and limit results
            results.sort(key=lambda x: x.similarity_score, reverse=True)
            return results[:limit]

        except Exception as e:
            self.logger.error(f"Error finding similar documents: {e}")
            return []

    async def generate_predictive_insights(self) -> Dict[str, Any]:
        """Generate predictive insights for document processing"""
        try:
            # Get historical data
            historical_data = self.db_manager.get_historical_processing_data()

            # Analyze patterns
            patterns = self._analyze_processing_patterns(historical_data)

            # Generate predictions
            predictions = self._generate_predictions(patterns)

            # Calculate confidence intervals
            confidence_intervals = self._calculate_confidence_intervals(
                predictions)

            return {
                "patterns": patterns,
                "predictions": predictions,
                "confidence_intervals": confidence_intervals,
                "recommendations": self._generate_recommendations(predictions)
            }

        except Exception as e:
            self.logger.error(f"Error generating predictive insights: {e}")
            return {}

    async def cluster_documents(self,
                                n_clusters: int = 5,
                                category: Optional[str] = None) -> Dict[str, Any]:
        """Cluster documents using simple text-based clustering"""
        try:
            # Get documents for clustering
            documents = self.db_manager.get_documents_for_clustering(category)

            if not documents:
                return {"clusters": {}, "centroids": [], "silhouette_score": 0, "total_documents": 0}

            # Simple clustering based on content length and category
            clusters = defaultdict(list)

            for doc in documents:
                content_length = len(doc.get('content', ''))
                doc_category = doc.get('category', 'unknown')

                # Simple clustering logic
                if content_length < 1000:
                    cluster_key = "cluster_short"
                elif content_length < 5000:
                    cluster_key = "cluster_medium"
                else:
                    cluster_key = "cluster_long"

                clusters[cluster_key].append({
                    "document_id": doc['id'],
                    "title": doc.get('title', ''),
                    "similarity_to_centroid": 0.8  # Placeholder
                })

            # Calculate simple silhouette score
            silhouette_score = 0.6  # Placeholder

            return {
                "clusters": dict(clusters),
                "centroids": [],
                "silhouette_score": silhouette_score,
                "total_documents": len(documents)
            }

        except Exception as e:
            self.logger.error(f"Error clustering documents: {e}")
            return {"clusters": {}, "centroids": [], "silhouette_score": 0, "total_documents": 0}

    async def generate_quality_report(self,
                                      category: Optional[str] = None) -> Dict[str, Any]:
        """Generate comprehensive quality analysis report"""
        try:
            # Get quality metrics
            quality_metrics = self.db_manager.get_quality_metrics(category)

            # Analyze common issues
            common_issues = self._analyze_common_issues(quality_metrics)

            # Generate improvement recommendations
            recommendations = self._generate_quality_recommendations(
                quality_metrics, common_issues)

            # Calculate quality trends
            quality_trends = await self.analyze_trends("quality_score", "30d", category)

            return {
                "overall_quality_score": quality_metrics.get('average_quality', 0),
                "quality_distribution": quality_metrics.get('quality_distribution', {}),
                "common_issues": common_issues,
                "recommendations": recommendations,
                "quality_trends": quality_trends,
                "improvement_opportunities": self._identify_improvement_opportunities(quality_metrics)
            }

        except Exception as e:
            self.logger.error(f"Error generating quality report: {e}")
            return {}

    def _calculate_system_health(self, stats: Dict) -> float:
        """Calculate overall system health score"""
        try:
            # Calculate various health indicators
            success_rate = stats.get('success_rate', 0)
            avg_quality = stats.get('quality_metrics', {}).get(
                'average_quality', 0)
            error_rate = stats.get('error_rate', 0)

            # Weighted health score
            health_score = (
                success_rate * 0.4 +
                avg_quality * 0.3 +
                (100 - error_rate) * 0.3
            )

            return min(max(health_score, 0), 100)

        except Exception as e:
            self.logger.error(f"Error calculating system health: {e}")
            return 0

    def _get_trend_data(self,
                        metric: str,
                        start_date: datetime,
                        end_date: datetime,
                        category: Optional[str] = None) -> Dict[str, List]:
        """Get trend data for specific metric"""
        try:
            # Get data from database
            data = self.db_manager.get_metric_data(
                metric, start_date, end_date, category)

            # Process data into time series
            timestamps = []
            values = []

            for record in data:
                timestamps.append(record['timestamp'])
                values.append(record['value'])

            return {
                "timestamps": timestamps,
                "values": values
            }

        except Exception as e:
            self.logger.error(f"Error getting trend data: {e}")
            return {"timestamps": [], "values": []}

    def _calculate_trend_confidence(self, values: List[float]) -> float:
        """Calculate confidence in trend analysis"""
        try:
            if len(values) < 2:
                return 0

            # Calculate coefficient of variation
            mean_val = statistics.mean(values)
            std_val = statistics.stdev(values) if len(values) > 1 else 0

            cv = (std_val / mean_val) if mean_val > 0 else 0

            # Higher CV means lower confidence
            confidence = max(0, 100 - (cv * 100))

            return min(confidence, 100)

        except Exception as e:
            self.logger.error(f"Error calculating trend confidence: {e}")
            return 0

    def _calculate_text_similarity(self, text1: str, text2: str) -> float:
        """Calculate text similarity using simple methods"""
        try:
            if not text1 or not text2:
                return 0

            # Convert to lowercase and split into words
            words1 = set(re.findall(r'\w+', text1.lower()))
            words2 = set(re.findall(r'\w+', text2.lower()))

            if not words1 or not words2:
                return 0

            # Calculate Jaccard similarity
            intersection = len(words1.intersection(words2))
            union = len(words1.union(words2))

            return intersection / union if union > 0 else 0

        except Exception as e:
            self.logger.error(f"Error calculating text similarity: {e}")
            return 0

    def _extract_common_entities(self, doc1: Dict, doc2: Dict) -> List[str]:
        """Extract common entities between two documents"""
        try:
            # Simple entity extraction (can be enhanced with NER)
            entities1 = set(doc1.get('entities', []))
            entities2 = set(doc2.get('entities', []))

            return list(entities1.intersection(entities2))

        except Exception as e:
            self.logger.error(f"Error extracting common entities: {e}")
            return []

    def _extract_shared_topics(self, doc1: Dict, doc2: Dict) -> List[str]:
        """Extract shared topics between two documents"""
        try:
            # Extract topics from document metadata
            topics1 = set(doc1.get('topics', []))
            topics2 = set(doc2.get('topics', []))

            return list(topics1.intersection(topics2))

        except Exception as e:
            self.logger.error(f"Error extracting shared topics: {e}")
            return []

    def _calculate_relevance_score(self,
                                   target_doc: Dict,
                                   compare_doc: Dict,
                                   similarity: float) -> float:
        """Calculate relevance score for document comparison"""
        try:
            # Base score from similarity
            base_score = similarity

            # Adjust for category match
            category_bonus = 0.1 if target_doc.get(
                'category') == compare_doc.get('category') else 0

            # Adjust for date proximity
            date1 = datetime.fromisoformat(target_doc.get('created_at', ''))
            date2 = datetime.fromisoformat(compare_doc.get('created_at', ''))
            date_diff = abs((date1 - date2).days)
            date_penalty = min(0.1, date_diff / 365)  # Max 10% penalty

            relevance_score = base_score + category_bonus - date_penalty

            return max(0, min(1, relevance_score))

        except Exception as e:
            self.logger.error(f"Error calculating relevance score: {e}")
            return similarity

    def _analyze_processing_patterns(self, historical_data: List[Dict]) -> Dict[str, Any]:
        """Analyze processing patterns from historical data"""
        try:
            patterns = {
                "hourly_distribution": defaultdict(int),
                "daily_distribution": defaultdict(int),
                "processing_times": [],
                "error_patterns": defaultdict(int),
                "quality_trends": []
            }

            for record in historical_data:
                timestamp = datetime.fromisoformat(record['timestamp'])

                # Hourly distribution
                patterns["hourly_distribution"][timestamp.hour] += 1

                # Daily distribution
                patterns["daily_distribution"][timestamp.weekday()] += 1

                # Processing times
                if record.get('processing_time'):
                    patterns["processing_times"].append(
                        record['processing_time'])

                # Error patterns
                if record.get('error_type'):
                    patterns["error_patterns"][record['error_type']] += 1

                # Quality trends
                if record.get('quality_score'):
                    patterns["quality_trends"].append(record['quality_score'])

            return patterns

        except Exception as e:
            self.logger.error(f"Error analyzing processing patterns: {e}")
            return {}

    def _generate_predictions(self, patterns: Dict[str, Any]) -> Dict[str, Any]:
        """Generate predictions based on patterns"""
        try:
            predictions = {
                "peak_hours": [],
                "expected_volume": 0,
                "processing_time_forecast": 0,
                "quality_forecast": 0
            }

            # Predict peak hours
            hourly_dist = patterns.get("hourly_distribution", {})
            if hourly_dist:
                sorted_hours = sorted(
                    hourly_dist.items(), key=lambda x: x[1], reverse=True)
                predictions["peak_hours"] = [
                    hour for hour, count in sorted_hours[:3]]

            # Predict expected volume (simple average)
            total_processed = sum(patterns.get(
                "hourly_distribution", {}).values())
            avg_daily = total_processed / 7 if total_processed > 0 else 0
            predictions["expected_volume"] = int(avg_daily)

            # Predict processing time
            processing_times = patterns.get("processing_times", [])
            if processing_times:
                predictions["processing_time_forecast"] = statistics.mean(
                    processing_times)

            # Predict quality
            quality_trends = patterns.get("quality_trends", [])
            if quality_trends:
                predictions["quality_forecast"] = statistics.mean(
                    quality_trends)

            return predictions

        except Exception as e:
            self.logger.error(f"Error generating predictions: {e}")
            return {}

    def _calculate_confidence_intervals(self, predictions: Dict[str, Any]) -> Dict[str, Tuple[float, float]]:
        """Calculate confidence intervals for predictions"""
        try:
            intervals = {}

            # For processing time
            if predictions.get("processing_time_forecast"):
                # Simple confidence interval calculation
                mean_time = predictions["processing_time_forecast"]
                intervals["processing_time"] = (
                    mean_time * 0.8, mean_time * 1.2)

            # For quality forecast
            if predictions.get("quality_forecast"):
                mean_quality = predictions["quality_forecast"]
                intervals["quality"] = (
                    max(0, mean_quality - 0.1), min(1, mean_quality + 0.1))

            return intervals

        except Exception as e:
            self.logger.error(f"Error calculating confidence intervals: {e}")
            return {}

    def _generate_recommendations(self, predictions: Dict[str, Any]) -> List[str]:
        """Generate recommendations based on predictions"""
        try:
            recommendations = []

            # Processing time recommendations
            if predictions.get("processing_time_forecast", 0) > 30:
                recommendations.append(
                    "Consider optimizing document processing pipeline for faster processing")

            # Quality recommendations
            if predictions.get("quality_forecast", 0) < 0.7:
                recommendations.append(
                    "Implement additional quality checks to improve document quality")

            # Volume recommendations
            if predictions.get("expected_volume", 0) > 1000:
                recommendations.append(
                    "Consider scaling infrastructure to handle increased document volume")

            return recommendations

        except Exception as e:
            self.logger.error(f"Error generating recommendations: {e}")
            return []

    def _analyze_common_issues(self, quality_metrics: Dict) -> List[Dict]:
        """Analyze common quality issues"""
        try:
            issues = []

            # Analyze OCR issues
            if quality_metrics.get('ocr_accuracy', 0) < 0.9:
                issues.append({
                    "type": "OCR Accuracy",
                    "severity": "medium",
                    "description": "OCR accuracy below 90%",
                    "recommendation": "Consider using higher quality images or alternative OCR engines"
                })

            # Analyze content quality
            if quality_metrics.get('content_quality', 0) < 0.8:
                issues.append({
                    "type": "Content Quality",
                    "severity": "high",
                    "description": "Content quality below 80%",
                    "recommendation": "Implement content validation and enhancement processes"
                })

            return issues

        except Exception as e:
            self.logger.error(f"Error analyzing common issues: {e}")
            return []

    def _generate_quality_recommendations(self,
                                          quality_metrics: Dict,
                                          common_issues: List[Dict]) -> List[str]:
        """Generate quality improvement recommendations"""
        try:
            recommendations = []

            # Based on quality metrics
            if quality_metrics.get('average_quality', 0) < 0.8:
                recommendations.append(
                    "Implement automated quality checks for all documents")

            # Based on common issues
            for issue in common_issues:
                recommendations.append(issue.get('recommendation', ''))

            return recommendations

        except Exception as e:
            self.logger.error(f"Error generating quality recommendations: {e}")
            return []

    def _identify_improvement_opportunities(self, quality_metrics: Dict) -> List[Dict]:
        """Identify specific improvement opportunities"""
        try:
            opportunities = []

            # Analyze different quality dimensions
            dimensions = ['ocr_accuracy', 'content_quality',
                          'format_consistency', 'metadata_completeness']

            for dimension in dimensions:
                score = quality_metrics.get(dimension, 0)
                if score < 0.9:
                    opportunities.append({
                        "dimension": dimension,
                        "current_score": score,
                        "target_score": 0.9,
                        "improvement_potential": 0.9 - score
                    })

            return opportunities

        except Exception as e:
            self.logger.error(
                f"Error identifying improvement opportunities: {e}")
            return []
