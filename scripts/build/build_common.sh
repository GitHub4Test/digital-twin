#!/usr/bin/env bash
set -euo pipefail

echo ""
echo "==> Build common started"

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

echo "==> Build common ended"
