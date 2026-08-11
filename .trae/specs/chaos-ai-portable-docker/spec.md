# Chaos AI 可移植Docker镜像优化 - Product Requirement Document

## Overview
- **Summary**: 重构 `external/chaos/ai/Dockerfile` 为独立可移植的Docker镜像，解决当前镜像依赖六层基础镜像链、固定UID权限问题、root运行风险、双环境混淆、缺少挂载权限保护等问题，实现跨宿主机兼容、非root安全运行、conda环境统一管理、多入口环境一致性的生产级AI开发容器。
- **Purpose**: 当前镜像设计为内部开发变体层，无法独立分发；在不同宿主机环境中可能出现权限映射问题、环境不一致、安全风险；需要一个自包含、可移植、安全且环境一致的AI开发容器镜像。
- **Target Users**: AI算法工程师、NPU工具链开发者、需要在任意标准Docker环境中部署Chaos AI开发环境的用户。

## Goals
- 构建自包含独立镜像，不依赖外部基础镜像链，可在任意标准Docker环境运行
- 实现非root用户安全运行，创建"ai"作为默认用户，支持构建时配置UID/GID
- 创建专用py314 conda环境作为默认Python环境，确保包安装隔离
- 统一SSH/命令行/Jupyter三入口的环境激活，保证包管理一致性
- 配置umask和挂载点权限保护，防止宿主机文件权限被意外修改
- 提供清晰的环境管理使用文档
- 保持与现有NPU工具链挂载逻辑兼容

## Non-Goals (Out of Scope)
- 不修改xmnn-whl-builder、xmnn-runtime等下游镜像（后续可基于新镜像重构，本次不涉及）
- 不改动NPU工具链源码（npuusertools/npu_tvm通过volume挂载保持不变）
- 不迁移所有历史镜像构建链，本次Dockerfile是独立可选项
- 不实现Docker-in-Docker的rootless模式（保持现有DinD能力）
- 不删除现有devuser相关逻辑（保持向后兼容，新镜像使用ai用户）

## Background & Context
- 当前Dockerfile基于 `devcontainer-base:onnx-quantized-${BASE_TAG}`，需要先构建六层镜像链才能使用
- 当前使用devuser(UID 1000)固定UID，在宿主机UID不是1000时会导致挂载文件权限问题
- 当前包安装在conda base环境，同时存在/opt/venv双环境，可能导致用户在不同入口安装包位置不一致
- 当前没有umask配置，容器内进程创建的文件默认权限可能过于开放
- 当前镜像以root构建，USER指令未明确设置，存在以root运行容器的安全风险
- 项目硬性约束：Python ≥ 3.14、conda环境、LLVM/CMake/Ninja工具链、支持NPU工具链挂载

## Functional Requirements
- **FR-1**: 镜像基于Ubuntu 26.04官方基础镜像，所有依赖在Dockerfile内自包含安装，可独立构建
- **FR-2**: 创建名为"ai"的非root用户，支持构建参数 `AI_UID`/`AI_GID` 配置UID/GID（默认1000:1000）
- **FR-3**: 预装Miniconda，创建名为py314的专用conda环境（Python 3.14+）并设为默认激活环境
- **FR-4**: 所有系统用户入口（login shell、ssh non-interactive、Jupyter kernel）默认激活py314环境
- **FR-5**: 配置默认umask为0027，新创建文件默认权限为750/640
- **FR-6**: 预创建/workspace挂载点目录并设置ai用户所有权
- **FR-7**: 提供fix-permissions.sh辅助脚本，用于启动时调整挂载卷权限
- **FR-8**: 配置sshd禁止root用户登录
- **FR-9**: 支持构建参数 `GRANT_SUDO` 控制是否给ai用户sudo权限（默认yes用于开发环境）
- **FR-10**: 预装必要的系统工具和Python包（LLVM/CMake/Ninja、build工具链、Jupyter等）
- **FR-11**: 保留chaos-ai-init.sh的PYTHONPATH自动配置逻辑适配挂载的NPU工具链
- **FR-12**: 提供环境管理使用说明文档（在容器内 /opt/docs/ 或构建注释中）

## Non-Functional Requirements
- **NFR-1**: 镜像构建时间合理（利用BuildKit缓存，复用apt/conda/pip缓存）
- **NFR-2**: 跨宿主机兼容性：在任意标准Docker 20.10+环境可运行，不依赖特定宿主机配置
- **NFR-3**: 安全性：默认不以root运行，遵循最小权限原则
- **NFR-4**: 环境一致性：SSH/CMD/Jupyter中 `which python` 和 `pip install` 目标一致
- **NFR-5**: 可维护性：Dockerfile分层清晰，注释明确，关键配置可通过构建参数调整

## Constraints
- **Technical**:
  - 必须使用Dockerfile 1.7-labs语法（支持here-document和cache mount）
  - 基础镜像使用Ubuntu 26.04
  - 国内镜像源支持（通过APT_MIRROR/CONDA_MIRROR/PIP_MIRROR构建参数）
  - Python版本必须3.14+
  - 必须包含LLVM 22.1.8、CMake 4.4.0、Ninja 1.13.2
  - 保留时区配置Asia/Shanghai
- **Business**: 保持与现有docker-compose.yml和运行方式兼容
- **Dependencies**: Miniconda官方安装包、apt包管理器、pip

## Assumptions
- 用户使用Docker 20.10+版本支持BuildKit
- 开发环境需要sudo权限安装系统包（GRANT_SUDO=yes）
- NPU工具链仍通过volume挂载到/workspace下，不打包进镜像
- Jupyter使用conda环境内的ipykernel，无需单独/opt/venv

## Acceptance Criteria

### AC-1: 镜像可独立构建
- **Given**: 一台安装了Docker 20.10+的机器，无需预先构建任何本地基础镜像
- **When**: 执行 `docker build -t chaos-ai:portable .` 在external/chaos/ai目录
- **Then**: 构建成功完成，生成可运行镜像
- **Verification**: `programmatic`

### AC-2: 默认以非root用户ai运行
- **Given**: 使用构建好的镜像启动容器
- **When**: 执行 `docker run --rm chaos-ai:portable whoami`
- **Then**: 输出 `ai`，不是root
- **Verification**: `programmatic`

### AC-3: UID/GID可配置
- **Given**: 构建时指定 `--build-arg AI_UID=1001 --build-arg AI_GID=1001`
- **When**: 启动容器执行 `id -u ai && id -g ai`
- **Then**: 输出 `1001` 和 `1001`
- **Verification**: `programmatic`

### AC-4: 默认激活py314 conda环境
- **Given**: 容器正常启动
- **When**: 在交互式bash中执行 `echo $CONDA_DEFAULT_ENV && python --version`
- **Then**: 输出 `py314` 和 Python 3.14.x版本
- **Verification**: `programmatic`

### AC-5: SSH登录环境一致
- **Given**: 容器启动sshd服务，使用ai用户通过ssh登录
- **When**: 执行 `which python && pip --version`
- **Then**: python路径指向 `/opt/conda/envs/py314/bin/python`，pip使用py314环境的pip
- **Verification**: `programmatic`

### AC-6: Jupyter使用py314环境
- **Given**: 容器启动Jupyter服务
- **When**: 在Jupyter notebook中执行 `import sys; print(sys.executable)`
- **Then**: 输出路径包含 `envs/py314/bin/python`
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
- **Given**: py314环境已激活
- **When**: 执行 `pip install requests` 后 `python -c "import requests; print(requests.__file__)"`
- **Then**: requests包安装在 `/opt/conda/envs/py314/lib/python3.14/site-packages/` 下
- **Verification**: `programmatic`

### AC-10: 跨环境conda创建正常
- **Given**: py314环境激活
- **When**: 执行 `conda create -n testenv python=3.12 -y && conda activate testenv && python --version`
- **Then**: 成功创建testenv环境，Python版本为3.12.x，环境切换正常
- **Verification**: `programmatic`

### AC-11: NPU工具链挂载兼容
- **Given**: 启动容器时挂载npuusertools和npu_tvm到/workspace
- **When**: 登录容器检查PYTHONPATH
- **Then**: PYTHONPATH包含挂载的npuusertools和npu_tvm/python路径
- **Verification**: `programmatic`

### AC-12: Dockerfile结构清晰可维护
- **Given**: 完成的Dockerfile
- **When**: 人工审查Dockerfile
- **Then**: 分层清晰，有关键注释，构建参数明确，使用BuildKit cache
- **Verification**: `human-judgment`

## Open Questions (Resolved)
- [x] 是否需要完全移除/opt/venv还是保留兼容？→ **已移除**，统一使用conda py314环境，镜像中不创建/opt/venv
- [x] fix-permissions.sh是否需要在entrypoint自动执行还是用户手动调用？→ **用户手动调用**，提供脚本+文档说明，启动脚本不自动修改挂载卷权限（避免破坏宿主机文件）
- [x] 国内镜像源默认值是使用官方源还是默认国内源？→ **默认国内源**：APT_MIRROR=aliyun, CONDA_MIRROR=bfsu, PIP_MIRROR=aliyun，与原项目一致
