#!/usr/bin/env python3
"""
Test Runner for Legal Dashboard OCR
==================================

Comprehensive test runner that can execute all tests or specific test categories.
Supports running backend tests, docker tests, or all tests together.
"""

import os
import sys
import subprocess
import argparse
from pathlib import Path


def run_backend_tests():
    """Run backend tests"""
    print("🧪 Running Backend Tests...")
    print("=" * 50)

    backend_tests = [
        "tests/backend/test_api_endpoints.py",
        "tests/backend/test_ocr_pipeline.py",
        "tests/backend/test_ocr_fixes.py",
        "tests/backend/test_hf_deployment_fixes.py",
        "tests/backend/test_db_connection.py",
        "tests/backend/test_structure.py",
        "tests/backend/validate_fixes.py",
        "tests/backend/verify_frontend.py"
    ]

    for test_file in backend_tests:
        if os.path.exists(test_file):
            print(f"Running: {test_file}")
            try:
                result = subprocess.run([sys.executable, test_file],
                                        capture_output=True, text=True)
                if result.returncode == 0:
                    print(f"✅ {test_file}: PASSED")
                else:
                    print(f"❌ {test_file}: FAILED")
                    print(result.stderr)
            except Exception as e:
                print(f"❌ {test_file}: ERROR - {e}")
        else:
            print(f"⚠️ {test_file}: Not found")


def run_docker_tests():
    """Run docker tests"""
    print("🐳 Running Docker Tests...")
    print("=" * 50)

    docker_tests = [
        "tests/docker/test_docker.py",
        "tests/docker/validate_docker_setup.py",
        "tests/docker/simple_validation.py",
        "tests/docker/test_hf_deployment.py",
        "tests/docker/deployment_validation.py"
    ]

    for test_file in docker_tests:
        if os.path.exists(test_file):
            print(f"Running: {test_file}")
            try:
                result = subprocess.run([sys.executable, test_file],
                                        capture_output=True, text=True)
                if result.returncode == 0:
                    print(f"✅ {test_file}: PASSED")
                else:
                    print(f"❌ {test_file}: FAILED")
                    print(result.stderr)
            except Exception as e:
                print(f"❌ {test_file}: ERROR - {e}")
        else:
            print(f"⚠️ {test_file}: Not found")


def run_all_tests():
    """Run all tests"""
    print("🚀 Running All Tests...")
    print("=" * 50)

    run_backend_tests()
    print("\n")
    run_docker_tests()


def run_pytest():
    """Run tests using pytest"""
    print("🧪 Running Tests with pytest...")
    print("=" * 50)

    try:
        result = subprocess.run([sys.executable, "-m", "pytest", "tests/", "-v"],
                                capture_output=True, text=True)
        print(result.stdout)
        if result.stderr:
            print("Errors:")
            print(result.stderr)
        return result.returncode == 0
    except Exception as e:
        print(f"❌ pytest execution failed: {e}")
        return False


def main():
    """Main test runner"""
    parser = argparse.ArgumentParser(
        description="Legal Dashboard OCR Test Runner")
    parser.add_argument("--backend", action="store_true",
                        help="Run only backend tests")
    parser.add_argument("--docker", action="store_true",
                        help="Run only docker tests")
    parser.add_argument("--pytest", action="store_true",
                        help="Run tests using pytest")
    parser.add_argument("--all", action="store_true",
                        help="Run all tests (default)")

    args = parser.parse_args()

    print("🧪 Legal Dashboard OCR Test Runner")
    print("=" * 50)

    if args.pytest:
        success = run_pytest()
        sys.exit(0 if success else 1)
    elif args.backend:
        run_backend_tests()
    elif args.docker:
        run_docker_tests()
    else:
        # Default: run all tests
        run_all_tests()

    print("\n" + "=" * 50)
    print("✅ Test execution completed!")


if __name__ == "__main__":
    main()
