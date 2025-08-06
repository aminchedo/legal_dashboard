#!/usr/bin/env python3
"""
Simple Deployment Validation
===========================

Quick validation for Hugging Face Spaces deployment.
"""

import os
import sys


def main():
    print("🚀 Legal Dashboard OCR - Simple Deployment Validation")
    print("=" * 60)

    # Check essential files
    essential_files = [
        "huggingface_space/app.py",
        "huggingface_space/Spacefile",
        "huggingface_space/README.md",
        "requirements.txt",
        "app/services/ocr_service.py",
        "app/services/ai_service.py",
        "app/services/database_service.py",
        "data/sample_persian.pdf"
    ]

    print("🔍 Checking essential files...")
    all_files_exist = True

    for file_path in essential_files:
        if os.path.exists(file_path):
            print(f"✅ {file_path}")
        else:
            print(f"❌ {file_path}")
            all_files_exist = False

    # Check requirements.txt for gradio
    print("\n🔍 Checking requirements.txt...")
    try:
        with open("requirements.txt", "r", encoding="utf-8") as f:
            content = f.read()
            if "gradio" in content:
                print("✅ gradio found in requirements.txt")
            else:
                print("❌ gradio missing from requirements.txt")
                all_files_exist = False
    except Exception as e:
        print(f"❌ Error reading requirements.txt: {e}")
        all_files_exist = False

    # Check Spacefile
    print("\n🔍 Checking Spacefile...")
    try:
        with open("huggingface_space/Spacefile", "r", encoding="utf-8") as f:
            content = f.read()
            if "gradio" in content and "python" in content:
                print("✅ Spacefile properly configured")
            else:
                print("❌ Spacefile missing required configurations")
                all_files_exist = False
    except Exception as e:
        print(f"❌ Error reading Spacefile: {e}")
        all_files_exist = False

    # Final result
    print("\n" + "=" * 60)
    if all_files_exist:
        print("🎉 All checks passed! Ready for deployment.")
        print("\n📋 Deployment Steps:")
        print("1. Create Space on https://huggingface.co/spaces")
        print("2. Upload huggingface_space/ directory")
        print("3. Set HF_TOKEN environment variable")
        print("4. Deploy and test")
        return 0
    else:
        print("⚠️ Some checks failed. Please fix issues before deployment.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
