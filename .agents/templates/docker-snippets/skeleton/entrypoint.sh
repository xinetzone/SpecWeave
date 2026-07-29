#!/bin/bash
# Runtime Container Entrypoint
# Pattern: Build-Env-Reuse
# Features: UID/GID自动映射 + conda环境激活 + 环境变量设置 + gosu降权
set -euo pipefail

log() { echo "[entrypoint] $*" >&2; }

TARGET_USER=ai
TARGET_HOME=/home/ai
WORK_DIR=/workspace
CONDA_ENV_NAME="${CONDA_ENV_NAME:-{{CONDA_ENV_NAME}}}"
CONDA_DIR=/opt/conda
SITE_PACKAGES="${CONDA_DIR}/envs/${CONDA_ENV_NAME}/lib/python{{PYTHON_VERSION}}/site-packages"

# 1. 激活 conda 环境
log "Initializing conda environment: ${CONDA_ENV_NAME}"
source "${CONDA_DIR}/etc/profile.d/conda.sh"
conda activate "${CONDA_ENV_NAME}"

# 2. 设置动态库路径
LIBS_PATH="${SITE_PACKAGES}/{{LIB_DIR}}/_libs"
if [ -d "$LIBS_PATH" ]; then
    export TVM_LIBRARY_PATH="$LIBS_PATH"
    export LD_LIBRARY_PATH="$LIBS_PATH:${LD_LIBRARY_PATH:-}"
    log "Set TVM_LIBRARY_PATH=${LIBS_PATH}"
fi

# 3. 自动检测宿主机 UID/GID（支持 docker run -v 挂载时权限匹配）
if [ "$(id -u)" = "0" ]; then
    HOST_UID=$(stat -c '%u' "$WORK_DIR" 2>/dev/null || echo "${AI_UID:-1000}")
    HOST_GID=$(stat -c '%g' "$WORK_DIR" 2>/dev/null || echo "${AI_GID:-1000}")

    if [ "$HOST_UID" != "0" ] && [ "$HOST_UID" != "$(id -u ${TARGET_USER} 2>/dev/null || echo 0)" ]; then
        log "Adjusting UID/GID to match host: ${HOST_UID}:${HOST_GID}"
        groupmod -o -g "$HOST_GID" ${TARGET_USER} 2>/dev/null || true
        usermod -o -u "$HOST_UID" -g "$HOST_GID" ${TARGET_USER} 2>/dev/null || true
        chown -R "${HOST_UID}:${HOST_GID}" "$TARGET_HOME" /tmp 2>/dev/null || true
    fi
    setfacl -R -m "u:${HOST_UID}:rwx" "$WORK_DIR" 2>/dev/null || chmod -R 777 "$WORK_DIR"
    exec gosu "${TARGET_USER}" "$@"
else
    exec "$@"
fi
