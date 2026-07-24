#!/bin/bash
# =============================================================================
# SSH 非交互会话 PATH 集成测试
# =============================================================================
# 验证 SSH 非交互会话能否正确继承 Dockerfile ENV 中设置的 PATH，
# 确保 `ssh user@host 'which jupyter'` 等远程命令可找到 venv 中的可执行文件。
#
# 背景：Dockerfile 中 ENV PATH 仅对登录 shell 生效，SSH 非交互会话
# 不执行 .bashrc/.profile，需要 /etc/environment 配合 PAM 才能生效。
# 本测试验证三层配置（ENV + /etc/environment + /etc/profile.d）的正确性。
#
# 用法：
#   bash scripts/test-ssh-noninteractive-path.sh              # 完整测试（构建+运行+验证+清理）
#   bash scripts/test-ssh-noninteractive-path.sh --skip-build # 跳过构建（使用已有镜像）
#   bash scripts/test-ssh-noninteractive-path.sh --keep       # 测试后保留容器（调试用）
# =============================================================================

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
IMAGE_NAME="${IMAGE_NAME:-jupyter-ssh-base}"
IMAGE_TAG="${IMAGE_TAG:-test-ssh-path}"
CONTAINER_NAME="test-ssh-path-$$"
SSH_PORT="${SSH_PORT:-2222}"
SKIP_BUILD=false
KEEP_CONTAINER=false
PASS=0
FAIL=0

# ---- 颜色输出 ----
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

pass() { echo -e "  ${GREEN}[PASS]${NC} $*"; ((PASS++)) || true; }
fail() { echo -e "  ${RED}[FAIL]${NC} $*"; ((FAIL++)) || true; }
info() { echo -e "  ${YELLOW}[INFO]${NC} $*"; }

# ---- 参数解析 ----
while [[ $# -gt 0 ]]; do
    case "$1" in
        --skip-build) SKIP_BUILD=true; shift ;;
        --keep) KEEP_CONTAINER=true; shift ;;
        *) echo "Unknown option: $1"; exit 1 ;;
    esac
done

# ---- 清理函数 ----
cleanup() {
    if [ "$KEEP_CONTAINER" = false ]; then
        info "Cleaning up container: ${CONTAINER_NAME}"
        docker rm -f "${CONTAINER_NAME}" 2>/dev/null || true
    else
        info "Container kept for debugging: ${CONTAINER_NAME}"
        echo "  docker exec -it ${CONTAINER_NAME} bash"
        echo "  docker rm -f ${CONTAINER_NAME}  # when done"
    fi
}
trap cleanup EXIT

# ---- 构建镜像 ----
if [ "$SKIP_BUILD" = false ]; then
    echo ""
    echo "============================================"
    echo " Step 1: Build Docker image"
    echo "============================================"
    cd "$PROJECT_DIR"
    DOCKER_BUILDKIT=1 docker build -t "${IMAGE_NAME}:${IMAGE_TAG}" . || {
        fail "Docker build failed"
        exit 1
    }
    pass "Docker image built: ${IMAGE_NAME}:${IMAGE_TAG}"
else
    info "Skipping build, using existing image: ${IMAGE_NAME}:${IMAGE_TAG}"
fi

# ---- 启动容器 ----
echo ""
echo "============================================"
echo " Step 2: Start container"
echo "============================================"

USER_PASSWORD="test-pass-$(date +%s)"
docker run -d \
    --name "${CONTAINER_NAME}" \
    -p "${SSH_PORT}:22" \
    -e USER_PASSWORD="${USER_PASSWORD}" \
    -e JUPYTER_TOKEN=test-token \
    -e GRANT_SUDO=no \
    "${IMAGE_NAME}:${IMAGE_TAG}" || {
    fail "Failed to start container"
    exit 1
}
pass "Container started: ${CONTAINER_NAME}"

# ---- 等待服务就绪 ----
echo ""
echo "============================================"
echo " Step 3: Wait for services to be ready"
echo "============================================"

info "Waiting for SSH service to be ready..."
MAX_WAIT=30
WAITED=0
while [ $WAITED -lt $MAX_WAIT ]; do
    if docker exec "${CONTAINER_NAME}" pgrep -x sshd >/dev/null 2>&1; then
        pass "SSH service is running (waited ${WAITED}s)"
        break
    fi
    sleep 2
    WAITED=$((WAITED + 2))
done
if [ $WAITED -ge $MAX_WAIT ]; then
    fail "SSH service did not start within ${MAX_WAIT}s"
    docker logs "${CONTAINER_NAME}" | tail -20
    exit 1
fi

# ---- 安装 sshpass（用于非交互 SSH 密码认证） ----
if ! command -v sshpass &>/dev/null; then
    info "sshpass not found, attempting to install..."
    if command -v apt-get &>/dev/null; then
        sudo apt-get update -qq && sudo apt-get install -y -qq sshpass 2>/dev/null || {
            info "Cannot install sshpass (no sudo/apt), skipping SSH non-interactive tests"
            info "Tests requiring SSH will be skipped"
            SSH_AVAILABLE=false
        }
    else
        info "sshpass not available, skipping SSH non-interactive tests"
        SSH_AVAILABLE=false
    fi
else
    SSH_AVAILABLE=true
fi

# ---- 配置 SSH 免 Known Hosts 提示 ----
SSH_OPTS="-o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o LogLevel=ERROR -p ${SSH_PORT}"

# ---- 测试 SSH 非交互 PATH ----
echo ""
echo "============================================"
echo " Step 4: SSH non-interactive PATH tests"
echo "============================================"

if [ "${SSH_AVAILABLE:-false}" = true ]; then
    # Test 1: which jupyter (关键测试 — 验证 /etc/environment PATH)
    echo ""
    echo "--- Test 4.1: which jupyter (non-interactive SSH) ---"
    JUPYTER_PATH=$(sshpass -p "${USER_PASSWORD}" ssh ${SSH_OPTS} jupyteruser@127.0.0.1 'which jupyter' 2>/dev/null || echo "NOT_FOUND")
    if [ "$JUPYTER_PATH" != "NOT_FOUND" ] && [ -n "$JUPYTER_PATH" ]; then
        pass "which jupyter = ${JUPYTER_PATH}"
    else
        fail "which jupyter returned NOT_FOUND — SSH non-interactive PATH is broken!"
        info "Debug: checking /etc/environment in container..."
        docker exec "${CONTAINER_NAME}" cat /etc/environment
        info "Debug: checking PATH in non-interactive SSH..."
        sshpass -p "${USER_PASSWORD}" ssh ${SSH_OPTS} jupyteruser@127.0.0.1 'echo PATH=$PATH' 2>/dev/null || true
    fi

    # Test 2: which python3
    echo ""
    echo "--- Test 4.2: which python3 (non-interactive SSH) ---"
    PYTHON3_PATH=$(sshpass -p "${USER_PASSWORD}" ssh ${SSH_OPTS} jupyteruser@127.0.0.1 'which python3' 2>/dev/null || echo "NOT_FOUND")
    if [ "$PYTHON3_PATH" != "NOT_FOUND" ] && [ -n "$PYTHON3_PATH" ]; then
        pass "which python3 = ${PYTHON3_PATH}"
    else
        fail "which python3 returned NOT_FOUND"
    fi

    # Test 3: jupyter --version
    echo ""
    echo "--- Test 4.3: jupyter --version (non-interactive SSH) ---"
    JUPYTER_VERSION=$(sshpass -p "${USER_PASSWORD}" ssh ${SSH_OPTS} jupyteruser@127.0.0.1 'jupyter --version' 2>/dev/null || echo "FAILED")
    if [ "$JUPYTER_VERSION" != "FAILED" ] && [ -n "$JUPYTER_VERSION" ]; then
        pass "jupyter --version OK"
    else
        fail "jupyter --version failed in non-interactive SSH"
    fi

    # Test 4: pip --version
    echo ""
    echo "--- Test 4.4: pip --version (non-interactive SSH) ---"
    PIP_VERSION=$(sshpass -p "${USER_PASSWORD}" ssh ${SSH_OPTS} jupyteruser@127.0.0.1 'pip --version' 2>/dev/null || echo "FAILED")
    if [ "$PIP_VERSION" != "FAILED" ] && [ -n "$PIP_VERSION" ]; then
        pass "pip --version OK"
    else
        fail "pip --version failed in non-interactive SSH"
    fi

    # Test 5: Compare interactive vs non-interactive PATH
    echo ""
    echo "--- Test 4.5: Interactive vs non-interactive PATH comparison ---"
    INTERACTIVE_PATH=$(sshpass -p "${USER_PASSWORD}" ssh ${SSH_OPTS} -t jupyteruser@127.0.0.1 'echo $PATH' 2>/dev/null | tr -d '\r' || echo "FAILED")
    NONINTERACTIVE_PATH=$(sshpass -p "${USER_PASSWORD}" ssh ${SSH_OPTS} jupyteruser@127.0.0.1 'echo $PATH' 2>/dev/null | tr -d '\r' || echo "FAILED")
    if echo "$NONINTERACTIVE_PATH" | grep -q "/opt/venv/bin"; then
        pass "Non-interactive PATH contains /opt/venv/bin"
    else
        fail "Non-interactive PATH does NOT contain /opt/venv/bin"
        info "  Interactive PATH:   ${INTERACTIVE_PATH}"
        info "  Non-interactive PATH: ${NONINTERACTIVE_PATH}"
    fi
else
    info "Skipping SSH tests (sshpass not available)"
    info "To run SSH tests, install sshpass: sudo apt-get install sshpass"
fi

# ---- 测试 Jupyter HTTP（不需要 SSH） ----
echo ""
echo "============================================"
echo " Step 5: Jupyter HTTP health check"
echo "============================================"

# 等待 Jupyter 就绪
info "Waiting for Jupyter to be ready..."
MAX_WAIT=30
WAITED=0
JUPYTER_PORT=8888
while [ $WAITED -lt $MAX_WAIT ]; do
    HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" "http://127.0.0.1:${JUPYTER_PORT}/api" 2>/dev/null || echo "000")
    if [ "$HTTP_CODE" = "200" ] || [ "$HTTP_CODE" = "302" ] || [ "$HTTP_CODE" = "401" ] || [ "$HTTP_CODE" = "403" ]; then
        pass "Jupyter HTTP ${HTTP_CODE} (waited ${WAITED}s)"
        break
    fi
    sleep 2
    WAITED=$((WAITED + 2))
done
if [ $WAITED -ge $MAX_WAIT ]; then
    fail "Jupyter did not respond within ${MAX_WAIT}s (HTTP ${HTTP_CODE})"
fi

# ---- 测试 Docker HEALTHCHECK 机制 ----
echo ""
echo "============================================"
echo " Step 6: Docker HEALTHCHECK status"
echo "============================================"

# 等待 healthcheck 至少运行一次
info "Waiting for Docker healthcheck to run..."
sleep 10
HEALTH_STATUS=$(docker inspect --format='{{.State.Health.Status}}' "${CONTAINER_NAME}" 2>/dev/null || echo "unknown")
if [ "$HEALTH_STATUS" = "healthy" ]; then
    pass "Docker HEALTHCHECK status: healthy"
else
    info "Docker HEALTHCHECK status: ${HEALTH_STATUS} (may need more time)"
    # 再等 30 秒
    sleep 30
    HEALTH_STATUS=$(docker inspect --format='{{.State.Health.Status}}' "${CONTAINER_NAME}" 2>/dev/null || echo "unknown")
    if [ "$HEALTH_STATUS" = "healthy" ]; then
        pass "Docker HEALTHCHECK status: healthy (after additional wait)"
    else
        fail "Docker HEALTHCHECK status: ${HEALTH_STATUS} (expected: healthy)"
        docker inspect --format='{{json .State.Health}}' "${CONTAINER_NAME}" 2>/dev/null | python3 -m json.tool 2>/dev/null || true
    fi
fi

# ---- 测试容器内 healthcheck 脚本 ----
echo ""
echo "--- Test 6.1: Container healthcheck script ---"
if docker exec "${CONTAINER_NAME}" /usr/local/bin/healthcheck.sh; then
    pass "Container healthcheck.sh passed"
else
    fail "Container healthcheck.sh failed"
fi

# ---- 结果汇总 ----
echo ""
echo "============================================"
echo " Results Summary"
echo "============================================"
echo "  PASS: ${PASS}"
echo "  FAIL: ${FAIL}"
echo ""

if [ "$FAIL" -gt 0 ]; then
    echo -e "${RED}Some tests FAILED!${NC}"
    echo ""
    echo "Debug info:"
    echo "  Container logs:"
    docker logs "${CONTAINER_NAME}" | tail -30
    exit 1
else
    echo -e "${GREEN}All tests PASSED!${NC}"
    exit 0
fi