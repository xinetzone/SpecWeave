#!/bin/bash
# =============================================================================
# PyTorch Base Image Entrypoint
# =============================================================================
# Responsibilities:
#   1. Ensure conda env 'pytorch' is on PATH for both login and non-login shells
#   2. Load build-time config (e.g., ENTRYPOINT_QUIET) from /etc/pytorch-base-build-info
#   3. Switch to non-root 'ai' user if running as root (unless --user specified)
#   4. Display environment info banner on interactive startup
#   5. tini (PID 1) handles signal forwarding and zombie reaping
#
# Debug logging:
#   Set ENTRYPOINT_DEBUG=1 to enable debug-level logging (e.g., docker run -e ENTRYPOINT_DEBUG=1 ...)
# =============================================================================
set -e

# =============================================================================
# Structured logging (equivalent to logger.info/debug/warn/error)
# Output goes to stderr so it doesn't interfere with application stdout
# =============================================================================
_log_ts() { date '+%Y-%m-%d %H:%M:%S'; }

entry_log_info() {
    echo "[entrypoint][INFO]  $(_log_ts) | $*" >&2
}

entry_log_warn() {
    echo "[entrypoint][WARN]  $(_log_ts) | $*" >&2
}

entry_log_error() {
    echo "[entrypoint][ERROR] $(_log_ts) | $*" >&2
}

entry_log_debug() {
    if [ "${ENTRYPOINT_DEBUG:-0}" = "1" ]; then
        echo "[entrypoint][DEBUG] $(_log_ts) | $*" >&2
    fi
}

entry_log_branch() {
    entry_log_info "[BRANCH] >>> $*"
}

# =============================================================================
# Default environment paths (defined early for error trap context)
# =============================================================================
CONDA_DIR="/opt/conda"
ENV_NAME="pytorch"
ENV_PATH="${CONDA_DIR}/envs/${ENV_NAME}"

# =============================================================================
# Error handler - trap errors and log context (like build.sh)
# =============================================================================
_entrypoint_on_error() {
    local line_no=$1
    local cmd=$2
    entry_log_error "Entrypoint FAILED at line ${line_no}"
    entry_log_error "Failed command: ${cmd}"
    entry_log_error "Context:"
    entry_log_error "  PID        : $$"
    entry_log_error "  uid/gid    : $(id -u)/$(id -g)"
    entry_log_error "  user       : $(whoami 2>/dev/null || echo 'unknown')"
    entry_log_error "  working dir: $(pwd 2>/dev/null || echo 'unknown')"
    entry_log_error "  ENV_NAME   : ${ENV_NAME:-<not set>}"
    entry_log_error "  ENV_PATH   : ${ENV_PATH:-<not set>}"
    entry_log_error "  CONDA_DIR  : ${CONDA_DIR:-<not set>}"
    entry_log_error "  args       : $*"
}
trap '_entrypoint_on_error ${LINENO} "$BASH_COMMAND"' ERR

# =============================================================================
# Step 1: Entry initialization
# =============================================================================
entry_log_info "Entrypoint started (PID=$$, args='$*')"
entry_log_debug "Running as uid=$(id -u), gid=$(id -g), user=$(whoami)"
entry_log_debug "Working directory: $(pwd)"

# =============================================================================
# Load build-time configuration from /etc/pytorch-base-build-info
# =============================================================================
if [ -f /etc/pytorch-base-build-info ]; then
    entry_log_debug "Loading build-time config from /etc/pytorch-base-build-info..."
    while IFS='=' read -r key value; do
        case "$key" in
            PYTORCH_VERSION|PYTHON_VERSION|USE_GPU|CUDA_VERSION|BUILD_DATE)
                entry_log_debug "  build-info: ${key}=${value}"
                ;;
            ENTRYPOINT_QUIET)
                if [ "$value" = "1" ] && [ -z "${ENTRYPOINT_QUIET:-}" ]; then
                    export ENTRYPOINT_QUIET=1
                    entry_log_debug "  ENTRYPOINT_QUIET=1 loaded from build info"
                fi
                ;;
        esac
    done < /etc/pytorch-base-build-info
else
    entry_log_warn "Build info file /etc/pytorch-base-build-info not found (may be dev/debug image)"
fi

entry_log_debug "ENTRYPOINT_QUIET=${ENTRYPOINT_QUIET:-0}"
entry_log_debug "RUN_AS_USER=${RUN_AS_USER:-<not set, will default to 'ai'>}"

# =============================================================================
# Step 2: Environment setup - prepend conda env to PATH
# =============================================================================
entry_log_branch "Setting up conda environment '${ENV_NAME}' at ${ENV_PATH}"

if [ ! -d "$ENV_PATH" ]; then
    entry_log_error "Conda environment not found at ${ENV_PATH}!"
    entry_log_error "The image may be corrupted. Check /etc/pytorch-base-build-info for build details."
    ls -la "${CONDA_DIR}/envs/" 2>/dev/null || true
    exit 1
fi

export PATH="${ENV_PATH}/bin:${CONDA_DIR}/bin:${PATH}"
export CONDA_DEFAULT_ENV="${ENV_NAME}"
export CONDA_PREFIX="${ENV_PATH}"

entry_log_debug "PATH prefix: ${ENV_PATH}/bin:${CONDA_DIR}/bin"
entry_log_debug "CONDA_DEFAULT_ENV=${CONDA_DEFAULT_ENV}"
entry_log_debug "CONDA_PREFIX=${CONDA_PREFIX}"

# Source conda.sh for full conda functionality (activate/deactivate)
if [ -f "${CONDA_DIR}/etc/profile.d/conda.sh" ]; then
    entry_log_debug "Sourcing conda.sh from ${CONDA_DIR}/etc/profile.d/conda.sh"
    # shellcheck source=/dev/null
    . "${CONDA_DIR}/etc/profile.d/conda.sh"
    conda activate "${ENV_NAME}" 2>/dev/null || {
        entry_log_warn "conda activate ${ENV_NAME} failed (non-critical; PATH already set)"
    }
    entry_log_debug "conda activate ${ENV_NAME} completed"
else
    entry_log_warn "conda.sh not found at ${CONDA_DIR}/etc/profile.d/conda.sh; conda commands may not work"
fi

# Verify Python is from conda env
if command -v python &>/dev/null; then
    PYTHON_PATH=$(which python)
    PYTHON_VER=$(python --version 2>&1)
    entry_log_debug "Python binary: ${PYTHON_PATH}"
    entry_log_debug "Python version: ${PYTHON_VER}"
    if [[ "$PYTHON_PATH" != "${ENV_PATH}/bin/python" ]]; then
        entry_log_warn "Python is not from conda env! Expected ${ENV_PATH}/bin/python, got ${PYTHON_PATH}"
    fi
else
    entry_log_error "Python not found in PATH! Environment setup failed."
    exit 1
fi

# Check PyTorch availability (non-fatal; some derived images may not have it yet)
if python -c "import torch" 2>/dev/null; then
    PYTORCH_VER=$(python -c "import torch; print(torch.__version__)" 2>/dev/null || echo "unknown")
    CUDA_AVAIL=$(python -c "import torch; print(torch.cuda.is_available())" 2>/dev/null || echo "unknown")
    entry_log_debug "PyTorch version: ${PYTORCH_VER}, CUDA available: ${CUDA_AVAIL}"
else
    entry_log_debug "PyTorch not importable (may be installed later in derived image)"
fi

# =============================================================================
# Step 3: Display startup banner (only for interactive TTY shells)
# =============================================================================
show_banner() {
    if [ -z "${ENTRYPOINT_QUIET:-}" ] && [ -t 0 ]; then
        entry_log_info "Interactive TTY detected, displaying banner"
        echo ""
        echo "============================================================"
        echo "  PyTorch Base Image (Miniconda3 + Python + PyTorch)"
        echo "============================================================"
        echo ""
        echo "  Conda env : ${ENV_NAME} (${ENV_PATH})"
        echo "  Python    : $(python --version 2>&1 || echo 'unknown')"
        echo "  PyTorch   : $(python -c 'import torch; print(torch.__version__)' 2>&1 || echo 'not installed')"
        echo "  CUDA      : $(python -c 'import torch; print("available ("+str(torch.cuda.device_count())+" devices)" if torch.cuda.is_available() else "not available")' 2>&1 || echo 'unknown')"
        echo "  User      : $(whoami)"
        echo "  Workdir   : $(pwd)"
        echo ""
        echo "  Tip: conda env '${ENV_NAME}' is already activated on PATH"
        echo "  Tip: Set ENTRYPOINT_DEBUG=1 for verbose logging"
        echo "============================================================"
        echo ""
    else
        entry_log_debug "Banner suppressed (ENTRYPOINT_QUIET=${ENTRYPOINT_QUIET:-0}, TTY=$([ -t 0 ] && echo yes || echo no))"
    fi
}

# =============================================================================
# Step 4: User switching logic
# =============================================================================
switch_user_if_needed() {
    local target_user="${RUN_AS_USER:-ai}"
    entry_log_debug "User switch logic: current uid=$(id -u), target_user=${target_user}"

    if [ "$(id -u)" = "0" ]; then
        entry_log_branch "Running as root, checking if user switch is needed"

        if [ "$target_user" = "root" ]; then
            entry_log_branch "RUN_AS_USER=root: staying as root (user requested)"
            return 0
        fi

        if id "$target_user" &>/dev/null; then
            entry_log_info "Switching to user '${target_user}' (uid=$(id -u "$target_user"))"

            # Fix ownership of working directory if it's owned by root and writable
            local current_wd
            current_wd=$(pwd)
            if [ -d "$current_wd" ] && [ "$(stat -c '%u' "$current_wd" 2>/dev/null)" = "0" ]; then
                entry_log_debug "Working directory ${current_wd} is owned by root; changing ownership to ${target_user}"
                chown -R "${target_user}:${target_user}" "$current_wd" 2>/dev/null || \
                    entry_log_warn "Could not change ownership of ${current_wd} (non-critical)"
            fi

            entry_log_info "Executing command as '${target_user}' via gosu: $*"
            exec gosu "${target_user}" "$@"
        else
            entry_log_error "Target user '${target_user}' does not exist in container!"
            entry_log_error "Available users:"
            cat /etc/passwd | grep -E '/(bash|sh)$' | cut -d: -f1,3 | sed 's/^/  /' >&2
            exit 1
        fi
    else
        entry_log_debug "Not running as root (uid=$(id -u)), no user switch needed"
    fi
}

# =============================================================================
# Main execution flow
# =============================================================================
entry_log_debug "Entrypoint main flow starting"

# Check if gosu is available
if command -v gosu &>/dev/null; then
    entry_log_debug "gosu is available at $(which gosu)"
else
    entry_log_warn "gosu not found; user switching may not work correctly"
fi

# Handle user switching (when running as root)
if [ "$(id -u)" = "0" ]; then
    show_banner
    switch_user_if_needed "$@"
fi

entry_log_debug "Running command as uid=$(id -u), user=$(whoami)"

# If no command provided, start interactive bash login shell
if [ $# -eq 0 ]; then
    entry_log_branch "No command provided, starting interactive bash login shell"
    show_banner
    entry_log_info "Executing: /bin/bash -l"
    exec /bin/bash -l
else
    entry_log_branch "Executing user command: $*"
    entry_log_debug "Command args count: $#"
    entry_log_debug "Command[0]: $1"
    exec "$@"
fi
