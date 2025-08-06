#!/usr/bin/env python3
"""
Validation Script for Legal Dashboard API Integration
Tests all endpoints and validates the implementation
"""

import asyncio
import aiohttp
import json
import time
from typing import Dict, List, Any


class APIImplementationValidator:
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.results = []
        self.start_time = None

    async def test_endpoint(self, session: aiohttp.ClientSession, endpoint: str, method: str = "GET",
                            expected_status: int = 200, data: Dict = None) -> Dict[str, Any]:
        """Test a single API endpoint"""
        url = f"{self.base_url}{endpoint}"
        start_time = time.time()

        try:
            if method == "GET":
                async with session.get(url) as response:
                    response_time = (time.time() - start_time) * 1000
                    success = response.status == expected_status

                    result = {
                        "endpoint": endpoint,
                        "method": method,
                        "url": url,
                        "status": response.status,
                        "success": success,
                        "response_time": round(response_time, 2),
                        "error": None if success else f"Expected {expected_status}, got {response.status}"
                    }

                    if success:
                        try:
                            result["data"] = await response.json()
                        except:
                            result["data"] = await response.text()

                    return result

            elif method == "POST":
                async with session.post(url, json=data) as response:
                    response_time = (time.time() - start_time) * 1000
                    success = response.status == expected_status

                    result = {
                        "endpoint": endpoint,
                        "method": method,
                        "url": url,
                        "status": response.status,
                        "success": success,
                        "response_time": round(response_time, 2),
                        "error": None if success else f"Expected {expected_status}, got {response.status}"
                    }

                    if success:
                        try:
                            result["data"] = await response.json()
                        except:
                            result["data"] = await response.text()

                    return result

        except Exception as e:
            return {
                "endpoint": endpoint,
                "method": method,
                "url": url,
                "status": 0,
                "success": False,
                "response_time": round((time.time() - start_time) * 1000, 2),
                "error": str(e)
            }

    async def run_comprehensive_tests(self) -> List[Dict[str, Any]]:
        """Run comprehensive API tests"""
        print("🚀 Starting comprehensive API validation...")
        self.start_time = time.time()

        # Define test endpoints
        test_endpoints = [
            # System endpoints
            ("/api/health", "GET", 200),

            # Dashboard endpoints
            ("/api/dashboard/summary", "GET", 200),
            ("/api/dashboard/charts-data", "GET", 200),
            ("/api/dashboard/ai-suggestions", "GET", 200),
            ("/api/dashboard/ai-feedback", "POST", 200),
            ("/api/dashboard/performance-metrics", "GET", 200),
            ("/api/dashboard/trends", "GET", 200),

            # Documents endpoints
            ("/api/documents", "GET", 200),
            ("/api/documents/search/", "GET", 200),
            ("/api/documents/categories/", "GET", 200),
            ("/api/documents/sources/", "GET", 200),

            # OCR endpoints
            ("/api/ocr/process", "POST", 200),
            ("/api/ocr/process-and-save", "POST", 200),
            ("/api/ocr/batch-process", "POST", 200),
            ("/api/ocr/quality-metrics", "GET", 200),
            ("/api/ocr/models", "GET", 200),
            ("/api/ocr/status", "GET", 200),

            # Analytics endpoints
            ("/api/analytics/overview", "GET", 200),
            ("/api/analytics/trends", "GET", 200),
            ("/api/analytics/similarity", "GET", 200),
            ("/api/analytics/performance", "GET", 200),
            ("/api/analytics/entities", "GET", 200),
            ("/api/analytics/quality-analysis", "GET", 200),

            # Scraping endpoints
            ("/api/scraping/scrape", "POST", 200),
            ("/api/scraping/status", "GET", 200),
            ("/api/scraping/items", "GET", 200),
            ("/api/scraping/statistics", "GET", 200),
            ("/api/scraping/rating/summary", "GET", 200),
        ]

        async with aiohttp.ClientSession() as session:
            tasks = []
            for endpoint, method, expected_status in test_endpoints:
                if method == "POST":
                    # Add sample data for POST requests
                    data = {"test": "data"} if "ocr" in endpoint else {
                        "url": "https://example.com"}
                    task = self.test_endpoint(
                        session, endpoint, method, expected_status, data)
                else:
                    task = self.test_endpoint(
                        session, endpoint, method, expected_status)
                tasks.append(task)

            results = await asyncio.gather(*tasks, return_exceptions=True)

            # Process results
            for result in results:
                if isinstance(result, Exception):
                    self.results.append({
                        "endpoint": "unknown",
                        "method": "GET",
                        "url": "unknown",
                        "status": 0,
                        "success": False,
                        "response_time": 0,
                        "error": str(result)
                    })
                else:
                    self.results.append(result)

        return self.results

    def generate_report(self) -> Dict[str, Any]:
        """Generate a comprehensive validation report"""
        if not self.results:
            return {"error": "No test results available"}

        total_tests = len(self.results)
        successful_tests = sum(1 for r in self.results if r["success"])
        failed_tests = total_tests - successful_tests
        success_rate = (successful_tests / total_tests *
                        100) if total_tests > 0 else 0

        # Group by category
        categories = {
            "System": [],
            "Dashboard": [],
            "Documents": [],
            "OCR": [],
            "Analytics": [],
            "Scraping": []
        }

        for result in self.results:
            endpoint = result["endpoint"]
            if "/health" in endpoint:
                categories["System"].append(result)
            elif "/dashboard" in endpoint:
                categories["Dashboard"].append(result)
            elif "/documents" in endpoint:
                categories["Documents"].append(result)
            elif "/ocr" in endpoint:
                categories["OCR"].append(result)
            elif "/analytics" in endpoint:
                categories["Analytics"].append(result)
            elif "/scraping" in endpoint:
                categories["Scraping"].append(result)

        # Calculate category success rates
        category_stats = {}
        for category, results in categories.items():
            if results:
                category_success = sum(1 for r in results if r["success"])
                category_total = len(results)
                category_rate = (
                    category_success / category_total * 100) if category_total > 0 else 0
                category_stats[category] = {
                    "total": category_total,
                    "successful": category_success,
                    "failed": category_total - category_success,
                    "success_rate": round(category_rate, 1)
                }

        # Calculate average response time
        successful_responses = [r for r in self.results if r["success"]]
        avg_response_time = sum(r["response_time"] for r in successful_responses) / len(
            successful_responses) if successful_responses else 0

        report = {
            "summary": {
                "total_tests": total_tests,
                "successful_tests": successful_tests,
                "failed_tests": failed_tests,
                "success_rate": round(success_rate, 1),
                "avg_response_time": round(avg_response_time, 2),
                "total_time": round((time.time() - self.start_time) * 1000, 2) if self.start_time else 0
            },
            "category_stats": category_stats,
            "detailed_results": self.results,
            "status": "PASS" if success_rate >= 95 else "FAIL"
        }

        return report

    def print_report(self, report: Dict[str, Any]):
        """Print a formatted validation report"""
        print("\n" + "="*60)
        print("🔧 LEGAL DASHBOARD API IMPLEMENTATION VALIDATION")
        print("="*60)

        summary = report["summary"]
        print(f"\n📊 SUMMARY:")
        print(f"   Total Tests: {summary['total_tests']}")
        print(f"   Successful: {summary['successful_tests']} ✅")
        print(f"   Failed: {summary['failed_tests']} ❌")
        print(f"   Success Rate: {summary['success_rate']}%")
        print(f"   Avg Response Time: {summary['avg_response_time']}ms")
        print(f"   Total Test Time: {summary['total_time']}ms")

        print(f"\n🎯 TARGET: 95% Success Rate")
        print(f"📈 ACHIEVED: {summary['success_rate']}%")
        print(f"📋 STATUS: {report['status']}")

        print(f"\n📋 CATEGORY BREAKDOWN:")
        for category, stats in report["category_stats"].items():
            status = "✅" if stats["success_rate"] >= 95 else "⚠️" if stats["success_rate"] >= 80 else "❌"
            print(
                f"   {category}: {stats['successful']}/{stats['total']} ({stats['success_rate']}%) {status}")

        print(f"\n🔍 DETAILED RESULTS:")
        for result in report["detailed_results"]:
            status = "✅" if result["success"] else "❌"
            print(
                f"   {status} {result['method']} {result['endpoint']} - {result['status']} ({result['response_time']}ms)")
            if result["error"]:
                print(f"      Error: {result['error']}")

        print("\n" + "="*60)

        if report["status"] == "PASS":
            print("🎉 IMPLEMENTATION VALIDATION SUCCESSFUL!")
            print("✅ All critical endpoints are working correctly")
            print("✅ Ready for production deployment")
        else:
            print("⚠️  IMPLEMENTATION NEEDS ATTENTION")
            print("❌ Some endpoints are not working as expected")
            print("🔧 Review failed endpoints and fix issues")

        print("="*60)


async def main():
    """Main validation function"""
    validator = APIImplementationValidator()

    try:
        # Run comprehensive tests
        results = await validator.run_comprehensive_tests()

        # Generate and print report
        report = validator.generate_report()
        validator.print_report(report)

        # Save detailed report to file
        with open("validation_report.json", "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2, ensure_ascii=False)

        print(f"\n📄 Detailed report saved to: validation_report.json")

        return report["status"] == "PASS"

    except Exception as e:
        print(f"❌ Validation failed: {e}")
        return False

if __name__ == "__main__":
    success = asyncio.run(main())
    exit(0 if success else 1)
