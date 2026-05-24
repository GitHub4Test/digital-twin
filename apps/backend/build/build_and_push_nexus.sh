#!/usr/bin/env bash
set -euo pipefail

BUILD_SCRIPTS_PATH=$(cd .. && pwd)
echo "Build Scripts Path: $BUILD_SCRIPTS_PATH"
cd "$BUILD_SCRIPTS_PATH"

APPS_PATH="$BUILD_SCRIPTS_PATH/backend"

./build/build_common.sh

# api_service
./build/build_package.sh "$APPS_PATH/api-service"
./build/publish_package.sh "$APPS_PATH/api-service"
./build/build_docker.sh "$APPS_PATH/api-service"

# edge_server
./build/build_package.sh "$APPS_PATH/edge-server"
./build/publish_package.sh "$APPS_PATH/edge-server"
./build/build_docker.sh "$APPS_PATH/edge-server"