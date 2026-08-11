#!/usr/bin/env bash
set -euo pipefail

echo ""
echo "==> [$1] Build package started"

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

cd $1
rm -rf dist build *.egg-info

poetry config repositories.nexus $NEXUS_PYPI_REPO

poetry build
poetry publish -r nexus -u "$NEXUS_USERNAME" -p "$NEXUS_PASSWORD"

echo "==> [$1] Build package completed and pushed to nexus"

