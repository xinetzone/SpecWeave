#!/usr/bin/env bash
# build-minimal-base.sh — rebuild the two minimal baselines from the official
# openKylin 3.0 WSL rootfs.
#
# Produces, in order:
#   S1  localhost/openkylin:3.0-minimal       <- podman import of the .wsl file
#   S2  localhost/openkylin:3.0-minimal-gcc   <- S1 + gcc 15.2.0 (25 apt packages)
#
# Why S2 exists:
#   The official minimal rootfs ships no compiler, while the npu-toolchain
#   Containerfile gate runs `gcc --version`. The old full-desktop base carried
#   gcc; this layer restores the same compiler semantics on the minimal base.
#   The compiler stays in the final image on purpose (the container builds
#   npu_tvm), so there is no purge and no autoremove.
#
# Source reachability (measured 2026-11-05):
#   - archive.build.openkylin.top -> connection reset
#   - ppa.build.openkylin.top     -> connection timeout
#   - mirrors.aliyun.com/openkylin -> reachable (huanghe/Release 200)
#   The rootfs carries /etc/apt/sources.list.d/openkylin-anything.list pointing
#   at the unreachable ppa; it is removed first, otherwise apt stalls and then
#   fails on manpages/manpages-dev (served only by that ppa).
#
# Package pinning:
#   aliyun serves exactly the versions the old base had (gcc 4:15.2.0-5-ok3 /
#   gcc-15-x86-64-linux-gnu 15.2.0-16ok8 / libc6-dev 2.43-ok2). Only manpages +
#   manpages-dev are left out (documentation, and absent from the old container
#   too), hence --no-install-recommends with libc6-dev named explicitly:
#   libc6-dev is only a Recommends of gcc, but the headers are mandatory.
#
# Idempotence:
#   Existing tags are NOT overwritten: the step prints SKIP and exits 0, while
#   the read-only assertions and the three size metrics are still re-run so the
#   skip is evidenced. --force rebuilds and retags; the previous images remain
#   present as <none> (this script never rmi/prune anything). Before a --force
#   rebuild both tags are checked against every container (any state): a tag
#   that is in use aborts with a non-zero exit instead of being replaced.
#
# Usage:
#   bash scripts/build-minimal-base.sh [--force] [path/to/openKylin-3.0-wsl-amd64.wsl]
#
# Env overrides:
#   SRC_WSL, EXPECT_SHA256, MINIMAL_TAG, GCC_TAG, APT_MIRROR,
#   AI_ROOT, IMAGE_TMP, MIN_AVAIL_BYTES, GCC_WANT
#
# Exit codes:
#   0  both steps PASS or SKIP
#   1  a step FAILed (assertion, build, or a tag in use during --force)
#   2  usage error or preflight failure (podman / source / sha256 / disk)
set -Eeuo pipefail

AI_ROOT="${AI_ROOT:-/media/pc/data/ai}"
SRC_WSL="${SRC_WSL:-$AI_ROOT/.agents/wsl-images/openKylin-3.0-wsl-amd64.wsl}"
EXPECT_SHA256="${EXPECT_SHA256:-d6d0d708c54bbc643961aba21d74c0b18270715bdf2266ecec3bc55f486d07d4}"
MINIMAL_TAG="${MINIMAL_TAG:-localhost/openkylin:3.0-minimal}"
GCC_TAG="${GCC_TAG:-localhost/openkylin:3.0-minimal-gcc}"
APT_MIRROR="${APT_MIRROR:-https://mirrors.aliyun.com/openkylin}"
IMAGE_TMP="${IMAGE_TMP:-$AI_ROOT/.temp/podman-image-tmp}"
MIN_AVAIL_BYTES="${MIN_AVAIL_BYTES:-5368709120}"   # 5 GiB head-room for import + layer
GCC_WANT="${GCC_WANT:-15.2.0}"
GCC_PKG_COUNT=25

FORCE=0
SCRATCH=""

usage() {
    cat <<'EOF'
Usage: bash scripts/build-minimal-base.sh [--force] [SRC_WSL]

Steps:
  S1  podman import <SRC_WSL> localhost/openkylin:3.0-minimal
  S2  build localhost/openkylin:3.0-minimal-gcc on top of S1
      (gcc 15.2.0, 25 apt packages, --no-install-recommends + explicit libc6-dev)

Options:
  --force   rebuild even when the tag already exists (the old image is kept as
            <none>; nothing is deleted). Aborts if the tag is used by a container.
  -h, --help  show this help

Preconditions:
  * run on the server host ai@10.16.11.3 (local podman 5.6.2, rootless, overlay)
  * SRC_WSL readable and matching EXPECT_SHA256
  * mirrors.aliyun.com/openkylin reachable (only source used by S2)
  * graphroot has >= MIN_AVAIL_BYTES free (measured with df -B1, authoritative)

Metrics printed per step:
  df        : df -B1 before/after delta  <- AUTHORITATIVE
  images    : podman images SIZE (layer sum, rounded)
  rootfs    : du -sb --one-file-system / (image content only)
EOF
}

cleanup() {
    if [ -n "$SCRATCH" ] && [ -d "$SCRATCH" ]; then
        rm -rf "$SCRATCH"
    fi
}

# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------
df_avail() { df -B1 "$AI_ROOT" | awk 'NR==2{print $4}'; }

step_ids=() step_names=() step_results=() step_times=() step_notes=()
STEP_NOTE=""
ASSERT_FAIL=0
SUMMARY_FAILED=0

ok()  { printf '[BASE] PASS %-26s %s\n' "$1" "$2"; }
bad() { printf '[BASE] FAIL %-26s %s\n' "$1" "$2" >&2; ASSERT_FAIL=$((ASSERT_FAIL + 1)); }

run_step() {
    local id="$1" name="$2" fn="$3" started rc status
    started=$SECONDS
    STEP_NOTE=""
    printf '\n===== STEP %s %s =====\n' "$id" "$name"
    set +e
    "$fn"
    rc=$?
    set -e
    step_ids+=("$id")
    step_names+=("$name")
    step_times+=("$((SECONDS - started))s")
    case "$rc" in
        0) status=PASS ;;
        3) status=SKIP ;;
        *) status=FAIL ;;
    esac
    step_results+=("$status")
    if [ -z "$STEP_NOTE" ]; then
        if [ "$rc" -eq 0 ]; then STEP_NOTE="ok"; else STEP_NOTE="rc=$rc"; fi
    fi
    step_notes+=("$STEP_NOTE")
    printf '[BASE] %-3s %-22s ... %s (%ss)\n' "$id" "$name" "$status" "$((SECONDS - started))"
    return 0
}

last_result() {
    local i=$(( ${#step_results[@]} - 1 ))
    printf '%s' "${step_results[$i]}"
}

print_summary() {
    local i failed=0 pass=0 skip=0
    echo
    echo "================ SUMMARY ================"
    printf '%-4s %-22s %-6s %-7s %s\n' "STEP" "NAME" "RESULT" "TIME" "NOTE"
    for i in "${!step_ids[@]}"; do
        printf '%-4s %-22s %-6s %-7s %s\n' \
            "${step_ids[$i]}" "${step_names[$i]}" "${step_results[$i]}" \
            "${step_times[$i]}" "${step_notes[$i]}"
        case "${step_results[$i]}" in
            PASS) pass=$((pass + 1)) ;;
            SKIP) skip=$((skip + 1)) ;;
            *)    failed=$((failed + 1)) ;;
        esac
    done
    echo "========================================="
    printf '[BASE] total=%s pass=%s fail=%s skip=%s\n' \
        "${#step_ids[@]}" "$pass" "$failed" "$skip"
    SUMMARY_FAILED=$failed
    return 0
}

# Containers (any state) whose image is the given tag. Empty output => unused.
tag_users() {
    local tag="$1" tid cid info img name st
    tid="$(podman image inspect --format '{{.Id}}' "$tag" 2>/dev/null || true)"
    [ -n "$tid" ] || return 0
    for cid in $(podman ps -a --format '{{.ID}}'); do
        info="$(podman container inspect --format '{{.Image}}|{{.ImageName}}|{{.State.Status}}' "$cid" 2>/dev/null || true)"
        [ -n "$info" ] || continue
        img="${info%%|*}"
        info="${info#*|}"
        name="${info%%|*}"
        st="${info#*|}"
        if [ "$img" = "$tid" ] || [ "${img:0:12}" = "${tid:0:12}" ] || [ "$name" = "$tag" ]; then
            printf '%s %s [%s]\n' "$cid" "$name" "$st"
        fi
    done
    return 0
}

# In-container read-only probe. Emits key=value lines plus a delimited block for
# the "no tvm/xmnn entity" assertion (same find expression as verify.sh / the
# layer audit evidence).
probe() {
    local tag="$1"
    podman run --rm -i --pull=never "$tag" bash -s 2>&1 <<'PROBE'
set -u
. /etc/os-release
printf 'os_name=%s\n' "${NAME:-}"
printf 'os_id=%s\n' "${ID:-}"
printf 'os_version_id=%s\n' "${VERSION_ID:-}"
printf 'os_codename=%s\n' "${VERSION_CODENAME:-}"
printf 'os_version=%s\n' "${VERSION:-}"
printf 'ldd_path=%s\n' "$(command -v ldd || true)"
printf 'ldd_version=%s\n' "$(ldd --version 2>&1 | head -n1 || true)"
printf 'gcc_path=%s\n' "$(command -v gcc || echo MISSING)"
printf 'gcc_version=%s\n' "$(gcc --version 2>/dev/null | head -n1 || true)"
printf 'pkg_count=%s\n' "$(dpkg-query -W -f='${Package}\n' \
    cpp cpp-15 cpp-15-x86-64-linux-gnu cpp-x86-64-linux-gnu \
    gcc gcc-15 gcc-15-x86-64-linux-gnu gcc-x86-64-linux-gnu \
    libasan8 libatomic1 libc-dev-bin libc6-dev libcc1-0 libgcc-15-dev \
    libgomp1 libhwasan0 libisl23 libitm1 liblsan0 libmpc3 libquadmath0 \
    libtsan2 libubsan1 linux-libc-dev rpcsvc-proto 2>/dev/null | wc -l)"
printf -- '--entities--\n'
find / -xdev \( -name "libtvm.so" -o -name "xmnn" -o -name "tvm" -o -name "*xmnn*dist-info" -o -name "tvm_src.pth" -o -name "_editable_skbc_xmnn.pth" \) 2>/dev/null
printf -- '--end--\n'
printf 'rootfs_bytes=%s\n' "$(du -sb --one-file-system / | awk '{print $1}')"
PROBE
}

val() { printf '%s\n' "$1" | grep -m1 "^$2=" | cut -d= -f2- || true; }

assert_common() {  # <out>
    local out="$1" v ents
    v="$(val "$out" os_id)"
    if [ "$v" = "openkylin" ]; then
        ok "os-release ID" "$v"
    else
        bad "os-release ID" "got '$v' (expected openkylin)"
    fi
    v="$(val "$out" os_version_id)"
    if [ "$v" = "3.0" ]; then
        ok "os-release VERSION_ID" "$v"
    else
        bad "os-release VERSION_ID" "got '$v' (expected 3.0)"
    fi
    v="$(val "$out" os_codename)"
    if [ "$v" = "huanghe" ]; then
        ok "os-release codename" "$v"
    else
        bad "os-release codename" "got '$v' (expected huanghe)"
    fi
    v="$(val "$out" ldd_path)"
    if [ -n "$v" ]; then
        ok "ldd available" "$v | $(val "$out" ldd_version)"
    else
        bad "ldd available" "ldd not found in PATH"
    fi
    ents="$(printf '%s\n' "$out" | awk '/^--entities--$/{f=1;next} /^--end--$/{f=0} f')"
    if [ -z "$ents" ]; then
        ok "no tvm/xmnn entities" "find / -xdev: 0 hit"
    else
        bad "no tvm/xmnn entities" "$(printf '%s' "$ents" | tr '\n' ' ')"
    fi
}

assert_gcc_absent() {  # S1 only: the layer is what adds gcc
    local out="$1" v
    v="$(val "$out" gcc_path)"
    if [ "$v" = "MISSING" ]; then
        ok "gcc absent (expected)" "command -v gcc: not found"
    else
        bad "gcc absent (expected)" "found '$v' before the gcc layer"
    fi
}

assert_gcc_present() {
    local out="$1" v gv pc
    v="$(val "$out" gcc_path)"
    if [ -n "$v" ] && [ "$v" != "MISSING" ]; then
        ok "gcc present" "$v"
    else
        bad "gcc present" "command -v gcc: not found"
    fi
    gv="$(val "$out" gcc_version)"
    case "$gv" in
        *"$GCC_WANT"*) ok "gcc version" "$gv" ;;
        *)             bad "gcc version" "got '$gv' (expected *$GCC_WANT*)" ;;
    esac
    pc="$(val "$out" pkg_count)"
    if [ "$pc" = "$GCC_PKG_COUNT" ]; then
        ok "apt package count" "$pc/$GCC_PKG_COUNT installed"
    else
        bad "apt package count" "got '$pc' (expected $GCC_PKG_COUNT)"
    fi
}

metrics_block() {  # <step-label> <tag> <elapsed> <df_before> <df_after> <rootfs_bytes>
    local label="$1" tag="$2" elapsed="$3" d0="$4" d1="$5" rootfs="$6"
    local id size line
    id="$(podman image inspect --format '{{.Id}}' "$tag" | cut -c1-12)"
    size="$(podman image inspect --format '{{.Size}}' "$tag")"
    line="$(podman images --format '{{.ID}} {{.Repository}}:{{.Tag}} {{.Size}}' | grep -F "$tag " || true)"
    printf '[BASE] metrics %s\n' "$label"
    printf '[BASE]   df      : %s -> %s  delta=%s B   <- authoritative\n' "$d0" "$d1" "$(( $4 - $5 ))"
    printf '[BASE]   images  : %s (id=%s Size=%s B)\n' "${line:-$tag}" "$id" "$size"
    printf '[BASE]   rootfs  : %s B  (du -sb --one-file-system /)\n' "${rootfs:-unknown}"
    printf '[BASE]   elapsed : %s s\n' "$elapsed"
}

write_containerfile() {  # <dst>
    local dst="$1"
    cat > "$dst" <<'CF'
# Generated by scripts/build-minimal-base.sh — do not edit by hand.
FROM __BASE__

RUN printf "%s\n" \
      "deb __MIRROR__/ huanghe main cross pty" \
      "deb __MIRROR__/ huanghe-security main cross pty" \
      "deb __MIRROR__/ huanghe-updates main cross pty" \
      "deb __MIRROR__/ huanghe-proposed main cross pty" \
      > /etc/apt/sources.list \
 && rm -f /etc/apt/sources.list.d/openkylin-anything.list \
 && apt-get update -qq

RUN set -eux; \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        gcc libc6-dev; \
    echo "[gcc-layer] dpkg-query (25 packages):"; \
    dpkg-query -W -f='${Package} ${Version}\n' \
        cpp cpp-15 cpp-15-x86-64-linux-gnu cpp-x86-64-linux-gnu \
        gcc gcc-15 gcc-15-x86-64-linux-gnu gcc-x86-64-linux-gnu \
        libasan8 libatomic1 libc-dev-bin libc6-dev libcc1-0 libgcc-15-dev \
        libgomp1 libhwasan0 libisl23 libitm1 liblsan0 libmpc3 libquadmath0 \
        libtsan2 libubsan1 linux-libc-dev rpcsvc-proto; \
    rm -rf /var/cache/apt/archives/*.deb; \
    gcc --version | head -n1; \
    echo "[gcc-layer] apt lists retained: $(du -sb /var/lib/apt/lists | awk '{print $1}') bytes"
CF
    sed -i -e "s|__BASE__|${MINIMAL_TAG}|" -e "s|__MIRROR__|${APT_MIRROR}|g" "$dst"
}

# ---------------------------------------------------------------------------
# S1: import the official minimal rootfs
# ---------------------------------------------------------------------------
step_s1_import() {
    local skipped=0 d0 d1 t0 elapsed out users
    ASSERT_FAIL=0
    if podman image exists "$MINIMAL_TAG" >/dev/null 2>&1; then
        if [ "$FORCE" -ne 1 ]; then
            echo "  $MINIMAL_TAG 已存在 -> SKIP（--force 才重建）"
            skipped=1
        else
            users="$(tag_users "$MINIMAL_TAG")"
            if [ -n "$users" ]; then
                echo "  FAIL: $MINIMAL_TAG 正被容器使用，拒绝 --force 重建：" >&2
                printf '    %s\n' "$users" >&2
                return 1
            fi
        fi
    fi

    d0="$(df_avail)"; t0=$SECONDS
    if [ "$skipped" -eq 0 ]; then
        podman import "$SRC_WSL" "$MINIMAL_TAG"
    fi
    elapsed=$((SECONDS - t0)); d1="$(df_avail)"

    out="$(probe "$MINIMAL_TAG" || true)"
    assert_common "$out"
    assert_gcc_absent "$out"
    metrics_block "S1 minimal-import" "$MINIMAL_TAG" "$elapsed" "$d0" "$d1" "$(val "$out" rootfs_bytes)"
    [ "$ASSERT_FAIL" -eq 0 ] || return 1

    if [ "$skipped" -eq 1 ]; then
        STEP_NOTE="已存在，跳过导入（断言复跑 PASS）"
        return 3
    fi
    STEP_NOTE="import OK $(podman image inspect --format '{{.Id}}' "$MINIMAL_TAG" | cut -c1-12)"
    return 0
}

# ---------------------------------------------------------------------------
# S2: add gcc 15.2.0 on top of S1
# ---------------------------------------------------------------------------
step_s2_gcc() {
    local skipped=0 d0 d1 t0 elapsed out users
    ASSERT_FAIL=0
    if podman image exists "$GCC_TAG" >/dev/null 2>&1; then
        if [ "$FORCE" -ne 1 ]; then
            echo "  $GCC_TAG 已存在 -> SKIP（--force 才重建）"
            skipped=1
        else
            users="$(tag_users "$GCC_TAG")"
            if [ -n "$users" ]; then
                echo "  FAIL: $GCC_TAG 正被容器使用，拒绝 --force 重建：" >&2
                printf '    %s\n' "$users" >&2
                return 1
            fi
        fi
    fi

    if ! podman image exists "$MINIMAL_TAG" >/dev/null 2>&1; then
        echo "  FAIL: 基线镜像 $MINIMAL_TAG 缺失，无法构建 $GCC_TAG" >&2
        return 1
    fi

    d0="$(df_avail)"; t0=$SECONDS
    if [ "$skipped" -eq 0 ]; then
        mkdir -p "$SCRATCH/emptctx"
        write_containerfile "$SCRATCH/Containerfile"
        echo "  podman build --network host --format docker -t $GCC_TAG"
        podman build --network host --format docker \
            -t "$GCC_TAG" -f "$SCRATCH/Containerfile" "$SCRATCH/emptctx"
    fi
    elapsed=$((SECONDS - t0)); d1="$(df_avail)"

    out="$(probe "$GCC_TAG" || true)"
    assert_common "$out"
    assert_gcc_present "$out"
    metrics_block "S2 gcc-layer" "$GCC_TAG" "$elapsed" "$d0" "$d1" "$(val "$out" rootfs_bytes)"
    [ "$ASSERT_FAIL" -eq 0 ] || return 1

    if [ "$skipped" -eq 1 ]; then
        STEP_NOTE="已存在，跳过构建（断言复跑 PASS）"
        return 3
    fi
    STEP_NOTE="build OK $(podman image inspect --format '{{.Id}}' "$GCC_TAG" | cut -c1-12)"
    return 0
}

# ---------------------------------------------------------------------------
# preflight
# ---------------------------------------------------------------------------
preflight() {
    command -v podman >/dev/null 2>&1 || {
        echo "[BASE] FAIL: podman not found（须在服务器 ai@10.16.11.3 上运行）" >&2
        exit 2
    }
    podman info >/dev/null 2>&1 || {
        echo "[BASE] FAIL: podman backend unreachable（rootless socket 是否已起？）" >&2
        exit 2
    }

    [ -f "$SRC_WSL" ] || { echo "[BASE] FAIL: source not found: $SRC_WSL" >&2; exit 2; }
    [ -r "$SRC_WSL" ] || { echo "[BASE] FAIL: source not readable: $SRC_WSL" >&2; exit 2; }

    local actual bytes
    actual="$(sha256sum "$SRC_WSL" | awk '{print $1}')"
    bytes="$(stat -c '%s' "$SRC_WSL")"
    if [ "$actual" = "$EXPECT_SHA256" ]; then
        echo "[BASE] PASS source sha256: $actual ($bytes B)"
    else
        echo "[BASE] FAIL source sha256: got $actual, expected $EXPECT_SHA256" >&2
        exit 2
    fi

    local avail
    avail="$(df_avail)"
    if [ "$avail" -ge "$MIN_AVAIL_BYTES" ]; then
        echo "[BASE] PASS disk head-room: $avail B >= $MIN_AVAIL_BYTES B (df -B1 $AI_ROOT)"
    else
        echo "[BASE] FAIL disk head-room: $avail B < $MIN_AVAIL_BYTES B (df -B1 $AI_ROOT)" >&2
        exit 2
    fi

    mkdir -p "$IMAGE_TMP" || {
        echo "[BASE] FAIL: cannot create image_copy_tmp_dir $IMAGE_TMP" >&2
        exit 2
    }
    mkdir -p "$AI_ROOT/.temp/npu-toolchain" || {
        echo "[BASE] FAIL: cannot create scratch parent $AI_ROOT/.temp/npu-toolchain" >&2
        exit 2
    }

    echo "[BASE] image tmp: $IMAGE_TMP"
    echo "[BASE] minimal  : $MINIMAL_TAG"
    echo "[BASE] gcc      : $GCC_TAG"
    echo "[BASE] force    : $FORCE"
}

# ---------------------------------------------------------------------------
# main
# ---------------------------------------------------------------------------
main() {
    while [ "$#" -gt 0 ]; do
        case "$1" in
            --force) FORCE=1 ;;
            -h | --help) usage; exit 0 ;;
            -*) echo "[BASE] unknown option: $1" >&2; usage >&2; exit 2 ;;
            *) SRC_WSL="$1" ;;
        esac
        shift
    done

    trap cleanup EXIT
    preflight

    SCRATCH="$(mktemp -d "$AI_ROOT/.temp/npu-toolchain/build-minimal-base.XXXXXX")"
    echo "[BASE] scratch  : $SCRATCH"

    run_step S1 "minimal-import" step_s1_import
    if [ "$(last_result)" = "FAIL" ]; then
        print_summary
        echo "[BASE] ABORTED: fix the S1 failures above" >&2
        exit 1
    fi

    run_step S2 "gcc-layer" step_s2_gcc
    if [ "$(last_result)" = "FAIL" ]; then
        print_summary
        echo "[BASE] ABORTED: fix the S2 failures above" >&2
        exit 1
    fi

    print_summary
    if [ "$SUMMARY_FAILED" -ne 0 ]; then
        echo "[BASE] FAIL: $SUMMARY_FAILED step(s) failed" >&2
        exit 1
    fi
    echo "[BASE] OK: $MINIMAL_TAG + $GCC_TAG"
    exit 0
}

main "$@"
