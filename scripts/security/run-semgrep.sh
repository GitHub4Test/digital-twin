#!/usr/bin/env bash
set -euo pipefail

SERVICE_PATH="${1:?Usage: $0 <service-path>}"

cd "$SERVICE_PATH"

if [[ ! -d ".venv" ]]; then
  echo "Creating virtual environment for $(pwd)"
  poetry install --with dev --with security --no-interaction
fi

export TMPDIR="${TMPDIR:-/tmp}"
mkdir -p "$TMPDIR"
poetry run semgrep --config auto .