---
version: "1.0"
---

# XMNN Wheel Python 版本限制 - 产品需求文档

## Overview
- **Summary**: 为位于 `external/chaos/xmtools` 的 xmtools 项目设置严格的 Python 版本限制，确保该项目（包括构建过程和运行时）只能在 Python 3.14 及更高版本环境中运行。
- **Purpose**: 由于项目依赖 Nuitka 编译和 TVM 运行时，这些组件需要 Python 3.14+ 的特定 API 和特性，限制版本可避免因 Python 版本不兼容导致的构建失败和运行时错误。
- **Target Users**: XMNN 开发人员、构建工程师、使用 xmnn wheel 包的最终用户

## Goals
- 在 `pyproject.toml` 中明确声明 `requires-python = ">=3.14"`
- 在 CMake 构建阶段添加 Python 版本检查，低于 3.14 时终止构建
- 在 Invoke 构建任务的依赖检查阶段添加 Python 版本验证
- 在验证脚本中添加 Python 版本检查
- 确保依赖包与 Python 3.14+ 兼容

## Non-Goals (Out of Scope)
- 降级代码以支持 Python 3.13 或更早版本
- 添加对多个 Python 版本的并行支持
- 修改实际的 Python 代码逻辑
- 更新 docker 镜像配置（已有镜像使用 Python 3.14）

## Background & Context
- xmtools 项目使用 scikit-build-core + CMake + Nuitka 构建 wheel 包
- 项目依赖 TVM C++ 库和 Nuitka 编译的 Python 模块
- 之前的配置允许 Python 3.8+，但实际代码和依赖需要 Python 3.14+
- TVM 构建环境已配置为使用 Python 3.14（见 caffe-pycaffe 相关 docker 配置）
- Nuitka 对 Python 3.14 的支持需要特定版本

## Functional Requirements
- **FR-1**: 更新 `pyproject.toml`，将 `requires-python` 设置为 `">=3.14"`
- **FR-2**: 在 `CMakeLists.txt` 中添加 Python 版本检查，使用 `find_package(Python3)` 并验证版本 >= 3.14，否则 FATAL_ERROR
- **FR-3**: 在 `tasks.py` 的 `check_deps` 任务中添加 Python 版本验证逻辑
- **FR-4**: 在 `scripts/verify_wheel.py` 中添加 Python 版本检查
- **FR-5**: 验证所有依赖包（numpy, decorator, attrs, psutil, cloudpickle, scikit-build-core, cmake, ninja, nuitka）与 Python 3.14+ 兼容

## Non-Functional Requirements
- **NFR-1**: 版本检查应在构建流程早期执行，提供清晰的错误信息
- **NFR-2**: 错误信息应明确指出需要的版本（>=3.14）和当前检测到的版本
- **NFR-3**: 版本检查应在三个层面都存在：pip安装时、CMake配置时、任务脚本检查时，形成多层防护

## Constraints
- **Technical**: 必须使用 Python 3.14 或更高版本
- **Build System**: scikit-build-core >= 0.5, CMake >= 3.18, Ninja >= 1.10
- **Compatibility**: 所有声明的依赖必须支持 Python 3.14+

## Assumptions
- 开发和构建环境已配置 Python 3.14（WSL/Linux 环境）
- 依赖包的最新版本都支持 Python 3.14
- 用户理解版本限制的必要性，不需要向下兼容

## Acceptance Criteria

### AC-1: pyproject.toml 声明正确的 Python 版本要求
- **Given**: pyproject.toml 文件存在
- **When**: 查看项目配置
- **Then**: `[project]` 节中 `requires-python` 字段值为 `">=3.14"`
- **Verification**: `programmatic`

### AC-2: CMake 配置阶段检查 Python 版本
- **Given**: 使用 Python 3.13 或更低版本
- **When**: 执行 CMake 配置（如 `python -m build --wheel`）
- **Then**: CMake 配置失败，显示 FATAL_ERROR，明确提示需要 Python >= 3.14
- **Verification**: `programmatic`

### AC-3: CMake 配置在 Python 3.14+ 环境中正常通过
- **Given**: 使用 Python 3.14 或更高版本
- **When**: 执行 CMake 配置
- **Then**: 配置正常完成，版本检查通过
- **Verification**: `programmatic`

### AC-4: Invoke check_deps 任务检查 Python 版本
- **Given**: 使用 Python 3.13 或更低版本
- **When**: 执行 `inv check-deps`
- **Then**: 输出错误信息，显示当前版本和要求版本，以非零退出码终止
- **Verification**: `programmatic`

### AC-5: Invoke check_deps 在 Python 3.14+ 环境中通过
- **Given**: 使用 Python 3.14 或更高版本
- **When**: 执行 `inv check-deps`
- **Then**: Python 版本检查显示 ✓ 通过，继续其他检查
- **Verification**: `programmatic`

### AC-6: 验证脚本检查 Python 版本
- **Given**: 使用 Python 3.13 或更低版本运行 verify_wheel.py
- **When**: 执行验证脚本
- **Then**: 脚本检测版本不兼容并给出明确错误提示
- **Verification**: `programmatic`

### AC-7: 依赖包与 Python 3.14+ 兼容
- **Given**: 依赖列表已审查
- **When**: 在 Python 3.14 环境中安装所有依赖
- **Then**: 所有依赖（numpy, decorator, attrs, psutil, cloudpickle, scikit-build-core, cmake, ninja, nuitka）均可正常安装和导入
- **Verification**: `programmatic`

### AC-8: pip 安装时自动拒绝低版本 Python
- **Given**: wheel 包已构建
- **When**: 在 Python 3.13 或更低版本环境中尝试 `pip install xmnn-*.whl`
- **Then**: pip 报错，提示 Python 版本不满足要求
- **Verification**: `programmatic`

## Open Questions
- 无
