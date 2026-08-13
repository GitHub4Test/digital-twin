#!/usr/bin/env bash
set -e

PROTO_ROOT="protos"

API_GATEWAY=apps/backend/api-gateway/api_gateway
SENSOR_SERVICE=apps/backend/sensor-service/sensor_service

for OUT in "$API_GATEWAY" "$SENSOR_SERVICE"; do

  mkdir -p "$OUT/generated"
  touch "$OUT/generated/__init__.py"

  # Step 1: generate pb2 + grpc stubs
  python3 -m grpc_tools.protoc \
    -I "$PROTO_ROOT" \
    --python_out="$OUT/generated" \
    --grpc_python_out="$OUT/generated" \
    --pyi_out="$OUT/generated" \
    "$PROTO_ROOT/sensor/v1/sensor.proto"

  # Step 2: fix imports — use grpc_tools.protoc here too, NOT bare `protoc`
  python3 -m grpc_tools.protoc \
    -I "$PROTO_ROOT" \
    --include_imports \
    --descriptor_set_out=/dev/stdout \
    "$PROTO_ROOT/sensor/v1/sensor.proto" \
  | protol --create-package --in-place --python-out "$OUT/generated" raw

done