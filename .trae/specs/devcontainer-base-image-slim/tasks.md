# devcontainer-base 镜像瘦身 - Implementation Plan

> **架构变更记录（2026-08-14 更新）**：实际实施方案与原始规划有重要偏差——主Dockerfile已重构为**单镜像集成Miniforge3+Python3.14.6 free-threading(cp314t)+libmamba**（合并了原规划中"base"和"conda"两个镜像层，Conda发行版由 Miniconda3 改为 Miniforge3），Jupyter切换为Lab模式，新增libmamba为默认求解器。变体镜像（conda-llvm/onnx-pytorch/onnx-quantized）需基于新基础镜像重新构建验证。
>
> **应用路径变更**：2026-08-14 apps 目录按类型分组重构，devcontainer-base 路径由 `apps/devcontainer-base/` 变更为 **`apps/docker-images/devcontainer-base/`**。下文所有路径引用均为新路径。
>
> **后续演进（本 spec 之外）**：Task 1-7 完成后，项目继续推进 v2.2（构建流水线优化）与 v2.2.1（Stage 4 conda 性能优化），见本文档末尾「后续演进记录」章节。

## Task 1: 改造主Dockerfile - Miniforge3+Python3.14+libmamba+激进清理 ✅
- **Status**: `completed`
- **Completed**: 2026-08-13
- **Commits**: ceec9c07, 5efd3eac（后经 v2.2 流水线优化迭代）
- **Description**:
  - 修改 [apps/docker-images/devcontainer-base/Dockerfile](file:///d:/spaces/SpecWeave/apps/docker-images/devcontainer-base/Dockerfile)
  - **架构决策**：采用方案B（主镜像直接集成 Miniforge3），移除/opt/venv虚拟环境，Jupyter/Lab/Python全部通过conda管理
  - Python版本升级至**3.14.6**（conda-forge, GCC 14.4.0, free-threading build cp314t）
  - 配置**libmamba**为conda默认求解器（conda 26.3.2, conda-libmamba-solver 26.7.0, libmambapy 2.3.2；v2.2.1 引入 mamba 2.5.0 原生 CLI）
  - conda频道精简为**conda-forge only**（移除defaults频道，Miniforge3原生支持）
  - 实现**9步激进清理**：APT缓存、文档/man/info、Python __pycache__/.pyc、静态库.a/.la、strip二进制符号、conda遥测、locale精简、包缓存、权限修复
  - 构建计时器（BUILD TIMER）输出各阶段耗时
  - /etc/devcontainer-build-info元数据文件
  - 最终阶段内置验证：tini/supervisord/sshd/python/conda/pip/jupyter/docker/podman/entrypoint/healthcheck语法
- **Acceptance Criteria Addressed**: AC-1(partial), AC-3, AC-6, AC-8
- **Test Results**:
  - ✅ 镜像构建成功（v2.2 实测 2.46GB）
  - ✅ /opt/venv已移除
  - ✅ Python 3.14.6 free-threading, conda 26.3.2, libmamba solver正常
  - ✅ 8项深度验证通过（含libmambapy导入、PEP 695泛型语法、free-threading检测）

## Task 2: 配置Jupyter路径切换（notebook→lab） ✅
- **Status**: `completed`
- **Commits**: ceec9c07
- **Description**:
  - 修改 [config/supervisor/conf.d/jupyter.conf](file:///d:/spaces/SpecWeave/apps/docker-images/devcontainer-base/config/supervisor/conf.d/jupyter.conf)
  - command从`jupyter notebook`改为`/opt/conda/bin/jupyter lab`
  - PATH环境变量更新为conda路径
  - VIRTUAL_ENV移除
- **Acceptance Criteria Addressed**: AC-3, AC-4

## Task 3: 增强build.sh构建脚本 ✅
- **Status**: `completed`
- **Commits**: ceec9c07（后经 v2.2 流水线优化扩展）
- **Description**:
  - 修改 [scripts/build.sh](file:///d:/spaces/SpecWeave/apps/docker-images/devcontainer-base/scripts/build.sh)（+306行，后续 v2.2 扩展）
  - **日志持久化**：tee双输出到控制台+`logs/builds/build-<timestamp>.log`
  - **构建前预检（6项）**：Docker运行状态、BuildKit支持、磁盘空间≥10GB、Dockerfile存在性、Miniforge缓存、构建参数摘要
  - **详细构建输出**：`--progress=plain`模式
  - **错误捕获**：trap ERR自动输出日志路径+最后50行日志+排障建议
  - **多镜像源支持**：`--apt-mirror`/`--pip-mirror`/`--docker-mirror`/`--conda-mirror`（aliyun/tuna/official）
  - **网络模式**：`--network-host`解决国内网络问题
  - **v2.2 扩展参数**：`--verify-mode`（standard/fast/off）、`--deep-verify`（numpy/pandas可选深度验证）、`--tag`、`--python-build`（cp314t/cp314）
  - **冒烟测试**：构建后自动启动容器验证7项（Python版本/conda/libmamba/channels/pip/imports/conda-solve）
  - `-r/--registry`参数支持私有仓库前缀
- **Acceptance Criteria Addressed**: AC-1, AC-11
- **Test Results**:
  - ✅ bash语法验证通过
  - ✅ 使用official conda源构建成功（TUNA源连接失败有容错处理）
  - ✅ 7/7冒烟测试通过
  - ✅ v2.2.1 缓存热构建 Stage 4 从 419s→37s

## Task 4: 更新.gitignore ✅
- **Status**: `completed`
- **Commits**: ceec9c07
- **Description**:
  - 新增`.cache/`、`logs/`忽略规则
  - 新增`*.html`、`*report*.json`等构建产物忽略
  - 清理6个历史构建产物文件（benchmark/deployment/verification reports）

## Task 5: 更新README文档 ✅
- **Status**: `completed`
- **Commits**: 5efd3eac
- **Description**:
  - 更新[README.md](file:///d:/spaces/SpecWeave/apps/docker-images/devcontainer-base/README.md)
  - 特性列表更新（venv→Miniforge3+Python3.14+libmamba, Jupyter→JupyterLab）
  - 构建脚本参数文档（多镜像源、--network-host、--test、日志特性、--verify-mode/--deep-verify）
  - 快速开始示例标签更新为conda-libmamba-ft / v2.2-fasttest
  - 基础镜像使用示例补充conda/pip安装
  - 版本信息完整更新（Python 3.14.6, conda 26.3.2, libmambapy 2.3.2, 镜像2.46GB）

## Task 6: 变体镜像适配（conda-llvm/onnx-pytorch/onnx-quantized/ai-dev） ✅
- **Status**: `completed`（Dockerfile/脚本适配完成，运行时构建验证待Task 8）
- **Completed**: 2026-08-13
- **Commits**: 8d7b2d41
- **Depends On**: Task 1
- **Description**:
  - conda变体改为thin layer（不再重复安装Miniforge3，仅配置镜像源+验证conda可用）
  - conda-llvm变体：路径适配/opt/venv→/opt/conda，LLVMDEBUG包跳过（与llvmdev 20冲突），保留strip清理
  - onnx-pytorch/onnx-quantized变体：Python路径全部改为/opt/conda/bin
  - ai-dev变体：Python路径适配，移除/opt/venv引用
  - 所有变体 Dockerfile 采用 `FROM devcontainer-base:${BASE_TAG}` 参数化（conda/conda-llvm/onnx-pytorch/onnx-quantized/ai-dev 依赖链）
  - 所有test-*.sh测试脚本更新路径引用
- **Acceptance Criteria Addressed**: AC-1, AC-5, AC-7
- **Notes**: Python 3.14是非常新的版本（2026-08），PyTorch/ONNX Runtime可能尚未提供3.14 wheel，CI中变体构建标记为experimental(continue-on-error)

## Task 7: CI流水线更新 ✅
- **Status**: `completed`
- **Completed**: 2026-08-13
- **Commits**: 8d7b2d41
- **Depends On**: Task 6
- **Description**:
  - 完全重写[.github/workflows/devcontainer-variants.yml](file:///d:/spaces/SpecWeave/.github/workflows/devcontainer-variants.yml)（770行变更）
  - 架构从5层链式构建改为三job：build-main（主镜像构建+8项深度验证）→ push（条件推送）→ build-variants（实验性）
  - 新增多镜像源矩阵（aliyun/tuna/official），超时15min自动切换fallback
  - lint阶段：bash -n语法检查所有shell脚本+Python3语法检查
  - 主镜像8项深度验证：Python版本/conda版本/libmamba求解器/free-threading检测/PEP695语法/tini/supervisord/sshd
  - 新增free-threading demo脚本测试
  - 镜像推送job支持GitHub Secrets配置（REGISTRY_URL/REGISTRY_USERNAME/REGISTRY_PASSWORD）
  - PR触发lint+build-main(<20min)，main分支推送触发完整流程+推送
  - 变体构建标记为experimental（continue-on-error）
- **Acceptance Criteria Addressed**: AC-1, AC-10

## Task 8: 本地深度验证（变体运行时验证） ⏳
- **Status**: `in-progress`（主镜像验证已完成，变体运行时验证待执行）
- **Priority**: high
- **Depends On**: Task 6
- **Description**:
  - ✅ 主镜像深度验证已完成（v2.2：11项深度验证通过；v2.2.1：构建验证通过，Stage 4 优化验证）
  - ✅ v2.2.1 主镜像构建验证通过：镜像 2.46GB，Python 3.14.6 free-threading（Py_GIL_DISABLED=1），Stage 4 从 419s→37s
  - ✅ C扩展模板容器内验证通过（test-in-docker.sh 在 v2.2-fasttest 容器中：CMake配置/GCC 15.2.0编译/7项自检/8线程×100K压力测试/FT ABI检测全部通过）
  - ⏳ 变体镜像运行时验证待执行：
    - 重新构建所有变体镜像（需PyTorch/ONNX Python 3.14 wheel可用）
    - 验证LLVM工具链（clang/lld/cmake/ninja）
    - 验证PyTorch/ONNX导入（需确认Python 3.14兼容性）
    - 记录所有镜像体积，检查瘦身目标达成情况
    - 端到端服务验证（SSH/Docker DinD/JupyterLab/Podman）
- **Acceptance Criteria Addressed**: AC-2, AC-4, AC-5, AC-7, AC-8
- **Release Artifacts**:
  - RELEASE-v2.md已生成发布说明（含性能基准数据：cp314t 8线程 5.30x加速）
  - examples/free_threading_demo.py已提供并发性能示例（修复检测逻辑，使用sysconfig）
  - CI流水线已修正free-threading检测，新增cp314t环境创建验证
  - CHANGELOG.md 已记录 v2.2-ft 与 v2.2.1-ft 两个版本章节

## Task 9: 独立审查与修正 ⏳
- **Status**: `in-progress`（v2.2 已做部分对抗审查，Task 8 完成后需补充回归审查）
- **Priority**: medium
- **Depends On**: Task 8
- **Description**:
  - v2.2 阶段已完成：V2.2-BUILD-PIPELINE-OPTIMIZATION.md 四视角对抗审查（魔鬼代言人/新人/老板/未来）+ 6项优化 P0/P1/P2 规划
  - 已完成代码审查修复：fix(cext-template) 7078e4c0、fix(cmake-cext) a64fed68、fix(Dockerfile模板缓存挂载冲突) 6f26af4f
  - 待办：Task 8 完成后对变体构建结果做回归对抗审查（四视角：用户/运维/安全/维护）
  - 如有问题修复后重试验证
- **Acceptance Criteria Addressed**: AC-10

---

## 后续演进记录（本 spec 之外，2026-08-14 新增）

> Task 1-7 完成后，项目继续推进了两轮版本迭代（v2.2 / v2.2.1），记录在此供 spec 追溯。此部分工作与原始「瘦身」目标相关但超出原始 Task 范围。

### 后续 V1: v2.2 构建流水线优化（conda-libmamba-ft） ✅
- **Status**: `completed`（P0+P1 全部测试通过）
- **Commits**: 169d036f, 5271ca29, f6e5333b, a9f11263, a64fed68, 7078e4c0, 7333e4b3, 6f26af4f
- **文档**: [V2.2-BUILD-PIPELINE-OPTIMIZATION.md](file:///d:/spaces/SpecWeave/apps/docker-images/devcontainer-base/V2.2-BUILD-PIPELINE-OPTIMIZATION.md)
- **Description**:
  - **P0 核心优化**：Dockerfile 添加 BuildKit `--mount=type=cache`（pip/conda-pkgs/libmamba 三缓存）；verify-cext.sh 参数化重构（--python/--expect-soabi/--json/--deep，11项检测）；ft-benchmark.sh quick模式 500K primes/3.0x 阈值
  - **P1 增强**：--deep-verify 可选 numpy/pandas 深度验证；conda-lock/environment.yml 精确版本锁定（python=3.14.6 cp314t 等）；micromamba 对比实验（结论：无显著优势 2.48GB vs 2.46GB）；templates/cmake-cext C扩展标准模板（CMakeLists.txt + src/ft_extension.c + build.sh + test-in-docker.sh）
  - **P2 探索**：conda-pack 精简评估（未启用，作为后续方向）
  - **验收数据**：冷构建 642s（~10.7min，Stage 4 conda 求解 419s 为瓶颈），镜像 2.46GB，Python 3.14.6 cp314t（Py_GIL_DISABLED=1），C扩展 8线程×100K 原子操作压力测试通过（800,000次无竞态）
  - **文档产出**：docs/PY314T-C-EXTENSION-GUIDE.md（7大关键变化+7大坑+最佳实践）、docs/TECH-ADVISORY-defaults-channel-abi-risk.md

### 后续 V2: v2.2.1 Stage 4 conda 性能优化 ✅
- **Status**: `completed`（构建验证通过，标签 v2.2.1-opt）
- **Commits**: 6a591333, 3256adb9, b84631a0
- **Description**:
  - **三项关键优化**：repodata/execute 线程数 1→8（并行下载/解压）；两次 conda 命令合并为单次 `mamba create`（减少1次solver）；改用 mamba CLI 原生调用（减少 Python 层封装开销）
  - **验收数据**：Stage 4 从 419s→37s（缓存热构建），镜像体积 2.46GB 无增长，C扩展 6项验证通过，free-threading 保持
  - **可复用配置萃取**：Stage 4 配置提取为跨项目共享资产
    - variants/shared/config/condarc/condarc-performant{,-tuna,-aliyun}.yaml（静态模板）
    - variants/shared/scripts/conda-perf-setup.sh（动态脚本，CONDA_MIRROR/CONDA_THREADS/CONDA_TIMEOUT 环境变量参数化 + mamba_create_env source函数）
    - docs/CONDA-PERF-INTEGRATION-GUIDE.md（跨项目快速集成指南）
  - **Dockerfile 重构**：Stage 4 从 ~50行内联 heredoc 改为 3 行脚本调用（BuildKit bind mount 引用脚本，不增加镜像层）

## 交付物清单（更新后）
- ✅ [spec.md](file:///d:/spaces/SpecWeave/.trae/specs/devcontainer-base-image-slim/spec.md) - PRD（已同步 v2.2/v2.2.1 现状）
- ✅ [tasks.md](file:///d:/spaces/SpecWeave/.trae/specs/devcontainer-base-image-slim/tasks.md) - 实施计划（已更新路径与任务状态）
- ✅ [checklist.md](file:///d:/spaces/SpecWeave/.trae/specs/devcontainer-base-image-slim/checklist.md) - 预检清单（已更新）
