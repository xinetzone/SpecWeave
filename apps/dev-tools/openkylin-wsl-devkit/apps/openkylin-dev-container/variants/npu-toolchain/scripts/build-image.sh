#!/usr/bin/env bash
# build-image.sh — build localhost/openkylin-npu-toolchain:3.0 from this variant.
#
# The baseline image localhost/openkylin:3.0 must already exist locally: it is
# produced by importing the offline package
# /media/pc/data/ai/.agents/wsl-images/openKylin-3.0-desktop-wsl-amd64.wsl
# (gzip-compressed rootfs tar). This script never pulls implicitly and never
# builds that baseline itself.
#
# --format docker is passed explicitly: buildah inherits the OCI format of the
# imported base image, and OCI silently drops SHELL/HEALTHCHECK instructions.
set -Eeuo pipefail

BASE_IMAGE="${BASE_IMAGE:-localhost/openkylin:3.0}"
IMAGE="${IMAGE:-localhost/openkylin-npu-toolchain:3.0}"
IMAGE_TMP="${IMAGE_TMP:-/media/pc/data/ai/.temp/podman-image-tmp}"
NO_CACHE="${NO_CACHE:-}"
MINIFORGE_URL="https://mirrors.ustc.edu.cn/github-release/conda-forge/miniforge/LatestRelease/Miniforge3-Linux-x86_64.sh"
WSL_PACKAGE="/media/pc/data/ai/.agents/wsl-images/openKylin-3.0-desktop-wsl-amd64.wsl"

command -v podman >/dev/null 2>&1 || { echo "[BUILD] FAIL: podman not found" >&2; exit 2; }

if ! podman info >/dev/null 2>&1; then
    echo "[BUILD] FAIL: podman backend unreachable (is the rootless socket up?)" >&2
    exit 2
fi

# Podman stages image copies under image_copy_tmp_dir (containers-5.conf);
# import/commit-style operations fail when it does not exist.
mkdir -p "$IMAGE_TMP"

if ! podman image exists "$BASE_IMAGE" >/dev/null 2>&1; then
    echo "[BUILD] FAIL: baseline image '$BASE_IMAGE' is missing locally." >&2
    echo "[BUILD]   Import it once from the offline package:" >&2
    echo "[BUILD]     gunzip -c $WSL_PACKAGE \\" >&2
    echo "[BUILD]       | podman import - $BASE_IMAGE" >&2
    echo "[BUILD]   (only needed once; this script never pulls a base image)" >&2
    exit 2
fi

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CTX="$(dirname "$HERE")"

# Resolve the Miniforge digest from the USTC sidecar files when reachable; the
# Containerfile then verifies the download instead of only syntax-checking it.
resolve_sha() {
    local ext url tmp expected
    command -v curl >/dev/null 2>&1 || return 1
    for ext in .sha256 .sha256sum; do
        url="${MINIFORGE_URL}${ext}"
        tmp="$(mktemp)"
        if curl -fsSL --retry 2 -o "$tmp" "$url" 2>/dev/null && [ -s "$tmp" ]; then
            expected="$(awk 'NR==1{print $1}' "$tmp")"
            rm -f "$tmp"
            if [ -n "$expected" ]; then
                printf '%s' "$expected"
                return 0
            fi
        fi
        rm -f "$tmp"
    done
    return 1
}

BUILD_ARGS=()
if SHA="$(resolve_sha)"; then
    echo "[BUILD] miniforge sha256 (sidecar): $SHA"
    BUILD_ARGS+=(--build-arg "MINIFORGE_SHA256=$SHA")
else
    echo "[BUILD] no digest sidecar reachable; the Containerfile falls back to"
    echo "[BUILD] bash -n and prints the real sha256 in the build log."
fi

CMD=(podman build --format docker -t "$IMAGE" -f "$CTX/Containerfile")
if [ "${#BUILD_ARGS[@]}" -gt 0 ]; then
    CMD+=("${BUILD_ARGS[@]}")
fi
if [ -n "$NO_CACHE" ]; then
    CMD+=(--no-cache)
fi
CMD+=("$CTX")

echo "[BUILD] ${CMD[*]}"
"${CMD[@]}"

echo "[BUILD] image id: $(podman image inspect --format '{{.Id}}' "$IMAGE")"

# ---------------------------------------------------------------------------
# Post-build gate: python / cmake / ninja / sys.prefix
# Each check runs in a throwaway container. --userns=keep-id is deliberately
# NOT passed here: the image is a 13 GB imported rootfs, and on this storage
# backend keep-id makes podman run storage-chown-by-maps over the whole merged
# rootfs, holding the storage lock for many minutes and copy-uping into a root
# filesystem that is ~93% full. The version gate only executes binaries and
# never writes, so the plain (root) container is equivalent for it.
# ---------------------------------------------------------------------------
gate_out() {
    podman run --rm --pull=never "$IMAGE" "$@" 2>&1
}

# ge HAVE MIN -> true when HAVE >= MIN (version sort).
ge() {
    [ "$(printf '%s\n%s\n' "$2" "$1" | sort -V | head -n1)" = "$2" ]
}

gate_names=()
gate_results=()
gate_details=()

record() {
    gate_names+=("$1")
    gate_results+=("$2")
    gate_details+=("$3")
    printf '[BUILD] %-4s %-12s %s\n' "$2" "$1" "$3"
}

echo "[BUILD] gate: python / cmake / ninja / sys.prefix"

if v="$(gate_out python --version | awk '{print $2}')" && [ -n "$v" ] && ge "$v" "3.14"; then
    record python PASS "$v"
else
    record python FAIL "${v:-unavailable} (need >= 3.14)"
fi

if v="$(gate_out cmake --version | head -n1 | awk '{print $3}')" && [ -n "$v" ] && ge "$v" "3.18"; then
    record cmake PASS "$v"
else
    record cmake FAIL "${v:-unavailable} (need >= 3.18)"
fi

if v="$(gate_out ninja --version)" && [ -n "$v" ] && ge "$v" "1.10"; then
    record ninja PASS "$v"
else
    record ninja FAIL "${v:-unavailable} (need >= 1.10)"
fi

if v="$(gate_out python -c 'import sys; print(sys.prefix)')" && [ "$v" = "/opt/conda/envs/main" ]; then
    record sys-prefix PASS "$v"
else
    record sys-prefix FAIL "${v:-unavailable} (expected /opt/conda/envs/main)"
fi

echo
echo "================ SUMMARY ================"
printf '%-12s %-6s %s\n' "CHECK" "RESULT" "DETAIL"
i=0
while [ "$i" -lt "${#gate_names[@]}" ]; do
    printf '%-12s %-6s %s\n' "${gate_names[$i]}" "${gate_results[$i]}" "${gate_details[$i]}"
    i=$((i + 1))
done
echo "========================================="

failed=0
for r in "${gate_results[@]}"; do
    [ "$r" = "PASS" ] || failed=$((failed + 1))
done
if [ "$failed" -ne 0 ]; then
    echo "[BUILD] FAIL: $failed gate check(s) failed" >&2
    exit 1
fi

echo "[BUILD] OK: $IMAGE"