# NPU TVM Nuitka 打包功能 - 产品需求文档

## Overview
- **Summary**: 为 `npu_tvm` 项目实现 Nuitka 打包功能，将 TVM 和 VTA 的 Python 模块编译为优化的二进制 `.so` 文件，并使用 scikit-build-core 打包为可分发的 wheel 包。
- **Purpose**: 提供生产级别的 TVM/VTA 二进制分发能力，提高运行性能并减少运行时依赖。
- **Target Users**: NPU TVM 开发人员、部署工程师、最终用户

## Goals
- 在 `d:\spaces\SpecWeave\external\xmhub\npu_tvm\docker\local` 目录环境中实现完整的 Nuitka 打包流程
- 参考 `notebook/xmnn/tvm` 和 `notebook/xmnn/vta` 的实现方式与配置规范（仅作设计参考）
- 支持 TVM 和 VTA 两个组件的独立编译与打包
- 打包产物符合项目要求并能正确集成到现有系统架构中
- **完全自包含实现，不依赖 notebook 目录中的任何代码、资源或模块**

## Non-Goals (Out of Scope)
- XMNN 组件的打包（任务明确要求仅处理 tvm.so 和 vta.so）
- 客户端运行时镜像构建（notebook 的 inv client 功能）
- 镜像导出/推送功能（notebook 的 inv export 功能）
- 对 notebook 目录的任何形式的依赖或引用

## Background & Context
- 设计参考：`external/xmhub/notebook/xmnn/tvm` 和 `external/xmhub/notebook/xmnn/vta`（仅作架构设计参考，不引入依赖）
- 参考实现采用两阶段设计：Nuitka 编译 → scikit-build-core wheel 打包
- 目标环境是 `docker/local/conda/Dockerfile` 构建的容器，使用 Python 3.14 + LLVM 22
- 现有 docker-compose.yml 已有 tvm-builder 服务，需在此基础上扩展
- TVM CMake 构建产物位于 `/workspace/npu_tvm/build`

## Functional Requirements
- **FR-1**: 创建 Nuitka 打包配置目录结构，包含 TVM 和 VTA 的 pyproject.toml、CMakeLists.txt、启动文件（全部自包含）
- **FR-2**: 更新 Dockerfile，预安装 Nuitka 和 scikit-build-core 依赖
- **FR-3**: 创建 Nuitka 编译脚本，支持 TVM 和 VTA 模块的独立编译
- **FR-4**: 创建 wheel 打包脚本，使用 scikit-build-core 组装二进制包
- **FR-5**: 提供在容器内执行打包的入口脚本或 compose 服务配置

## Non-Functional Requirements
- **NFR-1**: 打包脚本应在现有 `npu-tvm-build` 容器环境中执行，无需新建独立镜像
- **NFR-2**: 支持增量编译（检测 .so 已存在时跳过）
- **NFR-3**: 产物完整性验证（检测必要文件是否存在）
- **NFR-4**: 编译产物应放置在 `build/` 目录下的 `nuitka/` 子目录
- **NFR-5**: **自包含性要求**：所有配置文件、脚本必须在 `npu_tvm/docker/local/nuitka/` 目录内创建，不得引用或依赖 `notebook` 目录中的任何内容

## Constraints
- **Technical**: Python 3.14, LLVM 22, Nuitka, scikit-build-core >= 0.10
- **Dependencies**: TVM CMake 构建产物（libtvm.so, libtvm_runtime.so, libvta.so）必须已存在
- **Environment**: 所有操作在 `docker/local` 目录环境中执行
- **Isolation**: 实现完全独立于 notebook 项目，不得引入任何跨项目依赖

## Assumptions
- TVM CMake 构建已完成，`build/` 目录包含 `libtvm.so`, `libtvm_runtime.so`, `libvta.so`
- Docker 环境已配置好（docker-compose 可正常运行）
- 用户已熟悉项目的 Docker 工作流

## Acceptance Criteria

### AC-1: Nuitka 打包配置目录结构完整（自包含）
- **Given**: 项目目录 `docker/local/nuitka/` 不存在
- **When**: 执行实现任务
- **Then**: 目录结构包含 tvm/ 和 vta/ 子目录，每个子目录包含 pyproject.toml、CMakeLists.txt；tvm/ 目录额外包含 _tvm_nuitka_init.py 和 tvm_nuitka_init.pth；所有文件均为自包含创建，不引用 notebook 目录
- **Verification**: `programmatic`

### AC-2: Dockerfile 包含 Nuitka 和 scikit-build-core
- **Given**: Dockerfile 已更新
- **When**: 构建镜像并进入容器
- **Then**: 执行 `pip list | grep -i nuitka` 和 `pip list | grep -i scikit-build` 均有输出
- **Verification**: `programmatic`

### AC-3: Nuitka 编译脚本可编译 TVM 和 VTA（独立编译）
- **Given**: TVM CMake 构建已完成
- **When**: 在容器内执行编译脚本
- **Then**: 生成独立的 `tvm.cpython-*.so` 和 `vta.cpython-*.so` 文件，VTA 编译时依赖已编译的 TVM
- **Verification**: `programmatic`

### AC-4: Wheel 打包脚本可生成独立的 wheel 文件（TVM 和 VTA 解耦）
- **Given**: Nuitka 编译已完成
- **When**: 在容器内执行打包脚本
- **Then**: 生成独立的 `tvm-*.whl` 和 `vta-*.whl` 文件，VTA wheel 通过 dependencies 声明对 TVM 的依赖
- **Verification**: `programmatic`

### AC-5: 打包产物可正确集成（独立安装）
- **Given**: wheel 文件已生成
- **When**: 先安装 TVM wheel，再安装 VTA wheel，然后导入模块
- **Then**: TVM 和 VTA 模块均可独立导入且功能正常
- **Verification**: `programmatic`

### AC-6: 自包含性验证
- **Given**: 实现完成
- **When**: 检查所有配置文件和脚本
- **Then**: 不存在任何对 `external/xmhub/notebook` 目录的引用、导入或依赖
- **Verification**: `programmatic`

## Open Questions
- [ ] 是否需要支持 no-llvm 变体？（参考实现中有此功能，但任务未明确要求）
- [ ] wheel 输出目录应放在哪里？（建议放在 `docker/local/nuitka/dist/`）