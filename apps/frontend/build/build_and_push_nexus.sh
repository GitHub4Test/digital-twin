#!/usr/bin/env bash
set -euo pipefail

BUILD_SCRIPTS_PATH=$(cd .. && pwd)
echo "Build Scripts Path: $BUILD_SCRIPTS_PATH"
cd "$BUILD_SCRIPTS_PATH"

APPS_PATH="$BUILD_SCRIPTS_PATH/frontend"

./build/build_common.sh

# frontend
./build/build_package.sh $APPS_PATH/digital-twin-app
./build/publish_package.sh $APPS_PATH/digital-twin-app
./build/build_docker.sh $APPS_PATH/digital-twin-app