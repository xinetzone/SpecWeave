#!/bin/bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LIB_DIR="${SCRIPT_DIR}/lib"

VERSION="1.0.0"
SSH_PORT="${SSH_PORT:-22}"
JUPYTER_PORT="${JUPYTER_PORT:-8888}"
FAIL=0

if [ -f "${LIB_DIR}/logging.sh" ]; then
    # shellcheck source=lib/logging.sh
    source "${LIB_DIR}/logging.sh"
else
    log_info() { echo "[$(date '+%Y-%m-%d %H:%M:%S')] [INFO] $*"; }
    log_ok() { echo "[$(date '+%Y-%m-%d %H:%M:%S')] [OK] $*"; }
    log_warn() { echo "[$(date '+%Y-%m-%d %H:%M:%S')] [WARN] $*"; }
    log_error() { echo "[$(date '+%Y-%m-%d %H:%M:%S')] [ERROR] $*" >&2; }
fi

show_version() {
    echo "healthcheck.sh v${VERSION}"
    exit 0
}

if [ $# -gt 0 ]; then
    case "$1" in
        -v|--version)
            show_version
            ;;
        *)
            ;;
    esac
fi

echo "[HEALTHCHECK] Starting health checks..."
echo "[HEALTHCHECK] SSH port: ${SSH_PORT}, Jupyter port: ${JUPYTER_PORT}"

if command -v podman >/dev/null 2>&1; then
    log_info "Podman detected, checking availability..."
    if podman --version >/dev/null 2>&1; then
        log_ok "Podman is available: $(podman --version 2>&1)"
        PODMAN_SOCKET=$(podman info --format '{{.Host.RemoteSocket.Path}}' 2>/dev/null || echo "")
        if [ -n "${PODMAN_SOCKET}" ]; then
            log_info "Podman remote socket path: ${PODMAN_SOCKET}"
        fi
    else
        log_warn "Podman command exists but not functional (non-fatal)"
    fi
else
    log_info "Podman not detected (non-fatal, skipping podman checks)"
fi

if ! pgrep -x sshd >/dev/null 2>&1; then
    log_error "sshd process not running"
    FAIL=1
else
    log_ok "sshd process is running"
    if timeout 2 bash -c "exec 3<>/dev/tcp/127.0.0.1/${SSH_PORT} && exec 3>&-" 2>/dev/null; then
        log_ok "sshd port ${SSH_PORT}: TCP connection OK"
    else
        log_error "sshd port ${SSH_PORT}: TCP connection FAILED"
        FAIL=1
    fi
fi

JUPYTER_CHECKED=0

if pgrep -f "jupyter" >/dev/null 2>&1; then
    log_ok "Jupyter process is running"
    JUPYTER_PYTHON=""
    if [ -x "/opt/conda/envs/main/bin/python" ]; then
        JUPYTER_PYTHON="/opt/conda/envs/main/bin/python"
    elif command -v python >/dev/null 2>&1; then
        JUPYTER_PYTHON="python"
    fi

    if [ -n "${JUPYTER_PYTHON}" ]; then
        HTTP_CODE=$(${JUPYTER_PYTHON} -c "
import urllib.request
import sys
try:
    req = urllib.request.Request('http://127.0.0.1:${JUPYTER_PORT}/api', method='GET')
    with urllib.request.urlopen(req, timeout=3) as r:
        print(r.status)
except urllib.error.HTTPError as e:
    print(e.code)
except Exception:
    print('000')
" 2>/dev/null || echo "000")
        JUPYTER_CHECKED=1
    fi

    if [ "${JUPYTER_CHECKED}" -eq 0 ] && command -v curl >/dev/null 2>&1; then
        HTTP_CODE=$(curl -s --max-time 3 -o /dev/null -w "%{http_code}" "http://127.0.0.1:${JUPYTER_PORT}/api" 2>/dev/null || echo "000")
        JUPYTER_CHECKED=1
    fi

    if [ "${JUPYTER_CHECKED}" -eq 0 ]; then
        log_warn "No HTTP client available (python/curl), skipping HTTP check"
        HTTP_CODE="200"
    fi

    if [ "$HTTP_CODE" = "200" ] || [ "$HTTP_CODE" = "302" ] || [ "$HTTP_CODE" = "401" ] || [ "$HTTP_CODE" = "403" ]; then
        log_ok "Jupyter port ${JUPYTER_PORT}: HTTP ${HTTP_CODE} OK"
    else
        log_error "Jupyter port ${JUPYTER_PORT}: HTTP ${HTTP_CODE} FAILED"
        FAIL=1
    fi
else
    log_error "Jupyter process not running"
    FAIL=1
fi

if [ "$FAIL" -eq 1 ]; then
    log_error "STATUS: UNHEALTHY"
    exit 1
fi

log_ok "STATUS: HEALTHY"
exit 0
