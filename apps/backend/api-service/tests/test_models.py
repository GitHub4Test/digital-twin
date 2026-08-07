"""
API Service Models Unit Tests - Backend
Tests for Pydantic models in models.py covering data validation and serialization
"""

import sys
import os
import unittest
from datetime import datetime
from pydantic import ValidationError

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../apps/backend/api-service/src'))
from api_service.models import (
    SensorReadingCreate,
    SensorReadingResponse,
    HealthCheckResponse,
    MessageResponse,
    ErrorResponse
)


class TestSensorReadingCreate(unittest.TestCase):
    """Test suite for SensorReadingCreate model"""

    def test_valid_sensor_reading(self):
        """Should create valid sensor reading"""
        now = datetime.now().isoformat()
        reading = SensorReadingCreate(
            timestamp=now,
            temperature=24.5,
            humidity=61.2
        )
        self.assertEqual(reading.temperature, 24.5)
        self.assertEqual(reading.humidity, 61.2)

    def test_temperature_min_boundary(self):
        """Temperature at minimum boundary (-50) should be valid"""
        now = datetime.now().isoformat()
        reading = SensorReadingCreate(
            timestamp=now,
            temperature=-50.0,
            humidity=50.0
        )
        self.assertEqual(reading.temperature, -50.0)

    def test_temperature_max_boundary(self):
        """Temperature at maximum boundary (150) should be valid"""
        now = datetime.now().isoformat()
        reading = SensorReadingCreate(
            timestamp=now,
            temperature=150.0,
            humidity=50.0
        )
        self.assertEqual(reading.temperature, 150.0)

    def test_temperature_below_minimum(self):
        """Temperature below -50 should fail validation"""
        now = datetime.now().isoformat()
        with self.assertRaises(ValidationError):
            SensorReadingCreate(
                timestamp=now,
                temperature=-50.1,
                humidity=50.0
            )

    def test_temperature_above_maximum(self):
        """Temperature above 150 should fail validation"""
        now = datetime.now().isoformat()
        with self.assertRaises(ValidationError):
            SensorReadingCreate(
                timestamp=now,
                temperature=150.1,
                humidity=50.0
            )

    def test_humidity_min_boundary(self):
        """Humidity at minimum boundary (0) should be valid"""
        now = datetime.now().isoformat()
        reading = SensorReadingCreate(
            timestamp=now,
            temperature=25.0,
            humidity=0.0
        )
        self.assertEqual(reading.humidity, 0.0)

    def test_humidity_max_boundary(self):
        """Humidity at maximum boundary (100) should be valid"""
        now = datetime.now().isoformat()
        reading = SensorReadingCreate(
            timestamp=now,
            temperature=25.0,
            humidity=100.0
        )
        self.assertEqual(reading.humidity, 100.0)

    def test_humidity_below_minimum(self):
        """Humidity below 0 should fail validation"""
        now = datetime.now().isoformat()
        with self.assertRaises(ValidationError):
            SensorReadingCreate(
                timestamp=now,
                temperature=25.0,
                humidity=-0.1
            )

    def test_humidity_above_maximum(self):
        """Humidity above 100 should fail validation"""
        now = datetime.now().isoformat()
        with self.assertRaises(ValidationError):
            SensorReadingCreate(
                timestamp=now,
                temperature=25.0,
                humidity=100.1
            )

    def test_missing_timestamp(self):
        """Missing timestamp should fail validation"""
        with self.assertRaises(ValidationError):
            SensorReadingCreate(
                temperature=25.0,
                humidity=50.0
            )

    def test_missing_temperature(self):
        """Missing temperature should fail validation"""
        now = datetime.now().isoformat()
        with self.assertRaises(ValidationError):
            SensorReadingCreate(
                timestamp=now,
                humidity=50.0
            )

    def test_missing_humidity(self):
        """Missing humidity should fail validation"""
        now = datetime.now().isoformat()
        with self.assertRaises(ValidationError):
            SensorReadingCreate(
                timestamp=now,
                temperature=25.0
            )

    def test_invalid_timestamp_format(self):
        """Invalid timestamp format should fail"""
        with self.assertRaises(ValidationError):
            SensorReadingCreate(
                timestamp="not-a-timestamp",
                temperature=25.0,
                humidity=50.0
            )

    def test_temperature_with_decimals(self):
        """Temperature with decimal places should work"""
        now = datetime.now().isoformat()
        reading = SensorReadingCreate(
            timestamp=now,
            temperature=24.567,
            humidity=61.234
        )
        self.assertAlmostEqual(reading.temperature, 24.567, places=3)

    def test_realistic_sensor_data(self):
        """Should accept realistic sensor data"""
        now = datetime.now().isoformat()
        reading = SensorReadingCreate(
            timestamp=now,
            temperature=22.5,
            humidity=55.0
        )
        self.assertEqual(reading.temperature, 22.5)
        self.assertEqual(reading.humidity, 55.0)

    def test_extreme_valid_temperatures(self):
        """Should accept extreme but valid temperatures"""
        now = datetime.now().isoformat()
        cold = SensorReadingCreate(timestamp=now, temperature=-40.0, humidity=50.0)
        hot = SensorReadingCreate(timestamp=now, temperature=140.0, humidity=50.0)
        self.assertEqual(cold.temperature, -40.0)
        self.assertEqual(hot.temperature, 140.0)

    def test_humidity_boundary_conditions(self):
        """Should handle humidity boundary conditions"""
        now = datetime.now().isoformat()
        dry = SensorReadingCreate(timestamp=now, temperature=25.0, humidity=5.0)
        humid = SensorReadingCreate(timestamp=now, temperature=25.0, humidity=95.0)
        self.assertEqual(dry.humidity, 5.0)
        self.assertEqual(humid.humidity, 95.0)


class TestSensorReadingResponse(unittest.TestCase):
    """Test suite for SensorReadingResponse model"""

    def test_valid_response(self):
        """Should create valid response"""
        now = datetime.now().isoformat()
        response = SensorReadingResponse(
            timestamp=now,
            temperature=24.5,
            humidity=61.2,
            status="RECEIVED"
        )
        self.assertEqual(response.temperature, 24.5)
        self.assertEqual(response.humidity, 61.2)
        self.assertEqual(response.status, "RECEIVED")

    def test_from_attributes_config(self):
        """Should allow creation from ORM objects"""
        class FakeSensor:
            timestamp = datetime.now().isoformat()
            temperature = 25.0
            humidity = 60.0
            status = "RECEIVED"

        sensor = FakeSensor()
        response = SensorReadingResponse.model_validate(sensor)
        self.assertEqual(response.temperature, 25.0)
        self.assertEqual(response.humidity, 60.0)
        self.assertEqual(response.status, "RECEIVED")

    def test_response_has_all_fields(self):
        """Response should have timestamp, temperature, humidity"""
        now = datetime.now().isoformat()
        response = SensorReadingResponse(
            timestamp=now,
            temperature=25.0,
            humidity=50.0,
            status="RECEIVED"
        )
        self.assertTrue(hasattr(response, 'timestamp'))
        self.assertTrue(hasattr(response, 'temperature'))
        self.assertTrue(hasattr(response, 'humidity'))
        self.assertTrue(hasattr(response, 'status'))


class TestHealthCheckResponse(unittest.TestCase):
    """Test suite for HealthCheckResponse model"""

    def test_valid_health_check(self):
        """Should create valid health check response"""
        health = HealthCheckResponse(
            status="healthy",
            service="backend",
            version="1.0.0"
        )
        self.assertEqual(health.status, "healthy")
        self.assertEqual(health.service, "backend")
        self.assertEqual(health.version, "1.0.0")

    def test_different_status_values(self):
        """Should accept different status values"""
        for status in ["healthy", "unhealthy", "degraded"]:
            health = HealthCheckResponse(
                status=status,
                service="backend",
                version="1.0.0"
            )
            self.assertEqual(health.status, status)

    def test_missing_status(self):
        """Missing status should fail validation"""
        with self.assertRaises(ValidationError):
            HealthCheckResponse(
                service="backend",
                version="1.0.0"
            )

    def test_missing_service(self):
        """Missing service should fail validation"""
        with self.assertRaises(ValidationError):
            HealthCheckResponse(
                status="healthy",
                version="1.0.0"
            )

    def test_missing_version(self):
        """Missing version should fail validation"""
        with self.assertRaises(ValidationError):
            HealthCheckResponse(
                status="healthy",
                service="backend"
            )

    def test_version_formats(self):
        """Should accept various version formats"""
        for version in ["1.0.0", "1.0", "1", "1.0.0-beta", "2023.05.23"]:
            health = HealthCheckResponse(
                status="healthy",
                service="backend",
                version=version
            )
            self.assertEqual(health.version, version)


class TestMessageResponse(unittest.TestCase):
    """Test suite for MessageResponse model"""

    def test_valid_message_response(self):
        """Should create valid message response"""
        response = MessageResponse(
            message="Sensor reading stored successfully",
            event_id="event-123",
            status="RECEIVED",
        )
        self.assertEqual(response.message, "Sensor reading stored successfully")
        self.assertEqual(response.event_id, "event-123")
        self.assertEqual(response.status, "RECEIVED")

    def test_missing_message(self):
        """Missing message should fail validation"""
        with self.assertRaises(ValidationError):
            MessageResponse()

    def test_empty_message(self):
        """Empty string message should be valid"""
        response = MessageResponse(message="", event_id="event-123", status="RECEIVED")
        self.assertEqual(response.message, "")

    def test_long_message(self):
        """Should accept long messages"""
        long_msg = "x" * 1000
        response = MessageResponse(message=long_msg, event_id="event-123", status="RECEIVED")
        self.assertEqual(response.message, long_msg)

    def test_special_characters_in_message(self):
        """Should accept special characters"""
        special_msg = "Error: Connection to 192.168.1.1:8000 failed! Status: ⚠"
        response = MessageResponse(message=special_msg, event_id="event-456", status="ERROR")
        self.assertEqual(response.message, special_msg)


class TestErrorResponse(unittest.TestCase):
    """Test suite for ErrorResponse model"""

    def test_valid_error_response(self):
        """Should create valid error response"""
        error = ErrorResponse(
            detail="Database connection failed"
        )
        self.assertEqual(error.detail, "Database connection failed")

    def test_missing_detail(self):
        """Missing detail should fail validation"""
        with self.assertRaises(ValidationError):
            ErrorResponse()

    def test_empty_detail(self):
        """Empty detail should be valid"""
        error = ErrorResponse(detail="")
        self.assertEqual(error.detail, "")

    def test_detailed_error_messages(self):
        """Should accept detailed error messages"""
        errors = [
            "Database connection failed: timeout after 30s",
            "Validation error: temperature must be between -50 and 150",
            "Request failed with status 500"
        ]
        for msg in errors:
            error = ErrorResponse(detail=msg)
            self.assertEqual(error.detail, msg)

    def test_error_with_special_chars(self):
        """Should handle special characters in errors"""
        error_msg = "Error in file /path/to/file.py:42 - Invalid JSON: {\"key\": \"value\"}"
        error = ErrorResponse(detail=error_msg)
        self.assertEqual(error.detail, error_msg)


if __name__ == '__main__':
    unittest.main()
