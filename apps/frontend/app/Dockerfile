# ---------- Stage 1: Builder ----------

# Use an official Python runtime as a parent image
FROM python:3.11-slim AS builder

# Install system dependencies including poetry
RUN apt-get update && apt-get install -y \
    curl \
    build-essential \
    python3-dev \
    libffi-dev \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Install Poetry safely
RUN pip install --no-cache-dir poetry==2.3.2

ENV PATH="/root/.local/bin:$PATH"

WORKDIR /app

# Copy only dependency files first (better caching)
COPY pyproject.toml poetry.lock README.md ./

# copy source code
COPY src ./src

# Install dependencies (without dev dependencies)
RUN poetry config virtualenvs.create false && \
    poetry install --only main --no-interaction --no-ansi

# ---------- Stage 2: Runtime ----------
FROM python:3.11-slim

# Copy installed Python packages from builder
COPY --from=builder /usr/local/lib/python3.11 /usr/local/lib/python3.11
COPY --from=builder /usr/local/bin /usr/local/bin

WORKDIR /app

# Copy application code
COPY src/dashboard.py .
COPY src/twin_model.py .

# Create .streamlit config directory
RUN mkdir -p ~/.streamlit

# Streamlit configuration
RUN echo "\
[server]\n\
headless = true\n\
port = 8501\n\
enableCORS = false\n\
" > ~/.streamlit/config.toml

# Expose port
EXPOSE 8501

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:8501/_stcore/health || exit 1

# Run Streamlit app
CMD ["streamlit", "run", "dashboard.py", "--server.address=0.0.0.0"]
