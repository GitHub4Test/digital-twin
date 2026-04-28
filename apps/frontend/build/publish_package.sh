#!/usr/bin/env bash
set -euo pipefail

source ./build/.env

cd $1

poetry config repositories.nexus $NEXUS_PYPI_REPO
poetry publish -r nexus -u "$NEXUS_USERNAME" -p "$NEXUS_PASSWORD"