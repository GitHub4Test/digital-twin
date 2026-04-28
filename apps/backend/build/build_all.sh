#!/usr/bin/env bash
set -euo pipefail

####### ONLY ONCE
cat > buildkitd.toml <<'EOF'
[registry."192.168.178.59:5001"]
  http = true
  insecure = true
EOF

docker buildx rm multiarch-builder || true

docker buildx create \
  --name multiarch-builder \
  --driver docker-container \
  --config ./buildkitd.toml \
  --use

docker buildx inspect --bootstrap
####### ONLY ONCE

# api_service
./build/build_package.sh api-service
./build/publish_package.sh api-service
./build/build_docker.sh api-service 1.0.0

# edge_server
./build/build_package.sh edge-server
./build/publish_package.sh edge-server
./build/build_docker.sh edge-server 0.1.0