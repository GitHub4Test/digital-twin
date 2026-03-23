import time
import math
import requests
import os
from datetime import datetime
from . import logger

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
    
    # Simulate humidity fluctuation
    global humidity
    humidity += (50 - humidity) * 0.02 + (0.1 if cooling_on else -0.05)
    humidity = max(30, min(80, humidity))
    
    payload = {
        "timestamp": datetime.now().isoformat(),
        "temperature": round(temperature, 2),
        "humidity": round(humidity, 2)
    }
    return payload

def send_sensor_data(payload: dict, timeout_s: int):
    try:
        response = requests.post(SERVER_URL, json=payload, timeout=timeout_s)
        if response.status_code == 200:
            logger.info(f"Sensor reading sent: {payload}")
        else:
            logger.error(f"Server error ({response.status_code}): {payload}")
    except requests.exceptions.RequestException as e:
        logger.exception(f"Connection error: {str(e)}")
    
if __name__ == "__main__":

    # Backend API service URL - configurable via environment variable
    SERVER_URL = os.environ.get("BACKEND_API_URL", "http://localhost:8000/update")

    temperature = 22.0
    outside_temp = 30
    cooling_on = False
    humidity = 50.0    
    logger.info(f"Connecting to backend API at: {SERVER_URL}")

    # run in a loop to get continuously sensor values
    while True:
        # get simulated values from sensor
        payload = extract_simulated_payload()

        # send sensor data to backend service
        send_sensor_data(payload, 5)

        time.sleep(3)
