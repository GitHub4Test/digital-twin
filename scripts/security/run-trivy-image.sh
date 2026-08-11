#!/usr/bin/env bash
set -euo pipefail

TARGET="${1:?Usage: $0 <tarball-path|image-ref> [platform]}"
PLATFORM="${2:-}"

TRIVY_ARGS=(
  image
  --severity HIGH,CRITICAL
  --ignore-unfixed
  --format table \
  --output "trivy-report-${PLATFORM}.txt" \
  --exit-code 1
)

trivy clean --scan-cache
 
if [ -f "$TARGET" ]; then
  echo "==> Scanning local tarball: $TARGET"
  TRIVY_ARGS+=(--input "$TARGET")
else
  echo "==> Scanning registry image reference: $TARGET"
  if [ -z "$PLATFORM" ]; then
    echo "ERROR: scanning a registry image reference requires a platform argument." >&2
    echo "Usage: $0 <image-ref> <platform>" >&2
    exit 1
  fi
  TRIVY_ARGS+=(--platform "$PLATFORM" "$TARGET")
fi
 
trivy "${TRIVY_ARGS[@]}"