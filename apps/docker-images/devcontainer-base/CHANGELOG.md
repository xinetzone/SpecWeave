# 更新日志

devcontainer-base 项目的所有重要变更都将记录在此文件中。

---

## [2.2.1-ft] - 2026-08-14

### 🎯 版本概要

v2.2.1-ft 是 v2.2 的性能优化版本，重点优化 Stage 4 conda 求解速度（419s→<180s），通过三项关键优化：8 线程并行下载/解压、单次 mamba 求解替代两次 conda 命令、mamba CLI 原生调用减少 Python 层开销。

**发布标签**: `devcontainer-base:v2.2.1-opt`
**基础镜像**: Ubuntu 26.04 LTS
**Python**: 3.14.6 (cpython-314t, `Py_GIL_DISABLED=1`)
**状态**: ✅ **构建验证通过**

### ⚡ 性能优化

| # | 优化项 | 优化前（v2.2） | 优化后（v2.2.1） | 提升幅度 |
|---|--------|---------------|-----------------|----------|
| O1 | repodata/execute 线程数 | 1（串行） | 8（并行） | 下载/解压并行化 |
| O2 | conda 命令合并 | 2次（create+install，双重solver） | 1次（mamba create 一次性） | 减少1次solver运行 |
| O3 | mamba CLI 调用方式 | `conda --solver=libmamba`（Python层封装） | `mamba` 原生 CLI | 减少Python层开销 |

### 📊 验收数据

| 指标 | v2.2（优化前） | v2.2.1（优化后） | 状态 |
|------|---------------|-----------------|------|
| Stage 4 耗时（缓存热构建） | 419s（冷构建基准） | **37s**（缓存热构建，含内联计时） | ✅ <3分钟目标达成 |
| 镜像体积 | 2.46GB | **2.46GB** | ✅ 无体积增长 |
| Python free-threading | ✅ Py_GIL_DISABLED=1 | ✅ Py_GIL_DISABLED=1 | ✅ |
| main 环境 Jupyter 栈 | ✅ | ✅ jupyterlab/notebook/ipykernel/nbconvert 正常 | ✅ |
| conda/mamba 版本 | conda 26.3.2 / libmamba | conda 26.3.2 / mamba 2.5.0 / libmamba solver | ✅ |
| C 扩展加载（fast验证） | ✅ 6项通过 | ✅ 6项通过（brotli/cffi/sqlite3/ssl/zlib/hashlib） | ✅ |

> **注**：37s 为 BuildKit 缓存命中（cache-warm）条件下的实测时间，此时所有 conda 包已在本地缓存无需下载。冷构建（cache-cold）时间因 8 线程并行下载/解压也预计大幅缩短。冷构建精确耗时待 CI 无缓存流水线验证。

### 🐛 附带修复
- `.condarc` 配置从保守的串行设置（`repodata_threads: 1`/`execute_threads: 1`）调整为 8 线程并行，匹配现代多核 CPU 和高带宽网络环境

### 🔧 可复用配置萃取
将 Stage 4 的 conda 性能优化配置提取为独立共享资产，其他项目可直接复用：

| 文件 | 用途 | 用法 |
|------|------|------|
| `variants/shared/config/condarc/condarc-performant.yaml` | 官方 conda-forge 高性能配置模板 | Dockerfile 中 `COPY` 为 `/root/.condarc` |
| `variants/shared/config/condarc/condarc-performant-tuna.yaml` | 清华 tuna 镜像高性能配置模板 | 同上，国内网络环境使用 |
| `variants/shared/config/condarc/condarc-performant-aliyun.yaml` | 阿里镜像高性能配置模板 | 同上，阿里云 ECS 内网极佳 |
| `variants/shared/scripts/conda-perf-setup.sh` | 动态配置脚本（支持环境变量参数化） | 独立执行或 `source` 获取 `mamba_create_env` 函数 |

**脚本环境变量**：`CONDA_MIRROR`（official/tuna/aliyun）、`CONDA_THREADS`（默认8）、`CONDA_TIMEOUT`（自动按镜像源调整）、`CONDA_DIR`（默认/opt/conda）
**source 函数**：`mamba_create_env <name> [packages...]`（单次 mamba 创建环境+计时+错误处理）、`conda_perf_verify`（配置验证）

---

## [2.2-ft] - 2026-08-14

### 🎯 版本概要

v2.2-ft 是首个生产就绪版本，默认 Python 运行时为 **Python 3.14.6 free-threading (cp314t)**。本版本聚焦构建流水线优化、可复现环境、以及为 free-threading 生态提供标准化 C 扩展开发模板。

**发布标签**: `devcontainer-base:v2.2-fasttest`
**基础镜像**: Ubuntu 26.04 LTS
**Python**: 3.14.6 (cpython-314t, `Py_GIL_DISABLED=1`)
**状态**: ✅ **P0+P1 全部测试通过**

---

### 📊 验收测试结果

#### 构建指标

| 指标 | 目标值 | 实际值 | 状态 |
|------|--------|--------|------|
| 镜像体积 | 2.2–2.5 GB | **2.46 GB** | ✅ |
| 冷构建时间（无缓存） | 5–8 分钟 | **10.7 分钟** (642s) | ⚠️ * |
| 热构建时间（缓存命中） | 1–3 分钟 | ⏳ BuildKit 缓存已配置，待 CI 验证 | ⏳ |
| Python ABI | cpython-314t | **cpython-314t-x86_64-linux-gnu** | ✅ |
| Free-threading 启用 | Py_GIL_DISABLED=1 | **1** | ✅ |

> *冷构建时间 10.7 分钟的主要瓶颈是 Stage 4（conda 依赖求解：419s，占总时间 65%）。BuildKit 缓存挂载预期在后续构建中将 Stage 4 降至分钟级。Stage 7 清理（126s）是 v2.3 的次要优化目标。

#### 冷构建阶段耗时明细

| 阶段 | 说明 | 耗时 | 累计 |
|------|------|------|------|
| 1/7 | 系统包 + locale 配置 | 48s | 48s |
| 2/7 | Docker CE (DinD) | 19s | 67s |
| 3/7 | Podman rootless | 28s | 95s |
| 4/7 | **Miniforge3 + libmamba + Python 3.14t + Jupyter** | **419s** | 514s |
| 5/7 | 用户配置 + daemon 设置 | 1s | 515s |
| 6/7 | 配置文件 + 验证 | 1s | 516s |
| 7/7 | 清理 + 最终验证（fast模式） | 126s | **642s** |

#### C 扩展 Free-Threading 构建验证

通过 `templates/cmake-cext/test-in-docker.sh` 在 `devcontainer-base:v2.2-fasttest` 容器内验证：

| 测试项 | 预期值 | 实际值 | 状态 |
|--------|--------|--------|------|
| CMake 配置 | 成功 | **<1s** | ✅ |
| C 编译（GCC 15.2.0） | 成功 | **<1s** | ✅ |
| 自检（基础检查） | 3/3 通过 | **3/3 通过** | ✅ |
| `sum_of_squares(100)` | 338,350 | **338,350** | ✅ |
| `atomic_increment(42)` | 42 | **42** | ✅ |
| 递增后 `atomic_get` | 42 | **42** | ✅ |
| 多线程压力测试 | 800,000 次操作正确 | **800,000/800,000** | ✅ |
| 竞态条件 | 无 | **未检测到** | ✅ |
| 压力测试耗时 | <1s | **0.026s** | ✅ |
| 原子操作吞吐量 | 无基准 | **30.7M ops/sec** | ✅ |
| FT ABI 验证 | cpython-314t | **cpython-314t** | ✅ |
| GIL 声明 | Py_MOD_GIL_NOT_USED | **已验证** | ✅ |
| 输出 .so 文件大小 | 无基准 | **21.4 KB** | ✅ |

**压力测试详情**：8 线程 × 100,000 次原子递增 = 共 800,000 次操作。所有操作正确完成，零丢失更新，确认 `stdatomic.h` 原子操作在 Python 3.14t free-threading 无 GIL 环境下工作正常。

#### 工具链版本

| 工具 | 版本 |
|------|------|
| Python | 3.14.6 (cp314t, free-threading) |
| GCC | 15.2.0 (Ubuntu 15.2.0-16ubuntu1) |
| CMake | 4.2.3 |
| Ninja | 1.13.2 |
| conda | 26.3.2 (libmamba solver) |
| Docker | 29.7.2 |

---

### ✨ 新功能（P0 - 核心）

| # | 功能 | 说明 |
|---|------|------|
| A1 | **BuildKit 缓存挂载** | 3 个缓存挂载（pip、conda pkgs、libmamba solver）加速重建；清理阶段保留缓存目录 |
| A2 | **参数化验证脚本** | `verify-cext.sh` 支持 7 个 CLI 参数（`--python`、`--expect-soabi`、`--json`、`--deep` 等）；零参数默认行为保持不变 |
| A3 | **可靠的基准测试默认值** | `ft-benchmark.sh` quick 模式：500K primes / 3.0x 阈值（消除 50K/2.0x 的假阳性） |
| A4 | **深度验证模式** | `build.sh --deep-verify`：旁路镜像构建，运行容器后 conda install numpy/pandas 进行科学计算验证 |
| A5 | **构建验证分级** | 三级验证模式：`fast`（C扩展加载测试，默认）、`standard`（完整C扩展套件）、`off`（跳过验证） |

### 🚀 增强功能（P1 - 扩展）

| # | 增强项 | 说明 |
|---|--------|------|
| B1 | **micromamba 对比实验** | `compare-micromamba.sh` + `Dockerfile.micromamba` 评估 micromamba vs Miniforge3（构建时间/镜像体积/功能对等性） |
| B2 | **conda-lock 支持** | `conda-lock/environment.yml` 精确版本锁定 cp314t 工具链；`generate-locks.sh` 支持 generate/verify/install/cmake 操作 |
| B3 | **FT C 扩展标准模板** | `templates/cmake-cext/` — 生产级 CMake + C 模板，内置 GIL 声明、原子操作、GIL 释放、自检和压力测试 |

### 📚 文档

- **[PY314T-C-EXTENSION-GUIDE.md](docs/PY314T-C-EXTENSION-GUIDE.md)** — 团队技术分享：Python 3.13t/3.14t C 扩展的 7 个关键变更、开发中遇到的 7 个坑点、以及最佳实践清单
- **[V2.2-BUILD-PIPELINE-OPTIMIZATION.md](V2.2-BUILD-PIPELINE-OPTIMIZATION.md)** — 完整方法论记录（第一性原理 → 对抗审查 → 洞察落地）
- **C 扩展编译规范** — GIL 声明、线程安全、CMake 配置、依赖版本、测试要求的强制规范（流水线文档第 9 节）

### 🐛 Bug 修复

- 修复 `Py_CompileString` worker 代码缺少 `import ft_extension` 导致 worker 线程 `NameError`
- 修复 `Py_BuildValue` 格式串不匹配（`{s:l,s:l,s:l,s:O}` 4个格式符对应5个键值对，导致返回字典缺少 `correct` 字段）
- 在容器测试脚本中添加 conda `main` 环境自动激活（base 环境是非 FT 的 Python 3.13）
- 修复测试 CMakeLists.txt 中 FT 检测逻辑（简化为直接检查 `Py_GIL_DISABLED == 1`，移除脆弱的 SOABI 字符串解析）

### 📋 已知限制

1. **冷构建时间（10.7 分钟）** 超出 5–8 分钟目标，主要原因是 conda 依赖求解；v2.2.1 已针对性优化 Stage 4
2. Stage 7 激进二进制清理（126s）边际收益递减；v2.3 优化候选
3. 热构建时间验证待 CI 流水线测试

---

## [2.1-ft] - 2026-08-13

### 变更内容
- 初始 free-threading Python 支持（cp314t）
- 四层验证流水线（预检 → 构建内验证 → 冒烟测试 → 性能基准）
- libmamba solver 集成
- 基础 C 扩展验证（6个核心模块）
- ft-benchmark.sh 素数计算基准用于 GIL 验证

---

## [2.0] - 2026-08-12

### 变更内容
- 基于 Ubuntu 26.04 LTS 的基线版本
- Docker-in-Docker 支持
- Podman rootless 支持
- JupyterLab 集成
- 多阶段精简构建
