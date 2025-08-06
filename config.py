"""
Configuration Management for Legal Dashboard
==========================================
Centralized configuration with environment detection and optimization.
"""

import os
import logging
import warnings
from pathlib import Path
from typing import Dict, Any, Optional

# Suppress common warnings
warnings.filterwarnings("ignore", message=".*trapped.*error reading bcrypt version.*")
warnings.filterwarnings("ignore", message=".*TRANSFORMERS_CACHE.*deprecated.*")
warnings.filterwarnings("ignore", message=".*Field.*model_name.*conflict.*")
warnings.filterwarnings("ignore", category=FutureWarning, module="transformers")

class Config:
    """Configuration manager with environment detection"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.is_hf_spaces = bool(os.getenv("SPACE_ID"))
        self.is_docker = os.path.exists("/.dockerenv")
        self.is_development = os.getenv("ENVIRONMENT", "production") == "development"
        
        # Detect environment
        if self.is_hf_spaces:
            self.environment = "huggingface_spaces"
        elif self.is_docker:
            self.environment = "docker"
        else:
            self.environment = "local"
            
        self.logger.info(f"🌍 Environment detected: {self.environment}")
        self._setup_config()
    
    def _setup_config(self):
        """Setup configuration based on environment"""
        
        # Base directories
        if self.is_hf_spaces:
            self.base_dir = "/tmp/legal_dashboard"
            self.cache_dir = "/tmp/hf_cache"
        elif self.is_docker:
            self.base_dir = "/app"
            self.cache_dir = "/app/cache"
        else:
            self.base_dir = os.getcwd()
            self.cache_dir = os.path.join(self.base_dir, "cache")
        
        # Create directory structure
        self.directories = {
            "base": self.base_dir,
            "data": os.path.join(self.base_dir, "data"),
            "cache": self.cache_dir,
            "logs": os.path.join(self.base_dir, "logs"),
            "uploads": os.path.join(self.base_dir, "uploads"),
            "backups": os.path.join(self.base_dir, "backups"),
        }
        
        # Create directories
        for name, path in self.directories.items():
            try:
                os.makedirs(path, exist_ok=True)
                self.logger.info(f"📁 {name.capitalize()} directory: {path}")
            except PermissionError:
                self.logger.warning(f"⚠️ Cannot create {name} directory: {path}")
                # Fallback to /tmp
                fallback = f"/tmp/legal_dashboard_{name}"
                os.makedirs(fallback, exist_ok=True)
                self.directories[name] = fallback
                self.logger.info(f"📁 Using fallback {name} directory: {fallback}")
    
    @property
    def database_config(self) -> Dict[str, Any]:
        """Database configuration"""
        return {
            "dir": self.directories["data"],
            "name": "legal_documents.db",
            "path": os.path.join(self.directories["data"], "legal_documents.db"),
            "backup_interval": 3600 if self.is_hf_spaces else 86400,  # More frequent in HF Spaces
        }
    
    @property
    def auth_config(self) -> Dict[str, Any]:
        """Authentication configuration"""
        return {
            "secret_key": os.getenv("JWT_SECRET_KEY", "your-secret-key-change-in-production"),
            "algorithm": "HS256",
            "access_token_expire_minutes": int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30")),
            "refresh_token_expire_days": int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", "7")),
            "bcrypt_rounds": 12 if not self.is_hf_spaces else 10,  # Lighter for HF Spaces
        }
    
    @property
    def server_config(self) -> Dict[str, Any]:
        """Server configuration"""
        return {
            "host": "0.0.0.0" if (self.is_hf_spaces or self.is_docker) else "127.0.0.1",
            "port": int(os.getenv("PORT", "7860" if self.is_hf_spaces else "8000")),
            "workers": 1 if self.is_hf_spaces else int(os.getenv("WORKERS", "4")),
            "reload": self.is_development,
            "log_level": os.getenv("LOG_LEVEL", "info").lower(),
            "access_log": not self.is_hf_spaces,  # Disable access log in HF Spaces
        }
    
    @property
    def ai_config(self) -> Dict[str, Any]:
        """AI/ML configuration"""
        return {
            "cache_dir": self.cache_dir,
            "model_name": "microsoft/trocr-small-stage1" if self.is_hf_spaces else "microsoft/trocr-base-stage1",
            "device": "cpu",  # Force CPU for compatibility
            "max_workers": 1 if self.is_hf_spaces else 2,
            "batch_size": 1 if self.is_hf_spaces else 4,
            "timeout": 30 if self.is_hf_spaces else 60,
        }
    
    @property
    def redis_config(self) -> Dict[str, Any]:
        """Redis configuration"""
        return {
            "host": os.getenv("REDIS_HOST", "localhost"),
            "port": int(os.getenv("REDIS_PORT", "6379")),
            "db": int(os.getenv("REDIS_DB", "0")),
            "password": os.getenv("REDIS_PASSWORD"),
            "socket_timeout": 5,
            "decode_responses": True,
            "retry_on_timeout": True,
            "health_check_interval": 30,
            "fallback_to_memory": True,  # Always fallback if Redis unavailable
        }
    
    @property
    def logging_config(self) -> Dict[str, Any]:
        """Logging configuration"""
        return {
            "level": logging.INFO if not self.is_development else logging.DEBUG,
            "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            "file": os.path.join(self.directories["logs"], "legal_dashboard.log") if not self.is_hf_spaces else None,
            "max_bytes": 10 * 1024 * 1024,  # 10MB
            "backup_count": 5,
        }
    
    def get_environment_variables(self) -> Dict[str, str]:
        """Get all environment variables to set"""
        return {
            # Paths
            "DATABASE_DIR": self.directories["data"],
            "DATABASE_PATH": self.database_config["path"],
            "PYTHONPATH": self.base_dir,
            
            # AI/ML
            "HF_HOME": self.cache_dir,
            "TRANSFORMERS_CACHE": self.cache_dir,  # For backward compatibility
            "HF_HUB_CACHE": self.cache_dir,
            "TORCH_HOME": self.cache_dir,
            "TOKENIZERS_PARALLELISM": "false",
            "CUDA_VISIBLE_DEVICES": "",  # Force CPU
            
            # Performance
            "OMP_NUM_THREADS": "1" if self.is_hf_spaces else "4",
            "PYTHONUNBUFFERED": "1",
            "PYTHONDONTWRITEBYTECODE": "1",
            
            # Logging
            "LOG_LEVEL": self.server_config["log_level"].upper(),
            "ENVIRONMENT": self.environment,
            
            # Application
            "JWT_SECRET_KEY": self.auth_config["secret_key"],
            "ACCESS_TOKEN_EXPIRE_MINUTES": str(self.auth_config["access_token_expire_minutes"]),
            "REFRESH_TOKEN_EXPIRE_DAYS": str(self.auth_config["refresh_token_expire_days"]),
        }
    
    def apply_environment_variables(self):
        """Apply all environment variables"""
        env_vars = self.get_environment_variables()
        
        for key, value in env_vars.items():
            os.environ[key] = value
            if not key.startswith(("JWT_", "SECRET")):  # Don't log sensitive data
                self.logger.info(f"🔧 {key}={value}")
            else:
                self.logger.info(f"🔧 {key}=***")
    
    def validate_setup(self) -> bool:
        """Validate configuration setup"""
        issues = []
        
        # Check directory permissions
        for name, path in self.directories.items():
            if not os.path.exists(path):
                issues.append(f"Directory {name} does not exist: {path}")
            elif not os.access(path, os.W_OK):
                issues.append(f"Directory {name} is not writable: {path}")
        
        # Check required environment variables
        required_vars = ["DATABASE_DIR", "HF_HOME"]
        for var in required_vars:
            if not os.getenv(var):
                issues.append(f"Required environment variable {var} is not set")
        
        # Check database path
        db_path = self.database_config["path"]
        db_dir = os.path.dirname(db_path)
        if not os.access(db_dir, os.W_OK):
            issues.append(f"Database directory is not writable: {db_dir}")
        
        if issues:
            self.logger.error("❌ Configuration validation failed:")
            for issue in issues:
                self.logger.error(f"  - {issue}")
            return False
        
        self.logger.info("✅ Configuration validation passed")
        return True
    
    def get_summary(self) -> Dict[str, Any]:
        """Get configuration summary"""
        return {
            "environment": self.environment,
            "is_hf_spaces": self.is_hf_spaces,
            "is_docker": self.is_docker,
            "is_development": self.is_development,
            "directories": self.directories,
            "database_config": self.database_config,
            "server_config": self.server_config,
            "ai_config": self.ai_config,
        }

# Global configuration instance
config = Config()

def setup_environment():
    """Setup environment with configuration"""
    logging.basicConfig(
        level=config.logging_config["level"],
        format=config.logging_config["format"]
    )
    
    logger = logging.getLogger(__name__)
    logger.info("🔧 Setting up Legal Dashboard configuration...")
    
    # Apply environment variables
    config.apply_environment_variables()
    
    # Validate setup
    if not config.validate_setup():
        logger.error("❌ Configuration setup failed")
        return False
    
    logger.info("✅ Configuration setup completed")
    logger.info(f"📋 Environment: {config.environment}")
    logger.info(f"📁 Data directory: {config.directories['data']}")
    logger.info(f"💾 Cache directory: {config.directories['cache']}")
    logger.info(f"🌐 Server: {config.server_config['host']}:{config.server_config['port']}")
    
    return True

if __name__ == "__main__":
    # Test configuration
    setup_environment()
    
    import json
    print("\n" + "="*50)
    print("Configuration Summary:")
    print("="*50)
    print(json.dumps(config.get_summary(), indent=2, default=str))