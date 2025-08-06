#!/usr/bin/env python3
"""
Test database connection in Docker environment
"""

from app.services.database_service import DatabaseManager
import os
import sys
import sqlite3
import logging

# Add the app directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))


def test_database_connection():
    """Test database connection and initialization"""
    print("Testing database connection...")

    try:
        # Test with default path
        db_manager = DatabaseManager()
        print(f"✅ Database manager created with path: {db_manager.db_path}")

        # Test initialization
        db_manager.initialize()
        print("✅ Database initialized successfully")

        # Test connection
        if db_manager.is_connected():
            print("✅ Database connection verified")
        else:
            print("❌ Database connection failed")
            return False

        # Test basic operations
        cursor = db_manager.connection.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        print(f"✅ Found {len(tables)} tables in database")

        db_manager.close()
        print("✅ Database connection closed successfully")

        return True

    except Exception as e:
        print(f"❌ Database test failed: {e}")
        return False


if __name__ == "__main__":
    success = test_database_connection()
    sys.exit(0 if success else 1)
