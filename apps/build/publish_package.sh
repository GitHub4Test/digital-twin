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

cd $1

poetry config repositories.nexus $NEXUS_PYPI_REPO
poetry publish -r nexus -u "$NEXUS_USERNAME" -p "$NEXUS_PASSWORD"