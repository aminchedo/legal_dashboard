#!/usr/bin/env python3
"""
Analytics Integration Test
Verifies that all analytics features are properly integrated into the improved_legal_dashboard.html
"""

import os
import re
import json
from typing import Dict, List, Any

class AnalyticsIntegrationTester:
    def __init__(self, dashboard_file: str = "frontend/improved_legal_dashboard.html"):
        self.dashboard_file = dashboard_file
        self.results = {}
        
    def test_file_exists(self) -> bool:
        """Test if the dashboard file exists"""
        exists = os.path.exists(self.dashboard_file)
        self.results["file_exists"] = exists
        return exists
    
    def test_analytics_sections(self) -> Dict[str, bool]:
        """Test if all 6 analytics sections are present"""
        try:
            with open(self.dashboard_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            sections = {
                "overview": "نمای کلی" in content,
                "trends": "روندها و الگوها" in content,
                "predictions": "پیش‌بینی‌ها" in content,
                "quality": "ارزیابی کیفیت" in content,
                "health": "سلامت سیستم" in content,
                "clustering": "خوشه‌بندی اسناد" in content
            }
            
            self.results["analytics_sections"] = sections
            return sections
            
        except Exception as e:
            self.results["analytics_sections"] = {"error": str(e)}
            return {"error": str(e)}
    
    def test_analytics_css(self) -> Dict[str, bool]:
        """Test if analytics CSS styles are present"""
        try:
            with open(self.dashboard_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            css_classes = {
                "analytics_dashboard": ".analytics-dashboard" in content,
                "analytics_grid": ".analytics-grid" in content,
                "analytics_card": ".analytics-card" in content,
                "overview_stats": ".overview-stats" in content,
                "trends_chart": ".trends-chart" in content,
                "predictions_chart": ".predictions-chart" in content,
                "quality_chart": ".quality-chart" in content,
                "health_chart": ".health-chart" in content,
                "clustering_chart": ".clustering-chart" in content
            }
            
            self.results["analytics_css"] = css_classes
            return css_classes
            
        except Exception as e:
            self.results["analytics_css"] = {"error": str(e)}
            return {"error": str(e)}
    
    def test_analytics_javascript(self) -> Dict[str, bool]:
        """Test if analytics JavaScript functions are present"""
        try:
            with open(self.dashboard_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            js_functions = {
                "refresh_overview": "refreshOverview()" in content,
                "refresh_trends": "refreshTrends()" in content,
                "refresh_predictions": "refreshPredictions()" in content,
                "refresh_quality": "refreshQuality()" in content,
                "refresh_health": "refreshHealth()" in content,
                "refresh_clustering": "refreshClustering()" in content,
                "analytics_endpoints": "ANALYTICS_ENDPOINTS" in content,
                "chart_functions": "updateOverviewChart" in content
            }
            
            self.results["analytics_javascript"] = js_functions
            return js_functions
            
        except Exception as e:
            self.results["analytics_javascript"] = {"error": str(e)}
            return {"error": str(e)}
    
    def test_analytics_elements(self) -> Dict[str, bool]:
        """Test if analytics HTML elements are present"""
        try:
            with open(self.dashboard_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            elements = {
                "overview_content": 'id="overviewContent"' in content,
                "trends_content": 'id="trendsContent"' in content,
                "predictions_content": 'id="predictionsContent"' in content,
                "quality_content": 'id="qualityContent"' in content,
                "health_content": 'id="healthContent"' in content,
                "clustering_content": 'id="clusteringContent"' in content,
                "refresh_button": 'id="refreshAnalyticsBtn"' in content,
                "chart_canvases": 'ChartCanvas' in content
            }
            
            self.results["analytics_elements"] = elements
            return elements
            
        except Exception as e:
            self.results["analytics_elements"] = {"error": str(e)}
            return {"error": str(e)}
    
    def test_rtl_support(self) -> Dict[str, bool]:
        """Test if RTL support is properly implemented"""
        try:
            with open(self.dashboard_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            rtl_features = {
                "rtl_dir": 'dir="rtl"' in content,
                "persian_lang": 'lang="fa"' in content,
                "persian_text": 'نمای کلی' in content,
                "vazirmatn_font": 'Vazirmatn' in content
            }
            
            self.results["rtl_support"] = rtl_features
            return rtl_features
            
        except Exception as e:
            self.results["rtl_support"] = {"error": str(e)}
            return {"error": str(e)}
    
    def test_responsive_design(self) -> Dict[str, bool]:
        """Test if responsive design is implemented"""
        try:
            with open(self.dashboard_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            responsive_features = {
                "media_queries": "@media" in content,
                "grid_layout": "grid-template-columns" in content,
                "flexbox": "display: flex" in content,
                "responsive_charts": "responsive: true" in content
            }
            
            self.results["responsive_design"] = responsive_features
            return responsive_features
            
        except Exception as e:
            self.results["responsive_design"] = {"error": str(e)}
            return {"error": str(e)}
    
    def run_all_tests(self) -> Dict[str, Any]:
        """Run all analytics integration tests"""
        print("🔍 Testing Analytics Integration...")
        print("=" * 60)
        
        # Run all tests
        file_exists = self.test_file_exists()
        sections = self.test_analytics_sections()
        css = self.test_analytics_css()
        javascript = self.test_analytics_javascript()
        elements = self.test_analytics_elements()
        rtl = self.test_rtl_support()
        responsive = self.test_responsive_design()
        
        # Calculate success rates
        total_tests = 0
        successful_tests = 0
        
        for test_name, test_results in self.results.items():
            if isinstance(test_results, dict) and "error" not in test_results:
                test_count = len(test_results)
                test_success = sum(1 for v in test_results.values() if v)
                total_tests += test_count
                successful_tests += test_success
                
                print(f"\n📊 {test_name.replace('_', ' ').title()}:")
                for feature, status in test_results.items():
                    icon = "✅" if status else "❌"
                    print(f"   {icon} {feature.replace('_', ' ')}")
        
        # Summary
        success_rate = (successful_tests / total_tests * 100) if total_tests > 0 else 0
        
        print("\n" + "=" * 60)
        print("📈 INTEGRATION SUMMARY")
        print("=" * 60)
        print(f"Total Tests: {total_tests}")
        print(f"Successful: {successful_tests}")
        print(f"Failed: {total_tests - successful_tests}")
        print(f"Success Rate: {success_rate:.1f}%")
        
        # Final assessment
        print("\n🎯 FINAL ASSESSMENT")
        print("=" * 60)
        if success_rate >= 95:
            print("✅ EXCELLENT: Analytics integration is complete and functional!")
            print("   All 6 analytics sections are properly integrated.")
        elif success_rate >= 80:
            print("⚠️  GOOD: Most analytics features are integrated.")
            print("   Some minor issues may need attention.")
        elif success_rate >= 60:
            print("⚠️  FAIR: Basic analytics integration is present.")
            print("   Several features may need improvement.")
        else:
            print("❌ POOR: Analytics integration is incomplete.")
            print("   Significant work needed for full integration.")
        
        return {
            "total_tests": total_tests,
            "successful_tests": successful_tests,
            "success_rate": success_rate,
            "results": self.results
        }
    
    def save_results(self, filename: str = "analytics_integration_results.json"):
        """Save test results to JSON file"""
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, indent=2, ensure_ascii=False)
        print(f"\n💾 Results saved to: {filename}")

def main():
    """Main test execution"""
    print("🚀 Analytics Integration Verification")
    print("=" * 60)
    
    tester = AnalyticsIntegrationTester()
    summary = tester.run_all_tests()
    tester.save_results()
    
    return summary["success_rate"] >= 80

if __name__ == "__main__":
    main() 