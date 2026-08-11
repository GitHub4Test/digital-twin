#!/usr/bin/env bash
set -e

PROTO_ROOT="protos"
OUT="generated_output"

mkdir -p "$OUT"
touch "$OUT/__init__.py"

# Step 1: generate pb2 + grpc stubs
python3 -m grpc_tools.protoc \
  -I "$PROTO_ROOT" \
  --python_out="$OUT" \
  --grpc_python_out="$OUT" \
  --pyi_out="$OUT" \
  "$PROTO_ROOT/sensor/v1/sensor.proto"

# Step 2: fix imports — use grpc_tools.protoc here too, NOT bare `protoc`
python3 -m grpc_tools.protoc \
  -I "$PROTO_ROOT" \
  --include_imports \
  --descriptor_set_out=/dev/stdout \
  "$PROTO_ROOT/sensor/v1/sensor.proto" \
| protol --create-package --in-place --python-out "$OUT" raw