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
  --secret id=nexus_ca_cert,env=NEXUS_CA_CERT \
  --secret id=nexus_username,env=NEXUS_USERNAME \
  --secret id=nexus_password,env=NEXUS_PASSWORD \
  -t "$IMAGE" \
  -t "$NEXUS_DOCKER_REPO/$(basename "$SERVICE_PATH"):latest" \
  --load \
  .

echo "Scanning Docker image for vulnerabilities..."
if ! ../../scripts/security/run-trivy-image.sh "$IMAGE"; then
  echo "Docker image scan failed; aborting push." >&2
  exit 1
fi

echo "Docker image scan passed; pushing:"
echo "$IMAGE"

docker push "$IMAGE"
docker push "$NEXUS_DOCKER_REPO/$(basename "$SERVICE_PATH"):latest"