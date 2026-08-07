FROM python:3.11-slim

WORKDIR /app

ARG NEXUS_PYPI_SIMPLE_URL
ARG NEXUS_USERNAME
ARG NEXUS_PASSWORD
ARG PACKAGE_NAME
ARG VERSION

RUN pip install --no-cache-dir \
    --index-url http://${NEXUS_USERNAME}:${NEXUS_PASSWORD}@${NEXUS_PYPI_SIMPLE_URL} \
    --trusted-host 192.168.178.59 \
    ${PACKAGE_NAME}==${VERSION} \
 && python -m pip uninstall -y setuptools wheel || true \
 && rm -rf /usr/local/lib/python3.11/site-packages/setuptools* \
 && rm -rf /usr/local/lib/python3.11/site-packages/wheel* \
 && rm -rf /usr/local/lib/python3.11/site-packages/*jaraco*

RUN addgroup --system digital-twin \
    && adduser --system --ingroup digital-twin digital-twin

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