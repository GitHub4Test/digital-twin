import os
import random
import time
from dataclasses import dataclass
from datetime import UTC, datetime
from uuid import uuid4

import requests

from . import logger

# Module-level defaults so functions and importing tests have predictable state
SERVER_URL = os.environ.get("BACKEND_API_URL", "http://localhost:8000/api/v1/sensor/readings")

# Simulation state defaults
@dataclass
class SensorState:
    temperature: float = 22.0
    outside_temperature: float = 30.0
    humidity: float = 50.0
    cooling_on: bool = False
    humidity_phase: bool = False # internal toggle to create small deterministic humidity oscillation

DEFAULT_TIMEOUT_S = 5
DEFAULT_INTERVAL_S = int(os.environ.get("SENSOR_INTERVAL_S", "15"))

class SensorSimulator:
    def __init__(self, state: SensorState | None = None):
        self._state = state or SensorState()

    def generate_reading(self) -> dict:

        self._update_temperature()
        self._update_cooling_state()
        self._update_humidity()

        event_id = str(uuid4())

        payload = {
            "timestamp": datetime.now(UTC).isoformat(),
            "temperature": round(self._state.temperature, 2),
            "humidity": round(self._state.humidity, 2),
        }

        headers = {
            "Idempotency-Key": event_id,
        }
        return payload, headers

    def _update_temperature(self) -> None:
        state = self._state

        # Heat exchange model
        state.temperature += (
            state.outside_temperature - state.temperature
        ) * 0.05

        # Cooling system effect
        if state.cooling_on:
            state.temperature -= 0.3

    def _update_cooling_state(self) -> None:
        # Decide cooling state based on temperature thresholds
        if self._state.temperature > 26:
            self._state.cooling_on = True
        elif self._state.temperature < 24:
            self._state.cooling_on = False

    def _update_humidity(self) -> None:
        # Simulate humidity fluctuation with a small deterministic oscillation
        state = self._state

        state.humidity_phase = not state.humidity_phase
        phase_value = 0.2 if state.humidity_phase else -0.2

        state.humidity += (
            (50 - state.humidity) * 0.02
            + (0.1 if state.cooling_on else -0.05)
            + phase_value
            + random.uniform(-0.05, 0.05)
        )

        state.humidity = max(
            30.0,
            min(80.0, state.humidity),
        )

class SensorApiClient:
    def __init__(self, server_url: str = SERVER_URL, timeout_s: int = 5):
        self._server_url = server_url
        self._timeout_s = timeout_s
        self._session = requests.Session()

    def send_reading(self, payload: dict, headers: dict) -> bool:

        logger.info(
            "Sending sensor reading: temp=%sC, humidity=%s%%",
            payload["temperature"],
            payload["humidity"],
        )

        try:
            response = self._session.post(
                self._server_url,
                json=payload,
                headers=headers,
                timeout=self._timeout_s,
            )

            response.raise_for_status()

        except requests.RequestException as exc:
            logger.exception(
                "Failed to send sensor reading: %s",
                exc,
            )
            return False

        logger.info(
            "Sensor reading sent successfully with status %s",
            response.status_code,
        )

        return True

    def close(self) -> None:
        self._session.close()

def run_simulator(
    server_url: str = SERVER_URL,
    interval_s: int = DEFAULT_INTERVAL_S,
) -> None:
    simulator = SensorSimulator()
    client = SensorApiClient(server_url)

    logger.info(
        "Connecting to backend API at: %s",
        server_url,
    )
    logger.info(
        "Edge server simulator starting - generating sensor data"
    )

    try:
        while True:
            payload, headers = simulator.generate_reading()
            client.send_reading(payload, headers)

            time.sleep(interval_s)

    except KeyboardInterrupt:
        logger.info("Edge server simulator stopped")

    finally:
        client.close()

if __name__ == "__main__":
    run_simulator()
