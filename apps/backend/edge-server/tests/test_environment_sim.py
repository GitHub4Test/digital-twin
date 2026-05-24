"""
Environment Simulation Unit Tests - Backend Edge Server
Tests for environment_sim.py covering temperature/humidity simulation and sensor data transmission
"""

import sys
import os
import unittest
import requests
from datetime import datetime
from unittest.mock import patch, MagicMock

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../apps/backend/edge-server/src'))
from edge_server import environment_sim


class TestEnvironmentSim(unittest.TestCase):
    """Test suite for environment simulation functions"""

    def setUp(self):
        """Reset global state before each test"""
        environment_sim.temperature = 20.0
        environment_sim.outside_temp = 25
        environment_sim.cooling_on = False
        environment_sim.humidity = 50.0
        environment_sim.humidity_phase = False

    def test_extract_simulated_payload_returns_dict_with_required_fields(self):
        """Payload should contain timestamp, temperature, and humidity"""
        payload = environment_sim.extract_simulated_payload()
        self.assertIn("timestamp", payload)
        self.assertIn("temperature", payload)
        self.assertIn("humidity", payload)

    def test_extract_simulated_payload_has_correct_types(self):
        """Payload values should have correct types"""
        payload = environment_sim.extract_simulated_payload()
        self.assertIsInstance(payload["timestamp"], str)
        self.assertIsInstance(payload["temperature"], float)
        self.assertIsInstance(payload["humidity"], float)

    def test_extract_simulated_payload_timestamp_is_iso_format(self):
        """Timestamp should be ISO format"""
        payload = environment_sim.extract_simulated_payload()
        try:
            datetime.fromisoformat(payload["timestamp"])
            timestamp_valid = True
        except ValueError:
            timestamp_valid = False
        self.assertTrue(timestamp_valid)

    def test_temperature_converges_to_outside_temp(self):
        """Temperature should gradually converge toward outside temperature"""
        environment_sim.temperature = 20.0
        environment_sim.outside_temp = 30
        environment_sim.cooling_on = False
        
        payload1 = environment_sim.extract_simulated_payload()
        initial_temp = payload1["temperature"]
        
        for _ in range(50):
            environment_sim.extract_simulated_payload()
        
        final_temp = environment_sim.temperature
        self.assertGreater(final_temp, initial_temp)
        self.assertLess(final_temp, environment_sim.outside_temp)

    def test_cooling_activates_at_26_degrees(self):
        """Cooling should turn on when temp exceeds 26°C"""
        environment_sim.temperature = 26.5
        environment_sim.outside_temp = 30
        environment_sim.cooling_on = False
        
        environment_sim.extract_simulated_payload()
        self.assertTrue(environment_sim.cooling_on)

    def test_cooling_deactivates_below_24_degrees(self):
        """Cooling should turn off when temp drops below 24°C"""
        environment_sim.temperature = 23.5
        environment_sim.outside_temp = 30
        environment_sim.cooling_on = True
        
        environment_sim.extract_simulated_payload()
        self.assertFalse(environment_sim.cooling_on)

    def test_cooling_reduces_temperature(self):
        """When cooling is on, temperature should decrease"""
        environment_sim.temperature = 27.0
        environment_sim.outside_temp = 30
        environment_sim.cooling_on = True
        
        payload = environment_sim.extract_simulated_payload()
        self.assertLess(payload["temperature"], 27.0)

    def test_humidity_bounded_between_30_and_80(self):
        """Humidity should stay within 30-80% range"""
        for _ in range(100):
            payload = environment_sim.extract_simulated_payload()
            self.assertGreaterEqual(payload["humidity"], 30.0)
            self.assertLessEqual(payload["humidity"], 80.0)

    def test_humidity_oscillates_with_phase(self):
        """Humidity should show oscillation due to humidity_phase toggle"""
        environment_sim.temperature = 25.0
        environment_sim.outside_temp = 30
        environment_sim.humidity = 50.0
        
        humidity_values = []
        for _ in range(10):
            payload = environment_sim.extract_simulated_payload()
            humidity_values.append(payload["humidity"])
        
        self.assertTrue(any(h > 50.0 for h in humidity_values))
        self.assertTrue(any(h < 50.0 for h in humidity_values))

    def test_temperature_rounded_to_2_decimals(self):
        """Temperature should be rounded to 2 decimal places"""
        payload = environment_sim.extract_simulated_payload()
        temp_str = str(payload["temperature"])
        decimal_places = len(temp_str.split('.')[-1]) if '.' in temp_str else 0
        self.assertLessEqual(decimal_places, 2)

    def test_humidity_rounded_to_2_decimals(self):
        """Humidity should be rounded to 2 decimal places"""
        payload = environment_sim.extract_simulated_payload()
        humidity_str = str(payload["humidity"])
        decimal_places = len(humidity_str.split('.')[-1]) if '.' in humidity_str else 0
        self.assertLessEqual(decimal_places, 2)

    @patch('edge_server.environment_sim.requests.post')
    def test_send_sensor_data_success(self, mock_post):
        """Should successfully send sensor data when status 200"""
        mock_post.return_value.status_code = 200
        payload = {"temperature": 25.0, "humidity": 50.0, "timestamp": datetime.now().isoformat()}
        
        environment_sim.send_sensor_data(payload, timeout_s=5)
        
        mock_post.assert_called_once_with(
            environment_sim.SERVER_URL,
            json=payload,
            timeout=5
        )

    @patch('edge_server.environment_sim.requests.post')
    def test_send_sensor_data_server_error(self, mock_post):
        """Should handle server errors gracefully"""
        mock_post.return_value.status_code = 500
        payload = {"temperature": 25.0, "humidity": 50.0}
        
        environment_sim.send_sensor_data(payload, timeout_s=5)
        
        mock_post.assert_called_once()

    @patch('edge_server.environment_sim.requests.post')
    def test_send_sensor_data_connection_error(self, mock_post):
        """Should handle connection errors without raising"""
        mock_post.side_effect = requests.exceptions.ConnectionError("Connection failed")
        payload = {"temperature": 25.0, "humidity": 50.0}
        
        try:
            environment_sim.send_sensor_data(payload, timeout_s=5)
        except Exception as e:
            self.fail(f"send_sensor_data raised {e} on connection error")

    @patch('edge_server.environment_sim.requests.post')
    def test_send_sensor_data_timeout_error(self, mock_post):
        """Should handle timeout errors without raising"""
        mock_post.side_effect = requests.exceptions.Timeout("Request timed out")
        payload = {"temperature": 25.0, "humidity": 50.0}
        
        try:
            environment_sim.send_sensor_data(payload, timeout_s=5)
        except Exception as e:
            self.fail(f"send_sensor_data raised {e} on timeout")

    @patch('edge_server.environment_sim.requests.post')
    def test_send_sensor_data_http_error(self, mock_post):
        """Should handle HTTP errors without raising"""
        mock_post.side_effect = requests.exceptions.HTTPError("HTTP error")
        payload = {"temperature": 25.0, "humidity": 50.0}
        
        try:
            environment_sim.send_sensor_data(payload, timeout_s=5)
        except Exception as e:
            self.fail(f"send_sensor_data raised {e} on HTTP error")

    @patch('edge_server.environment_sim.requests.post')
    def test_send_sensor_data_request_exception(self, mock_post):
        """Should handle general request exceptions"""
        mock_post.side_effect = requests.exceptions.RequestException("Generic error")
        payload = {"temperature": 25.0, "humidity": 50.0}
        
        try:
            environment_sim.send_sensor_data(payload, timeout_s=5)
        except Exception as e:
            self.fail(f"send_sensor_data raised {e}")

    @patch('edge_server.environment_sim.requests.post')
    def test_send_sensor_data_with_timeout_parameter(self, mock_post):
        """Should pass correct timeout to requests.post"""
        mock_post.return_value.status_code = 200
        payload = {"temperature": 25.0, "humidity": 50.0}
        
        environment_sim.send_sensor_data(payload, timeout_s=10)
        
        call_kwargs = mock_post.call_args[1]
        self.assertEqual(call_kwargs['timeout'], 10)

    @patch('edge_server.environment_sim.requests.post')
    def test_send_sensor_data_uses_server_url(self, mock_post):
        """Should use SERVER_URL from module"""
        mock_post.return_value.status_code = 200
        payload = {"temperature": 25.0, "humidity": 50.0}
        
        environment_sim.send_sensor_data(payload, timeout_s=5)
        
        call_url = mock_post.call_args[0][0]
        self.assertEqual(call_url, environment_sim.SERVER_URL)

    @patch('edge_server.environment_sim.requests.post')
    def test_send_sensor_data_status_code_other_than_200(self, mock_post):
        """Should handle non-200 status codes"""
        for status_code in [201, 400, 404, 500, 502, 503]:
            mock_post.return_value.status_code = status_code
            payload = {"temperature": 25.0, "humidity": 50.0}
            
            try:
                environment_sim.send_sensor_data(payload, timeout_s=5)
            except Exception as e:
                self.fail(f"send_sensor_data raised {e} for status {status_code}")


if __name__ == '__main__':
    unittest.main()
