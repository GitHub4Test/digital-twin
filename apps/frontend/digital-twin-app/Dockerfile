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
 && (python -m pip uninstall -y setuptools wheel || true)
 
# Create .streamlit config directory
RUN mkdir -p /home/digital-twin/.streamlit \
    && echo "\
[server]\n\
headless = true\n\
port = 8501\n\
enableCORS = false\n\
" > /home/digital-twin/.streamlit/config.toml \
    && chown -R digital-twin:digital-twin /home/digital-twin/.streamlit

# Expose port
EXPOSE 8501

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8501/_stcore/health')" || exit 1

USER digital-twin

# Run Streamlit app
CMD ["sh", "-c", "streamlit run $(python -c 'import digital_twin_app.dashboard as m; print(m.__file__)') --server.address=0.0.0.0"]