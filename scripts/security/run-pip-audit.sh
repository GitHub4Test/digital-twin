#!/usr/bin/env bash
set -euo pipefail

SERVICE_PATH="${1:?Usage: $0 <service-path>}"

cd "$SERVICE_PATH"

poetry export -f requirements.txt --without-hashes -o /tmp/requirements-audit.txt
poetry run pip-audit -r /tmp/requirements-audit.txt