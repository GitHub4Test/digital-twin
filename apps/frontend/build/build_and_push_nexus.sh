#!/usr/bin/env bash
set -euo pipefail

echo "==> Frontend: Build has been started"

BUILD_SCRIPTS_PATH=scripts/build

APPS_PATH="apps/frontend/digital-twin-app"

./$BUILD_SCRIPTS_PATH/build_common.sh

./$BUILD_SCRIPTS_PATH/build_publish_package.sh "$APPS_PATH"
./$BUILD_SCRIPTS_PATH/build_docker.sh "$APPS_PATH"

echo "==> Frontend: Build has been ended"