# Conda + LLVM 22.1 Docker 开发环境 - The Implementation Plan

## [x] Task 1: 创建 Docker 目录结构并调研 LLVM 22.1 安装方式
- **Priority**: high
- **Depends On**: None
- **Description**:
  - 创建目标目录 `d:\spaces\SpecWeave\external\chaos\xmtools\docker\dev-llvm22\`
  - 调研 conda-forge 是否提供 LLVM 22.1 包
  - 调研 LLVM 官方 APT 源的 22.1 版本可用性
  - 确定基础镜像选择（Ubuntu 24.04 还是 continuumio/miniconda3）
- **Acceptance Criteria Addressed**: AC-1
- **Test Requirements**:
  - `programmatic` TR-1.1: 目标目录存在
  - `human-judgement` TR-1.2: 调研结论记录，确定安装方案
- **Notes**: 优先尝试 conda-forge 安装，如果不可用再考虑官方源或二进制包。调研结果：conda-forge提供LLVM 22.1.8，选择Ubuntu 26.04 + Miniconda + conda-forge安装方案

## [x] Task 2: 编写 Dockerfile - 基础系统和 Conda 安装
- **Priority**: high
- **Depends On**: Task 1
- **Description**:
  - 选择基础镜像（Ubuntu 26.04）
  - 安装基础系统依赖（wget, bzip2, ca-certificates 等）
  - 下载并安装 Miniconda3 到 /opt/conda
  - 配置 Conda（添加 conda-forge channel，设置默认不自动激活 base）
  - 设置 PATH 环境变量包含 /opt/conda/bin
  - 清理 Conda 缓存减小镜像体积
- **Acceptance Criteria Addressed**: AC-2, AC-7
- **Test Requirements**:
  - `programmatic` TR-2.1: `conda --version` 可正常执行
  - `programmatic` TR-2.2: `which conda` 输出 /opt/conda/bin/conda
  - `programmatic` TR-2.3: PATH 环境变量包含 /opt/conda/bin

## [x] Task 3: 编写 Dockerfile - LLVM 22.1 安装
- **Priority**: high
- **Depends On**: Task 2
- **Description**:
  - 根据 Task 1 调研结果选择 LLVM 安装方式（优先 conda install llvmdev=22.1 或官方包）
  - 如果使用 Conda：`conda install -c conda-forge llvm=22.1.8 clang=22.1.8 llvm-tools=22.1.7`
  - 设置 LLVM_CONFIG 环境变量
  - 验证 LLVM 版本
- **Acceptance Criteria Addressed**: AC-3, AC-4, AC-5, AC-10
- **Test Requirements**:
  - `programmatic` TR-3.1: `llvm-config --version` 输出 22.1.x
  - `programmatic` TR-3.2: clang、opt、llc、llvm-dis 等工具均在 PATH 中
  - `programmatic` TR-3.3: LLVM_CONFIG 环境变量指向正确的 llvm-config 路径
  - `programmatic` TR-3.4: Docker 构建日志中显示 LLVM 版本验证结果

## [x] Task 4: 编写 Dockerfile - 构建工具安装和环境配置
- **Priority**: high
- **Depends On**: Task 3
- **Description**:
  - 通过apt安装build-essential, ccache, git, pkg-config
  - 通过conda安装cmake, ninja, python=3.14, pip
  - 设置工作目录为 /workspace
  - 配置 LD_LIBRARY_PATH 包含 LLVM 库路径
  - 清理 apt 和 conda 缓存
  - 设置默认 CMD 为 bash
- **Acceptance Criteria Addressed**: AC-6, AC-7
- **Test Requirements**:
  - `programmatic` TR-4.1: cmake --version, ninja --version, gcc --version 可正常执行
  - `programmatic` TR-4.2: 工作目录为 /workspace
  - `programmatic` TR-4.3: apt 和 Conda 缓存已清理

## [x] Task 5: 创建构建脚本 build-docker.sh
- **Priority**: medium
- **Depends On**: Task 4
- **Description**:
  - 创建 shell 脚本 build-docker.sh
  - 脚本功能：构建 Docker 镜像，标签为 xmnn-dev:llvm22
  - 包含构建进度提示和验证步骤
  - 构建成功后输出使用说明
- **Acceptance Criteria Addressed**: AC-8
- **Test Requirements**:
  - `programmatic` TR-5.1: 脚本存在
  - `human-judgement` TR-5.2: 脚本逻辑正确，可执行

## [ ] Task 6: 本地构建验证和测试
- **Priority**: high
- **Depends On**: Task 5
- **Description**:
  - 在 WSL2 环境中执行 build-docker.sh 构建镜像
  - 运行容器并执行所有验收标准中的验证命令
  - 检查镜像大小是否符合 NFR-1 要求
  - 修复构建过程中遇到的问题（如包版本不存在、依赖冲突等）
  - 如 Conda 渠道无 LLVM 22.1，切换到官方源或二进制安装方案
- **Acceptance Criteria Addressed**: AC-1, AC-2, AC-3, AC-4, AC-5, AC-6, AC-7, AC-9
- **Test Requirements**:
  - `programmatic` TR-6.1: docker build 命令成功完成（exit code 0）
  - `programmatic` TR-6.2: 所有 AC-1 到 AC-7 的验证命令均通过
  - `programmatic` TR-6.3: 镜像大小 <= 2GB
- **Notes**: 这是端到端验证，需要实际运行 Docker 构建
