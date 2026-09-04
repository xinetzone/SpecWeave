---
version: 1.0
---

# Caffe + PyCaffe 独立 Docker 镜像 Spec

## Why

当前 `docker/modules/pycaffe/Dockerfile` 依赖 `caffe-cpu:python-module` 基础镜像，而 `python-module` 又依赖 `docker/local/conda/scripts/generate-makefile-config.sh`，形成两层间接依赖链。需要在 `docker/` 下创建全新的独立 Dockerfile 方案，基于 `ubuntu:26.04` 从零编译 Caffe 并构建 pycaffe wheel，消除所有 `python-module` 依赖。

## What Changes

- 在 `docker/standalone/pycaffe/` 下创建全新的独立 Dockerfile，基于 `ubuntu:26.04`
- 采用多阶段构建：base-system → base-builder → caffe-builder → pycaffe-builder → runtime
- 参考 `docker/local/conda/Dockerfile` 的多阶段架构和 `docker/modules/pycaffe/Dockerfile` 的 pycaffe wheel 构建参数
- 内联 Makefile.config 生成逻辑（不再依赖外部 `generate-makefile-config.sh` 脚本）
- 复制 `docker/modules/pycaffe/scripts/` 验证脚本到新目录
- 创建 `docker/standalone/pycaffe/Makefile` 作为统一构建入口

## Impact

- Affected specs: 无（全新模块，不影响现有 spec）
- Affected code: `docker/standalone/pycaffe/`（新建）、`docker/modules/pycaffe/`（只读参考，不修改）
- 不修改任何现有文件

## ADDED Requirements

### Requirement: 独立多阶段 Dockerfile

系统 SHALL 在 `docker/standalone/pycaffe/Dockerfile` 提供基于 `ubuntu:26.04` 的多阶段 Docker 构建文件，包含以下阶段：

- **base-system**: 基础系统环境（apt 换源、CA 证书、基础工具）
- **base-builder**: 构建环境（C++ 编译器、Caffe 系统依赖、Python 3、科学计算包）
- **caffe-builder**: Caffe 编译（从 `caffex/` 源码编译，生成 `libcaffe.so`、`_caffe.so`、tools）
- **pycaffe-builder**: PyCaffe wheel 构建（从 `python/pycaffe/` 源码，使用 scikit-build-core 构建 wheel）
- **runtime**: 运行时镜像（合并 Caffe 编译产物 + pycaffe wheel 安装，最终可运行镜像）

#### Scenario: 完整构建流程

- **WHEN** 执行 `make -C docker/standalone/pycaffe all`
- **THEN** 依次构建 base-system → base-builder → caffe-builder → pycaffe-builder → runtime 五个阶段
- **THEN** 最终产出 `caffe-cpu:standalone-pycaffe` 镜像

#### Scenario: 仅构建到 caffe-builder 阶段

- **WHEN** 执行 `docker build --target caffe-builder -t caffe-cpu:standalone-caffe -f docker/standalone/pycaffe/Dockerfile .`
- **THEN** 产出包含已编译 Caffe 的镜像，不含 pycaffe wheel

### Requirement: 内联 Makefile.config 生成

系统 SHALL 在 Dockerfile 内直接生成 `Makefile.config`，不依赖外部 `generate-makefile-config.sh` 脚本。配置应包含：

- `CPU_ONLY := 1`
- `BLAS := open`
- Python include/lib 路径自动探测
- Boost.Python 库自动探测
- C++14 编译标准
- HDF5 serial 路径支持

#### Scenario: Makefile.config 自动生成

- **WHEN** caffe-builder 阶段执行
- **THEN** 在 `/workspace/caffex/` 下自动生成 `Makefile.config`
- **THEN** 配置包含 CPU_ONLY、BLAS、Python 路径、Boost.Python 库名等必要参数

### Requirement: PyCaffe wheel 构建参数

系统 SHALL 使用与 `docker/modules/pycaffe/Dockerfile` 一致的 scikit-build-core 构建参数：

- `cmake.define.CONDA_PREFIX` 指向 Caffe 编译产物目录
- `cmake.define.CAFFE_INCLUDE_DIR` 指向 Caffe 头文件目录
- `cmake.define.CAFFE_LIBRARY` 指向 `libcaffe.so` 路径
- 使用 `--no-isolation` 跳过隔离环境

#### Scenario: wheel 构建成功

- **WHEN** pycaffe-builder 阶段执行 `python -m build --wheel`
- **THEN** 在 `dist/` 目录下生成 `pycaffe-*.whl` 文件
- **THEN** wheel 包含 `_caffe.so` 扩展模块

### Requirement: 运行时验证

系统 SHALL 在 runtime 阶段执行验证，确保：

- `import pycaffe` 成功
- `pycaffe.Net` 类可用
- `pycaffe.set_mode_cpu()` 正常工作
- LeNet 前向传播通过（若 prototxt 存在）
- 所有 Solver 类可用

#### Scenario: 镜像验证通过

- **WHEN** runtime 镜像构建完成
- **THEN** `pycaffe` 导入成功且版本号可获取
- **THEN** 所有验证脚本通过

### Requirement: 统一构建入口 Makefile

系统 SHALL 在 `docker/standalone/pycaffe/Makefile` 提供统一构建入口，支持以下目标：

- `all`: 完整构建 runtime 镜像
- `caffe-builder`: 仅构建到 Caffe 编译阶段
- `clean`: 清理构建产物

#### Scenario: Makefile 构建

- **WHEN** 执行 `make -C docker/standalone/pycaffe all`
- **THEN** 使用正确的 Dockerfile 路径和构建上下文构建镜像
- **THEN** 构建完成后自动运行验证脚本

### Requirement: 验证脚本复用

系统 SHALL 将 `docker/modules/pycaffe/scripts/verify-pycaffe.sh` 和 `docker/modules/pycaffe/scripts/verify-parity.sh` 复制到 `docker/standalone/pycaffe/scripts/`，保持验证逻辑一致。

#### Scenario: 验证脚本可复用

- **WHEN** 复制验证脚本到新目录
- **THEN** 脚本内容与源文件一致
- **THEN** 脚本在 runtime 镜像中可正常执行