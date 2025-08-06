#!/usr/bin/env python3
"""
Docker Setup Validation Script
=============================

Validates that all Docker deployment requirements are met for Hugging Face Spaces.
"""

import os
import sys
from pathlib import Path


def check_file_exists(filepath, description):
    """Check if a file exists"""
    if Path(filepath).exists():
        print(f"✅ {description}: {filepath}")
        return True
    else:
        print(f"❌ {description}: {filepath} - MISSING")
        return False


def check_dockerfile():
    """Validate Dockerfile contents"""
    dockerfile_path = "Dockerfile"
    if not check_file_exists(dockerfile_path, "Dockerfile"):
        return False

    with open(dockerfile_path, 'r') as f:
        content = f.read()

    required_elements = [
        "FROM python:3.10-slim",
        "EXPOSE 7860",
        "CMD [\"uvicorn\"",
        "port 7860"
    ]

    for element in required_elements:
        if element in content:
            print(f"✅ Dockerfile contains: {element}")
        else:
            print(f"❌ Dockerfile missing: {element}")
            return False

    return True


def check_dockerignore():
    """Validate .dockerignore contents"""
    dockerignore_path = ".dockerignore"
    if not check_file_exists(dockerignore_path, ".dockerignore"):
        return False

    with open(dockerignore_path, 'r') as f:
        content = f.read()

    required_patterns = [
        "__pycache__",
        ".git",
        "*.log",
        "venv"
    ]

    for pattern in required_patterns:
        if pattern in content:
            print(f"✅ .dockerignore excludes: {pattern}")
        else:
            print(f"⚠️  .dockerignore missing: {pattern}")

    return True


def check_requirements():
    """Validate requirements.txt"""
    req_path = "requirements.txt"
    if not check_file_exists(req_path, "requirements.txt"):
        return False

    with open(req_path, 'r') as f:
        content = f.read()

    required_packages = [
        "fastapi",
        "uvicorn",
        "transformers",
        "torch",
        "PyMuPDF",
        "pytesseract"
    ]

    for package in required_packages:
        if package in content:
            print(f"✅ requirements.txt includes: {package}")
        else:
            print(f"❌ requirements.txt missing: {package}")
            return False

    return True


def check_readme_metadata():
    """Validate README.md HF Spaces metadata"""
    readme_path = "README.md"
    if not check_file_exists(readme_path, "README.md"):
        return False

    with open(readme_path, 'r') as f:
        content = f.read()

    required_metadata = [
        "sdk: docker",
        "title: Legal Dashboard OCR System",
        "emoji: 🚀"
    ]

    for metadata in required_metadata:
        if metadata in content:
            print(f"✅ README.md contains: {metadata}")
        else:
            print(f"❌ README.md missing: {metadata}")
            return False

    return True


def check_app_structure():
    """Validate application structure"""
    required_dirs = [
        "app",
        "app/api",
        "app/services",
        "app/models",
        "frontend"
    ]

    for dir_path in required_dirs:
        if Path(dir_path).exists():
            print(f"✅ Directory exists: {dir_path}")
        else:
            print(f"❌ Directory missing: {dir_path}")
            return False

    return True


def check_main_py():
    """Validate main.py configuration"""
    main_path = "app/main.py"
    if not check_file_exists(main_path, "app/main.py"):
        return False

    with open(main_path, 'r') as f:
        content = f.read()

    required_elements = [
        "port=7860",
        "host=\"0.0.0.0\"",
        "/health"
    ]

    for element in required_elements:
        if element in content:
            print(f"✅ main.py contains: {element}")
        else:
            print(f"❌ main.py missing: {element}")
            return False

    return True


def main():
    """Main validation function"""
    print("🔍 Validating Docker setup for Hugging Face Spaces...")
    print("=" * 60)

    checks = [
        ("Dockerfile", check_dockerfile),
        (".dockerignore", check_dockerignore),
        ("requirements.txt", check_requirements),
        ("README.md metadata", check_readme_metadata),
        ("App structure", check_app_structure),
        ("main.py configuration", check_main_py)
    ]

    all_passed = True

    for description, check_func in checks:
        print(f"\n📋 Checking {description}...")
        if not check_func():
            all_passed = False
        print()

    print("=" * 60)
    if all_passed:
        print("🎉 All checks passed! Ready for Hugging Face Spaces deployment.")
        print("\n🚀 Next steps:")
        print("1. Test locally: docker build -t legal-dashboard-ocr .")
        print("2. Run container: docker run -p 7860:7860 legal-dashboard-ocr")
        print("3. Deploy to HF Spaces: Push to your Space repository")
    else:
        print("❌ Some checks failed. Please fix the issues above.")
        sys.exit(1)


if __name__ == "__main__":
    main()
