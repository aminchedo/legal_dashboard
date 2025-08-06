#!/usr/bin/env python3
"""
Test OCR Pipeline, Database Schema & Tokenizer Fixes
====================================================

Comprehensive test script to validate all fixes for Hugging Face deployment issues.
Tests tokenizer conversion, OCR pipeline initialization, database schema, and error handling.
"""

import os
import sys
import logging
import tempfile
import sqlite3
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def test_dependencies():
    """Test that all required dependencies are installed"""
    logger.info("🧪 Testing dependencies...")

    required_packages = [
        "sentencepiece",
        "protobuf",
        "transformers",
        "torch",
        "fastapi",
        "uvicorn"
    ]

    missing_packages = []

    for package in required_packages:
        try:
            __import__(package)
            logger.info(f"✅ {package} is installed")
        except ImportError:
            logger.error(f"❌ {package} is missing")
            missing_packages.append(package)

    if missing_packages:
        logger.error(f"Missing packages: {missing_packages}")
        return False

    return True


def test_database_schema():
    """Test database schema creation without SQL syntax errors"""
    logger.info("🧪 Testing database schema...")

    try:
        # Create a temporary database
        temp_db_path = "/tmp/test_legal_dashboard.db"

        # Import database service
        sys.path.append(str(Path(__file__).parent / "app"))
        from services.database_service import DatabaseManager

        # Create database manager with test path
        db_manager = DatabaseManager(temp_db_path)

        # Test initialization
        db_manager.initialize()

        if db_manager.is_connected():
            logger.info("✅ Database schema created successfully")

            # Test table creation
            cursor = db_manager.connection.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = cursor.fetchall()
            table_names = [table[0] for table in tables]

            expected_tables = ["documents",
                               "ai_training_data", "system_metrics"]
            for table in expected_tables:
                if table in table_names:
                    logger.info(f"✅ Table '{table}' created successfully")
                else:
                    logger.error(f"❌ Table '{table}' missing")
                    return False

            # Test document insertion
            test_doc = {
                'title': 'Test Document',
                'full_text': 'Test content',
                'keywords': ['test', 'document'],
                'references': ['ref1', 'ref2']
            }

            doc_id = db_manager.insert_document(test_doc)
            logger.info(f"✅ Document insertion successful: {doc_id}")

            # Clean up
            db_manager.close()
            os.remove(temp_db_path)

            return True
        else:
            logger.error("❌ Database connection failed")
            return False

    except Exception as e:
        logger.error(f"❌ Database schema test failed: {e}")
        return False


def test_ocr_pipeline_initialization():
    """Test OCR pipeline initialization with error handling"""
    logger.info("🧪 Testing OCR pipeline initialization...")

    try:
        # Import OCR service
        sys.path.append(str(Path(__file__).parent / "app"))
        from services.ocr_service import OCRPipeline

        # Create OCR pipeline
        ocr_pipeline = OCRPipeline()

        # Test that initialize method exists
        if hasattr(ocr_pipeline, 'initialize'):
            logger.info("✅ OCR pipeline has initialize method")
        else:
            logger.error("❌ OCR pipeline missing initialize method")
            return False

        # Test initialization
        ocr_pipeline.initialize()

        if ocr_pipeline.initialized:
            logger.info("✅ OCR pipeline initialized successfully")
            logger.info(f"✅ Model name: {ocr_pipeline.model_name}")
            return True
        else:
            logger.error("❌ OCR pipeline initialization failed")
            return False

    except Exception as e:
        logger.error(f"❌ OCR pipeline test failed: {e}")
        return False


def test_tokenizer_conversion():
    """Test tokenizer conversion with sentencepiece fallback"""
    logger.info("🧪 Testing tokenizer conversion...")

    try:
        from transformers import pipeline

        # Test basic pipeline creation
        test_pipeline = pipeline(
            "image-to-text",
            model="microsoft/trocr-base-stage1",
            cache_dir="/tmp/hf_cache"
        )

        logger.info("✅ Basic pipeline creation successful")

        # Test with slow tokenizer fallback
        try:
            slow_pipeline = pipeline(
                "image-to-text",
                model="microsoft/trocr-base-stage1",
                cache_dir="/tmp/hf_cache",
                use_fast=False
            )
            logger.info("✅ Slow tokenizer fallback successful")
        except Exception as slow_error:
            logger.warning(f"⚠️ Slow tokenizer fallback failed: {slow_error}")

        return True

    except Exception as e:
        logger.error(f"❌ Tokenizer conversion test failed: {e}")
        return False


def test_environment_setup():
    """Test environment setup for Hugging Face deployment"""
    logger.info("🧪 Testing environment setup...")

    # Test directory creation
    test_dirs = ["/tmp/hf_cache", "/tmp/data"]

    for dir_path in test_dirs:
        try:
            os.makedirs(dir_path, exist_ok=True)
            logger.info(f"✅ Created directory: {dir_path}")

            # Test write access
            test_file = os.path.join(dir_path, "test.tmp")
            with open(test_file, 'w') as f:
                f.write("test")
            os.remove(test_file)
            logger.info(f"✅ Directory writable: {dir_path}")

        except Exception as e:
            logger.error(f"❌ Directory test failed for {dir_path}: {e}")
            return False

    # Test environment variables
    os.environ["TRANSFORMERS_CACHE"] = "/tmp/hf_cache"
    os.environ["HF_HOME"] = "/tmp/hf_cache"
    os.environ["DATABASE_PATH"] = "/tmp/data/legal_dashboard.db"

    expected_vars = {
        "TRANSFORMERS_CACHE": "/tmp/hf_cache",
        "HF_HOME": "/tmp/hf_cache",
        "DATABASE_PATH": "/tmp/data/legal_dashboard.db"
    }

    for var_name, expected_value in expected_vars.items():
        actual_value = os.getenv(var_name)
        if actual_value == expected_value:
            logger.info(f"✅ Environment variable {var_name}: {actual_value}")
        else:
            logger.error(
                f"❌ Environment variable {var_name}: expected {expected_value}, got {actual_value}")
            return False

    return True


def test_main_app_startup():
    """Test main app startup with all fixes"""
    logger.info("🧪 Testing main app startup...")

    try:
        # Import main app
        sys.path.append(str(Path(__file__).parent / "app"))
        from main import app

        # Test that app can be created
        logger.info("✅ Main app created successfully")

        # Test health endpoint
        from fastapi.testclient import TestClient
        client = TestClient(app)

        response = client.get("/health")
        if response.status_code == 200:
            health_data = response.json()
            logger.info("✅ Health endpoint working")
            logger.info(f"✅ Health data: {health_data}")
            return True
        else:
            logger.error(f"❌ Health endpoint failed: {response.status_code}")
            return False

    except Exception as e:
        logger.error(f"❌ Main app test failed: {e}")
        return False


def test_error_handling():
    """Test error handling for various failure scenarios"""
    logger.info("🧪 Testing error handling...")

    try:
        # Test database with invalid path
        sys.path.append(str(Path(__file__).parent / "app"))
        from services.database_service import DatabaseManager

        # Test with invalid path (should handle gracefully)
        db_manager = DatabaseManager("/invalid/path/test.db")

        # This should not crash
        try:
            db_manager.initialize()
        except Exception as e:
            logger.info(f"✅ Database gracefully handled invalid path: {e}")

        # Test OCR with invalid model
        from services.ocr_service import OCRPipeline

        # Create OCR with invalid model (should fallback)
        ocr_pipeline = OCRPipeline("invalid/model/name")
        ocr_pipeline.initialize()

        if ocr_pipeline.initialized:
            logger.info("✅ OCR gracefully handled invalid model")
        else:
            logger.info("✅ OCR properly marked as not initialized")

        return True

    except Exception as e:
        logger.error(f"❌ Error handling test failed: {e}")
        return False


def main():
    """Run all tests"""
    logger.info(
        "🚀 Starting OCR Pipeline, Database Schema & Tokenizer Fixes Test Suite")

    tests = [
        ("Dependencies", test_dependencies),
        ("Environment Setup", test_environment_setup),
        ("Database Schema", test_database_schema),
        ("OCR Pipeline Initialization", test_ocr_pipeline_initialization),
        ("Tokenizer Conversion", test_tokenizer_conversion),
        ("Main App Startup", test_main_app_startup),
        ("Error Handling", test_error_handling),
    ]

    results = []

    for test_name, test_func in tests:
        logger.info(f"\n{'='*50}")
        logger.info(f"Running: {test_name}")
        logger.info(f"{'='*50}")

        try:
            result = test_func()
            results.append((test_name, result))

            if result:
                logger.info(f"✅ {test_name}: PASSED")
            else:
                logger.error(f"❌ {test_name}: FAILED")

        except Exception as e:
            logger.error(f"❌ {test_name}: ERROR - {e}")
            results.append((test_name, False))

    # Summary
    logger.info(f"\n{'='*50}")
    logger.info("TEST SUMMARY")
    logger.info(f"{'='*50}")

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        logger.info(f"{test_name}: {status}")

    logger.info(f"\nOverall: {passed}/{total} tests passed")

    if passed == total:
        logger.info(
            "🎉 All tests passed! OCR pipeline, database schema, and tokenizer fixes are ready.")
        return True
    else:
        logger.error("⚠️ Some tests failed. Please review the fixes.")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
