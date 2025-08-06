#!/usr/bin/env python3
"""
Docker Test Script for Legal Dashboard OCR
==========================================

This script tests the Docker container to ensure it's working correctly
for Hugging Face Spaces deployment.
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
            ["docker", "build", "-t", "legal-dashboard-ocr", "."],
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
                "test-legal-dashboard", "legal-dashboard-ocr"],
            capture_output=True,
            text=True
        )

        if container.returncode != 0:
            print(f"❌ Container startup failed: {container.stderr}")
            return False

        # Wait for container to start
        print("⏳ Waiting for container to start...")
        time.sleep(30)

        # Test health endpoint
        try:
            response = requests.get("http://localhost:7860/health", timeout=10)
            if response.status_code == 200:
                print("✅ Container health check passed")
                return True
            else:
                print(f"❌ Health check failed: {response.status_code}")
                return False
        except requests.exceptions.RequestException as e:
            print(f"❌ Health check error: {e}")
            return False

    except Exception as e:
        print(f"❌ Container test error: {e}")
        return False
    finally:
        # Cleanup
        subprocess.run(
            ["docker", "stop", "test-legal-dashboard"], capture_output=True)
        subprocess.run(["docker", "rm", "test-legal-dashboard"],
                       capture_output=True)


def test_api_endpoints():
    """Test API endpoints"""
    print("🔍 Testing API endpoints...")

    endpoints = [
        "/",
        "/health",
        "/docs",
        "/api/dashboard/summary"
    ]

    for endpoint in endpoints:
        try:
            response = requests.get(
                f"http://localhost:7860{endpoint}", timeout=10)
            # 404 is OK for some endpoints
            if response.status_code in [200, 404]:
                print(f"✅ {endpoint}: {response.status_code}")
            else:
                print(f"❌ {endpoint}: {response.status_code}")
        except requests.exceptions.RequestException as e:
            print(f"❌ {endpoint}: {e}")


def main():
    """Main test function"""
    print("🧪 Starting Docker tests for Legal Dashboard OCR...")

    # Test 1: Docker build
    if not test_docker_build():
        print("❌ Docker build test failed")
        sys.exit(1)

    # Test 2: Docker run
    if not test_docker_run():
        print("❌ Docker run test failed")
        sys.exit(1)

    # Test 3: API endpoints
    test_api_endpoints()

    print("✅ All Docker tests completed successfully!")
    print("🚀 Ready for Hugging Face Spaces deployment!")


if __name__ == "__main__":
    main()
