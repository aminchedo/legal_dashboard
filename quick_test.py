#!/usr/bin/env python3
"""
Quick Test for Scraping and Rating System
=========================================

Simple test to verify the system is working with the actual database.
"""

import asyncio
import sys
import os
from datetime import datetime, timezone
from app.services.scraping_service import ScrapingService, ScrapingStrategy
from app.services.rating_service import RatingService


async def quick_test():
    """Quick test of the scraping and rating system"""
    print("🚀 Quick Test - Scraping and Rating System")
    print("=" * 50)

    try:
        # Initialize services with actual database
        print("📦 Initializing services...")
        scraping_service = ScrapingService(db_path="legal_documents.db")
        rating_service = RatingService(db_path="legal_documents.db")

        print("✅ Services initialized")

        # Test scraping service
        print("\n🧪 Testing scraping service...")
        job_id = await scraping_service.start_scraping_job(
            urls=["https://example.com"],
            strategy=ScrapingStrategy.GENERAL
        )
        print(f"✅ Started job: {job_id}")

        # Get job status
        status = await scraping_service.get_job_status(job_id)
        print(f"✅ Job status: {status['status'] if status else 'unknown'}")

        # Test rating service
        print("\n🧪 Testing rating service...")
        sample_item = {
            'id': 'test_item_001',
            'url': 'https://example.com/test',
            'title': 'Test Document',
            'content': 'This is a test document with some content.',
            'metadata': {'source': 'test'},
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'source_url': 'https://example.com',
            'domain': 'example.com',
            'word_count': 10,
            'language': 'en'
        }

        rating_result = await rating_service.rate_item(sample_item)
        print(
            f"✅ Rated item: {rating_result.rating_level.value} ({rating_result.overall_score:.3f})")

        # Get rating summary
        summary = await rating_service.get_rating_summary()
        print(f"✅ Rating summary: {summary.get('total_rated', 0)} items rated")

        print("\n🎉 All tests passed! System is working correctly.")
        return True

    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(quick_test())
    sys.exit(0 if success else 1)
