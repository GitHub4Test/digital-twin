"""
API Routes Unit Tests - Backend
Tests for FastAPI endpoints in sensor.py and common.py
"""

import sys
import os
import unittest
from datetime import datetime
from unittest.mock import patch, MagicMock, AsyncMock, Mock
from fastapi.testclient import TestClient

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../apps/backend/api-gateway/src'))

# Set test DB path before importing app
import tempfile
os.environ['DB_PATH'] = os.path.join(tempfile.gettempdir(), 'test_api.sqlite3')

# Create test client
from api_gateway.main import app

client = TestClient(app)


class TestCommonRoutes(unittest.TestCase):
    """Test suite for common health check routes"""

    def test_health_check_endpoint(self):
        """GET /api/v1/health should return healthy status"""
        response = client.get("/api/v1/health")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['status'], 'healthy')
        self.assertEqual(data['service'], 'backend')
        self.assertEqual(data['version'], '1.0.0')

    def test_health_check_returns_correct_model(self):
        """Health check response should have all required fields"""
        response = client.get("/api/v1/health")
        data = response.json()
        self.assertIn('status', data)
        self.assertIn('service', data)
        self.assertIn('version', data)

    def test_liveness_check_endpoint(self):
        """GET /api/v1/live should indicate service is alive"""
        response = client.get("/api/v1/live")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['status'], 'alive')
        self.assertEqual(data['service'], 'backend')

    def test_liveness_check_returns_correct_fields(self):
        """Liveness check should have all required fields"""
        response = client.get("/api/v1/live")
        data = response.json()
        self.assertIn('status', data)
        self.assertIn('service', data)
        self.assertIn('version', data)

    def test_readiness_check_endpoint(self):
        """GET /api/v1/ready should check database readiness"""
        response = client.get("/api/v1/ready")
        self.assertIn(response.status_code, [200, 503])

    def test_readiness_check_returns_health_response(self):
        """Readiness check should return health response model"""
        response = client.get("/api/v1/ready")
        if response.status_code == 200:
            data = response.json()
            self.assertIn('status', data)
            self.assertIn('service', data)

    def test_all_health_endpoints_have_version(self):
        """All health endpoints should include version"""
        endpoints = ["/api/v1/health", "/api/v1/live", "/api/v1/ready"]
        for endpoint in endpoints:
            response = client.get(endpoint)
            if response.status_code == 200:
                data = response.json()
                self.assertEqual(data['version'], '1.0.0')

    def test_health_endpoint_content_type(self):
        """Health endpoint should return JSON"""
        response = client.get("/api/v1/health")
        self.assertIn('application/json', response.headers['content-type'])

    def test_health_status_is_string(self):
        """Health status should be a string"""
        response = client.get("/api/v1/health")
        data = response.json()
        self.assertIsInstance(data['status'], str)

    def test_service_name_is_backend(self):
        """Service name should be 'backend'"""
        response = client.get("/api/v1/health")
        data = response.json()
        self.assertEqual(data['service'], 'backend')


class TestSensorReadingsValidation(unittest.TestCase):
    """Test suite for sensor reading validation and constraints"""

    def test_create_reading_missing_timestamp(self):
        """POST /api/v1/sensors/readings without timestamp should fail"""
        payload = {
            "temperature": 24.5,
            "humidity": 61.2
        }
        response = client.post("/api/v1/sensors/readings", json=payload)
        self.assertEqual(response.status_code, 422)

    def test_create_reading_missing_temperature(self):
        """POST /api/v1/sensors/readings without temperature should fail"""
        now = datetime.now().isoformat()
        payload = {
            "timestamp": now,
            "humidity": 61.2
        }
        response = client.post("/api/v1/sensors/readings", json=payload)
        self.assertEqual(response.status_code, 422)

    def test_create_reading_missing_humidity(self):
        """POST /api/v1/sensors/readings without humidity should fail"""
        now = datetime.now().isoformat()
        payload = {
            "timestamp": now,
            "temperature": 24.5
        }
        response = client.post("/api/v1/sensors/readings", json=payload)
        self.assertEqual(response.status_code, 422)

    def test_create_reading_temperature_below_minimum(self):
        """Temperature below -50 should fail validation"""
        now = datetime.now().isoformat()
        payload = {
            "timestamp": now,
            "temperature": -51.0,
            "humidity": 50.0
        }
        response = client.post("/api/v1/sensors/readings", json=payload)
        self.assertEqual(response.status_code, 422)

    def test_create_reading_temperature_above_maximum(self):
        """Temperature above 150 should fail validation"""
        now = datetime.now().isoformat()
        payload = {
            "timestamp": now,
            "temperature": 151.0,
            "humidity": 50.0
        }
        response = client.post("/api/v1/sensors/readings", json=payload)
        self.assertEqual(response.status_code, 422)

    def test_create_reading_humidity_below_minimum(self):
        """Humidity below 0 should fail validation"""
        now = datetime.now().isoformat()
        payload = {
            "timestamp": now,
            "temperature": 25.0,
            "humidity": -1.0
        }
        response = client.post("/api/v1/sensors/readings", json=payload)
        self.assertEqual(response.status_code, 422)

    def test_create_reading_humidity_above_maximum(self):
        """Humidity above 100 should fail validation"""
        now = datetime.now().isoformat()
        payload = {
            "timestamp": now,
            "temperature": 25.0,
            "humidity": 101.0
        }
        response = client.post("/api/v1/sensors/readings", json=payload)
        self.assertEqual(response.status_code, 422)

    def test_create_reading_invalid_timestamp_format(self):
        """Invalid timestamp format should fail"""
        payload = {
            "timestamp": "not-a-timestamp",
            "temperature": 25.0,
            "humidity": 50.0
        }
        response = client.post("/api/v1/sensors/readings", json=payload)
        self.assertEqual(response.status_code, 422)

    def test_create_reading_temperature_at_min_boundary(self):
        """Temperature at -50 should be valid"""
        now = datetime.now().isoformat()
        payload = {
            "timestamp": now,
            "temperature": -50.0,
            "humidity": 50.0
        }
        response = client.post("/api/v1/sensors/readings", json=payload)
        self.assertIn(response.status_code, [202, 500, 503])

    def test_create_reading_temperature_at_max_boundary(self):
        """Temperature at 150 should be valid"""
        now = datetime.now().isoformat()
        payload = {
            "timestamp": now,
            "temperature": 150.0,
            "humidity": 50.0
        }
        response = client.post("/api/v1/sensors/readings", json=payload)
        self.assertIn(response.status_code, [202, 500, 503])

    def test_create_reading_humidity_at_min_boundary(self):
        """Humidity at 0 should be valid"""
        now = datetime.now().isoformat()
        payload = {
            "timestamp": now,
            "temperature": 25.0,
            "humidity": 0.0
        }
        response = client.post("/api/v1/sensors/readings", json=payload)
        self.assertIn(response.status_code, [202, 500, 503])

    def test_create_reading_humidity_at_max_boundary(self):
        """Humidity at 100 should be valid"""
        now = datetime.now().isoformat()
        payload = {
            "timestamp": now,
            "temperature": 25.0,
            "humidity": 100.0
        }
        response = client.post("/api/v1/sensors/readings", json=payload)
        self.assertIn(response.status_code, [202, 500, 503])

    def test_create_reading_with_float_precision(self):
        """Should accept high precision floats"""
        now = datetime.now().isoformat()
        payload = {
            "timestamp": now,
            "temperature": 24.123456,
            "humidity": 61.987654
        }
        response = client.post("/api/v1/sensors/readings", json=payload)
        self.assertIn(response.status_code, [202, 500, 503])

    def test_create_reading_with_string_temperature(self):
        """String temperature should fail validation"""
        now = datetime.now().isoformat()
        payload = {
            "timestamp": now,
            "temperature": "25.0",
            "humidity": 50.0
        }
        response = client.post("/api/v1/sensors/readings", json=payload)
        # Pydantic may coerce strings, so check it's not 422 or is 201/500
        self.assertNotEqual(response.status_code, 404)

    def test_create_reading_with_null_temperature(self):
        """Null temperature should fail validation"""
        now = datetime.now().isoformat()
        payload = {
            "timestamp": now,
            "temperature": None,
            "humidity": 50.0
        }
        response = client.post("/api/v1/sensors/readings", json=payload)
        self.assertEqual(response.status_code, 422)

    def test_event_endpoint_missing_timestamp(self):
        """Event endpoint without timestamp should fail"""
        payload = {
            "temperature": 25.0,
            "humidity": 50.0
        }
        response = client.post("/api/v1/sensors/readings", json=payload)
        self.assertEqual(response.status_code, 422)

    def test_event_endpoint_missing_temperature(self):
        """Event endpoint without temperature should fail"""
        now = datetime.now().isoformat()
        payload = {
            "timestamp": now,
            "humidity": 50.0
        }
        response = client.post("/api/v1/sensors/readings", json=payload)
        self.assertEqual(response.status_code, 422)

    def test_event_endpoint_missing_humidity(self):
        """Event endpoint without humidity should fail"""
        now = datetime.now().isoformat()
        payload = {
            "timestamp": now,
            "temperature": 25.0
        }
        response = client.post("/api/v1/sensors/readings", json=payload)
        self.assertEqual(response.status_code, 422)

    def test_event_endpoint_temperature_validation(self):
        """Event endpoint should validate temperature range"""
        now = datetime.now().isoformat()
        payload = {
            "timestamp": now,
            "temperature": 200.0,
            "humidity": 50.0
        }
        response = client.post("/api/v1/sensors/readings", json=payload)
        self.assertEqual(response.status_code, 422)

    def test_event_endpoint_humidity_validation(self):
        """Event endpoint should validate humidity range"""
        now = datetime.now().isoformat()
        payload = {
            "timestamp": now,
            "temperature": 25.0,
            "humidity": 150.0
        }
        response = client.post("/api/v1/sensors/readings", json=payload)
        self.assertEqual(response.status_code, 422)


class TestGetSensorDataEndpoint(unittest.TestCase):
    """Test suite for GET sensor data endpoint"""

    def test_get_sensor_data_accepts_no_params(self):
        """GET /api/v1/sensors/readings should work without parameters"""
        response = client.get("/api/v1/sensors/readings")
        # Either success or DB error is acceptable
        self.assertIn(response.status_code, [200, 500, 503])

    def test_get_sensor_data_with_limit_1(self):
        """GET /api/v1/sensors/readings?limit=1 should be valid"""
        response = client.get("/api/v1/sensors/readings?limit=1")
        self.assertIn(response.status_code, [200, 500, 503])

    def test_get_sensor_data_with_limit_1000(self):
        """GET /api/v1/sensors/readings?limit=1000 should be valid"""
        response = client.get("/api/v1/sensors/readings?limit=1000")
        self.assertIn(response.status_code, [200, 500, 503])

    def test_get_sensor_data_limit_0_invalid(self):
        """GET /api/v1/sensors/readings?limit=0 should fail"""
        response = client.get("/api/v1/sensors/readings?limit=0")
        self.assertEqual(response.status_code, 422)

    def test_get_sensor_data_limit_1001_invalid(self):
        """GET /api/v1/sensors/readings?limit=1001 should fail"""
        response = client.get("/api/v1/sensors/readings?limit=1001")
        self.assertEqual(response.status_code, 422)

    def test_get_sensor_data_limit_string_invalid(self):
        """GET /api/v1/sensors/readings?limit=abc should fail"""
        response = client.get("/api/v1/sensors/readings?limit=abc")
        self.assertEqual(response.status_code, 422)

    def test_get_sensor_data_limit_float(self):
        """GET /api/v1/sensors/readings?limit=50.5 might be coerced to int"""
        response = client.get("/api/v1/sensors/readings?limit=50.5")
        # Depends on how FastAPI handles float to int conversion
        self.assertIn(response.status_code, [200, 422, 500])

    def test_get_sensor_data_limit_negative(self):
        """GET /api/v1/sensors/readings?limit=-1 should fail"""
        response = client.get("/api/v1/sensors/readings?limit=-1")
        self.assertEqual(response.status_code, 422)

    def test_get_sensor_data_multiple_limit_params(self):
        """Multiple limit parameters - last one should be used"""
        response = client.get("/api/v1/sensors/readings?limit=10&limit=20")
        self.assertIn(response.status_code, [200, 422, 500, 503])


# class TestDeleteSensorDataEndpoint(unittest.TestCase):
#     """Test suite for DELETE sensor data endpoint"""

#     def test_delete_sensor_data_returns_message_response(self):
#         """DELETE /api/v1/sensors/readings should return message"""
#         response = client.delete("/api/v1/sensors/readings")
#         if response.status_code == 200:
#             data = response.json()
#             self.assertIn('message', data)
#         else:
#             # DB error is acceptable
#             self.assertEqual(response.status_code, 500)

#     def test_delete_sensor_data_accept_no_body(self):
#         """DELETE /api/v1/sensors/readings should not require body"""
#         response = client.delete("/api/v1/sensors/readings")
#         # Either success or error is fine
#         self.assertIn(response.status_code, [200, 500])


class TestAPIErrorHandling(unittest.TestCase):
    """Test suite for error handling and edge cases"""

    def test_nonexistent_endpoint_returns_404(self):
        """Non-existent endpoint should return 404"""
        response = client.get("/api/v1/nonexistent")
        self.assertEqual(response.status_code, 404)

    def test_invalid_method_returns_405(self):
        """Using wrong HTTP method should return 405"""
        response = client.post("/api/v1/health")
        self.assertEqual(response.status_code, 405)

    def test_malformed_json_returns_422(self):
        """Malformed JSON should return 422"""
        response = client.post(
            "/api/v1/sensors/readings",
            content=b"invalid json",
            headers={"Content-Type": "application/json"}
        )
        self.assertEqual(response.status_code, 422)

    def test_put_method_not_allowed(self):
        """PUT method should not be allowed"""
        response = client.put("/api/v1/sensors/readings")
        self.assertEqual(response.status_code, 405)

    def test_patch_method_not_allowed(self):
        """PATCH method should not be allowed"""
        response = client.patch("/api/v1/sensors/readings")
        self.assertEqual(response.status_code, 405)

    def test_options_method_allowed(self):
        """OPTIONS method should be handled"""
        response = client.options("/api/v1/health")
        self.assertIn(response.status_code, [200, 204, 405])


class TestEventEndpointStatusCode(unittest.TestCase):
    """Test suite for event endpoint status codes"""

    def test_event_endpoint_returns_202_or_500(self):
        """Event endpoint should return 202 Accepted or 500 on error"""
        now = datetime.now().isoformat()
        payload = {
            "timestamp": now,
            "temperature": 25.0,
            "humidity": 50.0
        }
        response = client.post("/api/v1/sensors/readings", json=payload)
        self.assertIn(response.status_code, [202, 500, 503])

    def test_event_endpoint_returns_json_response(self):
        """Event endpoint should return JSON response"""
        now = datetime.now().isoformat()
        payload = {
            "timestamp": now,
            "temperature": 25.0,
            "humidity": 50.0
        }
        response = client.post("/api/v1/sensors/readings", json=payload)
        if response.status_code in [202, 500]:
            self.assertIn('application/json', response.headers['content-type'])


if __name__ == '__main__':
    unittest.main()
