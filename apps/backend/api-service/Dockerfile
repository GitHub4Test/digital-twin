# syntax=docker/dockerfile:1.7
FROM python:3.11-slim

WORKDIR /app

ARG NEXUS_PYPI_SIMPLE_URL
ARG PACKAGE_NAME
ARG VERSION

RUN --mount=type=secret,id=nexus_ca_cert \
    --mount=type=secret,id=nexus_username \
    --mount=type=secret,id=nexus_password \
    cp /run/secrets/nexus_ca_cert /usr/local/share/ca-certificates/nexus-ca.crt \
 && update-ca-certificates \
 && export NEXUS_USERNAME="$(cat /run/secrets/nexus_username)" \
 && export NEXUS_PASSWORD="$(cat /run/secrets/nexus_password)" \
 && pip install --no-cache-dir \
    --index-url "https://${NEXUS_USERNAME}:${NEXUS_PASSWORD}@${NEXUS_PYPI_SIMPLE_URL}" \
    "${PACKAGE_NAME}==${VERSION}" \
 && python -m pip uninstall -y setuptools wheel || true \
 && rm -rf /usr/local/lib/python3.11/site-packages/setuptools* \
 && rm -rf /usr/local/lib/python3.11/site-packages/wheel* \
 && rm -rf /usr/local/lib/python3.11/site-packages/*jaraco*

RUN addgroup --system digital-twin \
    && adduser --system --ingroup digital-twin digital-twin

USER digital-twin

CMD ["uvicorn", "api_service.main:app", "--host", "0.0.0.0", "--port", "8000"]