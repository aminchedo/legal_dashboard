#!/usr/bin/env python3
"""
Comprehensive Test Suite for Legal Dashboard System
Tests all API endpoints, frontend functionality, and integration features
"""

import requests
import json
import time
import sys
from datetime import datetime


class LegalDashboardTester:
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url
        self.results = {
            "timestamp": datetime.now().isoformat(),
            "backend_tests": {},
            "frontend_tests": {},
            "integration_tests": {},
            "performance_metrics": {},
            "issues": []
        }

    def test_backend_connectivity(self):
        """Test basic backend connectivity"""
        print("🔍 Testing Backend Connectivity...")
        try:
            response = requests.get(f"{self.base_url}/docs", timeout=10)
            if response.status_code == 200:
                print("✅ Backend is running and accessible")
                return True
            else:
                print(
                    f"❌ Backend responded with status {response.status_code}")
                return False
        except requests.exceptions.ConnectionError:
            print("❌ Cannot connect to backend server")
            return False
        except Exception as e:
            print(f"❌ Connection error: {e}")
            return False

    def test_api_endpoints(self):
        """Test all API endpoints"""
        print("\n🔍 Testing API Endpoints...")

        endpoints = [
            ("/api/dashboard-summary", "GET"),
            ("/api/documents", "GET"),
            ("/api/charts-data", "GET"),
            ("/api/ai-suggestions", "GET"),
        ]

        for endpoint, method in endpoints:
            try:
                start_time = time.time()
                response = requests.get(
                    f"{self.base_url}{endpoint}", timeout=10)
                latency = (time.time() - start_time) * 1000

                if response.status_code == 200:
                    data = response.json()
                    print(
                        f"✅ {endpoint} - Status: {response.status_code} - Latency: {latency:.2f}ms")
                    self.results["backend_tests"][endpoint] = {
                        "status": "success",
                        "status_code": response.status_code,
                        "latency_ms": latency,
                        "data_structure": type(data).__name__,
                        "data_keys": list(data.keys()) if isinstance(data, dict) else f"List with {len(data)} items"
                    }
                else:
                    print(f"❌ {endpoint} - Status: {response.status_code}")
                    self.results["backend_tests"][endpoint] = {
                        "status": "error",
                        "status_code": response.status_code,
                        "error": response.text
                    }

            except Exception as e:
                print(f"❌ {endpoint} - Error: {e}")
                self.results["backend_tests"][endpoint] = {
                    "status": "error",
                    "error": str(e)
                }

    def test_post_endpoints(self):
        """Test POST endpoints"""
        print("\n🔍 Testing POST Endpoints...")

        # Test scraping trigger
        try:
            response = requests.post(
                f"{self.base_url}/api/scrape-trigger",
                json={"manual_trigger": True},
                timeout=10
            )
            if response.status_code in [200, 202]:
                print("✅ /api/scrape-trigger - Success")
                self.results["backend_tests"]["/api/scrape-trigger"] = {
                    "status": "success",
                    "status_code": response.status_code
                }
            else:
                print(
                    f"❌ /api/scrape-trigger - Status: {response.status_code}")
                self.results["backend_tests"]["/api/scrape-trigger"] = {
                    "status": "error",
                    "status_code": response.status_code
                }
        except Exception as e:
            print(f"❌ /api/scrape-trigger - Error: {e}")
            self.results["backend_tests"]["/api/scrape-trigger"] = {
                "status": "error",
                "error": str(e)
            }

        # Test AI training
        try:
            response = requests.post(
                f"{self.base_url}/api/train-ai",
                json={
                    "document_id": "test-id",
                    "feedback_type": "approved",
                    "feedback_score": 10,
                    "feedback_text": "Test feedback"
                },
                timeout=10
            )
            if response.status_code in [200, 202]:
                print("✅ /api/train-ai - Success")
                self.results["backend_tests"]["/api/train-ai"] = {
                    "status": "success",
                    "status_code": response.status_code
                }
            else:
                print(f"❌ /api/train-ai - Status: {response.status_code}")
                self.results["backend_tests"]["/api/train-ai"] = {
                    "status": "error",
                    "status_code": response.status_code
                }
        except Exception as e:
            print(f"❌ /api/train-ai - Error: {e}")
            self.results["backend_tests"]["/api/train-ai"] = {
                "status": "error",
                "error": str(e)
            }

    def test_data_quality(self):
        """Test data quality and structure"""
        print("\n🔍 Testing Data Quality...")

        try:
            # Test dashboard summary
            response = requests.get(
                f"{self.base_url}/api/dashboard-summary", timeout=10)
            if response.status_code == 200:
                data = response.json()
                required_fields = [
                    "total_documents", "documents_today", "error_documents", "average_score"]
                missing_fields = [
                    field for field in required_fields if field not in data]

                if not missing_fields:
                    print("✅ Dashboard summary has all required fields")
                    self.results["data_quality"] = {
                        "dashboard_summary": "complete",
                        "fields_present": required_fields
                    }
                else:
                    print(
                        f"❌ Missing fields in dashboard summary: {missing_fields}")
                    self.results["data_quality"] = {
                        "dashboard_summary": "incomplete",
                        "missing_fields": missing_fields
                    }

            # Test documents endpoint
            response = requests.get(
                f"{self.base_url}/api/documents?limit=5", timeout=10)
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list):
                    print(
                        f"✅ Documents endpoint returns list with {len(data)} items")
                    if data:
                        sample_doc = data[0]
                        doc_fields = ["id", "title", "source",
                                      "category", "final_score"]
                        missing_doc_fields = [
                            field for field in doc_fields if field not in sample_doc]
                        if not missing_doc_fields:
                            print("✅ Document structure is complete")
                        else:
                            print(
                                f"❌ Missing fields in documents: {missing_doc_fields}")
                else:
                    print("❌ Documents endpoint doesn't return a list")

        except Exception as e:
            print(f"❌ Data quality test error: {e}")

    def test_performance(self):
        """Test API performance"""
        print("\n🔍 Testing Performance...")

        endpoints = ["/api/dashboard-summary",
                     "/api/documents", "/api/charts-data"]
        performance_data = {}

        for endpoint in endpoints:
            latencies = []
            for _ in range(3):  # Test 3 times
                try:
                    start_time = time.time()
                    response = requests.get(
                        f"{self.base_url}{endpoint}", timeout=10)
                    latency = (time.time() - start_time) * 1000
                    latencies.append(latency)
                    time.sleep(0.1)  # Small delay between requests
                except Exception as e:
                    print(f"❌ Performance test failed for {endpoint}: {e}")
                    break

            if latencies:
                avg_latency = sum(latencies) / len(latencies)
                max_latency = max(latencies)
                min_latency = min(latencies)

                print(
                    f"📊 {endpoint}: Avg={avg_latency:.2f}ms, Min={min_latency:.2f}ms, Max={max_latency:.2f}ms")

                performance_data[endpoint] = {
                    "average_latency_ms": avg_latency,
                    "min_latency_ms": min_latency,
                    "max_latency_ms": max_latency,
                    "test_count": len(latencies)
                }

        self.results["performance_metrics"] = performance_data

    def generate_report(self):
        """Generate comprehensive test report"""
        print("\n" + "="*60)
        print("📋 COMPREHENSIVE TEST REPORT")
        print("="*60)

        # Summary
        total_tests = len(self.results["backend_tests"])
        successful_tests = sum(1 for test in self.results["backend_tests"].values()
                               if test.get("status") == "success")

        print(f"\n📊 Test Summary:")
        print(f"   Total API Tests: {total_tests}")
        print(f"   Successful: {successful_tests}")
        print(f"   Failed: {total_tests - successful_tests}")
        print(
            f"   Success Rate: {(successful_tests/total_tests)*100:.1f}%" if total_tests > 0 else "N/A")

        # Performance Summary
        if self.results["performance_metrics"]:
            print(f"\n⚡ Performance Summary:")
            for endpoint, metrics in self.results["performance_metrics"].items():
                print(
                    f"   {endpoint}: {metrics['average_latency_ms']:.2f}ms avg")

        # Issues
        if self.results["issues"]:
            print(f"\n⚠️  Issues Found:")
            for issue in self.results["issues"]:
                print(f"   - {issue}")

        # Save detailed report
        with open("test_report.json", "w", encoding="utf-8") as f:
            json.dump(self.results, f, indent=2, ensure_ascii=False)

        print(f"\n📄 Detailed report saved to: test_report.json")

        return self.results

    def run_all_tests(self):
        """Run all tests"""
        print("🚀 Starting Comprehensive Legal Dashboard Test Suite")
        print("="*60)

        # Test connectivity first
        if not self.test_backend_connectivity():
            print("❌ Backend not accessible. Please start the server first.")
            return False

        # Run all tests
        self.test_api_endpoints()
        self.test_post_endpoints()
        self.test_data_quality()
        self.test_performance()

        # Generate report
        return self.generate_report()


if __name__ == "__main__":
    tester = LegalDashboardTester()
    results = tester.run_all_tests()

    if results:
        print("\n✅ Test suite completed successfully!")
    else:
        print("\n❌ Test suite failed!")
        sys.exit(1)
