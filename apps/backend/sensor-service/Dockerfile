# syntax=docker/dockerfile:1.7
FROM python:3.12-slim AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

ARG PACKAGE_NAME
ARG VERSION
ARG NEXUS_PYPI_SIMPLE_URL

RUN addgroup --system digital-twin \
    && adduser --system --ingroup digital-twin digital-twin

WORKDIR /app

RUN --mount=type=cache,target=/root/.cache/pip \
    --mount=type=secret,id=nexus_username \
    --mount=type=secret,id=nexus_password \
    NEXUS_USERNAME=$(cat /run/secrets/nexus_username) && \
    NEXUS_PASSWORD=$(cat /run/secrets/nexus_password) && \
    pip install --no-cache-dir \
      --index-url "http://${NEXUS_USERNAME}:${NEXUS_PASSWORD}@${NEXUS_PYPI_SIMPLE_URL}" \
      --trusted-host "$(echo "$NEXUS_PYPI_SIMPLE_URL" | cut -d/ -f1 | cut -d: -f1)" \
      "${PACKAGE_NAME}==${VERSION}"

RUN mkdir -p /data \
    && chown -R digital-twin:digital-twin /data

USER digital-twin

EXPOSE 8001

CMD ["python3", "-m", "sensor_service.app"]
