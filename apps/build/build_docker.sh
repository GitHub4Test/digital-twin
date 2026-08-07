#!/usr/bin/env bash
set -euo pipefail

# Load non-secret config only
set -a
[ -f ./build/.env ] && source ./build/.env
set +a

# Load local secrets only outside GitHub Actions
if [ -z "${GITHUB_ACTIONS:-}" ] && [ -f ./build/.env.local ]; then
  set -a
  source ./build/.env.local
  set +a
fi

: "${NEXUS_USERNAME:?NEXUS_USERNAME is required}"
: "${NEXUS_PASSWORD:?NEXUS_PASSWORD is required}"

SERVICE_PATH="$1"

cd "$SERVICE_PATH"

VERSION="$(poetry version -s)"
PACKAGE_NAME="$(basename "$SERVICE_PATH" | tr '-' '_')"
IMAGE="$NEXUS_DOCKER_REPO/$(basename "$SERVICE_PATH"):$VERSION"

echo "$NEXUS_PASSWORD" | docker login "$NEXUS_DOCKER_REPO" \
  -u "$NEXUS_USERNAME" \
  --password-stdin

docker buildx build \
  --builder multiarch-builder \
  --no-cache \
  --platform "$PLATFORM" \
  --build-arg PACKAGE_NAME="$PACKAGE_NAME" \
  --build-arg VERSION="$VERSION" \
  --build-arg NEXUS_PYPI_SIMPLE_URL=$NEXUS_PYPI_SIMPLE_URL \
  --build-arg NEXUS_USERNAME=$NEXUS_USERNAME \
  --build-arg NEXUS_PASSWORD=$NEXUS_PASSWORD \
  -t "$IMAGE" \
  -t "$NEXUS_DOCKER_REPO/$(basename "$SERVICE_PATH"):latest" \
  --push \
  .

echo "Docker image pushed:"
echo "$IMAGE"

../../scripts/security/run-trivy-image.sh "$IMAGE"