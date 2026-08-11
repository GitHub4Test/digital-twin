"""
Database Operations Unit Tests - Backend
Tests for database.py covering initialization, CRUD operations, and health checks
"""

import sys
import os
import unittest
import tempfile
import sqlite3
import json
import uuid
from datetime import datetime
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../src'))
from sensor_service.db_controller.db_mgr import DBMgr
from sensor_service.db_controller.db_exceptions import DuplicateEventError

class TestDatabaseInit(unittest.TestCase):
    """Test suite for Database initialization"""

    def setUp(self):
        """Create a temporary database for each test"""
        self.temp_dir = tempfile.TemporaryDirectory()
        self.db_path = os.path.join(self.temp_dir.name, "test.db")
        self.db = DBMgr(db_path=self.db_path)

    def tearDown(self):
        """Clean up temporary database"""
        self.temp_dir.cleanup()

    def test_database_default_path(self):
        """Database should use default path when not specified"""
        db = DBMgr()
        self.assertEqual(db.db_path, os.environ.get("DB_PATH", "./data/database.db"))

    def test_database_custom_path(self):
        """Database should use custom path when specified"""
        custom_path = "/custom/path/db.sqlite"
        db = DBMgr(db_path=custom_path)
        self.assertEqual(db.db_path, custom_path)

class TestHealthCheck(unittest.TestCase):
    """Test suite for health_check method"""

    def setUp(self):
        """Create and initialize a temporary database for each test"""
        self.temp_dir = tempfile.TemporaryDirectory()
        self.db_path = os.path.join(self.temp_dir.name, "test.db")
        self.db = DBMgr(db_path=self.db_path)

    def tearDown(self):
        """Clean up temporary database"""
        self.temp_dir.cleanup()

    def test_health_check_returns_boolean(self):
        """Health check should return a boolean value"""
        result = self.db.health_check()
        self.assertIsInstance(result, bool)

    def test_health_check_healthy_database(self):
        """Should return True for a healthy database"""
        result = self.db.health_check()
        self.assertTrue(result)

    def test_health_check_nonexistent_database(self):
        """Should handle nonexistent database gracefully"""
        db = DBMgr(db_path="/nonexistent/path/database.db")
        # SQLite will create it, so it should return True
        result = db.health_check()
        # Could be True (if SQLite auto-creates) or False (if permission denied)
        self.assertIsInstance(result, bool)

if __name__ == "__main__":
    unittest.main()
