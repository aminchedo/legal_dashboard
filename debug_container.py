#!/usr/bin/env python3
"""
Debug script for Docker container environment
"""

import os
import sys
import sqlite3
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def debug_environment():
    """Debug the container environment"""
    print("=== Container Environment Debug ===")

    # Check current directory
    print(f"Current directory: {os.getcwd()}")

    # Check if /app/data exists
    data_dir = "/app/data"
    if os.path.exists(data_dir):
        print(f"✅ Data directory exists: {data_dir}")
        print(f"   Permissions: {oct(os.stat(data_dir).st_mode)[-3:]}")
        print(f"   Writable: {os.access(data_dir, os.W_OK)}")
    else:
        print(f"❌ Data directory does not exist: {data_dir}")

    # Check environment variables
    print(f"DATABASE_PATH: {os.getenv('DATABASE_PATH', 'Not set')}")
    print(f"TRANSFORMERS_CACHE: {os.getenv('TRANSFORMERS_CACHE', 'Not set')}")
    print(f"HF_HOME: {os.getenv('HF_HOME', 'Not set')}")

    # Try to create data directory
    try:
        os.makedirs(data_dir, mode=0o777, exist_ok=True)
        print(f"✅ Created/verified data directory: {data_dir}")
    except Exception as e:
        print(f"❌ Failed to create data directory: {e}")

    # Try database connection
    try:
        db_path = os.getenv('DATABASE_PATH', '/app/data/legal_dashboard.db')
        print(f"Testing database connection to: {db_path}")

        # Ensure directory exists
        db_dir = os.path.dirname(db_path)
        os.makedirs(db_dir, mode=0o777, exist_ok=True)

        # Test connection
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT 1")
        result = cursor.fetchone()
        print(f"✅ Database connection successful: {result}")
        conn.close()

    except Exception as e:
        print(f"❌ Database connection failed: {e}")


if __name__ == "__main__":
    debug_environment()
