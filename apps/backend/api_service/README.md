# Backend Service - Digital Twin

Unified FastAPI backend service for Digital Twin sensor data management with integrated SQLite database.

## 📋 Overview

The backend service handles:
- Sensor data ingestion from environment simulator
- RESTful API endpoints for data retrieval and management
- SQLite database operations
- Health monitoring and service diagnostics

## 🏗️ Architecture

```
app/
├── models.py       # Pydantic data models
├── database.py     # SQLite database handler
├── routes.py       # API endpoint definitions
└── main.py         # FastAPI app factory

main.py            # Entry point
pyproject.toml     # Poetry dependencies
Dockerfile         # Container image definition
```

## 🛠️ Tech Stack

- **Python 3.11+**
- **FastAPI 0.104.1** - Web framework
- **Uvicorn 0.24.0** - ASGI server
- **Pydantic 2.5.0** - Data validation
- **SQLite** - Embedded database
- **Poetry** - Dependency management

## 🚀 Quick Start

### Local Development

```bash
# Install dependencies
poetry install

# Run server
poetry run python main.py
```

Server runs on `http://localhost:8000`

### Docker

```bash
# Build image
docker build -t digital-twin-backend .

# Run container
docker run -p 8000:8000 -v database_data:/data digital-twin-backend
```

## 📡 API Endpoints

### Health Check
```bash
GET /health

Response:
{
  "status": "healthy",
  "service": "backend"
}
```

### Submit Sensor Reading
```bash
POST /update
Content-Type: application/json

Request:
{
  "timestamp": "2026-02-15T10:30:00",
  "temperature": 25.5,
  "humidity": 55.2
}

Response:
{
  "status": "success",
  "message": "Sensor reading recorded"
}
```

### Get Sensor Data
```bash
GET /data?limit=200

Response:
[
  {
    "timestamp": "2026-02-15T10:30:00",
    "temperature": 25.5,
    "humidity": 55.2
  },
  ...
]
```

### Clear All Data
```bash
DELETE /data

Response:
{
  "status": "success",
  "message": "All sensor data cleared"
}
```

## 📁 Code Structure

### models.py
Pydantic schemas for request/response validation:
- `SensorReading` - Input data model
- `SensorReadingResponse` - Output data model
- `HealthCheckResponse` - Health check response

### database.py
SQLite database operations:
- `Database.init()` - Initialize schema
- `Database.insert_reading()` - Store sensor data
- `Database.get_readings()` - Retrieve sensor data
- `Database.clear_readings()` - Delete all data

### routes.py
FastAPI route handlers:
- `/health` - Service health
- `POST /update` - Store reading
- `GET /data` - Retrieve readings
- `DELETE /data` - Clear data

### main.py
FastAPI application factory with startup initialization

## 🔧 Configuration

### Environment Variables
- `DB_PATH` - SQLite database path (default: `/data/database.db`)

### Poetry Dependencies

**Production**
- fastapi
- uvicorn[standard]
- pydantic

**Development**
- pytest
- black
- flake8

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

## 🧪 Development

### Code Formatting
```bash
poetry run black app/ main.py
```

### Linting
```bash
poetry run flake8 app/ main.py
```

### Testing
```bash
poetry run pytest
```

## 🐳 Docker

### Build
```bash
docker build -t digital-twin-backend .
```

### Run
```bash
docker run -p 8000:8000 -v database_data:/data digital-twin-backend
```

### Health Check
```bash
curl http://localhost:8000/api/v1/health
```

## 📊 Database

SQLite database with single table:

```sql
CREATE TABLE sensor (
    timestamp TEXT NOT NULL,
    temperature REAL NOT NULL,
    humidity REAL NOT NULL
)
```

Data persists in Docker volume `/data/database.db`

## 🔍 Troubleshooting

### Database errors
- Check `/data` directory permissions
- Verify SQLite file exists: `ls -la /data/database.db`
- Clear and reinitialize: `DELETE FROM sensor;`

### Connection refused
- Ensure service is running: `curl http://localhost:8000/api/v1/health`
- Check port 8000 is available: `lsof -i :8000`

### Poetry lock issues
```bash
poetry lock --no-update
```

### Docker build fails
```bash
docker build --no-cache -t digital-twin-backend .
```

## 📚 Further Reading

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Pydantic Documentation](https://docs.pydantic.dev/)
- [Poetry Documentation](https://python-poetry.org/docs/)
- [SQLite Documentation](https://www.sqlite.org/docs.html)
