# Frontend Dashboard - Digital Twin

Streamlit web application for real-time monitoring and visualization of Digital Twin sensor data with predictive analytics.

## 📋 Overview

The frontend dashboard provides:
- Real-time temperature and humidity visualization
- Historical data analysis with line charts
- Temperature prediction using linear regression
- Alert system for anomalies
- Connected to backend API

## 🏗️ Architecture

```
frontend/
├── dashboard.py    # Main Streamlit app
├── twin_model.py   # Prediction model
├── pyproject.toml  # Poetry dependencies
└── README.md       # This file
```

## 🛠️ Tech Stack

- **Python 3.11+**
- **Streamlit 1.28.0** - Web app framework
- **Pandas 2.1.0** - Data manipulation
- **NumPy 1.26.0** - Numerical computing
- **Requests 2.31.0** - HTTP client
- **Poetry** - Dependency management

## 🚀 Quick Start

### Local Development

```bash
# Install dependencies
poetry install

# Run dashboard
poetry run streamlit run dashboard.py
```

Dashboard runs on `http://localhost:8501`

## 📱 Dashboard Features

### Metrics
- **Current Temperature** - Real-time temperature reading
- **Predicted Next Temperature** - ML-based forecast

### Visualizations
- Temperature trend line chart
- Humidity trend line chart
- 200 most recent sensor readings

### Alerts
- Overheating alert when temperature > 30°C
- Error display with warning icon

## 📁 Code Structure

### dashboard.py
Main Streamlit application:
- Connects to backend API (`http://localhost:8000/data`)
- Formats sensor data into DataFrame
- Renders charts and metrics
- Displays alerts

**Key Components:**
1. Title and page setup
2. API data retrieval
3. Data sorting and preparation
4. Line charts for temperature/humidity
5. Current metrics display
6. Prediction display
7. Alert trigger logic

### twin_model.py
Machine learning prediction model:
- Linear regression for temperature prediction
- Trend analysis on historical data
- Next temperature forecast

**Functions:**
- `predict_next(temperature_list)` - Forecast next temperature

## 🔧 Configuration

### Backend Connection
Default backend URL: `http://localhost:8000/data`

To change backend URL, modify dashboard.py:
```python
response = requests.get("http://your-backend-url:8000/data")
```

### Environment Variables
Set these to override defaults:
```bash
export BACKEND_API_URL=http://your-server:8000
```

## 📊 Data Requirements

Dashboard expects backend to return JSON array:
```json
[
  {
    "timestamp": "2026-02-15T10:30:00",
    "temperature": 25.5,
    "humidity": 55.2
  },
  ...
]
```

Maximum 200 most recent records displayed.

## 🧪 Development

### Code Formatting
```bash
poetry run black dashboard.py twin_model.py
```

### Linting
```bash
poetry run flake8 dashboard.py twin_model.py
```

### Testing
```bash
poetry run pytest
```

## 📦 Dependency Management

Add dependencies:
```bash
poetry add <package-name>
poetry lock
```

Update all dependencies:
```bash
poetry update
```

Install all dependencies:
```bash
poetry install
```

## 🐳 Docker (Optional)

You can also containerize the frontend separately:

```bash
# Create Dockerfile in frontend directory
docker build -t digital-twin-frontend .
docker run -p 8501:8501 digital-twin-frontend
```

## 🔍 Troubleshooting

### Backend connection refused
```
ConnectionError: Failed to establish a new connection
```
- Verify backend is running: `curl http://localhost:8000/health`
- Check backend URL configuration
- Ensure port 8000 is accessible

### No data displayed
- Check backend has sensor data: `curl http://localhost:8000/data`
- Verify response format is valid JSON
- Check DataFrame is populated

### Charts not rendering
- Ensure pandas and numpy are installed correctly
- Verify data timestamps are valid
- Check for empty or malformed data

### Streamlit caching issues
```bash
streamlit cache clear
poetry run streamlit run dashboard.py --logger.level=debug
```

### Poetry lock issues
```bash
poetry lock --no-update
```

## 📚 Further Reading

- [Streamlit Documentation](https://docs.streamlit.io/)
- [Pandas Documentation](https://pandas.pydata.org/docs/)
- [NumPy Documentation](https://numpy.org/doc/)
- [Scikit-Learn Linear Regression](https://scikit-learn.org/stable/modules/generated/sklearn.linear_model.LinearRegression.html)
- [Poetry Documentation](https://python-poetry.org/docs/)

## 🎨 Customization

### Change alert threshold
In dashboard.py, modify:
```python
if current_temp > 30:  # Change 30 to your threshold
    st.error("⚠ Overheating Detected")
```

### Add new metrics
Update dashboard.py to include additional metrics:
```python
st.metric("New Metric", value)
```

### Improve prediction model
Enhance twin_model.py with:
- Polynomial regression
- LSTM neural networks
- Seasonal decomposition
- More advanced ML algorithms

### Customize styling
Use Streamlit theming in `.streamlit/config.toml`:
```toml
[theme]
primaryColor = "#FF6B6B"
backgroundColor = "#F0F2F6"
```
