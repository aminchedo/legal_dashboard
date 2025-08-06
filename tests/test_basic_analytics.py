#!/usr/bin/env python3
"""
Basic Analytics Test Suite
=========================

Simple test suite for core analytics functionality without heavy dependencies.
"""

from app.services.cache_service import cache_service
from app.services.database_service import DatabaseManager
import asyncio
import sys
import os
import json
from datetime import datetime, timedelta
from typing import Dict, List, Any

# Add the app directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))


class BasicAnalyticsTester:
    """Basic tester for core analytics features"""

    def __init__(self):
        self.db_manager = DatabaseManager()
        self.test_results = {
            "total_tests": 0,
            "passed": 0,
            "failed": 0,
            "errors": []
        }

    async def run_all_tests(self):
        """Run all basic analytics tests"""
        print("🚀 Basic Analytics Test Suite")
        print("=" * 50)

        try:
            # Test database connectivity
            await self.test_database_connectivity()

            # Test cache functionality
            await self.test_cache_functionality()

            # Test basic metrics calculation
            await self.test_basic_metrics()

            # Test document operations
            await self.test_document_operations()

            # Generate test report
            self.generate_test_report()

        except Exception as e:
            print(f"❌ Test suite failed: {e}")
            import traceback
            traceback.print_exc()

    async def test_database_connectivity(self):
        """Test database connectivity and basic operations"""
        print("\n🗄️ Testing Database Connectivity...")

        try:
            # Test database connection
            is_connected = self.db_manager.is_connected()
            assert is_connected, "Database should be connected"

            # Test basic statistics
            stats = self.db_manager.get_document_statistics()
            assert isinstance(stats, dict), "Statistics should be a dictionary"

            print(f"✅ Database connectivity test passed")
            print(f"   - Connected: {is_connected}")
            print(f"   - Statistics keys: {list(stats.keys())}")

            self.test_results["passed"] += 1

        except Exception as e:
            print(f"❌ Database connectivity test failed: {e}")
            self.test_results["failed"] += 1
            self.test_results["errors"].append(f"Database connectivity: {e}")

        self.test_results["total_tests"] += 1

    async def test_cache_functionality(self):
        """Test cache functionality"""
        print("\n⚡ Testing Cache Functionality...")

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

            print(f"✅ Cache functionality test passed")
            print(
                f"   - Cache hit rate: {cache_stats.get('hit_rate', 0):.1f}%")

            self.test_results["passed"] += 1

        except Exception as e:
            print(f"❌ Cache functionality test failed: {e}")
            self.test_results["failed"] += 1
            self.test_results["errors"].append(f"Cache functionality: {e}")

        self.test_results["total_tests"] += 1

    async def test_basic_metrics(self):
        """Test basic metrics calculation"""
        print("\n📊 Testing Basic Metrics...")

        try:
            # Get document statistics
            stats = self.db_manager.get_document_statistics()

            # Test basic metric calculations
            total_docs = stats.get('total_documents', 0)
            assert isinstance(
                total_docs, int), "Total documents should be an integer"
            assert total_docs >= 0, "Total documents should be non-negative"

            # Test quality metrics
            quality_metrics = stats.get('quality_metrics', {})
            assert isinstance(
                quality_metrics, dict), "Quality metrics should be a dictionary"

            # Test category distribution
            category_dist = stats.get('category_distribution', {})
            assert isinstance(
                category_dist, dict), "Category distribution should be a dictionary"

            print(f"✅ Basic metrics test passed")
            print(f"   - Total documents: {total_docs}")
            print(f"   - Quality metrics: {len(quality_metrics)}")
            print(f"   - Categories: {len(category_dist)}")

            self.test_results["passed"] += 1

        except Exception as e:
            print(f"❌ Basic metrics test failed: {e}")
            self.test_results["failed"] += 1
            self.test_results["errors"].append(f"Basic metrics: {e}")

        self.test_results["total_tests"] += 1

    async def test_document_operations(self):
        """Test document operations"""
        print("\n📄 Testing Document Operations...")

        try:
            # Test getting all documents
            all_docs = self.db_manager.get_all_documents()
            assert isinstance(all_docs, list), "All documents should be a list"

            # Test getting documents by date
            today = datetime.now().date()
            today_docs = self.db_manager.get_documents_by_date(today)
            assert isinstance(
                today_docs, list), "Today's documents should be a list"

            # Test getting processing times
            processing_times = self.db_manager.get_processing_times()
            assert isinstance(processing_times,
                              list), "Processing times should be a list"

            print(f"✅ Document operations test passed")
            print(f"   - Total documents: {len(all_docs)}")
            print(f"   - Today's documents: {len(today_docs)}")
            print(f"   - Processing times: {len(processing_times)}")

            self.test_results["passed"] += 1

        except Exception as e:
            print(f"❌ Document operations test failed: {e}")
            self.test_results["failed"] += 1
            self.test_results["errors"].append(f"Document operations: {e}")

        self.test_results["total_tests"] += 1

    def generate_test_report(self):
        """Generate comprehensive test report"""
        print("\n" + "=" * 50)
        print("📋 Basic Analytics Test Report")
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

        with open("basic_analytics_test_report.json", "w", encoding="utf-8") as f:
            json.dump(test_report, f, indent=2, ensure_ascii=False)

        print(f"\n📄 Test report saved to: basic_analytics_test_report.json")

        if success_rate >= 90:
            print("🎉 All tests passed! Basic analytics system is working correctly.")
        elif success_rate >= 70:
            print("⚠️ Most tests passed. Some issues need attention.")
        else:
            print("❌ Multiple test failures detected. System needs fixes.")

        return success_rate >= 90


async def main():
    """Main test runner"""
    tester = BasicAnalyticsTester()
    success = await tester.run_all_tests()
    return 0 if success else 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
