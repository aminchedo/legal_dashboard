#!/usr/bin/env python3
"""
Legal Dashboard Universal Runner
================================
Universal runner script for all environments: HF Spaces, Docker, Local
"""

import sys
import os
import logging
import warnings
import signal
import time
from pathlib import Path

# Add current directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

# Suppress warnings early
warnings.filterwarnings("ignore", message=".*trapped.*error reading bcrypt version.*")
warnings.filterwarnings("ignore", message=".*TRANSFORMERS_CACHE.*deprecated.*")
warnings.filterwarnings("ignore", category=FutureWarning, module="transformers")

# Import configuration
try:
    from config import setup_environment, config
except ImportError:
    print("❌ Configuration module not found. Please ensure config.py is present.")
    sys.exit(1)

class LegalDashboardRunner:
    """Universal runner for Legal Dashboard"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.app_process = None
        self.setup_signal_handlers()
    
    def setup_signal_handlers(self):
        """Setup signal handlers for graceful shutdown"""
        def signal_handler(signum, frame):
            self.logger.info(f"🛑 Received signal {signum}, shutting down...")
            self.shutdown()
            sys.exit(0)
        
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
    
    def check_dependencies(self) -> bool:
        """Check if all required dependencies are available"""
        required_modules = [
            ("fastapi", "FastAPI framework"),
            ("uvicorn", "ASGI server"),
            ("sqlite3", "Database (built-in)"),
            ("passlib", "Password hashing"),
            ("jose", "JWT tokens"),
        ]
        
        optional_modules = [
            ("gradio", "Gradio interface (for HF Spaces)"),
            ("transformers", "AI/ML models"),
            ("redis", "Caching"),
        ]
        
        missing_required = []
        missing_optional = []
        
        # Check required modules
        for module, description in required_modules:
            try:
                __import__(module)
                self.logger.info(f"✅ {description}")
            except ImportError:
                missing_required.append((module, description))
                self.logger.error(f"❌ {description} - Missing: {module}")
        
        # Check optional modules
        for module, description in optional_modules:
            try:
                __import__(module)
                self.logger.info(f"✅ {description}")
            except ImportError:
                missing_optional.append((module, description))
                self.logger.warning(f"⚠️ {description} - Optional: {module}")
        
        if missing_required:
            self.logger.error("❌ Missing required dependencies:")
            for module, desc in missing_required:
                self.logger.error(f"  pip install {module}")
            return False
        
        if missing_optional and config.is_hf_spaces:
            # Check if gradio is available for HF Spaces
            if any(module == "gradio" for module, _ in missing_optional):
                self.logger.error("❌ Gradio is required for HF Spaces deployment")
                return False
        
        return True
    
    def test_database_connection(self) -> bool:
        """Test database connectivity"""
        try:
            import sqlite3
            import tempfile
            
            # Test with temporary database
            test_db = os.path.join(tempfile.gettempdir(), "test_legal_dashboard.db")
            
            conn = sqlite3.connect(test_db)
            cursor = conn.cursor()
            cursor.execute("CREATE TABLE IF NOT EXISTS test (id INTEGER PRIMARY KEY)")
            cursor.execute("INSERT INTO test (id) VALUES (1)")
            cursor.execute("SELECT * FROM test")
            result = cursor.fetchone()
            conn.close()
            
            # Clean up
            if os.path.exists(test_db):
                os.remove(test_db)
            
            if result:
                self.logger.info("✅ Database connectivity test passed")
                return True
            else:
                self.logger.error("❌ Database test failed - no data returned")
                return False
                
        except Exception as e:
            self.logger.error(f"❌ Database connectivity test failed: {e}")
            return False
    
    def run_gradio_interface(self):
        """Run Gradio interface for HF Spaces"""
        try:
            self.logger.info("🤗 Starting Gradio interface for HF Spaces...")
            
            # Import and run Gradio app
            if os.path.exists("app.py"):
                import app  # This will run the Gradio interface
            else:
                self.logger.error("❌ app.py not found for Gradio interface")
                return False
                
        except Exception as e:
            self.logger.error(f"❌ Failed to start Gradio interface: {e}")
            return False
    
    def run_fastapi_server(self):
        """Run FastAPI server"""
        try:
            self.logger.info("🚀 Starting FastAPI server...")
            
            import uvicorn
            from app.main import app
            
            # Server configuration
            server_config = config.server_config
            
            self.logger.info(f"🌐 Server starting on {server_config['host']}:{server_config['port']}")
            self.logger.info(f"👥 Workers: {server_config['workers']}")
            self.logger.info(f"📊 Log level: {server_config['log_level']}")
            
            # Run server
            uvicorn.run(
                app,
                host=server_config['host'],
                port=server_config['port'],
                workers=server_config['workers'],
                log_level=server_config['log_level'],
                access_log=server_config['access_log'],
                reload=server_config['reload']
            )
            
        except Exception as e:
            self.logger.error(f"❌ Failed to start FastAPI server: {e}")
            return False
    
    def run(self):
        """Main run method"""
        print("=" * 60)
        print("🏛️ Legal Dashboard - Universal Runner")
        print("=" * 60)
        
        # Setup environment
        if not setup_environment():
            self.logger.error("❌ Environment setup failed")
            sys.exit(1)
        
        # Check dependencies
        if not self.check_dependencies():
            self.logger.error("❌ Dependency check failed")
            sys.exit(1)
        
        # Test database
        if not self.test_database_connection():
            self.logger.error("❌ Database test failed")
            sys.exit(1)
        
        # Show configuration summary
        self.logger.info("📋 Configuration Summary:")
        self.logger.info(f"  Environment: {config.environment}")
        self.logger.info(f"  HF Spaces: {config.is_hf_spaces}")
        self.logger.info(f"  Docker: {config.is_docker}")
        self.logger.info(f"  Development: {config.is_development}")
        self.logger.info(f"  Data Directory: {config.directories['data']}")
        self.logger.info(f"  Cache Directory: {config.directories['cache']}")
        
        # Run appropriate interface
        try:
            if config.is_hf_spaces:
                # HF Spaces - use Gradio interface
                self.run_gradio_interface()
            else:
                # Docker/Local - use FastAPI server
                self.run_fastapi_server()
                
        except KeyboardInterrupt:
            self.logger.info("🛑 Received keyboard interrupt")
        except Exception as e:
            self.logger.error(f"❌ Unexpected error: {e}")
            sys.exit(1)
        finally:
            self.shutdown()
    
    def shutdown(self):
        """Graceful shutdown"""
        self.logger.info("🔄 Shutting down Legal Dashboard...")
        
        if self.app_process:
            try:
                self.app_process.terminate()
                self.app_process.wait(timeout=10)
            except:
                self.app_process.kill()
        
        self.logger.info("✅ Shutdown completed")

def main():
    """Main entry point"""
    runner = LegalDashboardRunner()
    runner.run()

if __name__ == "__main__":
    main()