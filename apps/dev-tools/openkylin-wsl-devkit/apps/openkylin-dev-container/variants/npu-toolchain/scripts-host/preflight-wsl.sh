#!/usr/bin/env bash
# preflight-wsl.sh — WSL 宿主侧只读预检脚本
#
# 用途：在 WSL OpenKylin 发行版内执行，验证宿主环境是否具备跑通
#       npu-toolchain 容器的全部前置条件（规格 v1.1 阶段 1）
#
# 执行方式：
#   bash scripts-host/preflight-wsl.sh
#
# 退出码：
#   0 — 全部 PASS
#   非 0 — 有 FAIL 项，按类别号返回（10+A, 20+B, 30+C, 40+D, 50+E）
#
# 约束：
#   * 只读检查，不执行任何 mount / install / build 命令
#   * 不依赖网络访问（除了 conda-forge llvmdev 可达性探测可跳过）
#   * 不输出任何凭据或敏感信息

set -euo pipefail

# ---------------------------------------------------------------------------
# 颜色 + 输出辅助
# ---------------------------------------------------------------------------
PASS='\033[32m[PASS]\033[0m'
FAIL='\033[31m[FAIL]\033[0m'
INFO='\033[36m[INFO]\033[0m'
WARN='\033[33m[WARN]\033[0m'

_log()  { local level=$1; shift; echo -e "  $level $*"; }
_ok()   { _log "$PASS" "$*"; }
_bad()  { _log "$FAIL" "$*"; ((failures++)); }
_info() { _log "$INFO" "$*"; }
_warn() { _log "$WARN" "$*"; ((warnings++)); }

section() { echo; echo "══════ $1 ══════"; }

failures=0
warnings=0

# ===================================================================
# A. 宿主身份 — OpenKylin 版本 / UID / GID / 非 root
# ===================================================================
section "A. 宿主身份"

os_id="unknown"
os_ver="unknown"
if [[ -f /etc/os-release ]]; then
    # shellcheck disable=SC1091
    source /etc/os-release
    os_id="$ID"
    os_ver="$VERSION_ID"
    _ok "/etc/os-release → $os_id $os_ver (PRETTY_NAME=$PRETTY_NAME)"
else
    _bad "/etc/os-release 不存在，无法识别发行版"
fi

host_uid="$(id -u)"
host_gid="$(id -g)"
host_user="$(id -un)"
_ok "宿主用户: $host_user  uid=$host_uid  gid=$host_gid"

if [[ $host_uid -eq 0 ]]; then
    _bad "宿主用户是 root (uid=0) — 规格要求 userns=keep-id 下宿主 UID ≠ 0"
else
    _ok "宿主 UID ≠ 0，userns=keep-id 可用"
fi

# ===================================================================
# B. rootless Podman
# ===================================================================
section "B. rootless Podman"

if command -v podman &>/dev/null; then
    _ok "podman 可用 → $(podman --version | head -n1)"

    if rootless_status="$(podman info --format '{{.Host.Security.Rootless}}' 2>&1)"; then
        if [[ "$rootless_status" == "true" ]]; then
            _ok "Podman rootless=true"
        else
            _bad "Podman rootless=$rootless_status （应为 true）"
        fi
    else
        _bad "podman info 执行失败: $rootless_status"
    fi

    _info "compose 可用性: $(podman compose version 2>&1 || echo '(podman compose not available)')"
else
    _bad "podman 不可用 — 请先安装 rootless Podman（okw podman preflight/install/verify）"
fi

# /etc/subuid / /etc/subgid — keep-id 不依赖它们，但记录现状
if [[ -f /etc/subuid ]]; then
    _info "/etc/subuid: $(wc -l < /etc/subuid) 行（keep-id 模式下不使用，但记录现状）"
    grep -q "^$host_user:" /etc/subuid && _info "subuid 条目存在" || _warn "subuid 无 $host_user 条目（keep-id 正常工作仍 OK）"
else
    _info "/etc/subuid 不存在（keep-id 正常工作仍 OK）"
fi
if [[ -f /etc/subgid ]]; then
    _info "/etc/subgid: $(wc -l < /etc/subgid) 行"
else
    _info "/etc/subgid 不存在（keep-id 正常工作仍 OK）"
fi

# ===================================================================
# C. CIFS/SMB 挂载
# ===================================================================
section "C. CIFS/SMB 挂载"

# C1 mount.cifs / cifs-utils
if command -v mount.cifs &>/dev/null; then
    _ok "mount.cifs 可用 → $(mount.cifs -V 2>&1 | head -n1)"
else
    _bad "mount.cifs 不可用 — WSL 内需要 cifs-utils 包（apt install cifs-utils）"
fi

# C2 SMB 凭据（只读检查是否导出，不打印值）
if [[ -n "${SMB_USER:-}" && -n "${SMB_PASS:-}" ]]; then
    _ok "SMB_USER / SMB_PASS 环境变量已导出"
else
    _warn "SMB_USER / SMB_PASS 未导出 — 需要时请 export SMB_USER=...; export SMB_PASS=... 后再执行 mount.cifs"
fi

# C3 drvfs 自动挂载（Windows 盘符）
drvfs_found=()
for mnt in /mnt/s /mnt/c /mnt/d /mnt/e /mnt/f; do
    if [[ -d "$mnt" ]]; then
        # 取第一个文件名做存在性探测
        if file_count=$(find "$mnt" -maxdepth 1 -mindepth 1 2>/dev/null | head -n5 | wc -l); then
            owner=$(stat -c '%u:%g' "$mnt" 2>/dev/null || echo "unknown")
            _info "drvfs 挂载点 $mnt 存在（属主 $owner）"
            drvfs_found+=("$mnt")
        fi
    fi
done
if [[ ${#drvfs_found[@]} -eq 0 ]]; then
    _warn "未发现 drvfs 自动挂载的 Windows 盘符（/mnt/s /mnt/c 等）"
fi

# C4 共享目录可达性（UNC 路径或已挂载点）
target="//10.16.11.3/ai"
probe_ok=false
# 路径 1: drvfs 挂载点 S 盘
if [[ -d /mnt/s ]]; then
    if [[ -f /mnt/s/notebook/libs/npu_tvm/CMakeLists.txt ]]; then
        _ok "通过 drvfs /mnt/s 可达 npu_tvm CMakeLists.txt"
        probe_ok=true
    fi
fi
# 路径 2: WSL 侧 CIFS 挂载点（规格预配置 /mnt/srv/ai）
if [[ -d /mnt/srv/ai ]]; then
    if [[ -f /mnt/srv/ai/notebook/libs/npu_tvm/CMakeLists.txt ]]; then
        _ok "通过 CIFS 挂载点 /mnt/srv/ai 可达 npu_tvm CMakeLists.txt"
        probe_ok=true
    fi
fi
if [[ $probe_ok == false ]]; then
    _bad "共享目录 $target 不可达 — 请先在 WSL 内挂载 CIFS（见规格 §3.2）或检查 drvfs"
fi

# ===================================================================
# D. LLVM ≥ 21（21 或 22）
# ===================================================================
section "D. LLVM ≥ 21"

llvm_ok=false
llvm_ver=""

if command -v llvm-config &>/dev/null; then
    llvm_ver="$(llvm-config --version 2>/dev/null || echo 'unknown')"
    major_ver="${llvm_ver%%.*}"
    if [[ "$major_ver" =~ ^[0-9]+$ ]] && (( major_ver >= 21 )); then
        _ok "llvm-config 可用 → $llvm_ver (≥ 21, 通过)"
        _ok "llvm-config --libfiles: $(llvm-config --libfiles 2>/dev/null | wc -w) 个文件"
        _ok "llvm-config --cmakedir: $(llvm-config --cmakedir 2>/dev/null || echo '(none)')"
        llvm_ok=true
    elif [[ "$major_ver" =~ ^[0-9]+$ ]]; then
        _bad "llvm-config 版本 $llvm_ver < 21"
    else
        _warn "llvm-config --version 输出异常: '$llvm_ver'"
    fi
else
    _warn "llvm-config 不可用 — 需要获取 LLVM ≥ 21（21 或 22）"
    llvm_ver="(not installed)"
fi

# D2 conda-forge llvmdev 可达性探测（只读：看宿主 conda/miniforge 是否存在）
if command -v conda &>/dev/null; then
    _info "宿主 conda 可用 → $(conda --version)"
    # 只读探测：不实际安装，仅测试镜像可达性
    # 注：如果不想等待网络，这步可以跳过
    if [[ -n "${LLVM_PROBE_NETWORK:-}" ]]; then
        _info "网络探测模式启用：测试 conda-forge USTC 镜像是否可达..."
        if timeout 10 conda search -c https://mirrors.ustc.edu.cn/anaconda/cloud/conda-forge llvmdev --info 2>&1 | grep -q "conda-forge/linux-64"; then
            _ok "conda-forge llvmdev USTC 镜像可达"
        else
            _warn "conda-forge llvmdev USTC 镜像可能不可达（timeout=10s），请手动确认"
        fi
    else
        _info "提示：设置 LLVM_PROBE_NETWORK=1 可启用 conda-forge 网络探测（默认跳过）"
    fi
else
    _warn "宿主 conda 不可用 — 若计划用 conda-forge 安装 llvmdev，需先装 Miniforge3"
fi

if [[ $llvm_ok == false ]]; then
    _bad "LLVM ≥ 21 未就绪 — 获取选项：(a) conda-forge llvmdev ~59MB (b) 服务器 scp /usr/lib/llvm-21 ~300MB (c) 容器 bind mount 宿主路径"
fi

# ===================================================================
# E. 构建基础
# ===================================================================
section "E. 构建基础"

for tool in gcc g++ cmake make git python3; do
    if command -v "$tool" &>/dev/null; then
        ver=$("$tool" --version 2>&1 | head -n1)
        _ok "$tool → $ver"
    else
        _warn "$tool 不可用（容器内 conda-forge 会提供宿主级 gcc/g++ 仍需）"
    fi
done

# ===================================================================
# 汇总
# ===================================================================
echo
echo "══════ 预检汇总 ══════"
echo "  失败: $failures   警告: $warnings"
echo
if [[ $failures -eq 0 ]]; then
    echo -e "  ${PASS} 全部检查通过 — 宿主环境就绪"
    echo "  下一步：阶段 2（CIFS 挂载 + 容器启动）"
    exit 0
else
    echo -e "  ${FAIL} 有 $failures 项失败 — 请按上方建议修复后重跑"
    exit $((failures * 10))
fi
