#!/usr/bin/env python3
"""
Test Hugging Face Deployment Fixes
==================================

Comprehensive test script to validate all fixes for Hugging Face Spaces deployment.
Tests directory creation, environment variables, database connectivity, and OCR model loading.
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


def test_directory_creation():
    """Test creation of writable directories"""
    logger.info("🧪 Testing directory creation...")

    test_dirs = ["/tmp/hf_cache", "/tmp/data"]

    for dir_path in test_dirs:
        try:
            os.makedirs(dir_path, exist_ok=True)
            logger.info(f"✅ Created directory: {dir_path}")

            # Test if directory is writable
            test_file = os.path.join(dir_path, "test_write.tmp")
            with open(test_file, 'w') as f:
                f.write("test")
            os.remove(test_file)
            logger.info(f"✅ Directory is writable: {dir_path}")

        except Exception as e:
            logger.error(
                f"❌ Failed to create/write to directory {dir_path}: {e}")
            return False

    return True


def test_environment_variables():
    """Test environment variable setup"""
    logger.info("🧪 Testing environment variables...")

    # Set environment variables
    os.environ["TRANSFORMERS_CACHE"] = "/tmp/hf_cache"
    os.environ["HF_HOME"] = "/tmp/hf_cache"
    os.environ["DATABASE_PATH"] = "/tmp/data/legal_dashboard.db"

    # Verify environment variables
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


def test_database_connection():
    """Test database connection with new path"""
    logger.info("🧪 Testing database connection...")

    try:
        # Import database service
        sys.path.append(str(Path(__file__).parent / "app"))
        from services.database_service import DatabaseManager

        # Create database manager with new path
        db_manager = DatabaseManager()

        # Test initialization
        db_manager.initialize()

        if db_manager.is_connected():
            logger.info("✅ Database connection successful")

            # Test basic operations
            cursor = db_manager.connection.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = cursor.fetchall()
            logger.info(f"✅ Database tables: {[table[0] for table in tables]}")

            return True
        else:
            logger.error("❌ Database connection failed")
            return False

    except Exception as e:
        logger.error(f"❌ Database test failed: {e}")
        return False


def test_ocr_model_loading():
    """Test OCR model loading with cache directory"""
    logger.info("🧪 Testing OCR model loading...")

    try:
        # Import OCR service
        sys.path.append(str(Path(__file__).parent / "app"))
        from services.ocr_service import OCRPipeline

        # Create OCR pipeline
        ocr_pipeline = OCRPipeline()

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
        logger.error(f"❌ OCR test failed: {e}")
        return False


def test_main_app_startup():
    """Test main app startup with new configuration"""
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
            logger.info("✅ Health endpoint working")
            return True
        else:
            logger.error(f"❌ Health endpoint failed: {response.status_code}")
            return False

    except Exception as e:
        logger.error(f"❌ Main app test failed: {e}")
        return False


def test_dockerfile_configuration():
    """Test Dockerfile configuration"""
    logger.info("🧪 Testing Dockerfile configuration...")

    try:
        dockerfile_path = Path(__file__).parent / "Dockerfile"

        if not dockerfile_path.exists():
            logger.error("❌ Dockerfile not found")
            return False

        with open(dockerfile_path, 'r') as f:
            content = f.read()

        # Check for required configurations
        checks = [
            ("ENV TRANSFORMERS_CACHE=/tmp/hf_cache",
             "TRANSFORMERS_CACHE environment variable"),
            ("ENV HF_HOME=/tmp/hf_cache", "HF_HOME environment variable"),
            ("ENV DATABASE_PATH=/tmp/data/legal_dashboard.db",
             "DATABASE_PATH environment variable"),
            ("RUN mkdir -p /tmp/hf_cache /tmp/data", "Directory creation"),
        ]

        for check_text, description in checks:
            if check_text in content:
                logger.info(f"✅ {description} found in Dockerfile")
            else:
                logger.error(f"❌ {description} missing from Dockerfile")
                return False

        # Check that old paths are not used
        old_paths = [
            "ENV TRANSFORMERS_CACHE=/app/cache",
            "ENV DATABASE_PATH=/app/data",
            "RUN mkdir -p /app/data /app/cache",
            "chmod -R 777 /app/data"
        ]

        for old_path in old_paths:
            if old_path in content:
                logger.warning(f"⚠️ Old path found in Dockerfile: {old_path}")

        return True

    except Exception as e:
        logger.error(f"❌ Dockerfile test failed: {e}")
        return False


def test_start_script():
    """Test start script configuration"""
    logger.info("🧪 Testing start script configuration...")

    try:
        start_script_path = Path(__file__).parent / "start.sh"

        if not start_script_path.exists():
            logger.error("❌ start.sh not found")
            return False

        with open(start_script_path, 'r') as f:
            content = f.read()

        # Check for required configurations
        checks = [
            ("mkdir -p /tmp/hf_cache /tmp/data", "Directory creation"),
            ("export TRANSFORMERS_CACHE=/tmp/hf_cache", "TRANSFORMERS_CACHE export"),
            ("export HF_HOME=/tmp/hf_cache", "HF_HOME export"),
            ("export DATABASE_PATH=/tmp/data/legal_dashboard.db", "DATABASE_PATH export"),
        ]

        for check_text, description in checks:
            if check_text in content:
                logger.info(f"✅ {description} found in start.sh")
            else:
                logger.error(f"❌ {description} missing from start.sh")
                return False

        # Check that old configurations are not used
        old_configs = [
            "mkdir -p /app/data /app/cache",
            "chmod -R 777 /app/data /app/cache"
        ]

        for old_config in old_configs:
            if old_config in content:
                logger.warning(
                    f"⚠️ Old configuration found in start.sh: {old_config}")

        return True

    except Exception as e:
        logger.error(f"❌ Start script test failed: {e}")
        return False


def main():
    """Run all tests"""
    logger.info("🚀 Starting Hugging Face Deployment Fixes Test Suite")

    tests = [
        ("Directory Creation", test_directory_creation),
        ("Environment Variables", test_environment_variables),
        ("Database Connection", test_database_connection),
        ("OCR Model Loading", test_ocr_model_loading),
        ("Main App Startup", test_main_app_startup),
        ("Dockerfile Configuration", test_dockerfile_configuration),
        ("Start Script Configuration", test_start_script),
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
            "🎉 All tests passed! Hugging Face deployment fixes are ready.")
        return True
    else:
        logger.error("⚠️ Some tests failed. Please review the fixes.")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
