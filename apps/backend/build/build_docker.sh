#!/usr/bin/env bash
set -euo pipefail

source ./build/.env

cd $1

IMAGE="$NEXUS_DOCKER_REPO/$(basename $1):$2"

docker buildx build \
  --builder multiarch-builder \
  --platform "$PLATFORM" \
  --build-arg PACKAGE_NAME=$(basename $1 | tr '-' '_') \
  --build-arg VERSION=$2 \
  --build-arg NEXUS_PYPI_SIMPLE_URL=$NEXUS_PYPI_SIMPLE_URL \
  --build-arg NEXUS_USERNAME=$NEXUS_USERNAME \
  --build-arg NEXUS_PASSWORD=$NEXUS_PASSWORD \
  --cache-from=type=local,src=.buildx-cache \
  --cache-to=type=local,dest=.buildx-cache,mode=max \
  -t "$IMAGE" \
  --push \
  .

echo "Docker image pushed:"
echo "$IMAGE"