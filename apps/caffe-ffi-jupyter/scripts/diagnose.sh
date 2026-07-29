#!/bin/bash
# =============================================================================
# diagnose.sh — Caffe-FFI Docker 容器故障诊断与快速修复脚本
# 功能：自动检测 protobuf 版本冲突、共享库解析失败、环境变量问题等
# 使用：bash scripts/diagnose.sh [--container NAME] [--fix-protobuf] [--fix-ldpath]
# 日志格式：默认 text（人类可读），使用 --log-format=json 输出 JSON Lines 适配监控平台
# =============================================================================
set -euo pipefail

# ── 加载统一日志库 ──
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=lib/logging.sh
source "${SCRIPT_DIR}/lib/logging.sh"
LOG_SERVICE="caffe-ffi-diagnose"

# ── 默认参数 ──
CONTAINER_NAME="${CONTAINER_NAME:-caffe-ffi-jupyter}"
FIX_PROTOBUF=false
FIX_LDPATH=false
FIX_ALL=false
DUMP_INFO=false

# log_section 是 diagnose.sh 特有的分区输出，使用 log_step
log_section() { log_step "$*"; }

usage() {
    cat << EOF
${_CLR_BOLD}Caffe-FFI 容器故障诊断与修复工具${_CLR_RESET}

用法: bash scripts/diagnose.sh [选项]

${_CLR_BOLD}选项:${_CLR_RESET}
  --container NAME    指定容器名称（默认: caffe-ffi-jupyter）
  --fix-protobuf      尝试自动修复 protobuf 版本冲突
  --fix-ldpath        尝试自动修复共享库路径问题
  --fix-all           执行所有自动修复（protobuf + ldpath）
  --dump              导出完整诊断信息到文件
  --log-format FMT    日志格式: text (默认) | json
  --log-level LEVEL   日志级别: DEBUG|INFO|WARN|ERROR (默认: INFO)
  --log-json          JSON 同时输出到 stdout
  -h, --help          显示帮助

${_CLR_BOLD}监控平台集成:${_CLR_RESET}
  JSON 事件日志默认写入: /tmp/caffe-ffi-events.jsonl
  使用 --log-format=json 将主输出切换为 JSON Lines 格式

${_CLR_BOLD}诊断能力:${_CLR_RESET}
  1. 容器运行状态检查
  2. supervisord/SSH/Jupyter 服务状态
  3. conda 环境完整性（Python版本、包列表）
  4. protobuf 版本一致性（Python/C++/pip/conda 四重校验）
  5. _caffe_ffi.so 共享库依赖解析（ldd深度分析）
  6. RPATH 嵌入检查
  7. LD_LIBRARY_PATH 和 ld.so.conf.d 配置
  8. tvm_ffi 可发现性检查
  9. Jupyter Kernel 注册检查
  10. 构建日志分析（如可用）

${_CLR_BOLD}示例:${_CLR_RESET}
  bash scripts/diagnose.sh                              # 默认诊断
  bash scripts/diagnose.sh --container my-caffe         # 指定容器
  bash scripts/diagnose.sh --fix-all                    # 诊断并自动修复
  bash scripts/diagnose.sh --fix-protobuf               # 仅修复protobuf
  bash scripts/diagnose.sh --dump                       # 导出诊断报告
  bash scripts/diagnose.sh --log-format=json            # JSON 输出供监控采集
EOF
}

# ── 解析命令行参数 ──
_args=()
while [[ $# -gt 0 ]]; do
    case "$1" in
        --log-format=*) LOG_FORMAT="${1#*=}"; shift ;;
        --log-level=*)  LOG_LEVEL="${1#*=}"; shift ;;
        --log-json)     LOG_JSON_STDOUT=1; shift ;;
        --container)   CONTAINER_NAME="$2"; shift 2 ;;
        --fix-protobuf) FIX_PROTOBUF=true; shift ;;
        --fix-ldpath)  FIX_LDPATH=true; shift ;;
        --fix-all)     FIX_ALL=true; FIX_PROTOBUF=true; FIX_LDPATH=true; shift ;;
        --dump)        DUMP_INFO=true; shift ;;
        -h|--help)     usage; exit 0 ;;
        *) _args+=("$1"); shift ;;
    esac
done
set -- "${_args[@]:-}"

APP_DIR="$(dirname "$SCRIPT_DIR")"

# Docker exec 快捷方式
DEXEC="docker exec $CONTAINER_NAME bash -lc"
CONDA_ACT="source /opt/conda/etc/profile.d/conda.sh && conda activate caffe-ffi &&"

# ── 记录诊断启动事件 ──
log_set_field "container" "$CONTAINER_NAME"
log_event "diagnose_start" "fix_protobuf=$FIX_PROTOBUF" "fix_ldpath=$FIX_LDPATH" "fix_all=$FIX_ALL"

DIAG_OUTPUT=""
dump_log() {
    DIAG_OUTPUT+="$1"$'\n'
    echo "$1"
}

# ── 检查容器是否存在且运行 ──
check_container() {
    log_section "1. 容器状态检查"

    if ! docker ps -a --format '{{.Names}}' 2>/dev/null | grep -q "^${CONTAINER_NAME}$"; then
        log_error "容器 '$CONTAINER_NAME' 不存在！"
        log_info "可用容器列表："
        docker ps -a --format 'table {{.Names}}\t{{.Status}}\t{{.Image}}' 2>/dev/null || true
        exit 1
    fi

    CONTAINER_STATUS=$(docker inspect -f '{{.State.Status}}' "$CONTAINER_NAME" 2>/dev/null)
    CONTAINER_RUNNING=$(docker inspect -f '{{.State.Running}}' "$CONTAINER_NAME" 2>/dev/null)

    dump_log "容器名称: $CONTAINER_NAME"
    dump_log "容器状态: $CONTAINER_STATUS"
    dump_log "是否运行: $CONTAINER_RUNNING"

    if [ "$CONTAINER_RUNNING" != "true" ]; then
        log_fail "容器未运行（状态: $CONTAINER_STATUS）"
        log_info "尝试启动容器..."
        docker start "$CONTAINER_NAME" 2>/dev/null || {
            log_error "容器启动失败！查看日志："
            docker logs "$CONTAINER_NAME" 2>&1 | tail -30
            exit 1
        }
        sleep 10
        log_ok "容器已启动"
    else
        log_ok "容器运行中"
    fi

    # 容器运行时长
    UPTIME=$(docker ps --filter name="$CONTAINER_NAME" --format '{{.Status}}' 2>/dev/null)
    dump_log "运行信息: $UPTIME"
}

# ── 检查服务状态 ──
check_services() {
    log_section "2. 服务状态检查"

    # supervisord
    if $DEXEC "supervisorctl status" 2>/dev/null; then
        log_ok "supervisord 正常"
    else
        log_fail "supervisord 异常"
        dump_log "[FAIL] supervisord status check failed"
    fi

    # SSH
    if $DEXEC "supervisorctl status sshd" 2>/dev/null | grep -q RUNNING; then
        log_ok "SSH 服务运行中"
    else
        log_fail "SSH 服务未运行"
        dump_log "[FAIL] SSH service not running"
    fi

    # Jupyter
    JUPYTER_STATUS=$($DEXEC "supervisorctl status jupyter" 2>/dev/null || echo "UNKNOWN")
    if echo "$JUPYTER_STATUS" | grep -q RUNNING; then
        log_ok "Jupyter 服务运行中"
    else
        log_fail "Jupyter 服务异常: $JUPYTER_STATUS"
        dump_log "[FAIL] Jupyter service: $JUPYTER_STATUS"
    fi
}

# ── 检查 conda 环境 ──
check_conda_env() {
    log_section "3. Conda 环境检查"

    # conda 是否存在
    if ! $DEXEC "test -d /opt/conda/envs/caffe-ffi" 2>/dev/null; then
        log_fail "caffe-ffi conda 环境不存在！"
        dump_log "[FAIL] /opt/conda/envs/caffe-ffi not found"
        return 1
    fi
    log_ok "conda 环境目录存在"

    # Python 版本
    PY_VER=$($DEXEC "$CONDA_ACT python --version" 2>&1)
    dump_log "Python: $PY_VER"
    if echo "$PY_VER" | grep -q "Python 3.14"; then
        log_ok "$PY_VER"
    else
        log_warn "Python 版本异常: $PY_VER（期望 3.14.x）"
        dump_log "[WARN] Python version mismatch"
    fi

    # conda 包列表（关键包）
    log_info "关键 conda 包版本："
    for pkg in libprotobuf protobuf cmake ninja numpy openblas; do
        VER=$($DEXEC "$CONDA_ACT conda list | grep -E '^${pkg}[[:space:]]' | awk '{print \$2}'" 2>/dev/null || echo "NOT INSTALLED")
        if [ "$VER" = "NOT INSTALLED" ] || [ -z "$VER" ]; then
            log_fail "$pkg: 未安装"
            dump_log "[FAIL] conda package '$pkg' not found"
        else
            log_ok "$pkg: $VER"
        fi
    done

    # pip 包列表
    log_info "关键 pip 包版本："
    for pkg in scikit-build-core apache-tvm-ffi ipykernel caffe-ffi; do
        VER=$($DEXEC "$CONDA_ACT pip show $pkg 2>/dev/null | grep '^Version:' | awk '{print \$2}'" 2>/dev/null || echo "NOT INSTALLED")
        if [ "$VER" = "NOT INSTALLED" ] || [ -z "$VER" ]; then
            log_fail "$pkg: 未安装"
            dump_log "[FAIL] pip package '$pkg' not found"
        else
            log_ok "$pkg: $VER"
        fi
    done
}

# ── 检查 protobuf 版本一致性 ──
check_protobuf() {
    log_section "4. Protobuf 版本一致性检查（关键诊断项）"

    # Python protobuf
    PY_PB_VER=$($DEXEC "$CONDA_ACT python -c 'import google.protobuf; print(google.protobuf.__version__)'" 2>&1 || echo "IMPORT_ERROR")
    dump_log "Python protobuf: $PY_PB_VER"

    # Conda libprotobuf
    CONDA_PB_VER=$($DEXEC "$CONDA_ACT conda list libprotobuf | grep -E '^libprotobuf[[:space:]]' | awk '{print \$2}'" 2>/dev/null || echo "NOT FOUND")
    dump_log "Conda libprotobuf: $CONDA_PB_VER"

    # protoc 版本
    PROTOC_VER=$($DEXEC "$CONDA_ACT protoc --version 2>&1 | grep -oE '[0-9]+\.[0-9]+' | head -1" 2>/dev/null || echo "NOT FOUND")
    dump_log "protoc: $PROTOC_VER"

    # 系统 libprotobuf.so 版本
    SYS_PB_SO=$($DEXEC "ldconfig -p 2>/dev/null | grep libprotobuf.so | head -3" 2>&1 || echo "NOT FOUND")
    dump_log "System libprotobuf.so:"
    dump_log "$SYS_PB_SO"

    # caffe-ffi 链接的 protobuf
    CAFFE_PB=$($DEXEC "$CONDA_ACT _SO=\$(python -c 'import caffe_ffi,os; print(os.path.join(os.path.dirname(caffe_ffi.__file__), \"_caffe_ffi.so\"))' 2>/dev/null || echo ''); if [ -n \"\$_SO\" ]; then ldd \"\$_SO\" | grep protobuf; fi" 2>&1 || echo "CAFFE_FFI NOT IMPORTABLE")
    dump_log "caffe-ffi links protobuf:"
    dump_log "$CAFFE_PB"

    PROTOBUF_OK=true

    # 检查 Python protobuf >= 7
    if echo "$PY_PB_VER" | grep -qE '^[7-9]\.|^[1-9][0-9]\.'; then
        log_ok "Python protobuf 版本: $PY_PB_VER (>= 7.0.0)"
    else
        log_fail "Python protobuf 版本过低: $PY_PB_VER（要求 >= 7.0.0）"
        PROTOBUF_OK=false
    fi

    # 检查 protoc 版本一致性
    if [ "$PROTOC_VER" != "NOT FOUND" ]; then
        if echo "$PROTOC_VER" | grep -qE '^[7-9]\.|^[1-9][0-9]\.'; then
            log_ok "protoc 版本: $PROTOC_VER"
        else
            log_warn "protoc 版本: $PROTOC_VER（可能与 Python protobuf 不一致）"
        fi
    fi

    # 版本一致性比较（Python protobuf 主版本 vs libprotobuf 主版本）
    PY_PB_MAJOR=$(echo "$PY_PB_VER" | cut -d. -f1)
    if [ "$CONDA_PB_VER" != "NOT FOUND" ]; then
        CONDA_PB_MAJOR=$(echo "$CONDA_PB_VER" | cut -d. -f1)
        if [ "$PY_PB_MAJOR" = "$CONDA_PB_MAJOR" ]; then
            log_ok "Python protobuf ($PY_PB_MAJOR.x) 与 conda libprotobuf ($CONDA_PB_MAJOR.x) 主版本一致"
        else
            log_fail "版本不一致！Python protobuf=$PY_PB_MAJOR.x, conda libprotobuf=$CONDA_PB_MAJOR.x"
            PROTOBUF_OK=false
        fi
    fi

    if ! $PROTOBUF_OK; then
        log_error "检测到 protobuf 版本问题！"
        if $FIX_PROTOBUF || $FIX_ALL; then
            fix_protobuf
        else
            log_info "使用 --fix-protobuf 参数尝试自动修复"
        fi
    fi
}

# ── 检查共享库依赖 ──
check_shared_libs() {
    log_section "5. 共享库依赖解析检查（关键诊断项）"

    # 获取 _caffe_ffi.so 路径
    _CAFFE_SO=$($DEXEC "$CONDA_ACT python -c 'import caffe_ffi, os; print(os.path.join(os.path.dirname(caffe_ffi.__file__), \"_caffe_ffi.so\"))'" 2>/dev/null || echo "")

    if [ -z "$_CAFFE_SO" ]; then
        log_fail "无法定位 _caffe_ffi.so（caffe_ffi 可能无法导入）"
        # 尝试直接搜索
        log_info "搜索 _caffe_ffi.so 文件..."
        FOUND_SO=$($DEXEC "find /opt/conda/envs/caffe-ffi -name '_caffe_ffi.so' 2>/dev/null | head -3" || echo "")
        if [ -n "$FOUND_SO" ]; then
            log_info "找到 _caffe_ffi.so: $FOUND_SO"
            _CAFFE_SO="$FOUND_SO"
        else
            log_fail "_caffe_ffi.so 未找到，caffe-ffi 可能未正确安装"
            dump_log "[FAIL] _caffe_ffi.so not found in container"
            return 1
        fi
    fi

    dump_log "_caffe_ffi.so: $_CAFFE_SO"

    # 文件存在性
    if $DEXEC "test -f '$_CAFFE_SO'"; then
        log_ok "_caffe_ffi.so 存在"
    else
        log_fail "_caffe_ffi.so 文件不存在"
        return 1
    fi

    # ldd 完整输出
    log_info "ldd _caffe_ffi.so 输出："
    LDD_FULL=$($DEXEC "ldd '$_CAFFE_SO'" 2>&1)
    echo "$LDD_FULL"
    dump_log "=== ldd _caffe_ffi.so ==="
    dump_log "$LDD_FULL"

    # 检查 not found
    if echo "$LDD_FULL" | grep -q 'not found'; then
        UNRESOLVED=$(echo "$LDD_FULL" | grep 'not found')
        log_fail "存在未解析的共享库依赖："
        echo "$UNRESOLVED"
        dump_log "[FAIL] Unresolved shared libraries:"
        dump_log "$UNRESOLVED"
        LDPATH_OK=false
    else
        log_ok "所有共享库依赖已解析"
        LDPATH_OK=true
    fi

    # RPATH 检查
    log_info "RPATH 检查（readelf -d）："
    if $DEXEC "command -v readelf" &>/dev/null; then
        RPATH_INFO=$($DEXEC "readelf -d '$_CAFFE_SO' | grep -E 'RPATH|RUNPATH'" 2>&1 || echo "NO RPATH")
        echo "$RPATH_INFO"
        dump_log "RPATH/RUNPATH: $RPATH_INFO"
        if echo "$RPATH_INFO" | grep -q -E 'RPATH|RUNPATH'; then
            log_ok "RPATH/RUNPATH 已嵌入"
        else
            log_warn "未嵌入 RPATH/RUNPATH（依赖 LD_LIBRARY_PATH 或 ldconfig）"
        fi
    else
        log_warn "readelf 不可用，跳过 RPATH 检查"
    fi

    # LD_LIBRARY_PATH 检查
    log_info "LD_LIBRARY_PATH 环境变量："
    LPATH=$($DEXEC "echo \$LD_LIBRARY_PATH" 2>&1)
    echo "  LD_LIBRARY_PATH=$LPATH"
    dump_log "LD_LIBRARY_PATH=$LPATH"

    # ld.so.conf.d 检查
    log_info "/etc/ld.so.conf.d/caffe-ffi.conf："
    LDCONF=$($DEXEC "cat /etc/ld.so.conf.d/caffe-ffi.conf 2>/dev/null || echo 'FILE NOT FOUND'")
    echo "$LDCONF"
    dump_log "ld.so.conf.d/caffe-ffi.conf:"
    dump_log "$LDCONF"

    # conda lib 目录
    CONDA_LIB="/opt/conda/envs/caffe-ffi/lib"
    if echo "$LPATH" | grep -q "$CONDA_LIB" || echo "$LDCONF" | grep -q "$CONDA_LIB"; then
        log_ok "conda lib 目录已在库搜索路径中"
    else
        log_fail "conda lib 目录未在库搜索路径中！"
        LDPATH_OK=false
    fi

    if [ "${LDPATH_OK:-true}" = "false" ]; then
        if $FIX_LDPATH || $FIX_ALL; then
            fix_ldpath
        else
            log_info "使用 --fix-ldpath 参数尝试自动修复"
        fi
    fi
}

# ── 检查 tvm_ffi ──
check_tvm_ffi() {
    log_section "6. tvm_ffi 依赖检查"

    TVM_FFI_VER=$($DEXEC "$CONDA_ACT python -c 'import tvm_ffi; print(tvm_ffi.__version__)' 2>&1" || echo "IMPORT_ERROR")
    TVM_FFI_PATH=$($DEXEC "$CONDA_ACT python -c 'import tvm_ffi, os; print(os.path.dirname(tvm_ffi.__file__))' 2>&1" || echo "NOT FOUND")
    dump_log "tvm_ffi version: $TVM_FFI_VER"
    dump_log "tvm_ffi path: $TVM_FFI_PATH"

    if [ "$TVM_FFI_VER" = "IMPORT_ERROR" ]; then
        log_fail "tvm_ffi 导入失败！"

        # 尝试 tvm.ffi
        TVM_FFI_ALT=$($DEXEC "$CONDA_ACT python -c 'import tvm.ffi; print(\"tvm.ffi available\")' 2>&1" || echo "NOT FOUND")
        if [ "$TVM_FFI_ALT" != "NOT FOUND" ]; then
            log_warn "tvm.ffi 可用但 tvm_ffi 不可用，包名可能不一致"
        else
            log_fail "tvm.ffi 也不可用，apache-tvm-ffi 可能未安装或安装失败"
        fi
    else
        log_ok "tvm_ffi $TVM_FFI_VER at $TVM_FFI_PATH"
    fi

    # tvm_ffi 共享库
    if [ "$TVM_FFI_PATH" != "NOT FOUND" ]; then
        TVM_SO=$($DEXEC "find '$TVM_FFI_PATH' -name 'libtvm_ffi*.so' -o -name '_tvm_ffi*.so' 2>/dev/null | head -5" || echo "")
        if [ -n "$TVM_SO" ]; then
            log_info "tvm_ffi 共享库："
            echo "$TVM_SO"
        else
            log_warn "tvm_ffi 目录中未找到 .so 文件"
        fi
    fi
}

# ── 检查 Jupyter Kernel ──
check_jupyter_kernel() {
    log_section "7. Jupyter Kernel 注册检查"

    KERNELS=$($DEXEC "jupyter kernelspec list 2>/dev/null" || echo "JUPYTER NOT IN PATH")
    dump_log "Jupyter kernels:"
    dump_log "$KERNELS"
    echo "$KERNELS"

    if echo "$KERNELS" | grep -q caffe-ffi; then
        log_ok "caffe-ffi kernel 已注册"
        KERNEL_PATH=$($DEXEC "jupyter kernelspec list 2>/dev/null | grep caffe-ffi | awk '{print \$2}'" || echo "")
        if [ -n "$KERNEL_PATH" ]; then
            KERNEL_JSON=$($DEXEC "cat ${KERNEL_PATH}/kernel.json 2>/dev/null" || echo "")
            dump_log "kernel.json:"
            dump_log "$KERNEL_JSON"
        fi
    else
        log_fail "caffe-ffi kernel 未注册！"
        if $FIX_ALL; then
            log_info "尝试注册 Jupyter kernel..."
            $DEXEC "$CONDA_ACT python -m ipykernel install --name caffe-ffi --display-name 'Python 3.14 (caffe-ffi)' --prefix=/usr/local --replace" 2>&1 && log_ok "Kernel 注册成功"
        fi
    fi
}

# ── 修复 protobuf ──
fix_protobuf() {
    log_section "🔧 自动修复: Protobuf 版本冲突"

    log_info "在 conda 环境中重新安装 protobuf>=7.0.0..."
    $DEXEC "$CONDA_ACT pip install --no-cache-dir 'protobuf>=7.0.0' --force-reinstall" 2>&1 | tail -10 || {
        log_warn "pip 安装失败，尝试 conda 安装..."
        $DEXEC "$CONDA_ACT conda install -y -c conda-forge 'libprotobuf>=7.0.0' 'protobuf>=7.0.0'" 2>&1 | tail -10 || true
    }

    # 验证修复
    NEW_VER=$($DEXEC "$CONDA_ACT python -c 'import google.protobuf; print(google.protobuf.__version__)'" 2>&1)
    if echo "$NEW_VER" | grep -qE '^[7-9]\.|^[1-9][0-9]\.'; then
        log_ok "修复成功！protobuf 版本: $NEW_VER"
    else
        log_warn "修复后版本仍有问题: $NEW_VER"
        log_info "手动修复命令："
        echo "  docker exec -it $CONTAINER_NAME bash"
        echo "  source /opt/conda/etc/profile.d/conda.sh && conda activate caffe-ffi"
        echo "  pip install 'protobuf>=7.0.0' --force-reinstall"
        echo "  # 或"
        echo "  conda install -y -c conda-forge 'protobuf>=7.0.0' 'libprotobuf>=7.0.0'"
    fi
}

# ── 修复共享库路径 ──
fix_ldpath() {
    log_section "🔧 自动修复: 共享库路径问题"

    log_info "步骤1: 重建 ld.so.conf.d 配置..."
    $DEXEC "bash -c '
source /opt/conda/etc/profile.d/conda.sh && conda activate caffe-ffi
TVM_DIR=\$(python -c \"import tvm_ffi, os; print(os.path.dirname(tvm_ffi.__file__))\" 2>/dev/null || echo \"\")
CAFFE_DIR=\$(python -c \"import caffe_ffi, os; print(os.path.dirname(caffe_ffi.__file__))\" 2>/dev/null || echo \"\")
echo \"/opt/conda/envs/caffe-ffi/lib\" > /etc/ld.so.conf.d/caffe-ffi.conf
[ -n \"\$TVM_DIR\" ] && echo \"\$TVM_DIR\" >> /etc/ld.so.conf.d/caffe-ffi.conf
[ -n \"\$CAFFE_DIR\" ] && echo \"\$CAFFE_DIR\" >> /etc/ld.so.conf.d/caffe-ffi.conf
ldconfig
echo \"ldconfig updated\"
cat /etc/ld.so.conf.d/caffe-ffi.conf
'" 2>&1

    log_info "步骤2: 确保 LD_LIBRARY_PATH 正确..."
    # 更新 /etc/environment 和 .bashrc
    $DEXEC "grep -q 'caffe-ffi/lib' /home/jupyteruser/.bashrc 2>/dev/null || echo 'export LD_LIBRARY_PATH=/opt/conda/envs/caffe-ffi/lib:\${LD_LIBRARY_PATH}' >> /home/jupyteruser/.bashrc" 2>&1

    log_info "步骤3: 验证修复..."
    _SO=$($DEXEC "$CONDA_ACT python -c 'import caffe_ffi, os; print(os.path.join(os.path.dirname(caffe_ffi.__file__), \"_caffe_ffi.so\"))'" 2>/dev/null || echo "")
    if [ -n "$_SO" ]; then
        LDD_CHECK=$($DEXEC "ldd '$_SO' 2>&1 | grep 'not found'" || echo "ALL RESOLVED")
        if [ "$LDD_CHECK" = "ALL RESOLVED" ] || [ -z "$LDD_CHECK" ]; then
            log_ok "共享库修复成功！所有依赖已解析"
        else
            log_warn "仍有未解析依赖："
            echo "$LDD_CHECK"
            log_info "可能需要重新 pip 安装 caffe-ffi："
            echo "  docker exec -it $CONTAINER_NAME bash"
            echo "  source /opt/conda/etc/profile.d/conda.sh && conda activate caffe-ffi"
            echo "  pip install /path/to/caffe-ffi --no-build-isolation -v"
        fi
    fi
}

# ── 主诊断流程 ──
log_section "Caffe-FFI 容器诊断工具"
log_info "目标容器: $CONTAINER_NAME"
log_info "修复模式: protobuf=$FIX_PROTOBUF, ldpath=$FIX_LDPATH"
echo ""

check_container
check_services
check_conda_env
check_protobuf
check_shared_libs
check_tvm_ffi
check_jupyter_kernel

# ── 导出诊断报告 ──
if $DUMP_INFO; then
    REPORT_FILE="/tmp/caffe-ffi-diag-$(date +%Y%m%d-%H%M%S).log"
    echo "$DIAG_OUTPUT" > "$REPORT_FILE"
    echo ""
    log_info "完整诊断报告已导出到: $REPORT_FILE"
fi

# ── 总结 ──
log_section "诊断完成"
log_event "diagnose_complete" "protobuf_ok=$([ -z "${PROTOBUF_ISSUES:-}" ] && echo true || echo false)" \
  "ldpath_ok=$([ "${LDPATH_OK:-true}" = "true" ] && echo true || echo false)"
echo -e "${_CLR_CYAN}快速修复命令参考：${_CLR_RESET}"
echo "  bash scripts/diagnose.sh --container $CONTAINER_NAME --fix-all"
echo ""
echo -e "${_CLR_CYAN}手动进入容器调试：${_CLR_RESET}"
echo "  docker exec -it $CONTAINER_NAME bash"
echo "  source /opt/conda/etc/profile.d/conda.sh && conda activate caffe-ffi"
echo ""
echo -e "${_CLR_CYAN}重新构建镜像（终极方案）：${_CLR_RESET}"
echo "  bash scripts/build.sh --cn --no-cache --verify"
echo ""
echo -e "${_CLR_CYAN}详细部署指南：${_CLR_RESET}"
echo "  参见 WSL-DEPLOY-GUIDE.md"
echo -e "${_CLR_GRAY}JSON 事件日志: ${LOG_JSON_OUTPUT}${_CLR_RESET}"
