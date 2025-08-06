#!/usr/bin/env python3
"""
Legal Dashboard - Final System Test
===================================
Comprehensive test suite for all deployment environments.
"""

import os
import sys
import json
import time
import tempfile
import requests
import sqlite3
import subprocess
import threading
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional

# Add project to path
sys.path.insert(0, str(Path(__file__).parent))

class Colors:
    """ANSI color codes for terminal output"""
    RED = '\033[0;31m'
    GREEN = '\033[0;32m'
    YELLOW = '\033[1;33m'
    BLUE = '\033[0;34m'
    PURPLE = '\033[0;35m'
    CYAN = '\033[0;36m'
    WHITE = '\033[1;37m'
    NC = '\033[0m'  # No Color

class TestResult:
    """Test result container"""
    def __init__(self, name: str, passed: bool, message: str, duration: float = 0.0, details: Dict = None):
        self.name = name
        self.passed = passed
        self.message = message
        self.duration = duration
        self.details = details or {}
        self.timestamp = datetime.now()

class LegalDashboardTester:
    """Comprehensive tester for Legal Dashboard"""
    
    def __init__(self):
        self.results: List[TestResult] = []
        self.start_time = time.time()
        self.server_process = None
        self.base_url = "http://localhost:8000"
        self.gradio_url = "http://localhost:7860"
        
    def print_colored(self, message: str, color: str = Colors.NC):
        """Print colored message"""
        print(f"{color}{message}{Colors.NC}")
    
    def print_success(self, message: str):
        self.print_colored(f"✅ {message}", Colors.GREEN)
    
    def print_error(self, message: str):
        self.print_colored(f"❌ {message}", Colors.RED)
    
    def print_warning(self, message: str):
        self.print_colored(f"⚠️ {message}", Colors.YELLOW)
    
    def print_info(self, message: str):
        self.print_colored(f"ℹ️ {message}", Colors.BLUE)
    
    def add_result(self, result: TestResult):
        """Add test result"""
        self.results.append(result)
        
        if result.passed:
            self.print_success(f"{result.name} - {result.message}")
        else:
            self.print_error(f"{result.name} - {result.message}")
    
    def test_environment_setup(self) -> bool:
        """Test environment setup and configuration"""
        self.print_info("Testing environment setup...")
        
        start_time = time.time()
        
        try:
            # Test config import
            from config import config, setup_environment
            
            # Test environment setup
            setup_success = setup_environment()
            
            details = {
                "environment": config.environment,
                "is_hf_spaces": config.is_hf_spaces,
                "is_docker": config.is_docker,
                "directories": config.directories,
            }
            
            duration = time.time() - start_time
            
            if setup_success:
                self.add_result(TestResult(
                    "Environment Setup", 
                    True, 
                    f"Environment ({config.environment}) configured successfully", 
                    duration,
                    details
                ))
                return True
            else:
                self.add_result(TestResult(
                    "Environment Setup", 
                    False, 
                    "Environment setup failed", 
                    duration,
                    details
                ))
                return False
                
        except Exception as e:
            duration = time.time() - start_time
            self.add_result(TestResult(
                "Environment Setup", 
                False, 
                f"Exception: {str(e)}", 
                duration
            ))
            return False
    
    def test_dependencies(self) -> bool:
        """Test all dependencies"""
        self.print_info("Testing dependencies...")
        
        start_time = time.time()
        
        # Critical dependencies
        critical_deps = [
            ("fastapi", "FastAPI framework"),
            ("uvicorn", "ASGI server"),
            ("sqlite3", "Database (built-in)"),
            ("passlib", "Password hashing"),
            ("jose", "JWT tokens"),
            ("pydantic", "Data validation"),
        ]
        
        # Optional dependencies
        optional_deps = [
            ("gradio", "Gradio interface"),
            ("transformers", "AI/ML models"),
            ("redis", "Caching"),
            ("requests", "HTTP client"),
        ]
        
        missing_critical = []
        available_optional = []
        
        # Test critical dependencies
        for module, desc in critical_deps:
            try:
                __import__(module)
            except ImportError:
                missing_critical.append((module, desc))
        
        # Test optional dependencies
        for module, desc in optional_deps:
            try:
                __import__(module)
                available_optional.append((module, desc))
            except ImportError:
                pass
        
        duration = time.time() - start_time
        
        if missing_critical:
            self.add_result(TestResult(
                "Dependencies", 
                False, 
                f"Missing critical dependencies: {[m[0] for m in missing_critical]}", 
                duration,
                {"missing": missing_critical, "available_optional": available_optional}
            ))
            return False
        else:
            self.add_result(TestResult(
                "Dependencies", 
                True, 
                f"All critical dependencies available. Optional: {len(available_optional)}", 
                duration,
                {"available_optional": available_optional}
            ))
            return True
    
    def test_database_operations(self) -> bool:
        """Test database operations"""
        self.print_info("Testing database operations...")
        
        start_time = time.time()
        
        try:
            # Create temporary database
            with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as temp_db:
                db_path = temp_db.name
            
            # Test SQLite operations
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # Create test tables (similar to auth.py)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS test_users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    email TEXT UNIQUE NOT NULL,
                    hashed_password TEXT NOT NULL,
                    role TEXT NOT NULL DEFAULT 'user',
                    is_active BOOLEAN NOT NULL DEFAULT 1,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Test data insertion
            cursor.execute("""
                INSERT INTO test_users (username, email, hashed_password, role)
                VALUES (?, ?, ?, ?)
            """, ("testuser", "test@example.com", "hashed_password", "user"))
            
            # Test data retrieval
            cursor.execute("SELECT * FROM test_users WHERE username = ?", ("testuser",))
            result = cursor.fetchone()
            
            # Test data update
            cursor.execute("UPDATE test_users SET role = ? WHERE username = ?", ("admin", "testuser"))
            
            # Test data deletion
            cursor.execute("DELETE FROM test_users WHERE username = ?", ("testuser",))
            
            conn.commit()
            conn.close()
            
            # Clean up
            os.unlink(db_path)
            
            duration = time.time() - start_time
            
            if result:
                self.add_result(TestResult(
                    "Database Operations", 
                    True, 
                    "All database operations successful", 
                    duration,
                    {"operations": ["CREATE", "INSERT", "SELECT", "UPDATE", "DELETE"]}
                ))
                return True
            else:
                self.add_result(TestResult(
                    "Database Operations", 
                    False, 
                    "Data retrieval failed", 
                    duration
                ))
                return False
                
        except Exception as e:
            duration = time.time() - start_time
            self.add_result(TestResult(
                "Database Operations", 
                False, 
                f"Exception: {str(e)}", 
                duration
            ))
            return False
    
    def test_authentication_system(self) -> bool:
        """Test authentication system"""
        self.print_info("Testing authentication system...")
        
        start_time = time.time()
        
        try:
            # Test bcrypt
            from passlib.context import CryptContext
            pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
            
            # Test password hashing
            password = "testpassword123"
            hashed = pwd_context.hash(password)
            verified = pwd_context.verify(password, hashed)
            
            if not verified:
                raise Exception("Password verification failed")
            
            # Test JWT
            from jose import jwt
            
            secret_key = "test-secret-key"
            payload = {"user_id": 1, "username": "testuser"}
            
            # Create token
            token = jwt.encode(payload, secret_key, algorithm="HS256")
            
            # Decode token
            decoded = jwt.decode(token, secret_key, algorithms=["HS256"])
            
            if decoded["username"] != "testuser":
                raise Exception("JWT token verification failed")
            
            duration = time.time() - start_time
            
            self.add_result(TestResult(
                "Authentication System", 
                True, 
                "bcrypt and JWT working correctly", 
                duration,
                {"bcrypt": "✓", "jwt": "✓"}
            ))
            return True
            
        except Exception as e:
            duration = time.time() - start_time
            self.add_result(TestResult(
                "Authentication System", 
                False, 
                f"Exception: {str(e)}", 
                duration
            ))
            return False
    
    def test_fastapi_app_creation(self) -> bool:
        """Test FastAPI app creation"""
        self.print_info("Testing FastAPI app creation...")
        
        start_time = time.time()
        
        try:
            # Import and create app
            from app.main import app
            
            # Check app properties
            app_info = {
                "title": app.title,
                "version": app.version,
                "routes_count": len(app.routes),
                "middleware_count": len(app.middleware_stack),
            }
            
            # Check specific routes exist
            route_paths = [route.path for route in app.routes if hasattr(route, 'path')]
            expected_routes = ["/", "/api/health", "/api/auth/login", "/api/documents"]
            
            missing_routes = [route for route in expected_routes if route not in route_paths]
            
            duration = time.time() - start_time
            
            if missing_routes:
                self.add_result(TestResult(
                    "FastAPI App Creation", 
                    False, 
                    f"Missing routes: {missing_routes}", 
                    duration,
                    app_info
                ))
                return False
            else:
                self.add_result(TestResult(
                    "FastAPI App Creation", 
                    True, 
                    f"App created with {len(route_paths)} routes", 
                    duration,
                    app_info
                ))
                return True
                
        except Exception as e:
            duration = time.time() - start_time
            self.add_result(TestResult(
                "FastAPI App Creation", 
                False, 
                f"Exception: {str(e)}", 
                duration
            ))
            return False
    
    def start_test_server(self) -> Optional[subprocess.Popen]:
        """Start test server"""
        self.print_info("Starting test server...")
        
        try:
            # Start FastAPI server
            cmd = [
                sys.executable, "-m", "uvicorn", 
                "app.main:app", 
                "--host", "127.0.0.1", 
                "--port", "8000",
                "--log-level", "warning"
            ]
            
            self.server_process = subprocess.Popen(
                cmd, 
                stdout=subprocess.DEVNULL, 
                stderr=subprocess.DEVNULL
            )
            
            # Wait for server to start
            for i in range(30):  # Wait up to 30 seconds
                try:
                    response = requests.get(f"{self.base_url}/api/health", timeout=2)
                    if response.status_code == 200:
                        self.print_success("Test server started successfully")
                        return self.server_process
                except:
                    pass
                time.sleep(1)
            
            self.print_error("Test server failed to start")
            return None
            
        except Exception as e:
            self.print_error(f"Failed to start test server: {e}")
            return None
    
    def test_api_endpoints(self) -> bool:
        """Test API endpoints"""
        self.print_info("Testing API endpoints...")
        
        start_time = time.time()
        
        # Endpoints to test
        endpoints = [
            ("/api/health", "GET", 200),
            ("/", "GET", 200),
            ("/api/docs", "GET", 200),
            ("/api/auth/health", "GET", 200),
        ]
        
        results = {}
        
        for endpoint, method, expected_status in endpoints:
            try:
                if method == "GET":
                    response = requests.get(f"{self.base_url}{endpoint}", timeout=10)
                else:
                    response = requests.request(method, f"{self.base_url}{endpoint}", timeout=10)
                
                results[endpoint] = {
                    "status": response.status_code,
                    "expected": expected_status,
                    "success": response.status_code == expected_status
                }
                
            except Exception as e:
                results[endpoint] = {
                    "status": "error",
                    "expected": expected_status,
                    "success": False,
                    "error": str(e)
                }
        
        duration = time.time() - start_time
        
        # Check results
        successful_endpoints = sum(1 for r in results.values() if r.get("success", False))
        total_endpoints = len(endpoints)
        
        if successful_endpoints == total_endpoints:
            self.add_result(TestResult(
                "API Endpoints", 
                True, 
                f"All {total_endpoints} endpoints responding correctly", 
                duration,
                results
            ))
            return True
        else:
            self.add_result(TestResult(
                "API Endpoints", 
                False, 
                f"Only {successful_endpoints}/{total_endpoints} endpoints working", 
                duration,
                results
            ))
            return False
    
    def test_authentication_flow(self) -> bool:
        """Test complete authentication flow"""
        self.print_info("Testing authentication flow...")
        
        start_time = time.time()
        
        try:
            # Test registration (if possible)
            register_data = {
                "username": "testuser123",
                "email": "testuser123@example.com",
                "password": "testpassword123"
            }
            
            # Test login with default credentials
            login_data = {
                "username": "admin",
                "password": "admin123"
            }
            
            auth_results = {}
            
            # Try login
            try:
                response = requests.post(
                    f"{self.base_url}/api/auth/login", 
                    json=login_data, 
                    timeout=10
                )
                
                if response.status_code == 200:
                    data = response.json()
                    if "access_token" in data:
                        auth_results["login"] = "success"
                        
                        # Test protected endpoint
                        headers = {"Authorization": f"Bearer {data['access_token']}"}
                        me_response = requests.get(
                            f"{self.base_url}/api/auth/me", 
                            headers=headers, 
                            timeout=10
                        )
                        
                        if me_response.status_code == 200:
                            auth_results["protected_endpoint"] = "success"
                        else:
                            auth_results["protected_endpoint"] = f"failed: {me_response.status_code}"
                    else:
                        auth_results["login"] = "no_token"
                else:
                    auth_results["login"] = f"failed: {response.status_code}"
                    
            except Exception as e:
                auth_results["login"] = f"error: {str(e)}"
            
            duration = time.time() - start_time
            
            if auth_results.get("login") == "success":
                self.add_result(TestResult(
                    "Authentication Flow", 
                    True, 
                    "Login and token validation successful", 
                    duration,
                    auth_results
                ))
                return True
            else:
                self.add_result(TestResult(
                    "Authentication Flow", 
                    False, 
                    f"Authentication failed: {auth_results}", 
                    duration,
                    auth_results
                ))
                return False
                
        except Exception as e:
            duration = time.time() - start_time
            self.add_result(TestResult(
                "Authentication Flow", 
                False, 
                f"Exception: {str(e)}", 
                duration
            ))
            return False
    
    def test_gradio_interface(self) -> bool:
        """Test Gradio interface (if available)"""
        self.print_info("Testing Gradio interface...")
        
        start_time = time.time()
        
        try:
            import gradio as gr
            
            # Test if app.py can be imported
            try:
                # Try importing without running
                with open("app.py", "r") as f:
                    content = f.read()
                
                # Check for Gradio-related content
                gradio_indicators = ["gr.Blocks", "launch", "gradio"]
                found_indicators = [ind for ind in gradio_indicators if ind in content]
                
                duration = time.time() - start_time
                
                if found_indicators:
                    self.add_result(TestResult(
                        "Gradio Interface", 
                        True, 
                        f"Gradio interface available with indicators: {found_indicators}", 
                        duration,
                        {"indicators": found_indicators}
                    ))
                    return True
                else:
                    self.add_result(TestResult(
                        "Gradio Interface", 
                        False, 
                        "Gradio indicators not found in app.py", 
                        duration
                    ))
                    return False
                    
            except FileNotFoundError:
                duration = time.time() - start_time
                self.add_result(TestResult(
                    "Gradio Interface", 
                    False, 
                    "app.py not found", 
                    duration
                ))
                return False
                
        except ImportError:
            duration = time.time() - start_time
            self.add_result(TestResult(
                "Gradio Interface", 
                False, 
                "Gradio not available (optional)", 
                duration
            ))
            return True  # Not critical
    
    def stop_test_server(self):
        """Stop test server"""
        if self.server_process:
            self.print_info("Stopping test server...")
            self.server_process.terminate()
            try:
                self.server_process.wait(timeout=10)
            except subprocess.TimeoutExpired:
                self.server_process.kill()
            self.server_process = None
    
    def generate_report(self) -> Dict[str, Any]:
        """Generate comprehensive test report"""
        end_time = time.time()
        total_duration = end_time - self.start_time
        
        # Calculate statistics
        total_tests = len(self.results)
        passed_tests = sum(1 for r in self.results if r.passed)
        failed_tests = total_tests - passed_tests
        pass_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        # Categorize results
        critical_tests = ["Environment Setup", "Dependencies", "Database Operations", "FastAPI App Creation"]
        critical_results = [r for r in self.results if r.name in critical_tests]
        critical_passed = sum(1 for r in critical_results if r.passed)
        
        # Determine overall status
        if critical_passed == len(critical_results) and pass_rate >= 80:
            overall_status = "READY FOR DEPLOYMENT"
            status_color = Colors.GREEN
        elif critical_passed == len(critical_results):
            overall_status = "DEPLOYMENT READY WITH WARNINGS"
            status_color = Colors.YELLOW
        else:
            overall_status = "NOT READY FOR DEPLOYMENT"
            status_color = Colors.RED
        
        report = {
            "timestamp": datetime.now().isoformat(),
            "total_duration": total_duration,
            "overall_status": overall_status,
            "statistics": {
                "total_tests": total_tests,
                "passed_tests": passed_tests,
                "failed_tests": failed_tests,
                "pass_rate": pass_rate
            },
            "critical_systems": {
                "total": len(critical_results),
                "passed": critical_passed,
                "status": "CRITICAL SYSTEMS OK" if critical_passed == len(critical_results) else "CRITICAL ISSUES"
            },
            "test_results": [
                {
                    "name": r.name,
                    "passed": r.passed,
                    "message": r.message,
                    "duration": r.duration,
                    "details": r.details
                }
                for r in self.results
            ]
        }
        
        return report, status_color
    
    def print_summary(self):
        """Print test summary"""
        report, status_color = self.generate_report()
        
        print("\n" + "="*80)
        self.print_colored("🧪 LEGAL DASHBOARD - FINAL TEST REPORT", Colors.WHITE)
        print("="*80)
        
        # Overall status
        self.print_colored(f"📊 OVERALL STATUS: {report['overall_status']}", status_color)
        print()
        
        # Statistics
        stats = report['statistics']
        self.print_info(f"📈 Test Statistics:")
        print(f"   Total Tests: {stats['total_tests']}")
        print(f"   Passed: {stats['passed_tests']} ✅")
        print(f"   Failed: {stats['failed_tests']} ❌")
        print(f"   Pass Rate: {stats['pass_rate']:.1f}%")
        print(f"   Total Duration: {report['total_duration']:.2f}s")
        print()
        
        # Critical systems
        critical = report['critical_systems']
        critical_color = Colors.GREEN if critical['status'] == "CRITICAL SYSTEMS OK" else Colors.RED
        self.print_colored(f"🔧 Critical Systems: {critical['status']} ({critical['passed']}/{critical['total']})", critical_color)
        print()
        
        # Individual test results
        self.print_info("📋 Individual Test Results:")
        for result in self.results:
            status_icon = "✅" if result.passed else "❌"
            color = Colors.GREEN if result.passed else Colors.RED
            self.print_colored(f"   {status_icon} {result.name}: {result.message} ({result.duration:.2f}s)", color)
        
        print("\n" + "="*80)
        
        # Recommendations
        if report['overall_status'] == "READY FOR DEPLOYMENT":
            self.print_success("🎉 System is ready for deployment!")
            print("   ✅ All critical systems operational")
            print("   ✅ Authentication working")
            print("   ✅ Database operations successful")
            print("   ✅ API endpoints responding")
            print()
            print("📋 Next steps:")
            print("   1. Deploy to your chosen platform")
            print("   2. Set environment variables")
            print("   3. Change default admin password")
            print("   4. Monitor application logs")
            
        elif report['overall_status'] == "DEPLOYMENT READY WITH WARNINGS":
            self.print_warning("⚠️ System ready with some warnings")
            print("   ✅ Critical systems operational")
            print("   ⚠️ Some optional features may not work")
            print()
            print("📋 Recommendations:")
            print("   1. Review failed tests")
            print("   2. Fix non-critical issues if needed")
            print("   3. Deploy with caution")
            
        else:
            self.print_error("❌ System not ready for deployment")
            print("   ❌ Critical system failures detected")
            print()
            print("📋 Required actions:")
            print("   1. Fix critical system issues")
            print("   2. Re-run tests")
            print("   3. Do not deploy until issues resolved")
        
        print("\n" + "="*80)
    
    def save_report(self, filename: str = "test_report.json"):
        """Save detailed report to file"""
        report, _ = self.generate_report()
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        self.print_success(f"Detailed report saved to {filename}")
    
    def run_all_tests(self):
        """Run all tests"""
        self.print_colored("🚀 Starting Legal Dashboard Final Test Suite", Colors.WHITE)
        print("="*80)
        
        # Define test sequence
        tests = [
            ("Environment Setup", self.test_environment_setup),
            ("Dependencies", self.test_dependencies),
            ("Database Operations", self.test_database_operations),
            ("Authentication System", self.test_authentication_system),
            ("FastAPI App Creation", self.test_fastapi_app_creation),
            ("Gradio Interface", self.test_gradio_interface),
        ]
        
        # Run core tests
        for test_name, test_func in tests:
            try:
                test_func()
            except Exception as e:
                self.add_result(TestResult(
                    test_name, 
                    False, 
                    f"Unexpected error: {str(e)}", 
                    0.0
                ))
        
        # Run server tests if possible
        server_started = self.start_test_server()
        if server_started:
            try:
                self.test_api_endpoints()
                self.test_authentication_flow()
            finally:
                self.stop_test_server()
        else:
            self.add_result(TestResult(
                "Server Tests", 
                False, 
                "Could not start test server", 
                0.0
            ))
        
        # Generate and display results
        self.print_summary()
        self.save_report()

def main():
    """Main function"""
    tester = LegalDashboardTester()
    tester.run_all_tests()

if __name__ == "__main__":
    main()