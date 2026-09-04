# XMNN Docker 运行时镜像（WSL 构建） - Product Requirement Document

## Overview
- **Summary**: 在 WSL2 (Ubuntu 24.04) 环境中，基于已生成的 xmnn wheel 包（`xmnn-1.2.2a0-cp314-cp314-linux_x86_64.whl`, 184MB）构建一个可直接运行的 Docker 运行时镜像。镜像需包含正确的 Python 3.14 环境、所有系统级和 Python 级依赖，能成功导入 tvm/vta/xmnn 并执行核心功能。
- **Purpose**: 为终端用户提供开箱即用的 XMNN Docker 运行环境，用户无需关心 Python 版本、LLVM/ICU 等系统库安装、环境变量配置等问题，`docker run` 即可使用。
- **Target Users**: 需要在 Linux/Docker 环境中使用 XMNN（TVM+VTA+XMNN 编译工具链）进行模型编译、量化和推理的开发者和部署工程师。

## Goals
- 在 WSL2 Ubuntu 环境中成功构建 Docker 运行时镜像
- 镜像基于现有 `Dockerfile.runtime`（多阶段构建：builder 阶段安装依赖+wheel，runtime 阶段精简运行时）
- 镜像内含 Python 3.14 + xmnn wheel + 所有必要依赖（numpy, scipy, ml_dtypes, Pillow 等）
- wheel 内捆绑的 9 个非系统共享库（libLLVM-22, libicu, libxml2, libstdc++ 等）通过 RPATH 正确解析，无需系统预装 LLVM/ICU
- 镜像启动后可直接 `import tvm; import vta; import xmnn` 成功
- 支持通过 build-arg 选择性安装可选依赖（ONNX/PyTorch/TF/RPC 等）
- 镜像体积尽可能精简（多阶段构建，不含编译工具链）

## Non-Goals (Out of Scope)
- 不在本次任务中重新编译 Nuitka .so 文件（wheel 已构建完成）
- 不支持 GPU/CUDA 运行时（本次仅 CPU 版本）
- 不修改 wheel 包内容（仅在 Docker 构建层面适配）
- 不支持 Windows 原生容器（仅 Linux 容器，通过 WSL2 运行）
- 不推送到远程镜像仓库（仅本地构建和验证）

## Background & Context
- 已完成 Nuitka 编译将 TVM/VTA/XMNN Python 源码编译为机器码 `.so` 文件
- 已通过 scikit-build-core + CMake + Ninja 打 wheel 包，wheel 内含 9 个捆绑的非系统共享库（解决 libLLVM-22 等依赖问题）
- 已修复 pyproject.toml 核心依赖（添加 scipy，因为 tvm.relay.quantize 在顶层导入 scipy.stats.entropy）
- 项目已有 `docker/Dockerfile.runtime` 多阶段构建方案，但需要验证其与最新 wheel 的兼容性
- WSL2 Ubuntu-24.04 已安装 Docker 29.6.1，已有 `npu-tvm-builder` 构建容器
- 现有 Dockerfile.runtime 基于 `condaforge/miniforge3`，通过 environment.yml 创建 conda 环境，builder→runtime 两阶段构建

## Functional Requirements
- **FR-1**: WSL2 中 Docker 服务正常运行，可执行 docker build/run 命令
- **FR-2**: wheel 文件放置在 Docker 构建上下文可访问的位置
- **FR-3**: Dockerfile.runtime 正确配置 Python 3.14 环境并安装 wheel 及所有依赖
- **FR-4**: 构建过程中自动验证 tvm/vta/xmnn 导入成功
- **FR-5**: 运行时镜像中 TVM_LIBRARY_PATH 正确指向捆绑库目录（tvm/_libs/）
- **FR-6**: entrypoint 脚本正确处理 UID/GID 映射和工作目录权限
- **FR-7**: 镜像支持通过 docker run 进入交互式 shell 或直接执行 Python 脚本
- **FR-8**: 构建完成后运行容器进行端到端功能验证

## Non-Functional Requirements
- **NFR-1**: 运行时镜像体积应尽可能小（目标 < 1.5GB，不含可选的 PyTorch/TF 等大依赖）
- **NFR-2**: 镜像构建时间应在 10 分钟内（利用 Docker 层缓存）
- **NFR-3**: 镜像启动后 import tvm 应在 5 秒内完成
- **NFR-4**: 镜像内不应包含 Nuitka/Cython/gcc 等编译工具链
- **NFR-5**: 所有共享库依赖通过 RPATH 解析，不依赖 LD_LIBRARY_PATH 环境变量（.pth 文件处理）

## Constraints
- **Technical**: 
  - 目标平台：Linux x86_64（wheel 为 cp314-linux_x86_64）
  - Python 版本：3.14（wheel 绑定 CPython 3.14 ABI）
  - 基础镜像：condaforge/miniforge3:24.9.2-0（已有 Dockerfile.runtime 使用）
  - 构建环境：WSL2 Ubuntu 24.04 + Docker
- **Business**: 使用已有 Dockerfile.runtime 作为基础，避免重复造轮子
- **Dependencies**: wheel 位于 `dist/xmnn-1.2.2a0-cp314-cp314-linux_x86_64.whl`

## Assumptions
- WSL2 中 Docker 已正确安装并运行（之前已验证 Docker 29.6.1 可用）
- 现有 Dockerfile.runtime 的多阶段构建逻辑基本正确，可能需要微调 wheel 路径或依赖
- wheel 内捆绑的系统库（libLLVM 等）在 condaforge/miniforge3 基础镜像上能正常工作（RPATH=$ORIGIN）
- conda-forge 源有 Python 3.14 可用

## Acceptance Criteria

### AC-1: WSL Docker 环境就绪
- **Given**: WSL2 Ubuntu 24.04 环境
- **When**: 执行 `docker --version` 和 `docker info`
- **Then**: Docker 服务正常运行，版本信息正确输出
- **Verification**: `programmatic`

### AC-2: Docker 镜像构建成功
- **Given**: wheel 文件在构建上下文正确位置，Dockerfile.runtime 配置正确
- **When**: 执行 `docker build -f docker/Dockerfile.runtime -t xmnn-runtime:1.2.2 .`
- **Then**: 镜像构建成功，无错误退出
- **Verification**: `programmatic`

### AC-3: 镜像内核心模块导入成功
- **Given**: 镜像已构建完成
- **When**: 执行 `docker run --rm xmnn-runtime:1.2.2 python -c "import tvm; import vta; import xmnn; print('OK')"`
- **Then**: 输出 "OK"，无 ImportError 或共享库加载错误
- **Verification**: `programmatic`

### AC-4: TVM 核心功能可正常使用
- **Given**: 容器正在运行
- **When**: 在容器内执行 TE compute、Relay 构建、NDArray 操作
- **Then**: 所有操作成功执行，无运行时错误
- **Verification**: `programmatic`

### AC-5: 共享库依赖完全解析
- **Given**: 容器内环境
- **When**: 对 tvm/_libs/*.so 执行 `ldd` 检查
- **Then**: 无 "not found" 的共享库依赖
- **Verification**: `programmatic`

### AC-6: 镜像体积合理
- **Given**: 镜像已构建
- **When**: 执行 `docker images xmnn-runtime:1.2.2`
- **Then**: 镜像大小在合理范围内（< 1.5GB 基础版，含 infer+report extras）
- **Verification**: `programmatic`

### AC-7: 交互式 shell 可用
- **Given**: 镜像已构建
- **When**: 执行 `docker run -it --rm xmnn-runtime:1.2.2 bash`
- **Then**: 进入容器 bash shell，可交互执行 Python 命令
- **Verification**: `programmatic`

### AC-8: 环境变量自动配置
- **Given**: 容器启动
- **When**: 在容器内检查 TVM_LIBRARY_PATH 和 Python 路径
- **Then**: TVM_LIBRARY_PATH 正确指向 tvm/_libs/，.pth 初始化脚本正常执行
- **Verification**: `programmatic`

## Open Questions
- [ ] 是否需要将 wheel 复制到 `packaging/dist/`（Dockerfile.runtime 期望的路径）还是修改 Dockerfile 中的 COPY 路径？
- [ ] Dockerfile.runtime 使用 conda 环境，但 wheel 的 Python 依赖通过 pip 安装即可满足，是否需要简化为直接 pip 安装（不使用 conda env create）？
- [ ] 是否需要构建包含 ONNX/PyTorch 等可选依赖的镜像变体？
