#!/usr/bin/env bash
set -euo pipefail

SERVICE_PATH="${1:?Usage: $0 <service-path>}"

cd "$SERVICE_PATH"

poetry run semgrep --config auto .