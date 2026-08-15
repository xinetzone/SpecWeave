#!/usr/bin/env bash
# setup-wsl-docker-gpu.sh
# WSL2 Docker GPU支持一键配置脚本（幂等安全，可重复执行）
#
# 运行位置：WSL2 Ubuntu（24.04/26.04）内部，需要sudo权限
# 用法：
#   sudo bash setup-wsl-docker-gpu.sh          # 完整安装配置+验证
#   sudo bash setup-wsl-docker-gpu.sh --verify # 仅验证当前状态
#   sudo bash setup-wsl-docker-gpu.sh --mirror ustc  # 使用中科大镜像（国内推荐）
#   sudo bash setup-wsl-docker-gpu.sh --mirror official  # 使用NVIDIA官方源
#
# 功能：
#   1. 三层诊断（L1驱动→L2工具→L3运行时）
#   2. 幂等安装nvidia-container-toolkit（不重复安装）
#   3. 配置Docker nvidia runtime
#   4. 配置wsl.conf [boot]开机自启（幂等更新）
#   5. 启动/重启Docker守护进程（WSL无systemd模式）
#   6. 端到端验证

set -euo pipefail

# ============================================================
# 配置
# ============================================================

MIRROR="ustc"  # ustc | official
ONLY_VERIFY=false
WSL_CONF="/etc/wsl.conf"
DOCKER_DAEMON_JSON="/etc/docker/daemon.json"
NVIDIA_SOURCE_LIST="/etc/apt/sources.list.d/nvidia-container-toolkit.list"
NVIDIA_KEYRING="/usr/share/keyrings/nvidia-container-toolkit-keyring.gpg"
ARCH=$(dpkg --print-architecture)
BACKUP_SUFFIX=".bak.$(date +%Y%m%d%H%M%S)"
UBUNTU_CODENAME=$(. /etc/os-release && echo "${VERSION_CODENAME:-noble}")

# 颜色
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
CYAN='\033[0;36m'
GRAY='\033[0;90m'
NC='\033[0m'

# ============================================================
# 辅助函数
# ============================================================

log_step()  { echo -e "\n${CYAN}[*] $*${NC}"; }
log_pass()  { echo -e "${GREEN}[PASS] $*${NC}"; }
log_fail()  { echo -e "${RED}[FAIL] $*${NC}"; }
log_warn()  { echo -e "${YELLOW}[WARN] $*${NC}"; }
log_info()  { echo -e "${GRAY}       $*${NC}"; }

check_root() {
    if [ "$(id -u)" -ne 0 ]; then
        log_fail "此脚本需要root权限，请用 sudo 运行"
        exit 1
    fi
}

backup_file() {
    local f="$1"
    if [ -f "$f" ] && [ ! -f "${f}${BACKUP_SUFFIX}" ]; then
        cp "$f" "${f}${BACKUP_SUFFIX}"
        log_info "已备份: ${f} -> ${f}${BACKUP_SUFFIX}"
    fi
}

# ============================================================
# 参数解析
# ============================================================

while [ $# -gt 0 ]; do
    case "$1" in
        --verify) ONLY_VERIFY=true; shift ;;
        --mirror) MIRROR="$2"; shift 2 ;;
        --help|-h)
            head -20 "$0" | grep '^#' | sed 's/^# \{0,1\}//'
            exit 0 ;;
        *) echo "未知参数: $1"; exit 1 ;;
    esac
done

# ============================================================
# 诊断函数
# ============================================================

check_l1_driver() {
    if command -v nvidia-smi &>/dev/null && nvidia-smi &>/dev/null; then
        local drv_ver=$(nvidia-smi 2>/dev/null | grep 'Driver Version' | awk '{print $6}')
        local gpu_name=$(nvidia-smi 2>/dev/null | grep '|.*NVIDIA' | head -1 | sed 's/|//g' | awk '{print $2,$3,$4}' | xargs)
        log_pass "L1驱动层: nvidia-smi正常"
        log_info "GPU: ${gpu_name:-NVIDIA GPU} | 驱动: ${drv_ver:-unknown}"
        return 0
    else
        log_fail "L1驱动层: nvidia-smi不可用"
        log_info "  修复: 检查Windows侧NVIDIA驱动是否安装，执行 wsl --shutdown 后重试"
        return 1
    fi
}

check_l2_toolkit() {
    local ok=true
    if ! dpkg -l nvidia-container-toolkit &>/dev/null | grep -q '^ii'; then
        log_fail "L2工具层: nvidia-container-toolkit未安装"; ok=false
    else
        log_pass "L2工具层: nvidia-container-toolkit已安装"
    fi
    if ! command -v nvidia-container-runtime &>/dev/null; then
        log_fail "L2工具层: nvidia-container-runtime不在PATH"; ok=false
    fi
    if ! command -v nvidia-ctk &>/dev/null; then
        log_fail "L2工具层: nvidia-ctk不在PATH"; ok=false
    fi
    if [ "$ok" = true ]; then
        local ver=$(nvidia-ctk --version 2>/dev/null | head -1 || echo "unknown")
        log_info "$ver"
    fi
    $ok && return 0 || return 1
}

check_l3_runtime() {
    if ! docker info &>/dev/null; then
        log_fail "L3运行时层: Docker daemon未运行"
        return 1
    fi
    if docker info 2>&1 | grep -q 'nvidia'; then
        log_pass "L3运行时层: Docker nvidia runtime已注册"
        local runtimes=$(docker info 2>&1 | grep Runtimes | awk -F: '{print $2}' | xargs)
        log_info "Runtimes: $runtimes"
        return 0
    else
        log_fail "L3运行时层: Docker nvidia runtime未注册"
        log_info "  需要执行: nvidia-ctk runtime configure --runtime=docker && 重启Docker"
        return 1
    fi
}

check_gpu_container() {
    # 优先用已有的轻量镜像
    local test_image=""
    for img in ubuntu:22.04 ubuntu:24.04; do
        if docker images "$img" --format '{{.Repository}}:{{.Tag}}' 2>/dev/null | grep -q "$img"; then
            test_image="$img"
            break
        fi
    done

    if [ -z "$test_image" ]; then
        log_info "本地无测试镜像，跳过容器GPU测试（运行完整配置时将拉取ubuntu:22.04）"
        return 0
    fi

    if docker run --rm --gpus all "$test_image" nvidia-smi &>/dev/null; then
        log_pass "GPU容器测试: 容器内nvidia-smi成功"
        return 0
    else
        log_fail "GPU容器测试: 容器内无法访问GPU"
        return 1
    fi
}

check_wsl_conf() {
    if [ ! -f "$WSL_CONF" ]; then
        log_warn "wsl.conf不存在"
        return 1
    fi
    if grep -q '^\[boot\]' "$WSL_CONF" && grep -q 'containerd' "$WSL_CONF" && grep -q 'dockerd' "$WSL_CONF"; then
        log_pass "wsl.conf: [boot]段已配置Docker自启"
        return 0
    else
        log_warn "wsl.conf: [boot]段未正确配置Docker自启"
        return 1
    fi
}

# ============================================================
# 安装配置函数
# ============================================================

install_prereqs() {
    log_step "安装前置依赖"
    apt-get update -qq
    apt-get install -y --no-install-recommends ca-certificates curl gnupg2 >/dev/null 2>&1
    log_pass "前置依赖就绪"
}

setup_nvidia_repo() {
    log_step "配置NVIDIA apt源"

    if [ -f "$NVIDIA_SOURCE_LIST" ] && grep -q 'libnvidia-container' "$NVIDIA_SOURCE_LIST" && ! grep -q '\$(ARCH)' "$NVIDIA_SOURCE_LIST"; then
        log_pass "NVIDIA apt源已配置（跳过）"
        return 0
    fi

    local base_url
    case "$MIRROR" in
        ustc)  base_url="https://mirrors.ustc.edu.cn/libnvidia-container" ;;
        official) base_url="https://nvidia.github.io/libnvidia-container" ;;
        *) log_fail "未知镜像源: $MIRROR"; return 1 ;;
    esac

    # 添加GPG key
    if [ ! -f "$NVIDIA_KEYRING" ]; then
        curl -fsSL "${base_url}/gpgkey" | gpg --dearmor -o "$NVIDIA_KEYRING"
        log_info "GPG key已添加"
    fi

    # 直接写入源文件（不依赖$(ARCH)展开）
    cat > "$NVIDIA_SOURCE_LIST" <<EOF
deb [signed-by=${NVIDIA_KEYRING}] ${base_url}/stable/deb/${ARCH} /
#deb [signed-by=${NVIDIA_KEYRING}] ${base_url}/experimental/deb/${ARCH} /
EOF

    log_pass "NVIDIA apt源已配置（使用${MIRROR}镜像，架构${ARCH}）"
}

install_toolkit() {
    log_step "安装nvidia-container-toolkit"

    if check_l2_toolkit; then
        return 0
    fi

    apt-get update -qq
    apt-get install -y nvidia-container-toolkit

    if check_l2_toolkit; then
        log_pass "nvidia-container-toolkit安装成功"
    else
        log_fail "nvidia-container-toolkit安装失败"
        return 1
    fi
}

configure_docker_runtime() {
    log_step "配置Docker nvidia runtime"

    if check_l3_runtime; then
        return 0
    fi

    # 确保/etc/docker目录存在
    mkdir -p /etc/docker

    backup_file "$DOCKER_DAEMON_JSON"
    nvidia-ctk runtime configure --runtime=docker

    if check_l3_runtime; then
        log_pass "Docker nvidia runtime配置完成"
    else
        log_fail "Docker nvidia runtime配置失败"
        return 1
    fi
}

configure_wsl_boot() {
    log_step "配置wsl.conf [boot] Docker自启"

    if check_wsl_conf && [ -f "$WSL_CONF" ]; then
        # 检查是否需要更新boot命令
        if grep -q 'containerd.*dockerd' "$WSL_CONF"; then
            log_pass "wsl.conf [boot]已正确配置（跳过）"
            return 0
        fi
    fi

    backup_file "$WSL_CONF"

    local boot_cmd='command="nohup containerd > /var/log/containerd-boot.log 2>&1 & sleep 2; nohup dockerd > /var/log/dockerd-boot.log 2>&1"'

    if [ ! -f "$WSL_CONF" ]; then
        cat > "$WSL_CONF" <<WSL_EOF
[network]
generateResolvConf = false

[boot]
${boot_cmd}

[automount]
enabled = true
options = "metadata,umask=0022,fmask=0011"
mountFsTab = true
WSL_EOF
    else
        # 备份原有内容，移除已有的[boot]段（如果存在），添加新配置
        local tmp_conf=$(mktemp)
        local in_boot=false
        while IFS= read -r line; do
            if [[ "$line" =~ ^\[boot\] ]]; then
                in_boot=true
                continue
            fi
            if $in_boot && [[ "$line" =~ ^\[ ]]; then
                in_boot=false
            fi
            if ! $in_boot; then
                echo "$line" >> "$tmp_conf"
            fi
        done < "$WSL_CONF"

        # 追加[boot]段
        cat >> "$tmp_conf" <<WSL_EOF

[boot]
${boot_cmd}
WSL_EOF

        # 确保有[automount]段
        if ! grep -q '^\[automount\]' "$tmp_conf"; then
            cat >> "$tmp_conf" <<'WSL_EOF'

[automount]
enabled = true
options = "metadata,umask=0022,fmask=0011"
mountFsTab = true
WSL_EOF
        fi

        mv "$tmp_conf" "$WSL_CONF"
    fi

    if check_wsl_conf; then
        log_pass "wsl.conf [boot]配置完成"
        log_info "注意：需要在Windows PowerShell执行 wsl --shutdown 使[boot]配置生效"
    else
        log_fail "wsl.conf配置失败"
        return 1
    fi
}

start_docker() {
    log_step "启动Docker守护进程"

    # 如果已在运行，不需要启动
    if docker info &>/dev/null; then
        log_pass "Docker已在运行"
        return 0
    fi

    # 先启动containerd
    if ! pgrep -x containerd &>/dev/null; then
        setsid containerd > /var/log/containerd.log 2>&1 < /dev/null &
        sleep 2
        log_info "containerd已启动"
    fi

    # 启动dockerd
    setsid dockerd > /var/log/dockerd.log 2>&1 < /dev/null &

    # 等待就绪
    local waited=0
    while [ $waited -lt 20 ]; do
        if docker info &>/dev/null; then
            log_pass "Docker启动成功"
            return 0
        fi
        sleep 1
        waited=$((waited + 1))
    done

    log_fail "Docker启动超时，请检查日志: /var/log/dockerd.log"
    log_info "最近日志:"
    tail -20 /var/log/dockerd.log 2>/dev/null || true
    return 1
}

pull_test_image_and_verify() {
    log_step "端到端GPU容器验证"

    if ! docker images ubuntu:22.04 --format '{{.Repository}}:{{.Tag}}' 2>/dev/null | grep -q 'ubuntu:22.04'; then
        log_info "拉取ubuntu:22.04测试镜像..."
        docker pull ubuntu:22.04 --quiet || {
            log_warn "镜像拉取失败（可能网络问题），跳过容器测试"
            return 0
        }
    fi

    if docker run --rm --gpus all ubuntu:22.04 nvidia-smi &>/dev/null; then
        log_pass "端到端验证通过: 容器内GPU访问正常"
        docker run --rm --gpus all ubuntu:22.04 nvidia-smi 2>&1 | head -10
        return 0
    else
        log_fail "端到端验证失败: 容器内无法访问GPU"
        return 1
    fi
}

# ============================================================
# 排查指南
# ============================================================

show_troubleshooting() {
    cat <<'TS_GUIDE'

==================== 快速排查指南 ====================

如果重启WSL后Docker没有自动启动，按以下顺序排查：

1. 检查wsl.conf语法
   $ cat /etc/wsl.conf
   → 确认有[boot]段且command行正确（无引号转义错误）
   → 如果编辑过wsl.conf，必须执行 wsl --shutdown 才生效

2. 检查boot日志
   $ cat /var/log/dockerd-boot.log
   $ cat /var/log/containerd-boot.log
   → 查看启动命令的输出和错误

3. 检查daemon.json合法性
   $ python3 -m json.tool /etc/docker/daemon.json > /dev/null && echo "JSON valid" || echo "JSON invalid!"
   → JSON格式错误会导致dockerd启动失败

4. 手动启动Docker看错误输出
   $ sudo setsid containerd > /tmp/c.log 2>&1 < /dev/null &
   $ sleep 2; sudo setsid dockerd > /tmp/d.log 2>&1 < /dev/null &
   $ sleep 3; cat /tmp/d.log

5. 检查apt源是否有效
   $ sudo apt update
   $ apt-cache policy nvidia-container-toolkit
   → 如果找不到包，检查源文件中$(ARCH)是否已展开为amd64

6. 检查是否启用了systemd（影响启动方式）
   $ ps -p 1 -o comm=
   → 输出 systemd: 用 sudo systemctl start docker
   → 输出 init: 用 setsid 方式启动（本脚本的方式）

7. 确认执行了 wsl --shutdown（不是关闭终端再打开）
   → 关闭WSL终端窗口不会停止WSL虚拟机
   → 必须在PowerShell中执行 wsl --shutdown 才会真正重启

重新执行本脚本可自动修复大部分问题（幂等安全）：
   $ sudo bash setup-wsl-docker-gpu.sh

======================================================
TS_GUIDE
}

# ============================================================
# 主流程
# ============================================================

echo "============================================"
echo " WSL2 Docker GPU 配置脚本"
echo "============================================"
echo " 镜像源: ${MIRROR}"
echo " 模式: $(if $ONLY_VERIFY; then echo '仅验证'; else echo '完整配置'; fi)"
echo " 架构: ${ARCH}"
echo " 发行版: ${UBUNTU_CODENAME}"
echo "============================================"

check_root

# 验证模式
if $ONLY_VERIFY; then
    log_step "诊断模式"
    echo ""
    l1=0; l2=0; l3=0; gc=0; wc=0
    check_l1_driver && l1=1 || true
    check_l2_toolkit && l2=1 || true
    check_l3_runtime && l3=1 || true
    if [ $l3 -eq 1 ]; then check_gpu_container && gc=1 || true; fi
    check_wsl_conf && wc=1 || true

    echo ""
    echo "============================================"
    echo -e " L1驱动层:     $( [ $l1 -eq 1 ] && echo -e ${GREEN}PASS${NC} || echo -e ${RED}FAIL${NC} )"
    echo -e " L2工具层:     $( [ $l2 -eq 1 ] && echo -e ${GREEN}PASS${NC} || echo -e ${RED}FAIL${NC} )"
    echo -e " L3运行时层:   $( [ $l3 -eq 1 ] && echo -e ${GREEN}PASS${NC} || echo -e ${RED}FAIL${NC} )"
    echo -e " wsl.conf:     $( [ $wc -eq 1 ] && echo -e ${GREEN}OK${NC} || echo -e ${YELLOW}NOT CONFIGURED${NC} )"
    echo "============================================"

    if [ $l1 -eq 1 ] && [ $l2 -eq 1 ] && [ $l3 -eq 1 ]; then
        echo ""
        echo -e "${GREEN}🎉 核心功能正常！${NC}"
        if [ $wc -eq 0 ]; then
            echo -e "${YELLOW}⚠ wsl.conf [boot]未配置，WSL重启后Docker不会自动启动${NC}"
            echo "  运行 sudo bash $0 完成完整配置"
        fi
    else
        show_troubleshooting
        exit 1
    fi
    exit 0
fi

# 完整配置模式
log_step "Step 0: 三层预诊断"
echo ""
l1_pre=true; l2_pre=true; l3_pre=true
check_l1_driver || l1_pre=false
check_l2_toolkit || l2_pre=false
check_l3_runtime || l3_pre=false

if $l1_pre && $l2_pre && $l3_pre && check_wsl_conf; then
    echo ""
    log_pass "所有配置已就绪！"
    check_gpu_container || true
    exit 0
fi

# 按需执行安装配置步骤
if ! $l1_pre; then
    log_fail "L1驱动层未就绪，请先修复NVIDIA驱动"
    log_info "nvidia-smi不可用时无法继续配置，请确认WSL2 GPU透传正常"
    exit 1
fi

if ! $l2_pre; then
    install_prereqs
    setup_nvidia_repo
    install_toolkit
fi

configure_docker_runtime
configure_wsl_boot
start_docker
pull_test_image_and_verify

# 最终汇总
echo ""
echo "============================================"
echo " 配置完成！"
echo "============================================"
echo ""
log_pass "L1 驱动层:     正常"
log_pass "L2 工具层:     已安装nvidia-container-toolkit"
log_pass "L3 运行时层:   Docker nvidia runtime已注册"
log_pass "wsl.conf:      [boot]段已配置Docker自启"
echo ""
echo -e "${YELLOW}⚠ 重要提醒：${NC}"
echo "  1. 在Windows PowerShell中执行: wsl --shutdown"
echo "  2. 重新打开WSL，Docker将自动启动"
echo "  3. 验证: bash $0 --verify"
echo "     或在PowerShell运行: Restart-WslDockerGpu.ps1"
echo ""
echo "如果重启后Docker未自动启动，运行:"
echo "  bash $0 --verify  查看诊断结果"
echo ""
