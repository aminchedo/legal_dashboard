#!/usr/bin/env python3
"""
Simple Implementation Validation
==============================

Validates the implementation of the Legal Dashboard system by checking:
- File structure and imports
- Service implementations
- Configuration files
- Documentation completeness
"""

import os
import sys
import json
from pathlib import Path
from typing import Dict, List, Any

def validate_file_structure() -> Dict[str, Any]:
    """Validate the file structure and key files exist"""
    results = {
        "status": "PASSED",
        "missing_files": [],
        "required_files": [
            "app/main.py",
            "app/services/scraping_service.py",
            "app/services/rating_service.py",
            "app/services/database_service.py",
            "app/services/ai_service.py",
            "app/api/scraping.py",
            "app/api/dashboard.py",
            "app/api/websocket.py",
            "app.py",
            "requirements.txt",
            "README.md",
            "API.md",
            "DEPLOYMENT.md"
        ]
    }
    
    print("🔍 Checking file structure...")
    
    for file_path in results["required_files"]:
        if not os.path.exists(file_path):
            results["missing_files"].append(file_path)
            print(f"❌ Missing: {file_path}")
        else:
            print(f"✅ Found: {file_path}")
    
    if results["missing_files"]:
        results["status"] = "FAILED"
    
    return results

def validate_main_integration() -> Dict[str, Any]:
    """Validate main.py integration"""
    results = {"status": "PASSED", "issues": []}
    
    print("\n🔧 Checking main.py integration...")
    
    try:
        # Check if main.py exists and can be imported
        main_path = Path("app/main.py")
        if not main_path.exists():
            results["status"] = "FAILED"
            results["issues"].append("main.py not found")
            return results
        
        # Read main.py content
        with open(main_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check for required imports
        required_imports = [
            "ScrapingService",
            "RatingService", 
            "ScrapingStrategy",
            "start_background_scraping",
            "start_background_rating"
        ]
        
        for import_name in required_imports:
            if import_name not in content:
                results["issues"].append(f"Missing import/function: {import_name}")
                print(f"❌ Missing: {import_name}")
            else:
                print(f"✅ Found: {import_name}")
        
        # Check for Persian sources configuration
        if "PERSIAN_LEGAL_SOURCES" not in content:
            results["issues"].append("Missing PERSIAN_LEGAL_SOURCES configuration")
            print("❌ Missing: PERSIAN_LEGAL_SOURCES")
        else:
            print("✅ Found: PERSIAN_LEGAL_SOURCES")
        
        # Check for Persian keywords
        if "PERSIAN_LEGAL_KEYWORDS" not in content:
            results["issues"].append("Missing PERSIAN_LEGAL_KEYWORDS configuration")
            print("❌ Missing: PERSIAN_LEGAL_KEYWORDS")
        else:
            print("✅ Found: PERSIAN_LEGAL_KEYWORDS")
        
        # Check for new API endpoints
        new_endpoints = [
            "/api/system/start-scraping",
            "/api/system/start-rating", 
            "/api/system/status",
            "/api/system/statistics"
        ]
        
        for endpoint in new_endpoints:
            if endpoint not in content:
                results["issues"].append(f"Missing endpoint: {endpoint}")
                print(f"❌ Missing: {endpoint}")
            else:
                print(f"✅ Found: {endpoint}")
        
        if results["issues"]:
            results["status"] = "FAILED"
            
    except Exception as e:
        results["status"] = "FAILED"
        results["issues"].append(f"Error reading main.py: {str(e)}")
    
    return results

def validate_app_py() -> Dict[str, Any]:
    """Validate app.py for HF Spaces compatibility"""
    results = {"status": "PASSED", "issues": []}
    
    print("\n🌐 Checking app.py for HF Spaces...")
    
    try:
        app_path = Path("app.py")
        if not app_path.exists():
            results["status"] = "FAILED"
            results["issues"].append("app.py not found")
            return results
        
        with open(app_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check for HF Spaces specific configurations
        hf_requirements = [
            "'PORT': '7860'",
            "TRANSFORMERS_CACHE",
            "HF_HOME",
            "'ENVIRONMENT': 'production'",
            "uvicorn.run"
        ]
        
        for req in hf_requirements:
            if req not in content:
                results["issues"].append(f"Missing HF requirement: {req}")
                print(f"❌ Missing: {req}")
            else:
                print(f"✅ Found: {req}")
        
        if results["issues"]:
            results["status"] = "FAILED"
            
    except Exception as e:
        results["status"] = "FAILED"
        results["issues"].append(f"Error reading app.py: {str(e)}")
    
    return results

def validate_requirements() -> Dict[str, Any]:
    """Validate requirements.txt completeness"""
    results = {"status": "PASSED", "issues": []}
    
    print("\n📦 Checking requirements.txt...")
    
    try:
        req_path = Path("requirements.txt")
        if not req_path.exists():
            results["status"] = "FAILED"
            results["issues"].append("requirements.txt not found")
            return results
        
        with open(req_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check for essential dependencies
        essential_deps = [
            "fastapi",
            "uvicorn",
            "aiohttp",
            "beautifulsoup4",
            "sqlalchemy",
            "redis",
            "transformers",
            "torch",
            "numpy",
            "pandas",
            "hazm",
            "websockets"
        ]
        
        for dep in essential_deps:
            if dep not in content:
                results["issues"].append(f"Missing dependency: {dep}")
                print(f"❌ Missing: {dep}")
            else:
                print(f"✅ Found: {dep}")
        
        if results["issues"]:
            results["status"] = "FAILED"
            
    except Exception as e:
        results["status"] = "FAILED"
        results["issues"].append(f"Error reading requirements.txt: {str(e)}")
    
    return results

def validate_documentation() -> Dict[str, Any]:
    """Validate documentation completeness"""
    results = {"status": "PASSED", "issues": []}
    
    print("\n📚 Checking documentation...")
    
    # Check README.md
    readme_path = Path("README.md")
    if readme_path.exists():
        with open(readme_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check for Persian content
        if "داشبورد حقوقی" in content:
            print("✅ README.md contains Persian content")
        else:
            results["issues"].append("README.md missing Persian content")
            print("❌ README.md missing Persian content")
        
        # Check for key sections
        key_sections = [
            "معماری سیستم",
            "راه‌اندازی سریع",
            "API Documentation",
            "منابع حقوقی ایرانی"
        ]
        
        for section in key_sections:
            if section in content:
                print(f"✅ Found section: {section}")
            else:
                results["issues"].append(f"Missing section: {section}")
                print(f"❌ Missing section: {section}")
    else:
        results["issues"].append("README.md not found")
        print("❌ README.md not found")
    
    # Check API.md
    api_path = Path("API.md")
    if api_path.exists():
        print("✅ API.md exists")
    else:
        results["issues"].append("API.md not found")
        print("❌ API.md not found")
    
    # Check DEPLOYMENT.md
    deploy_path = Path("DEPLOYMENT.md")
    if deploy_path.exists():
        print("✅ DEPLOYMENT.md exists")
    else:
        results["issues"].append("DEPLOYMENT.md not found")
        print("❌ DEPLOYMENT.md not found")
    
    if results["issues"]:
        results["status"] = "FAILED"
    
    return results

def validate_rating_service() -> Dict[str, Any]:
    """Validate rating service implementation"""
    results = {"status": "PASSED", "issues": []}
    
    print("\n⭐ Checking rating service...")
    
    try:
        rating_path = Path("app/services/rating_service.py")
        if not rating_path.exists():
            results["status"] = "FAILED"
            results["issues"].append("rating_service.py not found")
            return results
        
        with open(rating_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check for required methods
        required_methods = [
            "get_unrated_items",
            "rate_item",
            "get_rating_summary",
            "_evaluate_source_credibility",
            "_evaluate_content_completeness"
        ]
        
        for method in required_methods:
            if method not in content:
                results["issues"].append(f"Missing method: {method}")
                print(f"❌ Missing: {method}")
            else:
                print(f"✅ Found: {method}")
        
        # Check for Persian legal terms
        if "قانون" in content or "حقوق" in content:
            print("✅ Contains Persian legal terms")
        else:
            results["issues"].append("Missing Persian legal terms")
            print("❌ Missing Persian legal terms")
        
        if results["issues"]:
            results["status"] = "FAILED"
            
    except Exception as e:
        results["status"] = "FAILED"
        results["issues"].append(f"Error reading rating service: {str(e)}")
    
    return results

def generate_summary_report(all_results: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
    """Generate summary report"""
    total_checks = len(all_results)
    passed_checks = sum(1 for result in all_results.values() if result["status"] == "PASSED")
    failed_checks = total_checks - passed_checks
    
    summary = {
        "total_checks": total_checks,
        "passed_checks": passed_checks,
        "failed_checks": failed_checks,
        "success_rate": (passed_checks / total_checks) * 100 if total_checks > 0 else 0,
        "overall_status": "PASSED" if failed_checks == 0 else "FAILED",
        "detailed_results": all_results
    }
    
    print(f"\n📊 Validation Summary:")
    print(f"Total Checks: {total_checks}")
    print(f"Passed: {passed_checks}")
    print(f"Failed: {failed_checks}")
    print(f"Success Rate: {summary['success_rate']:.1f}%")
    print(f"Overall Status: {summary['overall_status']}")
    
    if failed_checks > 0:
        print(f"\n❌ Failed Checks:")
        for check_name, result in all_results.items():
            if result["status"] == "FAILED":
                print(f"  - {check_name}: {', '.join(result.get('issues', []))}")
    
    return summary

def main():
    """Main validation function"""
    print("🏛️ Legal Dashboard Implementation Validation")
    print("=" * 50)
    
    # Run all validations
    results = {
        "file_structure": validate_file_structure(),
        "main_integration": validate_main_integration(),
        "app_py": validate_app_py(),
        "requirements": validate_requirements(),
        "documentation": validate_documentation(),
        "rating_service": validate_rating_service()
    }
    
    # Generate summary
    summary = generate_summary_report(results)
    
    # Save results
    with open("validation_report.json", "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)
    
    print(f"\n📄 Results saved to: validation_report.json")
    
    # Exit with appropriate code
    if summary["overall_status"] == "PASSED":
        print("✅ Implementation validation completed successfully!")
        sys.exit(0)
    else:
        print("❌ Implementation validation failed!")
        sys.exit(1)

if __name__ == "__main__":
    main()
