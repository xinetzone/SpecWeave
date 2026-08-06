# =============================================================================
# caffe-ffi 生产部署镜像（基于 Conv v4 OpenMP 优化技术总结）
#
# 设计要点（源自 caffe-ffi-conv-v4-optimization-summary.md §6 部署要点）：
#   1. 多阶段构建：Builder 编译 conda 环境与 C++ 扩展，Runtime 精简镜像
#   2. 环境变量在 Runtime 固化（ENV + entrypoint.sh），禁止 Python 内 os.environ
#   3. OpenMP 双层并行隔离：外层 Conv OMP 多线程 + 内层 BLAS 单线程
#   4. 时区 Asia/Shanghai 三层保证（tzdata + localtime + ENV TZ）
#   5. 至少 4 核 CPU 配额（由 docker run --cpus 保证，见 build.sh 提示）
#
# 构建用法（在 SpecWeave 根目录执行）：
#   cd d:/spaces/SpecWeave
#   docker build -f .trae/specs/caffe-ffi-conv-v4-milestone/deploy/Dockerfile \
#     -t caffe-ffi-prod:latest .
# 国内镜像源：--build-arg APT_MIRROR=aliyun --build-arg PIP_MIRROR=aliyun \
#              --build-arg CONDA_MIRROR=tuna
#
# DEPLOY_PROFILE 双层含义：
#   - 构建期 --build-arg：固化 Runtime 阶段 ENV 默认值（记录进镜像元数据）
#   - 运行期 -e DEPLOY_PROFILE=xxx：运行时覆盖（优先级更高，推荐）
#   取值: latency(延迟敏感) / throughput(吞吐优先) / general(通用均衡)
# =============================================================================

# -----------------------------------------------------------------------------
# 全局构建参数
# -----------------------------------------------------------------------------
ARG APT_MIRROR=official
ARG PIP_MIRROR=official
ARG CONDA_MIRROR=official
ARG PYTHON_VERSION=3.14
ARG DEPLOY_PROFILE=general

# =============================================================================
# STAGE 1: Builder — 编译 caffe-ffi conda 环境 + C++ 扩展
# =============================================================================
FROM continuumio/miniconda3:latest AS builder

SHELL ["/bin/bash", "-e", "-o", "pipefail", "-c"]

ARG APT_MIRROR
ARG PIP_MIRROR
ARG CONDA_MIRROR
ARG PYTHON_VERSION

ENV DEBIAN_FRONTEND=noninteractive \
    LANG=C.UTF-8 \
    LC_ALL=C.UTF-8 \
    CONDA_DIR=/opt/conda \
    PATH=/opt/conda/bin:$PATH

# -----------------------------------------------------------------------------
# [Builder 1/4] 配置 APT 镜像并安装构建依赖
# -----------------------------------------------------------------------------
RUN echo "=== [Builder 1/4] APT mirror: ${APT_MIRROR} ===" && \
    if [ "${APT_MIRROR}" = "aliyun" ]; then \
        for f in /etc/apt/sources.list.d/debian.sources /etc/apt/sources.list; do \
            if [ -f "$$f" ]; then \
                sed -i 's|http://deb.debian.org|http://mirrors.aliyun.com|g; s|http://security.debian.org|http://mirrors.aliyun.com|g' "$$f"; \
            fi; \
        done; \
    elif [ "${APT_MIRROR}" = "tuna" ]; then \
        for f in /etc/apt/sources.list.d/debian.sources /etc/apt/sources.list; do \
            if [ -f "$$f" ]; then \
                sed -i 's|http://deb.debian.org|https://mirrors.tuna.tsinghua.edu.cn|g; s|http://security.debian.org|https://mirrors.tuna.tsinghua.edu.cn|g' "$$f"; \
            fi; \
        done; \
    fi && \
    apt-get update && \
    apt-get install -y --no-install-recommends \
        build-essential \
        pkg-config \
        wget \
        ca-certificates \
        git \
    && rm -rf /var/lib/apt/lists/* && \
    echo "[BUILD] Builder base packages installed"

# -----------------------------------------------------------------------------
# [Builder 2/4] 配置 conda/pip 镜像并创建 caffe-ffi conda 环境
# 参考: projects/xuanspace/libs/caffe-ffi/environment.yml + conda.recipe/meta.yaml
# -----------------------------------------------------------------------------
RUN echo "=== [Builder 2/4] Creating conda env: caffe-ffi (Python ${PYTHON_VERSION}) ===" && \
    source "${CONDA_DIR}/etc/profile.d/conda.sh" && \
    conda config --system --set auto_activate_base false && \
    if [ "${CONDA_MIRROR}" = "tuna" ]; then \
        printf 'channels:\n  - https://mirrors.tuna.tsinghua.edu.cn/anaconda/cloud/conda-forge\n  - https://mirrors.tuna.tsinghua.edu.cn/anaconda/pkgs/r\n  - https://mirrors.tuna.tsinghua.edu.cn/anaconda/pkgs/main\nshow_channel_urls: true\nchannel_priority: strict\nssl_verify: true\n' > "${CONDA_DIR}/.condarc" && \
        echo "[BUILD] Using Tsinghua TUNA conda mirror"; \
    else \
        printf 'channels:\n  - conda-forge\n  - defaults\nchannel_priority: strict\n' > "${CONDA_DIR}/.condarc" && \
        echo "[BUILD] Using default conda channels"; \
    fi && \
    if [ "${PIP_MIRROR}" = "aliyun" ]; then \
        mkdir -p /root/.config/pip && \
        printf '[global]\nindex-url = https://mirrors.aliyun.com/pypi/simple/\ntrusted-host = mirrors.aliyun.com\nretries = 10\ntimeout = 120\n' > /root/.config/pip/pip.conf; \
    elif [ "${PIP_MIRROR}" = "tuna" ]; then \
        mkdir -p /root/.config/pip && \
        printf '[global]\nindex-url = https://pypi.tuna.tsinghua.edu.cn/simple/\ntrusted-host = pypi.tuna.tsinghua.edu.cn\nretries = 10\ntimeout = 120\n' > /root/.config/pip/pip.conf; \
    fi && \
    echo "[BUILD] conda create ..." && \
    conda create -y -n caffe-ffi -c conda-forge \
        python="${PYTHON_VERSION}" \
        pip setuptools wheel setuptools-scm \
        "libprotobuf>=7.0.0" \
        "protobuf>=7.0.0" \
        zlib \
        libopenblas \
        "cmake>=3.26" \
        "ninja>=1.13" \
        make \
        cxx-compiler \
        patchelf \
    && conda activate caffe-ffi && \
    echo "[BUILD] conda env 'caffe-ffi', Python: $(python --version)" && \
    pip install --no-cache-dir \
        "numpy>=2.3" \
        "scikit-build-core>=0.10" \
        "cython>=3.2.8" \
        "typing-extensions>=4.5" \
        "pytest>=8.0" \
    && echo "[BUILD] Base Python deps installed"

# -----------------------------------------------------------------------------
# [Builder 3/4] 从源码编译 tvm-ffi（本地 vendor 源码）
# 参考: build.sh 中 CAFFE_FFI_TVM_FFI_DIR 逻辑，本地源码 pip 安装
# -----------------------------------------------------------------------------
# 构建上下文：SpecWeave 根目录
COPY projects/xuanspace/vendor/tvm-ffi /tmp/tvm-ffi
COPY projects/xuanspace/libs/caffe-ffi /tmp/caffe-ffi

# 安装 tvm-ffi
RUN echo "=== [Builder 3/4] Building tvm-ffi from local source ===" && \
    source "${CONDA_DIR}/etc/profile.d/conda.sh" && conda activate caffe-ffi && \
    export SETUPTOOLS_SCM_PRETEND_VERSION="0.1.13" && \
    export CMAKE_ARGS="-DTVM_FFI_USE_LIBBACKTRACE=OFF -DTVM_FFI_BACKTRACE_ON_SEGFAULT=OFF" && \
    cd /tmp/tvm-ffi && \
    pip install . --no-deps -vv --no-build-isolation && \
    echo "[BUILD] tvm-ffi installed: $(python -c 'import tvm_ffi; print(tvm_ffi.__version__)')"

# -----------------------------------------------------------------------------
# [Builder 4/4] 编译 caffe-ffi（本地源码，含 Conv v4 OpenMP 优化）
# -----------------------------------------------------------------------------
RUN echo "=== [Builder 4/4] Building caffe-ffi from local source ===" && \
    source "${CONDA_DIR}/etc/profile.d/conda.sh" && conda activate caffe-ffi && \
    export CAFFE_FFI_TVM_FFI_DIR=/tmp/tvm-ffi && \
    export SETUPTOOLS_SCM_PRETEND_VERSION="0.1.0" && \
    cd /tmp/caffe-ffi && \
    pip install . --no-deps -vv --no-build-isolation && \
    echo "[BUILD] caffe-ffi installed: $(python -c 'import caffe_ffi; print(caffe_ffi.__version__)')" && \
    echo "[BUILD] caffe_ffi.is_available: $(python -c 'import caffe_ffi; print(caffe_ffi.is_available())')" && \
    conda clean -ya && pip cache purge 2>/dev/null || true && \
    echo "[BUILD] ========== BUILDER STAGE COMPLETE =========="

# =============================================================================
# STAGE 2: Runtime — 精简生产镜像
# =============================================================================
FROM continuumio/miniconda3:latest

SHELL ["/bin/bash", "-e", "-o", "pipefail", "-c"]

LABEL maintainer="caffe-ffi Production Team" \
      description="caffe-ffi CPU inference production image (Conv v4 OpenMP optimized)"

ARG APT_MIRROR
ARG DEPLOY_PROFILE
ARG PYTHON_VERSION

ARG CONDA_DIR=/opt/conda
ARG ENV_NAME=caffe-ffi
ARG ENV_PATH=/opt/conda/envs/caffe-ffi
ARG APP_DIR=/app

ENV CONDA_DIR=/opt/conda \
    ENV_NAME=caffe-ffi \
    ENV_PATH=/opt/conda/envs/caffe-ffi \
    PATH=/opt/conda/envs/caffe-ffi/bin:/opt/conda/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin \
    LD_LIBRARY_PATH=/opt/conda/envs/caffe-ffi/lib:/opt/conda/lib:${LD_LIBRARY_PATH} \
    CONDA_DEFAULT_ENV=caffe-ffi \
    APP_DIR=/app \
    DEPLOY_PROFILE=${DEPLOY_PROFILE}

# -----------------------------------------------------------------------------
# [Runtime 1/5] 时区 Asia/Shanghai 三层保证 + 运行时系统依赖
# -----------------------------------------------------------------------------
RUN echo "=== [Runtime 1/5] Setting timezone Asia/Shanghai ===" && \
    if [ "${APT_MIRROR}" = "aliyun" ]; then \
        for f in /etc/apt/sources.list.d/debian.sources /etc/apt/sources.list; do \
            if [ -f "$$f" ]; then \
                sed -i 's|http://deb.debian.org|http://mirrors.aliyun.com|g; s|http://security.debian.org|http://mirrors.aliyun.com|g' "$$f"; \
            fi; \
        done; \
    elif [ "${APT_MIRROR}" = "tuna" ]; then \
        for f in /etc/apt/sources.list.d/debian.sources /etc/apt/sources.list; do \
            if [ -f "$$f" ]; then \
                sed -i 's|http://deb.debian.org|https://mirrors.tuna.tsinghua.edu.cn|g; s|http://security.debian.org|https://mirrors.tuna.tsinghua.edu.cn|g' "$$f"; \
            fi; \
        done; \
    fi && \
    apt-get update && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        tzdata \
        libgomp1 \
        curl \
    && ln -sf /usr/share/zoneinfo/Asia/Shanghai /etc/localtime && \
    echo "Asia/Shanghai" > /etc/timezone && \
    rm -rf /var/lib/apt/lists/* && \
    echo "[BUILD] Timezone set to Asia/Shanghai (layer 1/2 done, layer 3 via ENV TZ)"

ENV TZ=Asia/Shanghai

# -----------------------------------------------------------------------------
# [Runtime 2/5] 复制 caffe-ffi conda 环境（含编译好的 C++ 扩展）
# -----------------------------------------------------------------------------
COPY --from=builder /opt/conda/envs/caffe-ffi /opt/conda/envs/caffe-ffi

RUN echo "=== [Runtime 2/5] Copying conda env ===" && \
    test -x "${ENV_PATH}/bin/python" && \
    echo "Python: $("${ENV_PATH}/bin/python" --version)" && \
    echo "${CONDA_DIR}/lib" > /etc/ld.so.conf.d/caffe-ffi.conf && \
    echo "${ENV_PATH}/lib" >> /etc/ld.so.conf.d/caffe-ffi.conf && \
    ldconfig && \
    "${ENV_PATH}/bin/python" -c "import numpy; print('numpy', numpy.__version__)" && \
    "${ENV_PATH}/bin/python" -c "import caffe_ffi; print('caffe_ffi', caffe_ffi.__version__, 'available', caffe_ffi.is_available())"

# -----------------------------------------------------------------------------
# [Runtime 3/5] 固化 OpenMP 双层并行隔离环境变量（转换基础默认值）
# 注意：不设置 OMP_PROC_BIND（混合 P/E 核让 OS 调度），OPENBLAS_NUM_THREADS 必须=1
# Profile 具体值由 entrypoint.sh 依据 DEPLOY_PROFILE 覆盖（见 §6 三 Profile）
# -----------------------------------------------------------------------------
ENV OMP_NUM_THREADS=4 \
    OPENBLAS_NUM_THREADS=1 \
    OMP_WAIT_POLICY=PASSIVE \
    KMP_DUPLICATE_LIB_OK=TRUE \
    GLOG_minloglevel=2 \
    PYTHONUNBUFFERED=1

# -----------------------------------------------------------------------------
# [Runtime 4/5] 应用目录 + 入口脚本
# -----------------------------------------------------------------------------
RUN mkdir -p "${APP_DIR}/models" "${APP_DIR}/config" && \
    echo "[BUILD] App dir created: ${APP_DIR}"

COPY .trae/specs/caffe-ffi-conv-v4-milestone/deploy/entrypoint.sh /usr/local/bin/entrypoint.sh
RUN chmod +x /usr/local/bin/entrypoint.sh && \
    sed -i 's/\r$//' /usr/local/bin/entrypoint.sh && \
    echo "[BUILD] entrypoint.sh installed"

# -----------------------------------------------------------------------------
# [Runtime 5/5] 健康检查 + 元数据
# -----------------------------------------------------------------------------
RUN echo "=== [Runtime 5/5] Final metadata ===" && \
    printf 'BUILD_DATE=%s\nBASE_IMAGE=continuumio/miniconda3:latest\nENV_NAME=caffe-ffi\nPYTHON_VERSION=%s\nDEPLOY_PROFILE=%s\nSERVICES=caffe-ffi-inference\n' \
        "$(date -u +%Y-%m-%dT%H:%M:%SZ)" "${PYTHON_VERSION}" "${DEPLOY_PROFILE}" > /etc/caffe-ffi-prod-build-info && \
    cat /etc/caffe-ffi-prod-build-info && \
    echo "[BUILD] ========== RUNTIME STAGE COMPLETE =========="

WORKDIR ${APP_DIR}

# 健康检查：验证 caffe_ffi 可导入 + 环境变量配置正确
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
    CMD ["/usr/local/bin/entrypoint.sh", "--healthcheck"]

# 入口：环境变量自检 + 启动用户命令（默认进入交互式 shell）
ENTRYPOINT ["/usr/local/bin/entrypoint.sh"]
CMD ["bash"]