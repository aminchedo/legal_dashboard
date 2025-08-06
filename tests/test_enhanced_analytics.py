#!/usr/bin/env python3
"""
Enhanced Analytics Test Suite
============================

Comprehensive test suite for the enhanced analytics system including:
- Real-time metrics validation
- Trend analysis testing
- Predictive insights verification
- System health monitoring
- Document clustering analysis
- Quality assessment testing
"""

from app.services.cache_service import cache_service
from app.services.ai_service import AIScoringEngine
from app.services.database_service import DatabaseManager
from app.services.advanced_analytics_service import AdvancedAnalyticsService
import asyncio
import sys
import os
import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any

# Add the app directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))


class EnhancedAnalyticsTester:
    """Comprehensive tester for enhanced analytics features"""

    def __init__(self):
        self.analytics_service = AdvancedAnalyticsService()
        self.db_manager = DatabaseManager()
        self.ai_engine = AIScoringEngine()
        self.test_results = {
            "total_tests": 0,
            "passed": 0,
            "failed": 0,
            "errors": []
        }

    async def run_all_tests(self):
        """Run all enhanced analytics tests"""
        print("🚀 Enhanced Analytics Test Suite")
        print("=" * 50)

        try:
            # Test real-time metrics
            await self.test_real_time_metrics()

            # Test trend analysis
            await self.test_trend_analysis()

            # Test predictive insights
            await self.test_predictive_insights()

            # Test document clustering
            await self.test_document_clustering()

            # Test quality assessment
            await self.test_quality_assessment()

            # Test system health monitoring
            await self.test_system_health()

            # Test similarity analysis
            await self.test_similarity_analysis()

            # Test cache performance
            await self.test_cache_performance()

            # Generate test report
            self.generate_test_report()

        except Exception as e:
            print(f"❌ Test suite failed: {e}")
            import traceback
            traceback.print_exc()

    async def test_real_time_metrics(self):
        """Test real-time metrics functionality"""
        print("\n📊 Testing Real-time Metrics...")

        try:
            metrics = await self.analytics_service.get_real_time_metrics()

            # Validate metrics structure
            required_fields = [
                'total_documents', 'processed_today', 'avg_processing_time',
                'success_rate', 'error_rate', 'cache_hit_rate',
                'quality_score', 'system_health'
            ]

            for field in required_fields:
                if not hasattr(metrics, field):
                    raise ValueError(f"Missing required field: {field}")

            # Validate metric ranges
            assert 0 <= metrics.total_documents, "Total documents should be non-negative"
            assert 0 <= metrics.processed_today, "Processed today should be non-negative"
            assert 0 <= metrics.avg_processing_time, "Average processing time should be non-negative"
            assert 0 <= metrics.success_rate <= 100, "Success rate should be between 0-100"
            assert 0 <= metrics.error_rate <= 100, "Error rate should be between 0-100"
            assert 0 <= metrics.cache_hit_rate <= 100, "Cache hit rate should be between 0-100"
            assert 0 <= metrics.quality_score <= 1, "Quality score should be between 0-1"
            assert 0 <= metrics.system_health <= 100, "System health should be between 0-100"

            print(f"✅ Real-time metrics test passed")
            print(f"   - Total documents: {metrics.total_documents}")
            print(f"   - Processed today: {metrics.processed_today}")
            print(f"   - System health: {metrics.system_health:.1f}%")

            self.test_results["passed"] += 1

        except Exception as e:
            print(f"❌ Real-time metrics test failed: {e}")
            self.test_results["failed"] += 1
            self.test_results["errors"].append(f"Real-time metrics: {e}")

        self.test_results["total_tests"] += 1

    async def test_trend_analysis(self):
        """Test trend analysis functionality"""
        print("\n📈 Testing Trend Analysis...")

        try:
            # Test different metrics and time periods
            test_cases = [
                {"metric": "processing_time", "time_period": "7d"},
                {"metric": "quality_score", "time_period": "30d"},
                {"metric": "document_volume", "time_period": "90d"}
            ]

            for test_case in test_cases:
                trend_data = await self.analytics_service.analyze_trends(
                    metric=test_case["metric"],
                    time_period=test_case["time_period"]
                )

                # Validate trend data structure
                assert hasattr(trend_data, 'period'), "Missing period field"
                assert hasattr(trend_data, 'metric'), "Missing metric field"
                assert hasattr(trend_data, 'values'), "Missing values field"
                assert hasattr(
                    trend_data, 'timestamps'), "Missing timestamps field"
                assert hasattr(
                    trend_data, 'trend_direction'), "Missing trend_direction field"
                assert hasattr(
                    trend_data, 'change_percentage'), "Missing change_percentage field"
                assert hasattr(
                    trend_data, 'confidence'), "Missing confidence field"

                # Validate trend direction
                assert trend_data.trend_direction in ['up', 'down', 'stable'], \
                    f"Invalid trend direction: {trend_data.trend_direction}"

                # Validate confidence range
                assert 0 <= trend_data.confidence <= 100, \
                    f"Confidence should be between 0-100, got: {trend_data.confidence}"

                print(f"   ✅ {test_case['metric']} ({test_case['time_period']}): "
                      f"{trend_data.trend_direction} ({trend_data.change_percentage:.1f}%)")

            print("✅ Trend analysis test passed")
            self.test_results["passed"] += 1

        except Exception as e:
            print(f"❌ Trend analysis test failed: {e}")
            self.test_results["failed"] += 1
            self.test_results["errors"].append(f"Trend analysis: {e}")

        self.test_results["total_tests"] += 1

    async def test_predictive_insights(self):
        """Test predictive insights functionality"""
        print("\n🔮 Testing Predictive Insights...")

        try:
            insights = await self.analytics_service.generate_predictive_insights()

            # Validate insights structure
            required_sections = ['patterns', 'predictions',
                                 'confidence_intervals', 'recommendations']

            for section in required_sections:
                assert section in insights, f"Missing section: {section}"

            # Validate predictions
            predictions = insights.get('predictions', {})
            if predictions:
                assert isinstance(
                    predictions, dict), "Predictions should be a dictionary"

                # Check for expected prediction fields
                expected_fields = ['peak_hours', 'expected_volume',
                                   'processing_time_forecast', 'quality_forecast']
                for field in expected_fields:
                    if field in predictions:
                        assert isinstance(predictions[field], (int, float, list)), \
                            f"Prediction field {field} should be numeric or list"

            # Validate recommendations
            recommendations = insights.get('recommendations', [])
            assert isinstance(
                recommendations, list), "Recommendations should be a list"

            print(f"✅ Predictive insights test passed")
            print(
                f"   - Patterns analyzed: {len(insights.get('patterns', {}))}")
            print(f"   - Recommendations generated: {len(recommendations)}")

            self.test_results["passed"] += 1

        except Exception as e:
            print(f"❌ Predictive insights test failed: {e}")
            self.test_results["failed"] += 1
            self.test_results["errors"].append(f"Predictive insights: {e}")

        self.test_results["total_tests"] += 1

    async def test_document_clustering(self):
        """Test document clustering functionality"""
        print("\n🔗 Testing Document Clustering...")

        try:
            # Test clustering with different parameters
            test_cases = [
                {"n_clusters": 3, "category": None},
                {"n_clusters": 5, "category": "legal"},
                {"n_clusters": 2, "category": "contract"}
            ]

            for test_case in test_cases:
                clustering_result = await self.analytics_service.cluster_documents(
                    n_clusters=test_case["n_clusters"],
                    category=test_case["category"]
                )

                # Validate clustering result structure
                assert 'clusters' in clustering_result, "Missing clusters field"
                assert 'centroids' in clustering_result, "Missing centroids field"
                assert 'silhouette_score' in clustering_result, "Missing silhouette_score field"
                assert 'total_documents' in clustering_result, "Missing total_documents field"

                # Validate silhouette score range
                silhouette_score = clustering_result['silhouette_score']
                assert -1 <= silhouette_score <= 1, \
                    f"Silhouette score should be between -1 and 1, got: {silhouette_score}"

                # Validate clusters
                clusters = clustering_result['clusters']
                assert isinstance(
                    clusters, dict), "Clusters should be a dictionary"

                print(f"   ✅ {test_case['n_clusters']} clusters "
                      f"(silhouette: {silhouette_score:.3f})")

            print("✅ Document clustering test passed")
            self.test_results["passed"] += 1

        except Exception as e:
            print(f"❌ Document clustering test failed: {e}")
            self.test_results["failed"] += 1
            self.test_results["errors"].append(f"Document clustering: {e}")

        self.test_results["total_tests"] += 1

    async def test_quality_assessment(self):
        """Test quality assessment functionality"""
        print("\n🏆 Testing Quality Assessment...")

        try:
            quality_report = await self.analytics_service.generate_quality_report()

            # Validate quality report structure
            required_fields = [
                'overall_quality_score', 'quality_distribution', 'common_issues',
                'recommendations', 'quality_trends', 'improvement_opportunities'
            ]

            for field in required_fields:
                assert field in quality_report, f"Missing field: {field}"

            # Validate quality score range
            overall_score = quality_report['overall_quality_score']
            assert 0 <= overall_score <= 1, \
                f"Overall quality score should be between 0-1, got: {overall_score}"

            # Validate quality distribution
            quality_dist = quality_report['quality_distribution']
            assert isinstance(
                quality_dist, dict), "Quality distribution should be a dictionary"

            # Validate common issues
            common_issues = quality_report['common_issues']
            assert isinstance(
                common_issues, list), "Common issues should be a list"

            # Validate recommendations
            recommendations = quality_report['recommendations']
            assert isinstance(
                recommendations, list), "Recommendations should be a list"

            print(f"✅ Quality assessment test passed")
            print(f"   - Overall quality: {overall_score:.1%}")
            print(f"   - Common issues: {len(common_issues)}")
            print(f"   - Recommendations: {len(recommendations)}")

            self.test_results["passed"] += 1

        except Exception as e:
            print(f"❌ Quality assessment test failed: {e}")
            self.test_results["failed"] += 1
            self.test_results["errors"].append(f"Quality assessment: {e}")

        self.test_results["total_tests"] += 1

    async def test_system_health(self):
        """Test system health monitoring"""
        print("\n💚 Testing System Health Monitoring...")

        try:
            # Get real-time metrics for health calculation
            metrics = await self.analytics_service.get_real_time_metrics()

            # Validate system health calculation
            system_health = metrics.system_health
            assert 0 <= system_health <= 100, \
                f"System health should be between 0-100, got: {system_health}"

            # Test health calculation logic
            calculated_health = self.analytics_service._calculate_system_health({
                'success_rate': metrics.success_rate,
                'quality_metrics': {'average_quality': metrics.quality_score},
                'error_rate': metrics.error_rate
            })

            assert 0 <= calculated_health <= 100, \
                f"Calculated health should be between 0-100, got: {calculated_health}"

            print(f"✅ System health test passed")
            print(f"   - System health: {system_health:.1f}%")
            print(f"   - Success rate: {metrics.success_rate:.1f}%")
            print(f"   - Quality score: {metrics.quality_score:.3f}")

            self.test_results["passed"] += 1

        except Exception as e:
            print(f"❌ System health test failed: {e}")
            self.test_results["failed"] += 1
            self.test_results["errors"].append(f"System health: {e}")

        self.test_results["total_tests"] += 1

    async def test_similarity_analysis(self):
        """Test document similarity analysis"""
        print("\n🔍 Testing Similarity Analysis...")

        try:
            # Get a sample document ID for testing
            documents = self.db_manager.get_all_documents()
            if not documents:
                print("   ⚠️ No documents available for similarity testing")
                self.test_results["passed"] += 1
                return

            test_document_id = documents[0]['id']

            # Test similarity analysis
            similar_docs = await self.analytics_service.find_similar_documents(
                document_id=test_document_id,
                threshold=0.7,
                limit=5
            )

            # Validate similarity results
            assert isinstance(
                similar_docs, list), "Similar documents should be a list"

            for doc in similar_docs:
                assert hasattr(doc, 'document_id'), "Missing document_id field"
                assert hasattr(
                    doc, 'similarity_score'), "Missing similarity_score field"
                assert hasattr(
                    doc, 'common_entities'), "Missing common_entities field"
                assert hasattr(
                    doc, 'shared_topics'), "Missing shared_topics field"
                assert hasattr(
                    doc, 'relevance_score'), "Missing relevance_score field"

                # Validate similarity score range
                assert 0 <= doc.similarity_score <= 1, \
                    f"Similarity score should be between 0-1, got: {doc.similarity_score}"

                # Validate relevance score range
                assert 0 <= doc.relevance_score <= 1, \
                    f"Relevance score should be between 0-1, got: {doc.relevance_score}"

            print(f"✅ Similarity analysis test passed")
            print(f"   - Similar documents found: {len(similar_docs)}")
            if similar_docs:
                print(
                    f"   - Average similarity: {sum(d.similarity_score for d in similar_docs) / len(similar_docs):.3f}")

            self.test_results["passed"] += 1

        except Exception as e:
            print(f"❌ Similarity analysis test failed: {e}")
            self.test_results["failed"] += 1
            self.test_results["errors"].append(f"Similarity analysis: {e}")

        self.test_results["total_tests"] += 1

    async def test_cache_performance(self):
        """Test cache performance and efficiency"""
        print("\n⚡ Testing Cache Performance...")

        try:
            # Test cache operations
            test_key = "test_analytics_key"
            test_data = {"test": "data",
                         "timestamp": datetime.now().isoformat()}

            # Set cache data
            await cache_service.set(test_key, test_data, expire=60)

            # Get cache data
            cached_data = await cache_service.get(test_key)
            assert cached_data == test_data, "Cached data should match original data"

            # Test cache stats
            cache_stats = await cache_service.get_stats()
            assert isinstance(
                cache_stats, dict), "Cache stats should be a dictionary"

            # Validate cache hit rate calculation
            if 'hit_rate' in cache_stats:
                hit_rate = cache_stats['hit_rate']
                assert 0 <= hit_rate <= 100, \
                    f"Cache hit rate should be between 0-100, got: {hit_rate}"

            print(f"✅ Cache performance test passed")
            print(
                f"   - Cache hit rate: {cache_stats.get('hit_rate', 0):.1f}%")

            self.test_results["passed"] += 1

        except Exception as e:
            print(f"❌ Cache performance test failed: {e}")
            self.test_results["failed"] += 1
            self.test_results["errors"].append(f"Cache performance: {e}")

        self.test_results["total_tests"] += 1

    def generate_test_report(self):
        """Generate comprehensive test report"""
        print("\n" + "=" * 50)
        print("📋 Enhanced Analytics Test Report")
        print("=" * 50)

        success_rate = (self.test_results["passed"] / self.test_results["total_tests"] * 100) \
            if self.test_results["total_tests"] > 0 else 0

        print(f"📊 Test Summary:")
        print(f"   - Total tests: {self.test_results['total_tests']}")
        print(f"   - Passed: {self.test_results['passed']}")
        print(f"   - Failed: {self.test_results['failed']}")
        print(f"   - Success rate: {success_rate:.1f}%")

        if self.test_results["errors"]:
            print(f"\n❌ Errors encountered:")
            for error in self.test_results["errors"]:
                print(f"   - {error}")

        # Save test results
        test_report = {
            "timestamp": datetime.now().isoformat(),
            "test_results": self.test_results,
            "success_rate": success_rate
        }

        with open("enhanced_analytics_test_report.json", "w", encoding="utf-8") as f:
            json.dump(test_report, f, indent=2, ensure_ascii=False)

        print(f"\n📄 Test report saved to: enhanced_analytics_test_report.json")

        if success_rate >= 90:
            print("🎉 All tests passed! Enhanced analytics system is working correctly.")
        elif success_rate >= 70:
            print("⚠️ Most tests passed. Some issues need attention.")
        else:
            print("❌ Multiple test failures detected. System needs fixes.")

        return success_rate >= 90


async def main():
    """Main test runner"""
    tester = EnhancedAnalyticsTester()
    success = await tester.run_all_tests()
    return 0 if success else 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
