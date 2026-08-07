import time
import math
import requests
import os
import random
from datetime import datetime, timezone
from uuid import uuid4

from . import logger

# Module-level defaults so functions and importing tests have predictable state
SERVER_URL = os.environ.get("BACKEND_API_URL", "http://localhost:8000/api/v1/readings")

# Simulation state defaults
temperature = 22.0
outside_temp = 30
cooling_on = False
humidity = 50.0
# internal toggle to create small deterministic humidity oscillation
humidity_phase = False

def extract_simulated_payload() -> dict:
   
    # Heat exchange model
    global temperature
    global outside_temp
    temperature += (outside_temp - temperature) * 0.05
    
    # Cooling system effect
    global cooling_on
    if cooling_on:
        temperature -= 0.3
    
    # Decide cooling
    if temperature > 26:
        cooling_on = True
    elif temperature < 24:
        cooling_on = False
    
    # Simulate humidity fluctuation with a small deterministic oscillation
    global humidity
    global humidity_phase
    humidity_phase = not humidity_phase
    phase_val = 0.2 if humidity_phase else -0.2
    humidity += (50 - humidity) * 0.02 + (0.1 if cooling_on else -0.05) + phase_val + random.uniform(-0.05, 0.05)
    humidity = max(30, min(80, humidity))
    
    event_id = str(uuid4())

    payload = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "temperature": round(temperature, 2),
        "humidity": round(humidity, 2)
    }

    headers = {
        "Idempotency-Key": event_id,
    }    
    return payload, headers

def send_sensor_data(payload: dict, headers: dict, timeout_s: int):
    try:
        logger.info(f"Sending sensor reading: temp={payload.get('temperature')}C, humidity={payload.get('humidity')}%")
        response = requests.post(SERVER_URL, json=payload, headers=headers, timeout=timeout_s)
        if response.status_code in [200, 202]:
            logger.info(f"Sensor reading sent successfully with status {response.status_code}")
        else:
            logger.error(f"Server error ({response.status_code}): {payload}")
    except requests.exceptions.RequestException as e:
        logger.exception(f"Connection error: {str(e)}")
    
if __name__ == "__main__":

    logger.info(f"Connecting to backend API at: {SERVER_URL}")
    logger.info("Edge server simulator starting - generating sensor data")

    # run in a loop to get continuously sensor values
    while True:
        # get simulated values from sensor
        payload, headers = extract_simulated_payload()

        # send sensor data to backend service
        send_sensor_data(payload=payload, headers=headers, timeout_s=5)

        time.sleep(3)
