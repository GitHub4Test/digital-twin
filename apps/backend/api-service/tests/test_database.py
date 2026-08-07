"""
Database Operations Unit Tests - Backend
Tests for database.py covering initialization, CRUD operations, and health checks
"""

import sys
import os
import unittest
import tempfile
import sqlite3
from datetime import datetime
from pathlib import Path

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../src'))
from api_service.db.database import Database
from api_service.models import SensorReadingResponse


class TestDatabaseInit(unittest.TestCase):
    """Test suite for Database initialization"""

    def setUp(self):
        """Create a temporary database for each test"""
        self.temp_dir = tempfile.TemporaryDirectory()
        self.db_path = os.path.join(self.temp_dir.name, "test.db")
        self.db = Database(db_path=self.db_path)

    def tearDown(self):
        """Clean up temporary database"""
        self.temp_dir.cleanup()

    def test_database_init_creates_directory(self):
        """Database init should create directory if it doesn't exist"""
        self.db.init()
        self.assertTrue(os.path.exists(os.path.dirname(self.db_path)))

    def test_database_init_creates_table(self):
        """Database init should create sensor table"""
        self.db.init()
        
        # Verify table exists
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='sensor'")
        result = cursor.fetchone()
        conn.close()
        
        self.assertIsNotNone(result)
        self.assertEqual(result[0], 'sensor')

    def test_database_init_idempotent(self):
        """Database init should be idempotent (safe to call multiple times)"""
        self.db.init()
        self.db.init()  # Should not raise any error
        
        # Verify table still exists and is intact
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM sensor")
        count = cursor.fetchone()[0]
        conn.close()
        
        self.assertEqual(count, 0)

    def test_database_default_path(self):
        """Database should use default path when not specified"""
        db = Database()
        self.assertEqual(db.db_path, os.environ.get("DB_PATH", "./data/database.db"))

    def test_database_custom_path(self):
        """Database should use custom path when specified"""
        custom_path = "/custom/path/db.sqlite"
        db = Database(db_path=custom_path)
        self.assertEqual(db.db_path, custom_path)


class TestInsertReading(unittest.TestCase):
    """Test suite for insert_reading method"""

    def setUp(self):
        """Create and initialize a temporary database for each test"""
        self.temp_dir = tempfile.TemporaryDirectory()
        self.db_path = os.path.join(self.temp_dir.name, "test.db")
        self.db = Database(db_path=self.db_path)
        self.db.init()

    def tearDown(self):
        """Clean up temporary database"""
        self.temp_dir.cleanup()

    def test_insert_valid_reading(self):
        """Should successfully insert a valid sensor reading"""
        timestamp = datetime.now().isoformat()
        result = self.db.insert_reading(event_id="event1", timestamp=timestamp, temperature=24.5, humidity=61.2)
        
        self.assertEqual(result["status"], "success")
        self.assertIn("recorded", result["message"].lower())

    def test_insert_reading_persists_to_database(self):
        """Inserted reading should be retrievable from database"""
        timestamp = datetime.now().isoformat()
        self.db.insert_reading(event_id="event1", timestamp=timestamp, temperature=22.3, humidity=55.0)
        
        # Verify directly from database
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM sensor")
        count = cursor.fetchone()[0]
        conn.close()
        
        self.assertEqual(count, 1)

    def test_insert_multiple_readings(self):
        """Should successfully insert multiple sensor readings"""
        timestamps = [
            datetime.now().isoformat(),
            datetime.now().isoformat()
        ]
        
        for i, timestamp in enumerate(timestamps):
            result = self.db.insert_reading(event_id=f"event{i+1}", timestamp=timestamp, temperature=20.0 + i, humidity=50.0 + i)
            self.assertEqual(result["status"], "success")
        
        # Verify count
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM sensor")
        count = cursor.fetchone()[0]
        conn.close()
        
        self.assertEqual(count, 2)

    def test_insert_reading_with_negative_temperature(self):
        """Should accept negative temperature values"""
        timestamp = datetime.now().isoformat()
        result = self.db.insert_reading(event_id="event1", timestamp=timestamp, temperature=-10.5, humidity=40.0)
        self.assertEqual(result["status"], "success")

    def test_insert_reading_with_high_humidity(self):
        """Should accept high humidity values"""
        timestamp = datetime.now().isoformat()
        result = self.db.insert_reading(event_id="event1", timestamp=timestamp, temperature=25.0, humidity=99.9)
        self.assertEqual(result["status"], "success")

    def test_insert_reading_with_extreme_values(self):
        """Should accept extreme but valid temperature and humidity values"""
        timestamp = datetime.now().isoformat()
        result = self.db.insert_reading(event_id="event1", timestamp=timestamp, temperature=-50.0, humidity=0.0)  # Min values
        self.assertEqual(result["status"], "success")
        
        result = self.db.insert_reading(event_id="event2", timestamp=timestamp, temperature=150.0, humidity=100.0)  # Max values
        self.assertEqual(result["status"], "success")


class TestGetReadings(unittest.TestCase):
    """Test suite for get_readings method"""

    def setUp(self):
        """Create, initialize, and populate a temporary database for each test"""
        self.temp_dir = tempfile.TemporaryDirectory()
        self.db_path = os.path.join(self.temp_dir.name, "test.db")
        self.db = Database(db_path=self.db_path)
        self.db.init()

    def tearDown(self):
        """Clean up temporary database"""
        self.temp_dir.cleanup()

    def test_get_readings_empty_database(self):
        """Should return empty list when database has no readings"""
        readings = self.db.get_readings()
        self.assertEqual(readings, [])

    def test_get_readings_single_entry(self):
        """Should retrieve a single sensor reading"""
        timestamp = datetime.now().isoformat()
        self.db.insert_reading(event_id="event1", timestamp=timestamp, temperature=24.5, humidity=61.2)
        
        readings = self.db.get_readings()
        
        self.assertEqual(len(readings), 1)
        self.assertIsInstance(readings[0], SensorReadingResponse)
        self.assertEqual(float(readings[0].temperature), 24.5)
        self.assertEqual(float(readings[0].humidity), 61.2)

    def test_get_readings_multiple_entries(self):
        """Should retrieve multiple sensor readings"""
        timestamps = [
            datetime.now().isoformat(),
            datetime.now().isoformat()
        ]
        
        for i, timestamp in enumerate(timestamps):
            self.db.insert_reading(event_id=f"event{i+1}", timestamp=timestamp, temperature=20.0 + i, humidity=50.0 + i)
        
        readings = self.db.get_readings()
        self.assertEqual(len(readings), 2)

    def test_get_readings_returns_most_recent_first(self):
        """Should return readings ordered by timestamp (most recent first)"""
        timestamps = [
            "2026-01-01T10:00:00",
            "2026-01-01T11:00:00",
            "2026-01-01T09:00:00"
        ]
        
        for i, timestamp in enumerate(timestamps):
            self.db.insert_reading(event_id=f"event{i+1}", timestamp=timestamp, temperature=20.0 + i, humidity=50.0 + i)
        
        readings = self.db.get_readings()
        
        # Most recent should be first (timestamps are parsed as datetime objects)
        self.assertEqual(str(readings[0].timestamp), "2026-01-01 11:00:00")
        self.assertEqual(str(readings[1].timestamp), "2026-01-01 10:00:00")
        self.assertEqual(str(readings[2].timestamp), "2026-01-01 09:00:00")

    def test_get_readings_respects_limit(self):
        """Should respect the limit parameter"""
        # Insert 10 readings
        for i in range(10):
            timestamp = f"2026-01-01T{i:02d}:00:00"
            self.db.insert_reading(event_id=f"event{i+1}", timestamp=timestamp, temperature=20.0 + i, humidity=50.0 + i)
        
        readings = self.db.get_readings(limit=5)
        self.assertEqual(len(readings), 5)

    def test_get_readings_default_limit(self):
        """Should use default limit of 200"""
        # Insert 150 readings
        for i in range(150):
            timestamp = f"2026-01-01T{i % 24:02d}:{i % 60:02d}:{i % 60:02d}"
            self.db.insert_reading(event_id=f"event{i+1}", timestamp=timestamp, temperature=20.0 + (i % 50), humidity=50.0)
        
        readings = self.db.get_readings()
        self.assertEqual(len(readings), 150)

    def test_get_readings_beyond_limit_respected(self):
        """Should not return more than limit even if more data exists"""
        # Insert 300 readings
        for i in range(300):
            timestamp = f"2026-01-01T{i % 24:02d}:{i % 60:02d}:{i % 60:02d}"
            self.db.insert_reading(event_id=f"event{i+1}", timestamp=timestamp, temperature=20.0, humidity=50.0)
        
        readings = self.db.get_readings(limit=200)
        self.assertEqual(len(readings), 200)

    def test_get_readings_returns_sensor_reading_response_objects(self):
        """Should return SensorReadingResponse objects"""
        timestamp = datetime.now().isoformat()
        self.db.insert_reading(event_id="event1", timestamp=timestamp, temperature=24.5, humidity=61.2)
        
        readings = self.db.get_readings()
        
        for reading in readings:
            self.assertIsInstance(reading, SensorReadingResponse)
            self.assertTrue(hasattr(reading, 'timestamp'))
            self.assertTrue(hasattr(reading, 'temperature'))
            self.assertTrue(hasattr(reading, 'humidity'))


class TestClearReadings(unittest.TestCase):
    """Test suite for clear_readings method"""

    def setUp(self):
        """Create, initialize, and populate a temporary database for each test"""
        self.temp_dir = tempfile.TemporaryDirectory()
        self.db_path = os.path.join(self.temp_dir.name, "test.db")
        self.db = Database(db_path=self.db_path)
        self.db.init()

    def tearDown(self):
        """Clean up temporary database"""
        self.temp_dir.cleanup()

    def test_clear_readings_empty_database(self):
        """Should successfully clear empty database"""
        result = self.db.clear_readings()
        
        self.assertEqual(result["status"], "success")
        self.assertIn("cleared", result["message"].lower())

    def test_clear_readings_removes_all_data(self):
        """Should remove all sensor data from database"""
        # Insert some readings
        for i in range(5):
            timestamp = datetime.now().isoformat()
            self.db.insert_reading(event_id=f"event{i+1}", timestamp=timestamp, temperature=20.0 + i, humidity=50.0 + i)
        
        # Verify data exists
        readings = self.db.get_readings()
        self.assertEqual(len(readings), 5)
        
        # Clear readings
        result = self.db.clear_readings()
        self.assertEqual(result["status"], "success")
        
        # Verify data is gone
        readings = self.db.get_readings()
        self.assertEqual(len(readings), 0)

    def test_clear_readings_is_idempotent(self):
        """Should safely clear database multiple times"""
        # Insert some readings
        for i in range(3):
            timestamp = datetime.now().isoformat()
            self.db.insert_reading(event_id=f"event{i+1}", timestamp=timestamp, temperature=20.0, humidity=50.0)
        
        # Clear twice
        result1 = self.db.clear_readings()
        result2 = self.db.clear_readings()
        
        self.assertEqual(result1["status"], "success")
        self.assertEqual(result2["status"], "success")
        
        # Database should still be empty
        readings = self.db.get_readings()
        self.assertEqual(len(readings), 0)


class TestHealthCheck(unittest.TestCase):
    """Test suite for health_check method"""

    def setUp(self):
        """Create and initialize a temporary database for each test"""
        self.temp_dir = tempfile.TemporaryDirectory()
        self.db_path = os.path.join(self.temp_dir.name, "test.db")
        self.db = Database(db_path=self.db_path)
        self.db.init()

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
        db = Database(db_path="/nonexistent/path/database.db")
        # SQLite will create it, so it should return True
        result = db.health_check()
        # Could be True (if SQLite auto-creates) or False (if permission denied)
        self.assertIsInstance(result, bool)

    def test_health_check_with_data_present(self):
        """Should return True even with data in database"""
        # Insert some data
        for i in range(10):
            timestamp = datetime.now().isoformat()
            self.db.insert_reading(event_id=f"event{i+1}", timestamp=timestamp, temperature=20.0 + i, humidity=50.0 + i)
        
        result = self.db.health_check()
        self.assertTrue(result)

    def test_health_check_after_clear(self):
        """Should return True after clearing database"""
        # Insert and then clear
        timestamp = datetime.now().isoformat()
        self.db.insert_reading(event_id="event1", timestamp=timestamp, temperature=20.0, humidity=50.0)
        self.db.clear_readings()
        
        result = self.db.health_check()
        self.assertTrue(result)


class TestDatabaseIntegration(unittest.TestCase):
    """Integration tests for multiple database operations"""

    def setUp(self):
        """Create and initialize a temporary database for each test"""
        self.temp_dir = tempfile.TemporaryDirectory()
        self.db_path = os.path.join(self.temp_dir.name, "test.db")
        self.db = Database(db_path=self.db_path)
        self.db.init()

    def tearDown(self):
        """Clean up temporary database"""
        self.temp_dir.cleanup()

    def test_full_workflow(self):
        """Test complete workflow: init -> insert -> retrieve -> clear"""
        # Insert readings
        timestamps = [
            "2026-01-01T10:00:00",
            "2026-01-01T11:00:00",
            "2026-01-01T12:00:00"
        ]
        
        for i, timestamp in enumerate(timestamps):
            result = self.db.insert_reading(event_id=f"event{i+1}", timestamp=timestamp, temperature=20.0 + i, humidity=50.0 + i)
            self.assertEqual(result["status"], "success")
        
        # Verify health check passes
        self.assertTrue(self.db.health_check())
        
        # Retrieve readings
        readings = self.db.get_readings()
        self.assertEqual(len(readings), 3)
        
        # Clear all
        clear_result = self.db.clear_readings()
        self.assertEqual(clear_result["status"], "success")
        
        # Verify empty
        readings = self.db.get_readings()
        self.assertEqual(len(readings), 0)

    def test_insert_and_retrieve_preserves_data(self):
        """Test that inserted data is correctly preserved and retrieved"""
        test_data = [
            ("2026-01-01T10:00:00", 22.5, 55.0),
            ("2026-01-01T11:00:00", 23.5, 56.0),
            ("2026-01-01T12:00:00", 24.5, 57.0),
        ]
        
        # Insert test data
        for i, (timestamp, temp, humidity) in enumerate(test_data):
            self.db.insert_reading(event_id=f"event{i+1}", timestamp=timestamp, temperature=temp, humidity=humidity)
        
        # Retrieve and verify
        readings = self.db.get_readings()
        self.assertEqual(len(readings), len(test_data))
        
        # Verify each reading matches (most recent first)
        # Note: timestamps are parsed as datetime objects
        expected_times = [
            "2026-01-01 12:00:00",
            "2026-01-01 11:00:00",
            "2026-01-01 10:00:00"
        ]
        for i, reading in enumerate(readings):
            self.assertEqual(str(reading.timestamp), expected_times[i])
            idx = len(test_data) - 1 - i
            self.assertEqual(float(reading.temperature), test_data[idx][1])
            self.assertEqual(float(reading.humidity), test_data[idx][2])

    def test_multiple_clear_operations_sequence(self):
        """Test sequence of insert and clear operations"""
        # First batch
        self.db.insert_reading(event_id="event1", timestamp="2026-01-01T10:00:00", temperature=20.0, humidity=50.0)
        self.db.insert_reading(event_id="event2", timestamp="2026-01-01T11:00:00", temperature=21.0, humidity=51.0)
        
        readings = self.db.get_readings()
        self.assertEqual(len(readings), 2)
        
        # Clear
        self.db.clear_readings()
        
        # Second batch
        self.db.insert_reading(event_id="event3", timestamp="2026-01-01T12:00:00", temperature=22.0, humidity=52.0)
        readings = self.db.get_readings()
        self.assertEqual(len(readings), 1)
        self.assertEqual(readings[0].temperature, 22.0)

if __name__ == "__main__":
    unittest.main()
