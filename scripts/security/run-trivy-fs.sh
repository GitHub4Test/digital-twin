#!/usr/bin/env bash
set -euo pipefail

TARGET="${1:-.}"

trivy fs \
  --severity HIGH,CRITICAL \
  "$TARGET"