import streamlit as st
import logging
import os
import requests
import pandas as pd
import os
import sys
from twin_model import predict_next


log_level = os.getenv("LOG_LEVEL", "INFO").upper()

logging.basicConfig(
    level=log_level,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
    handlers=[
        logging.StreamHandler()          # only stdout/stderr
    ]
)

logger = logging.getLogger("digital_twin_app")
logger.info("Logger initialized")

st.title("🌍 Raspberry Pi 4 Digital Twin")

def get_data(timeout_s: int = 5):

    # Get backend URL from environment variable, default to localhost for local development    
    BACKEND_API_URL = os.environ.get("BACKEND_API_URL", "http://localhost:8000/data")
    
    try:
        logger.info(f"Requesting data from backend: {BACKEND_API_URL}")
        response = requests.get(BACKEND_API_URL, timeout=timeout_s)
        response.raise_for_status()
        data = response.json()
        logger.info(f"Received data: {data}")
    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to connect to backend: {str(e)}")
        st.error(f"Failed to connect to backend: {str(e)}")
        st.info(f"Connecting to: {BACKEND_API_URL}")
        data = []
    
    return data

def display_current_and_predicted_temparature(current_received_data):

    df = pd.DataFrame(data, columns=["timestamp", "temperature", "humidity"])
    
    if not df.empty:
        df = df.sort_values("timestamp")
    
        st.line_chart(df["temperature"])
        st.line_chart(df["humidity"])
    
        current_temp = df["temperature"].iloc[-1]
        prediction = predict_next(df["temperature"].tolist())
    
        st.metric("Current Temperature", current_temp)
        st.metric("Predicted Next Temperature", prediction)
    
        if current_temp > 30:
            st.error("⚠ Overheating Detected")    
        
        return prediction

# receive data from backend service
data = get_data(5)

# display graph having current temp and next predicted temparature
prediction = display_current_and_predicted_temparature(data)

