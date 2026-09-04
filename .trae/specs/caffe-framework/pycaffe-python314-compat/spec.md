# PyCaffe pyproject.toml Python 3.14+ 兼容性更新 - Product Requirement Document

## Overview

* **Summary**: 更新 `caffe-slim/pycaffe/pyproject.toml` 中的 Python 版本约束和依赖版本下限，使其正确声明对 Python 3.14+ 的兼容性要求，并确保所有依赖包版本约束与 Python 3.14 兼容。

* **Purpose**: 当前 `pyproject.toml` 的 `requires-python` 已设置为 `>=3.14`，但运行时依赖的版本下限过于陈旧（如 `numpy>=1.7.1`、`scipy>=0.13.2`），这些旧版本不提供 Python 3.14 的 wheel 或源码兼容性，会导致 pip 解析依赖时选择不兼容的版本或解析失败。需要将所有依赖版本下限提升到支持 Python 3.14 的最低版本。

* **Target Users**: PyCaffe 包维护者、使用 pycaffe wheel 的开发者、Docker 镜像构建系统。

## Goals

* 正确声明 `requires-python = ">=3.14"`

* 将所有运行时依赖（dependencies）的版本下限提升到兼容 Python 3.14 的最低版本

* 将构建系统依赖（build-system.requires）的版本下限提升到兼容 Python 3.14 的最低版本

* 将可选依赖（optional-dependencies）的版本下限同步更新

* 更新 scikit-build 配置中的 `wheel.py-api` 以正确标记 Python 3.14+ ABI 兼容性

* 同步更新 `build.sh` 注释中的 Python 版本要求

## Non-Goals (Out of Scope)

* 不修改 C++ 源码或 CMakeLists.txt

* 不修改 Dockerfile 中的基础镜像或 Python 版本（Docker 构建环境的 Python 升级是独立任务）

* 不升级到比"支持 Python 3.14 的最低版本"更高的版本（避免不必要的版本跳跃）

* 不修改 `caffex/` 目录下的任何文件（BVLC 原始 fork，禁止修改）

* 不添加新的依赖包

## Background & Context

* Python 3.14 是较新的 Python 版本，许多科学计算包从特定版本开始才提供 3.14 兼容的 wheel

* numpy 从 2.1+ 开始正式支持 Python 3.14

* scipy 从 1.14+ 开始支持 Python 3.14

* 现行 Dockerfile(standalone/pycaffe) 使用 Ubuntu 26.04 系统 Python，已经安装了较新版本的包（numpy>=2, scipy>=1.7 等），pyproject.toml 的约束应与实际构建环境保持一致

* pyproject.toml 当前的依赖版本是 BVLC Caffe 时代的遗留约束（numpy>=1.7.1 约为 2013 年版本），严重过时

* `wheel.py-api = "py3"` 表示通用 Python 3 ABI，对于包含 C 扩展的包应该使用 `cp3` 标记，但 scikit-build-core 会自动处理，当前设置可保留

## Functional Requirements

* **FR-1**: `requires-python` 正确声明为 `">=3.14"`（已满足，需验证）

* **FR-2**: `build-system.requires` 中所有包的版本下限兼容 Python 3.14

* **FR-3**: `project.dependencies` 中所有运行时依赖的版本下限兼容 Python 3.14

* **FR-4**: `project.optional-dependencies` 中 test 和 full 组的依赖版本下限兼容 Python 3.14

* **FR-5**: `tool.scikit-build` 配置与 Python 3.14 兼容

* **FR-6**: `build.sh` 中的 Python 版本注释同步更新

## Non-Functional Requirements

* **NFR-1**: TOML 格式正确性：修改后的 pyproject.toml 必须是合法 TOML

* **NFR-2**: 版本约束一致性：pyproject.toml 中的版本下限不得高于 Dockerfile(standalone/pycaffe)中安装的版本

* **NFR-3**: 最小变更原则：只修改版本号，不改变依赖列表或添加新依赖

## Constraints

* **Technical**:

  * 仅修改 `pyproject.toml` 和 `build.sh` 两个文件

  * TOML 语法，需使用正确的引号和列表格式

  * scikit-build-core >=0.10 是构建后端，需要确保其版本支持 Python 3.14

* **Business**: caffe-slim 是 CPU-only slim 版本，不引入 GPU/CUDA 相关依赖

* **Dependencies**:

  * numpy 2.1+ 支持 Python 3.14

  * scipy 1.14+ 支持 Python 3.14

  * 其他包需要逐一确认最低兼容版本

## Assumptions

* Python 3.14 是目标版本，3.14+ 包含 3.14、3.15 等未来版本

* Docker 构建环境（Ubuntu 26.04）将提供 Python 3.14+ 的系统包

* scikit-build-core 最新版本（>=0.10）已支持 Python 3.14

* 现有依赖列表不需要增减包

## Acceptance Criteria

### AC-1: requires-python 正确声明

* **Given**: pyproject.toml 文件存在

* **When**: 检查 \[project] 节的 requires-python 字段

* **Then**: 值为 `">=3.14"`，TOML 语法正确

* **Verification**: `programmatic`

### AC-2: 构建系统依赖兼容 Python 3.14

* **Given**: pyproject.toml 的 \[build-system] 节

* **When**: 检查 requires 列表中每个包的版本约束

* **Then**: 每个包的版本下限 >= 支持 Python 3.14 的最低版本

* **Verification**: `programmatic`

### AC-3: 运行时依赖兼容 Python 3.14

* **Given**: pyproject.toml 的 \[project] dependencies 列表

* **When**: 检查每个依赖的版本约束

* **Then**: 每个包的版本下限 >= 支持 Python 3.14 的最低版本，且不高于 Dockerfile 中已安装的版本

* **Verification**: `programmatic`

### AC-4: 可选依赖兼容 Python 3.14

* **Given**: pyproject.toml 的 \[project.optional-dependencies] 节

* **When**: 检查 test 和 full 组中每个包的版本约束

* **Then**: 每个包的版本下限 >= 支持 Python 3.14 的最低版本

* **Verification**: `programmatic`

### AC-5: TOML 文件格式验证通过

* **Given**: 修改后的 pyproject.toml

* **When**: 使用 Python tomllib/tomli 解析该文件

* **Then**: 解析成功无错误，所有字段值正确

* **Verification**: `programmatic`

### AC-6: build.sh 注释同步

* **Given**: build.sh 文件

* **When**: 检查文件中的 Python 版本注释

* **Then**: 注释反映 Python 3.14+ 的要求

* **Verification**: `human-judgment`

### AC-7: scikit-build 配置兼容性

* **Given**: pyproject.toml 的 \[tool.scikit-build] 节

* **When**: 检查 wheel.py-api 和相关配置

* **Then**: 配置不阻止 Python 3.14+ 构建

* **Verification**: `programmatic`

## Open Questions

* [ ] numpy 2.0 是否支持 Python 3.14？需要确认 numpy 2.0 vs 2.1 的 Python 3.14 支持情况

* [ ] 是否需要同时更新 `wheel.py-api` 从 `"py3"` 改为 `"cp314"` 或 `"py314"`？需要确认 scikit-build-core 对 C 扩展包的最佳实践

