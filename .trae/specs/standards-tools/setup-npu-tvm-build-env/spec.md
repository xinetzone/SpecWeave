---
version: 1.2
---

# NPU TVM 容器化构建环境与 XMNN Git 版本控制 - Product Requirement Document

## Overview
- **Summary**: 为 `external/xmhub/npu_tvm` 项目构建基于 Docker 的容器化开发打包环境，包含 conda、ninja、cmake 完整工具链；同时在 `external/xmhub/xmnn` 新建目录初始化 Git 仓库，配置分支策略与提交规范，实现代码变更的完整追踪管理。
- **Purpose**: 解决 npu_tvm 打包环境一致性问题（消除"在我机器上能跑"的环境差异），通过容器化确保可移植性；为 xmnn 模块建立规范的版本控制体系，支撑后续开发协作。
- **Target Users**: NPU TVM 开发工程师、构建打包工程师、XMNN 模块开发者

## Goals
- 基于官方 conda 基础镜像构建独立的 Dockerfile，正确配置 conda 环境变量、ninja 编译工具路径和 cmake 构建参数
- Docker 环境满足 npu_tvm 的 CPU 版本构建与打包需求（含 conda recipe 打包能力）
- 在 `external/xmhub/xmnn/` 创建新目录并初始化 Git 仓库
- 配置 xmnn 仓库的分支策略（main/develop 模型）、提交规范（Conventional Commits）、.gitignore 规则
- 提供环境构建、容器运行、Git 操作的详细实施步骤与验证方法文档

## Non-Goals (Out of Scope)
- 不包含 CUDA/GPU 版本的 Docker 镜像构建（本次仅 CPU 版本）
- 不涉及 npu_tvm 源码本身的修改或功能开发
- 不将现有分散的 xmnn 代码（npuusertools/xmnn、notebook/xmnn）迁移整合到新仓库（仅创建空仓库框架）
- 不配置 CI/CD 流水线（仅本地 Git 配置）
- 不配置远程仓库推送（仅本地初始化）

## Background & Context
- `npu_tvm` 是 Apache TVM 的定制分支（lxw 分支），用于 NPU 深度学习编译器栈，已内置 conda recipe（`conda/recipe/`）和 docker 配置（`docker/`）
- 现有 `dev-env/llvm-dev` 提供了基于 `localhost/nuitka-gcc-llvm:latest` 的挂载式开发环境，但依赖私有基础镜像，可移植性受限
- npu_tvm 的 CMake 构建需要 LLVM、VTA 等组件支持，关键构建选项包括 `USE_LLVM`、`USE_VTA`、`USE_RPC`、`USE_THREADS` 等
- xmnn 相关代码目前分散在 `npuusertools/xmnn/`（Python工具链）、`notebook/xmnn/`（wheel打包工程）、`dev-env/xmnn-packager/xmnn/`（打包配置）三处，用户要求先创建独立空仓库作为后续统一版本控制的基础

## Functional Requirements
- **FR-1**: Dockerfile 基于 continuumio/miniconda3 官方基础镜像构建
- **FR-2**: Dockerfile 正确安装 ninja-build、cmake、gcc/g++ 编译工具链
- **FR-3**: Dockerfile 配置 conda 环境变量（CONDA_DIR、PATH 包含 conda bin、conda 初始化）
- **FR-4**: Dockerfile 配置 ninja 路径，确保 cmake 能自动发现 ninja 构建器
- **FR-5**: Dockerfile 预置 npu_tvm 构建所需的 cmake 参数默认值（USE_LLVM、USE_VTA、CMAKE_BUILD_TYPE 等）
- **FR-6**: Dockerfile 支持 conda build 命令，可执行 npu_tvm 的 conda recipe 打包
- **FR-7**: 容器支持目录挂载，可将宿主 npu_tvm 源码挂载到容器内进行构建
- **FR-8**: 在 `external/xmhub/xmnn/` 创建目录并执行 `git init` 初始化仓库
- **FR-9**: xmnn 仓库配置初始分支为 `main`，并创建 `develop` 开发分支
- **FR-10**: xmnn 仓库配置 .gitignore 文件（Python 编译产物、构建目录、IDE 文件、虚拟环境等）
- **FR-11**: xmnn 仓库配置提交规范（commit-msg hook 或 commitlint 配置，遵循 Conventional Commits）
- **FR-12**: xmnn 仓库配置 .gitattributes 处理行尾符和二进制文件
- **FR-13**: xmnn 仓库创建初始 README.md 说明仓库用途
- **FR-14**: 提供 Docker 镜像构建、容器运行、环境验证的完整操作步骤文档
- **FR-15**: 提供 xmnn Git 仓库初始化验证、分支操作、提交流程的操作指南

## Non-Functional Requirements
- **NFR-1**: Docker 镜像构建应可复现，使用国内镜像源（阿里云 apt/pip/conda）加速构建
- **NFR-2**: Dockerfile 遵循层排序规范（基础镜像→环境变量→系统包→语言包→配置→COPY→入口）
- **NFR-3**: 容器以非 root 用户运行，遵循安全最佳实践
- **NFR-4**: Docker 镜像大小应控制在合理范围（建议 <5GB）
- **NFR-5**: 所有配置文件和脚本必须有清晰注释说明用途
- **NFR-6**: Git 配置文件遵循业界通用最佳实践

## Constraints
- **Technical**: 
  - Docker 运行在 Linux 容器模式（npu_tvm 构建目标为 Linux）
  - 基础镜像选用 continuumio/miniconda3（用户指定基于 conda 基础镜像）
  - CMake >= 3.18（npu_tvm CMakeLists.txt 要求）
  - Python >= 3.14（用户指定）
  - LLVM >= 22（用户指定）
- **Business**:
  - 不依赖私有基础镜像（确保在任何 Docker 环境可构建）
  - 使用国内镜像源（阿里云）加速下载
- **Dependencies**:
  - Docker Engine >= 20.10
  - Git >= 2.30

## Assumptions
- 用户已安装 Docker 并可执行 docker build/run 命令
- 用户网络可访问 Docker Hub 和阿里云镜像源
- npu_tvm 源码已克隆到 `external/xmhub/npu_tvm/` 目录
- xmnn 新仓库初始为空，后续再迁移代码
- 容器内构建的产物可通过挂载目录输出到宿主机

## Acceptance Criteria

### AC-1: Dockerfile 可成功构建镜像
- **Given**: Docker 已安装且 daemon 运行中
- **When**: 在 npu_tvm 项目 docker 目录执行 `docker build -t npu-tvm-build:latest .`
- **Then**: 镜像构建成功，无报错，`docker images` 中可见 npu-tvm-build:latest 镜像
- **Verification**: `programmatic`
- **Notes**: 使用 `--build-arg` 可配置基础镜像 tag

### AC-2: 容器内 conda 环境正确配置
- **Given**: npu-tvm-build 镜像已构建
- **When**: 运行容器并执行 `conda --version` 和 `which conda`
- **Then**: conda 命令可用，路径为 `/opt/conda/bin/conda`，conda 版本正常输出
- **Verification**: `programmatic`

### AC-3: 容器内 Python 3.14 正确配置
- **Given**: npu-tvm-build 镜像已构建
- **When**: 运行容器并执行 `python --version`
- **Then**: Python 版本 >= 3.14，pip 可用且配置了阿里云源
- **Verification**: `programmatic`

### AC-4: 容器内 ninja、cmake 和 LLVM 22 可用且路径正确
- **Given**: 容器正常运行
- **When**: 执行 `ninja --version`、`cmake --version` 和 `llvm-config --version`
- **Then**: ninja 版本 >= 1.10，cmake 版本 >= 3.18，LLVM 版本 >= 22，且 cmake 能通过 `cmake -G Ninja` 识别 ninja
- **Verification**: `programmatic`

### AC-5: 容器可成功配置 npu_tvm CMake 构建
- **Given**: 容器运行且 npu_tvm 源码已挂载到 `/workspace/npu_tvm`
- **When**: 在容器内创建 build 目录并执行 cmake 配置（指定 LLVM_CONFIG 路径）
- **Then**: cmake 配置成功，生成 build.ninja 文件，关键选项（LLVM 22、VTA）配置正确
- **Verification**: `programmatic`

### AC-6: 容器支持 conda build 打包
- **Given**: npu_tvm 源码已挂载
- **When**: 在容器内执行 `conda build conda/recipe`
- **Then**: conda build 启动并开始编译打包流程（允许依赖下载时间，编译过程可中断验证环境）
- **Verification**: `programmatic`
- **Notes**: 完整编译耗时较长，验证 conda build 命令可正常启动即可

### AC-7: xmnn 目录已创建且 Git 仓库初始化完成
- **Given**: 执行初始化任务
- **When**: 检查 `external/xmhub/xmnn/` 目录并执行 `git status`
- **Then**: 目录存在且包含 .git 子目录，git status 输出正常（显示初始分支）
- **Verification**: `programmatic`

### AC-8: xmnn 仓库分支策略配置正确
- **Given**: xmnn Git 仓库已初始化
- **When**: 执行 `git branch -a` 查看分支
- **Then**: 存在 main 分支（当前/默认）和 develop 分支
- **Verification**: `programmatic`

### AC-9: xmnn 仓库 .gitignore 配置正确
- **Given**: xmnn 仓库初始化完成
- **When**: 检查 .gitignore 文件内容并创建测试文件验证
- **Then**: .gitignore 包含 Python、CMake、IDE、虚拟环境等常见忽略规则，测试文件（如 __pycache__/、build/、*.pyc）被正确忽略
- **Verification**: `programmatic`

### AC-10: xmnn 仓库提交规范配置
- **Given**: xmnn 仓库配置完成
- **When**: 检查提交规范配置并尝试不符合规范的提交
- **Then**: 存在 commit-msg hook 或配置文件说明 Conventional Commits 规范，不符合规范的提交被拦截或警告
- **Verification**: `programmatic` + `human-judgment`

### AC-11: 提供完整的构建和使用文档
- **Given**: 所有实施任务完成
- **When**: 审阅文档内容
- **Then**: 文档包含 Docker 镜像构建命令、容器运行命令、环境验证步骤（含 Python 3.14、LLVM 22 版本验证）、Git 操作指南，步骤清晰可执行
- **Verification**: `human-judgment`

## Open Questions
- [ ] Python 3.14 + LLVM 22 在 conda-forge 上是否均有可用的预编译包？是否需要从源码编译某些依赖？
- [ ] npu_tvm Python 依赖（numpy、scipy 等）是否已有兼容 Python 3.14 的版本？
- [ ] xmnn 仓库的 commit-msg hook 使用何种方案（简单 shell 脚本 vs commitlint + husky）？
- [ ] Docker 容器是否需要 SSH 服务（类似 llvm-dev）还是仅作为一次性构建环境使用？
