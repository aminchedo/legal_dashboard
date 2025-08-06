#!/usr/bin/env python3
"""
Backend Health Check Script
Detects and starts FastAPI backend server, then tests all analytics endpoints
"""

import requests
import subprocess
import time
import os
import sys

BASE_URL = "http://localhost:8001"
ANALYTICS_ENDPOINTS = [
    "/api/analytics/realtime",
    "/api/analytics/trends",
    "/api/analytics/predictions",
    "/api/analytics/similarity",
    "/api/analytics/clustering",
    "/api/analytics/quality",
    "/api/analytics/health",
    "/api/analytics/performance"
]


def check_backend_running():
    """Check if FastAPI server is running on localhost:8000"""
    try:
        response = requests.get(BASE_URL + "/docs", timeout=3)
        if response.status_code == 200:
            print("✅ FastAPI server is running on", BASE_URL)
            return True
    except requests.exceptions.RequestException:
        print("❌ Backend server is not responding.")
    return False


def check_port_usage():
    """Check if port 8000 is already in use"""
    try:
        result = subprocess.run(
            ["netstat", "-ano", "|", "findstr", ":8000"],
            shell=True, capture_output=True, text=True
        )
        if result.stdout.strip():
            print("⚠️  Port 8000 is already in use:")
            print(result.stdout)
            return True
        return False
    except Exception as e:
        print(f"⚠️  Could not check port usage: {e}")
        return False


def start_backend():
    """Start the FastAPI backend server"""
    print("🚀 Attempting to start FastAPI backend server...")

    # Check if we're in the right directory
    current_dir = os.getcwd()
    print(f"📁 Current directory: {current_dir}")

    # Look for the main.py file
    main_py_path = os.path.join(current_dir, "app", "main.py")
    if not os.path.exists(main_py_path):
        print(f"❌ Could not find app/main.py at {main_py_path}")
        return None

    print(f"✅ Found main.py at {main_py_path}")

    # Start the server using uvicorn
    try:
        process = subprocess.Popen(
            ["python", "-m", "uvicorn", "app.main:app",
                "--reload", "--host", "0.0.0.0", "--port", "8000"],
            cwd=current_dir,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        print("⏳ Waiting 10 seconds for server startup...")
        time.sleep(10)
        return process
    except Exception as e:
        print(f"❌ Failed to start server: {e}")
        return None


def test_endpoints():
    """Test all analytics endpoints"""
    print("\n🔍 Testing analytics endpoints...")
    results = {}
    successful = 0

    for endpoint in ANALYTICS_ENDPOINTS:
        url = BASE_URL + endpoint
        try:
            response = requests.get(url, timeout=5)
            status = response.status_code
            if status == 200:
                print(f"✅ {endpoint} | Status: {status}")
                results[endpoint] = "OK"
                successful += 1
            else:
                print(f"⚠️  {endpoint} | Status: {status}")
                results[endpoint] = f"FAIL ({status})"
        except requests.exceptions.RequestException as e:
            print(f"❌ {endpoint} | Error: {str(e)}")
            results[endpoint] = "ERROR"

    return results, successful


def main():
    """Main health check execution"""
    print("🔧 Starting Backend Health Check...")
    print("=" * 60)

    # Check if server is already running
    server_running = check_backend_running()
    process = None

    if not server_running:
        print("\n📡 Server not running. Starting backend...")

        # Check for port conflicts
        if check_port_usage():
            print(
                "⚠️  Port 8000 is in use. You may need to stop the conflicting process.")
            print("   Run: netstat -ano | findstr :8000")
            print("   Then: taskkill /PID <PID> /F")

        # Start the server
        process = start_backend()

        # Check if server started successfully
        if not check_backend_running():
            print("❌ Backend server failed to start. Please check:")
            print(
                "   1. Are all dependencies installed? (pip install -r requirements.txt)")
            print("   2. Is port 8000 available?")
            print("   3. Are there any import errors in app/main.py?")
            return False

    # Test all endpoints
    results, successful = test_endpoints()

    # Summary
    print("\n" + "=" * 60)
    print("📊 TEST SUMMARY")
    print("=" * 60)
    total_endpoints = len(ANALYTICS_ENDPOINTS)
    success_rate = (successful / total_endpoints) * 100

    for endpoint, status in results.items():
        icon = "✅" if status == "OK" else "❌"
        print(f"{icon} {endpoint}: {status}")

    print(
        f"\n📈 Success Rate: {successful}/{total_endpoints} ({success_rate:.1f}%)")

    # Cleanup
    if process:
        print("\n🛑 Stopping temporary backend server...")
        process.terminate()
        process.wait()

    # Final assessment
    print("\n🎯 FINAL ASSESSMENT")
    print("=" * 60)
    if success_rate >= 95:
        print("✅ EXCELLENT: All analytics endpoints are working correctly!")
        print("   Ready for frontend integration and deployment.")
    elif success_rate >= 80:
        print("⚠️  GOOD: Most endpoints working, some issues to address.")
        print("   Review failed endpoints before deployment.")
    elif success_rate >= 50:
        print("⚠️  FAIR: Half of endpoints working, significant issues.")
        print("   Server may need restart or configuration fixes.")
    else:
        print("❌ POOR: Most endpoints failing, server likely down.")
        print("   Check server status and database connectivity.")

    return success_rate >= 80


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
