# Digital Twin

A small demo platform that simulates an environment and exposes APIs and a frontend dashboard.

## Contents

- apps/backend: API service and edge server implementations
- apps/frontend: Dashboard app
- setup: Deployment manifests, Helm charts, and Ansible playbooks
- infra: Infrastructure provisioning and monitoring tooling
- tests: Unit and integration tests

## Architecture

- **API service**: located at `apps/backend/api_service`. Implements REST APIs and data models (see `apps/backend/api_service/src/main.py`, `apps/backend/api_service/src/models.py`, and `apps/backend/api_service/src/database.py`).
- **Edge server / simulator**: located at `apps/backend/edge_server`. Runs environment simulation and sensor/actuator emulation (see `apps/backend/edge_server/src/environment_sim.py`).
- **Frontend dashboard**: single-page dashboard app in `apps/frontend/app` (see `apps/frontend/app/src/dashboard.py` and `apps/frontend/app/src/twin_model.py`).
- **Persistence**: service-local database utilities are under `apps/backend/api_service/src/database.py`. Production storage/backing services are configured via Helm/Kubernetes manifests or `infra` tooling.
- **Deployment artifacts**: Helm chart at `setup/helm-chart/digital-twin` and raw Kubernetes manifests under `setup/k8s` for cluster deployments. Ansible playbooks and systemd templates are under `setup/app/ansible` for host-based installs.

## Deployment

This repository supports multiple deployment targets: local development with Docker Compose, containerized cluster deployments via Helm/kubectl (Kubernetes), and host-based deployments via Ansible.

- Local development (Docker Compose):

```bash
# From a terminal for the backend
cd apps/backend
docker-compose up --build

# From a second terminal for the frontend
cd apps/frontend
docker-compose up --build
```

- Kubernetes (Helm):

```bash
# Create namespace and install the chart
kubectl create namespace digital-twin || true
helm upgrade --install digital-twin setup/helm-chart/digital-twin -n digital-twin -f setup/helm-chart/digital-twin/values.yaml
```

- Kubernetes (raw manifests):

```bash
kubectl apply -f setup/k8s/backend -n digital-twin
kubectl apply -f setup/k8s/frontend -n digital-twin
```

- Host-based deployment (Ansible):

```bash
# Example: run the app playbook (inventory and vault may be required)
ansible-playbook -i setup/app/ansible/hosts setup/app/ansible/playbooks/apps.yml  -e operation="install/uninstall" -t install/uninstall
```

- Infrastructure provisioning (Terraform / scripts):

```bash
# Provision infrastructure where applicable
cd infra/terraform
terraform init
terraform apply

# Or run helper script
./infra/deploy.sh
```

Notes:
- Secrets and credentials are managed via Ansible Vault files and Helm values; review `setup/app/ansible/group_vars` and `setup/helm-chart/digital-twin/values.yaml` before deploying.
- For k3s or other lightweight clusters, use the Helm chart or the `setup/k8s` manifests depending on preference.

## Quick start (development)

1. Start backend and frontend with Docker Compose (from repo root):

```bash
# Terminal 1
cd apps/backend && docker-compose up --build

# Terminal 2 (from repo root)
cd apps/frontend && docker-compose up --build
```

2. API service: apps/backend/api_service — see `src/main.py` for routes and configuration.

3. Frontend: apps/frontend/app — see `src/dashboard.py` for startup.

## Run tests

Run the Python tests from the repo root:

```bash
python -m pytest tests/
```

## Development notes

- Python projects use `pyproject.toml` in each service. Install dependencies per-service in a virtualenv.
- Kubernetes manifests and Helm charts are in setup/ for staging/production deployments.

## Contributing

Please open issues or pull requests with clear descriptions and tests.

## License

TBD
