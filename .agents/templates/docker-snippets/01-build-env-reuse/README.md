# 模式1：基础镜像环境直用（Build-Env-Reuse）

> **核心原则**：已有build镜像包含完整编译依赖时，runtime镜像直接FROM复用，不做conda create/clone。
>
> **构建时间对比**：从零创建conda环境(60+min) → conda create --clone(7min+网络不稳定) → 直接复用build环境(<1min缓存命中)
>
> **源洞察**：XMNN Docker构建三次方案迭代——"为runtime创建干净环境"的直觉在已有build基础镜像场景下不适用

---

## 片段A：Dockerfile.runtime 模板

将以下模板复制到项目中，替换 `{{PLACEHOLDER}}` 变量即可使用：

```dockerfile
# ============================================================
# {{PROJECT_NAME}} Runtime Dockerfile
# Pattern: Build-Env-Reuse (基础镜像环境直用)
# Source: XMNN retrospective 2026-07-22
# ============================================================

# 【关键决策】直接使用构建镜像作为runtime基础，不新建conda环境
# 构建镜像已包含：Python {{PYTHON_VERSION}}、LLVM、numpy/scipy等所有编译依赖
FROM {{BUILD_IMAGE_NAME}}:{{BUILD_IMAGE_TAG}} AS runtime

ARG DEBIAN_FRONTEND=noninteractive
ARG CONDA_ENV_NAME={{CONDA_ENV_NAME}}
ARG AI_UID=1000
ARG AI_GID=1000
ARG WORKSPACE_DIR=/workspace

# 【关键配置】直接指向已有conda环境的bin和lib路径
ENV PIP_INDEX_URL=https://mirrors.aliyun.com/pypi/simple \
    PIP_TRUSTED_HOST=mirrors.aliyun.com \
    PATH=/opt/conda/envs/${CONDA_ENV_NAME}/bin:/opt/conda/bin:${PATH} \
    LD_LIBRARY_PATH=/opt/conda/envs/${CONDA_ENV_NAME}/lib:/opt/conda/lib:/usr/local/lib

# 系统包：仅安装runtime额外需要的包（tzdata/sudo/acl/gosu等）
# 注意：不要安装Python包（由pip install wheel处理）
RUN set -eux; \
    for f in /etc/apt/sources.list /etc/apt/sources.list.d/*.list; do \
        if [ -f "$f" ]; then \
            sed -i -E 's@http://(deb|security).debian.org@https://mirrors.aliyun.com@g' "$f" || true; \
        fi; \
    done; \
    apt-get update -qq; \
    apt-get install -y --no-install-recommends -qq \
        tzdata sudo acl passwd gosu libstdc++6 libgomp1 libgcc-s1 findutils; \
    rm -rf /var/lib/apt/lists/*

# 【层顺序优化】远程依赖先安装（可缓存），本地wheel后COPY（频繁变更）
RUN set -eux; \
    pip install --no-cache-dir \
        {{EXTRA_PIP_PACKAGES}}; \
    python -c "from importlib.metadata import version; \
deps=['numpy','scipy']; \
[print(f'  {d}: {version(d)}') for d in deps]"

# COPY本地wheel（最后COPY，不影响前面的缓存层）
COPY {{WHEEL_RELATIVE_PATH}}/ {{WHEEL_NAME_PATTERN}} /tmp/wheels/
COPY docker/entrypoint-runtime.sh /usr/local/bin/entrypoint.sh
RUN chmod +x /usr/local/bin/entrypoint.sh

# 安装wheel + 内置验证
RUN set -eux; \
    WHEEL_FILE=$(ls /tmp/wheels/{{WHEEL_NAME_PATTERN}} | head -1); \
    echo "Installing wheel: $WHEEL_FILE"; \
    pip install --no-cache-dir "$WHEEL_FILE"; \
    echo "Verifying installation..."; \
    python -c "from importlib.metadata import version; print('  {{PYPI_PACKAGE_NAME}}:', version('{{PYPI_PACKAGE_NAME}}'))"; \
    SITE_PKGS=$(python -c "import site; print(site.getsitepackages()[0])"); \
    echo "Verifying shared library dependencies..."; \
    for so in "$SITE_PKGS"/{{LIB_DIR}}/_libs/*.so*; do \
        if [ -f "$so" ]; then \
            MISSING=$(ldd "$so" 2>/dev/null | grep "not found" || true); \
            if [ -n "$MISSING" ]; then \
                echo "ERROR: Missing deps for $so:"; echo "$MISSING"; exit 1; \
            fi; \
        fi; \
    done; \
    echo "All shared library dependencies OK"; \
    rm -rf /tmp/wheels

# 工作目录与运行时用户
WORKDIR ${WORKSPACE_DIR}
RUN mkdir -p ${WORKSPACE_DIR} && chmod 777 ${WORKSPACE_DIR}
ENTRYPOINT ["/usr/local/bin/entrypoint.sh"]
CMD ["/bin/bash", "-l"]
```

### 占位符替换表

| 占位符 | 替换为 | XMNN项目示例值 |
|--------|--------|---------------|
| `{{PROJECT_NAME}}` | 项目名 | xmnn |
| `{{BUILD_IMAGE_NAME}}` | build镜像名 | npu-tvm-build |
| `{{BUILD_IMAGE_TAG}}` | build镜像tag | conda |
| `{{PYTHON_VERSION}}` | Python版本 | 3.14 |
| `{{CONDA_ENV_NAME}}` | conda环境名 | tvm-build |
| `{{EXTRA_PIP_PACKAGES}}` | 额外pip包（空格分隔） | pandas matplotlib openpyxl tqdm tomlkit |
| `{{WHEEL_RELATIVE_PATH}}` | wheel相对Dockerfile的路径 | packaging/dist |
| `{{WHEEL_NAME_PATTERN}}` | wheel文件glob | xmnn-*.whl |
| `{{PYPI_PACKAGE_NAME}}` | PyPI分发包名 | xmnn |
| `{{LIB_DIR}}` | 包内_libs目录名 | tvm |

---

## 片段B：entrypoint-runtime.sh 模板

```bash
#!/bin/bash
set -euo pipefail

# ============================================================
# Runtime Entrypoint Script
# Pattern: Build-Env-Reuse
# Features: UID/GID映射 + conda环境激活 + 环境变量设置
# ============================================================

log() { echo "[entrypoint] $*" >&2; }

TARGET_USER=ai
TARGET_HOME=/home/ai
WORK_DIR=/workspace
CONDA_ENV_NAME="${CONDA_ENV_NAME:-{{CONDA_ENV_NAME}}}"
CONDA_DIR=/opt/conda
SITE_PACKAGES="${CONDA_DIR}/envs/${CONDA_ENV_NAME}/lib/python{{PYTHON_VERSION}}/site-packages"

# 1. 初始化conda环境
log "Initializing conda environment: ${CONDA_ENV_NAME}"
source "${CONDA_DIR}/etc/profile.d/conda.sh"
conda activate "${CONDA_ENV_NAME}"

# 2. 设置TVM/库路径（根据项目调整）
TVM_LIBS_PATH="${SITE_PACKAGES}/{{LIB_DIR}}/_libs"
if [ -d "$TVM_LIBS_PATH" ]; then
    export TVM_LIBRARY_PATH="$TVM_LIBS_PATH"
    export LD_LIBRARY_PATH="$TVM_LIBS_PATH:${LD_LIBRARY_PATH:-}"
    log "Set TVM_LIBRARY_PATH=${TVM_LIBS_PATH}"
fi

# 3. 自动检测宿主机UID/GID（支持docker run -v挂载时权限匹配）
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
```

---

## 片段C：.pth 包自初始化模板

```python
# site-packages/_{{PKG_NAME}}_init.py
# 安装到 site-packages/，由对应的 .pth 文件自动导入
import os

_pkg_dir = os.path.dirname(__file__)
_libs_dir = os.path.join(_pkg_dir, '{{LIB_DIR}}', '_libs')

# 设置库搜索路径（Python进程内生效，不依赖系统ENV）
if os.path.isdir(_libs_dir):
    current = os.environ.get('LD_LIBRARY_PATH', '')
    if _libs_dir not in current:
        os.environ['LD_LIBRARY_PATH'] = (
            f'{_libs_dir}:{current}' if current else _libs_dir
        )

# 设置硬件配置路径（VTA等）
os.environ.setdefault('{{HW_PATH_ENV_VAR}}', os.path.join(_pkg_dir, '{{HW_DIR}}'))
```

```python
# site-packages/{{PKG_NAME}}_init.pth
# 每行一条Python语句，Python启动时自动执行
import _{{PKG_NAME}}_init
```

---

## 反模式速查（Do NOT）

| ❌ 反模式 | ✅ 正确做法 |
|-----------|-----------|
| `FROM python:3.14-slim` + 手动装LLVM/依赖 | FROM已有build镜像，依赖已就位 |
| `conda create -n runtime python=3.14 --clone tvm-build` | 直接使用tvm-build环境，不clone |
| `conda env create -f environment.yml` 在runtime层 | environment.yml只在build层使用 |
| 镜像中`conda clean -a`减小体积 | 不要清缓存——开发调试可能需要 |
| 不声明`USER root`直接apt-get | Dockerfile开头显式`USER root` |
| CMD用`/bin/bash`非login shell | CMD用`/bin/bash -l`加载conda profile |
