#!/bin/bash
set -e

WORKSPACE="/mnt/d/spaces/SpecWeave/apps/docker-images/devcontainer-base"

# 1. Ensure daemon.json is in place
mkdir -p /etc/docker
cp "$WORKSPACE/daemon.json" /etc/docker/daemon.json
echo "=== daemon.json configured ==="

# 2. Kill any existing dockerd
pkill dockerd 2>/dev/null || true
sleep 1
rm -f /var/run/docker.sock

# 3. Start dockerd
echo "=== Starting dockerd... ==="
nohup dockerd >/tmp/dockerd.log 2>&1 &

# 4. Wait for Docker to be ready
for i in $(seq 1 30); do
  if docker info >/dev/null 2>&1; then
    echo "Docker ready after ${i}s"
    break
  fi
  sleep 1
done

# 5. Verify Docker works
echo "=== Docker version ==="
docker version --format '{{.Server.Version}}'
echo ""
echo "=== Docker info (mirrors) ==="
docker info 2>&1 | grep -A5 "Registry Mirrors" || true
