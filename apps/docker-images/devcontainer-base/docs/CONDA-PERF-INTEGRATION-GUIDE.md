# Conda 性能配置快速集成指南

> 将 devcontainer-base v2.2.1 验证通过的 conda/mamba 高性能配置复用到你的项目中。
> 实测效果：Stage 4 构建时间从 419s 降至 37s（缓存热构建，11.3x 加速）。

---

## 一、资产清单

| 资产 | 路径 | 类型 | 适用场景 |
|------|------|------|---------|
| 官方源高性能模板 | `variants/shared/config/condarc/condarc-performant.yaml` | 静态 YAML | 海外/国际网络、配置固定 |
| 清华 TUNA 模板 | `variants/shared/config/condarc/condarc-performant-tuna.yaml` | 静态 YAML | 中国大陆网络、配置固定 |
| 阿里镜像模板 | `variants/shared/config/condarc/condarc-performant-aliyun.yaml` | 静态 YAML | 中国大陆网络、配置固定 |
| 动态配置脚本 | `variants/shared/scripts/conda-perf-setup.sh` | Shell 脚本 | 需要动态选择镜像源/调整参数 |

**核心优化三原则**（适用于所有资产）：
1. **并行 I/O**：`repodata_threads: N` / `execute_threads: N`（默认 N=8）
2. **单次 Solver**：所有包在单次 `mamba create`/`mamba install` 中指定
3. **原生 CLI**：使用 `mamba` 命令而非 `conda --solver=libmamba`

---

## 二、前置条件

| 条件 | 说明 |
|------|------|
| conda 发行版 | Miniforge3（推荐，自带 mamba）或 Miniconda3 + `conda install mamba` |
| conda 安装路径 | 默认 `/opt/conda`，可通过 `CONDA_DIR` 环境变量覆盖 |
| Docker BuildKit | 推荐使用 BuildKit 以支持 cache mount 和 bind mount |
| CPU 核心数 | 建议 ≥4 核，线程数默认 8 适配大多数 CI 环境 |

> ⚠️ **Micromamba 用户注意**：本套资产面向 Miniforge3/Miniconda3 + mamba CLI。Micromamba 使用 `.mambarc` 配置，不适用本指南。

---

## 三、三种集成方式

### 方式 A：静态模板（最简单，一行 COPY）

适合镜像源固定、不需要运行时决策的场景。只需一行 COPY 指令，零运行时开销。

**Step 1**：将模板文件复制到你的项目构建上下文中（或直接引用相对路径）。

**Step 2**：在 Dockerfile 中 conda 安装**之后**、创建环境**之前**添加：

```dockerfile
# 官方源（海外/国际网络）
COPY variants/shared/config/condarc/condarc-performant.yaml /root/.condarc

# ── 或清华 TUNA（中国大陆） ──
# COPY variants/shared/config/condarc/condarc-performant-tuna.yaml /root/.condarc

# ── 或阿里镜像 ──
# COPY variants/shared/config/condarc/condarc-performant-aliyun.yaml /root/.condarc
```

**Step 3**：设置 libmamba 为默认 solver（模板文件不包含此设置以兼容不同 conda 版本）：

```dockerfile
RUN conda config --set solver libmamba
```

**完整示例**：

```dockerfile
# 安装 Miniforge3 后...
COPY condarc-performant-tuna.yaml /root/.condarc
RUN conda config --set solver libmamba && \
    mamba create -y -n myenv -c conda-forge --override-channels \
        python=3.12 numpy pandas jupyterlab
```

---

### 方式 B：动态脚本（推荐，支持环境变量参数化）

适合需要通过构建参数（build-arg）切换镜像源、调整线程数的场景。

**Step 1**：将 `conda-perf-setup.sh` 复制到项目中（推荐放在 `scripts/` 或 `docker/` 目录下）。

**Step 2**：在 Dockerfile 中通过 COPY 或 BuildKit bind mount 引用脚本：

**方式 B1：COPY 模式（兼容性最好）**

```dockerfile
# 在 conda 安装之后、创建环境之前
COPY scripts/conda-perf-setup.sh /tmp/conda-perf-setup.sh
RUN chmod +x /tmp/conda-perf-setup.sh && \
    CONDA_MIRROR=tuna CONDA_THREADS=8 bash /tmp/conda-perf-setup.sh && \
    mamba create -y -n myenv -c conda-forge --override-channels python=3.12 numpy
```

**方式 B2：BuildKit bind mount（零镜像层开销，推荐）**

```dockerfile
# syntax=docker/dockerfile:1.6
RUN --mount=type=bind,source=scripts/conda-perf-setup.sh,target=/tmp/conda-perf-setup.sh,readonly \
    chmod +x /tmp/conda-perf-setup.sh && \
    CONDA_MIRROR=${CONDA_MIRROR} CONDA_THREADS=${CONDA_THREADS} bash /tmp/conda-perf-setup.sh && \
    mamba create -y -n myenv -c conda-forge --override-channels python=3.12 numpy
```

配合 `docker build --build-arg CONDA_MIRROR=tuna` 可在构建时动态切换镜像源。

**环境变量参考**：

| 变量 | 默认值 | 说明 |
|------|--------|------|
| `CONDA_DIR` | `/opt/conda` | conda 安装根目录 |
| `CONDA_MIRROR` | `official` | 镜像源：`official` / `tuna` / `aliyun` |
| `CONDA_THREADS` | `8` | 并行下载/解压线程数（建议=CPU核心数） |
| `CONDA_TIMEOUT` | 自动（官方300s/镜像120s） | 读取超时秒数 |
| `CONDA_RETRIES` | `5` | 最大重试次数 |
| `CONDA_OUTPUT` | `/root/.condarc` | .condarc 写入路径 |

**配合 BuildKit cache mount（强烈推荐）**：

```dockerfile
RUN --mount=type=cache,target=/opt/conda/pkgs,sharing=locked \
    --mount=type=cache,target=/root/.cache/conda,sharing=locked \
    --mount=type=bind,source=scripts/conda-perf-setup.sh,target=/tmp/conda-perf-setup.sh,readonly \
    CONDA_MIRROR=tuna CONDA_THREADS=8 bash /tmp/conda-perf-setup.sh && \
    mamba create -y -n myenv -c conda-forge --override-channels python=3.12 numpy pandas
```

---

### 方式 C：Source 模式（高级，获取辅助函数）

适合在 CI 脚本或复杂构建流程中使用，脚本 source 后提供两个辅助函数。

```bash
#!/bin/bash
set -euo pipefail

source /path/to/conda-perf-setup.sh

# 方式1：先运行配置（写入.condarc + 设置solver）
CONDA_MIRROR=tuna CONDA_THREADS=8 bash /path/to/conda-perf-setup.sh

# 方式2：直接使用 mamba_create_env 辅助函数
# 优势：自动选择 mamba/conda、单次 solver、内联计时、错误处理
mamba_create_env myenv python=3.12 numpy pandas jupyterlab scikit-learn

# 验证配置
conda_perf_verify
```

**辅助函数**：

| 函数 | 用法 | 说明 |
|------|------|------|
| `mamba_create_env <name> [pkgs...]` | `mamba_create_env myenv python=3.12 numpy` | 一次性创建环境，自动选择mamba/conda fallback，含计时和错误处理 |
| `conda_perf_verify` | `conda_perf_verify` | 验证 conda/mamba 可用性、.condarc 配置 |

---

## 四、创建环境的最佳实践

### ✅ 正确：单次 mamba create

```dockerfile
RUN mamba create -y -n myenv -c conda-forge --override-channels -q \
    "python=3.12" \
    pip \
    numpy \
    pandas \
    "jupyterlab>=4.0" \
    ipykernel
```

### ❌ 错误：分步安装（导致双重 solver）

```dockerfile
# 不要这样做！两次命令 = 两次 solver 运行
RUN mamba create -y -n myenv python=3.12 && \
    mamba install -y -n myenv numpy pandas jupyterlab
```

### ✅ 正确：pip 包在 conda 之后安装

```dockerfile
RUN mamba create -y -n myenv -c conda-forge python=3.12 numpy pip && \
    /opt/conda/envs/myenv/bin/pip install some-pip-only-package
```

---

## 五、完整 Dockerfile 参考

```dockerfile
# syntax=docker/dockerfile:1.6
FROM ubuntu:24.04

# ── 安装系统依赖 ──
RUN apt-get update && apt-get install -y --no-install-recommends \
        wget bzip2 ca-certificates bash \
    && rm -rf /var/lib/apt/lists/*

# ── 安装 Miniforge3 ──
ARG MINIFORGE_VERSION=24.11.3-2
RUN wget -q "https://github.com/conda-forge/miniforge/releases/download/${MINIFORGE_VERSION}/Miniforge3-${MINIFORGE_VERSION}-Linux-x86_64.sh" \
        -O /tmp/miniforge.sh && \
    bash /tmp/miniforge.sh -b -p /opt/conda && \
    rm /tmp/miniforge.sh

ENV PATH=/opt/conda/bin:$PATH

# ── 构建参数 ──
ARG CONDA_MIRROR=official
ARG CONDA_THREADS=8

# ── 高性能 conda 配置（使用共享脚本） ──
RUN --mount=type=cache,target=/opt/conda/pkgs,sharing=locked \
    --mount=type=cache,target=/root/.cache/conda,sharing=locked \
    --mount=type=bind,source=scripts/conda-perf-setup.sh,target=/tmp/conda-perf-setup.sh,readonly \
    chmod +x /tmp/conda-perf-setup.sh && \
    CONDA_MIRROR=${CONDA_MIRROR} CONDA_THREADS=${CONDA_THREADS} \
        bash /tmp/conda-perf-setup.sh && \
    mamba create -y -n myenv -c conda-forge --override-channels -q \
        python=3.12 \
        pip \
        numpy \
        pandas \
        jupyterlab \
        ipykernel && \
    /opt/conda/bin/conda clean -afy

# ── 激活环境 ──
RUN echo "source activate myenv" >> ~/.bashrc
ENV PATH=/opt/conda/envs/myenv/bin:$PATH

# ── 验证 ──
RUN python --version && \
    python -c "import numpy; print(f'numpy {numpy.__version__}')" && \
    jupyter --version
```

**构建命令**：

```bash
# 国际网络
docker build -t my-conda-image .

# 中国大陆网络（清华镜像，8线程）
docker build -t my-conda-image \
    --build-arg CONDA_MIRROR=tuna \
    --build-arg CONDA_THREADS=8 \
    .

# 中国大陆网络（阿里镜像，16线程）
docker build -t my-conda-image \
    --build-arg CONDA_MIRROR=aliyun \
    --build-arg CONDA_THREADS=16 \
    .
```

---

## 六、验证集成效果

构建完成后，在容器内运行以下命令验证配置是否生效：

```bash
# 1. 检查 .condarc 配置
cat /root/.condarc
# 预期：repodata_threads: 8, execute_threads: 8, 正确的channels

# 2. 检查 solver
conda config --show solver
# 预期：solver: libmamba

# 3. 检查 mamba 版本
mamba --version
# 预期：正常输出版本号

# 4. 安装速度测试
time mamba install -y -n base -c conda-forge --override-channels -q scipy
# 对比优化前后的时间
```

---

## 七、常见问题

**Q1：我使用的是 Miniconda3（不是 Miniforge3），能用吗？**
> 可以。但需要先安装 mamba CLI：
> ```bash
> conda install -y -n base -c conda-forge mamba
> ```
> 如果不安装 mamba，脚本会自动回退到 `conda --solver=libmamba`（稍慢但仍可用）。

**Q2：线程数设多少合适？**
> 建议设为 Docker 构建可使用的 CPU 核心数。大多数 CI 环境（GitHub Actions、GitLab CI）是 2-4 核，设 4-8 即可；本地构建 8-16 核可设 8-16。注意：线程数超过核心数不会带来额外收益，反而可能增加上下文切换开销。

**Q3：为什么脚本设置了超时自动适配？**
> 官方 conda-forge 源在海外，中国大陆访问延迟高、带宽低，需要更长超时（300s）；国内镜像（tuna/aliyun）延迟低，120s 通常足够。如果你显式设置了 `CONDA_TIMEOUT`，脚本会使用你的值而非自动适配。

**Q4：BuildKit cache mount 有什么用？**
> `--mount=type=cache,target=/opt/conda/pkgs` 将 conda 下载的包缓存到宿主机，后续构建时不需要重新下载，可大幅加速重建。`sharing=locked` 防止并发构建时缓存损坏。

**Q5：可以在非 Docker 环境（本地/CI 脚本）中使用吗？**
> 完全可以。直接执行脚本即可：
> ```bash
> CONDA_MIRROR=tuna CONDA_THREADS=8 bash conda-perf-setup.sh
> ```
> 脚本会自动检测 conda 路径（优先 `/opt/conda`，其次 PATH 中的 conda）。

**Q6：.condarc 中为什么没有直接设置 solver？**
> 不同版本的 conda 对 `.condarc` 中 `solver:` 字段的兼容性不同，部分老版本会报错。因此脚本使用 `conda config --set solver libmamba` 命令设置，更安全可靠。静态模板用户也需要手动执行此命令。

---

## 八、性能调优参考

| 环境 | CONDA_THREADS | CONDA_MIRROR | CONDA_TIMEOUT | 预期场景 |
|------|--------------|-------------|--------------|---------|
| GitHub Actions (2核) | 4 | official/tuna | 300/120 | CI 构建 |
| GitLab CI (4核) | 8 | official/tuna | 300/120 | CI 构建 |
| 本地 WSL2 (8核) | 8 | tuna/aliyun | 120 | 开发构建 |
| 本地 Mac M系列 (8核) | 8 | official | 300 | 开发构建 |
| 服务器 (16+核) | 16 | official | 300 | 生产构建 |
| 弱网环境 | 4 | tuna/aliyun | 300 | 网络差时降低并发避免超时 |

---

## 九、相关资源

| 资源 | 路径 |
|------|------|
| 性能优化模式文档 | `.agents/docs/retrospective/patterns/code-patterns/conda-build-performance-triple-optimization.md` |
| v2.2.1 里程碑复盘报告 | `.agents/docs/retrospective/reports/build-engineering/retrospective-devcontainer-v221-conda-perf-20260814/README.md` |
| 洞察萃取 | `.agents/docs/retrospective/reports/build-engineering/retrospective-devcontainer-v221-conda-perf-20260814/insight-extraction.md` |
| Dockerfile 实战参考 | `Dockerfile`（Stage 4/7 部分） |
| CHANGELOG | `CHANGELOG.md`（v2.2.1-ft 章节） |
