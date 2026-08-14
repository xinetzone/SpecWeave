# Conda 高性能 Dockerfile 模板

三种集成方式的可复制 Dockerfile 模板，配合 [conda-perf-setup.sh](../../scripts/conda-perf-setup.sh) 和 [condarc-performant*.yaml](../../config/condarc/) 使用。

## 模板选择指南

| 模板文件 | 方式 | 复杂度 | BuildKit | 需要复制的文件 | 适用场景 |
|---------|------|--------|:---:|--------------|---------|
| `Dockerfile.method-a-static` | A: 静态 YAML | ★☆☆☆☆ | 需要 | Dockerfile + 1个YAML | 镜像源固定、追求最简配置 |
| `Dockerfile.method-b1-copy` | B1: COPY 脚本 | ★★☆☆☆ | 需要 | Dockerfile + 1个Shell脚本 | 偏好传统COPY方式、动态切换镜像源 |
| `Dockerfile.method-b2-bindmount` | B2: BuildKit bind mount | ★★☆☆☆ | **需要（推荐）** | Dockerfile + 1个Shell脚本 | **推荐**：零镜像层、脚本变更不影响缓存 |

> 💡 **三种模板均使用 BuildKit cache mount** 加速重建。B1 与 B2 的核心区别是脚本传递方式：B1 用 COPY 写入镜像层（脚本变更会导致后续层缓存失效），B2 用 bind mount 零层挂载（脚本变更不影响后续层缓存）。若镜像源固定不需要动态切换，用 A 最简。

## 快速开始（方式 B2，推荐）

```bash
# 1. 创建项目目录
mkdir my-conda-project && cd my-conda-project
mkdir scripts

# 2. 复制模板和脚本
cp /path/to/Dockerfile.method-b2-bindmount Dockerfile
cp /path/to/conda-perf-setup.sh scripts/

# 3. 替换占位符
#    __BASE_IMAGE__     → ubuntu:24.04
#    __MINIFORGE_VER__  → 24.11.3-2
#    __PYTHON_VERSION__ → 3.12
#    __CONDA_PACKAGES__ → numpy pandas jupyterlab
#    __APP_DIR__        → /app

# 4. 构建（国内网络用 tuna 镜像）
DOCKER_BUILDKIT=1 docker build -t my-conda-app \
    --build-arg CONDA_MIRROR=tuna \
    --build-arg CONDA_THREADS=8 .

# 5. 运行
docker run --rm -it my-conda-app python -c "import numpy; print(numpy.__version__)"
```

## 文件来源

需要从 devcontainer-base 项目复制到你的项目中的文件：

| 文件 | 来源路径 | 放置位置（相对 Dockerfile） |
|------|---------|--------------------------|
| YAML 模板（方式A） | `variants/shared/config/condarc/condarc-performant*.yaml` | 与 Dockerfile 同级 |
| 配置脚本（方式B） | `variants/shared/scripts/conda-perf-setup.sh` | `scripts/conda-perf-setup.sh` |

## 核心优化三原则（所有模板内置）

1. **并行 I/O**：`repodata_threads: 8` / `execute_threads: 8`
2. **单次 Solver**：所有包在一次 `mamba create` 中指定
3. **原生 CLI**：使用 `mamba` 而非 `conda --solver=libmamba`

## Method B2 深度解析：为什么推荐 bind mount

### 机制对比：COPY vs bind mount vs cache mount

| 机制 | 写入镜像层 | 缓存持久化 | 脚本变更影响 | BuildKit 版本要求 |
|------|:---:|:---:|:---:|:---:|
| `COPY script.sh /tmp/` | ✅ 增加一层 (~5KB) | ❌ 随层缓存 | 🔴 **使后续所有层缓存失效** | 任意版本 |
| `--mount=type=bind` | ❌ 零层开销 | N/A（只读挂载） | 🟢 **仅影响当前 RUN** | 18.09+ |
| `--mount=type=cache` | ❌ 零层开销 | ✅ 跨构建持久化 | 🟢 **不影响其他层** | 18.09+ |

**关键理解**：Docker 构建时每条 `RUN` 指令的缓存 key 由父层 hash + 指令文本 + 输入文件 checksum 共同决定。

- **COPY 脚本**：脚本文件 checksum 成为该层 hash 的一部分。脚本任何修改（包括注释）都会改变层 hash，导致**所有后续层**缓存失效。虽然 B1 也使用了 cache mount（已下载的包不重复下载），但 `mamba create` 层需要重新执行 solver（~20-40s），且 COPY 产生一个额外镜像层（~5KB）。
- **bind mount 脚本**：脚本内容 hash 是该 RUN 指令 cache key 的一部分（脚本变则该 RUN 重跑），但 **bind mount 不写入镜像层**。如果脚本输出（.condarc 内容）完全相同，产出的层 digest 不变，后续层（mamba create）仍可命中缓存；即使配置变了导致后续层重跑，cache mount 里已下载的包也能让求解器跳过下载。

### 性能对比（典型场景：numpy + pandas + jupyterlab，约 1.2GB 包）

> 数据基于国内 TUNA 镜像 + 8 线程场景估算，实际耗时因网络带宽/CPU/磁盘速度而异。假设 Dockerfile 层顺序正确（COPY 应用代码在最后）。

| 构建场景 | Method A (静态YAML) | Method B1 (COPY脚本) | Method B2 (bind mount 推荐) |
|---------|:---:|:---:|:---:|
| **首次构建（冷缓存，全量下载）** | ~120-180s | ~120-180s | ~120-180s |
| **仅代码变更（配置/包均未变）** | ~3-8s ⚡ | ~3-8s ⚡ | ~3-8s ⚡ |
| **配置文件/脚本注释微调（输出不变）** | ~20-40s（COPY层失效，re-solve） | ~20-40s（COPY层失效，re-solve） | **~3-8s** ⚡（层digest不变） |
| **配置变更（镜像源/线程数，包未变）** | ~20-40s（cache mount命中包） | ~20-40s（cache mount命中包） | ~20-40s（cache mount命中包） |
| **新增一个包（暖缓存）** | ~20-40s | ~20-40s | ~20-40s |
| **镜像大小额外开销** | +~0.5KB（YAML层） | +~5KB（脚本层） | **+0KB** |
| **并发构建安全** | ✅ | ✅ | ✅ (sharing=locked) |

**B2 为什么是推荐方案**：三种模板在冷构建和配置变更场景性能相当（都受益于 cache mount），核心差异在于**脚本/配置微调场景**——B2 的 bind mount 机制使脚本变更不写入镜像层，输出不变时后续层直接命中缓存，实现 3-8s 重建；而 B1 的 COPY 机制会导致后续层失效，即使 cache mount 命中已下载的包，仍需 20-40s 重新求解。对于频繁迭代配置的开发阶段，B2 提供约 5-10x 的微调加速。

> 💡 **Method A 最简**：不需要脚本，仅一个 YAML 文件 + 一行 COPY，适合镜像源固定、不需要动态切换的项目。B1 适合偏好传统 COPY 方式且不介意脚本变更触发 re-solve 的场景。

### cache mount 路径规范（避免冲突）

三个 cache mount 的职责和路径必须严格分离，**不可合并**：

```dockerfile
# ✅ 正确：三个独立 cache mount，各司其职
# /opt/conda/pkgs    → conda 包缓存（tar.bz2/.conda 文件）
# /root/.cache/conda → libmamba solver 元数据缓存
# /root/.cache/pip   → pip wheel 缓存
RUN --mount=type=cache,target=/opt/conda/pkgs,sharing=locked \
    --mount=type=cache,target=/root/.cache/conda,sharing=locked \
    --mount=type=cache,target=/root/.cache/pip,sharing=locked \
    mamba create -y -n myenv ...
```

| 路径 | 内容 | 典型大小 | 能否跨项目共享 |
|------|------|---------|:---:|
| `/opt/conda/pkgs` | 下载的 conda 包（tar.bz2/.conda）+ 解压后的 pkgs 目录 | 500MB-3GB | ✅ 同架构可共享 |
| `/root/.cache/conda` | libmamba repodata 缓存、SAT solver 临时文件 | 10-50MB | ✅ 可共享 |
| `/root/.cache/pip` | pip wheel 缓存、HTTP 缓存 | 50-200MB | ✅ 可共享 |
| `/var/cache/apt` | APT 下载的 .deb 包 | 50-200MB | ✅ 同基础镜像可共享 |
| `/var/lib/apt/lists` | APT 软件包列表元数据 | 10-30MB | ✅ 可共享 |

> ⚠️ **不要合并路径**：`/root/.cache` 不能同时挂 conda 和 pip——BuildKit 以 exact path 为 key 隔离缓存，合并会导致不同构建的缓存互相覆盖或内容混杂。

### Best Practices（B2 最佳实践）

#### 1. cache mount id 隔离（多项目/多 Python 版本场景）

当同一台机器构建多个项目时，建议用 `id` 参数隔离缓存，避免不同项目的包缓存混杂导致缓存污染：

```dockerfile
# 多项目共存时，给 cache mount 加 id 前缀
RUN --mount=type=cache,id=conda-pkgs-v1,target=/opt/conda/pkgs,sharing=locked \
    --mount=type=cache,id=conda-metadata-v1,target=/root/.cache/conda,sharing=locked \
    --mount=type=cache,id=pip-wheels-v1,target=/root/.cache/pip,sharing=locked \
    mamba create -y -n myenv ...
```

- 不同 Python 版本建议加后缀区分：`id=conda-pkgs-py312`
- conda-forge 大版本升级（如 Python 3.12→3.13）时建议改 id（如 `-v2`），防止旧包残留

#### 2. sharing 模式选择

| 模式 | 并发行为 | 适用场景 |
|------|---------|---------|
| `sharing=locked`（默认） | 互斥锁，串行写入 | **推荐**：conda/pip 包安装不是并发安全的 |
| `sharing=shared` | 多读单写 | 只读场景，不适合安装包 |
| `sharing=private` | 每个构建独立副本 | 并行 CI 构建但缓存不共享，写入快 |

> conda 的包解压和链接操作**不是并发安全的**，多个构建并发写入同一个 `/opt/conda/pkgs` cache 会导致包损坏。务必使用 `sharing=locked`。

#### 3. 线程数调优（CONDA_THREADS）

```dockerfile
ARG CONDA_THREADS=8
# 建议值：
# - 本地开发（4-8核）：设为 CPU 核心数
# - CI 环境（2-4核）：设为 2-4，避免 CPU 争抢
# - 高核数机器（16+核）：设为 8-12，repodata 解析并行度有限，过高无收益
```

`repodata_threads` 控制 repodata.json 并行下载/解析数，`execute_threads` 控制包解压/链接并行数。两者设为相同值即可。瓶颈通常在磁盘 I/O 而非 CPU，超过 12 线程边际收益递减。

#### 4. Dockerfile 层顺序优化（最大化缓存命中）

```dockerfile
# ✅ 正确：变化频率从低到高排列
FROM ubuntu:24.04
SHELL ["/bin/bash", "-e", "-o", "pipefail", "-c"]

# Layer 1: 系统依赖（变化频率：最低）
RUN --mount=type=cache,target=/var/cache/apt,sharing=locked \
    --mount=type=cache,target=/var/lib/apt/lists,sharing=locked \
    apt-get update && apt-get install -y --no-install-recommends wget bzip2 ...

# Layer 2: Miniforge 安装（变化频率：低，版本固定时可缓存数月）
RUN _MINIFORGE_URL="..." && wget ... && bash /tmp/miniforge.sh -b -p /opt/conda

# Layer 3: conda-perf-setup.sh 配置（变化频率：中，调整镜像源/线程）
RUN --mount=type=bind,source=scripts/conda-perf-setup.sh,target=/tmp/setup.sh,readonly \
    --mount=type=cache,target=/opt/conda/pkgs,sharing=locked \
    --mount=type=cache,target=/root/.cache/conda,sharing=locked \
    bash /tmp/setup.sh

# Layer 4: conda 包安装（变化频率：中高，新增/升级包）
RUN --mount=type=cache,target=/opt/conda/pkgs,sharing=locked \
    --mount=type=cache,target=/root/.cache/conda,sharing=locked \
    --mount=type=cache,target=/root/.cache/pip,sharing=locked \
    mamba create -y -n myenv ...

# Layer 5: 应用代码（变化频率：最高，放最后！）
COPY . /app
WORKDIR /app
```

> 核心原则：**将变化频率高的指令放后面**。应用代码 `COPY . /app` 永远放最后，否则每次代码变更都会导致 conda 环境重建。

#### 5. 缓存清理与诊断

```bash
# 查看 BuildKit 缓存占用
docker system df -v | grep -E "BuildKit|Cache"

# 清理所有 BuildKit 缓存（释放磁盘空间）
docker builder prune --filter type=exec.cachemount

# 仅清理超过 30 天未使用的缓存
docker builder prune --filter "until=720h" --filter type=exec.cachemount

# 查看特定 cache mount 的内容（需进入 buildkit 容器）
# 一般不需要，BuildKit 自动管理
```

#### 6. CI 环境注意事项

| CI 平台 | BuildKit 默认 | cache mount 持久化 | 建议配置 |
|---------|:---:|:---:|---------|
| GitHub Actions | ✅ (setup-buildx) | ❌ 每次 VM 全新 | 用 `actions/cache` 备份 `/var/lib/buildkit` 或用 registry cache |
| GitLab CI | 需配置 | ❌ runner 新容器 | 配置 `--cache-to type=registry` |
| Jenkins（持久化 agent） | ✅ | ✅ agent 本地磁盘 | 天然支持，无需额外配置 |
| 本地 Docker Desktop | ✅ | ✅ | 天然支持 |

> **CI 无持久化缓存时**：cache mount 在每次构建中都是冷的，退化为 Method A 的性能水平。此时 B2 仍有「脚本变更不失效包安装层」的优势，但首次下载不可避免。可以使用 BuildKit registry cache（`--cache-to type=registry,ref=myrepo/cache:tag`）实现跨 CI 运行的缓存共享。

#### 7. 关键概念：cache mount 内容不进入镜像

BuildKit `--mount=type=cache` 挂载的目录是**构建时缓存**，其内容**不会**出现在最终镜像中。这意味着：

- `/opt/conda/pkgs` 里已下载/解压的包不会增加镜像体积
- 镜像只包含 `envs/myenv/` 中实际安装的文件（硬链接或拷贝）
- 因此在有 cache mount 的 RUN 中，**不要**用 `conda clean -afy` 激进清理——那只会清掉缓存中下次构建可复用的包，却不能减小镜像
- 正确做法：`conda clean -y -l -q` 仅清理锁文件（防止跨构建残留锁），保留已解压包供下次硬链接复用
- 仅在不使用 BuildKit 的传统构建（无 `--mount=type=cache`）时，才用 `conda clean -afy` 激进清理减小镜像层体积。本仓库提供的三种模板均使用 cache mount，统一使用 `-y -l -q`。

### 常见陷阱

| ❌ 错误做法 | ✅ 正确做法 | 原因 |
|-----------|-----------|------|
| `COPY conda-perf-setup.sh /tmp/` + `RUN bash /tmp/setup.sh` | `--mount=type=bind,source=...,target=/tmp/setup.sh,readonly` | COPY 会使后续层缓存失效 |
| `--mount=type=cache,target=/root/.cache`（合并缓存） | 分别挂载 `conda/` 和 `pip/` | BuildKit exact-path 隔离，合并会导致缓存混杂 |
| `sharing=shared` 安装包 | `sharing=locked` | conda/pip 非并发安全，会损坏包 |
| `conda create` 后 `conda install`（分两步） | 一次 `mamba create` 指定所有包 | 两步 = solver 运行两次，且第二层无法充分利用缓存 |
| `conda install -n base ...` 装包到 base | 创建独立环境 `myenv` | base 环境装包会污染 Miniforge 层，难以缓存 |
| cache mount 下 `conda clean -afy` | `conda clean -y -l -q`（仅锁文件） | -a -f 会清掉 cache mount 中下次构建可复用的已解压包 |
| 在 `mamba create` 前 `COPY . /app` | COPY 放最后 | 代码变更不应触发环境重建 |

## 详细文档

完整集成指南见 [docs/CONDA-PERF-INTEGRATION-GUIDE.md](../../../../docs/CONDA-PERF-INTEGRATION-GUIDE.md)。
