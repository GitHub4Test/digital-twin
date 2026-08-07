#!/usr/bin/env bash
set -euo pipefail

TARGET="${1:-.}"

trivy fs \
  --severity HIGH,CRITICAL \
  --exit-code 1 \
  "$TARGET"