#!/usr/bin/env python3
"""
Integration Test for Legal Dashboard Frontend-Backend
====================================================
Tests the complete integration between frontend and backend.
"""

import requests
import json
import time
import os
from pathlib import Path

class IntegrationTest:
    def __init__(self, base_url="http://localhost:7860"):
        self.base_url = base_url
        self.api_base = f"{base_url}/api"
        self.test_results = []
        
    def log_test(self, test_name, success, message="", data=None):
        """Log test result"""
        result = {
            "test": test_name,
            "success": success,
            "message": message,
            "data": data,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
        }
        self.test_results.append(result)
        
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}: {message}")
        if data:
            print(f"   Data: {json.dumps(data, indent=2, ensure_ascii=False)}")
        print()
        
    def test_health_endpoint(self):
        """Test health check endpoint"""
        try:
            response = requests.get(f"{self.api_base}/health", timeout=10)
            if response.status_code == 200:
                data = response.json()
                self.log_test("Health Check", True, "Health endpoint working", data)
                return True
            else:
                self.log_test("Health Check", False, f"Status code: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Health Check", False, f"Error: {str(e)}")
            return False
    
    def test_dashboard_summary(self):
        """Test dashboard summary endpoint"""
        try:
            response = requests.get(f"{self.api_base}/dashboard/summary", timeout=10)
            if response.status_code == 200:
                data = response.json()
                if data.get("success") and "data" in data:
                    self.log_test("Dashboard Summary", True, "Dashboard data retrieved", data["data"])
                    return True
                else:
                    self.log_test("Dashboard Summary", False, "Invalid response structure")
                    return False
            else:
                self.log_test("Dashboard Summary", False, f"Status code: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Dashboard Summary", False, f"Error: {str(e)}")
            return False
    
    def test_documents_endpoint(self):
        """Test documents endpoint"""
        try:
            response = requests.get(f"{self.api_base}/documents/?limit=5", timeout=10)
            if response.status_code == 200:
                data = response.json()
                if data.get("success") and "data" in data:
                    self.log_test("Documents List", True, f"Retrieved {len(data['data']['documents'])} documents", data["data"])
                    return True
                else:
                    self.log_test("Documents List", False, "Invalid response structure")
                    return False
            else:
                self.log_test("Documents List", False, f"Status code: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Documents List", False, f"Error: {str(e)}")
            return False
    
    def test_file_upload(self):
        """Test file upload functionality"""
        try:
            # Create a test file
            test_file_path = "/tmp/test_integration.txt"
            with open(test_file_path, "w", encoding="utf-8") as f:
                f.write("این یک فایل تست برای بررسی یکپارچگی است.\n")
                f.write("This is a test file for integration testing.\n")
            
            # Upload the file
            with open(test_file_path, "rb") as f:
                files = {"files": ("test_integration.txt", f, "text/plain")}
                response = requests.post(f"{self.api_base}/ocr/upload", files=files, timeout=30)
            
            # Clean up test file
            os.remove(test_file_path)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success") and "data" in data:
                    self.log_test("File Upload", True, "File uploaded successfully", data["data"])
                    return True
                else:
                    self.log_test("File Upload", False, "Invalid response structure")
                    return False
            else:
                self.log_test("File Upload", False, f"Status code: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("File Upload", False, f"Error: {str(e)}")
            return False
    
    def test_charts_endpoints(self):
        """Test chart data endpoints"""
        endpoints = [
            ("/dashboard/charts/processing-trends", "Processing Trends"),
            ("/dashboard/charts/status-distribution", "Status Distribution"),
            ("/dashboard/charts/category-distribution", "Category Distribution")
        ]
        
        all_success = True
        for endpoint, name in endpoints:
            try:
                response = requests.get(f"{self.api_base}{endpoint}", timeout=10)
                if response.status_code == 200:
                    data = response.json()
                    if data.get("success") and "data" in data:
                        self.log_test(f"Chart: {name}", True, "Chart data retrieved", data["data"])
                    else:
                        self.log_test(f"Chart: {name}", False, "Invalid response structure")
                        all_success = False
                else:
                    self.log_test(f"Chart: {name}", False, f"Status code: {response.status_code}")
                    all_success = False
            except Exception as e:
                self.log_test(f"Chart: {name}", False, f"Error: {str(e)}")
                all_success = False
        
        return all_success
    
    def test_frontend_accessibility(self):
        """Test if frontend is accessible"""
        try:
            response = requests.get(self.base_url, timeout=10)
            if response.status_code == 200:
                content = response.text
                if "داشبورد حقوقی" in content or "Legal Dashboard" in content:
                    self.log_test("Frontend Accessibility", True, "Frontend is accessible")
                    return True
                else:
                    self.log_test("Frontend Accessibility", False, "Frontend content not found")
                    return False
            else:
                self.log_test("Frontend Accessibility", False, f"Status code: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Frontend Accessibility", False, f"Error: {str(e)}")
            return False
    
    def test_api_documentation(self):
        """Test API documentation endpoint"""
        try:
            response = requests.get(f"{self.api_base}/docs", timeout=10)
            if response.status_code == 200:
                self.log_test("API Documentation", True, "API docs accessible")
                return True
            else:
                self.log_test("API Documentation", False, f"Status code: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("API Documentation", False, f"Error: {str(e)}")
            return False
    
    def test_cors_headers(self):
        """Test CORS headers"""
        try:
            headers = {"Origin": "http://localhost:3000"}
            response = requests.get(f"{self.api_base}/health", headers=headers, timeout=10)
            cors_headers = response.headers.get("Access-Control-Allow-Origin")
            if cors_headers:
                self.log_test("CORS Headers", True, "CORS headers present")
                return True
            else:
                self.log_test("CORS Headers", False, "CORS headers missing")
                return False
        except Exception as e:
            self.log_test("CORS Headers", False, f"Error: {str(e)}")
            return False
    
    def run_all_tests(self):
        """Run all integration tests"""
        print("🔗 Starting Frontend-Backend Integration Tests")
        print("=" * 60)
        
        tests = [
            self.test_health_endpoint,
            self.test_dashboard_summary,
            self.test_documents_endpoint,
            self.test_file_upload,
            self.test_charts_endpoints,
            self.test_frontend_accessibility,
            self.test_api_documentation,
            self.test_cors_headers
        ]
        
        passed = 0
        total = len(tests)
        
        for test in tests:
            try:
                if test():
                    passed += 1
            except Exception as e:
                self.log_test(test.__name__, False, f"Test failed with exception: {str(e)}")
        
        # Generate summary
        print("=" * 60)
        print(f"📊 INTEGRATION TEST SUMMARY")
        print("=" * 60)
        print(f"✅ Passed: {passed}/{total}")
        print(f"❌ Failed: {total - passed}/{total}")
        print(f"📈 Success Rate: {(passed/total)*100:.1f}%")
        
        # Save detailed results
        results_file = "integration_test_results.json"
        with open(results_file, "w", encoding="utf-8") as f:
            json.dump({
                "summary": {
                    "passed": passed,
                    "total": total,
                    "success_rate": (passed/total)*100
                },
                "tests": self.test_results
            }, f, indent=2, ensure_ascii=False)
        
        print(f"📄 Detailed results saved to: {results_file}")
        
        if passed == total:
            print("🎉 ALL TESTS PASSED! Frontend-Backend integration is working perfectly!")
            return True
        else:
            print("⚠️ Some tests failed. Please check the results above.")
            return False

def main():
    """Main test runner"""
    test = IntegrationTest()
    success = test.run_all_tests()
    
    if success:
        print("\n🚀 INTEGRATION STATUS: EXCELLENT")
        print("✅ Frontend and backend are fully integrated and working!")
        print("✅ All API endpoints are responding correctly")
        print("✅ File upload functionality is working")
        print("✅ Dashboard data is being served")
        print("✅ Frontend is accessible and functional")
    else:
        print("\n⚠️ INTEGRATION STATUS: NEEDS ATTENTION")
        print("❌ Some integration points need to be fixed")
        print("❌ Check the test results above for details")

if __name__ == "__main__":
    main()