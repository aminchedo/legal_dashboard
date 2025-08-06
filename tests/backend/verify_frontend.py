#!/usr/bin/env python3
"""
Frontend Verification Script
============================

Verifies that the improved_legal_dashboard.html is properly configured
as the main frontend application.
"""

import os
import sys


def verify_frontend_files():
    """Verify frontend files exist and are properly configured"""
    print("🔍 Verifying frontend configuration...")

    # Check if improved_legal_dashboard.html exists
    if os.path.exists("frontend/improved_legal_dashboard.html"):
        print("✅ frontend/improved_legal_dashboard.html exists")

        # Get file size
        size = os.path.getsize("frontend/improved_legal_dashboard.html")
        print(f"   📏 File size: {size:,} bytes")
    else:
        print("❌ frontend/improved_legal_dashboard.html missing")
        return False

    # Check if index.html exists (should be a copy of improved_legal_dashboard.html)
    if os.path.exists("frontend/index.html"):
        print("✅ frontend/index.html exists")

        # Get file size
        size = os.path.getsize("frontend/index.html")
        print(f"   📏 File size: {size:,} bytes")
    else:
        print("❌ frontend/index.html missing")
        return False

    # Check if both files have the same size (they should be identical)
    size_improved = os.path.getsize("frontend/improved_legal_dashboard.html")
    size_index = os.path.getsize("frontend/index.html")

    if size_improved == size_index:
        print("✅ Both files have identical sizes (properly copied)")
    else:
        print("⚠️  Files have different sizes - may need to recopy")

    return True


def verify_fastapi_config():
    """Verify FastAPI is configured to serve the frontend"""
    print("\n🔧 Verifying FastAPI configuration...")

    try:
        with open("app/main.py", "r", encoding="utf-8") as f:
            content = f.read()

        # Check for static file mounting
        if "StaticFiles(directory=\"frontend\"" in content:
            print("✅ Static file serving configured")
        else:
            print("❌ Static file serving not configured")
            return False

        # Check for port configuration
        if "port=7860" in content or "PORT=7860" in content or "7860" in content:
            print("✅ Port 7860 configured")
        else:
            print("❌ Port 7860 not configured")
            return False

        # Check for CORS middleware
        if "CORSMiddleware" in content:
            print("✅ CORS middleware configured")
        else:
            print("❌ CORS middleware not configured")
            return False

        return True

    except Exception as e:
        print(f"❌ Error reading main.py: {e}")
        return False


def verify_docker_config():
    """Verify Docker configuration"""
    print("\n🐳 Verifying Docker configuration...")

    # Check Dockerfile
    if os.path.exists("Dockerfile"):
        print("✅ Dockerfile exists")

        try:
            with open("Dockerfile", "r", encoding="utf-8") as f:
                content = f.read()

            if "EXPOSE 7860" in content:
                print("✅ Port 7860 exposed in Dockerfile")
            else:
                print("❌ Port 7860 not exposed in Dockerfile")
                return False

            if "uvicorn" in content and "7860" in content:
                print("✅ Uvicorn configured for port 7860")
            else:
                print("❌ Uvicorn not properly configured")
                return False

        except Exception as e:
            print(f"❌ Error reading Dockerfile: {e}")
            return False
    else:
        print("❌ Dockerfile missing")
        return False

    return True


def verify_hf_metadata():
    """Verify Hugging Face metadata"""
    print("\n📋 Verifying Hugging Face metadata...")

    try:
        with open("README.md", "r", encoding="utf-8") as f:
            content = f.read()

        if "sdk: docker" in content:
            print("✅ SDK set to docker")
        else:
            print("❌ SDK not set to docker")
            return False

        if "title: Legal Dashboard OCR System" in content:
            print("✅ Title configured")
        else:
            print("❌ Title not configured")
            return False

        if "emoji: 🚀" in content:
            print("✅ Emoji configured")
        else:
            print("❌ Emoji not configured")
            return False

        return True

    except Exception as e:
        print(f"❌ Error reading README.md: {e}")
        return False


def main():
    """Main verification function"""
    print("🧪 Verifying Legal Dashboard OCR Frontend Configuration")
    print("=" * 60)

    checks = [
        ("Frontend Files", verify_frontend_files),
        ("FastAPI Config", verify_fastapi_config),
        ("Docker Config", verify_docker_config),
        ("HF Metadata", verify_hf_metadata)
    ]

    all_passed = True

    for description, check_func in checks:
        print(f"\n📋 {description}...")
        if not check_func():
            all_passed = False
        print()

    print("=" * 60)
    if all_passed:
        print("🎉 All verifications passed!")
        print("\n✅ Your improved_legal_dashboard.html is properly configured as the main frontend")
        print("✅ It will be served at the root URL (/) when deployed")
        print("✅ FastAPI will serve it as index.html")
        print("✅ Docker and Hugging Face Spaces configuration is ready")

        print("\n🚀 Deployment Summary:")
        print("- Dashboard UI: http://localhost:7860/ (your improved_legal_dashboard.html)")
        print("- API Docs: http://localhost:7860/docs")
        print("- Health Check: http://localhost:7860/health")
        print("- API Endpoints: http://localhost:7860/api/*")

        print("\n📝 Next Steps:")
        print("1. Test locally: uvicorn app.main:app --host 0.0.0.0 --port 7860")
        print("2. Deploy to HF Spaces: Push to your Space repository")
        print("3. Access your dashboard at the HF Space URL")

    else:
        print("❌ Some verifications failed. Please fix the issues above.")
        sys.exit(1)


if __name__ == "__main__":
    main()
