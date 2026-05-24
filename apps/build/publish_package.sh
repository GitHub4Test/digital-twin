#!/usr/bin/env bash
set -euo pipefail

set -a
[ -f ./build/.env ] && source ./build/.env
[ -f ./build/.env.local ] && source ./build/.env.local
set +a

: "${NEXUS_USERNAME:?NEXUS_USERNAME is required}"
: "${NEXUS_PASSWORD:?NEXUS_PASSWORD is required}"

cd $1

poetry config repositories.nexus $NEXUS_PYPI_REPO
poetry publish -r nexus -u "$NEXUS_USERNAME" -p "$NEXUS_PASSWORD"