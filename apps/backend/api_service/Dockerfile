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

# build wheel
RUN poetry build

# ---------- Stage 2: Runtime ----------
FROM python:3.11-slim

RUN apt-get update && apt-get install -y curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# copy built package
COPY --from=builder /app/dist/*.whl .

# install package
RUN pip install *.whl

# Create data directory for database
RUN mkdir -p /data

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=10s --timeout=5s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Run application
CMD ["python", "-m", "src.main"]
