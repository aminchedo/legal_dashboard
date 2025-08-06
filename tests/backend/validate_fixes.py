#!/usr/bin/env python3
"""
Validation Script for Database and Cache Fixes
============================================

Tests the fixes for:
1. SQLite database path issues
2. Hugging Face cache permissions
"""

import os
import sys
import tempfile
import shutil
from pathlib import Path


def test_database_path():
    """Test database path creation and access"""
    print("🔍 Testing database path fixes...")

    try:
        # Test the new database path
        from app.services.database_service import DatabaseManager

        # Test with default path (should be /app/data/legal_dashboard.db)
        db = DatabaseManager()
        print("✅ Database manager initialized with default path")

        # Test if database directory exists
        db_dir = os.path.dirname(db.db_path)
        if os.path.exists(db_dir):
            print(f"✅ Database directory exists: {db_dir}")
        else:
            print(f"❌ Database directory missing: {db_dir}")
            return False

        # Test database connection
        if db.is_connected():
            print("✅ Database connection successful")
        else:
            print("❌ Database connection failed")
            return False

        db.close()
        return True

    except Exception as e:
        print(f"❌ Database test failed: {e}")
        return False


def test_cache_directory():
    """Test Hugging Face cache directory setup"""
    print("\n🔍 Testing cache directory fixes...")

    try:
        # Check if cache directory is set
        cache_dir = os.environ.get("TRANSFORMERS_CACHE")
        if cache_dir:
            print(f"✅ TRANSFORMERS_CACHE set to: {cache_dir}")
        else:
            print("❌ TRANSFORMERS_CACHE not set")
            return False

        # Check if cache directory exists and is writable
        if os.path.exists(cache_dir):
            print(f"✅ Cache directory exists: {cache_dir}")
        else:
            print(f"❌ Cache directory missing: {cache_dir}")
            return False

        # Test write permissions
        test_file = os.path.join(cache_dir, "test_write.tmp")
        try:
            with open(test_file, 'w') as f:
                f.write("test")
            os.remove(test_file)
            print("✅ Cache directory is writable")
        except Exception as e:
            print(f"❌ Cache directory not writable: {e}")
            return False

        return True

    except Exception as e:
        print(f"❌ Cache test failed: {e}")
        return False


def test_dockerfile_updates():
    """Test Dockerfile changes"""
    print("\n🔍 Testing Dockerfile updates...")

    try:
        dockerfile_path = "Dockerfile"
        if not os.path.exists(dockerfile_path):
            print("❌ Dockerfile not found")
            return False

        with open(dockerfile_path, 'r') as f:
            content = f.read()

        # Check for directory creation
        if "mkdir -p /app/data /app/cache" in content:
            print("✅ Directory creation command found")
        else:
            print("❌ Directory creation command missing")
            return False

        # Check for permissions
        if "chmod -R 777 /app/data /app/cache" in content:
            print("✅ Permission setting command found")
        else:
            print("❌ Permission setting command missing")
            return False

        # Check for environment variables
        if "ENV TRANSFORMERS_CACHE=/app/cache" in content:
            print("✅ TRANSFORMERS_CACHE environment variable found")
        else:
            print("❌ TRANSFORMERS_CACHE environment variable missing")
            return False

        if "ENV HF_HOME=/app/cache" in content:
            print("✅ HF_HOME environment variable found")
        else:
            print("❌ HF_HOME environment variable missing")
            return False

        return True

    except Exception as e:
        print(f"❌ Dockerfile test failed: {e}")
        return False


def test_main_py_updates():
    """Test main.py updates"""
    print("\n🔍 Testing main.py updates...")

    try:
        main_py_path = "app/main.py"
        if not os.path.exists(main_py_path):
            print("❌ main.py not found")
            return False

        with open(main_py_path, 'r') as f:
            content = f.read()

        # Check for directory creation
        if "os.makedirs(\"/app/cache\", exist_ok=True)" in content:
            print("✅ Cache directory creation found")
        else:
            print("❌ Cache directory creation missing")
            return False

        if "os.makedirs(\"/app/data\", exist_ok=True)" in content:
            print("✅ Data directory creation found")
        else:
            print("❌ Data directory creation missing")
            return False

        # Check for environment variable setting
        if "os.environ[\"TRANSFORMERS_CACHE\"] = \"/app/cache\"" in content:
            print("✅ TRANSFORMERS_CACHE environment variable setting found")
        else:
            print("❌ TRANSFORMERS_CACHE environment variable setting missing")
            return False

        return True

    except Exception as e:
        print(f"❌ main.py test failed: {e}")
        return False


def test_dockerignore_updates():
    """Test .dockerignore updates"""
    print("\n🔍 Testing .dockerignore updates...")

    try:
        dockerignore_path = ".dockerignore"
        if not os.path.exists(dockerignore_path):
            print("❌ .dockerignore not found")
            return False

        with open(dockerignore_path, 'r') as f:
            content = f.read()

        # Check for cache exclusions
        if "cache/" in content:
            print("✅ Cache directory exclusion found")
        else:
            print("❌ Cache directory exclusion missing")
            return False

        if "/app/cache/" in content:
            print("✅ /app/cache exclusion found")
        else:
            print("❌ /app/cache exclusion missing")
            return False

        return True

    except Exception as e:
        print(f"❌ .dockerignore test failed: {e}")
        return False


def main():
    """Run all validation tests"""
    print("🚀 Legal Dashboard OCR - Fix Validation")
    print("=" * 50)

    # Change to project directory
    project_dir = Path(__file__).parent
    os.chdir(project_dir)

    # Run tests
    tests = [
        test_database_path,
        test_cache_directory,
        test_dockerfile_updates,
        test_main_py_updates,
        test_dockerignore_updates
    ]

    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"❌ Test failed with exception: {e}")
            results.append(False)

    # Summary
    print("\n" + "=" * 50)
    print("📊 Validation Results Summary")
    print("=" * 50)

    passed = sum(results)
    total = len(results)

    print(f"✅ Passed: {passed}/{total}")
    print(f"❌ Failed: {total - passed}/{total}")

    if all(results):
        print("\n🎉 All fixes validated successfully!")
        print("\n✅ Runtime errors should be resolved:")
        print("   • SQLite database path fixed")
        print("   • Hugging Face cache permissions fixed")
        print("   • Environment variables properly set")
        print("   • Docker container ready for deployment")
        return 0
    else:
        print("\n⚠️ Some fixes need attention. Please check the errors above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
