#!/bin/bash
#
# devcontainer-base healthcheck script
# Checks SSH, Docker (DinD/DooD), Podman (rootless), and Jupyter services conditionally.
#
# Timeout budget (HEALTHCHECK --timeout=10s, reserve 1s overhead → 9s for probes):
#   SSH:    pgrep instant + TCP probe 2s
#   Docker: socket checks instant + docker ps 3s + docker info 2s (cosmetic, skipped if ps fails)
#   Podman: binary check instant + podman ps 3s (rootless via su -)
#   Jupyter: pgrep instant + curl --max-time 2s
#   Worst case (all functional probes hang simultaneously): 2+3+3+2 = 10s (edge case = system failure)
#
# Design principle: functional probe > existence check.
#   Process/socket existence alone is insufficient (process may be hung/zombie).
#   Each service runs a minimal command that proves the daemon/runtime can respond.
#
# Note: This script requires executable permission. In Dockerfile, use:
#   COPY --chmod=755 scripts/healthcheck.sh /usr/local/bin/healthcheck.sh
# or COPY with --chmod=+x (BuildKit required)

ENABLE_SSH="${ENABLE_SSH:-yes}"
ENABLE_DOCKER="${ENABLE_DOCKER:-yes}"
ENABLE_PODMAN="${ENABLE_PODMAN:-no}"
ENABLE_JUPYTER="${ENABLE_JUPYTER:-yes}"
SSH_PORT="${SSH_PORT:-22}"
JUPYTER_PORT="${JUPYTER_PORT:-8888}"
PODMAN_USER="${NON_ROOT_USER:-devuser}"
# Pre-resolve PODMAN_UID for XDG_RUNTIME_DIR (used by rootless podman)
PODMAN_UID=$(id -u "${PODMAN_USER}" 2>/dev/null || echo "1000")
FAIL=0
SERVICES_ENABLED=0

check_ssh() {
    if ! pgrep -x sshd >/dev/null 2>&1; then
        echo "[HEALTHCHECK] sshd port ${SSH_PORT}: FAILED (process not running)"
        FAIL=1
        return
    fi

    if timeout 2 bash -c "exec 3<>/dev/tcp/127.0.0.1/${SSH_PORT} && exec 3>&-" 2>/dev/null; then
        echo "[HEALTHCHECK] sshd port ${SSH_PORT}: OK"
    else
        echo "[HEALTHCHECK] sshd port ${SSH_PORT}: FAILED"
        FAIL=1
    fi
}

check_docker() {
    DOCKER_MODE="dood"
    DOCKER_SOCK="/var/run/docker.sock"

    # Detect DinD vs DooD: dockerd running inside container → DinD; socket mounted from host → DooD
    if pgrep -x dockerd >/dev/null 2>&1; then
        DOCKER_MODE="dind"
    fi

    if [ ! -S "${DOCKER_SOCK}" ]; then
        echo "[HEALTHCHECK] docker (${DOCKER_MODE}) ${DOCKER_SOCK}: FAILED (socket not found)"
        FAIL=1
        return
    fi

    if [ ! -r "${DOCKER_SOCK}" ] || [ ! -w "${DOCKER_SOCK}" ]; then
        echo "[HEALTHCHECK] docker (${DOCKER_MODE}) ${DOCKER_SOCK}: FAILED (socket not accessible)"
        FAIL=1
        return
    fi

    # 最小功能探测：docker ps 能正常返回即证明 daemon 可响应请求，而非仅检查 socket/进程存在
    if ! timeout 3 docker ps >/dev/null 2>&1; then
        echo "[HEALTHCHECK] docker (${DOCKER_MODE}) ${DOCKER_SOCK}: FAILED (docker ps failed)"
        FAIL=1
        return
    fi

    # 附带版本信息（可选展示，失败不判定为不健康——ps 已证明 daemon 可响应）
    DOCKER_VERSION=$(timeout 2 docker info --format '{{.ServerVersion}}' 2>/dev/null)
    echo "[HEALTHCHECK] docker (${DOCKER_MODE}) ${DOCKER_SOCK}: OK${DOCKER_VERSION:+ (version ${DOCKER_VERSION})}"
}

check_podman() {
    # Rootless Podman：以非 root 用户（默认 devuser）按需运行，无常驻 daemon。
    # 用 podman ps 作为最小功能探测，验证 rootless 运行时可用，而非仅检查二进制存在。
    # 显式设置 XDG_RUNTIME_DIR 以确保 rootless podman 能找到运行时目录（容器内无 systemd-logind）。
    if ! command -v podman >/dev/null 2>&1; then
        echo "[HEALTHCHECK] podman (rootless) as ${PODMAN_USER}: FAILED (binary not found)"
        FAIL=1
        return
    fi

    if timeout 3 su - "${PODMAN_USER}" -c "XDG_RUNTIME_DIR=/run/user/${PODMAN_UID} podman ps >/dev/null 2>&1"; then
        echo "[HEALTHCHECK] podman (rootless) as ${PODMAN_USER}: OK"
    else
        echo "[HEALTHCHECK] podman (rootless) as ${PODMAN_USER}: FAILED (podman ps failed)"
        FAIL=1
    fi
}

check_jupyter() {
    if ! pgrep -f "jupyter" >/dev/null 2>&1; then
        echo "[HEALTHCHECK] jupyter port ${JUPYTER_PORT}: FAILED (process not running)"
        FAIL=1
        return
    fi

    # --max-time 2: HTTP API must respond within 2s (localhost should be near-instant)
    HTTP_CODE=$(curl -s --max-time 2 -o /dev/null -w "%{http_code}" "http://127.0.0.1:${JUPYTER_PORT}/api" 2>/dev/null || echo "000")
    if [ "$HTTP_CODE" = "200" ] || [ "$HTTP_CODE" = "302" ] || [ "$HTTP_CODE" = "401" ] || [ "$HTTP_CODE" = "403" ]; then
        echo "[HEALTHCHECK] jupyter port ${JUPYTER_PORT}: OK (HTTP ${HTTP_CODE})"
    else
        echo "[HEALTHCHECK] jupyter port ${JUPYTER_PORT}: FAILED (HTTP ${HTTP_CODE})"
        FAIL=1
    fi
}

if [ "$ENABLE_SSH" = "yes" ]; then
    SERVICES_ENABLED=1
    check_ssh
fi

if [ "$ENABLE_DOCKER" = "yes" ]; then
    SERVICES_ENABLED=1
    check_docker
fi

if [ "$ENABLE_PODMAN" = "yes" ]; then
    SERVICES_ENABLED=1
    check_podman
fi

if [ "$ENABLE_JUPYTER" = "yes" ]; then
    SERVICES_ENABLED=1
    check_jupyter
fi

if [ "$SERVICES_ENABLED" -eq 0 ]; then
    echo "[HEALTHCHECK] STATUS: HEALTHY (no services enabled - command mode)"
    exit 0
fi

if [ "$FAIL" -eq 1 ]; then
    echo "[HEALTHCHECK] STATUS: UNHEALTHY"
    exit 1
fi

echo "[HEALTHCHECK] STATUS: HEALTHY"
exit 0
