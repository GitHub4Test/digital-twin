#!/usr/bin/env bash
set -euo pipefail

####### ONLY ONCE
cat > buildkitd.toml <<'EOF'
[registry."192.168.178.59:5001"]
  http = true
  insecure = true
EOF

docker buildx rm multiarch-builder

docker buildx create \
  --name multiarch-builder \
  --driver docker-container \
  --config ./buildkitd.toml \
  --use

docker buildx inspect --bootstrap
####### ONLY ONCE

# frontend
./build/build_package.sh digital-twin-app
./build/publish_package.sh digital-twin-app
./build/build_docker.sh digital-twin-app 1.0.0