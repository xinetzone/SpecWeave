#!/bin/bash
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

source "${SCRIPT_DIR}/lib/logging.sh"
LOG_SERVICE="dind-ssh-check-env"
LOG_JSON_OUTPUT="/tmp/dind-ssh-check-env-events.jsonl"

eval "$(log_parse_args "$@")"

_start_time=$(date +%s)
_elapsed() { echo $(( $(date +%s) - _start_time )); }

OS_TYPE="unknown"
OS_DETAIL=""
WSL_VERSION=""
WSL_INTEROP_OK=0
DOCKER_AVAILABLE=0
DOCKER_MODE=""
WSLC_AVAILABLE=0
WSLC_PATH=""
RECOMMENDED_RUNTIME=""
READY=0

detect_os() {
    log_step "OS Detection"
    case "$(uname -s)" in
        Linux*)
            OS_TYPE="linux"
            if grep -qi microsoft /proc/version 2>/dev/null || [ -n "${WSL_DISTRO_NAME:-}" ]; then
                OS_DETAIL="wsl"
                if uname -r | grep -qi "WSL2" || [ -n "${WSL_INTEROP:-}" ]; then
                    WSL_VERSION="2"
                else
                    WSL_VERSION="1"
                fi
                log_ok "WSL${WSL_VERSION} detected (${WSL_DISTRO_NAME:-Unknown distro})"
            else
                OS_DETAIL="native"
                log_ok "Native Linux detected"
            fi
            [ -f /etc/os-release ] && . /etc/os-release && log_info "  Distro: ${PRETTY_NAME:-unknown}"
            log_info "  Kernel: $(uname -r)"
            ;;
        Darwin*)
            OS_TYPE="macos"; OS_DETAIL="native"
            log_ok "macOS detected"
            ;;
        MINGW*|MSYS*|CYGWIN*)
            OS_TYPE="windows"; OS_DETAIL="git-bash"
            log_ok "Windows (Git Bash/MSYS2) detected"
            ;;
        *)
            OS_TYPE="unknown"
            log_warn "Unknown OS: $(uname -s)"
            ;;
    esac
    log_event os_detected os_type="$OS_TYPE" os_detail="$OS_DETAIL" wsl_version="${WSL_VERSION:-0}"
    echo ""
}

detect_wsl() {
    [ "$OS_DETAIL" != "wsl" ] && return 0
    log_step "WSL Interop Check"
    if [ -n "${WSL_INTEROP:-}" ] && [ -S "$WSL_INTEROP" ]; then
        log_ok "WSL interop socket available"; WSL_INTEROP_OK=1
    else
        log_warn "WSL interop not available - Windows exe may not be accessible"
    fi
    command -v wslpath &>/dev/null && log_ok "wslpath available" || log_warn "wslpath not found"
    if [ "$WSL_VERSION" = "1" ]; then
        log_warn "WSL1: container support limited - upgrade to WSL2 recommended"
    else
        log_ok "WSL2: full container support available"
    fi
    echo ""
}

detect_docker() {
    log_step "Docker Detection"
    if command -v docker &>/dev/null; then
        DOCKER_VERSION=$(docker --version 2>/dev/null | head -1 || echo "unknown")
        log_ok "Docker CLI found: ${DOCKER_VERSION}"
        if docker info &>/dev/null 2>&1; then
            DOCKER_AVAILABLE=1
            log_ok "Docker daemon reachable"
            if [ "$OS_DETAIL" = "wsl" ]; then
                if docker info 2>/dev/null | grep -qi "docker desktop"; then
                    DOCKER_MODE="docker-desktop"
                    log_ok "  Mode: Docker Desktop WSL integration"
                else
                    DOCKER_MODE="native-in-wsl"
                    log_ok "  Mode: Native Docker Engine in WSL"
                fi
            fi
        else
            log_warn "Docker daemon not reachable"
            if [ "$OS_DETAIL" = "wsl" ]; then
                log_warn "  - Ensure Docker Desktop is running and WSL integration is enabled"
            fi
        fi
    else
        log_warn "Docker CLI not found"
    fi
    log_event docker_detected available="$DOCKER_AVAILABLE" mode="${DOCKER_MODE:-none}"
    echo ""
}

detect_wslc() {
    log_step "WSLC (wslc.exe) Detection"
    if [ "$OS_TYPE" = "windows" ] || [ "$OS_DETAIL" = "wsl" ]; then
        if [ "$OS_DETAIL" = "wsl" ] && [ "$WSL_INTEROP_OK" = "1" ]; then
            WSLC_PATH="wslc.exe"
        elif [ "$OS_TYPE" = "windows" ]; then
            WSLC_PATH="wslc.exe"
        fi
        if [ -n "$WSLC_PATH" ] && command -v "$WSLC_PATH" &>/dev/null; then
            WSLC_AVAILABLE=1
            WSLC_VER=$($WSLC_PATH --version 2>/dev/null || echo "preview")
            log_ok "wslc.exe found: ${WSLC_VER}"
            log_warn "  NOTE: wslc is PREVIEW - API may change"
            log_warn "  NOTE: Limited network support; DinD may not work (privileged)"
        else
            log_warn "wslc.exe not found (update WSL: wsl --update)"
        fi
    else
        log_info "Not Windows/WSL - wslc.exe not applicable"
    fi
    log_event wslc_detected available="$WSLC_AVAILABLE" path="${WSLC_PATH:-none}"
    echo ""
}

check_requirements() {
    log_step "Summary"
    if [ "$DOCKER_AVAILABLE" = "1" ]; then
        log_ok "Docker: AVAILABLE (recommended for full DinD)"
        READY=1; RECOMMENDED_RUNTIME="docker"
    else
        log_warn "Docker: NOT AVAILABLE"
        if [ "$WSLC_AVAILABLE" = "1" ]; then
            log_ok "wslc: AVAILABLE (SSH-only mode, DinD limited)"
            READY=1; RECOMMENDED_RUNTIME="wslc"
        else
            log_error "No container runtime available"
        fi
    fi
    if [ "$OS_DETAIL" = "wsl" ] && [ "$WSL_VERSION" = "1" ]; then
        log_warn "WSL1: containers not fully supported"; READY=0
    fi
    echo ""
    if [ "$READY" = "1" ]; then
        log_ok "========================================"
        log_ok "Environment ready! Recommended runtime: ${RECOMMENDED_RUNTIME}"
        log_ok "========================================"
    else
        log_error "========================================"
        log_error "Environment NOT ready"
        log_error "========================================"
        echo ""
        log_info "Install options:"
        if [ "$OS_DETAIL" = "wsl" ] || [ "$OS_TYPE" = "windows" ]; then
            log_info "  1) Docker Desktop (recommended): https://www.docker.com/products/docker-desktop/"
            log_info "  2) wslc.exe (preview, no DinD): run 'wsl --update' in PowerShell"
            log_info "  3) Docker Engine in WSL: https://docs.docker.com/engine/install/ubuntu/"
        else
            log_info "  Install Docker Engine: https://docs.docker.com/engine/install/"
        fi
        [ "$WSL_VERSION" = "1" ] && log_info "  Upgrade WSL1->WSL2: wsl --set-version <distro> 2"
    fi
    echo ""
    cat > "${PROJECT_DIR}/.env.detected" <<EOF
OS_TYPE=${OS_TYPE}
OS_DETAIL=${OS_DETAIL}
WSL_VERSION=${WSL_VERSION:-0}
DOCKER_AVAILABLE=${DOCKER_AVAILABLE}
WSLC_AVAILABLE=${WSLC_AVAILABLE}
RECOMMENDED_RUNTIME=${RECOMMENDED_RUNTIME:-none}
READY=${READY}
EOF
    log_event check_complete ready="$READY" recommended_runtime="${RECOMMENDED_RUNTIME:-none}" duration=$(_elapsed)
    log_metric check_duration $(_elapsed) seconds
    return $((1 - READY))
}

echo "============================================================"
echo "  dind-ssh Environment Checker"
echo "  Project: ${PROJECT_DIR}"
echo "  Time: $(date)"
echo "============================================================"
echo ""
detect_os
detect_wsl
detect_docker
detect_wslc
check_requirements
