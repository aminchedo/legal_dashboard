#!/usr/bin/env python3
"""
Test script to verify the project structure and basic functionality.
"""

import sys
import os
from pathlib import Path


def test_imports():
    """Test that all modules can be imported"""
    print("🔍 Testing imports...")

    try:
        # Test app imports
        from app.main import app
        print("✅ FastAPI app imported successfully")

        from app.services.ocr_service import OCRPipeline
        print("✅ OCR service imported successfully")

        from app.services.database_service import DatabaseManager
        print("✅ Database service imported successfully")

        from app.services.ai_service import AIScoringEngine
        print("✅ AI service imported successfully")

        from app.models.document_models import LegalDocument
        print("✅ Document models imported successfully")

        return True

    except Exception as e:
        print(f"❌ Import error: {e}")
        return False


def test_structure():
    """Test that all required files exist"""
    print("\n🔍 Testing project structure...")

    required_files = [
        "requirements.txt",
        "app/main.py",
        "app/api/documents.py",
        "app/api/ocr.py",
        "app/api/dashboard.py",
        "app/services/ocr_service.py",
        "app/services/database_service.py",
        "app/services/ai_service.py",
        "app/models/document_models.py",
        "frontend/improved_legal_dashboard.html",
        "frontend/test_integration.html",
        "tests/test_api_endpoints.py",
        "tests/test_ocr_pipeline.py",
        "data/sample_persian.pdf",
        "huggingface_space/app.py",
        "huggingface_space/Spacefile",
        "huggingface_space/README.md",
        "README.md"
    ]

    missing_files = []
    for file_path in required_files:
        if not os.path.exists(file_path):
            missing_files.append(file_path)
        else:
            print(f"✅ {file_path}")

    if missing_files:
        print(f"\n❌ Missing files: {missing_files}")
        return False
    else:
        print("\n✅ All required files exist")
        return True


def test_basic_functionality():
    """Test basic functionality"""
    print("\n🔍 Testing basic functionality...")

    try:
        # Test OCR pipeline initialization
        from app.services.ocr_service import OCRPipeline
        ocr = OCRPipeline()
        print("✅ OCR pipeline initialized")

        # Test database manager
        from app.services.database_service import DatabaseManager
        db = DatabaseManager()
        print("✅ Database manager initialized")

        # Test AI engine
        from app.services.ai_service import AIScoringEngine
        ai = AIScoringEngine()
        print("✅ AI engine initialized")

        # Test document model
        from app.models.document_models import LegalDocument
        doc = LegalDocument(title="Test Document")
        print("✅ Document model created")

        return True

    except Exception as e:
        print(f"❌ Functionality test error: {e}")
        return False


def main():
    """Run all tests"""
    print("🚀 Legal Dashboard OCR - Structure Test")
    print("=" * 50)

    # Change to project directory
    project_dir = Path(__file__).parent
    os.chdir(project_dir)

    # Run tests
    tests = [
        test_structure,
        test_imports,
        test_basic_functionality
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
    print("📊 Test Results Summary")
    print("=" * 50)

    passed = sum(results)
    total = len(results)

    print(f"✅ Passed: {passed}/{total}")
    print(f"❌ Failed: {total - passed}/{total}")

    if all(results):
        print("\n🎉 All tests passed! Project structure is ready.")
        return 0
    else:
        print("\n⚠️ Some tests failed. Please check the errors above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
