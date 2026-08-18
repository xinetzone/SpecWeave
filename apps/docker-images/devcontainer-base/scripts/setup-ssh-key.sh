#!/bin/bash
# =============================================================================
# SSH 免密登录配置脚本
# =============================================================================
# 自动将宿主机 SSH 公钥注入到 devcontainer 容器，实现从宿主机无缝 SSH 进入容器。
#
# 安全原则（基于经验教训）:
#   - 不生成/分发私钥，私钥仅保留在宿主机
#   - 只在容器侧配置 authorized_keys + 权限
#   - 支持两种模式：运行时注入（立即生效）和 .env 持久化（重启后生效）
#
# 用法:
#   bash scripts/setup-ssh-key.sh              # 自动检测公钥→注入运行中容器+写入.env
#   bash scripts/setup-ssh-key.sh --no-env     # 仅注入运行中容器，不写.env
#   bash scripts/setup-ssh-key.sh --env-only   # 仅写入.env，不注入运行中容器
#   bash scripts/setup-ssh-key.sh -k ~/.ssh/id_ed25519.pub  # 指定公钥文件
#
# 配置后可直接:
#   ssh devuser@localhost -p 2222   # 无需密码
# =============================================================================

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
ENV_FILE="$PROJECT_DIR/.env.dev"
COMPOSE_FILE="$PROJECT_DIR/docker-compose.dev.yml"
CONTAINER_NAME="${CONTAINER_NAME:-devcontainer-dev}"
SSH_USER="devuser"
SSH_PORT="${SSH_PORT:-2222}"

# 颜色
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'

info()  { echo -e "${CYAN}[INFO]${NC} $*"; }
ok()    { echo -e "${GREEN}[OK]${NC} $*"; }
warn()  { echo -e "${YELLOW}[WARN]${NC} $*"; }
error() { echo -e "${RED}[ERROR]${NC} $*" >&2; }

# 解析参数
INJECT_RUNNING=true
WRITE_ENV=true
PUB_KEY_FILE=""

while [[ $# -gt 0 ]]; do
    case "$1" in
        --no-env)    WRITE_ENV=false; shift ;;
        --env-only)  INJECT_RUNNING=false; shift ;;
        -k|--key)    PUB_KEY_FILE="$2"; shift 2 ;;
        -h|--help)
            echo "Usage: $0 [--no-env] [--env-only] [-k <pubkey-file>]"
            echo ""
            echo "  --no-env     Don't write to .env.dev (runtime injection only)"
            echo "  --env-only   Only write to .env.dev (no running container injection)"
            echo "  -k FILE      Specify public key file (default: auto-detect from ~/.ssh/)"
            exit 0 ;;
        *) error "Unknown option: $1"; exit 1 ;;
    esac
done

# ── 函数: 在WSL/Linux/macOS中检测Docker可用 ────────────────────────────────
find_docker_cmd() {
    if command -v docker &>/dev/null; then
        echo "docker"
    elif command -v wsl.exe &>/dev/null; then
        echo "wsl.exe docker"
    else
        echo ""
    fi
}

# 检测环境: Windows (通过WSL运行Docker) 还是 原生Linux
detect_os() {
    if [[ "$(uname -s)" == "Linux"* ]]; then
        if grep -qi microsoft /proc/version 2>/dev/null; then
            echo "wsl"
        else
            echo "linux"
        fi
    elif [[ "$(uname -s)" == "Darwin" ]]; then
        echo "macos"
    else
        echo "windows"
    fi
}

# ── 步骤1: 查找宿主机公钥 ──────────────────────────────────────────────────
find_pub_key() {
    local found_keys=()

    if [[ -n "$PUB_KEY_FILE" ]]; then
        if [[ -f "$PUB_KEY_FILE" ]]; then
            echo "$PUB_KEY_FILE"
            return 0
        else
            error "Specified public key file not found: $PUB_KEY_FILE"
            exit 1
        fi
    fi

    # 自动搜索 ~/.ssh/ 下的公钥文件
    local ssh_dir="$HOME/.ssh"
    for keytype in id_ed25519 id_rsa id_ecdsa id_ed25519_sk; do
        if [[ -f "$ssh_dir/${keytype}.pub" ]]; then
            found_keys+=("$ssh_dir/${keytype}.pub")
        fi
    done

    if [[ ${#found_keys[@]} -eq 0 ]]; then
        error "No SSH public key found in ~/.ssh/"
        echo ""
        echo "  Generate one first:"
        echo "    ssh-keygen -t ed25519 -C 'your@email.com'"
        echo ""
        exit 1
    fi

    if [[ ${#found_keys[@]} -eq 1 ]]; then
        echo "${found_keys[0]}"
        return 0
    fi

    # 多个公钥，让用户选择
    echo ""
    info "Multiple public keys found:"
    for i in "${!found_keys[@]}"; do
        local key_comment
        key_comment=$(awk '{print $NF}' "${found_keys[$i]}" 2>/dev/null || echo "(no comment)")
        echo "  [$i] ${found_keys[$i]}  ($key_comment)"
    done
    echo ""
    read -p "Select key [0-$((${#found_keys[@]}-1))] (default: 0): " choice
    choice="${choice:-0}"
    echo "${found_keys[$choice]}"
}

# ── 步骤2: 读取公钥内容 ────────────────────────────────────────────────────
read_pub_key() {
    local key_file="$1"
    if [[ ! -f "$key_file" ]]; then
        error "Public key file not found: $key_file"
        exit 1
    fi
    cat "$key_file"
}

# ── 步骤3: 注入到运行中容器（docker exec） ────────────────────────────────
inject_to_running_container() {
    local pub_key="$1"
    local docker_cmd

    local os_type
    os_type=$(detect_os)

    if [[ "$os_type" == "windows" ]]; then
        # Windows原生: 通过WSL执行docker命令
        docker_cmd="wsl -d Ubuntu-26.04 -e docker"
    else
        docker_cmd="docker"
    fi

    info "Checking container '$CONTAINER_NAME'..."
    local container_status
    container_status=$($docker_cmd inspect -f '{{.State.Status}}' "$CONTAINER_NAME" 2>/dev/null || echo "not_found")

    if [[ "$container_status" != "running" ]]; then
        warn "Container '$CONTAINER_NAME' is not running (status: $container_status)"
        info "Key will be configured on next container start (via .env.dev)"
        return 1
    fi

    info "Container is running, injecting SSH public key..."

    # 写入authorized_keys并修复权限（遵循经验587366: 目录700, 文件600）
    # 使用单引号包裹pub_key避免shell解释特殊字符
    $docker_cmd exec "$CONTAINER_NAME" bash -c "
        mkdir -p /home/$SSH_USER/.ssh && \
        chmod 700 /home/$SSH_USER/.ssh && \
        touch /home/$SSH_USER/.ssh/authorized_keys && \
        # 避免重复添加同一把公钥
        if ! grep -qF '$pub_key' /home/$SSH_USER/.ssh/authorized_keys 2>/dev/null; then
            echo '$pub_key' >> /home/$SSH_USER/.ssh/authorized_keys && \
            echo '[Key added]'
        else
            echo '[Key already exists]'
        fi && \
        chmod 600 /home/$SSH_USER/.ssh/authorized_keys && \
        chown -R $SSH_USER:$SSH_USER /home/$SSH_USER/.ssh && \
        echo '[Permissions fixed: .ssh=700, authorized_keys=600]'
    "

    ok "Public key injected into running container"
    return 0
}

# ── 步骤4: 写入.env.dev（持久化配置，重启后生效） ─────────────────────────
write_to_env() {
    local pub_key="$1"

    if [[ ! -f "$ENV_FILE" ]]; then
        if [[ -f "$PROJECT_DIR/.env.dev.example" ]]; then
            cp "$PROJECT_DIR/.env.dev.example" "$ENV_FILE"
            info "Created .env.dev from template"
        else
            touch "$ENV_FILE"
        fi
    fi

    # 检查SSH_PUBLIC_KEY是否已存在
    if grep -q "^SSH_PUBLIC_KEY=" "$ENV_FILE" 2>/dev/null; then
        # 更新已有值
        # 使用awk安全替换（处理公钥中的特殊字符）
        local escaped_key
        escaped_key=$(printf '%s\n' "$pub_key" | sed 's/[\/&]/\\&/g')
        # 直接sed替换更简单
        sed -i "s|^SSH_PUBLIC_KEY=.*|SSH_PUBLIC_KEY=$escaped_key|" "$ENV_FILE"
        ok "Updated SSH_PUBLIC_KEY in .env.dev"
    else
        # 添加新行
        echo "SSH_PUBLIC_KEY=$pub_key" >> "$ENV_FILE"
        ok "Added SSH_PUBLIC_KEY to .env.dev"
    fi
}

# ── 步骤5: 配置本地 SSH config（可选，方便连接） ──────────────────────────
setup_ssh_config() {
    local ssh_config="$HOME/.ssh/config"
    local host_alias="devcontainer"

    echo ""
    read -p "Add SSH config alias 'devcontainer' to ~/.ssh/config for easy access? [Y/n] " -n 1 -r
    echo ""
    if [[ ! $REPLY =~ ^[Nn]$ ]]; then
        # 检查是否已存在
        if grep -q "Host $host_alias" "$ssh_config" 2>/dev/null; then
            warn "Host '$host_alias' already exists in ~/.ssh/config, skipping"
            return
        fi

        mkdir -p "$(dirname "$ssh_config")"
        cat >> "$ssh_config" << EOF

Host $host_alias
    HostName localhost
    Port $SSH_PORT
    User $SSH_USER
    StrictHostKeyChecking no
    UserKnownHostsFile /dev/null

EOF
        ok "SSH config alias 'devcontainer' added"
        info "Now you can connect with: ssh $host_alias"
    fi
}

# ── 主流程 ─────────────────────────────────────────────────────────────────
main() {
    echo ""
    echo -e "${CYAN}╔══════════════════════════════════════════════╗${NC}"
    echo -e "${CYAN}║   SSH Key Setup for devcontainer             ║${NC}"
    echo -e "${CYAN}╚══════════════════════════════════════════════╝${NC}"
    echo ""

    # 1. 查找公钥
    local pub_key_file
    pub_key_file=$(find_pub_key)
    info "Using public key: $pub_key_file"

    # 2. 读取公钥内容
    local pub_key
    pub_key=$(read_pub_key "$pub_key_file")
    local key_fingerprint
    key_fingerprint=$(ssh-keygen -lf "$pub_key_file" 2>/dev/null | awk '{print $2}' || echo "?")
    info "Key fingerprint: $key_fingerprint"

    # 3. 注入运行中容器
    if $INJECT_RUNNING; then
        echo ""
        inject_to_running_container "$pub_key" || true
    fi

    # 4. 写入.env.dev
    if $WRITE_ENV; then
        echo ""
        write_to_env "$pub_key"
    fi

    # 5. SSH config alias（可选）
    setup_ssh_config

    # 6. 测试连接
    echo ""
    info "Testing SSH connection..."
    local os_type
    os_type=$(detect_os)
    local ssh_cmd="ssh"

    if [[ "$os_type" == "windows" ]] && command -v ssh.exe &>/dev/null; then
        ssh_cmd="ssh.exe"
    fi

    if $ssh_cmd -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null \
               -o ConnectTimeout=5 -o BatchMode=yes \
               -p "$SSH_PORT" "$SSH_USER@localhost" "echo 'SSH connection successful!'" 2>/dev/null; then
        ok "SSH passwordless login is working! 🎉"
    else
        warn "Immediate test failed (container may need a moment to reload)"
        info "Try: ssh $SSH_USER@localhost -p $SSH_PORT"
    fi

    echo ""
    echo -e "${GREEN}╔══════════════════════════════════════════════╗${NC}"
    echo -e "${GREEN}║   SSH Key Setup Complete                     ║${NC}"
    echo -e "${GREEN}╚══════════════════════════════════════════════╝${NC}"
    echo ""
    echo "  Connect with:"
    echo "    ssh $SSH_USER@localhost -p $SSH_PORT"
    echo "    ssh devcontainer   (if you added the config alias)"
    echo ""
}

main "$@"
