#!/usr/bin/env bash
set -euo pipefail

IMAGE="${1:?Usage: $0 <image>}"

trivy clean --scan-cache

trivy image \
  --severity HIGH,CRITICAL \
  --ignore-unfixed \
  --format table \
  --exit-code 1 \
  "$IMAGE"