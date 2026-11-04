#!/usr/bin/env bash
# run.sh — main entry point for the npu-toolchain variant.
#
# This script runs on the server host itself (ai@10.16.11.3): /media/pc/data/ai
# is a local directory, so no remote hop, no extra mount layer and no filesystem
# type assertion is needed. The script checks that the source exists, prepares
# the workspace scratch directory, starts the container with the rootless
# contract flags, and proves that the bind mount is writable with the expected
# ownership before reporting success.
#
# Usage: bash scripts/run.sh [up|down|shell|status]
set -Eeuo pipefail

# ---------------------------------------------------------------------------
# pinned names / paths (override through the environment if really needed)
# ---------------------------------------------------------------------------
IMAGE="${IMAGE:-localhost/openkylin-npu-toolchain:3.0}"
CTR="${CTR:-npu-toolchain}"
VOL="${VOL:-npu-build}"
SRC="${SRC:-/media/pc/data/ai}"   # host workspace, bind-mounted read-write
# Podman intermediate copy dir (containers-5.conf image_copy_tmp_dir). Created
# on demand here; the podman configuration itself is never modified.
IMAGE_TMP="${IMAGE_TMP:-/media/pc/data/ai/.temp/podman-image-tmp}"
SCRATCH_HOST="${SCRATCH_HOST:-$SRC/.temp/npu-toolchain}"
# Probes must never be dropped at the workspace root (.temp/ is the only
# allowed scratch location in the workspace).
PROBE_DIR="/workspace/ai/.temp/npu-toolchain"

step_names=()
step_results=()
step_notes=()

usage() {
    cat <<'EOF'
Usage: bash scripts/run.sh [command]

Commands:
  up       (default) preflight -> image check -> volume -> run -> mount probe
  down     remove the container (the npu-build volume is kept)
  shell    open an interactive bash inside the running container
  status   show container / volume / image state
EOF
}

# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------
run_step() {
    local name="$1"
    shift
    local started=$SECONDS
    local rc
    printf '\n[STEP] %-14s begin\n' "$name"
    set +e
    "$@"
    rc=$?
    set -e
    local elapsed=$((SECONDS - started))
    step_names+=("$name")
    if [ "$rc" -eq 0 ]; then
        step_results+=("PASS")
        printf '[STEP] %-14s PASS (%ss)\n' "$name" "$elapsed"
    else
        step_results+=("FAIL")
        printf '[STEP] %-14s FAIL rc=%s (%ss)\n' "$name" "$rc" "$elapsed" >&2
    fi
    step_notes+=("${elapsed}s")
    return "$rc"
}

print_summary() {
    echo
    echo "================ SUMMARY ================"
    printf '%-16s %-6s %s\n' "STEP" "RESULT" "TIME"
    local i
    for i in "${!step_names[@]}"; do
        printf '%-16s %-6s %s\n' "${step_names[$i]}" "${step_results[$i]}" "${step_notes[$i]}"
    done
    echo "========================================="
    local r
    for r in "${step_results[@]}"; do
        [ "$r" = "PASS" ] || return 1
    done
    return 0
}

fail_fast() {
    echo >&2
    print_summary >&2 || true
    echo "[run] ABORTED: fix the FAIL rows above" >&2
    exit 1
}

# ---------------------------------------------------------------------------
# steps
# ---------------------------------------------------------------------------

# 1. Preflight: the workspace source must exist and be readable. A missing or
#    unreadable source is a hard error with an explicit fix hint — never a
#    silent downgrade to a smaller mount set.
preflight() {
    if [ ! -d "$SRC" ]; then
        echo "  FAIL: workspace source $SRC does not exist" >&2
        echo "  FIX : run this script on the server host (ai@10.16.11.3) where" >&2
        echo "        /media/pc/data/ai is a local directory, then re-run." >&2
        return 1
    fi
    if [ ! -r "$SRC" ]; then
        echo "  FAIL: workspace source $SRC is not readable by uid $(id -u)" >&2
        echo "  FIX : ls -ld $SRC   # check ownership/mode, then re-run" >&2
        return 1
    fi
    echo "  $SRC readable (uid $(id -u))"
}

# 2. Create the scratch locations used before/after the container starts.
prepare_dirs() {
    mkdir -p "$IMAGE_TMP" "$SCRATCH_HOST"
    echo "  image tmp: $IMAGE_TMP"
    echo "  scratch  : $SCRATCH_HOST"
}

# 3. The image must already exist locally (never pull implicitly).
ensure_image() {
    if podman image exists "$IMAGE" >/dev/null 2>&1; then
        echo "  image $IMAGE present"
        return 0
    fi
    echo "  FAIL: image $IMAGE is missing" >&2
    echo "  FIX : bash scripts/build-image.sh" >&2
    return 1
}

# 4. Ensure the named build volume exists (artefacts stay off the workspace).
ensure_volume() {
    # `podman volume exists` was added in podman 4.5; inspect covers older ones.
    if podman volume exists "$VOL" >/dev/null 2>&1 || podman volume inspect "$VOL" >/dev/null 2>&1; then
        echo "  volume $VOL already exists"
    else
        podman volume create "$VOL" >/dev/null
        echo "  volume $VOL created"
    fi
}

# 5. Start the container with the rootless contract flags. No port is
#    published; the image CMD keeps the container idle.
run_container() {
    if podman container exists "$CTR" >/dev/null 2>&1; then
        echo "  removing stale container $CTR"
        podman rm -f "$CTR" >/dev/null
    fi

    local -a args=(
        run -d
        --pull=never
        --name "$CTR"
        --device /dev/fuse
        --security-opt label=disable
        --cgroupns=host
        --userns=keep-id
        --mount "type=bind,source=$SRC,target=/workspace/ai,bind-propagation=rshared"
        -v "$VOL:/opt/build"
        "$IMAGE"
    )

    echo "  podman ${args[*]}"
    podman "${args[@]}" >/dev/null
    echo "  container $CTR started"
}

# 6. Prove the bind mount is writable inside the container: chmod and symlink
#    must stick, and the file must be owned by uid 1006 (host uid mapped through
#    userns keep-id). The same file must then be visible on the host.
probe_mount() {
    local out
    set +e
    out="$(podman exec "$CTR" bash -c '
        mkdir -p /workspace/ai/.temp/npu-toolchain
        cd /workspace/ai/.temp/npu-toolchain
        touch .probe
        chmod 700 .probe
        ln -sfn .probe .probe-link
        stat -c "%a %u" .probe
    ' 2>&1)"
    local rc=$?
    set -e
    if [ "$rc" -ne 0 ]; then
        printf '  FAIL: in-container probe failed (rc=%s)\n%s\n' "$rc" "$out" >&2
        return 1
    fi
    out="$(printf '%s\n' "$out" | tail -n 1)"
    echo "  in-container stat: $out"
    if [ "$out" != "700 1006" ]; then
        echo "  FAIL: expected mode/owner '700 1006', got '$out'" >&2
        return 1
    fi

    if [ ! -f "$SCRATCH_HOST/.probe" ]; then
        echo "  FAIL: host-side $SCRATCH_HOST/.probe not visible" >&2
        return 1
    fi
    echo "  host-side $SCRATCH_HOST/.probe visible"
}

# 7. Report the runtime handles.
summary() {
    podman ps --filter "name=^${CTR}$" --format '  container: {{.Names}}  {{.Status}}'
    podman volume inspect "$VOL" --format '  volume   : {{.Name}}' 2>/dev/null \
        || echo "  volume   : $VOL (inspect failed)"
    echo "  workspace: /workspace/ai (rw bind <- $SRC)"
    echo "  builddir : /opt/build (volume $VOL)"
    podman exec "$CTR" bash -c 'python --version' || return 1
}

# ---------------------------------------------------------------------------
# commands
# ---------------------------------------------------------------------------
do_up() {
    run_step preflight preflight || fail_fast
    run_step prepare_dirs prepare_dirs || fail_fast
    run_step ensure_image ensure_image || fail_fast
    run_step ensure_volume ensure_volume || fail_fast
    run_step run_container run_container || fail_fast
    run_step probe_mount probe_mount || fail_fast
    run_step summary summary || fail_fast
    print_summary
    echo "[run] OK: $CTR is up ($IMAGE)"
}

do_down() {
    if podman container exists "$CTR" >/dev/null 2>&1; then
        podman rm -f "$CTR" >/dev/null
        echo "[run] removed container $CTR"
    else
        echo "[run] no container named $CTR"
    fi
    echo "[run] volume $VOL kept (drop it with: podman volume rm $VOL)"
}

do_shell() {
    if ! podman container exists "$CTR" >/dev/null 2>&1; then
        echo "[run] FAIL: container $CTR not found (run: bash scripts/run.sh up)" >&2
        exit 2
    fi
    exec podman exec -it "$CTR" bash
}

do_status() {
    podman ps -a --filter "name=^${CTR}$" --format 'table {{.Names}}\t{{.Status}}'
    podman volume inspect "$VOL" --format 'volume {{.Name}} {{.Mountpoint}}' 2>/dev/null \
        || echo "volume $VOL absent"
    if podman image exists "$IMAGE" >/dev/null 2>&1; then
        echo "image $IMAGE present"
    else
        echo "image $IMAGE absent (run: bash scripts/build-image.sh)"
    fi
}

main() {
    local cmd="${1:-up}"
    case "$cmd" in
        up) shift || true; do_up ;;
        down) do_down ;;
        shell) do_shell ;;
        status) do_status ;;
        -h | --help | help) usage ;;
        *)
            echo "[run] unknown command: $cmd" >&2
            usage >&2
            exit 2
            ;;
    esac
}

main "$@"