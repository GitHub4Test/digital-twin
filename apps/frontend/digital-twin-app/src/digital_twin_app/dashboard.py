import streamlit as st
import logging
import os
import requests
import pandas as pd
import os
import sys
import pybreaker
from digital_twin_app.twin_model import predict_next
from digital_twin_app.resilience import fetch_backend_data, BackendReadError


log_level = os.getenv("LOG_LEVEL", "INFO").upper()

logging.basicConfig(
    level=log_level,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
    handlers=[
        logging.StreamHandler()          # only stdout/stderr
    ]
)

logger = logging.getLogger("digital_twin_app")
logger.info("Dashboard logger initialized")
logger.info("Digital Twin Dashboard application starting")

st.title("🌍 Raspberry Pi 4 Digital Twin")
logger.info("Dashboard UI initialized")

def get_data(timeout_s: int = 5):
    """
    Fetches data from the backend API with error handling, retries, and circuit breaker.
    @param timeout_s: Timeout in seconds for the API request (default: 5)
    @return: List of data received from the backend, or an empty list if an error occurs
    """

    # Get backend URL from environment variable, default to localhost for local development    
    BACKEND_API_URL = os.environ.get("BACKEND_API_URL", "http://localhost:8000/api/v1/readings")
    logger.info(f"Backend API URL: {BACKEND_API_URL}")
    
    try:
        logger.info(f"Requesting data from backend with timeout={timeout_s}s")
        data = fetch_backend_data(BACKEND_API_URL, timeout_s)
        logger.info(f"Successfully received {len(data)} readings from backend")
        return data
    except pybreaker.CircuitBreakerError:
        logger.error("Circuit breaker is open. Backend temporarily unavailable.")
        st.warning("Backend temporarily unavailable. Please try again shortly.")
        st.info(f"Connecting to: {BACKEND_API_URL}")
        return []
    except BackendReadError as e:
        logger.error(f"Backend read failed after retries: {str(e)}")
        st.error(f"Backend read failed after retries: {str(e)}")
        st.info(f"Connecting to: {BACKEND_API_URL}")
        return []
    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to connect to backend: {str(e)}")
        st.error(f"Failed to connect to backend: {str(e)}")
        st.info(f"Connecting to: {BACKEND_API_URL}")
        return []

# Function to display current and predicted temperature
def display_current_and_predicted_temparature(current_received_data):
    """
    Displays the current temperature and humidity data along with the predicted next temperature.
    @param current_received_data: List of data received from the backend, expected to contain timestamp, temperature, and humidity
    @return: Predicted next temperature
    """
    
    if not current_received_data:
        logger.warning("No sensor data available to display")
        st.warning("No sensor data available.")
        return None

    logger.info(f"Displaying data for {len(current_received_data)} sensor readings")

    df = pd.DataFrame(current_received_data)
    logger.info(f"DataFrame created with {len(df)} rows")

    expected_columns = [
        "event_id",
        "timestamp",
        "temperature",
        "humidity",
        "status",
    ]

    for col in expected_columns:
        if col not in df.columns:
            df[col] = None    
    
    if not df.empty:
        logger.info("Processing sensor data for display")
        df = df.sort_values("timestamp")

        st.line_chart(df["temperature"])
        logger.info("Temperature chart rendered")
        
        st.line_chart(df["humidity"])
        logger.info("Humidity chart rendered")

        current_temp = df["temperature"].iloc[-1]
        logger.info(f"Current temperature: {current_temp}C")
        
        prediction = predict_next(df["temperature"].tolist())

        st.metric("Current Temperature", current_temp)
        st.metric("Predicted Next Temperature", prediction)

        latest_status = df["status"].iloc[-1]
        logger.info(f"Latest reading status: {latest_status}")

        if latest_status == "PROCESSED":
            logger.info("Latest reading has been processed")
            st.success("Latest reading processed successfully")

        elif latest_status == "RECEIVED":
            logger.info("Latest reading is waiting for processing")
            st.warning("Latest reading waiting for processing")
    
        elif latest_status == "FAILED":
            logger.error("Latest reading processing failed")
            st.error("Latest reading processing failed")

        st.subheader("Latest Sensor Readings")
        logger.info("Displaying latest sensor readings table")

        display_df = df.sort_values(
            "timestamp",
            ascending=False,
        ) 
        
        st.dataframe(
            display_df[
                [
                    "timestamp",
                    "temperature",
                    "humidity",
                    "status",
                ]
            ],
            use_container_width=True,
        )

        if current_temp > 30:
            logger.warning(f"Temperature warning: {current_temp}C exceeds threshold of 30C")
            st.error("⚠ Overheating Detected")
                    
        return prediction

# receive data from backend service
logger.info("Dashboard retrieving data from backend")
data = get_data(5)

# display graph having current temp and next predicted temparature
logger.info("Dashboard rendering visualization")
prediction = display_current_and_predicted_temparature(data)
logger.info(f"Dashboard update complete. Predicted next temp: {prediction}")

