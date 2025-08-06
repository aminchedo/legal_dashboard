#!/usr/bin/env python3
"""
Integration Test for Legal Dashboard System
==========================================

Comprehensive test suite to validate all system components including:
- Service integration
- Background tasks
- API endpoints
- Database operations
- Scraping and rating functionality
"""

import asyncio
import json
import logging
import os
import sys
import time
from pathlib import Path
from typing import Dict, List, Any

# Add the app directory to the path
sys.path.insert(0, str(Path(__file__).parent / "app"))

from fastapi.testclient import TestClient
from app.main import app
from app.services.scraping_service import ScrapingService, ScrapingStrategy
from app.services.rating_service import RatingService
from app.services.database_service import DatabaseManager

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class LegalDashboardIntegrationTest:
    """Comprehensive integration test for Legal Dashboard system"""
    
    def __init__(self):
        self.client = TestClient(app)
        self.test_results = {}
        self.start_time = time.time()
        
    def run_all_tests(self) -> Dict[str, Any]:
        """Run all integration tests"""
        logger.info("🚀 Starting Legal Dashboard Integration Tests...")
        
        try:
            # Test 1: System Health
            self.test_system_health()
            
            # Test 2: Service Initialization
            self.test_service_initialization()
            
            # Test 3: Database Operations
            self.test_database_operations()
            
            # Test 4: Scraping Service
            self.test_scraping_service()
            
            # Test 5: Rating Service
            self.test_rating_service()
            
            # Test 6: API Endpoints
            self.test_api_endpoints()
            
            # Test 7: Background Tasks
            self.test_background_tasks()
            
            # Test 8: Persian Language Support
            self.test_persian_support()
            
            # Test 9: Error Handling
            self.test_error_handling()
            
            # Test 10: Performance
            self.test_performance()
            
            self.generate_report()
            return self.test_results
            
        except Exception as e:
            logger.error(f"❌ Integration test failed: {e}")
            self.test_results["overall_status"] = "FAILED"
            self.test_results["error"] = str(e)
            return self.test_results
    
    def test_system_health(self):
        """Test system health endpoint"""
        logger.info("🔍 Testing system health...")
        
        try:
            response = self.client.get("/api/health")
            assert response.status_code == 200
            
            data = response.json()
            assert "status" in data
            assert "services" in data
            assert "version" in data
            
            # Check if all services are healthy
            services = data.get("services", {})
            healthy_services = sum(1 for status in services.values() if status == "healthy")
            total_services = len(services)
            
            logger.info(f"✅ Health check passed: {healthy_services}/{total_services} services healthy")
            self.test_results["system_health"] = "PASSED"
            
        except Exception as e:
            logger.error(f"❌ Health check failed: {e}")
            self.test_results["system_health"] = "FAILED"
    
    def test_service_initialization(self):
        """Test service initialization"""
        logger.info("🔧 Testing service initialization...")
        
        try:
            # Test database service
            db_manager = DatabaseManager()
            db_manager.initialize()
            assert db_manager.is_connected()
            
            # Test scraping service
            scraping_service = ScrapingService(db_path=":memory:")
            assert scraping_service is not None
            
            # Test rating service
            rating_service = RatingService(db_path=":memory:")
            assert rating_service is not None
            
            logger.info("✅ Service initialization passed")
            self.test_results["service_initialization"] = "PASSED"
            
        except Exception as e:
            logger.error(f"❌ Service initialization failed: {e}")
            self.test_results["service_initialization"] = "FAILED"
    
    def test_database_operations(self):
        """Test database operations"""
        logger.info("💾 Testing database operations...")
        
        try:
            db_manager = DatabaseManager()
            db_manager.initialize()
            
            # Test document insertion
            test_doc = {
                "title": "Test Legal Document",
                "content": "This is a test legal document content.",
                "category": "test",
                "file_size": 1024,
                "file_type": "txt"
            }
            
            doc_id = db_manager.add_document(test_doc)
            assert doc_id is not None
            
            # Test document retrieval
            retrieved_doc = db_manager.get_document(doc_id)
            assert retrieved_doc is not None
            assert retrieved_doc["title"] == test_doc["title"]
            
            # Test document search
            search_results = db_manager.search_documents("test")
            assert len(search_results) > 0
            
            logger.info("✅ Database operations passed")
            self.test_results["database_operations"] = "PASSED"
            
        except Exception as e:
            logger.error(f"❌ Database operations failed: {e}")
            self.test_results["database_operations"] = "FAILED"
    
    async def test_scraping_service(self):
        """Test scraping service functionality"""
        logger.info("🔍 Testing scraping service...")
        
        try:
            scraping_service = ScrapingService(db_path=":memory:")
            
            # Test scraping job creation
            test_urls = ["https://example.com"]
            job_id = await scraping_service.start_scraping_job(
                urls=test_urls,
                strategy=ScrapingStrategy.LEGAL_DOCUMENTS,
                keywords=["قانون", "حقوق"]
            )
            
            assert job_id is not None
            
            # Test job status retrieval
            job_status = await scraping_service.get_job_status(job_id)
            assert job_status is not None
            assert "status" in job_status
            
            # Test statistics
            stats = await scraping_service.get_scraping_statistics()
            assert isinstance(stats, dict)
            
            logger.info("✅ Scraping service passed")
            self.test_results["scraping_service"] = "PASSED"
            
        except Exception as e:
            logger.error(f"❌ Scraping service failed: {e}")
            self.test_results["scraping_service"] = "FAILED"
    
    async def test_rating_service(self):
        """Test rating service functionality"""
        logger.info("⭐ Testing rating service...")
        
        try:
            rating_service = RatingService(db_path=":memory:")
            
            # Test item rating
            test_item = {
                "id": "test_item_1",
                "url": "https://example.com/test",
                "title": "Test Legal Document",
                "content": "This is a test legal document with Persian content قانون تجارت",
                "metadata": {"source": "test"},
                "timestamp": "2024-01-15T10:00:00Z",
                "source_url": "https://example.com",
                "word_count": 50,
                "language": "fa",
                "strategy_used": "legal_documents",
                "domain": "example.com"
            }
            
            rating_result = await rating_service.rate_item(test_item, "test_evaluator")
            assert rating_result is not None
            assert hasattr(rating_result, 'overall_score')
            assert 0 <= rating_result.overall_score <= 1
            
            # Test rating summary
            summary = await rating_service.get_rating_summary()
            assert isinstance(summary, dict)
            
            # Test unrated items
            unrated_items = await rating_service.get_unrated_items(limit=10)
            assert isinstance(unrated_items, list)
            
            logger.info("✅ Rating service passed")
            self.test_results["rating_service"] = "PASSED"
            
        except Exception as e:
            logger.error(f"❌ Rating service failed: {e}")
            self.test_results["rating_service"] = "FAILED"
    
    def test_api_endpoints(self):
        """Test API endpoints"""
        logger.info("🌐 Testing API endpoints...")
        
        try:
            # Test health endpoint
            response = self.client.get("/api/health")
            assert response.status_code == 200
            
            # Test system status endpoint
            response = self.client.get("/api/system/status")
            assert response.status_code == 200
            
            # Test system statistics endpoint
            response = self.client.get("/api/system/statistics")
            assert response.status_code == 200
            
            # Test manual scraping trigger
            response = self.client.post("/api/system/start-scraping")
            assert response.status_code == 200
            
            # Test manual rating trigger
            response = self.client.post("/api/system/start-rating")
            assert response.status_code == 200
            
            logger.info("✅ API endpoints passed")
            self.test_results["api_endpoints"] = "PASSED"
            
        except Exception as e:
            logger.error(f"❌ API endpoints failed: {e}")
            self.test_results["api_endpoints"] = "FAILED"
    
    def test_background_tasks(self):
        """Test background task functionality"""
        logger.info("🔄 Testing background tasks...")
        
        try:
            # Test that background task endpoints exist
            response = self.client.post("/api/system/start-scraping")
            assert response.status_code == 200
            
            response = self.client.post("/api/system/start-rating")
            assert response.status_code == 200
            
            # Check system status for background task indicators
            response = self.client.get("/api/system/status")
            assert response.status_code == 200
            
            data = response.json()
            assert "background_tasks" in data
            
            logger.info("✅ Background tasks passed")
            self.test_results["background_tasks"] = "PASSED"
            
        except Exception as e:
            logger.error(f"❌ Background tasks failed: {e}")
            self.test_results["background_tasks"] = "FAILED"
    
    def test_persian_support(self):
        """Test Persian language support"""
        logger.info("🇮🇷 Testing Persian language support...")
        
        try:
            # Test Persian keywords in main.py
            from app.main import PERSIAN_LEGAL_KEYWORDS, PERSIAN_LEGAL_SOURCES
            
            assert len(PERSIAN_LEGAL_KEYWORDS) > 0
            assert all(isinstance(keyword, str) for keyword in PERSIAN_LEGAL_KEYWORDS)
            
            assert len(PERSIAN_LEGAL_SOURCES) > 0
            assert all("name" in source for source in PERSIAN_LEGAL_SOURCES)
            assert all("url" in source for source in PERSIAN_LEGAL_SOURCES)
            
            # Test Persian content in rating service
            rating_service = RatingService(db_path=":memory:")
            
            persian_test_item = {
                "id": "persian_test",
                "title": "قانون تجارت ایران",
                "content": "این یک سند حقوقی فارسی است که شامل قوانین تجارت می‌باشد.",
                "metadata": {},
                "timestamp": "2024-01-15T10:00:00Z",
                "source_url": "https://example.com",
                "word_count": 20,
                "language": "fa",
                "strategy_used": "legal_documents",
                "domain": "example.com"
            }
            
            # This should work without errors
            asyncio.run(rating_service.rate_item(persian_test_item, "test"))
            
            logger.info("✅ Persian language support passed")
            self.test_results["persian_support"] = "PASSED"
            
        except Exception as e:
            logger.error(f"❌ Persian language support failed: {e}")
            self.test_results["persian_support"] = "FAILED"
    
    def test_error_handling(self):
        """Test error handling"""
        logger.info("🚨 Testing error handling...")
        
        try:
            # Test 404 error
            response = self.client.get("/api/nonexistent")
            assert response.status_code == 404
            
            # Test invalid endpoint
            response = self.client.post("/api/system/invalid")
            assert response.status_code in [404, 405]
            
            # Test malformed requests
            response = self.client.post("/api/system/start-scraping", 
                                     json={"invalid": "data"})
            assert response.status_code in [200, 422]  # Should handle gracefully
            
            logger.info("✅ Error handling passed")
            self.test_results["error_handling"] = "PASSED"
            
        except Exception as e:
            logger.error(f"❌ Error handling failed: {e}")
            self.test_results["error_handling"] = "FAILED"
    
    def test_performance(self):
        """Test basic performance metrics"""
        logger.info("⚡ Testing performance...")
        
        try:
            start_time = time.time()
            
            # Test health endpoint response time
            response = self.client.get("/api/health")
            health_time = time.time() - start_time
            
            assert health_time < 2.0  # Should respond within 2 seconds
            
            # Test system status response time
            start_time = time.time()
            response = self.client.get("/api/system/status")
            status_time = time.time() - start_time
            
            assert status_time < 3.0  # Should respond within 3 seconds
            
            logger.info(f"✅ Performance test passed - Health: {health_time:.2f}s, Status: {status_time:.2f}s")
            self.test_results["performance"] = "PASSED"
            
        except Exception as e:
            logger.error(f"❌ Performance test failed: {e}")
            self.test_results["performance"] = "FAILED"
    
    def generate_report(self):
        """Generate test report"""
        end_time = time.time()
        total_time = end_time - self.start_time
        
        passed_tests = sum(1 for result in self.test_results.values() if result == "PASSED")
        total_tests = len(self.test_results)
        
        logger.info(f"\n📊 Test Results Summary:")
        logger.info(f"Total Tests: {total_tests}")
        logger.info(f"Passed: {passed_tests}")
        logger.info(f"Failed: {total_tests - passed_tests}")
        logger.info(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        logger.info(f"Total Time: {total_time:.2f} seconds")
        
        # Overall status
        if passed_tests == total_tests:
            self.test_results["overall_status"] = "PASSED"
            logger.info("🎉 All tests passed! System is ready for deployment.")
        else:
            self.test_results["overall_status"] = "FAILED"
            logger.error("❌ Some tests failed. Please check the implementation.")
        
        self.test_results["summary"] = {
            "total_tests": total_tests,
            "passed_tests": passed_tests,
            "failed_tests": total_tests - passed_tests,
            "success_rate": (passed_tests/total_tests)*100,
            "total_time": total_time
        }

def main():
    """Main test runner"""
    logger.info("🏛️ Legal Dashboard Integration Test Suite")
    logger.info("=" * 50)
    
    # Create test instance
    test_suite = LegalDashboardIntegrationTest()
    
    # Run all tests
    results = test_suite.run_all_tests()
    
    # Save results to file
    with open("integration_test_results.json", "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    logger.info(f"\n📄 Results saved to: integration_test_results.json")
    
    # Exit with appropriate code
    if results.get("overall_status") == "PASSED":
        logger.info("✅ Integration test completed successfully!")
        sys.exit(0)
    else:
        logger.error("❌ Integration test failed!")
        sys.exit(1)

if __name__ == "__main__":
    main()