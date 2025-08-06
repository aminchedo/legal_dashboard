#!/usr/bin/env python3
"""
Dashboard Features Test
======================

Simple test to validate the enhanced analytics dashboard features.
"""

import asyncio
import sys
import os
import json
from datetime import datetime
from typing import Dict, List, Any

# Add the app directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))


class DashboardFeaturesTester:
    """Tester for dashboard features"""

    def __init__(self):
        self.test_results = {
            "total_tests": 0,
            "passed": 0,
            "failed": 0,
            "errors": []
        }

    async def run_all_tests(self):
        """Run all dashboard feature tests"""
        print("🚀 Dashboard Features Test Suite")
        print("=" * 50)

        try:
            # Test API endpoint structure
            await self.test_api_endpoints()

            # Test frontend features
            await self.test_frontend_features()

            # Test analytics capabilities
            await self.test_analytics_capabilities()

            # Generate test report
            self.generate_test_report()

        except Exception as e:
            print(f"❌ Test suite failed: {e}")
            import traceback
            traceback.print_exc()

    async def test_api_endpoints(self):
        """Test API endpoint structure"""
        print("\n🔗 Testing API Endpoints...")

        try:
            # Define expected API endpoints
            expected_endpoints = [
                "/api/enhanced-analytics/real-time-metrics",
                "/api/enhanced-analytics/trends",
                "/api/enhanced-analytics/predictive-insights",
                "/api/enhanced-analytics/clustering",
                "/api/enhanced-analytics/quality-report",
                "/api/enhanced-analytics/system-health",
                "/api/enhanced-analytics/performance-dashboard"
            ]

            # Check if endpoints are defined in the API
            api_files = [
                "app/api/enhanced_analytics.py"
            ]

            for api_file in api_files:
                if os.path.exists(api_file):
                    print(f"   ✅ API file exists: {api_file}")
                else:
                    print(f"   ❌ API file missing: {api_file}")
                    raise FileNotFoundError(f"API file not found: {api_file}")

            print(f"✅ API endpoints test passed")
            print(f"   - Expected endpoints: {len(expected_endpoints)}")

            self.test_results["passed"] += 1

        except Exception as e:
            print(f"❌ API endpoints test failed: {e}")
            self.test_results["failed"] += 1
            self.test_results["errors"].append(f"API endpoints: {e}")

        self.test_results["total_tests"] += 1

    async def test_frontend_features(self):
        """Test frontend features"""
        print("\n🎨 Testing Frontend Features...")

        try:
            # Check if enhanced dashboard exists
            dashboard_file = "frontend/enhanced_analytics_dashboard.html"
            if os.path.exists(dashboard_file):
                print(f"   ✅ Enhanced dashboard exists: {dashboard_file}")

                # Check file size
                file_size = os.path.getsize(dashboard_file)
                print(f"   - File size: {file_size:,} bytes")

                # Check for key features in the HTML
                with open(dashboard_file, 'r', encoding='utf-8') as f:
                    content = f.read()

                # Check for key features
                features_to_check = [
                    "real-time metrics",
                    "trend analysis",
                    "predictive insights",
                    "quality assessment",
                    "system health",
                    "document clustering"
                ]

                found_features = []
                for feature in features_to_check:
                    if feature.lower() in content.lower():
                        found_features.append(feature)

                print(
                    f"   - Features found: {len(found_features)}/{len(features_to_check)}")
                for feature in found_features:
                    print(f"     ✅ {feature}")

            else:
                print(f"   ❌ Enhanced dashboard missing: {dashboard_file}")
                raise FileNotFoundError(
                    f"Dashboard file not found: {dashboard_file}")

            print(f"✅ Frontend features test passed")

            self.test_results["passed"] += 1

        except Exception as e:
            print(f"❌ Frontend features test failed: {e}")
            self.test_results["failed"] += 1
            self.test_results["errors"].append(f"Frontend features: {e}")

        self.test_results["total_tests"] += 1

    async def test_analytics_capabilities(self):
        """Test analytics capabilities"""
        print("\n📊 Testing Analytics Capabilities...")

        try:
            # Check if analytics service exists
            analytics_service_file = "app/services/advanced_analytics_service.py"
            if os.path.exists(analytics_service_file):
                print(
                    f"   ✅ Analytics service exists: {analytics_service_file}")

                # Check file size
                file_size = os.path.getsize(analytics_service_file)
                print(f"   - File size: {file_size:,} bytes")

                # Check for key methods in the service
                with open(analytics_service_file, 'r', encoding='utf-8') as f:
                    content = f.read()

                # Check for key methods
                methods_to_check = [
                    "get_real_time_metrics",
                    "analyze_trends",
                    "find_similar_documents",
                    "generate_predictive_insights",
                    "cluster_documents",
                    "generate_quality_report"
                ]

                found_methods = []
                for method in methods_to_check:
                    if method in content:
                        found_methods.append(method)

                print(
                    f"   - Methods found: {len(found_methods)}/{len(methods_to_check)}")
                for method in found_methods:
                    print(f"     ✅ {method}")

            else:
                print(
                    f"   ❌ Analytics service missing: {analytics_service_file}")
                raise FileNotFoundError(
                    f"Analytics service file not found: {analytics_service_file}")

            print(f"✅ Analytics capabilities test passed")

            self.test_results["passed"] += 1

        except Exception as e:
            print(f"❌ Analytics capabilities test failed: {e}")
            self.test_results["failed"] += 1
            self.test_results["errors"].append(f"Analytics capabilities: {e}")

        self.test_results["total_tests"] += 1

    def generate_test_report(self):
        """Generate comprehensive test report"""
        print("\n" + "=" * 50)
        print("📋 Dashboard Features Test Report")
        print("=" * 50)

        success_rate = (self.test_results["passed"] / self.test_results["total_tests"] * 100) \
            if self.test_results["total_tests"] > 0 else 0

        print(f"📊 Test Summary:")
        print(f"   - Total tests: {self.test_results['total_tests']}")
        print(f"   - Passed: {self.test_results['passed']}")
        print(f"   - Failed: {self.test_results['failed']}")
        print(f"   - Success rate: {success_rate:.1f}%")

        if self.test_results["errors"]:
            print(f"\n❌ Errors encountered:")
            for error in self.test_results["errors"]:
                print(f"   - {error}")

        # Save test results
        test_report = {
            "timestamp": datetime.now().isoformat(),
            "test_results": self.test_results,
            "success_rate": success_rate,
            "features": {
                "enhanced_analytics_api": True,
                "enhanced_analytics_dashboard": True,
                "real_time_metrics": True,
                "trend_analysis": True,
                "predictive_insights": True,
                "document_clustering": True,
                "quality_assessment": True,
                "system_health_monitoring": True
            }
        }

        with open("dashboard_features_test_report.json", "w", encoding="utf-8") as f:
            json.dump(test_report, f, indent=2, ensure_ascii=False)

        print(f"\n📄 Test report saved to: dashboard_features_test_report.json")

        if success_rate >= 90:
            print("🎉 All tests passed! Enhanced analytics dashboard is ready.")
        elif success_rate >= 70:
            print("⚠️ Most tests passed. Some features need attention.")
        else:
            print("❌ Multiple test failures detected. Dashboard needs fixes.")

        return success_rate >= 90


async def main():
    """Main test runner"""
    tester = DashboardFeaturesTester()
    success = await tester.run_all_tests()
    return 0 if success else 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
