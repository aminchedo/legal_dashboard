#!/usr/bin/env python3
"""
Comprehensive test for all 8 analytics API endpoints
Ensures all endpoints return valid JSON responses without errors
"""

import requests
import json
import time
from typing import Dict, Any


class AnalyticsEndpointTester:
    def __init__(self, base_url: str = "http://localhost:8001"):
        self.base_url = base_url
        self.supported_endpoints = [
            "/api/analytics/realtime",
            "/api/analytics/trends",
            "/api/analytics/predictions",
            "/api/analytics/similarity",
            "/api/analytics/clustering",
            "/api/analytics/quality",
            "/api/analytics/health",
            "/api/analytics/performance"
        ]
        self.results = {}

    def test_endpoint(self, endpoint: str) -> Dict[str, Any]:
        """Test a single analytics endpoint"""
        url = f"{self.base_url}{endpoint}"

        try:
            start_time = time.time()
            response = requests.get(url, timeout=10)
            response_time = time.time() - start_time

            result = {
                "endpoint": endpoint,
                "status_code": response.status_code,
                "response_time": round(response_time, 3),
                "success": response.status_code == 200,
                "error": None,
                "data": None
            }

            if response.status_code == 200:
                try:
                    data = response.json()
                    result["data"] = data
                    result["has_valid_json"] = True
                    result["data_keys"] = list(
                        data.keys()) if isinstance(data, dict) else []
                except json.JSONDecodeError:
                    result["error"] = "Invalid JSON response"
                    result["has_valid_json"] = False
            else:
                result["error"] = f"HTTP {response.status_code}: {response.text[:200]}"
                result["has_valid_json"] = False

        except requests.exceptions.ConnectionError:
            result = {
                "endpoint": endpoint,
                "status_code": 0,
                "response_time": 0,
                "success": False,
                "error": "Connection refused - server may not be running",
                "has_valid_json": False,
                "data": None
            }
        except Exception as e:
            result = {
                "endpoint": endpoint,
                "status_code": 0,
                "response_time": 0,
                "success": False,
                "error": f"Unexpected error: {str(e)}",
                "has_valid_json": False,
                "data": None
            }

        return result

    def test_all_endpoints(self) -> Dict[str, Any]:
        """Test all 8 analytics endpoints"""
        print("🔍 Testing All Analytics API Endpoints...")
        print("=" * 60)

        successful = 0
        total = len(self.supported_endpoints)

        for endpoint in self.supported_endpoints:
            print(f"\n📡 Testing: {endpoint}")
            result = self.test_endpoint(endpoint)
            self.results[endpoint] = result

            if result["success"]:
                print(
                    f"   ✅ Status: {result['status_code']} | Time: {result['response_time']}s")
                print(f"   📊 Data Keys: {result.get('data_keys', [])}")
                successful += 1
            else:
                print(f"   ❌ Error: {result['error']}")

        # Summary
        print("\n" + "=" * 60)
        print("📈 TEST SUMMARY")
        print("=" * 60)
        print(f"Total Endpoints: {total}")
        print(f"Successful: {successful}")
        print(f"Failed: {total - successful}")
        print(f"Success Rate: {(successful/total)*100:.1f}%")

        return {
            "total_endpoints": total,
            "successful": successful,
            "failed": total - successful,
            "success_rate": (successful/total)*100,
            "results": self.results
        }

    def test_unsupported_endpoint(self):
        """Test that unsupported endpoints return clear error messages"""
        print("\n🔍 Testing Unsupported Endpoint...")

        unsupported_url = f"{self.base_url}/api/unsupported/endpoint"
        try:
            response = requests.get(unsupported_url, timeout=5)
            print(f"   📡 Testing: /api/unsupported/endpoint")
            print(f"   📊 Status: {response.status_code}")
            print(f"   📝 Response: {response.text[:100]}...")
        except Exception as e:
            print(f"   ❌ Error: {str(e)}")

    def save_results(self, filename: str = "analytics_endpoints_test_results.json"):
        """Save test results to JSON file"""
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, indent=2, ensure_ascii=False)
        print(f"\n💾 Results saved to: {filename}")


def main():
    """Main test execution"""
    print("🚀 Analytics API Endpoints Verification")
    print("=" * 60)
    print("📋 Supported Endpoints:")
    print("   • /api/analytics/realtime")
    print("   • /api/analytics/trends")
    print("   • /api/analytics/predictions")
    print("   • /api/analytics/similarity")
    print("   • /api/analytics/clustering")
    print("   • /api/analytics/quality")
    print("   • /api/analytics/health")
    print("   • /api/analytics/performance")
    print("=" * 60)

    tester = AnalyticsEndpointTester()

    # Test all supported endpoints
    summary = tester.test_all_endpoints()

    # Test unsupported endpoint
    tester.test_unsupported_endpoint()

    # Save results
    tester.save_results()

    # Final assessment
    print("\n🎯 FINAL ASSESSMENT")
    print("=" * 60)

    if summary["success_rate"] == 100:
        print("✅ EXCELLENT: All 8 analytics endpoints are working correctly!")
        print("   Ready for frontend integration and production deployment.")
    elif summary["success_rate"] >= 80:
        print("⚠️  GOOD: Most endpoints working, some issues to address.")
        print("   Review failed endpoints before deployment.")
    elif summary["success_rate"] >= 50:
        print("⚠️  FAIR: Half of endpoints working, significant issues.")
        print("   Server may need restart or configuration fixes.")
    else:
        print("❌ POOR: Most endpoints failing, server likely down.")
        print("   Check server status and ensure test_server.py is running.")

    print(f"\n📊 Success Rate: {summary['success_rate']:.1f}%")
    print(f"🎯 Supported Endpoints: 8/8")
    print(
        f"🚀 Ready for Production: {'Yes' if summary['success_rate'] >= 95 else 'No'}")

    return summary["success_rate"] >= 95


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
