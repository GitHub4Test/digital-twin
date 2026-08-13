#!/usr/bin/env bash
set -euo pipefail

echo ""

# Load non-secret config only
set -a
[ -f ./scripts/build/.env ] && source ./scripts/build/.env
set +a

# Load local secrets only outside GitHub Actions
if [ -z "${GITHUB_ACTIONS:-}" ] && [ -f ./scripts/build/.env.local ]; then
  set -a
  source ./scripts/build/.env.local
  set +a
fi

: "${NEXUS_USERNAME:?NEXUS_USERNAME is required}"
: "${NEXUS_PASSWORD:?NEXUS_PASSWORD is required}"

SERVICE_PATH="$1"
VERSION="$(cd "$SERVICE_PATH" &&poetry version -s)"
PACKAGE_NAME="$(basename "$SERVICE_PATH")"
IMAGE="$NEXUS_DOCKER_REPO/$(basename "$SERVICE_PATH"):$VERSION"

LATEST_TAG="$NEXUS_DOCKER_REPO/$(basename "$SERVICE_PATH"):latest"
CACHE_TAG="$NEXUS_DOCKER_REPO/$(basename "$SERVICE_PATH"):buildcache"
 
echo "$NEXUS_PASSWORD" | docker login "$NEXUS_DOCKER_REPO" \
  -u "$NEXUS_USERNAME" \
  --password-stdin

echo "==> ==> 1. $PACKAGE_NAME: Building Docker image for platforms - $PLATFORMS"

BUILD_ARGS=(
  --builder multiarch-builder
  -f "$SERVICE_PATH/Dockerfile"
  --progress=plain \
  --cache-from "type=registry,ref=$CACHE_TAG"
  --cache-to "type=registry,ref=$CACHE_TAG,mode=max"
  --build-arg "NEXUS_PYPI_SIMPLE_URL=$NEXUS_PYPI_SIMPLE_URL"
  --build-arg "PACKAGE_NAME=$PACKAGE_NAME"
  --build-arg "VERSION=$VERSION"
  --secret "id=nexus_username,env=NEXUS_USERNAME"
  --secret "id=nexus_password,env=NEXUS_PASSWORD"
  --build-context service="$SERVICE_PATH"  
)
 
TMP_DIR="$(mktemp -d)" 

# build temporary tar ball images for each platform and scan it before pushing it nexus later
for PLATFORM in $(echo "$PLATFORMS" | tr ',' ' '); do
  echo "==> ==> 2. Scanning platform: $PLATFORM"

  SAFE_NAME="$(echo "$PLATFORM" | tr '/' '-')"
  TARBALL="$TMP_DIR/image-$SAFE_NAME.tar"

  docker buildx build \
    --platform "$PLATFORM" \
    "${BUILD_ARGS[@]}" \
    -t "$IMAGE" \
    --output "type=docker,dest=$TARBALL" \
    .
 
  # scan using trivy 
  if ! ./scripts/security/run-trivy-image.sh $TARBALL; then
    echo "==> ==> !! Trivy found vulnerabilities for $PLATFORM"
    exit 1
  fi

  echo "==> ==> 3. Scanning platform: $PLATFORM passed."

done

echo "==> ==> 4. All platform scans passed!"

docker buildx build \
  --platform "$PLATFORMS" \
  "${BUILD_ARGS[@]}" \
  -t "$IMAGE" \
  -t "$LATEST_TAG" \
  --push \
  .

echo "==> $PACKAGE_NAME: Docker image is build and pushed to nexus!"