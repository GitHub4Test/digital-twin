# Copilot Workspace Instructions — Digital Twin

Purpose: quick, actionable guidance for AI assistants and new contributors to get productive in this repository.

## Quick Start

- Backend (API + edge):

```bash
cd apps/backend
docker-compose up --build
```

- Frontend (dashboard):

```bash
cd apps/frontend
docker-compose up --build
```

- Run tests:

```bash
python -m pytest tests/
```

## Key Locations

- API service: [apps/backend/api_service](apps/backend/api_service/)
- Edge simulator: [apps/backend/edge_server](apps/backend/edge_server/)
- Frontend dashboard: [apps/frontend/app](apps/frontend/app/)
- Docker Compose files: [apps/backend/docker-compose.yml](apps/backend/docker-compose.yml), [apps/frontend/docker-compose.yml](apps/frontend/docker-compose.yml)
- Ansible playbooks: [setup/app/ansible/playbooks/apps.yml](setup/app/ansible/playbooks/apps.yml)
- Infrastructure scripts: [infra/deploy.sh](infra/deploy.sh) and [setup/terraform](setup/terraform/) (where applicable)

## Conventions

- Each Python service uses `pyproject.toml` / Poetry for dependency management.
- Services expose ports: backend `8000` (FastAPI), frontend `8501` (Streamlit).
- Configuration via environment variables; check service `src` modules for expected names (e.g., `BACKEND_API_URL`).
- Tests live in `tests/` and use `pytest`.

## Deployment Options

- Local: Docker Compose (above).
- Kubernetes: Helm chart is in `setup/helm-chart/digital-twin` and raw manifests under `setup/k8s`.
- Host installs: Ansible playbooks in `setup/app/ansible` (uses group_vars and Vault files for secrets).

## How to ask the assistant (example prompts)

- "Run the backend unit tests and report failures from `tests/backend`." 
- "List the environment variables required by the API service and where they are read." 
- "Create a minimal `values.yaml` for the Helm chart to deploy one replica of backend and frontend." 

## Troubleshooting & Notes

- If containers fail to start, check `docker-compose` logs in the service folder.
- Secrets: review `setup/app/ansible/group_vars` and any Vault files before deploying.

## Next steps (suggested)

- Add `ARCHITECTURE.md` with a high-level diagram and component interactions.
- Provide sample `values.yaml` and `.env.example` files for local development.
