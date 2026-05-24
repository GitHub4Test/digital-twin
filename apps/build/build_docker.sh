#!/usr/bin/env bash
set -euo pipefail

set -a
[ -f ./build/.env ] && source ./build/.env
[ -f ./build/.env.local ] && source ./build/.env.local
set +a

: "${NEXUS_USERNAME:?NEXUS_USERNAME is required}"
: "${NEXUS_PASSWORD:?NEXUS_PASSWORD is required}"

SERVICE_PATH="$1"

cd "$SERVICE_PATH"

VERSION="$(poetry version -s)"
PACKAGE_NAME="$(basename "$SERVICE_PATH" | tr '-' '_')"
IMAGE="$NEXUS_DOCKER_REPO/$(basename "$SERVICE_PATH"):$VERSION"

docker buildx build \
  --builder multiarch-builder \
  --platform "$PLATFORM" \
  --build-arg PACKAGE_NAME="$PACKAGE_NAME" \
  --build-arg VERSION="$VERSION" \
  --build-arg NEXUS_PYPI_SIMPLE_URL=$NEXUS_PYPI_SIMPLE_URL \
  --build-arg NEXUS_USERNAME=$NEXUS_USERNAME \
  --build-arg NEXUS_PASSWORD=$NEXUS_PASSWORD \
  --cache-from=type=local,src=.buildx-cache \
  --cache-to=type=local,dest=.buildx-cache,mode=max \
  -t "$IMAGE" \
  -t "$NEXUS_DOCKER_REPO/$(basename "$SERVICE_PATH"):latest" \
  --push \
  .

echo "Docker image pushed:"
echo "$IMAGE"