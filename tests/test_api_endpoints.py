#!/usr/bin/env python3
"""
Enhanced Analytics API Endpoint Verification
Tests all 8 new RESTful endpoints for the enhanced analytics system
"""

import requests
import json
import time
from typing import Dict, List, Any

class AnalyticsAPITester:
    def __init__(self, base_url: str = "http://localhost:8001"):
        self.base_url = base_url
        self.endpoints = [
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
        """Test a single endpoint and return detailed results"""
        try:
            start_time = time.time()
            response = requests.get(f"{self.base_url}{endpoint}", timeout=10)
            response_time = time.time() - start_time
            
            result = {
                "status_code": response.status_code,
                "response_time": round(response_time, 3),
                "success": response.status_code == 200,
                "content_type": response.headers.get("content-type", ""),
                "content_length": len(response.content),
                "error": None
            }
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    result["data_keys"] = list(data.keys()) if isinstance(data, dict) else "Not a dict"
                    result["data_sample"] = str(data)[:200] + "..." if len(str(data)) > 200 else str(data)
                except json.JSONDecodeError:
                    result["error"] = "Invalid JSON response"
                    result["raw_response"] = response.text[:200]
            else:
                result["error"] = f"HTTP {response.status_code}: {response.text[:200]}"
                
        except requests.exceptions.ConnectionError:
            result = {
                "status_code": 0,
                "response_time": 0,
                "success": False,
                "error": "Connection refused - server may not be running",
                "content_type": "",
                "content_length": 0
            }
        except requests.exceptions.Timeout:
            result = {
                "status_code": 0,
                "response_time": 0,
                "success": False,
                "error": "Request timeout",
                "content_type": "",
                "content_length": 0
            }
        except Exception as e:
            result = {
                "status_code": 0,
                "response_time": 0,
                "success": False,
                "error": f"Unexpected error: {str(e)}",
                "content_type": "",
                "content_length": 0
            }
            
        return result
    
    def test_all_endpoints(self) -> Dict[str, Any]:
        """Test all endpoints and return comprehensive results"""
        print("🔍 Testing Enhanced Analytics API Endpoints...")
        print("=" * 60)
        
        total_tests = len(self.endpoints)
        successful_tests = 0
        
        for endpoint in self.endpoints:
            print(f"\n📡 Testing: {endpoint}")
            result = self.test_endpoint(endpoint)
            self.results[endpoint] = result
            
            if result["success"]:
                print(f"   ✅ Status: {result['status_code']} | Time: {result['response_time']}s")
                print(f"   📊 Data Keys: {result.get('data_keys', 'N/A')}")
                print(f"   📝 Sample: {result.get('data_sample', 'N/A')}")
                successful_tests += 1
            else:
                print(f"   ❌ Status: {result['status_code']} | Error: {result['error']}")
        
        # Summary
        print("\n" + "=" * 60)
        print("📈 TEST SUMMARY")
        print("=" * 60)
        print(f"Total Endpoints Tested: {total_tests}")
        print(f"Successful: {successful_tests}")
        print(f"Failed: {total_tests - successful_tests}")
        print(f"Success Rate: {(successful_tests/total_tests)*100:.1f}%")
        
        # Detailed results
        print("\n📋 DETAILED RESULTS")
        print("=" * 60)
        for endpoint, result in self.results.items():
            status_icon = "✅" if result["success"] else "❌"
            print(f"{status_icon} {endpoint}")
            print(f"   Status: {result['status_code']} | Time: {result['response_time']}s")
            if result["error"]:
                print(f"   Error: {result['error']}")
            if result.get("data_keys"):
                print(f"   Data: {result['data_keys']}")
        
        return {
            "total_tests": total_tests,
            "successful_tests": successful_tests,
            "success_rate": (successful_tests/total_tests)*100,
            "results": self.results
        }
    
    def save_results(self, filename: str = "api_test_results.json"):
        """Save test results to JSON file"""
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, indent=2, ensure_ascii=False)
        print(f"\n💾 Results saved to: {filename}")

def main():
    """Main test execution"""
    print("🚀 Enhanced Analytics API Verification")
    print("=" * 60)
    
    tester = AnalyticsAPITester()
    summary = tester.test_all_endpoints()
    tester.save_results()
    
    # Final assessment
    print("\n🎯 FINAL ASSESSMENT")
    print("=" * 60)
    if summary["success_rate"] >= 95:
        print("✅ EXCELLENT: All analytics endpoints are working correctly!")
        print("   Ready for frontend integration and deployment.")
    elif summary["success_rate"] >= 80:
        print("⚠️  GOOD: Most endpoints working, some issues to address.")
        print("   Review failed endpoints before deployment.")
    elif summary["success_rate"] >= 50:
        print("⚠️  FAIR: Half of endpoints working, significant issues.")
        print("   Server may need restart or configuration fixes.")
    else:
        print("❌ POOR: Most endpoints failing, server likely down.")
        print("   Check server status and database connectivity.")
    
    return summary["success_rate"] >= 80

if __name__ == "__main__":
    main() 