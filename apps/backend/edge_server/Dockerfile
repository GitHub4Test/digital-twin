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

WORKDIR /edge_server

# copy built package
COPY --from=builder /app/dist/*.whl .

# install package
RUN pip install *.whl

# Run environment_sim edge_server
CMD ["python", "-m", "src.environment_sim"]
