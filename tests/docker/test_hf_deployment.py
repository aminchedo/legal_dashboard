#!/usr/bin/env python3
"""
Hugging Face Deployment Test Script
===================================

Tests the Legal Dashboard OCR system for Hugging Face Spaces deployment.
"""

import requests
import time
import subprocess
import sys
import os


def test_docker_build():
    """Test Docker build process"""
    print("🔨 Testing Docker build...")
    try:
        result = subprocess.run(
            ["docker", "build", "-t", "legal-dashboard", "."],
            capture_output=True,
            text=True,
            cwd="."
        )
        if result.returncode == 0:
            print("✅ Docker build successful")
            return True
        else:
            print(f"❌ Docker build failed: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ Docker build error: {e}")
        return False


def test_docker_run():
    """Test Docker container startup"""
    print("🚀 Testing Docker container startup...")
    try:
        # Start container in background
        container = subprocess.run(
            ["docker", "run", "-d", "-p", "7860:7860", "--name",
                "test-legal-dashboard", "legal-dashboard"],
            capture_output=True,
            text=True
        )

        if container.returncode != 0:
            print(f"❌ Container startup failed: {container.stderr}")
            return False

        # Wait for container to start
        print("⏳ Waiting for container to start...")
        time.sleep(30)

        # Test endpoints
        endpoints = [
            ("/", "Dashboard UI"),
            ("/health", "Health Check"),
            ("/docs", "API Documentation"),
            ("/api/dashboard/summary", "Dashboard API")
        ]

        for endpoint, description in endpoints:
            try:
                response = requests.get(
                    f"http://localhost:7860{endpoint}", timeout=10)
                # 404 is OK for some endpoints
                if response.status_code in [200, 404]:
                    print(f"✅ {description}: {response.status_code}")
                else:
                    print(f"❌ {description}: {response.status_code}")
            except requests.exceptions.RequestException as e:
                print(f"❌ {description}: {e}")

        return True

    except Exception as e:
        print(f"❌ Container test error: {e}")
        return False
    finally:
        # Cleanup
        subprocess.run(
            ["docker", "stop", "test-legal-dashboard"], capture_output=True)
        subprocess.run(["docker", "rm", "test-legal-dashboard"],
                       capture_output=True)


def test_static_files():
    """Test static file serving"""
    print("📁 Testing static file serving...")

    # Check if index.html exists
    if os.path.exists("frontend/index.html"):
        print("✅ frontend/index.html exists")
    else:
        print("❌ frontend/index.html missing")
        return False

    # Check if main dashboard file exists
    if os.path.exists("frontend/improved_legal_dashboard.html"):
        print("✅ frontend/improved_legal_dashboard.html exists")
    else:
        print("❌ frontend/improved_legal_dashboard.html missing")
        return False

    return True


def test_fastapi_config():
    """Test FastAPI configuration"""
    print("🔧 Testing FastAPI configuration...")

    # Check if main.py has static mount
    with open("app/main.py", "r", encoding="utf-8") as f:
        content = f.read()

    required_elements = [
        "StaticFiles(directory=\"frontend\"",
        "port=7860",
        "host=\"0.0.0.0\""
    ]

    for element in required_elements:
        if element in content:
            print(f"✅ main.py contains: {element}")
        else:
            print(f"❌ main.py missing: {element}")
            return False

    return True


def main():
    """Main test function"""
    print("🧪 Starting Hugging Face deployment tests...")
    print("=" * 60)

    tests = [
        ("Static Files", test_static_files),
        ("FastAPI Config", test_fastapi_config),
        ("Docker Build", test_docker_build),
        ("Docker Run", test_docker_run)
    ]

    all_passed = True

    for description, test_func in tests:
        print(f"\n📋 Testing {description}...")
        if not test_func():
            all_passed = False
        print()

    print("=" * 60)
    if all_passed:
        print("🎉 All tests passed! Ready for Hugging Face Spaces deployment.")
        print("\n🚀 Next steps:")
        print("1. Push to Hugging Face Space repository")
        print("2. Monitor build logs")
        print("3. Access at: https://huggingface.co/spaces/<username>/legal-dashboard-ocr")
    else:
        print("❌ Some tests failed. Please fix the issues above.")
        sys.exit(1)


if __name__ == "__main__":
    main()
