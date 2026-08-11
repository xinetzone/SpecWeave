#!/bin/bash
#
# devcontainer-base healthcheck script
# Checks SSH, Docker (DinD/DooD), and Jupyter services conditionally
#
# Note: This script requires executable permission. In Dockerfile, use:
#   COPY scripts/healthcheck.sh /usr/local/bin/
#   RUN chmod +x /usr/local/bin/healthcheck.sh
# or COPY with --chmod=+x (BuildKit required)

ENABLE_SSH="${ENABLE_SSH:-yes}"
ENABLE_DOCKER="${ENABLE_DOCKER:-yes}"
ENABLE_JUPYTER="${ENABLE_JUPYTER:-yes}"
SSH_PORT="${SSH_PORT:-22}"
JUPYTER_PORT="${JUPYTER_PORT:-8888}"
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
    DOCKER_MODE="socket"
    DOCKER_PORT_DESC="/var/run/docker.sock"

    if pgrep -x dockerd >/dev/null 2>&1 || pgrep -f containerd >/dev/null 2>&1; then
        DOCKER_MODE="dind"
        DOCKER_PORT_DESC="2375/socket"
    fi

    if [ ! -S /var/run/docker.sock ]; then
        echo "[HEALTHCHECK] docker port ${DOCKER_PORT_DESC}: FAILED (socket not found)"
        FAIL=1
        return
    fi

    if [ ! -r /var/run/docker.sock ] || [ ! -w /var/run/docker.sock ]; then
        echo "[HEALTHCHECK] docker port ${DOCKER_PORT_DESC}: FAILED (socket not accessible)"
        FAIL=1
        return
    fi

    DOCKER_VERSION=$(timeout 5 docker info --format '{{.ServerVersion}}' 2>/dev/null)
    if [ -n "$DOCKER_VERSION" ]; then
        if [ "$DOCKER_MODE" = "dind" ]; then
            echo "[HEALTHCHECK] docker (DinD) port ${DOCKER_PORT_DESC}: OK (version ${DOCKER_VERSION})"
        else
            echo "[HEALTHCHECK] docker (DooD) port ${DOCKER_PORT_DESC}: OK (version ${DOCKER_VERSION})"
        fi
    else
        if timeout 5 docker ps >/dev/null 2>&1; then
            echo "[HEALTHCHECK] docker port ${DOCKER_PORT_DESC}: OK"
        else
            echo "[HEALTHCHECK] docker port ${DOCKER_PORT_DESC}: FAILED"
            FAIL=1
        fi
    fi
}

check_jupyter() {
    if ! pgrep -f "jupyter" >/dev/null 2>&1; then
        echo "[HEALTHCHECK] jupyter port ${JUPYTER_PORT}: FAILED (process not running)"
        FAIL=1
        return
    fi

    HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" "http://127.0.0.1:${JUPYTER_PORT}/api" 2>/dev/null || echo "000")
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
