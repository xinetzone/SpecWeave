# devcontainer-base 镜像瘦身 - Implementation Plan

> **架构变更记录**：实际实施方案与原始规划有重要偏差——主Dockerfile已重构为**单镜像集成Miniconda3+Python3.14+libmamba**（合并了原规划中"base"和"conda"两个镜像层），Jupyter切换为Lab模式，新增libmamba为默认求解器。变体镜像（conda-llvm/onnx-pytorch/onnx-quantized）需后续基于新基础镜像重新构建。

## Task 1: 改造主Dockerfile - Miniconda3+Python3.14+libmamba+激进清理 ✅
- **Status**: `completed`
- **Completed**: 2026-08-13
- **Commits**: ceec9c07, 5efd3eac
- **Description**:
  - 修改 [apps/devcontainer-base/Dockerfile](file:///d:/spaces/SpecWeave/apps/devcontainer-base/Dockerfile)
  - **架构决策**：采用方案B（主镜像直接集成Miniconda3），移除/opt/venv虚拟环境，Jupyter/Lab/Python全部通过conda管理
  - Python版本升级至**3.14.6**（conda-forge, GCC 14.4.0, free-threading build）
  - 配置**libmamba**为conda默认求解器（conda-libmamba-solver 26.7.0, libmambapy 2.3.2）
  - conda频道精简为**conda-forge only**（移除defaults频道）
  - 实现**9步激进清理**：APT缓存、文档/man/info、Python __pycache__/.pyc、静态库.a/.la、strip二进制符号、conda遥测、locale精简、包缓存、权限修复
  - 构建计时器（BUILD TIMER）输出各阶段耗时
  - /etc/devcontainer-build-info元数据文件
  - 最终阶段内置验证：tini/supervisord/sshd/python/conda/pip/jupyter/docker/podman/entrypoint/healthcheck语法
- **Acceptance Criteria Addressed**: AC-1(partial), AC-3, AC-6, AC-8
- **Test Results**:
  - ✅ 镜像构建成功（2.38GB）
  - ✅ /opt/venv已移除
  - ✅ Python 3.14.6, conda 26.7.0, libmamba solver正常
  - ✅ 8项深度验证通过（含libmambapy导入、PEP 695泛型语法、free-threading检测）

## Task 2: 配置Jupyter路径切换（notebook→lab） ✅
- **Status**: `completed`
- **Commits**: ceec9c07
- **Description**:
  - 修改 [config/supervisor/conf.d/jupyter.conf](file:///d:/spaces/SpecWeave/apps/devcontainer-base/config/supervisor/conf.d/jupyter.conf)
  - command从`jupyter notebook`改为`/opt/conda/bin/jupyter lab`
  - PATH环境变量更新为conda路径
  - VIRTUAL_ENV移除
- **Acceptance Criteria Addressed**: AC-3, AC-4

## Task 3: 增强build.sh构建脚本 ✅
- **Status**: `completed`
- **Commits**: ceec9c07
- **Description**:
  - 修改 [scripts/build.sh](file:///d:/spaces/SpecWeave/apps/devcontainer-base/scripts/build.sh)（+306行）
  - **日志持久化**：tee双输出到控制台+`logs/builds/build-<timestamp>.log`
  - **构建前预检（6项）**：Docker运行状态、BuildKit支持、磁盘空间≥10GB、Dockerfile存在性、Miniconda缓存、构建参数摘要
  - **详细构建输出**：`--progress=plain`模式
  - **错误捕获**：trap ERR自动输出日志路径+最后50行日志+排障建议
  - **多镜像源支持**：`--apt-mirror`/`--pip-mirror`/`--docker-mirror`/`--conda-mirror`（aliyun/tuna/official）
  - **网络模式**：`--network-host`解决国内网络问题
  - **冒烟测试**：构建后自动启动容器验证7项（Python版本/conda/libmamba/channels/pip/imports/conda-solve）
  - `-r/--registry`参数支持私有仓库前缀
- **Acceptance Criteria Addressed**: AC-1
- **Test Results**:
  - ✅ bash语法验证通过
  - ✅ 使用official conda源构建成功（TUNA源连接失败有容错处理）
  - ✅ 7/7冒烟测试通过

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
  - 更新[README.md](file:///d:/spaces/SpecWeave/apps/devcontainer-base/README.md)
  - 特性列表更新（venv→Miniconda+Python3.14+libmamba, Jupyter→JupyterLab）
  - 构建脚本参数文档（多镜像源、--network-host、--test、日志特性）
  - 快速开始示例标签更新为conda-libmamba-v2
  - 基础镜像使用示例补充conda/pip安装
  - 版本信息完整更新（Python 3.14.6, conda 26.7.0, libmambapy 2.3.2, 镜像2.38GB）

## Task 6: 变体镜像适配（conda-llvm/onnx-pytorch/onnx-quantized/ai-dev） ✅
- **Status**: `completed` (Dockerfile/脚本适配完成，运行时构建验证待Task 8)
- **Completed**: 2026-08-13
- **Commits**: 8d7b2d41
- **Depends On**: Task 1
- **Description**:
  - conda变体改为thin layer（不再重复安装Miniconda，仅配置镜像源+验证conda可用）
  - conda-llvm变体：路径适配/opt/venv→/opt/conda，LLVMDEBUG包跳过（与llvmdev 20冲突），保留strip清理
  - onnx-pytorch/onnx-quantized变体：Python路径全部改为/opt/conda/bin
  - ai-dev变体：Python路径适配，移除/opt/venv引用
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
- **Status**: `pending`
- **Priority**: high
- **Depends On**: Task 6
- **Description**:
  - ✅ 主镜像深度验证已完成（8项全部通过，见Task 1）
  - ⏳ 变体镜像运行时验证待执行：
    - 重新构建所有变体镜像（需PyTorch/ONNX Python 3.14 wheel可用）
    - 验证LLVM工具链（clang/lld/cmake/ninja）
    - 验证PyTorch/ONNX导入（需确认Python 3.14兼容性）
    - 记录所有镜像体积，检查瘦身目标达成情况
    - 端到端服务验证（SSH/Docker DinD/JupyterLab/Podman）
- **Acceptance Criteria Addressed**: AC-2, AC-4, AC-5, AC-7, AC-8
- **Release Artifacts**:
  - RELEASE-v2.md已生成发布说明（含性能基准数据：cp314t 8线程4.98x加速）
  - examples/free_threading_demo.py已提供并发性能示例（修复检测逻辑，使用sysconfig）
  - CI流水线已修正free-threading检测，新增cp314t环境创建验证

## Task 9: 独立审查与修正 ⏳
- **Status**: `pending`
- **Priority**: medium
- **Depends On**: Task 8
- **Description**:
  - 对抗性审查四视角：用户视角、运维视角、安全视角、维护视角
  - 如有问题修复后重试验证
- **Acceptance Criteria Addressed**: AC-10
