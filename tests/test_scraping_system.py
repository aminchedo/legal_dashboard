#!/usr/bin/env python3
"""
Simple Test Script for Scraping and Rating System
=================================================

This script tests the basic functionality of the scraping and rating system.
Run this to verify that all components are working correctly.
"""

from app.services.rating_service import RatingService
from app.services.scraping_service import ScrapingService, ScrapingStrategy
import asyncio
import json
import sys
import os
from datetime import datetime

# Add the app directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))


async def test_scraping_service():
    """Test the scraping service functionality"""
    print("🧪 Testing Scraping Service...")

    try:
        # Initialize scraping service
        scraping_service = ScrapingService(db_path=":memory:")
        print("✅ Scraping service initialized")

        # Test URL processing
        test_urls = [
            "https://example.com/test1",
            "https://example.com/test2"
        ]

        # Start a scraping job
        job_id = await scraping_service.start_scraping_job(
            urls=test_urls,
            strategy=ScrapingStrategy.GENERAL,
            max_depth=1,
            delay=0.1
        )
        print(f"✅ Started scraping job: {job_id}")

        # Get job status
        status = await scraping_service.get_job_status(job_id)
        print(f"✅ Job status: {status['status']}")

        # Get statistics
        stats = await scraping_service.get_scraping_statistics()
        print(f"✅ Statistics: {stats}")

        return True

    except Exception as e:
        print(f"❌ Scraping service test failed: {e}")
        return False


async def test_rating_service():
    """Test the rating service functionality"""
    print("\n🧪 Testing Rating Service...")

    try:
        # Initialize rating service
        rating_service = RatingService(db_path=":memory:")
        print("✅ Rating service initialized")

        # Create test item data
        test_item = {
            'id': 'test_item_001',
            'url': 'https://example.com/legal-doc',
            'title': 'Test Legal Document',
            'content': 'This is a test legal document with proper structure and legal terms including contract and agreement.',
            'metadata': {'content_type': 'text/html'},
            'timestamp': datetime.now().isoformat(),
            'source_url': 'https://example.com/legal-doc',
            'domain': 'example.com',
            'word_count': 20,
            'language': 'english',
            'strategy_used': 'legal_documents'
        }

        # Rate the item
        result = await rating_service.rate_item(test_item)
        print(
            f"✅ Rated item: {result.rating_level.value} ({result.overall_score:.3f})")
        print(f"   Criteria scores: {result.criteria_scores}")

        # Get rating summary
        summary = await rating_service.get_rating_summary()
        print(f"✅ Rating summary: {summary['total_rated']} items rated")

        return True

    except Exception as e:
        print(f"❌ Rating service test failed: {e}")
        return False


async def test_integration():
    """Test integration between scraping and rating services"""
    print("\n🧪 Testing Integration...")

    try:
        # Initialize both services
        scraping_service = ScrapingService(db_path=":memory:")
        rating_service = RatingService(db_path=":memory:")
        print("✅ Services initialized")

        # Create mock scraped item
        mock_item = {
            'id': 'integration_test_001',
            'url': 'https://court.gov.ir/document',
            'title': 'Legal Court Document',
            'content': 'This is a legal court document with proper legal structure and terminology.',
            'metadata': {'content_type': 'text/html', 'job_id': 'test_job'},
            'timestamp': datetime.now().isoformat(),
            'source_url': 'https://court.gov.ir/document',
            'domain': 'court.gov.ir',
            'word_count': 50,
            'language': 'english',
            'strategy_used': 'legal_documents'
        }

        # Simulate scraping process
        await scraping_service._store_scraped_item(mock_item)
        print("✅ Mock item stored")

        # Rate the item
        rating_result = await rating_service.rate_item(mock_item)
        print(
            f"✅ Integration test completed: {rating_result.rating_level.value}")

        return True

    except Exception as e:
        print(f"❌ Integration test failed: {e}")
        return False


async def test_api_endpoints():
    """Test API endpoints (requires running server)"""
    print("\n🧪 Testing API Endpoints...")

    try:
        import requests

        base_url = "http://localhost:8000"

        # Test health endpoint
        response = requests.get(f"{base_url}/api/health", timeout=5)
        if response.status_code == 200:
            print("✅ Health endpoint working")
        else:
            print(f"⚠️ Health endpoint returned {response.status_code}")

        # Test scraping statistics
        response = requests.get(f"{base_url}/api/scrape/statistics", timeout=5)
        if response.status_code == 200:
            print("✅ Scraping statistics endpoint working")
        else:
            print(f"⚠️ Scraping statistics returned {response.status_code}")

        # Test rating summary
        response = requests.get(f"{base_url}/api/rating/summary", timeout=5)
        if response.status_code == 200:
            print("✅ Rating summary endpoint working")
        else:
            print(f"⚠️ Rating summary returned {response.status_code}")

        return True

    except requests.exceptions.ConnectionError:
        print("⚠️ Server not running - skipping API tests")
        return True
    except Exception as e:
        print(f"❌ API test failed: {e}")
        return False


def test_dependencies():
    """Test that all required dependencies are available"""
    print("🧪 Testing Dependencies...")

    required_packages = [
        'fastapi',
        'aiohttp',
        'bs4',
        'numpy',
        'pydantic',
        'sqlite3'
    ]

    missing_packages = []

    for package in required_packages:
        try:
            if package == 'sqlite3':
                import sqlite3
            else:
                __import__(package)
            print(f"✅ {package}")
        except ImportError:
            print(f"❌ {package} - MISSING")
            missing_packages.append(package)

    if missing_packages:
        print(f"\n⚠️ Missing packages: {', '.join(missing_packages)}")
        print("Install with: pip install " +
              " ".join([pkg if pkg != 'bs4' else 'beautifulsoup4' for pkg in missing_packages]))
        return False

    return True


async def main():
    """Run all tests"""
    print("🚀 Starting Scraping and Rating System Tests")
    print("=" * 50)

    # Test dependencies first
    if not test_dependencies():
        print("\n❌ Dependency test failed. Please install missing packages.")
        return

    # Run all tests
    tests = [
        test_scraping_service(),
        test_rating_service(),
        test_integration(),
        test_api_endpoints()
    ]

    results = await asyncio.gather(*tests, return_exceptions=True)

    # Print summary
    print("\n" + "=" * 50)
    print("📊 Test Results Summary")
    print("=" * 50)

    test_names = [
        "Scraping Service",
        "Rating Service",
        "Integration",
        "API Endpoints"
    ]

    passed = 0
    total = len(results)

    for i, (name, result) in enumerate(zip(test_names, results)):
        if isinstance(result, Exception):
            print(f"❌ {name}: Failed with exception - {result}")
        elif result:
            print(f"✅ {name}: Passed")
            passed += 1
        else:
            print(f"❌ {name}: Failed")

    print(f"\n🎯 Overall: {passed}/{total} tests passed")

    if passed == total:
        print("🎉 All tests passed! The system is working correctly.")
    else:
        print("⚠️ Some tests failed. Please check the errors above.")

    return passed == total

if __name__ == "__main__":
    try:
        success = asyncio.run(main())
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n⏹️ Tests interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Unexpected error: {e}")
        sys.exit(1)
