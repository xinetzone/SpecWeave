#!/bin/bash
set -eo pipefail

TARGET_USER=ai
TARGET_HOME=/home/ai
WORK_DIR=/workspace
CONDA_ENV_NAME="${CONDA_ENV_NAME:-tvm-build}"
CONDA_DIR=/opt/conda

log() { echo "[entrypoint] $*" >&2; }

log "XMNN Runtime Entrypoint Starting"

source "${CONDA_DIR}/etc/profile.d/conda.sh"
conda activate "${CONDA_ENV_NAME}"

SITE_PACKAGES=$(python -c "import site; print(site.getsitepackages()[0])" 2>/dev/null)
log "site-packages: ${SITE_PACKAGES}"

export CONDA_PREFIX="${CONDA_DIR}/envs/${CONDA_ENV_NAME}"
export CONDA_DEFAULT_ENV="${CONDA_ENV_NAME}"
export TVM_FFI=ctypes
export PATH="${TARGET_HOME}/.local/bin:${PATH}"

TVM_LIBS_PATH="${SITE_PACKAGES}/tvm/_libs"
if [ -d "$TVM_LIBS_PATH" ]; then
    export TVM_LIBRARY_PATH="$TVM_LIBS_PATH"
    export LD_LIBRARY_PATH="$TVM_LIBS_PATH:${LD_LIBRARY_PATH:-}"
    log "TVM_LIBRARY_PATH=${TVM_LIBS_PATH}"
fi

VTA_HW_FOUND="${SITE_PACKAGES}/vta"
if [ -d "$VTA_HW_FOUND" ]; then
    export VTA_HW_PATH="$VTA_HW_FOUND"
fi

if [ "$(id -u)" = "0" ]; then
    mkdir -p "$WORK_DIR"

    if [ -n "${HOST_UID:-}" ] && [ -n "${HOST_GID:-}" ]; then
        log "Using specified UID=$HOST_UID, GID=$HOST_GID"
    elif [ -d "$WORK_DIR" ]; then
        HOST_UID=$(stat -c '%u' "$WORK_DIR" 2>/dev/null || echo "1000")
        HOST_GID=$(stat -c '%g' "$WORK_DIR" 2>/dev/null || echo "1000")
        log "Auto-detected UID=$HOST_UID, GID=$HOST_GID from $WORK_DIR"
    else
        HOST_UID=$(id -u $TARGET_USER 2>/dev/null || echo "1000")
        HOST_GID=$(id -g $TARGET_USER 2>/dev/null || echo "1000")
    fi

    if [ "$HOST_UID" = "0" ]; then
        log "Warning: UID=0 detected, keeping default non-root UID"
        HOST_UID=1000
        HOST_GID=1000
    fi

    CURRENT_UID=$(id -u $TARGET_USER 2>/dev/null || echo "0")
    CURRENT_GID=$(id -g $TARGET_USER 2>/dev/null || echo "0")

    if [ "$HOST_UID" != "$CURRENT_UID" ] || [ "$HOST_GID" != "$CURRENT_GID" ]; then
        log "Adjusting UID/GID: $CURRENT_UID:$CURRENT_GID -> $HOST_UID:$HOST_GID"

        if [ "$HOST_GID" != "$CURRENT_GID" ]; then
            EXISTING_GROUP=$(getent group "$HOST_GID" 2>/dev/null | cut -d: -f1 || true)
            if [ -n "$EXISTING_GROUP" ] && [ "$EXISTING_GROUP" != "$TARGET_USER" ]; then
                log "GID $HOST_GID taken by '$EXISTING_GROUP', moving it"
                NEW_GID=9999
                while getent group "$NEW_GID" >/dev/null 2>&1; do NEW_GID=$((NEW_GID+1)); done
                groupmod -g "$NEW_GID" "$EXISTING_GROUP" 2>/dev/null || true
            fi
            groupmod -g "$HOST_GID" "$TARGET_USER" 2>/dev/null || true
        fi

        if [ "$HOST_UID" != "$CURRENT_UID" ]; then
            EXISTING_USER=$(getent passwd "$HOST_UID" 2>/dev/null | cut -d: -f1 || true)
            if [ -n "$EXISTING_USER" ] && [ "$EXISTING_USER" != "$TARGET_USER" ]; then
                log "UID $HOST_UID taken by '$EXISTING_USER', moving it"
                NEW_UID=9999
                while getent passwd "$NEW_UID" >/dev/null 2>&1; do NEW_UID=$((NEW_UID+1)); done
                usermod -u "$NEW_UID" "$EXISTING_USER" 2>/dev/null || true
            fi
            usermod -u "$HOST_UID" -g "$HOST_GID" "$TARGET_USER" 2>/dev/null || true
        fi

        chown -R "$HOST_UID:$HOST_GID" "$TARGET_HOME" 2>/dev/null || true
        if [ -d "$SITE_PACKAGES" ]; then
            find "$SITE_PACKAGES" -xdev -not -user "$HOST_UID" -exec chown "$HOST_UID:$HOST_GID" {} + 2>/dev/null || true
        fi
    fi

    chown "$HOST_UID:$HOST_GID" "$WORK_DIR" 2>/dev/null || true
    chmod 2775 "$WORK_DIR" 2>/dev/null || true

    log "Executing as $TARGET_USER ($HOST_UID:$HOST_GID): $*"

    if command -v gosu &>/dev/null; then
        exec gosu "$TARGET_USER" "$@"
    else
        exec su -s /bin/bash "$TARGET_USER" -c '
            source "${CONDA_DIR}/etc/profile.d/conda.sh"
            conda activate "${CONDA_ENV_NAME}"
            exec "$@"
        ' bash "$@"
    fi
else
    exec "$@"
fi
