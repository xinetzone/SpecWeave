# Chaos AI 可移植Docker镜像优化 - The Implementation Plan

> **实现现状同步（2026-08-11）**：本文档已按 `external/chaos/ai/portable.Dockerfile`（v3.0 多阶段瘦身版）实际实现状态同步。原计划的"8 阶段独立 Ubuntu 构建 + py314 专用环境"演进为"base→deps→final 三阶段瘦身构建 + conda base 环境"。各任务交付物与状态已更新为对应实际实现。

## [x] Task 1: 创建portable.Dockerfile基础框架（多阶段构建）
- **Priority**: high
- **Depends On**: None
- **Description**:
  - 新建 `portable.Dockerfile` 作为独立可移植版本，保留原 `Dockerfile` 不动
  - 基于 `devcontainer-base:onnx-quantized-latest`（Ubuntu 26.04 + conda + LLVM + torch/onnx）自包含构建
  - **三阶段多阶段构建**：`base`（创建 ai 用户+目录+sudo，devuser→ai 重命名）→ `deps`（root 身份安装全部 Python 包）→ `final`（COPY 配置/脚本+运行时配置+元数据+7 项验证）
  - 关键优化：删除对 /opt/conda 的整体 chown（消除 4.6GB 复制层），conda 保持 root:root，ai 通过 sudo 安装包
  - 配置时区 Asia/Shanghai，BuildKit cache mount（apt/conda/pip）
- **Acceptance Criteria Addressed**: AC-1, AC-13, NFR-1, NFR-6
- **Deliverables**: `portable.Dockerfile`（320行, 3阶段构建, v3.0-portable-slim）
- **Notes**: 与最初"8 阶段独立 Ubuntu 构建"设想不同，实现采用 3 阶段瘦身且保留 devcontainer-base 依赖链

## [x] Task 2: 使用conda base环境（Python 3.14+）
- **Priority**: high
- **Depends On**: Task 1
- **Description**:
  - 复用基础镜像自带的 Miniconda base 环境（Python 3.14.4），不再创建独立 py314 环境
  - 配置 pip 镜像源（aliyun/tuna，通过 PIP_MIRROR 参数）
  - 配置 conda base 默认激活（conda-init.sh 写入 /etc/profile.d/）
  - 配置 pip 镜像源与 PIP_USER：deps 阶段 `PIP_USER=0`（包写入 /opt/conda），final 阶段恢复 `PIP_USER=1`
  - 设置 /opt/conda 保持 root:root 属主（ai 通过 sudo 安装）
- **Acceptance Criteria Addressed**: AC-4, AC-9, AC-10, FR-3, FR-13
- **Deliverables**: Stage 1(base) + Stage 2(deps) 中的 conda 配置
- **Notes**: 与最初"创建 py314 专用环境"设想不同，实现采用 base 环境（LLVM 工具链已在 base PATH 中）

## [x] Task 3: 安装LLVM/CMake/Ninja等NPU构建工具链
- **Priority**: high
- **Depends On**: Task 2
- **Description**:
  - 复用基础镜像预装的 LLVM/Clang 22.1.8、CMake ≥4.4、Ninja 1.13.2 工具链（在 base PATH 中）
  - 安装 XMNN 构建相关Python包到 base 环境：scikit-build-core、nuitka、invoke、build、decorator、attrs、cloudpickle、typing_extensions、pytest、psutil 等
  - 预装 ML/NLP 生态包：transformers、sentence-transformers、datasets、pyarrow、fastapi、numba、librosa 等
  - 验证工具版本符合要求
- **Acceptance Criteria Addressed**: FR-10
- **Deliverables**: Stage 2(deps) 的 pip install 列表 + Stage 3(final) 版本验证

## [x] Task 4: 创建ai用户并配置权限
- **Priority**: high
- **Depends On**: Task 1, Task 2
- **Description**:
  - 在 Stage 1(base) 复用基础镜像 devuser(UID 1001)，重命名为 ai（`usermod -l ai devuser`），支持 AI_UID/AI_GID 配置
  - 配置 ai 用户 home 目录 /home/ai，加入 docker、sudo 组
  - 根据 GRANT_SUDO 参数决定是否添加 sudo 免密（默认 yes）
  - **/opt/conda 保持 root:root**（ai 通过 sudo pip/conda 安装，不直接写 conda）
  - 预创建 /workspace 子目录：npu_tvm、npuusertools、models、project，属主 ai:ai
  - 配置默认 umask 0027（写入 /etc/profile、/etc/bash.bashrc、ai 用户.bashrc）
- **Acceptance Criteria Addressed**: AC-2, AC-3, AC-8, FR-2, FR-5, FR-6, FR-9
- **Deliverables**: Stage 1(base) 用户创建 + Stage 3(final) umask 配置
- **Notes**: 与最初"AI_UID/AI_GID 默认 1000:1000、conda 属主 ai:ai"设想不同，实现默认 1001:1001 且 conda 保持 root:root

## [x] Task 5: 配置多入口环境一致性（Shell/SSH/Jupyter）
- **Priority**: high
- **Depends On**: Task 2, Task 4
- **Description**:
  - 编写 /etc/profile.d/conda-init.sh：登录 shell 自动激活 base 环境
  - 配置 sshd：禁止 root 登录（PermitRootLogin no）、PermitUserEnvironment yes（SSH 非交互环境加载）
  - 编写 ssh 环境文件 /home/ai/.ssh/environment（PATH 优先 /opt/conda/bin + CONDA_DEFAULT_ENV=base）
  - Jupyter 使用 /opt/conda/bin/python（kernel.json PATH 优先 /opt/conda/bin），设置 PYTHONPATH/LD_LIBRARY_PATH
  - 移除对 /opt/venv 的依赖（统一 base 环境）
  - 配置 supervisord 管理 sshd、dockerd、jupyter 服务
  - 适配 chaos-ai-init.sh 逻辑到 profile.d 脚本
- **Acceptance Criteria Addressed**: AC-5, AC-6, AC-7, AC-11, FR-4, FR-8, FR-11, FR-14
- **Deliverables**:
  - `config/profile/conda-init.sh`
  - `config/ssh/sshd_config`
  - `config/jupyter/jupyter_notebook_config.py`
  - `config/jupyter/kernels/npu/kernel.json`
  - `config/supervisor/`（主配置+conf.d 子目录）

## [x] Task 6: 创建fix-permissions.sh和文档
- **Priority**: medium
- **Depends On**: Task 4
- **Description**:
  - 编写 /opt/bin/fix-permissions.sh 脚本，用于调整挂载卷权限（将 /workspace 下挂载目录权限调整为 ai 用户可访问）
  - 脚本支持指定目标目录、dry-run(-d)、verbose(-v)、quiet(-q) 模式，含前后状态扫描、变更对比、验证阶段、彩色诊断日志
  - 创建 /opt/docs/conda-environment-guide.md，说明如何管理 conda 环境、安装包（sudo pip/sudo conda/pip --user）、创建新环境
  - 写入 build metadata 到 /etc/chaos-ai-portable-build-info（版本/路径/镜像源/PIP_USER 等）
- **Acceptance Criteria Addressed**: FR-7, FR-12
- **Deliverables**:
  - `scripts/fix-permissions.sh`（438行, 含详细日志/dry-run/verbose/前后对比）
  - `docs/portable/conda-environment-guide.md`
  - Stage 3(final) build-info 生成

## [x] Task 7: 配置Docker-in-Docker和服务管理
- **Priority**: medium
- **Depends On**: Task 4, Task 5
- **Description**:
  - 复用基础镜像预装 Docker CE（支持 DinD）
  - 配置 daemon.json（含国内镜像加速）
  - 配置 supervisord 启动 sshd、dockerd、jupyter
  - 编写 start.sh 启动脚本，支持 DooD/DinD 自动检测（检测 /var/run/docker.sock），含 7 阶段诊断启动、ERR trap、步骤计时、彩色日志、二进制预检、挂载诊断
  - ENTRYPOINT 为空数组，CMD 默认启动 start.sh（内部 exec supervisord），允许用户覆盖 CMD
- **Acceptance Criteria Addressed**: NFR-2, FR-14
- **Deliverables**:
  - `config/docker/daemon.json`
  - `config/supervisor/conf.d/`（sshd.conf/dockerd.conf/jupyter.conf）
  - `scripts/start.sh`（529行, 7阶段诊断启动/DooD-DinD自动检测/ERR trap）
  - ENTRYPOINT=[], CMD=["/usr/local/bin/start.sh"]

## [x] Task 8: 设置运行时配置和最终清理
- **Priority**: high
- **Depends On**: Task 4, Task 5, Task 6, Task 7
- **Description**:
  - 运行时以 ai 用户执行服务（start.sh 以 ai 用户启动 supervisord 子服务）
  - 设置 WORKDIR /workspace
  - 配置 ENV PATH 确保 /opt/conda/bin 优先
  - 清理 apt 缓存、conda 缓存、pip 缓存、/tmp 文件
  - 运行冒烟测试（Stage 3 final 7 项验证：sshd 语法/supervisord/python/LLVM/CMake+Ninja/Docker+ML包/user+scripts）
  - 设置 CMD 默认启动 start.sh
  - Dockerfile 最终阶段输出构建信息和使用提示
- **Acceptance Criteria Addressed**: AC-2, NFR-1
- **Deliverables**: Stage 3(final) validation（7 项检查）+ WORKDIR/ENV/EXPOSE/CMD

## [x] Task 9: 端到端验证测试
- **Priority**: high
- **Depends On**: Task 8
- **Description**:
  - 通过 `chaos-ai-portable-image-slim` 流程完成多阶段瘦身构建与验证（2026-08-11 实测）
  - 验证独立构建（基于基础镜像链）
  - 验证默认非root运行（ai 用户）
  - 验证 UID/GID 自定义构建（AI_UID/AI_GID 1001）
  - 验证 SSH/Jupyter/CMD 三环境一致性（base 环境）
  - 验证 umask 权限保护（0027）
  - 验证 conda 环境创建和包安装（sudo pip 安装 + conda create 新环境）
  - 验证 NPU 工具链挂载兼容（PYTHONPATH）
  - 验证服务健康（sshd/dockerd/jupyter 均 RUNNING）
- **Acceptance Criteria Addressed**: AC-1~AC-13
- **Status**: **已完成**（2026-08-11 实测：镜像 9.59GB，Python 3.14.4，LLVM 22.1.8，CMake 4.4.2，Ninja 1.13.2，sshd/dockerd/jupyter 均 RUNNING，容器 healthy；docker-cache 缓存 2.0GB tar.gz 已保存）
