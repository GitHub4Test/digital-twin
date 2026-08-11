#!/usr/bin/env bash
set -euo pipefail

echo "==> Backend: Build has been started"

BUILD_SCRIPTS_PATH=scripts/build

APPS_PATH="apps/backend"

./$BUILD_SCRIPTS_PATH/build_common.sh

API_GATEWAY=api-gateway
SENSOR_SERVICE=sensor-service
EDGE_SERVER=edge-server

for APP in "$API_GATEWAY" "$SENSOR_SERVICE" "$EDGE_SERVER"; do
    echo "==> [$APP] Building and pushing package for app"

    ./$BUILD_SCRIPTS_PATH/build_publish_package.sh "$APPS_PATH/$APP"
    ./$BUILD_SCRIPTS_PATH/build_docker.sh "$APPS_PATH/$APP"
done

echo "==> Backend: Build has been ended"