# Environment Simulation Unit Tests including negative test cases for the Backend Edge Server functions in environment_sim.py. 

import unittest
import requests
from datetime import datetime
from unittest.mock import patch
from apps.backend.edge_server.src import environment_sim

class TestEnvironmentSim(unittest.TestCase):
    def setUp(self):
        environment_sim.temperature = 20.0
        environment_sim.outside_temp = 25
        environment_sim.cooling_on = False
        environment_sim.humidity = 50.0
        environment_sim.humidity_phase = False

    @patch('apps.backend.edge_server.src.environment_sim.requests.post')
    def test_send_sensor_data_success(self, mock_post):
        mock_post.return_value.status_code = 200
        payload = {"temperature": 25.0, "humidity": 50.0}
        environment_sim.send_sensor_data(payload, timeout_s=5)
        mock_post.assert_called_once_with(environment_sim.SERVER_URL, json=payload, timeout=5)

    @patch('apps.backend.edge_server.src.environment_sim.requests.post')
    def test_send_sensor_data_server_error(self, mock_post):
        mock_post.return_value.status_code = 500
        payload = {"temperature": 25.0, "humidity": 50.0}
        environment_sim.send_sensor_data(payload, timeout_s=5)
        mock_post.assert_called_once_with(environment_sim.SERVER_URL, json=payload, timeout=5)

    @patch('apps.backend.edge_server.src.environment_sim.requests.post')
    def test_send_sensor_data_connection_error(self, mock_post):
        mock_post.side_effect = requests.exceptions.ConnectionError("Connection failed")
        payload = {"temperature": 25.0, "humidity": 50.0}
        environment_sim.send_sensor_data(payload, timeout_s=5)
        mock_post.assert_called_once_with(environment_sim.SERVER_URL, json=payload, timeout=5)

    def test_extract_simulated_payload(self):
        environment_sim.temperature = 22.0
        environment_sim.outside_temp = 30
        environment_sim.cooling_on = False
        environment_sim.humidity = 50.0

        payload = environment_sim.extract_simulated_payload()
        self.assertIn("timestamp", payload)
        self.assertIn("temperature", payload)
        self.assertIn("humidity", payload)
        self.assertIsInstance(payload["temperature"], float)
        self.assertIsInstance(payload["humidity"], float)

    def test_extract_simulated_payload_cooling_on(self):
        environment_sim.temperature = 27.0
        environment_sim.outside_temp = 30
        environment_sim.cooling_on = True
        environment_sim.humidity = 50.0

        payload = environment_sim.extract_simulated_payload()
        self.assertTrue(environment_sim.cooling_on)
        self.assertLess(payload["temperature"], 27.0)

    def test_extract_simulated_payload_cooling_off(self):
        environment_sim.temperature = 23.0
        environment_sim.outside_temp = 30
        environment_sim.cooling_on = False
        environment_sim.humidity = 50.0

        payload = environment_sim.extract_simulated_payload()
        self.assertFalse(environment_sim.cooling_on)
        self.assertGreater(payload["temperature"], 23.0)

    def test_extract_simulated_payload_humidity_limits(self):
        environment_sim.temperature = 25.0
        environment_sim.outside_temp = 30
        environment_sim.cooling_on = True
        environment_sim.humidity = 80.0

        payload = environment_sim.extract_simulated_payload()
        self.assertLessEqual(payload["humidity"], 80.0)

        environment_sim.humidity = 30.0
        payload = environment_sim.extract_simulated_payload()
        self.assertGreaterEqual(payload["humidity"], 30.0)

    def test_extract_simulated_payload_temperature_limits(self):
        environment_sim.temperature = 22.0
        environment_sim.outside_temp = 30
        environment_sim.cooling_on = False
        environment_sim.humidity = 50.0

        for _ in range(100):
            payload = environment_sim.extract_simulated_payload()
            self.assertGreaterEqual(payload["temperature"], 15.0)
            self.assertLessEqual(payload["temperature"], 35.0)

    def test_extract_simulated_payload_humidity_fluctuation(self):
        environment_sim.temperature = 25.0
        environment_sim.outside_temp = 30
        environment_sim.cooling_on = True
        environment_sim.humidity = 50.0

        humidity_values = []
        for _ in range(100):
            payload = environment_sim.extract_simulated_payload()
            humidity_values.append(payload["humidity"])

        self.assertTrue(any(h > 50.0 for h in humidity_values))
        self.assertTrue(any(h < 50.0 for h in humidity_values))

    def test_extract_simulated_payload_timestamp_format(self):
        environment_sim.temperature = 25.0
        environment_sim.outside_temp = 30
        environment_sim.cooling_on = False
        environment_sim.humidity = 50.0

        payload = environment_sim.extract_simulated_payload()
        try:
            datetime.fromisoformat(payload["timestamp"])
            timestamp_valid = True
        except ValueError:
            timestamp_valid = False

        self.assertTrue(timestamp_valid)

    def test_extract_simulated_payload_cooling_decision(self):
        environment_sim.temperature = 27.0
        environment_sim.outside_temp = 30
        environment_sim.cooling_on = False
        environment_sim.humidity = 50.0

        payload = environment_sim.extract_simulated_payload()
        self.assertTrue(environment_sim.cooling_on)

        environment_sim.temperature = 23.0
        payload = environment_sim.extract_simulated_payload()
        self.assertFalse(environment_sim.cooling_on)

    def test_send_sensor_data_timeout(self):
        with patch('apps.backend.edge_server.src.environment_sim.requests.post') as mock_post, \
             patch('apps.backend.edge_server.src.environment_sim.logger') as mock_logger:
            mock_post.side_effect = requests.exceptions.Timeout("Request timed out")
            payload = {"temperature": 25.0, "humidity": 50.0}
            result = environment_sim.send_sensor_data(payload, timeout_s=5)
            mock_post.assert_called_once_with(environment_sim.SERVER_URL, json=payload, timeout=5)
            mock_logger.exception.assert_called()
            self.assertIsNone(result)

    def test_send_sensor_data_invalid_url(self):
        with patch('apps.backend.edge_server.src.environment_sim.requests.post') as mock_post, \
             patch('apps.backend.edge_server.src.environment_sim.logger') as mock_logger:
            mock_post.side_effect = requests.exceptions.InvalidURL("Invalid URL")
            payload = {"temperature": 25.0, "humidity": 50.0}
            result = environment_sim.send_sensor_data(payload, timeout_s=5)
            mock_post.assert_called_once_with(environment_sim.SERVER_URL, json=payload, timeout=5)
            mock_logger.exception.assert_called()
            self.assertIsNone(result)

    def test_send_sensor_data_http_error(self):
        with patch('apps.backend.edge_server.src.environment_sim.requests.post') as mock_post, \
             patch('apps.backend.edge_server.src.environment_sim.logger') as mock_logger:
            mock_post.side_effect = requests.exceptions.HTTPError("HTTP error occurred")
            payload = {"temperature": 25.0, "humidity": 50.0}
            result = environment_sim.send_sensor_data(payload, timeout_s=5)
            mock_post.assert_called_once_with(environment_sim.SERVER_URL, json=payload, timeout=5)
            mock_logger.exception.assert_called()
            self.assertIsNone(result)

    def test_send_sensor_data_request_exception(self):
        with patch('apps.backend.edge_server.src.environment_sim.requests.post') as mock_post, \
             patch('apps.backend.edge_server.src.environment_sim.logger') as mock_logger:
            mock_post.side_effect = requests.exceptions.RequestException("General request exception")
            payload = {"temperature": 25.0, "humidity": 50.0}
            result = environment_sim.send_sensor_data(payload, timeout_s=5)
            mock_post.assert_called_once_with(environment_sim.SERVER_URL, json=payload, timeout=5)
            mock_logger.exception.assert_called()
            self.assertIsNone(result)

    def test_send_sensor_data_empty_payload(self):
        with patch('apps.backend.edge_server.src.environment_sim.requests.post') as mock_post:
            mock_post.return_value.status_code = 200
            payload = {}
            environment_sim.send_sensor_data(payload, timeout_s=5)
            mock_post.assert_called_once_with(environment_sim.SERVER_URL, json=payload, timeout=5)

    def test_send_sensor_data_large_payload(self):
        with patch('apps.backend.edge_server.src.environment_sim.requests.post') as mock_post:
            mock_post.return_value.status_code = 200
            payload = {"temperature": 25.0, "humidity": 50.0, "extra_data": "x" * 10000}
            environment_sim.send_sensor_data(payload, timeout_s=5)
            mock_post.assert_called_once_with(environment_sim.SERVER_URL, json=payload, timeout=5)  

    def test_send_sensor_data_non_json_payload(self):
        with patch('apps.backend.edge_server.src.environment_sim.requests.post') as mock_post:
            mock_post.return_value.status_code = 200
            payload = "This is not a JSON payload"
            environment_sim.send_sensor_data(payload, timeout_s=5)
            mock_post.assert_called_once_with(environment_sim.SERVER_URL, json=payload, timeout=5)

if __name__ == '__main__':
    unittest.main()    