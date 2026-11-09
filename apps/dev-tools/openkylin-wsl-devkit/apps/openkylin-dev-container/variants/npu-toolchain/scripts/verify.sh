#!/usr/bin/env bash
# verify.sh — A1–A9 acceptance gate for the npu-toolchain variant.
#
# Two execution modes (both read-only, idempotent; nothing is rebuilt or deleted):
#
#   1) On the server host (primary; all fields available):
#        ssh ai@10.16.11.3
#        cd /media/pc/data/ai/notebook/dev/libs/AI/apps/dev-tools/openkylin-wsl-devkit/apps/openkylin-dev-container/variants/npu-toolchain
#        bash scripts/verify.sh
#      Prereqs: local podman (5.6.2) as user ai(1006); container npu-toolchain running.
#
#   2) From Windows through a remote client (Git Bash / MSYS bash):
#        PODMAN_REMOTE="podman --remote --connection remote-ai" bash scripts/verify.sh
#        # or a direct URL instead of a connection name:
#        PODMAN_REMOTE="podman --remote --url ssh://ai@10.16.11.3:22/run/user/1006/podman/podman.sock" bash scripts/verify.sh
#      Prereqs: podman.exe 5.8.1; ssh key auth works in BatchMode; the ssh_config
#      entry must be a *match* block (`Match host 10.16.11.3`), otherwise the
#      client loses the hostname and fails with `dial tcp :22`.
#
# Notes:
#   * `podman system df` is NOT used: it fails with an infra-container lstat
#     error on this host. Capacity comes from `df` inside the container.
#   * No `((var++))` under `set -euo pipefail` (it returns 1 on the first
#     increment); counters use `var=$((var+1))`.
#   * A7 is pinned to N/A by policy: the container publishes no port. Jupyter
#     would require recreating the container with -p (ports cannot be added).
set -Eeuo pipefail

CTR="${CTR:-npu-toolchain}"
IMAGE="${IMAGE:-localhost/openkylin-npu-toolchain:3.0}"
CAP_MIN_BYTES="${CAP_MIN_BYTES:-53687091200}"   # A9 gate: 50 GiB
EXPECT_UID="${EXPECT_UID:-1006}"

# --- invocation mode -------------------------------------------------------
if [ -n "${PODMAN_REMOTE:-}" ]; then
    read -r -a PM <<<"$PODMAN_REMOTE"
    MODE="remote-client"
else
    PM=(podman)
    MODE="on-server"
fi

names=() results=() notes=()
pass=0 fail=0 na=0

pm() { "${PM[@]}" "$@"; }
pexec() { "${PM[@]}" exec "$CTR" bash -lc "$1"; }

# Contract: the tvm / xmnn artefacts never live in the image. They are reachable
# only through the two required mounts (-v npu-build:/opt/build and
# -v /media/pc/data/ai:/workspace/ai). A missing mount therefore has to surface
# as a readable "卷/绑定挂载缺失" message instead of a Python traceback, and the
# checks below gate on those mounts before touching the interpreter.
has_mount() {  # has_mount <container-destination>
    "${PM[@]}" container inspect --format '{{range .Mounts}}{{.Destination}}{{"\n"}}{{end}}' "$CTR" 2>/dev/null \
        | grep -qx "$1"
}

record() {  # record <name> <PASS|FAIL|N/A> <note>
    names+=("$1"); results+=("$2"); notes+=("$3")
    printf '  [%-4s] %-26s %s\n' "$2" "$1" "$3"
}

check() {  # check <name> <function>
    local name="$1" out rc
    shift
    set +e
    out="$("$@" 2>&1)"
    rc=$?
    set -e
    out="$(printf '%s' "$out" | tr '\n' ' ' | cut -c1-190)"
    if [ "$rc" -eq 0 ]; then
        record "$name" PASS "${out:-ok}"
    else
        record "$name" FAIL "${out:-failed}"
    fi
    return 0
}

check_na() {  # check_na <name> <note>
    record "$1" N/A "$2"
}

# ==========================================================================
# Aux: runtime contract (G3) — failures here invalidate the A-gate too
# ==========================================================================
aux_container() {
    if ! pm container exists "$CTR" >/dev/null 2>&1; then
        echo "container $CTR not found"; return 1
    fi
    local st
    st="$(pm container inspect --format '{{.State.Status}}' "$CTR")"
    [ "$st" = "running" ] || { echo "state=$st (expected running)"; return 1; }
    echo "state=running"
}

aux_image() {
    pm image exists "$IMAGE" >/dev/null 2>&1 || { echo "image $IMAGE missing"; return 1; }
    echo "$IMAGE"
}

aux_privileged() {
    local v
    v="$(pm container inspect --format '{{.HostConfig.Privileged}}' "$CTR")"
    [ "$v" = "false" ] || { echo "Privileged=$v (expected false)"; return 1; }
    echo "Privileged=false"
}

aux_userns() {
    local mode uid
    mode="$(pm container inspect --format '{{.HostConfig.UsernsMode}}' "$CTR" 2>/dev/null || true)"
    uid="$(pexec 'id -u' 2>/dev/null || true)"
    if [ "$mode" = "keep-id" ] || [ "$uid" = "$EXPECT_UID" ]; then
        echo "UsernsMode=$mode container_uid=$uid"
        return 0
    fi
    echo "UsernsMode=$mode container_uid=$uid (keep-id not proven)"; return 1
}

aux_cgroup() {
    local m
    m="$(pm container inspect --format '{{.HostConfig.CgroupMode}}' "$CTR" 2>/dev/null || true)"
    [ -n "$m" ] || m="$(pm container inspect --format '{{.HostConfig.CgroupnsMode}}' "$CTR" 2>/dev/null || true)"
    [ "$m" = "host" ] || { echo "CgroupMode=$m (expected host)"; return 1; }
    echo "CgroupMode=host"
}

# ==========================================================================
# A1–A9
# ==========================================================================
a1_runtime() {  # remote podman reachable: version / rootless / overlay
    local v r d
    v="$(pm info --format '{{.Version.Version}}')" || { echo "podman info failed"; return 1; }
    r="$(pm info --format '{{.Host.Security.Rootless}}')"
    d="$(pm info --format '{{.Store.GraphDriverName}}')"
    [ "$r" = "true" ] || { echo "rootless=$r (expected true)"; return 1; }
    [ "$d" = "overlay" ] || { echo "driver=$d (expected overlay)"; return 1; }
    echo "server=$v rootless=$r driver=$d"
}

a2_connection() {  # client -> server path works (mode recorded)
    local cli srv
    cli="$(pm version --format '{{.Client.Version}}')" || { echo "client blocked"; return 1; }
    srv="$(pm version --format '{{.Server.Version}}')" || { echo "server unreachable"; return 1; }
    echo "mode=$MODE client=$cli server=$srv"
}

a3_llvm() {  # LLVM 22.x inside the container (supplied by the npu-build volume)
    local v ok
    ok="$(pexec 'test -x /opt/build/llvm22/bin/llvm-config && echo yes' 2>/dev/null || true)"
    if [ -z "$ok" ]; then
        if has_mount /opt/build; then
            echo "npu-build 卷已挂载，但缺少 /opt/build/llvm22/bin/llvm-config（S5 LLVM 供给未执行）"
        else
            echo "npu-build 卷未挂载到 /opt/build（A3 依赖 /opt/build/llvm22）"
        fi
        return 1
    fi
    if ! v="$(pexec '/opt/build/llvm22/bin/llvm-config --version')"; then
        echo "/opt/build/llvm22/bin/llvm-config not runnable"; return 1
    fi
    case "$v" in
        22.*) echo "llvm-config=$v"; return 0 ;;
        *)    echo "llvm-config=$v (expected 22.x)"; return 1 ;;
    esac
}

a4_tvm() {  # import tvm + llvm/ccompiler targets + linked libLLVM
    local out ldd tgt ok
    ok="$(pexec 'test -f /opt/build/npu_tvm/libtvm.so && echo yes' 2>/dev/null || true)"
    if [ -z "$ok" ]; then
        if has_mount /opt/build; then
            echo "npu-build 卷已挂载，但缺少 /opt/build/npu_tvm/libtvm.so（S6 编译未执行）"
        else
            echo "npu-build 卷未挂载到 /opt/build（A4 依赖 /opt/build/npu_tvm/libtvm.so）"
        fi
        return 1
    fi
    ok="$(pexec 'test -d /workspace/ai/notebook/libs/npu_tvm/python/tvm && echo yes' 2>/dev/null || true)"
    if [ -z "$ok" ]; then
        if has_mount /workspace/ai; then
            echo "/workspace/ai 已挂载，但 /workspace/ai/notebook/libs/npu_tvm/python/tvm 不存在"
        else
            echo "/workspace/ai 绑定挂载缺失（A4 依赖 tvm python 源码，见 npu-toolchain.pth）"
        fi
        return 1
    fi
    if ! out="$(pexec "python -c 'import tvm;print(\"tvm\",tvm.__version__);print(tvm.target.Target(\"llvm\"));print(tvm.target.Target(\"ccompiler\"))'")"; then
        echo "import tvm failed"; return 1
    fi
    tgt="$(printf '%s\n' "$out" | grep -Ec '^(llvm |ccompiler)' || true)"
    ldd="$(pexec 'ldd /opt/build/npu_tvm/libtvm.so | grep -E "libLLVM|not found" || echo "no libLLVM match"' 2>/dev/null || true)"
    printf '%s\n' "$out" | grep -q 'tvm 0.19' || { echo "unexpected tvm version: $(printf '%s' "$out" | head -n1)"; return 1; }
    [ "$tgt" -ge 2 ] || { echo "targets resolved=$tgt (expected 2)"; return 1; }
    printf '%s' "$ldd" | grep -q 'libLLVM.so.22' || { echo "libLLVM linkage: $ldd"; return 1; }
    echo "$(printf '%s' "$out" | head -n1) | targets=$tgt | $(printf '%s' "$ldd" | head -n1)"
}

a5_xmnn() {  # import xmnn and its distribution version
    local out ok
    if ! has_mount /opt/build; then
        echo "npu-build 卷未挂载到 /opt/build（A5 依赖 S7 安装的 xmnn）"; return 1
    fi
    ok="$(pexec '{ test -d /opt/build/npuusertools/userbase/lib/python3.14/site-packages/xmnn || test -d /workspace/ai/notebook/libs/npuusertools/xmnn; } && echo yes' 2>/dev/null || true)"
    if [ -z "$ok" ]; then
        echo "npu-build 卷已挂载，但 xmnn 源/安装目录不存在（S7 未执行）"
        return 1
    fi
    if ! out="$(pexec "python -c 'import xmnn,importlib.metadata as m;print(\"xmnn\",m.version(\"xmnn\"),xmnn.__file__)'")"; then
        echo "import xmnn failed"; return 1
    fi
    printf '%s' "$out" | grep -q '^xmnn ' || { echo "unexpected output: $out"; return 1; }
    echo "$out"
}

a6_uid() {  # container uid/gid aligned with host ai(1006)
    local u g
    u="$(pexec 'id -u')"; g="$(pexec 'id -g')"
    [ "$u" = "$EXPECT_UID" ] && [ "$g" = "$EXPECT_UID" ] \
        || { echo "container uid=$u gid=$g (expected $EXPECT_UID)"; return 1; }
    echo "uid=$u gid=$g"
}

a7_ports() {  # policy check: N/A by design (no published port)
    local out
    out="$(pm port "$CTR" 2>&1 || true)"
    if [ -z "$out" ]; then
        echo "podman port: <empty> (默认不发布端口)"
    else
        echo "podman port: $(printf '%s' "$out" | tr '\n' ';') (若为按需启用，需人工判 PASS)"
    fi
    return 0
}

a8_mount() {  # bind mount writable, mode/owner 700 1006, read-back, cleanup
    local p="/workspace/ai/.temp/npu-toolchain/.verify.$$"
    local out mode
    if ! has_mount /workspace/ai; then
        echo "/workspace/ai 绑定挂载缺失（A8 需要可写的工作区）"; return 1
    fi
    if ! out="$(pexec "mkdir -p /workspace/ai/.temp/npu-toolchain && printf 'probe-ok\\n' > $p && chmod 700 $p && stat -c '%a %u' $p && cat $p && rm -f $p")"; then
        echo "write/chmod/read-back failed"; return 1
    fi
    mode="$(printf '%s\n' "$out" | grep -m1 -E '^[0-7]{3,4} [0-9]+' || true)"
    printf '%s' "$out" | grep -q 'probe-ok' || { echo "read-back missing"; return 1; }
    [ "$mode" = "700 $EXPECT_UID" ] || { echo "mode/owner='$mode' (expected '700 $EXPECT_UID')"; return 1; }
    # 宿主侧可见性仅在本机模式可判（远程客户端看不到宿主路径）
    if [ "$MODE" = "on-server" ] && [ -d "${SRC:-/media/pc/data/ai}/.temp/npu-toolchain" ]; then
        echo "mode/owner=$mode host_dir=visible"
    else
        echo "mode/owner=$mode host_dir=not-checked($MODE)"
    fi
}

a9_capacity() {  # XFS free space >= 50 GiB, measured via df (system df is broken)
    local line avail
    if ! has_mount /workspace/ai; then
        echo "/workspace/ai 绑定挂载缺失（A9 需要在其上测量可用容量）"; return 1
    fi
    if ! line="$(pexec 'df -B1 /workspace/ai | tail -n1')"; then
        echo "df failed"; return 1
    fi
    avail="$(printf '%s\n' "$line" | awk '{print $4}')"
    [ -n "$avail" ] || { echo "cannot parse df: $line"; return 1; }
    if [ "$avail" -lt "$CAP_MIN_BYTES" ]; then
        echo "avail=$avail bytes < gate $CAP_MIN_BYTES"
        return 1
    fi
    echo "avail=$((avail / 1073741824)) GiB (gate $((CAP_MIN_BYTES / 1073741824)) GiB)"
}

# ==========================================================================
# run
# ==========================================================================
echo "[verify] npu-toolchain A1–A9 gate | mode=$MODE | client=$(command -v "${PM[0]}" >/dev/null 2>&1 && echo "${PM[*]}" || echo missing)"
echo
echo "aux: runtime contract"
check aux-container-running aux_container
check aux-image-present aux_image
check aux-no-privileged aux_privileged
check aux-userns-keep-id aux_userns
check aux-cgroupns-host aux_cgroup
echo
echo "A1–A9"
check A1-runtime-podman a1_runtime
check A2-connection a2_connection
check A3-llvm22 a3_llvm
check A4-npu_tvm a4_tvm
check A5-npuusertools a5_xmnn
check A6-uid-alignment a6_uid
check_na A7-port-publish "$(a7_ports)"
check A8-bind-mount a8_mount
check A9-capacity a9_capacity

echo
echo "================ SUMMARY ================"
printf '%-26s %-6s %s\n' "CHECK" "RESULT" "EVIDENCE"
i=0
while [ "$i" -lt "${#names[@]}" ]; do
    printf '%-26s %-6s %s\n' "${names[$i]}" "${results[$i]}" "${notes[$i]}"
    i=$((i + 1))
done
echo "========================================="

i=0
while [ "$i" -lt "${#results[@]}" ]; do
    case "${results[$i]}" in
        PASS) pass=$((pass + 1)) ;;
        N/A)  na=$((na + 1)) ;;
        *)    fail=$((fail + 1)) ;;
    esac
    i=$((i + 1))
done

echo "[verify] total=${#results[@]} pass=$pass fail=$fail na=$na"
# A-gate (A1–A9 only) verdict
a_fail=0
for n in "${!names[@]}"; do
    case "${names[$n]}" in
        A[1-9]-*) [ "${results[$n]}" = "FAIL" ] && a_fail=$((a_fail + 1)) ;;
    esac
done
if [ "$fail" -ne 0 ]; then
    echo "[verify] FAIL: $fail check(s) failed (A-gate failures: $a_fail)"
    exit 1
fi
echo "[verify] OK: A1–A6, A8, A9 PASS; A7 N/A by policy; aux contract PASS"
