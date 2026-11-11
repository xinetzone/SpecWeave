#!/usr/bin/env bash
# build-l1.sh — build the L1 self-contained npu-toolchain image.
#
# Difference from build-image.sh: that one builds the *environment* image
# (python/cmake/ninja/gcc only, toolchain arrives through the npu-build volume
# at run time). This one adds the derived layer of Containerfile.l1, which
# copies the volume entities into the image, so the result runs with no mount.
#
# Both sources are read-only build-time mounts; nothing is copied to the build
# context and the volume itself is never modified.
set -Eeuo pipefail

BASE_IMAGE="${BASE_IMAGE:-localhost/openkylin-npu-toolchain:3.0}"
IMAGE="${IMAGE:-localhost/openkylin-npu-toolchain:3.0-l1}"
VOLUME_DATA="${VOLUME_DATA:-/media/pc/data/ai/.agents/podman-storage/storage/volumes/npu-build/_data}"
TVM_PYTHON_SRC="${TVM_PYTHON_SRC:-/media/pc/data/ai/notebook/libs/npu_tvm/python}"
IMAGE_TMP="${IMAGE_TMP:-/media/pc/data/ai/.temp/podman-image-tmp}"

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CTX="$(dirname "$HERE")"

command -v podman >/dev/null 2>&1 || { echo "[L1] FAIL: podman not found" >&2; exit 2; }
podman info >/dev/null 2>&1 || { echo "[L1] FAIL: podman backend unreachable" >&2; exit 2; }
mkdir -p "$IMAGE_TMP"

for p in "$VOLUME_DATA/npu_tvm" "$VOLUME_DATA/llvm22" "$TVM_PYTHON_SRC/tvm"; do
    [ -d "$p" ] || { echo "[L1] FAIL: source missing: $p" >&2; exit 2; }
done
podman image exists "$BASE_IMAGE" || { echo "[L1] FAIL: base image $BASE_IMAGE missing" >&2; exit 2; }

echo "[L1] base : $BASE_IMAGE"
echo "[L1] src  : $VOLUME_DATA -> /src:ro"
echo "[L1] src  : $TVM_PYTHON_SRC -> /tvm-python:ro"
echo "[L1] out  : $IMAGE"

podman build --format docker \
    --build-arg "BASE_IMAGE=$BASE_IMAGE" \
    --volume "${VOLUME_DATA}:/src:ro" \
    --volume "${TVM_PYTHON_SRC}:/tvm-python:ro" \
    -t "$IMAGE" -f "$CTX/Containerfile.l1" "$CTX"

# ---------------------------------------------------------------------------
# Post-build L1 gate. Every check runs with no volume and no bind mount, which
# is exactly the receiving-host situation the L1 level claims to support.
# --userns=keep-id is not used: it would trigger a full rootfs chown-by-maps
# on a 18 GB image, and these checks only execute binaries and never write.
# ---------------------------------------------------------------------------
l1() { podman run --rm --pull=never --network none "$IMAGE" "$@" 2>&1; }

names=(); results=(); details=()
record() { names+=("$1"); results+=("$2"); details+=("$3"); printf '[L1] %-4s %-10s %s\n' "$2" "$1" "$3"; }

echo "[L1] gate: mount-free tvm / llvm / linkage"

if out="$(l1 python -c 'import tvm; print(tvm.__file__)')" && [ -n "$out" ]; then
    record import-tvm PASS "$out"
else
    record import-tvm FAIL "${out:-unavailable}"
fi

if v="$(l1 /opt/build/llvm22/bin/llvm-config --version)" && [ "$v" = "22.1.8" ]; then
    record llvm-config PASS "$v"
else
    record llvm-config FAIL "${v:-unavailable} (expected 22.1.8)"
fi

if out="$(l1 ldd /opt/build/npu_tvm/libtvm.so)" && ! printf '%s\n' "$out" | grep -q 'not found'; then
    record libtvm-ldd PASS "$(printf '%s\n' "$out" | grep 'libLLVM.so' | awk '{print $3}')"
else
    record libtvm-ldd FAIL "unresolved shared library"
fi

if out="$(l1 bash -c 'ls /opt/build | tr "\n" " "')"; then
    record opt-build PASS "$out"
else
    record opt-build FAIL "unavailable"
fi

echo
echo "================ SUMMARY ================"
printf '%-12s %-6s %s\n' "CHECK" "RESULT" "DETAIL"
i=0
while [ "$i" -lt "${#names[@]}" ]; do
    printf '%-12s %-6s %s\n' "${names[$i]}" "${results[$i]}" "${details[$i]}"
    i=$((i + 1))
done
echo "========================================="

failed=0
for r in "${results[@]}"; do
    [ "$r" = "PASS" ] || failed=$((failed + 1))
done
if [ "$failed" -ne 0 ]; then
    echo "[L1] FAIL: $failed gate check(s) failed" >&2
    exit 1
fi

echo "[L1] image id  : $(podman image inspect --format '{{.Id}}' "$IMAGE")"
echo "[L1] image size: $(podman image inspect --format '{{.Size}}' "$IMAGE") bytes"
echo "[L1] OK: $IMAGE"