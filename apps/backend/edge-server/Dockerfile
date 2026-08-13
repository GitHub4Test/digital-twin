# syntax=docker/dockerfile:1.7
FROM python:3.11-slim

WORKDIR /app

ARG NEXUS_PYPI_SIMPLE_URL
ARG PACKAGE_NAME
ARG VERSION

RUN addgroup --system digital-twin \
    && adduser --system --ingroup digital-twin digital-twin

RUN --mount=type=cache,target=/root/.cache/pip \
    --mount=type=secret,id=nexus_username \
    --mount=type=secret,id=nexus_password \
    NEXUS_USERNAME=$(cat /run/secrets/nexus_username) && \
    NEXUS_PASSWORD=$(cat /run/secrets/nexus_password) && \
    pip install --no-cache-dir \
    --index-url "http://${NEXUS_USERNAME}:${NEXUS_PASSWORD}@${NEXUS_PYPI_SIMPLE_URL}" \
    --trusted-host "$(echo "$NEXUS_PYPI_SIMPLE_URL" | cut -d/ -f1 | cut -d: -f1)" \
    "${PACKAGE_NAME}==${VERSION}" \
 && pip show "${PACKAGE_NAME}" \
 && python -c "import edge_server; print(edge_server.__file__)" \    
 && (python -m pip uninstall -y setuptools wheel || true)

USER digital-twin

# Run environment_sim edge_server
CMD ["python", "-m", "edge_server.environment_sim"]