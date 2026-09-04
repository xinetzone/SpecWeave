---
version: 1.0
---

# Caffe Conda Python 3.14 Docker 镜像 - Product Requirement Document

## Overview
- **Summary**: 为 BVLC Caffe 深度学习框架创建基于官方 conda 基础镜像的现代化 Docker 镜像，使用 Python 3.14 环境，在 WSL2 (Windows Subsystem for Linux) 环境中完成构建，优化镜像大小，确保 Caffe 及其 PyCaffe Python 绑定能正常运行。
- **Purpose**: 替代原有的基于 ubuntu:16.04 + Python 2 的老旧 Dockerfile，提供一个现代化、可维护、基于 conda 环境管理的 Caffe 运行/开发镜像，解决旧镜像的安全漏洞、Python 版本过旧、依赖冲突等问题。
- **Target Users**: Caffe 框架的开发者、研究者，需要在现代 Python 环境中使用 Caffe 的用户，WSL2 环境下的深度学习开发人员。

## Goals
- 使用官方 conda 基础镜像（Miniconda3 或 Mambaforge）作为构建起点
- 配置完整的 Python 3.14 conda 环境
- 成功编译 Caffe（CPU 版本）并启用 PyCaffe Python 绑定
- 安装所有必要的系统依赖和 Python 依赖
- 优化镜像大小（多阶段构建、缓存清理）
- 设置适当的工作目录和环境变量
- 确保在 WSL2 Ubuntu 环境中能够顺利构建
- 生成可移植的 Docker 镜像（可通过 docker save 导出为 tar 文件）
- 验证 `import caffe` 在容器内能正常工作

## Non-Goals (Out of Scope)
- 不包含 GPU/CUDA 支持（本次仅构建 CPU 版本）
- 不修改 caffex/ 目录下的原始 Caffe 源码
- 不构建 Caffe 的 MATLAB 绑定
- 不包含预训练模型或示例数据集下载
- 不支持多架构构建（仅 Linux x86_64）
- 不推送到 Docker Hub（仅本地构建和导出）
- 不解决 Python 3.14 与 Caffe 旧代码的兼容性问题（如果遇到兼容性问题，需要打补丁）

## Background &amp; Context
- **现有状态**: `caffex/docker/cpu/Dockerfile` 基于 ubuntu:16.04，使用 Python 2.7，依赖版本极旧，无法在现代环境中使用
- **Python 3.14 现状**: Python 3.14 是较新的版本，conda-forge 可能已有支持，但部分 C++ 依赖（如 Boost、protobuf）需要确认兼容性
- **Caffe 依赖**: Caffe 需要 BLAS、Boost、protobuf、glog、gflags、hdf5、leveldb、lmdb、snappy、OpenCV 等系统库，以及 numpy、scipy、protobuf 等 Python 包
- **WSL2 环境**: WSL2 Ubuntu 24.04 已具备 Docker 运行环境（之前 XMNN 项目已验证）
- **先前经验**: 之前为 XMNN 项目创建过基于 conda + environment.yml 的 Docker 镜像，有可复用的模式

## Functional Requirements
- **FR-1**: Dockerfile 基于官方 conda 镜像（优先 continuumio/miniconda3 或 condaforge/miniforge3）
- **FR-2**: 镜像内创建名为 `caffe` 的 conda 环境，Python 版本固定为 3.14
- **FR-3**: 安装所有 Caffe 编译所需的系统依赖（build-essential, cmake, git, wget, libblas-dev, libboost-all-dev, libgflags-dev, libgoogle-glog-dev, libhdf5-dev, libleveldb-dev, liblmdb-dev, libopencv-dev, libprotobuf-dev, libsnappy-dev, protobuf-compiler）
- **FR-4**: 通过 conda 或 pip 安装 PyCaffe 所需的 Python 依赖（numpy, scipy, scikit-image, matplotlib, h5py, leveldb, networkx, pandas, protobuf, pyyaml, Pillow, six, Cython）
- **FR-5**: 在容器内编译 Caffe CPU-only 版本，启用 PyCaffe 绑定
- **FR-6**: 设置正确的环境变量（CAFFE_ROOT, PYTHONPATH, PATH, LD_LIBRARY_PATH）
- **FR-7**: 设置工作目录为 `/workspace`
- **FR-8**: 采用多阶段构建优化镜像大小，清理 apt 和 conda/pip 缓存
- **FR-9**: 创建非 root 用户（可选但推荐）用于运行 Caffe
- **FR-10**: 提供构建脚本 `build-docker.sh` 便于在 WSL2 中一键构建
- **FR-11**: 提供运行脚本 `run-docker.sh` 验证镜像功能
- **FR-12**: 镜像构建后能够成功执行 `python -c "import caffe; print(caffe.__version__)"`

## Non-Functional Requirements
- **NFR-1**: 镜像大小应控制在 3GB 以内（包含编译工具链和完整 conda 环境）
- **NFR-2**: 构建过程在 WSL2 Ubuntu 环境中，8 核 CPU + 16GB 内存条件下应在 60 分钟内完成
- **NFR-3**: Dockerfile 应有清晰的注释说明每个阶段的作用
- **NFR-4**: 镜像应支持通过 `docker run -v $(pwd):/workspace` 挂载本地目录
- **NFR-5**: 构建失败时应有明确的错误信息输出

## Constraints
- **Technical**:
  - 仅支持 Linux x86_64 架构
  - Python 版本固定为 3.14（即使某些依赖版本可能需要兼容处理）
  - 仅 CPU 版本，不包含 CUDA
  - 使用 WSL2 (Ubuntu 24.04) + Docker 环境构建
  - 不修改 caffex/ 原始源码（如需兼容性补丁，在 Docker 构建过程中通过 sed 或 patch 应用）
- **Business**:
  - 交付物为 Dockerfile + 构建/运行脚本，位于 `d:\spaces\SpecWeave\external\chaos\caffe\docker\conda-cpu\` 目录
- **Dependencies**:
  - WSL2 环境中已安装 Docker
  - 网络连接正常（可下载 conda 包和 apt 包）
  - 本地已有 caffex/ 源码（不 git clone 远程仓库）

## Assumptions
- Python 3.14 在 conda-forge 上已有可用的包
- Caffe C++ 代码能够在现代 gcc (gcc 11/12) 下编译（可能需要少量编译标志调整）
- PyCaffe 的 Cython 绑定能够在 Python 3.14 下编译
- WSL2 环境已有足够的磁盘空间（至少 10GB 可用空间用于构建）
- 用户在 WSL2 中能够访问 `/mnt/d/spaces/SpecWeave/external/chaos/caffe` 目录

## Acceptance Criteria

### AC-1: Dockerfile 存在且语法正确
- **Given**: 在 `d:\spaces\SpecWeave\external\chaos\caffe\docker\conda-cpu\` 目录下
- **When**: 查看 Dockerfile 文件
- **Then**: Dockerfile 存在，以官方 conda 镜像为基础，语法正确可被 docker build 解析
- **Verification**: `programmatic`
- **Notes**: 可通过 `docker build --help` 或 hadolint 验证语法

### AC-2: Conda 环境正确创建且 Python 版本为 3.14
- **Given**: Docker 镜像构建完成
- **When**: 在容器内执行 `conda run -n caffe python --version`
- **Then**: 输出显示 Python 3.14.x
- **Verification**: `programmatic`

### AC-3: Caffe 编译成功且 PyCaffe 可导入
- **Given**: Docker 镜像构建完成
- **When**: 在容器内执行 `conda run -n caffe python -c "import caffe; print('Caffe imported successfully')"`
- **Then**: 无错误输出，成功打印 "Caffe imported successfully"
- **Verification**: `programmatic`

### AC-4: caffe 命令行工具可用
- **Given**: Docker 镜像构建完成
- **When**: 在容器内执行 `caffe --version`
- **Then**: 输出 Caffe 版本信息
- **Verification**: `programmatic`

### AC-5: 工作目录和环境变量正确设置
- **Given**: Docker 镜像构建完成
- **When**: 启动容器并执行 `pwd &amp;&amp; echo $CAFFE_ROOT &amp;&amp; echo $PYTHONPATH`
- **Then**: pwd 显示 `/workspace`，CAFFE_ROOT 指向 Caffe 安装目录，PYTHONPATH 包含 PyCaffe 路径
- **Verification**: `programmatic`

### AC-6: 构建脚本可在 WSL2 中执行
- **Given**: 在 WSL2 环境中，进入项目目录
- **When**: 执行 `./docker/conda-cpu/build-docker.sh`
- **Then**: Docker 镜像成功构建，标签为 `caffe:conda-py314-cpu`
- **Verification**: `programmatic`

### AC-7: 镜像可导出为可移植 tar 文件
- **Given**: Docker 镜像构建成功
- **When**: 执行 `docker save -o caffe-conda-py314-cpu.tar caffe:conda-py314-cpu`
- **Then**: tar 文件成功生成
- **Verification**: `programmatic`

### AC-8: 镜像大小合理
- **Given**: Docker 镜像构建完成
- **When**: 执行 `docker images caffe:conda-py314-cpu`
- **Then**: 镜像大小不超过 3GB
- **Verification**: `programmatic`

### AC-9: 本地目录挂载可正常工作
- **Given**: Docker 镜像构建完成
- **When**: 执行 `docker run --rm -v $(pwd):/workspace caffe:conda-py314-cpu ls /workspace`
- **Then**: 能正确列出挂载目录的内容
- **Verification**: `programmatic`

## Open Questions
- [ ] Python 3.14 与 Caffe 的 C++/Cython 代码是否存在兼容性问题？如果存在，需要哪些补丁？
- [ ] 应该使用 Miniconda3（Anaconda 官方）还是 Mambaforge（conda-forge，mamba 更快）？
- [ ] 是否需要在镜像中包含 Jupyter Notebook/Lab 便于交互式开发？
- [ ] 是否需要包含 OpenCV 的 Python 绑定？
- [ ] 编译时使用 Make 还是 CMake？（CMake 更现代但配置复杂，Make 更直接但需要调整 Makefile.config）
