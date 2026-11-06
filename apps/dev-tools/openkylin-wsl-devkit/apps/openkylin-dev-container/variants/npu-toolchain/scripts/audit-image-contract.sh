#!/usr/bin/env bash
# audit-image-contract.sh — static content contract audit for the npu-toolchain image.
#
# Complements verify.sh. verify.sh exercises the *running* container (mounts up,
# volume populated, python imports working); this script audits the *image*
# itself, with no mounts at all, and asserts two disjoint sets:
#   A. what must be present in the image layers;
#   B. what must NOT be present (no tvm/xmnn artefact may be baked in).
#   C. optional --with-volume: the npu-build volume resolves libLLVM from
#      /var/opt/build/llvm22/lib, not from the system package.
#
# The script is read-only: it never builds, imports, tags, removes or prunes.
# Every container it starts is `--rm --network none`.
#
# Usage:
#   bash scripts/audit-image-contract.sh [--image <ref>] [--with-volume] [--json]
#
#   --image <ref>   image to audit (default: localhost/openkylin-npu-toolchain:3.0-minimal,
#                   the tag produced by `podman build --build-arg
#                   BASE_IMAGE=localhost/openkylin:3.0-minimal-gcc` on this recipe)
#   --with-volume   additionally audit the npu-build volume + workspace bind mount
#   --json          append a machine-readable JSON document after the table
#
# Exit codes: 0 all PASS; 1 at least one FAIL; 2 UNKNOWN only (podman missing,
# image absent, --with-volume prerequisites absent). FAIL and UNKNOWN are never
# mixed: FAIL wins if both were recorded.
set -Eeuo pipefail

IMAGE="${IMAGE:-localhost/openkylin-npu-toolchain:3.0-minimal}"
VOL="${VOL:-npu-build}"
WS="${WS:-/media/pc/data/ai}"
WITH_VOLUME=0
JSON=0

usage() {
    cat <<'EOF'
用法: bash scripts/audit-image-contract.sh [选项]

选项:
  --image <ref>   要审计的镜像（默认 localhost/openkylin-npu-toolchain:3.0-minimal，
                  即本配方以 BASE_IMAGE=localhost/openkylin:3.0-minimal-gcc 构建出的 tag）
  --with-volume   额外审计 npu-build 卷与 /workspace/ai 绑定挂载（C 组）
  --json          在表格之后追加一段机器可读 JSON
  -h, --help      显示本帮助

分组:
  A 必须在（镜像层，无挂载）  os-release / gcc / conda 环境 / pth / 软链 / 镜像配置
  B 必须不在（镜像层，无挂载）无 tvm/xmnn 实体、/opt/build 为空、不可 import
  C 可选 --with-volume        libtvm.so 的 libLLVM 必须解析到 /var/opt/build/llvm22/lib

退出码: 0 全 PASS；1 有 FAIL；2 仅 UNKNOWN（podman/镜像/卷缺失）。
EOF
}

while [ "$#" -gt 0 ]; do
    case "$1" in
        --image)
            IMAGE="${2:-}"
            [ -n "$IMAGE" ] || { echo "[audit] --image 需要参数" >&2; exit 2; }
            shift 2
            ;;
        --with-volume) WITH_VOLUME=1; shift ;;
        --json) JSON=1; shift ;;
        -h | --help) usage; exit 0 ;;
        *)
            echo "[audit] 未知参数: $1" >&2
            usage >&2
            exit 2
            ;;
    esac
done

# ---------------------------------------------------------------------------
# result bookkeeping
# ---------------------------------------------------------------------------
names=()
results=()
notes=()
n_pass=0
n_fail=0
n_unknown=0

record() {  # record <名称> <PASS|FAIL|UNKNOWN> <实测值>
    names+=("$1")
    results+=("$2")
    notes+=("$3")
    case "$2" in
        PASS) n_pass=$((n_pass + 1)) ;;
        FAIL) n_fail=$((n_fail + 1)) ;;
        UNKNOWN) n_unknown=$((n_unknown + 1)) ;;
    esac
    printf '  [%-7s] %-26s %s\n' "$2" "$1" "$3"
}

# check <名称> <函数>：函数返回 0=PASS、4=UNKNOWN、其它=FAIL。
check() {
    local name="$1" out rc
    shift
    set +e
    out="$("$@" 2>&1)"
    rc=$?
    set -e
    out="$(printf '%s' "$out" | tr '\n' ' ' | sed 's/  */ /g' | cut -c1-220)"
    case "$rc" in
        0) record "$name" PASS "${out:-ok}" ;;
        4) record "$name" UNKNOWN "${out:-unknown}" ;;
        *) record "$name" FAIL "${out:-failed}" ;;
    esac
}

json_escape() {
    # 控制字符必须替换掉：ldd 的输出行以 Tab 开头，原样写进 JSON 会产出非法文档。
    printf '%s' "$1" | tr '\n\r\t' '   ' | sed -e 's/\\/\\\\/g' -e 's/"/\\"/g'
}

# ---------------------------------------------------------------------------
# containers: A/B always run with no mounts; C is the only one with mounts
# ---------------------------------------------------------------------------
img() { podman run --rm --network none "$IMAGE" bash -lc "$1" 2>&1; }
imgvol() {
    podman run --rm --network none \
        -v "$VOL:/opt/build" -v "$WS:/workspace/ai" \
        "$IMAGE" bash -lc "$1" 2>&1
}

# ==========================================================================
# A. must be present (image layers, no mounts)
# ==========================================================================
a1_os_release() {
    local out
    out="$(img '. /etc/os-release; printf "%s|%s|%s\n" "$ID" "$VERSION_ID" "$VERSION_CODENAME"')" || return 1
    [ "$out" = "openkylin|3.0|huanghe" ] || {
        echo "实测 $out（期望 openkylin|3.0|huanghe）"
        return 1
    }
    echo "$out"
}

a2_compiler() {
    local g l
    g="$(img 'gcc --version 2>&1 | head -n1')" || { echo "gcc 不可用"; return 1; }
    case "$g" in
        *15.2.0*) ;;
        *) echo "gcc 版本不符: $g"; return 1 ;;
    esac
    l="$(img 'ldd --version 2>&1 | head -n1')" || { echo "ldd 不可用"; return 1; }
    [ -n "$l" ] || { echo "ldd 不可用"; return 1; }
    echo "$g / $l"
}

a3_conda_env() {
    local py pipv tools
    img 'test -d /opt/conda/envs/main' >/dev/null || {
        echo "缺少 /opt/conda/envs/main"
        return 1
    }
    py="$(img '/opt/conda/envs/main/bin/python --version 2>&1')" || { echo "python 不可用"; return 1; }
    case "$py" in
        "Python 3.14."*) ;;
        *) echo "python 版本不符: $py"; return 1 ;;
    esac
    pipv="$(img '/opt/conda/envs/main/bin/pip --version 2>&1 | cut -d" " -f2')" || { echo "pip 不可用"; return 1; }
    [ "$pipv" = "26.2.2" ] || { echo "pip 版本不符: $pipv（期望 26.2.2）"; return 1; }
    tools="$(img 'for t in cmake ninja make; do command -v "$t" >/dev/null 2>&1 || echo "missing:$t"; done')" || true
    [ -z "$tools" ] || { echo "$tools"; return 1; }
    echo "$py / pip $pipv / cmake+ninja+make ok"
}

a4_pth_files() {
    local out
    out="$(img 'sp=/opt/conda/envs/main/lib/python3.14/site-packages; for f in conda-site.pth npu-toolchain.pth; do test -f "$sp/$f" && echo "ok:$f" || echo "missing:$f"; done')" || return 1
    case "$out" in
        *missing:*) echo "$out"; return 1 ;;
    esac
    echo "$out"
}

a5_pth_content() {
    local ver expected exp_bytes exp_sha out act_bytes act_sha
    ver="$(img '/opt/conda/envs/main/bin/python -c "import sys; print(\"%d.%d\" % sys.version_info[:2])"')" || {
        echo "无法取 python 版本"
        return 1
    }
    expected="$(printf '%s\n' \
        "/opt/build/npuusertools/userbase/lib/python${ver}/site-packages" \
        "/workspace/ai/notebook/libs/npuusertools" \
        "/workspace/ai/notebook/libs/npu_tvm/python")"
    exp_bytes="$(printf '%s\n' "$expected" | wc -c | tr -d ' ')"
    exp_sha="$(printf '%s\n' \
        "/opt/build/npuusertools/userbase/lib/python${ver}/site-packages" \
        "/workspace/ai/notebook/libs/npuusertools" \
        "/workspace/ai/notebook/libs/npu_tvm/python" | sha256sum | cut -d' ' -f1)"
    out="$(img 'f=/opt/conda/envs/main/lib/python3.14/site-packages/npu-toolchain.pth; wc -c < "$f"; sha256sum "$f" | cut -d" " -f1')" || {
        echo "读取 npu-toolchain.pth 失败"
        return 1
    }
    act_bytes="$(printf '%s\n' "$out" | sed -n 1p | tr -d ' ')"
    act_sha="$(printf '%s\n' "$out" | sed -n 2p | tr -d ' ')"
    if [ "$act_bytes" = "$exp_bytes" ] && [ "$act_sha" = "$exp_sha" ]; then
        echo "三行逐字一致（python${ver}，${act_bytes} B，sha256 $(printf '%s' "$act_sha" | cut -c1-12)…）"
        return 0
    fi
    echo "不一致：实测 ${act_bytes} B / ${act_sha}，期望 ${exp_bytes} B / ${exp_sha}"
    return 1
}

a6_build_symlink() {
    local out
    out="$(img 'test -d /opt/build && echo "dir:ok" || echo "dir:missing"; test -L /var/opt/build && echo "link:$(readlink /var/opt/build)" || echo "link:missing"')" || return 1
    if ! printf '%s\n' "$out" | grep -qx 'dir:ok' || ! printf '%s\n' "$out" | grep -qx 'link:/opt/build'; then
        echo "实测 $(printf '%s' "$out" | tr '\n' ' ')（期望 dir:ok + link:/opt/build）"
        return 1
    fi
    echo "dir:ok link:/opt/build"
}

a7_image_config() {
    local wd cmd envs hits
    wd="$(podman image inspect --format '{{.Config.WorkingDir}}' "$IMAGE" 2>&1)" || { echo "image inspect 失败"; return 1; }
    cmd="$(podman image inspect --format '{{json .Config.Cmd}}' "$IMAGE" 2>&1 | tr -d ' ')"
    envs="$(podman image inspect --format '{{range .Config.Env}}{{println .}}{{end}}' "$IMAGE" 2>&1)" || { echo "Env 读取失败"; return 1; }

    [ "$wd" = "/workspace" ] || { echo "WorkingDir=$wd（期望 /workspace）"; return 1; }
    [ "$cmd" = '["sleep","infinity"]' ] || { echo "Cmd=$cmd（期望 [\"sleep\",\"infinity\"]）"; return 1; }

    hits=0
    printf '%s\n' "$envs" | grep -qx 'TVM_LIBRARY_PATH=/opt/build/npu_tvm' && hits=$((hits + 1))
    printf '%s\n' "$envs" | grep -qx 'TEST_DATA_ROOT_PATH=/opt/build/tvm_test_data' && hits=$((hits + 1))
    printf '%s\n' "$envs" | grep -qx 'TVM_TEST_DATA_DIR=/opt/build/tvm_test_data' && hits=$((hits + 1))
    [ "$hits" -eq 3 ] || { echo "Env 命中 ${hits}/3（TVM_LIBRARY_PATH / TEST_DATA_ROOT_PATH / TVM_TEST_DATA_DIR）"; return 1; }
    echo "WorkingDir=$wd Cmd=$cmd Env=3/3"
}

# ==========================================================================
# B. must NOT be present (image layers, no mounts)
# ==========================================================================
b1_no_artifacts() {
    local out hits
    out="$(img 'find / -xdev \( -name libtvm.so -o -name tvm -o -name xmnn -o -name \*xmnn\*dist-info -o -name tvm_src.pth -o -name _editable_skbc_xmnn.pth \) 2>/dev/null')" || {
        echo "find 执行失败"
        return 1
    }
    hits="$(printf '%s\n' "$out" | grep -c . || true)"
    [ "$hits" -eq 0 ] || {
        echo "${hits} 处命中: $(printf '%s' "$out" | tr '\n' ' ' | cut -c1-120)"
        return 1
    }
    echo "0 命中（libtvm.so/tvm/xmnn/*xmnn*dist-info/tvm_src.pth/_editable_skbc_xmnn.pth）"
}

b2_build_dir_empty() {
    local n
    n="$(img 'find /opt/build -mindepth 1 2>/dev/null | wc -l')" || { echo "/opt/build 不可读"; return 1; }
    [ "$n" -eq 0 ] || { echo "/opt/build 内有 $n 项"; return 1; }
    echo "空目录（0 项）"
}

b3_no_import_without_mounts() {
    local out
    out="$(img 'python -c "import tvm" >/dev/null 2>&1 && echo tvm-importable; python -c "import xmnn" >/dev/null 2>&1 && echo xmnn-importable; true')" || {
        echo "python 不可用"
        return 4
    }
    [ -z "$out" ] || { echo "无挂载仍可导入: $out"; return 1; }
    echo "无挂载时 import tvm / import xmnn 均 ModuleNotFoundError"
}

# ==========================================================================
# C. optional --with-volume (npu-build:/opt/build + workspace bind)
# ==========================================================================
c2_mounts() {
    local out
    if ! podman volume exists "$VOL" >/dev/null 2>&1; then
        echo "卷 $VOL 不存在（未挂载，先跑 all-in-one.sh S6）"
        return 4
    fi
    out="$(imgvol 'grep -q " /opt/build " /proc/mounts && echo "optbuild:mounted" || echo "optbuild:missing"; grep -q " /workspace/ai " /proc/mounts && echo "workspace:mounted" || echo "workspace:missing"; test -e /opt/build/npu_tvm/libtvm.so && echo "libtvm:present" || echo "libtvm:missing"')" || {
        echo "挂载探测失败"
        return 4
    }
    local b
    b="$(printf '%s\n' "$out" | grep -c 'present$' || true)"
    case "$out" in
        *optbuild:missing*) echo "npu-build 卷未挂载到 /opt/build"; return 1 ;;
        *workspace:missing*) echo "/workspace/ai 绑定挂载缺失"; return 1 ;;
    esac
    if [ "$b" -ne 0 ]; then
        echo "$out"
        return 0
    fi
    echo "npu-build 卷已挂载，但缺少 /opt/build/npu_tvm/libtvm.so（S6 未执行）"
    return 1
}

c1_libtvm_llvm() {
    local out lddline path size
    if ! podman volume exists "$VOL" >/dev/null 2>&1; then
        echo "卷 $VOL 不存在（未挂载，先跑 all-in-one.sh S6）"
        return 4
    fi
    out="$(imgvol 'ldd /opt/build/npu_tvm/libtvm.so 2>&1 | grep -i libLLVM; f=$(readlink -f /var/opt/build/llvm22/lib/libLLVM.so.22.1 2>/dev/null); [ -n "$f" ] && stat -c "size:%s" "$f" 2>/dev/null')" || {
        echo "ldd 执行失败（libtvm.so 或卷内容缺失）"
        return 1
    }
    lddline="$(printf '%s\n' "$out" | grep -i libLLVM | head -n1)"
    path="$(printf '%s' "$lddline" | awk '{print $3}')"
    size="$(printf '%s\n' "$out" | sed -n 's/^size:/size:/p' | head -n1)"
    case "$path" in
        /var/opt/build/llvm22/lib/*) ;;
        /usr/lib/* | /lib/*)
            echo "FAIL: libLLVM 落到了系统包（$lddline）"
            return 1
            ;;
        *)
            echo "未解析到 /var/opt/build/llvm22/lib/（${lddline:-无 libLLVM 行}）"
            return 1
            ;;
    esac
    if [ -z "$size" ]; then
        echo "卷内 llvm22/lib/libLLVM.so.22.1 缺失"
        return 1
    fi
    if [ "${size#size:}" -lt 195900000 ]; then
        echo "$path $size（期望约 195933536 B，疑似系统包尺寸）"
        return 1
    fi
    echo "$path $size"
}

# ==========================================================================
# main
# ==========================================================================
echo "===== IMAGE CONTENT CONTRACT: $IMAGE ====="
if ! command -v podman >/dev/null 2>&1; then
    record "podman 可用性" UNKNOWN "podman 不在 PATH"
elif ! podman image exists "$IMAGE" >/dev/null 2>&1; then
    record "镜像存在" UNKNOWN "$IMAGE 不存在"
else
    echo "--- A. 必须在（无挂载） ---"
    check "A1 /etc/os-release" a1_os_release
    check "A2 gcc 15.2.0 + ldd" a2_compiler
    check "A3 conda env / python / pip / 工具" a3_conda_env
    check "A4 conda-site.pth + npu-toolchain.pth" a4_pth_files
    check "A5 npu-toolchain.pth 逐字三行" a5_pth_content
    check "A6 /var/opt/build -> /opt/build" a6_build_symlink
    check "A7 WorkingDir / Cmd / Env" a7_image_config

    echo "--- B. 必须不在（无挂载） ---"
    check "B1 无 tvm/xmnn 实体" b1_no_artifacts
    check "B2 /opt/build 为空" b2_build_dir_empty
    check "B3 无挂载时不可 import" b3_no_import_without_mounts

    if [ "$WITH_VOLUME" -eq 1 ]; then
        echo "--- C. 卷挂载（--with-volume） ---"
        check "C2 npu-build / workspace 挂载" c2_mounts
        check "C1 libtvm.so -> llvm22 解析" c1_libtvm_llvm
    fi
fi

echo
echo "================ SUMMARY ================"
printf '%-7s %-26s %s\n' "RESULT" "CHECK" "NOTE"
for i in "${!names[@]}"; do
    printf '%-7s %-26s %s\n' "${results[$i]}" "${names[$i]}" "${notes[$i]}"
done
echo "-----------------------------------------"
printf 'total=%d pass=%d fail=%d unknown=%d\n' "${#names[@]}" "$n_pass" "$n_fail" "$n_unknown"

if [ "$n_fail" -gt 0 ]; then
    rc=1
elif [ "$n_unknown" -gt 0 ]; then
    rc=2
else
    rc=0
fi
echo "exit=$rc"

if [ "$JSON" -eq 1 ]; then
    sep=""
    printf '{"image":"%s","with_volume":%s,"total":%d,"pass":%d,"fail":%d,"unknown":%d,"exit":%d,"checks":[' \
        "$(json_escape "$IMAGE")" "$([ "$WITH_VOLUME" -eq 1 ] && echo true || echo false)" \
        "${#names[@]}" "$n_pass" "$n_fail" "$n_unknown" "$rc"
    for i in "${!names[@]}"; do
        printf '%s{"name":"%s","result":"%s","note":"%s"}' "$sep" \
            "$(json_escape "${names[$i]}")" "${results[$i]}" "$(json_escape "${notes[$i]}")"
        sep=","
    done
    echo "]}"
fi

exit "$rc"
