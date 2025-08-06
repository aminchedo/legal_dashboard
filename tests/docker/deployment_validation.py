#!/usr/bin/env python3
"""
Deployment Validation Script for Hugging Face Spaces
===================================================

This script validates the essential components needed for successful deployment.
"""

import os
import sys
from pathlib import Path
import json


def check_file_structure():
    """Check that all required files exist for deployment"""
    print("🔍 Checking file structure...")

    required_files = [
        "huggingface_space/app.py",
        "huggingface_space/Spacefile",
        "huggingface_space/README.md",
        "requirements.txt",
        "app/services/ocr_service.py",
        "app/services/ai_service.py",
        "app/services/database_service.py",
        "app/models/document_models.py",
        "data/sample_persian.pdf"
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


def check_requirements():
    """Check requirements.txt for deployment compatibility"""
    print("\n🔍 Checking requirements.txt...")

    try:
        with open("requirements.txt", "r") as f:
            requirements = f.read()

        # Check for essential packages
        essential_packages = [
            "gradio",
            "transformers",
            "torch",
            "fastapi",
            "uvicorn",
            "PyMuPDF",
            "Pillow"
        ]

        missing_packages = []
        for package in essential_packages:
            if package not in requirements:
                missing_packages.append(package)

        if missing_packages:
            print(f"❌ Missing packages: {missing_packages}")
            return False
        else:
            print("✅ All essential packages found in requirements.txt")
            return True

    except Exception as e:
        print(f"❌ Error reading requirements.txt: {e}")
        return False


def check_spacefile():
    """Check Spacefile configuration"""
    print("\n🔍 Checking Spacefile...")

    try:
        with open("huggingface_space/Spacefile", "r") as f:
            spacefile_content = f.read()

        # Check for essential configurations
        required_configs = [
            "runtime: python",
            "run: python app.py",
            "gradio"
        ]

        missing_configs = []
        for config in required_configs:
            if config not in spacefile_content:
                missing_configs.append(config)

        if missing_configs:
            print(f"❌ Missing configurations: {missing_configs}")
            return False
        else:
            print("✅ Spacefile properly configured")
            return True

    except Exception as e:
        print(f"❌ Error reading Spacefile: {e}")
        return False


def check_app_entry_point():
    """Check the main app.py entry point"""
    print("\n🔍 Checking app.py entry point...")

    try:
        with open("huggingface_space/app.py", "r") as f:
            app_content = f.read()

        # Check for essential components
        required_components = [
            "import gradio",
            "gr.Blocks",
            "demo.launch"
        ]

        missing_components = []
        for component in required_components:
            if component not in app_content:
                missing_components.append(component)

        if missing_components:
            print(f"❌ Missing components: {missing_components}")
            return False
        else:
            print("✅ App entry point properly configured")
            return True

    except Exception as e:
        print(f"❌ Error reading app.py: {e}")
        return False


def check_sample_data():
    """Check that sample data exists"""
    print("\n🔍 Checking sample data...")

    sample_files = [
        "data/sample_persian.pdf"
    ]

    missing_files = []
    for file_path in sample_files:
        if not os.path.exists(file_path):
            missing_files.append(file_path)
        else:
            file_size = os.path.getsize(file_path)
            print(f"✅ {file_path} ({file_size} bytes)")

    if missing_files:
        print(f"❌ Missing sample files: {missing_files}")
        return False
    else:
        print("✅ Sample data available")
        return True


def generate_deployment_summary():
    """Generate deployment summary"""
    print("\n📋 Deployment Summary")
    print("=" * 50)

    summary = {
        "project_name": "Legal Dashboard OCR",
        "deployment_type": "Hugging Face Spaces",
        "framework": "Gradio",
        "entry_point": "huggingface_space/app.py",
        "requirements": "requirements.txt",
        "configuration": "huggingface_space/Spacefile",
        "documentation": "huggingface_space/README.md",
        "sample_data": "data/sample_persian.pdf"
    }

    for key, value in summary.items():
        print(f"{key.replace('_', ' ').title()}: {value}")

    return summary


def main():
    """Main validation function"""
    print("🚀 Legal Dashboard OCR - Deployment Validation")
    print("=" * 60)

    # Run all checks
    checks = [
        check_file_structure,
        check_requirements,
        check_spacefile,
        check_app_entry_point,
        check_sample_data
    ]

    results = []
    for check in checks:
        try:
            result = check()
            results.append(result)
        except Exception as e:
            print(f"❌ Check failed with exception: {e}")
            results.append(False)

    # Generate summary
    summary = generate_deployment_summary()

    # Final results
    print("\n" + "=" * 60)
    print("📊 Validation Results")
    print("=" * 60)

    passed = sum(results)
    total = len(results)

    print(f"✅ Passed: {passed}/{total}")
    print(f"❌ Failed: {total - passed}/{total}")

    if all(results):
        print("\n🎉 All validation checks passed!")
        print("✅ Project is ready for Hugging Face Spaces deployment")

        print("\n📋 Next Steps:")
        print("1. Create a new Space on Hugging Face")
        print("2. Upload the huggingface_space/ directory")
        print("3. Set HF_TOKEN environment variable")
        print("4. Deploy and test the application")

        return 0
    else:
        print("\n⚠️ Some validation checks failed.")
        print("Please fix the issues above before deployment.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
