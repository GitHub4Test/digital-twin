# Digital Twin - Raspberry Pi Environmental Monitoring System

A containerized microservices architecture for real-time environmental monitoring and thermal management on Raspberry Pi 4, featuring sensor simulation, REST API backend, and Streamlit dashboard visualization.

## 🏗️ Architecture

The system consists of two main components:

### Backend Service (Containerized)
- **FastAPI** server with SQLite database integration
- RESTful API endpoints for sensor data management
- Modular code structure: models, database, routes
- Health check endpoints for monitoring
- Poetry-based dependency management

### Frontend Dashboard (Local)
- **Streamlit** web application for real-time visualization
- Line charts for temperature and humidity trends
- Current metric display and predictive analytics
- Alert system for temperature anomalies
- Connects to backend API

### Environment Simulator
- Continuous thermal simulation with heat exchange model
- Automated cooling system control
- Periodic sensor data submission to backend
- Configurable backend URL via environment variables

## 🛠️ Technology Stack

### Backend
- **Python 3.11+**
- **FastAPI 0.104.1** - Modern web framework
- **Uvicorn 0.24.0** - ASGI server
- **Pydantic 2.5.0** - Data validation
- **SQLite** - Lightweight database
- **Poetry** - Dependency management

### Frontend
- **Python 3.11+**
- **Streamlit 1.28.0** - Web app framework
- **Pandas 2.1.0** - Data manipulation
- **NumPy 1.26.0** - Numerical computing
- **Requests 2.31.0** - HTTP client
- **Poetry** - Dependency management

### DevOps
- **Docker** - Containerization
- **Docker Compose** - Orchestration
- **Ansible** - Infrastructure automation

## 📋 Prerequisites

### For Local Development
- Python 3.11 or higher
- Poetry (install via: `pip install poetry`)
- Docker and Docker Compose (for containerized deployment)

### For Raspberry Pi Deployment
- Raspberry Pi 4 with Raspberry Pi OS
- SSH access to the device
- Ansible installed on control machine

## 🚀 Quick Start

### Local Development

1. **Clone the repository**
```bash
cd /Users/suhas-mac/Documents/Technical/Digital-Twin
```

2. **Setup backend with Poetry**
```bash
cd backend/api_service
poetry install
poetry run python main.py
```
Backend runs on `http://localhost:8000`

3. **Setup frontend with Poetry** (in new terminal)
```bash
cd frontend
poetry install
poetry run streamlit run dashboard.py
```
Dashboard runs on `http://localhost:8501`

4. **Run environment simulator** (in new terminal)
```bash
cd backend
BACKEND_API_URL=http://localhost:8000/update python environment_sim.py
```

### Docker Deployment

1. **Build and start services**
```bash
docker-compose up --build
```
- Backend API: `http://localhost:8000`
- Database volume: `database_data`

2. **Check service health**
```bash
curl http://localhost:8000/health
```

## 📡 API Endpoints

### Health Check
```
GET /health
Response: {"status": "healthy", "service": "backend"}
```

### Submit Sensor Reading
```
POST /update
Content-Type: application/json

{
  "timestamp": "2026-02-15T10:30:00",
  "temperature": 25.5,
  "humidity": 55.2
}

Response: {"status": "success", "message": "Sensor reading recorded"}
```

### Retrieve Sensor Data
```
GET /data?limit=200
Response: [
  {
    "timestamp": "2026-02-15T10:30:00",
    "temperature": 25.5,
    "humidity": 55.2
  },
  ...
]
```

### Clear All Sensor Data
```
DELETE /data
Response: {"status": "success", "message": "All sensor data cleared"}
```

## 📁 Project Structure

```
Digital-Twin/
├── backend/
│   ├── api_service/
│   │   ├── app/
│   │   │   ├── __init__.py
│   │   │   ├── models.py          # Pydantic models
│   │   │   ├── database.py        # SQLite operations
│   │   │   ├── routes.py          # API endpoints
│   │   │   └── main.py            # FastAPI app factory
│   │   ├── main.py                # Entry point
│   │   ├── Dockerfile
│   │   ├── pyproject.toml
│   │   ├── poetry.lock
│   │   ├── .dockerignore
│   │   └── README.md
│   ├── backend.py                 # Original backend (reference)
│   ├── environment_sim.py          # Thermal simulator
│   └── README.md
├── frontend/
│   ├── dashboard.py               # Streamlit app
│   ├── twin_model.py              # Prediction model
│   ├── pyproject.toml
│   ├── poetry.lock
│   └── README.md
├── docker-compose.yml             # Docker orchestration
├── setup.yml                       # Ansible playbook
├── hosts                           # Ansible inventory
├── ansible.cfg                     # Ansible configuration
├── digital-twin.service.j2        # Systemd service template
├── .dockerignore                   # Docker build exclusions
└── README.md                       # This file
```

## 🔧 Configuration

### Environment Variables

**Backend Service**
- `DB_PATH` - SQLite database path (default: `/data/database.db`)

**Environment Simulator**
- `BACKEND_API_URL` - Backend API URL (default: `http://localhost:8000/update`)

**Docker Compose**
- Set in `docker-compose.yml` or `.env` file

## 📦 Dependency Management with Poetry

### Add a new dependency
```bash
cd backend/api_service  # or frontend
poetry add <package-name>
poetry lock
```

### Update dependencies
```bash
poetry update
```

### Install dependencies
```bash
poetry install
```

### Run with Poetry
```bash
poetry run python main.py
```

## 🌐 Raspberry Pi Deployment with Ansible

### Prerequisites
- Ansible installed on your control machine
- SSH access to Raspberry Pi
- Update `hosts` file with Pi's IP/hostname

### Run deployment
```bash
ansible-playbook setup.yml
```

This will:
1. Update system packages
2. Install Docker and Docker Compose
3. Install Poetry
4. Clone/sync project files
5. Build Docker images
6. Setup systemd service for auto-start
7. Start Digital Twin services

### Monitor deployment
```bash
# SSH to Pi
ssh pi@raspberrypi.local

# Check service status
systemctl status digital-twin

# View logs
journalctl -u digital-twin -f

# Manage services
docker-compose -f /opt/digital-twin ps
docker-compose -f /opt/digital-twin logs -f
```

## 🧪 Development

### Backend Testing
```bash
cd backend/api_service
poetry install --with dev
poetry run pytest
```

### Code Formatting
```bash
poetry run black app/ main.py
poetry run flake8 app/ main.py
```

### Frontend Testing
```bash
cd frontend
poetry install --with dev
poetry run pytest
```

## 📊 Database Schema

### Sensor Table
```sql
CREATE TABLE sensor (
    timestamp TEXT NOT NULL,
    temperature REAL NOT NULL,
    humidity REAL NOT NULL
)
```

## 🔍 Troubleshooting

### Backend won't start
```bash
# Check Docker logs
docker-compose logs backend

# Verify database directory permissions
docker exec backend ls -la /data
```

### Environment simulator not connecting
```bash
# Verify backend is running
curl http://localhost:8000/health

# Check simulator logs and BACKEND_API_URL
echo $BACKEND_API_URL
```

### Poetry lock file errors
```bash
# Regenerate lock file
cd backend/api_service
poetry lock --no-update
```

### Ansible deployment issues
```bash
# Run with verbose output
ansible-playbook setup.yml -vv

# Check inventory
ansible-inventory -i hosts --list
```

## 📝 Notes

- The system uses a single containerized backend with integrated SQLite database
- Both backend and frontend use Poetry for modern Python dependency management
- Ansible automates the entire Raspberry Pi setup including Docker and systemd integration
- Data persists in Docker volume `database_data`
- Frontend can run on host or containerize separately as needed

## 📄 License

[Add your license here]

## 👥 Contributors

[Add contributor information]

## 📞 Support

For issues or questions, please check the troubleshooting section or contact the development team.

## K3S Networking details
            Internet
                │
          Router 192.168.178.1
                │
            wlan0
                │
            Node OS
                │
            cni0 (10.42.0.1)
          ┌─────┴─────┐
        veth        veth
        │            │
    Pod A         Pod B
    10.42.0.10    10.42.0.11
        │            │
        └──flannel overlay───┘

10.43.x.x
   │
iptables NAT
   │
pod endpoints            

# racher web ui setup
0. Create TLS certificates
  echo "192.168.178.59 rancher.local" | sudo tee -a /etc/hosts
  brew install mkcert nss
  mkcert -install
  mkcert rancher.local
1. Mac -> Run docker container -> 
  docker run -d \
  --name rancher \
  --restart=unless-stopped \
  --privileged \
  -p 80:80 \
  -p 443:443 \
  -v "$PWD/rancher.local.pem:/etc/rancher/ssl/cert.pem" \
  -v "$PWD/rancher.local-key.pem:/etc/rancher/ssl/key.pem" \
  rancher/rancher:stable
  # docker run -d --restart=unless-stopped   --privileged   -p 80:80 -p 443:443   --name rancher   rancher/rancher:latest
2. Once its up and running access http.//localhost
3. Follow the instructions for getting password and Specify the server URL as http://mac-ip
4. Once its logged-in, you will see the existing local racher node setup
5. Select Import Existing->Custom, given any cluster name <cluster_name>
6. Select Network as Flannel and click create button
7. Copy the statement having token that you have to run on the other cluster machine for ex. raspberry pi
8. Keep it on running the container, login with admin/<password from step 3>   
9. copy the token number only from step statement and put value of k3_rancher_token

# Use of ansible_vault for encrypt/decrypt values and use it in ansible
- provide vault password for vars_files included using for ex. -> ansible-playbook playbooks/raspberry_config.yml -e "operation=install" --tags install --ask-vault-pass # pswd:mac-pswd

# Tailscale setup
  - Private VPM network setup between Mac, Raspberrypi and cloud