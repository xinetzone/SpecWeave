# XMNN Runtime Dockerfile (基于 skeleton 模板)
# Pattern: 01-build-env-reuse（基础镜像环境直用）
# Base: npu-tvm-build:conda (conda env: tvm-build, Python 3.14.6)

FROM npu-tvm-build:conda AS runtime

ARG DEBIAN_FRONTEND=noninteractive
ARG CONDA_ENV_NAME=tvm-build
ARG AI_UID=1000
ARG AI_GID=1000
ARG WORKSPACE_DIR=/workspace

USER root

ENV PIP_INDEX_URL=https://mirrors.aliyun.com/pypi/simple \
    PIP_TRUSTED_HOST=mirrors.aliyun.com \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PYTHONUNBUFFERED=1 \
    TVM_FFI=ctypes \
    PATH=/opt/conda/envs/${CONDA_ENV_NAME}/bin:/opt/conda/bin:${PATH} \
    LD_LIBRARY_PATH=/opt/conda/envs/${CONDA_ENV_NAME}/lib:/opt/conda/lib:/usr/local/lib

RUN set -eux; \
    for f in /etc/apt/sources.list /etc/apt/sources.list.d/*.list; do \
        if [ -f "$f" ]; then \
            sed -i -E 's@http://(deb|security).debian.org@https://mirrors.aliyun.com@g' "$f" || true; \
            sed -i -E 's@https?://(deb|security).debian.org@https://mirrors.aliyun.com@g' "$f" || true; \
        fi; \
    done; \
    apt-get update -qq; \
    apt-get install -y --no-install-recommends -qq \
        tzdata sudo acl passwd gosu \
        libstdc++6 libgomp1 libgcc-s1 findutils; \
    ln -sf /usr/share/zoneinfo/Asia/Shanghai /etc/localtime; \
    echo "Asia/Shanghai" > /etc/timezone; \
    rm -rf /var/lib/apt/lists/*

RUN set -eux; \
    pip install --no-cache-dir \
        pandas matplotlib openpyxl tqdm tomlkit; \
    python -c "from importlib.metadata import version; \
deps=['numpy','scipy','pandas']; \
[print(f'  {d}: {version(d)}') for d in deps if True]"

RUN set -eux; \
    if ! getent group ai >/dev/null; then \
        if getent group ${AI_GID} >/dev/null; then \
            EXISTING_GROUP=$(getent group ${AI_GID} | cut -d: -f1); \
            echo "GID ${AI_GID} taken by '${EXISTING_GROUP}', creating ai group with new GID"; \
            groupadd ai; \
        else \
            groupadd -g ${AI_GID} ai; \
        fi; \
    fi; \
    AI_GID_ACTUAL=$(getent group ai | cut -d: -f3); \
    if ! id -u ai >/dev/null 2>&1; then \
        if getent passwd ${AI_UID} >/dev/null; then \
            echo "UID ${AI_UID} exists, creating ai user with auto UID"; \
            useradd -m -s /bin/bash -g ai ai; \
        else \
            useradd -m -s /bin/bash -u ${AI_UID} -g ai ai; \
        fi; \
    fi; \
    usermod -aG sudo ai; \
    echo "ai ALL=(ALL) NOPASSWD:ALL" > /etc/sudoers.d/90-ai; \
    chmod 0440 /etc/sudoers.d/90-ai; \
    mkdir -p ${WORKSPACE_DIR} /home/ai/.local /home/ai/.pip /home/ai/.cache; \
    chown -R ai:ai /home/ai ${WORKSPACE_DIR}

COPY wheels/xmnn-*.whl /tmp/wheels/
COPY docker/entrypoint.sh /usr/local/bin/entrypoint.sh
COPY docker/_xmnn_init.py /tmp/_init/_xmnn_init.py
COPY docker/xmnn_init.pth /tmp/_init/xmnn_init.pth
RUN chmod +x /usr/local/bin/entrypoint.sh

RUN set -eux; \
    WHEEL_FILE=$(ls /tmp/wheels/xmnn-*.whl | head -1); \
    echo "Installing wheel: $WHEEL_FILE"; \
    pip install --no-cache-dir "$WHEEL_FILE"; \
    SITE_PKGS=$(python -c "import site; print(site.getsitepackages()[0])"); \
    cp /tmp/_init/_xmnn_init.py "$SITE_PKGS/"; \
    cp /tmp/_init/xmnn_init.pth "$SITE_PKGS/"; \
    echo "Verifying installation..."; \
    python -c "from importlib.metadata import version; print('  xmnn:', version('xmnn'))"; \
    echo "Verifying shared library dependencies..."; \
    for so in "$SITE_PKGS"/tvm/_libs/*.so*; do \
        if [ -f "$so" ]; then \
            MISSING=$(ldd "$so" 2>/dev/null | grep "not found" || true); \
            if [ -n "$MISSING" ]; then \
                echo "ERROR: Missing deps for $so:"; echo "$MISSING"; exit 1; \
            fi; \
        fi; \
    done; \
    echo "All shared library dependencies OK"; \
    echo "Verifying core imports..."; \
    python -c "import tvm, vta, xmnn; print('  Core imports OK: tvm={}, vta={}, xmnn={}'.format(tvm.__file__, vta.__file__, xmnn.__file__))"; \
    echo "Verifying TVM TE compute..."; \
    python -c "import tvm; from tvm import te; import numpy as np; n = te.var('n'); A = te.placeholder((n,), name='A'); B = te.compute((n,), lambda i: A[i] * 2.0, name='B'); s = te.create_schedule(B.op); mod = tvm.build(s, [A, B], 'llvm', name='double_array'); ctx = tvm.cpu(0); a = tvm.nd.array(np.array([1.0, 2.0, 3.0], dtype='float32'), ctx); b = tvm.nd.array(np.zeros(3, dtype='float32'), ctx); mod(a, b); result = b.numpy().tolist(); assert result == [2.0, 4.0, 6.0], f'Expected [2.0,4.0,6.0], got {result}'; print('  TE compute: [1,2,3] * 2 = [2.0,4.0,6.0] OK')"; \
    chown -R ai:ai "$SITE_PKGS" /home/ai/.local /home/ai/.cache; \
    CONDA_ENV_BIN="/opt/conda/envs/${CONDA_ENV_NAME}/bin"; \
    if [ -d "$CONDA_ENV_BIN" ]; then chown -R ai:ai "$CONDA_ENV_BIN"; fi; \
    rm -rf /tmp/wheels /tmp/_init; \
    echo "=== XMNN Runtime image built successfully! ==="

WORKDIR ${WORKSPACE_DIR}
RUN chmod 2775 ${WORKSPACE_DIR}
ENTRYPOINT ["/usr/local/bin/entrypoint.sh"]
CMD ["/bin/bash", "-l"]
