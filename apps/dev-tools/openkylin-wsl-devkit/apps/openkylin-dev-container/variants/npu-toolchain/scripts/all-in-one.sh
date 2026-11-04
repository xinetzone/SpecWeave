#!/usr/bin/env bash
# all-in-one.sh — npu-toolchain 变体的一键可重放入口。
#
# 在宿主机 ai@10.16.11.3 上执行（/media/pc/data/ai 是宿主本地目录，无需远程跳板）。
# 串联九个步骤：基线镜像 → 变体镜像 → 容器 → 挂载门禁 → LLVM 21 供给 →
# npu_tvm → npuusertools →（可选）端到端冒烟 → 两库 git 洁净度。
#
# 用法:
#   bash scripts/all-in-one.sh [选项]
#
# 选项:
#   --full              额外执行 S8 端到端冒烟（onnx.yolov5s，约 21 分钟）
#   --skip-build-image  跳过 S2 变体镜像构建
#   --skip-tvm          跳过 S6 npu_tvm 构建与断言
#   -h, --help          显示本帮助
#
# 退出码:
#   0  所有步骤 PASS 或被 SKIP
#   1  至少一个步骤 FAIL
#   2  参数错误或运行环境不可用（podman 缺失 / 不可达）
#
# 幂等性：LLVM 21 已就位则跳过复制；容器已在运行则不重复启动；
# ninja 无改动时输出 "no work to do"。
#
# 日志: /workspace/ai/.temp/npu-toolchain/logs/all-in-one-<YYYYmmdd-HHMMSS>.log
set -uo pipefail

# ---------------------------------------------------------------------------
# 常量（脚本自身的绝对路径不硬编码，由 SCRIPT_DIR 推导）
# ---------------------------------------------------------------------------
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
AI_ROOT="/media/pc/data/ai"

BASE_IMAGE="${BASE_IMAGE:-localhost/openkylin:3.0}"
IMAGE="${IMAGE:-localhost/openkylin-npu-toolchain:3.0}"
CTR="${CTR:-npu-toolchain}"
IMAGE_TMP="${IMAGE_TMP:-$AI_ROOT/.temp/podman-image-tmp}"
WSL_PACKAGE="$AI_ROOT/.agents/wsl-images/openKylin-3.0-desktop-wsl-amd64.wsl"

# 宿主机侧路径
NPU_TVM_HOST="$AI_ROOT/notebook/libs/npu_tvm"
NPUUTILS_HOST="$AI_ROOT/notebook/libs/npuusertools"
LOG_DIR_HOST="$AI_ROOT/.temp/npu-toolchain/logs"

# 容器内路径（与宿主机路径经 bind 一一对应）
WS="/workspace/ai"
NPU_TVM="$WS/notebook/libs/npu_tvm"
NPUUTILS="$WS/notebook/libs/npuusertools"
LLVM_PREFIX="/opt/build/llvm21"
BUILD_ROOT="/opt/build"

# ---------------------------------------------------------------------------
# 选项
# ---------------------------------------------------------------------------
FULL=0
SKIP_BUILD_IMAGE=0
SKIP_TVM=0

usage() {
    cat <<'EOF'
用法: bash scripts/all-in-one.sh [选项]

选项:
  --full              额外执行 S8 端到端冒烟（onnx.yolov5s，约 21 分钟）
  --skip-build-image  跳过 S2 变体镜像构建（镜像已存在时省时）
  --skip-tvm          跳过 S6 npu_tvm 构建与断言
  -h, --help          显示本帮助

步骤:
  S1 基线镜像检查      podman image exists localhost/openkylin:3.0 + 中转目录
  S2 变体镜像构建      scripts/build-image.sh
  S3 容器启动          scripts/run.sh up（已在运行则视为 PASS）
  S4 挂载门禁          scripts/verify.sh
  S5 LLVM 21 供给      宿主 /usr/lib/llvm-21 → /opt/build/llvm21（幂等）
  S6 npu_tvm           cmake + ninja + import/Target 三项断言
  S7 npuusertools      build.sh + editable 安装 + import xmnn 路径断言
  S8 端到端冒烟        仅 --full：compile.py -n onnx.yolov5s
  S9 两库洁净度        git status --porcelain 行数断言（不修改任何仓库）

退出码: 0 全部 PASS/SKIP；1 有 FAIL；2 参数错误或环境不可用。
EOF
}

while [ "$#" -gt 0 ]; do
    case "$1" in
        --full) FULL=1 ;;
        --skip-build-image) SKIP_BUILD_IMAGE=1 ;;
        --skip-tvm) SKIP_TVM=1 ;;
        -h | --help)
            usage
            exit 0
            ;;
        *)
            echo "[all-in-one] unknown option: $1" >&2
            usage >&2
            exit 2
            ;;
    esac
    shift
done

# ---------------------------------------------------------------------------
# 步骤执行框架
# ---------------------------------------------------------------------------
step_ids=()
step_names=()
step_results=()
step_notes=()
step_times=()

STEP_NOTE=""

# run_step <id> <名称> <函数>
# 函数返回 0 → PASS；3 → SKIP；其它 → FAIL。不启用 set -e，逐步骤收集结果。
run_step() {
    local id="$1" name="$2" fn="$3"
    local started=$SECONDS rc idx status
    STEP_NOTE=""
    printf '\n===== STEP %s %s =====\n' "$id" "$name"
    "$fn"
    rc=$?
    idx=$((${#step_ids[@]}))
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
        [ "$rc" -eq 0 ] && STEP_NOTE="ok" || STEP_NOTE="rc=$rc"
    fi
    step_notes+=("$STEP_NOTE")
    printf '[STEP] %-3s %-20s ... %s (%ss)\n' "$id" "$name" "$status" "$((SECONDS - started))"
    return 0
}

print_summary() {
    local i failed=0
    echo
    echo "================ SUMMARY ================"
    printf '%-5s %-22s %-6s %-7s %s\n' "STEP" "NAME" "RESULT" "TIME" "NOTE"
    for i in "${!step_ids[@]}"; do
        printf '%-5s %-22s %-6s %-7s %s\n' \
            "${step_ids[$i]}" "${step_names[$i]}" "${step_results[$i]}" \
            "${step_times[$i]}" "${step_notes[$i]}"
        [ "${step_results[$i]}" = "FAIL" ] && failed=$((failed + 1))
    done
    echo "========================================="
    return "$failed"
}

# 容器必须存在且处于 running，否则后续步骤直接 FAIL（不静默降级）。
require_container() {
    if ! podman container exists "$CTR" >/dev/null 2>&1; then
        echo "  FAIL: 容器 $CTR 不存在（先执行 bash scripts/run.sh up）" >&2
        return 1
    fi
    local st
    st="$(podman container inspect --format '{{.State.Status}}' "$CTR" 2>/dev/null)"
    if [ "$st" != "running" ]; then
        echo "  FAIL: 容器 $CTR 状态=$st（期望 running）" >&2
        return 1
    fi
    return 0
}

# ---------------------------------------------------------------------------
# S1 基线镜像检查
# ---------------------------------------------------------------------------
step_s1_base_image() {
    if ! mkdir -p "$IMAGE_TMP" 2>/dev/null; then
        STEP_NOTE="无法创建 $IMAGE_TMP"
        echo "  FAIL: 无法创建 Podman 中转目录 $IMAGE_TMP" >&2
        return 1
    fi
    echo "  image_copy_tmp_dir: $IMAGE_TMP"

    if podman image exists "$BASE_IMAGE" >/dev/null 2>&1; then
        local id
        id="$(podman image inspect --format '{{.Id}}' "$BASE_IMAGE" 2>/dev/null | cut -c1-12)"
        echo "  基线镜像 $BASE_IMAGE 存在 (id ${id:-unknown})"
        STEP_NOTE="$BASE_IMAGE ${id:-present}"
        return 0
    fi

    echo "  FAIL: 基线镜像 $BASE_IMAGE 缺失" >&2
    echo "  FIX : 从离线包导入一次（本脚本不会隐式拉取）：" >&2
    echo "        gunzip -c $WSL_PACKAGE \\" >&2
    echo "          | podman import - $BASE_IMAGE" >&2
    STEP_NOTE="基线镜像缺失"
    return 1
}

# ---------------------------------------------------------------------------
# S2 变体镜像构建
# ---------------------------------------------------------------------------
step_s2_build_image() {
    if [ "$SKIP_BUILD_IMAGE" -eq 1 ]; then
        STEP_NOTE="--skip-build-image 指定，未重建"
        echo "  按 --skip-build-image 跳过镜像构建"
        return 3
    fi
    if ! podman image exists "$BASE_IMAGE" >/dev/null 2>&1; then
        STEP_NOTE="基线镜像缺失，无法构建"
        echo "  FAIL: 基线镜像 $BASE_IMAGE 缺失（见 S1 修复指引）" >&2
        return 1
    fi
    bash "$SCRIPT_DIR/build-image.sh"
    local rc=$?
    if [ "$rc" -eq 0 ]; then
        STEP_NOTE="$IMAGE 构建通过"
    else
        STEP_NOTE="build-image.sh rc=$rc"
    fi
    return "$rc"
}

# ---------------------------------------------------------------------------
# S3 容器启动
# ---------------------------------------------------------------------------
step_s3_container_up() {
    if require_container >/dev/null 2>&1; then
        echo "  容器 $CTR 已在运行，跳过重复启动（幂等）"
        STEP_NOTE="已在运行（未重启）"
        return 0
    fi
    bash "$SCRIPT_DIR/run.sh" up
    local rc=$?
    if [ "$rc" -eq 0 ]; then
        STEP_NOTE="run.sh up 通过"
    else
        STEP_NOTE="run.sh up rc=$rc"
    fi
    return "$rc"
}

# ---------------------------------------------------------------------------
# S4 挂载门禁
# ---------------------------------------------------------------------------
step_s4_verify() {
    if ! require_container; then
        STEP_NOTE="容器未运行"
        return 1
    fi
    bash "$SCRIPT_DIR/verify.sh"
    local rc=$?
    if [ "$rc" -eq 0 ]; then
        STEP_NOTE="verify.sh 13/13 通过"
    else
        STEP_NOTE="verify.sh rc=$rc"
    fi
    return "$rc"
}

# ---------------------------------------------------------------------------
# S5 LLVM 21 供给（幂等）
# ---------------------------------------------------------------------------
step_s5_llvm21() {
    if ! require_container; then
        STEP_NOTE="容器未运行"
        return 1
    fi

    # 幂等判据：包装器已存在且 --version 返回 21.x 则跳过复制。
    if podman exec "$CTR" test -x "$LLVM_PREFIX/bin/llvm-config" >/dev/null 2>&1; then
        local v
        v="$(podman exec "$CTR" "$LLVM_PREFIX/bin/llvm-config" --version 2>/dev/null)"
        case "$v" in
            21.*)
                echo "  LLVM $v 已就位（$LLVM_PREFIX），跳过复制"
                local inc lib
                inc="$(podman exec "$CTR" "$LLVM_PREFIX/bin/llvm-config" --includedir 2>/dev/null)"
                lib="$(podman exec "$CTR" "$LLVM_PREFIX/bin/llvm-config" --libdir 2>/dev/null)"
                echo "  includedir: $inc"
                echo "  libdir    : $lib"
                STEP_NOTE="已就位 LLVM $v（跳过复制）"
                return 0
            ;;
        esac
        echo "  已有 llvm-config 但版本为 '$v'，重新供给"
    fi

    # 宿主侧 LLVM 21 必须存在（LLVM 20 不可用）。
    local d missing=0
    for d in /usr/lib/llvm-21 /usr/include/llvm-21 /usr/include/llvm-c-21; do
        if [ ! -d "$d" ]; then
            echo "  FAIL: 宿主缺少 $d" >&2
            missing=1
        fi
    done
    if [ "$missing" -ne 0 ]; then
        echo "  FIX : 安装宿主 LLVM 21 开发包（源码依赖 Intrinsic::getOrInsertDeclaration）" >&2
        STEP_NOTE="宿主缺少 LLVM 21"
        return 1
    fi

    echo "  --- 复制 llvm-config / libLLVM / cmake / headers ---"
    podman exec "$CTR" mkdir -p "$LLVM_PREFIX/bin" "$LLVM_PREFIX/lib" "$LLVM_PREFIX/include" || {
        STEP_NOTE="容器内建目录失败"
        return 1
    }
    podman cp /usr/lib/llvm-21/bin/llvm-config "$CTR:$LLVM_PREFIX/bin/llvm-config.real" || {
        STEP_NOTE="llvm-config 复制失败"
        return 1
    }
    tar -C /usr/lib/llvm-21/lib -chf - libLLVM-21.so libLLVM.so libLLVM.so.1 libLLVM.so.21.0 \
        | podman exec -i "$CTR" tar -C "$LLVM_PREFIX/lib" -xf - || {
        STEP_NOTE="libLLVM 复制失败"
        return 1
    }
    tar -C /usr/lib/llvm-21 -chf - lib/cmake \
        | podman exec -i "$CTR" tar -C "$LLVM_PREFIX" -xf - || {
        STEP_NOTE="cmake 包复制失败"
        return 1
    }
    tar -C /usr/include/llvm-21 -chf - . \
        | podman exec -i "$CTR" tar -C "$LLVM_PREFIX/include" -xf - || {
        STEP_NOTE="llvm 头文件复制失败"
        return 1
    }
    tar -C /usr/include/llvm-c-21 -chf - . \
        | podman exec -i "$CTR" tar -C "$LLVM_PREFIX/include" -xf - || {
        STEP_NOTE="llvm-c 头文件复制失败"
        return 1
    }

    # 写 llvm-config 包装器：把宿主前缀改写为容器内前缀。
    podman exec -i "$CTR" bash -s <<'EOS'
set -uo pipefail
cat > /opt/build/llvm21/bin/llvm-config <<'WRAP'
#!/usr/bin/env bash
REAL=/opt/build/llvm21/bin/llvm-config.real
out="$("$REAL" "$@" 2>&1)"
rc=$?
printf '%s\n' "$out" | sed \
  -e 's#/usr/include/llvm-c-21#/opt/build/llvm21/include#g' \
  -e 's#/usr/include/llvm-21#/opt/build/llvm21/include#g' \
  -e 's#/usr/lib/llvm-21#/opt/build/llvm21#g'
exit "$rc"
WRAP
chmod +x /opt/build/llvm21/bin/llvm-config
EOS
    if [ $? -ne 0 ]; then
        STEP_NOTE="包装器写入失败"
        return 1
    fi

    echo "  --- 校验 ---"
    local ver inc lib
    ver="$(podman exec "$CTR" "$LLVM_PREFIX/bin/llvm-config" --version 2>/dev/null)"
    echo "  llvm-config --version: $ver"
    if ! printf '%s' "$ver" | grep -q '^21\.'; then
        echo "  FAIL: llvm-config --version 返回 '$ver'（期望 21.x）" >&2
        STEP_NOTE="版本校验失败: $ver"
        return 1
    fi
    inc="$(podman exec "$CTR" "$LLVM_PREFIX/bin/llvm-config" --includedir 2>/dev/null)"
    lib="$(podman exec "$CTR" "$LLVM_PREFIX/bin/llvm-config" --libdir 2>/dev/null)"
    echo "  includedir: $inc"
    echo "  libdir    : $lib"
    podman exec "$CTR" test -d "$inc" || {
        STEP_NOTE="includedir 不存在: $inc"
        return 1
    }
    podman exec "$CTR" test -e "$lib/libLLVM-21.so" || {
        STEP_NOTE="libLLVM-21.so 缺失"
        return 1
    }
    podman exec "$CTR" du -sh "$LLVM_PREFIX/bin" "$LLVM_PREFIX/include" "$LLVM_PREFIX/lib"
    STEP_NOTE="LLVM $ver 已供给"
    return 0
}

# ---------------------------------------------------------------------------
# S6 npu_tvm：cmake 配置 + ninja 构建 + 导入/目标断言
# ---------------------------------------------------------------------------
step_s6_npu_tvm() {
    if [ "$SKIP_TVM" -eq 1 ]; then
        STEP_NOTE="--skip-tvm 指定，未构建"
        echo "  按 --skip-tvm 跳过 npu_tvm 构建"
        return 3
    fi
    if ! require_container; then
        STEP_NOTE="容器未运行"
        return 1
    fi

    podman exec -i "$CTR" bash -s <<'EOS'
set -uo pipefail
# 仓库根没有 config.cmake，cmake/config.cmake 不会被 include，
# 因此 USE_CODEGENC / USE_LLVM 必须在命令行显式传入。
echo "  --- cmake configure ---"
cmake -G Ninja \
  -S /workspace/ai/notebook/libs/npu_tvm \
  -B /opt/build/npu_tvm \
  -DCMAKE_BUILD_TYPE=Release \
  -DUSE_CODEGENC=ON \
  -DUSE_LLVM=/opt/build/llvm21/bin/llvm-config
rc=$?
echo "  cmake rc=$rc"
[ "$rc" -eq 0 ] || exit 1

echo "  --- ninja tvm ---"
ninja -C /opt/build/npu_tvm tvm
rc=$?
echo "  ninja rc=$rc"
[ "$rc" -eq 0 ] || exit 1

test -f /opt/build/npu_tvm/libtvm.so || { echo "  FAIL: /opt/build/npu_tvm/libtvm.so 缺失"; exit 1; }
ls -l /opt/build/npu_tvm/libtvm.so

echo "  --- import tvm / Target 断言 ---"
export PYTHONPATH=/workspace/ai/notebook/libs/npu_tvm/python:/workspace/ai/notebook/libs/npu_tvm/vta/python:/workspace/ai/notebook/libs/npuusertools
export TVM_LIBRARY_PATH=/opt/build/npu_tvm
export PYTHONUSERBASE=/opt/build/npuusertools/userbase
export HOME=/tmp/tvmhome
export MPLCONFIGDIR=/tmp/mplconfig
# 新建卷重新构建的 libtvm.so 未必带 rpath，这里显式给动态库搜索路径兜底。
export LD_LIBRARY_PATH="/opt/build/llvm21/lib${LD_LIBRARY_PATH:+:$LD_LIBRARY_PATH}"
mkdir -p "$HOME" "$MPLCONFIGDIR"

python - <<'PY'
import tvm
print("  tvm.__version__ =", tvm.__version__)
assert tvm.__version__.startswith("0.19"), tvm.__version__
for key in ("llvm", "ccompiler"):
    tgt = tvm.target.Target(key)
    print('  Target("%s") -> %s' % (key, tgt))
print("  tvm file =", tvm.__file__)
PY
rc=$?
echo "  import rc=$rc"
[ "$rc" -eq 0 ] || exit 1
EOS
    local rc=$?
    if [ "$rc" -eq 0 ]; then
        STEP_NOTE="libtvm.so + import/Target 断言通过"
    else
        STEP_NOTE="npu_tvm 构建或断言失败 rc=$rc"
    fi
    return "$rc"
}

# ---------------------------------------------------------------------------
# S7 npuusertools：build.sh + editable 安装 + import xmnn 断言
# ---------------------------------------------------------------------------
step_s7_npuusertools() {
    if ! require_container; then
        STEP_NOTE="容器未运行"
        return 1
    fi

    podman exec -i "$CTR" bash -s <<'EOS'
set -uo pipefail
export HOME=/tmp/tvmhome
export PYTHONUSERBASE=/opt/build/npuusertools/userbase
mkdir -p "$HOME" /opt/build/npuusertools

cd /workspace/ai/notebook/libs/npuusertools || exit 1

echo "  --- build.sh (BUILD_DIR=/opt/build/npuusertools) ---"
BUILD_DIR=/opt/build/npuusertools bash scripts/build.sh
rc=$?
echo "  build.sh rc=$rc"
[ "$rc" -eq 0 ] || exit 1

# 系统 site-packages 只读，必须 --user + PYTHONUSERBASE 重定向前缀。
echo "  --- editable 安装（--user + PYTHONUSERBASE） ---"
python -m pip install --no-cache-dir --no-build-isolation --user -e . \
  --config-settings=build-dir=/opt/build/npuusertools
rc=$?
echo "  pip rc=$rc"
[ "$rc" -eq 0 ] || exit 1

echo "  --- import xmnn 路径断言 ---"
out="$(python -c 'import xmnn; print(xmnn.__file__)')"
rc=$?
echo "  import rc=$rc"
[ "$rc" -eq 0 ] || exit 1
echo "  xmnn.__file__ = $out"
case "$out" in
    /opt/build/npuusertools/userbase/*) ;;
    *)
        echo "  FAIL: xmnn 路径不在 /opt/build/npuusertools/userbase 下"
        exit 1
        ;;
esac
EOS
    local rc=$?
    if [ "$rc" -eq 0 ]; then
        STEP_NOTE="build/editable/import 断言通过"
    else
        STEP_NOTE="npuusertools 构建或断言失败 rc=$rc"
    fi
    return "$rc"
}

# ---------------------------------------------------------------------------
# S8 端到端冒烟（仅 --full，约 21 分钟）
# ---------------------------------------------------------------------------
step_s8_smoke() {
    if [ "$FULL" -ne 1 ]; then
        STEP_NOTE="未执行慢路径冒烟（需 --full）"
        echo "  未指定 --full，跳过端到端冒烟"
        return 3
    fi
    if ! require_container; then
        STEP_NOTE="容器未运行"
        return 1
    fi

    local smoke_log="$WS/.temp/npu-toolchain/logs/smoke-onnx-yolov5s-$(date +%Y%m%d-%H%M%S).log"
    echo "  冒烟日志: $smoke_log"

    podman exec -i -e SMOKE_LOG="$smoke_log" "$CTR" bash -s <<'EOS'
set -uo pipefail
export PYTHONPATH=/workspace/ai/notebook/libs/npu_tvm/python:/workspace/ai/notebook/libs/npu_tvm/vta/python:/workspace/ai/notebook/libs/npuusertools
export TVM_LIBRARY_PATH=/opt/build/npu_tvm
export PYTHONUSERBASE=/opt/build/npuusertools/userbase
export HOME=/tmp/tvmhome
export MPLCONFIGDIR=/tmp/mplconfig
export LD_LIBRARY_PATH="/opt/build/llvm21/lib${LD_LIBRARY_PATH:+:$LD_LIBRARY_PATH}"
mkdir -p "$HOME" "$MPLCONFIGDIR" "$(dirname "$SMOKE_LOG")"

cd /workspace/ai/notebook/libs/npuusertools || exit 1
start=$(date +%s)
python tools/compile.py -n onnx.yolov5s 2>&1 | tee "$SMOKE_LOG"
rc=${PIPESTATUS[0]}
elapsed=$(( $(date +%s) - start ))
echo "  compile rc=$rc elapsed=${elapsed}s"
[ "$rc" -eq 0 ] || exit 1
grep -q '模型编译全部完成' "$SMOKE_LOG" || { echo "  FAIL: 日志缺少“模型编译全部完成”"; exit 1; }
echo "  --- 产物 ---"
ls -l /workspace/ai/notebook/libs/npuusertools/temp/onnx.yolov5s/compile/ 2>/dev/null | head -20
EOS
    local rc=$?
    if [ "$rc" -eq 0 ]; then
        STEP_NOTE="onnx.yolov5s EXIT=0"
    else
        STEP_NOTE="冒烟失败 rc=$rc"
    fi
    return "$rc"
}

# ---------------------------------------------------------------------------
# S9 两库 git 洁净度（只读，不 checkout / restore / stash / clean）
# ---------------------------------------------------------------------------
step_s9_git_clean() {
    local u t u_lines t_lines other
    u="$(git -C "$NPUUTILS_HOST" status --porcelain 2>&1)"
    t="$(git -C "$NPU_TVM_HOST" status --porcelain 2>&1)"
    u_lines="$(printf '%s' "$u" | awk 'NF{n++} END{print n+0}')"
    t_lines="$(printf '%s' "$t" | awk 'NF{n++} END{print n+0}')"

    echo "  npuusertools: $u_lines 行"
    if [ "$u_lines" -gt 0 ]; then
        printf '%s\n' "$u" | awk 'NF{print "    " $0}'
    fi
    echo "  npu_tvm: $t_lines 行"
    if [ "$t_lines" -gt 0 ]; then
        printf '%s\n' "$t" | awk 'NF{print "    " $0}'
    fi

    # npu_tvm 仅允许用户既存改动 vta/python/vta/export_xm.py（不改不滚）。
    # porcelain 行为「XY <空格> 路径」，X/Y 各一位状态码，故前三位为状态码 + 分隔空格。
    other="$(printf '%s\n' "$t" | grep -vE '^.. vta/python/vta/export_xm\.py$' | awk 'NF{n++} END{print n+0}')"
    echo "  npu_tvm 除既存改动外的行数: $other"

    STEP_NOTE="npuusertools ${u_lines} 行 / npu_tvm ${t_lines} 行"
    if [ "$u_lines" -ne 0 ]; then
        echo "  FAIL: npuusertools 工作区不洁净（期望 0 行）" >&2
        return 1
    fi
    if [ "$other" -ne 0 ]; then
        echo "  FAIL: npu_tvm 出现 export_xm.py 之外的改动（期望 0 行）" >&2
        return 1
    fi
    return 0
}

# ---------------------------------------------------------------------------
# 主流程
# ---------------------------------------------------------------------------
main() {
    if ! command -v podman >/dev/null 2>&1; then
        echo "[all-in-one] FAIL: 未找到 podman（本脚本须在服务器 ai@10.16.11.3 上运行）" >&2
        exit 2
    fi
    if ! podman info >/dev/null 2>&1; then
        echo "[all-in-one] FAIL: podman 后端不可达（rootless socket 是否已起？）" >&2
        exit 2
    fi
    if ! mkdir -p "$LOG_DIR_HOST" 2>/dev/null; then
        echo "[all-in-one] FAIL: 无法创建日志目录 $LOG_DIR_HOST" >&2
        exit 2
    fi

    LOG="$LOG_DIR_HOST/all-in-one-$(date +%Y%m%d-%H%M%S).log"
    # 全量输出同时写日志并回显
    exec > >(tee -a "$LOG") 2>&1

    echo "[all-in-one] npu-toolchain 全链路"
    echo "  time      : $(date -Iseconds)"
    echo "  host uid  : $(id -u)"
    echo "  image     : $IMAGE"
    echo "  container : $CTR"
    echo "  options   : full=$FULL skip-build-image=$SKIP_BUILD_IMAGE skip-tvm=$SKIP_TVM"
    echo "  log       : $LOG"

    run_step S1 "base-image" step_s1_base_image
    run_step S2 "build-image" step_s2_build_image
    run_step S3 "container-up" step_s3_container_up
    run_step S4 "mount-gate" step_s4_verify
    run_step S5 "llvm21" step_s5_llvm21
    run_step S6 "npu_tvm" step_s6_npu_tvm
    run_step S7 "npuusertools" step_s7_npuusertools
    run_step S8 "e2e-smoke" step_s8_smoke
    run_step S9 "git-clean" step_s9_git_clean

    print_summary
    local failed=$?
    echo
    echo "日志: $LOG"
    if [ "$failed" -ne 0 ]; then
        echo "[all-in-one] FAIL: $failed 个步骤失败" >&2
        exit 1
    fi
    echo "[all-in-one] OK: 全部步骤通过（或按参数跳过）"
    exit 0
}

main