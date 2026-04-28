FROM python:3.11-slim

WORKDIR /app

ARG NEXUS_PYPI_SIMPLE_URL
ARG NEXUS_USERNAME
ARG NEXUS_PASSWORD
ARG PACKAGE_NAME
ARG VERSION

RUN pip install --no-cache-dir \
    --extra-index-url http://${NEXUS_USERNAME}:${NEXUS_PASSWORD}@${NEXUS_PYPI_SIMPLE_URL} \
     --trusted-host 192.168.178.59 \
    ${PACKAGE_NAME}==${VERSION}

CMD ["uvicorn", "api_service.main:app", "--host", "0.0.0.0", "--port", "8000"]