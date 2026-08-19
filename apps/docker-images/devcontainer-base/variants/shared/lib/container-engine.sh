#!/bin/bash
# =============================================================================
# lib/container-engine.sh — 容器引擎抽象库
# 提供 docker/podman 引擎自动检测与统一命令封装，消除测试脚本对引擎的硬编码依赖
#
# 用法 (在 source logging.sh 之后):
#   source "${VARIANTS_DIR}/shared/lib/container-engine.sh"
#   ENGINE="${BUILD_ENGINE:-auto}"   # 可提前覆盖；默认 auto 检测
#   detect_engine                    # 解析 ENGINE 并校验可用性
#
# 公共 API:
#   detect_engine                       # 解析 ENGINE(auto->docker/podman)并校验 PATH
#   engine_run <args...>                # 等价 ${ENGINE} run，统一输出流
#   engine_run_bash "<cmd>"             # 在容器 bash -c 中执行
#   engine_images <format>              # 列出镜像，剥离 registry 前缀(含 localhost/)
#   engine_image_exists <image>         # 判断镜像是否存在(已剥离前缀)
#   engine_cmd <args...>                # 透传执行引擎命令(非 run)
#
# 环境变量:
#   BUILD_ENGINE:  auto(默认) | docker | podman
# =============================================================================

# 引擎选择（可被调用方在 source 前通过 BUILD_ENGINE 覆盖，或 source 后直接改 ENGINE）
ENGINE="${BUILD_ENGINE:-auto}"  # auto|docker|podman

detect_engine() {
    # 构建/测试引擎自动检测（auto: 优先 docker，回退 podman），与 scripts/build.sh 保持一致
    if [ "$ENGINE" = "auto" ]; then
        if docker info >/dev/null 2>&1; then
            ENGINE="docker"
        elif podman info >/dev/null 2>&1; then
            ENGINE="podman"
        else
            log_fatal "Neither docker nor podman is available. Please install one or set BUILD_ENGINE explicitly."
        fi
    fi
    if ! command -v "$ENGINE" >/dev/null 2>&1; then
        log_fatal "Container engine '${ENGINE}' not found in PATH"
    fi
    log_info "Container engine: ${ENGINE}"
}

# 统一执行引擎命令（非 run 场景透传），供 images/inspect/version 等使用
engine_cmd() {
    ${ENGINE} "$@"
}

# 镜像 run 封装（无 mount）：统一输出流
engine_run() {
    ${ENGINE} run --rm "$IMAGE" "$@" 2>&1
}

# 镜像 run + bash -c
engine_run_bash() {
    ${ENGINE} run --rm "$IMAGE" bash -c "$1" 2>&1
}

# 镜像 run + 只读挂载目录 + bash -c
engine_run_mount_bash() {
    local host_dir="$1"
    local container_dir="$2"
    local cmd="$3"
    ${ENGINE} run --rm -v "${host_dir}:${container_dir}:ro" "$IMAGE" bash -c "$cmd" 2>&1
}

# 列出镜像，剥离 registry 前缀（podman 输出 localhost/xxx，docker 通常不带前缀）
# 参考 shim: podman images | sed 's|^localhost/||'
engine_images() {
    local format="${1:-'{{.Repository}}:{{.Tag}}'}"
    ${ENGINE} images --format "$format" 2>/dev/null | sed 's|^[^/]*/||'
}

# 判断镜像是否存在（与 $IMAGE 精确匹配，已剥离前缀）
engine_image_exists() {
    engine_images '{{.Repository}}:{{.Tag}}' | grep -qx "$IMAGE"
}