"""
Environment Simulation Unit Tests - Backend Edge Server
Tests for environment_sim.py covering temperature/humidity simulation and sensor data transmission
"""

import os
import sys
import unittest
from datetime import datetime
from unittest.mock import MagicMock, patch
from uuid import uuid4

import requests

from edge_server.environment_sim import (
    SERVER_URL,
    SensorApiClient,
    SensorSimulator,
    SensorState,
)

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../apps/backend/edge-server"))

class TestEnvironmentSim(unittest.TestCase):
    """Test suite for environment simulation."""

    def setUp(self):
        self._state = SensorState(
            temperature=20.0,
            outside_temperature=25.0,
            cooling_on=False,
            humidity=50.0,
            humidity_phase=False,
        )

        self._sensor_simulator = SensorSimulator(self._state)

        self.headers = {
            "Idempotency-Key": str(uuid4()),
        }

        self._sensor_client = SensorApiClient(
            server_url=SERVER_URL,
            timeout_s=10,
        )

    def tearDown(self):
        self._sensor_client.close()

    def test_generate_reading_returns_dict_with_required_fields(self):
        payload, _ = self._sensor_simulator.generate_reading()

        self.assertIn("timestamp", payload)
        self.assertIn("temperature", payload)
        self.assertIn("humidity", payload)

    def test_generate_reading_has_correct_types(self):
        payload, _ = self._sensor_simulator.generate_reading()

        self.assertIsInstance(payload["timestamp"], str)
        self.assertIsInstance(payload["temperature"], float)
        self.assertIsInstance(payload["humidity"], float)

    def test_generate_reading_timestamp_is_iso_format(self):
        payload, _ = self._sensor_simulator.generate_reading()

        timestamp = datetime.fromisoformat(payload["timestamp"])

        self.assertIsNotNone(timestamp.tzinfo)

    def test_generate_reading_returns_idempotency_header(self):
        _, headers = self._sensor_simulator.generate_reading()

        self.assertIn("Idempotency-Key", headers)
        self.assertTrue(headers["Idempotency-Key"])

    def test_temperature_converges_to_outside_temperature(self):
        self._state.temperature = 20.0
        self._state.outside_temperature = 30.0
        self._state.cooling_on = False

        payload, _ = self._sensor_simulator.generate_reading()
        initial_temperature = payload["temperature"]

        for _ in range(50):
            self._sensor_simulator.generate_reading()

        final_temperature = self._state.temperature

        self.assertGreater(
            final_temperature,
            initial_temperature,
        )
        self.assertLess(
            final_temperature,
            self._state.outside_temperature,
        )

    def test_cooling_activates_above_26_degrees(self):
        self._state.temperature = 26.5
        self._state.outside_temperature = 30.0
        self._state.cooling_on = False

        self._sensor_simulator.generate_reading()

        self.assertTrue(self._state.cooling_on)

    def test_cooling_deactivates_below_24_degrees(self):
        self._state.temperature = 23.5
        self._state.outside_temperature = 30.0
        self._state.cooling_on = True

        self._sensor_simulator.generate_reading()

        self.assertFalse(self._state.cooling_on)

    def test_cooling_reduces_temperature(self):
        self._state.temperature = 27.0
        self._state.outside_temperature = 27.0
        self._state.cooling_on = True

        payload, _ = self._sensor_simulator.generate_reading()

        self.assertLess(
            payload["temperature"],
            27.0,
        )

    def test_humidity_bounded_between_30_and_80(self):
        for _ in range(100):
            payload, _ = self._sensor_simulator.generate_reading()

            self.assertGreaterEqual(
                payload["humidity"],
                30.0,
            )
            self.assertLessEqual(
                payload["humidity"],
                80.0,
            )

    @patch(
        "edge_server.environment_sim.random.uniform",
        return_value=0.0,
    )
    def test_humidity_phase_toggles(self, _mock_random):
        initial_phase = self._state.humidity_phase

        self._sensor_simulator.generate_reading()

        self.assertNotEqual(
            self._state.humidity_phase,
            initial_phase,
        )

        self._sensor_simulator.generate_reading()

        self.assertEqual(
            self._state.humidity_phase,
            initial_phase,
        )

    def test_temperature_rounded_to_2_decimals(self):
        payload, _ = self._sensor_simulator.generate_reading()

        temperature = payload["temperature"]

        self.assertEqual(
            temperature,
            round(temperature, 2),
        )

    def test_humidity_rounded_to_2_decimals(self):
        payload, _ = self._sensor_simulator.generate_reading()

        humidity = payload["humidity"]

        self.assertEqual(
            humidity,
            round(humidity, 2),
        )

    @patch(
        "edge_server.environment_sim.requests.Session.post"
    )
    def test_send_reading_success(self, mock_post):
        response = MagicMock()
        response.status_code = 200
        response.raise_for_status.return_value = None
        mock_post.return_value = response

        payload = {
            "temperature": 25.0,
            "humidity": 50.0,
            "timestamp": datetime.now().isoformat(),
        }

        result = self._sensor_client.send_reading(
            payload,
            headers=self.headers,
        )

        self.assertTrue(result)

        mock_post.assert_called_once_with(
            SERVER_URL,
            json=payload,
            headers=self.headers,
            timeout=10,
        )

    @patch(
        "edge_server.environment_sim.requests.Session.post"
    )
    def test_send_reading_server_error(self, mock_post):
        response = MagicMock()
        response.status_code = 500
        response.raise_for_status.side_effect = (
            requests.exceptions.HTTPError(
                "500 Server Error"
            )
        )
        mock_post.return_value = response

        payload = {
            "temperature": 25.0,
            "humidity": 50.0,
        }

        result = self._sensor_client.send_reading(
            payload,
            headers=self.headers,
        )

        self.assertFalse(result)

    @patch(
        "edge_server.environment_sim.requests.Session.post"
    )
    def test_send_reading_connection_error(self, mock_post):
        mock_post.side_effect = (
            requests.exceptions.ConnectionError(
                "Connection failed"
            )
        )

        payload = {
            "temperature": 25.0,
            "humidity": 50.0,
        }

        result = self._sensor_client.send_reading(
            payload,
            headers=self.headers,
        )

        self.assertFalse(result)

    @patch(
        "edge_server.environment_sim.requests.Session.post"
    )
    def test_send_reading_timeout_error(self, mock_post):
        mock_post.side_effect = requests.exceptions.Timeout(
            "Request timed out"
        )

        payload = {
            "temperature": 25.0,
            "humidity": 50.0,
        }

        result = self._sensor_client.send_reading(
            payload,
            headers=self.headers,
        )

        self.assertFalse(result)

    @patch(
        "edge_server.environment_sim.requests.Session.post"
    )
    def test_send_reading_http_error(self, mock_post):
        mock_post.side_effect = requests.exceptions.HTTPError(
            "HTTP error"
        )

        payload = {
            "temperature": 25.0,
            "humidity": 50.0,
        }

        result = self._sensor_client.send_reading(
            payload,
            headers=self.headers,
        )

        self.assertFalse(result)

    @patch(
        "edge_server.environment_sim.requests.Session.post"
    )
    def test_send_reading_request_exception(self, mock_post):
        mock_post.side_effect = (
            requests.exceptions.RequestException(
                "Generic error"
            )
        )

        payload = {
            "temperature": 25.0,
            "humidity": 50.0,
        }

        result = self._sensor_client.send_reading(
            payload,
            headers=self.headers,
        )

        self.assertFalse(result)

    @patch(
        "edge_server.environment_sim.requests.Session.post"
    )
    def test_send_reading_uses_configured_timeout(
        self,
        mock_post,
    ):
        response = MagicMock()
        response.status_code = 200
        response.raise_for_status.return_value = None
        mock_post.return_value = response

        payload = {
            "temperature": 25.0,
            "humidity": 50.0,
        }

        self._sensor_client.send_reading(
            payload,
            headers=self.headers,
        )

        call_kwargs = mock_post.call_args.kwargs

        self.assertEqual(
            call_kwargs["timeout"],
            10,
        )

    @patch(
        "edge_server.environment_sim.requests.Session.post"
    )
    def test_send_reading_uses_server_url(
        self,
        mock_post,
    ):
        response = MagicMock()
        response.status_code = 200
        response.raise_for_status.return_value = None
        mock_post.return_value = response

        payload = {
            "temperature": 25.0,
            "humidity": 50.0,
        }

        self._sensor_client.send_reading(
            payload,
            headers=self.headers,
        )

        call_args = mock_post.call_args.args

        self.assertEqual(
            call_args[0],
            SERVER_URL,
        )

    @patch(
        "edge_server.environment_sim.requests.Session.post"
    )
    def test_send_reading_handles_http_error_statuses(
        self,
        mock_post,
    ):
        payload = {
            "temperature": 25.0,
            "humidity": 50.0,
        }

        for status_code in [400, 404, 500, 502, 503]:
            with self.subTest(status_code=status_code):
                response = MagicMock()
                response.status_code = status_code
                response.raise_for_status.side_effect = (
                    requests.exceptions.HTTPError(
                        f"{status_code} error"
                    )
                )

                mock_post.return_value = response

                result = self._sensor_client.send_reading(
                    payload,
                    headers=self.headers,
                )

                self.assertFalse(result)


if __name__ == "__main__":
    unittest.main()