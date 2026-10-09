#!/usr/bin/env bash
# build.sh — build the openKylin dev container image (Linux / openKylin WSL path).
# Detects podman, verifies the base image locally (no implicit pull unless
# PULL_BASE=1), then builds localhost/openkylin-dev:<TAG> from the project root.
set -euo pipefail

TAG="${TAG:-3.0}"
IMAGE="localhost/openkylin-dev:${TAG}"
# Base: locally imported openKylin 3.0 WSL rootfs (localhost/openkylin:3.0),
# local-only (not on any registry). Official registry 'latest' resolves to
# 2.0 SP1 LTS, not 3.0, hence the local import is the genuine 3.0 base.
BASE_IMAGE="${BASE_IMAGE:-localhost/openkylin:3.0}"
NO_CACHE="${NO_CACHE:-}"
PULL_BASE="${PULL_BASE:-0}"

command -v podman >/dev/null 2>&1 || { echo "[BUILD] FAIL: podman not found" >&2; exit 2; }
echo "[BUILD] podman: $(command -v podman)"

if ! podman info >/dev/null 2>&1; then
    echo "[BUILD] FAIL: podman backend unreachable (is the rootless socket up?)" >&2
    exit 2
fi

if ! podman image exists "$BASE_IMAGE" >/dev/null 2>&1; then
    if [ "$PULL_BASE" = "1" ]; then
        echo "[BUILD] pulling base image: $BASE_IMAGE"
        podman pull "$BASE_IMAGE"
    else
        echo "[BUILD] FAIL: base image '$BASE_IMAGE' missing locally." >&2
        echo "[BUILD]   the base is the locally imported WSL rootfs (no registry);" >&2
        echo "[BUILD]   import it first or set BASE_IMAGE to a registry image" >&2
        exit 2
    fi
fi

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CTX="$(dirname "$HERE")"

# Force docker image format: buildah inherits OCI format from the imported
# base image, and OCI silently drops SHELL/HEALTHCHECK instructions (observed
# on openKylin WSL-import base). Docker format honors both.
CMD=(podman build --format docker -t "$IMAGE" "$CTX")
[ -n "$NO_CACHE" ] && CMD+=(--no-cache)

echo "[BUILD] ${CMD[*]}"
"${CMD[@]}"

echo "[BUILD] OK: $IMAGE"
