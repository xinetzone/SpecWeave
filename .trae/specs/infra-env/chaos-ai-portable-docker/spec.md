# Chaos AI 可移植Docker镜像优化 - Product Requirement Document

> **实现现状同步（2026-08-11）**：本文档已按 `external/chaos/ai/portable.Dockerfile`（v3.0 多阶段瘦身版）的实际实现状态同步。与最初设想相比，实现发生了若干方向性演进（基础镜像保留 devcontainer-base 依赖链、默认 conda 环境从 py314 改为 base、构建阶段从 8 阶段简化为 3 阶段、ai 用户默认 UID/GID 从 1000 改为 1001、conda 属主从 ai:ai 改为 root:root）。以下各章节均已改为反映实际实现。

## Overview
- **Summary**: 重构 `external/chaos/ai/Dockerfile` 为独立可移植的Docker镜像（`portable.Dockerfile`），解决当前镜像依赖六层基础镜像链、固定UID权限问题、root运行风险、双环境混淆、缺少挂载权限保护等问题，实现跨宿主机兼容、非root安全运行、conda环境统一管理、多入口环境一致性的生产级AI开发容器。实现采用 **多阶段瘦身（base→deps→final）** 结构，基于 `devcontainer-base:onnx-quantized-latest` 自包含构建，镜像从 15.6GB 精简至 ~9.59GB。
- **Purpose**: 当前镜像设计为内部开发变体层，无法独立分发；在不同宿主机环境中可能出现权限映射问题、环境不一致、安全风险；需要一个自包含、可移植、安全且环境一致的AI开发容器镜像。
- **Target Users**: AI算法工程师、NPU工具链开发者、需要在任意标准Docker环境中部署Chaos AI开发环境的用户。

## Goals
- 构建自包含独立镜像，在任意标准Docker环境运行（**注**：实现基于 `devcontainer-base:onnx-quantized-latest` 基础镜像链自包含构建，未做到脱离该基础镜像链）
- 实现非root用户安全运行，创建"ai"作为默认用户，支持构建时配置UID/GID（默认 1001:1001，复用基础镜像 devuser）
- 使用 conda **base** 环境（Python 3.14+，含 LLVM 22.1.8 工具链）作为默认Python环境，统一包安装位置，消除 /opt/venv 双环境混淆
- 统一SSH/命令行/Jupyter三入口的环境激活，保证包管理一致性
- 配置umask和挂载点权限保护，防止宿主机文件权限被意外修改
- 精简镜像体积：多阶段构建重组 + 消除 conda chown 复制层，镜像从 15.6GB → ~9.59GB（降幅 38.5%）
- 提供清晰的环境管理使用文档

## Non-Goals (Out of Scope)
- 不修改xmnn-whl-builder、xmnn-runtime等下游镜像（后续可基于新镜像重构，本次不涉及）
- 不改动NPU工具链源码（npuusertools/npu_tvm通过volume挂载保持不变）
- 不迁移所有历史镜像构建链，本次Dockerfile是独立可选项
- 不实现Docker-in-Docker的rootless模式（保持现有DinD能力，并支持DooD/DinD自动检测）
- 不删除现有devuser相关逻辑（保持向后兼容，新镜像将devuser重命名为ai用户）
- 不实现完全脱离 devcontainer-base 基础镜像链的独立 Ubuntu 构建（当前实现仍依赖该链）

## Background & Context
- 当前Dockerfile基于 `devcontainer-base:onnx-quantized-latest`，需要先构建六层镜像链才能使用；`portable.Dockerfile` 在该基础镜像上自包含构建，不依赖额外本地镜像
- 当前使用devuser(UID 1000)固定UID，在宿主机UID不是1000时会导致挂载文件权限问题；portable 镜像改用 ai 用户（默认 UID/GID 1001:1001，构建时可配置 AI_UID/AI_GID）
- 当前包安装在conda base环境，同时存在/opt/venv双环境，可能导致用户在不同入口安装包位置不一致
- 当前没有umask配置，容器内进程创建的文件默认权限可能过于开放
- 当前镜像以root构建，USER指令未明确设置，存在以root运行容器的安全风险
- 项目硬性约束：Python ≥ 3.14、conda环境、LLVM/CMake/Ninja工具链、支持NPU工具链挂载
- **多阶段瘦身演进（2026-08-11）**：原单阶段构建对 /opt/conda 整体执行 `chown -R ai:ai`，产生 4.6GB 复制层导致镜像膨胀至 15.6GB；重构为 base→deps→final 三阶段，conda 保持 root:root，ai 用户通过 `sudo pip`/`sudo conda` 安装包，镜像精简至 ~9.59GB

## Functional Requirements
- **FR-1**: 镜像基于 `devcontainer-base:onnx-quantized-latest`（Ubuntu 26.04 + Miniconda base + LLVM 22.1.8 + torch/onnx/onnxruntime）自包含构建，采用 base→deps→final 三阶段多阶段构建
- **FR-2**: 创建名为"ai"的非root用户，支持构建参数 `AI_UID`/`AI_GID` 配置UID/GID（默认1001:1001，复用基础镜像 devuser 并重命名为 ai）
- **FR-3**: conda **base** 环境（Python 3.14+）作为默认Python环境，预装 LLVM/Clang 22.1.8、CMake ≥4.4、Ninja 1.13.2 工具链
- **FR-4**: 所有系统用户入口（login shell、ssh non-interactive、Jupyter kernel）默认激活 base 环境，`which python` 指向 `/opt/conda/bin/python`
- **FR-5**: 配置默认umask为0027，新创建文件默认权限为750/640
- **FR-6**: 预创建/workspace挂载点目录并设置ai用户所有权（npu_tvm、npuusertools、models、project）
- **FR-7**: 提供fix-permissions.sh辅助脚本，用于启动时调整挂载卷权限（支持 dry-run/verbose/quiet）
- **FR-8**: 配置sshd禁止root用户登录（PermitRootLogin no）
- **FR-9**: 支持构建参数 `GRANT_SUDO` 控制是否给ai用户sudo权限（默认yes用于开发环境）
- **FR-10**: 预装必要的系统工具和Python包（LLVM/CMake/Ninja、build工具链、scikit-build-core/nuitka、Jupyter等）
- **FR-11**: 保留chaos-ai-init.sh的PYTHONPATH自动配置逻辑适配挂载的NPU工具链
- **FR-12**: 提供环境管理使用说明文档（在容器内 /opt/docs/conda-environment-guide.md）
- **FR-13**: conda 属主保持 root:root，ai 用户通过 `sudo pip install`/`sudo conda install` 安装包（PIP_USER 构建期=0 写入 /opt/conda，运行期=1 支持 `pip install --user`）
- **FR-14**: 服务由 supervisord 托管（sshd/dockerd/jupyter），start.sh 支持 DooD/DinD 自动检测，ENTRYPOINT 为空数组允许覆盖 CMD

## Non-Functional Requirements
- **NFR-1**: 镜像构建时间合理（利用BuildKit缓存，复用apt/conda/pip缓存）
- **NFR-2**: 跨宿主机兼容性：在任意标准Docker 20.10+环境可运行，不依赖特定宿主机配置
- **NFR-3**: 安全性：默认不以root运行，遵循最小权限原则
- **NFR-4**: 环境一致性：SSH/CMD/Jupyter中 `which python` 和 `pip install` 目标一致
- **NFR-5**: 可维护性：Dockerfile分层清晰，注释明确，关键配置可通过构建参数调整
- **NFR-6**: 镜像体积精简：通过多阶段构建与消除 chown 复制层，镜像 ≤ ~10GB（对比原 15.6GB，降幅 ≥35%）

## Constraints
- **Technical**:
  - 必须使用Dockerfile 1.7-labs语法（支持here-document和cache mount）
  - 基础镜像使用 `devcontainer-base:onnx-quantized-latest`（Ubuntu 26.04 + conda + LLVM + torch/onnx）
  - 国内镜像源支持（通过 APT_MIRROR/CONDA_MIRROR/PIP_MIRROR 构建参数，默认 aliyun/bfsu/aliyun）
  - Python版本必须3.14+
  - 必须包含LLVM 22.1.8、CMake ≥4.4.0、Ninja 1.13.2
  - 保留时区配置Asia/Shanghai
  - deps 阶段 `ENV PIP_USER=0`（包写入 /opt/conda，root 属主全局可读），final 阶段恢复 `ENV PIP_USER=1`
  - conda 保持 root:root 属主，禁止对 /opt/conda 整体 chown（避免 4.6GB 复制层）
- **Business**: 保持与现有docker-compose.yml和运行方式兼容（镜像 tag 为 `chaos-ai:portable-slim`）
- **Dependencies**: devcontainer-base:onnx-quantized-latest 基础镜像、Miniconda、apt包管理器、pip

## Assumptions
- 用户使用Docker 20.10+版本支持BuildKit
- 开发环境需要sudo权限安装系统包（GRANT_SUDO=yes）
- NPU工具链仍通过volume挂载到/workspace下，不打包进镜像
- Jupyter使用conda base环境内的ipykernel，无需单独/opt/venv
- ai 用户通过 sudo 安装 conda 级包，无需直接写 conda 目录

## Acceptance Criteria

### AC-1: 镜像可基于基础镜像链构建
- **Given**: 已具备 `devcontainer-base:onnx-quantized-latest` 基础镜像的机器
- **When**: 执行 `docker build -f portable.Dockerfile -t chaos-ai:portable-slim .` 在external/chaos/ai目录
- **Then**: 构建成功完成，生成可运行镜像
- **Verification**: `programmatic`（已实测通过，2026-08-11）

### AC-2: 默认以非root用户ai运行
- **Given**: 使用构建好的镜像启动容器
- **When**: 执行 `docker run --rm chaos-ai:portable-slim whoami`
- **Then**: 输出 `ai`，不是root
- **Verification**: `programmatic`

### AC-3: UID/GID可配置
- **Given**: 构建时指定 `--build-arg AI_UID=1001 --build-arg AI_GID=1001`
- **When**: 启动容器执行 `id -u ai && id -g ai`
- **Then**: 输出 `1001` 和 `1001`
- **Verification**: `programmatic`

### AC-4: 默认激活base conda环境
- **Given**: 容器正常启动
- **When**: 在交互式bash中执行 `echo $CONDA_DEFAULT_ENV && python --version`
- **Then**: 输出 `base` 和 Python 3.14.x版本
- **Verification**: `programmatic`

### AC-5: SSH登录环境一致
- **Given**: 容器启动sshd服务，使用ai用户通过ssh登录
- **When**: 执行 `which python && pip --version`
- **Then**: python路径指向 `/opt/conda/bin/python`，pip使用base环境的pip
- **Verification**: `programmatic`

### AC-6: Jupyter使用base环境
- **Given**: 容器启动Jupyter服务
- **When**: 在Jupyter notebook中执行 `import sys; print(sys.executable)`
- **Then**: 输出路径为 `/opt/conda/bin/python`
- **Verification**: `programmatic`

### AC-7: 禁止root SSH登录
- **Given**: 容器sshd配置完成
- **When**: 检查sshd_config配置或尝试root ssh登录
- **Then**: PermitRootLogin no，root无法通过ssh登录
- **Verification**: `programmatic`

### AC-8: umask权限保护
- **Given**: 容器以ai用户登录
- **When**: 执行 `umask` 并创建新文件 `touch /workspace/testfile && ls -l /workspace/testfile`
- **Then**: umask输出0027，文件权限为 `-rw-r-----`（640）
- **Verification**: `programmatic`

### AC-9: pip安装到conda环境
- **Given**: base环境已激活
- **When**: 执行 `sudo pip install requests` 后 `python -c "import requests; print(requests.__file__)"`
- **Then**: requests包安装在 `/opt/conda/lib/python3.14/site-packages/` 下
- **Verification**: `programmatic`

### AC-10: 跨环境conda创建正常
- **Given**: base环境激活
- **When**: 执行 `conda create -n testenv python=3.12 -y && conda activate testenv && python --version`
- **Then**: 成功创建testenv环境，Python版本为3.12.x，环境切换正常
- **Verification**: `programmatic`

### AC-11: NPU工具链挂载兼容
- **Given**: 启动容器时挂载npuusertools和npu_tvm到/workspace
- **When**: 登录容器检查PYTHONPATH
- **Then**: PYTHONPATH包含挂载的npuusertools和npu_tvm/python路径
- **Verification**: `programmatic`

### AC-12: Dockerfile结构清晰可维护
- **Given**: 完成的portable.Dockerfile
- **When**: 人工审查Dockerfile
- **Then**: 分层清晰（base→deps→final三阶段），有关键注释，构建参数明确，使用BuildKit cache
- **Verification**: `human-judgment`

### AC-13: 镜像体积精简
- **Given**: 完成多阶段瘦身构建
- **When**: 执行 `docker images chaos-ai:portable-slim`
- **Then**: 镜像大小 ≤ ~10GB（实测 9.59GB，相比原 15.6GB 降幅 38.5%）
- **Verification**: `programmatic`（已实测通过，2026-08-11）

## Open Questions (Resolved)
- [x] 是否需要完全移除/opt/venv还是保留兼容？→ **统一使用 conda base 环境**，镜像内不再依赖 /opt/venv（PATH 中残留引用无害，实际不创建/不使用）
- [x] fix-permissions.sh是否需要在entrypoint自动执行还是用户手动调用？→ **用户手动调用**，提供脚本+文档说明，启动脚本不自动修改挂载卷权限（避免破坏宿主机文件）
- [x] 国内镜像源默认值是使用官方源还是默认国内源？→ **默认国内源**：APT_MIRROR=aliyun, CONDA_MIRROR=bfsu, PIP_MIRROR=aliyun，与原项目一致
- [x] 默认conda环境是专用 py314 还是 base？→ **base**（Python 3.14.4）。实现采用基础镜像自带的 base 环境，不再创建独立 py314 环境（LLVM 工具链已在 base PATH 中）
- [x] conda 属主与包安装方式？→ **conda 保持 root:root**，ai 用户通过 `sudo pip`/`sudo conda` 安装；配合 PIP_USER 构建期/运行期切换
- [x] ai 用户默认 UID/GID？→ **1001:1001**（复用基础镜像 devuser UID 1001，构建时可配置 AI_UID/AI_GID）
