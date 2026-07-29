---
version: 1.1
---

# Caffe PyCaffe 迁移至 scikit-build-core 构建系统 Spec

## Why

caffex 的 Python 接口（`python/caffe/`）使用原始 CMake `add_library(MODULE)` + Boost.Python 方式构建，产物通过符号链接放置，无法独立打包为 wheel，导致环境配置复杂、依赖系统级 Boost 库。需将其迁移至 `pycaffe/` 目录，采用 scikit-build-core + CMake + Ninja 现代化构建系统，参考 TVM-FFI 的打包模式，实现标准 wheel 构建和 pip 安装。

## What Changes

- 在 `pycaffe/` 目录创建 `pyproject.toml`，配置 scikit-build-core 构建后端
- 创建 `CMakeLists.txt`，替换原有 `python/CMakeLists.txt` 的 `add_library(MODULE)` 方式
- 从 `caffex/python/caffe/` 迁移所有 Python 模块到 `pycaffe/python/pycaffe/`
- 迁移 `_caffe.cpp` C++ 绑定文件（保留 Boost.Python 实现）
- 清理 Python 2 兼容代码（`six`、`izip_longest` 等）
- 构建产物为独立 wheel，支持 `pip install` 安装
- **BREAKING**: 构建系统从原始 CMake 迁移至 scikit-build-core，不再依赖 caffex 源码树内的 CMake 构建

## Impact

- Affected specs: `caffe-conda-python314-docker`（Dockerfile 中的 PyCaffe 构建步骤需调整为 pip install wheel）
- Affected code: `external/chaos/caffe/caffex/python/caffe/`（源，只读参考）、`external/chaos/caffe/python/pycaffe/`（目标，新建）
- 不修改 caffex 原始源码

## ADDED Requirements

### Requirement: scikit-build-core 构建配置

系统 SHALL 在 `pycaffe/pyproject.toml` 中配置 scikit-build-core 作为构建后端，使用 CMake + Ninja 编译 C++ 扩展。

#### Scenario: 构建 wheel 包
- **WHEN** 用户在 `pycaffe/` 目录执行 `pip install .` 或 `python -m build --wheel`
- **THEN** scikit-build-core 调用 CMake 配置并编译 `_caffe` C++ 扩展模块
- **THEN** 生成包含 `_caffe.so`（或 `.pyd`）和所有 Python 模块的标准 wheel

#### Scenario: 可编辑安装
- **WHEN** 用户执行 `pip install -e .`
- **THEN** 以可编辑模式安装，Python 源码修改即时生效

### Requirement: CMake 构建文件

系统 SHALL 在 `pycaffe/CMakeLists.txt` 中定义 C++ 扩展的编译规则，将 `_caffe.cpp` 编译为 Python 扩展模块。

#### Scenario: 编译 C++ 扩展
- **WHEN** CMake 配置阶段
- **THEN** 查找 Python3、Boost.Python、NumPy、protobuf 等依赖
- **THEN** 将 `_caffe.cpp` 编译为 `_caffe` 共享库
- **THEN** 链接 Caffe C++ 库和所有必要的系统库

### Requirement: Python 模块迁移

系统 SHALL 将 caffex 的 Python 模块迁移至 `pycaffe/python/pycaffe/`，保持原有 API 兼容性。

#### Scenario: 导入 pycaffe 包
- **WHEN** 用户在 Python 中执行 `import pycaffe` 或 `from pycaffe import Net`
- **THEN** 所有原有 API（Net、Solver、Classifier、Detector、io 等）可用
- **THEN** 行为与 caffex 原始 `import caffe` 一致

### Requirement: Python 2 兼容代码清理

系统 SHALL 移除所有 Python 2 兼容代码，包括 `six` 库依赖、`izip_longest` 等。

#### Scenario: Python 3.14 环境运行
- **WHEN** 在 Python 3.14 环境中导入 pycaffe
- **THEN** 无 Python 2 兼容层导致的警告或错误
- **THEN** `six` 库不再是必需依赖

### Requirement: 依赖声明

系统 SHALL 在 `pyproject.toml` 中声明完整的构建时和运行时依赖。

#### Scenario: 构建环境准备
- **WHEN** pip 安装 pycaffe wheel
- **THEN** 自动安装运行时依赖（numpy、protobuf、pyyaml、Pillow 等）
- **THEN** 构建时依赖（scikit-build-core、cmake、ninja、boost）在构建阶段可用

## MODIFIED Requirements

无。本次为新建 `pycaffe/` 目录，不修改现有代码。

### Requirement: Docker 多阶段构建集成

系统 SHALL 在 `docker/local/conda/Dockerfile` 中新增 `pycaffe-builder` 阶段，从 builder 阶段获取 Caffe 编译产物，通过 scikit-build-core 构建 pycaffe wheel，并在 runtime 阶段通过 pip 安装。

#### Scenario: Docker 多阶段构建
- **WHEN** 执行 `docker build --target runtime`
- **THEN** `pycaffe-builder` 阶段成功编译 `_caffe.so` 并生成 wheel
- **THEN** `runtime` 阶段成功安装 wheel，`import pycaffe` 无错误
- **THEN** `libcaffe.so` 符号链接正确创建，动态库依赖完整解析

### Requirement: 推理验证测试

系统 SHALL 提供 `test_inference.py` 自动测试脚本，验证 pycaffe 核心功能完整性。

#### Scenario: LeNet 推理测试
- **WHEN** 在 Docker runtime 容器内执行 `python test_inference.py`
- **THEN** 11 项测试全部通过（导入、CPU 模式、Net 创建、前向传播、反向传播、Blob 属性、Layer 属性、参数、io.Transformer、net_spec、Protobuf 序列化）
- **THEN** LeNet 前向传播输出形状为 (64, 10)，Softmax 输出归一化正确

## MODIFIED Requirements

无。本次为新建 `pycaffe/` 目录，不修改现有代码。

## REMOVED Requirements

无。caffex 原始代码保留不动。

<!-- changelog -->
- 2026-07-22 | update | v1.1：新增 Docker 多阶段构建集成和推理验证测试两个 Requirement；更新版本号