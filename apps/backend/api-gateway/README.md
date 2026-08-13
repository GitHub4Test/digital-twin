# Environment Simulator - Digital Twin

Thermal environment simulator that generates realistic sensor data and submits it to the Digital Twin backend service.

## 📋 Overview

The environment simulator provides:
- Continuous thermal simulation with heat exchange model
- Automated cooling system control logic
- Realistic humidity fluctuation
- Periodic sensor data submission to backend API
- Configurable backend URL and simulation parameters

## 🏗️ Architecture

```
backend/
├── environment_sim.py  # Main simulator script
├── api_service/        # Backend service
└── backend.py          # Original backend (reference)
```

## 🛠️ Tech Stack

- **Python 3.11+**
- **Requests 2.31.0** - HTTP client
- **Datetime** - Timestamp generation

## 🚀 Quick Start

### Local Development

```bash
# Basic run (requires backend on localhost:8000)
python environment_sim.py

# With custom backend URL
BACKEND_API_URL=http://192.168.1.100:8000/api/v1/readings python environment_sim.py

# With Docker backend
BACKEND_API_URL=http://backend:8000/api/v1/readings python environment_sim.py
```

## 🌡️ Simulation Model

### Heat Exchange Model
```
Temperature Change = (Outside Temp - Current Temp) * Heat Transfer Coefficient
```

- **Heat Transfer Coefficient**: 0.05 (controls how quickly system reaches ambient)
- **Outside Temperature**: 30°C (constant ambient)
- **Initial Temperature**: 22°C

### Cooling System
- **ON Temperature**: > 26°C
- **OFF Temperature**: < 24°C
- **Cooling Effect**: -0.3°C per cycle
- **Cycle Time**: 3 seconds

### Humidity Simulation
- **Base Humidity**: 50%
- **Range**: 30% - 80%
- **Natural Drift**: ±0.02 per cycle
- **Cooling Effect**: -0.05 on cool, +0.1 on heat

## 📡 Output Format

Sensor readings submitted to backend:

```json
{
  "timestamp": "2026-02-15T10:30:00.123456",
  "temperature": 25.50,
  "humidity": 55.20
}
```

Submissions made every 3 seconds via:
```
POST {BACKEND_API_URL}/update
Content-Type: application/json
```

## 🔧 Configuration

### Environment Variables

**Backend Connection**
- `BACKEND_API_URL` - Full URL to backend /readings endpoint
  - Default: `http://localhost:8000/api/v1/readings`
  - Docker: `http://backend:8000/api/v1/readings`
  - Remote: `http://192.168.1.x:8000/api/v1/readings`

### Simulation Parameters (Hard-coded)

Edit environment_sim.py to customize:

```python
# Initial conditions
temperature = 22.0  # Starting temperature (°C)
outside_temp = 30  # Ambient temperature (°C)
humidity = 50.0  # Starting humidity (%)

# Thresholds
if temperature > 26:  # Cooling ON threshold
    cooling_on = True
elif temperature < 24:  # Cooling OFF threshold
    cooling_on = False

# Cycle time
time.sleep(3)  # Seconds between readings
```

## 📊 Output Example

```
Connecting to backend API at: http://localhost:8000/api/v1/readings
[2026-02-15T10:30:00.123456] Sensor reading sent: {'timestamp': '2026-02-15T10:30:00.123456', 'temperature': 22.01, 'humidity': 50.02}
[2026-02-15T10:30:03.234567] Sensor reading sent: {'timestamp': '2026-02-15T10:30:03.234567', 'temperature': 22.14, 'humidity': 50.05}
[2026-02-15T10:30:06.345678] Sensor reading sent: {'timestamp': '2026-02-15T10:30:06.345678', 'temperature': 22.41, 'humidity': 50.08}
...
```

## 🔍 Troubleshooting

### Connection Error
```
[timestamp] Connection error: HTTPConnectionPool(host='localhost', port=8000): Max retries exceeded
```
- Verify backend is running: `curl http://localhost:8000/api/v1/health`
- Check `BACKEND_API_URL` is correct
- Ensure port 8000 is accessible
- For Docker: use `http://backend:8000/api/v1/readings`

### Server Error
```
[timestamp] Server error (500): {'status': 'error'}
```
- Check backend logs: `docker-compose logs backend`
- Verify database is initialized
- Check `/data` directory permissions

### No Output
- Ensure you're running in correct directory
- Check Python 3.11+ is installed
- Verify requests module is installed

## 🚀 Deployment Scenarios

### Local Development
```bash
cd backend
poetry install
poetry run python environment_sim.py
```

### Docker Compose
```bash
# In new terminal, simulator runs locally
BACKEND_API_URL=http://localhost:8000/update python environment_sim.py
```

### Raspberry Pi (via Ansible)
- Installed automatically in `/opt/digital-twin`
- Can be run as separate service or cron job

### Custom Host
```bash
BACKEND_API_URL=http://192.168.1.50:8000/update python environment_sim.py &
```

## 📝 Notes

- Simulator runs indefinitely until interrupted (Ctrl+C)
- Each cycle takes approximately 3 seconds
- Timestamps are in ISO 8601 format with microseconds
- Temperature rounds to 2 decimal places
- Humidity rounds to 2 decimal places
- Connection errors are logged but don't stop the simulator
- All readings use system time (no RTC required)

## 🔐 Security Notes

- Remove/parameterize hardcoded IP addresses for production
- Consider adding authentication to backend API
- Use HTTPS for remote connections
- Validate sensor data on backend

## 📚 Further Reading

- [Requests Documentation](https://docs.python-requests.org/)
- [Python Datetime](https://docs.python.org/3/library/datetime.html)
- [HTTP POST Specification](https://tools.ietf.org/html/rfc7231#section-6.3.2)
- [ISO 8601 Timestamp Format](https://en.wikipedia.org/wiki/ISO_8601)
