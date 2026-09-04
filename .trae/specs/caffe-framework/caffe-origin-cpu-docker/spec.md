---
version: 1.0
---

# Caffe Origin CPU Docker 构建 caffex/python 模块 Spec

## Why

`docker/local/conda/Dockerfile` 已验证可在 Ubuntu 22.04 + Python 3.10 环境下编译 Caffe CPU 版本，但其多阶段构建同时包含 `caffex/python`（Make 方式）与 `pycaffe/`（scikit-build-core 迁移方式）两条路径，结构复杂、关注点耦合。需要在 `docker/origin/` 目录下从零构建一个**只针对 `caffex/python` 原始模块**的纯净 CPU 版本 Dockerfile，作为简化基线，便于独立维护、对照演化与不依赖现代打包工具链的场景使用。

## What Changes

- 在 `projects/xuanspace/vendor/caffe/docker/origin/` 目录下新建 `Dockerfile`，采用 4 阶段构建（`base-system` → `base-builder` → `builder` → `runtime`），去除参考模板中的 `builder-dev` 与 `pycaffe-builder` 阶段
- 新建 `docker/origin/scripts/generate-makefile-config.sh`：自动生成 `Makefile.config`（CPU_ONLY=1，OpenBLAS，Python 3.10 路径）
- 新建 `docker/origin/scripts/verify-caffe.sh`：验证 `import caffe` 与 Caffe 工具链完整性
- 新建 `docker/origin/build.sh`：构建脚本，自包含日志函数（不依赖 `docker/local/lib/`）
- 新建 `docker/origin/run.sh`：运行脚本，挂载源码并设置环境变量
- 新建 `docker/origin/README.md`：使用说明文档（构建方法、运行方法、环境变量、常见问题）
- 构建产物路径：`PYTHONPATH=/workspace/caffex/python`，`CAFFE_ROOT=/workspace/caffex`
- **BREAKING**：与 `docker/local/conda/Dockerfile` 不同，本 Dockerfile **不构建 pycaffe wheel**，仅通过 `make pycaffe` 生成 `_caffe.so` 并通过 `PYTHONPATH` 暴露 `caffex/python` 模块

## Impact

- Affected specs:
  - `caffe-conda-python314-docker`（参考模板来源，不修改，仅作为只读参考）
  - `caffe-pycaffe-migration`（互斥方案：本 spec 走原始 caffex/python 路径，pycaffe-migration 走 scikit-build-core 迁移路径，两者并存）
- Affected code:
  - `projects/xuanspace/vendor/caffe/docker/origin/`（全部新建）
  - `projects/xuanspace/vendor/caffe/caffex/`（只读源码，COPY 进镜像但不修改）
  - `projects/xuanspace/vendor/caffe/caffex/python/`（构建目标模块，产物为 `caffe/_caffe.so`）
- 不修改 `caffex/` 原始源码（如需兼容性补丁，在 Docker 构建过程中通过 `sed` 或 `patch` 应用）

## ADDED Requirements

### Requirement: Dockerfile 多阶段构建（4 阶段）

系统 SHALL 在 `docker/origin/Dockerfile` 中定义 4 个构建阶段：`base-system`（公共基础层）、`base-builder`（构建工具链 + Python 依赖）、`builder`（编译 Caffe 源码）、`runtime`（运行时镜像）。

#### Scenario: 构建阶段顺序

- **WHEN** 执行 `docker build --target runtime -f docker/origin/Dockerfile .`
- **THEN** Docker 按 `base-system` → `base-builder` → `builder` → `runtime` 顺序依次构建
- **THEN** 每个阶段基于前一阶段的镜像层，缓存可复用

#### Scenario: 不包含 pycaffe-builder 阶段

- **WHEN** 查看 `docker/origin/Dockerfile` 的所有 `FROM ... AS ...` 指令
- **THEN** 阶段名称集合为 `{base-system, base-builder, builder, runtime}`
- **THEN** 不存在 `pycaffe-builder` 阶段，也不存在 `scikit-build-core`、`python -m build`、`pip install *.whl` 相关指令

### Requirement: 基础系统层（base-system）

系统 SHALL 基于 `ubuntu:22.04` 创建 `base-system` 阶段，配置 Aliyun 镜像源、安装基础工具（ca-certificates、curl、wget、tzdata、libgomp1、procps），并设置 `DEBIAN_FRONTEND=noninteractive`、`LANG=C.UTF-8`、`LC_ALL=C.UTF-8`、`PIP_INDEX_URL=https://mirrors.aliyun.com/pypi/simple` 等环境变量。

#### Scenario: apt 换源

- **WHEN** `base-system` 阶段执行
- **THEN** `/etc/apt/sources.list` 中 `archive.ubuntu.com` 与 `security.ubuntu.com` 被替换为 `mirrors.aliyun.com`
- **THEN** `apt-get update` 可成功执行

### Requirement: 构建工具链层（base-builder）

系统 SHALL 在 `base-builder` 阶段安装 Caffe 编译所需的全部系统依赖（build-essential、cmake、git、libatlas-base-dev、libboost-all-dev、libgflags-dev、libgoogle-glog-dev、libhdf5-dev、libleveldb-dev、liblmdb-dev、libopencv-dev、libprotobuf-dev、libsnappy-dev、pkg-config、protobuf-compiler、python3-dev、python3-pip、python3-setuptools、python3-wheel），并通过 pip 安装 PyCaffe 运行时依赖（numpy<2.0、scipy、matplotlib、scikit-image、h5py、networkx、pandas、pyyaml、Pillow、six、Cython、ipython、nose、python-dateutil、protobuf==3.20.3、python-gflags、leveldb）。

#### Scenario: Python 依赖版本约束

- **WHEN** `base-builder` 阶段执行 `pip install`
- **THEN** `numpy` 版本约束为 `>=1.21,<2.0`（避免 ABI 不兼容）
- **THEN** `protobuf` 版本固定为 `3.20.3`（兼容 Caffe proto 定义）
- **THEN** `Cython` 版本 `>=0.29`（兼容 Python 3.10）

#### Scenario: 非 root 用户创建

- **WHEN** `base-builder` 阶段完成依赖安装
- **THEN** 创建 `builder` 用户（UID/GID 可通过 `ARG` 配置，默认 1000:1000）
- **THEN** 用户加入 `sudo` 组并配置 `NOPASSWD:ALL`
- **THEN** 创建 `/workspace` 目录并 chown 给 `builder` 用户
- **THEN** 设置 `CAFFE_ROOT=/workspace/caffex`、`PYTHONPATH=/workspace/caffex/python`、`LD_LIBRARY_PATH` 包含 `/workspace/caffex/build/lib`

### Requirement: Caffe 源码编译阶段（builder）

系统 SHALL 在 `builder` 阶段 COPY 本地 `caffex/` 源码到 `/workspace/caffex`，调用 `generate-makefile-config.sh` 生成 `Makefile.config`，依次执行 `make all -j$(nproc)`、`make pycaffe -j$(nproc)`、`make tools -j$(nproc)`、`make distribute`，并验证 `build/lib/libcaffe.so*` 与 `python/caffe/_caffe*.so` 存在。

#### Scenario: Makefile.config 自动生成

- **WHEN** `builder` 阶段执行 `generate-makefile-config.sh`
- **THEN** 在 `/workspace/caffex/Makefile.config` 生成配置文件
- **THEN** 文件包含 `CPU_ONLY := 1`、`BLAS := open`、`OPENCV_VERSION := 4`
- **THEN** `PYTHON_INCLUDE` 指向系统 Python 3.10 头文件路径与 NumPy 头文件路径
- **THEN** `PYTHON_LIBRARIES` 包含 `boost_python310` 与 `python3.10`
- **THEN** `INCLUDE_DIRS` 包含 `/usr/include/hdf5/serial`（若存在）与 `/usr/include/opencv4`
- **THEN** `CXXFLAGS` 包含 `-std=c++14` 与若干 `-Wno-*` 选项

#### Scenario: 编译产物存在

- **WHEN** `builder` 阶段完成 `make all pycaffe tools distribute`
- **THEN** `/workspace/caffex/build/lib/libcaffe.so.1.0.0` 存在
- **THEN** `/workspace/caffex/python/caffe/_caffe.so` 存在（符号链接指向 build 目录下的实际 .so）
- **THEN** `/workspace/caffex/build/tools/caffe` 可执行文件存在
- **THEN** `/workspace/caffex/distribute/` 目录包含完整的头文件、库文件与 Python 模块

### Requirement: 运行时镜像阶段（runtime）

系统 SHALL 在 `runtime` 阶段从 `builder` 复制 `build/`、`python/`、`distribute/`、`Makefile.config` 到 `/workspace/caffex/`，创建 `libcaffe.so` 符号链接并执行 `ldconfig`，调用 `verify-caffe.sh` 验证 `import caffe` 成功。

#### Scenario: libcaffe.so 符号链接

- **WHEN** `runtime` 阶段执行
- **THEN** 执行 `ln -sf /workspace/caffex/build/lib/libcaffe.so.1.0.0 /workspace/caffex/build/lib/libcaffe.so`
- **THEN** 执行 `ldconfig` 刷新动态链接器缓存
- **THEN** `ldd /workspace/caffex/python/caffe/_caffe.so` 无 "not found" 错误

#### Scenario: import caffe 验证

- **WHEN** `runtime` 阶段执行 `verify-caffe.sh`
- **THEN** 脚本输出 `Caffe imported successfully!` 与版本号
- **THEN** 脚本输出 `caffe_pb2 imported successfully`（protobuf 模块可用）
- **THEN** 脚本检查 `caffe`、`compute_image_mean`、`convert_imageset`、`upgrade_net_proto_text` 工具存在

### Requirement: 构建脚本（build.sh）

系统 SHALL 在 `docker/origin/build.sh` 提供构建脚本，封装 `docker build` 命令，支持 `-t TAG`、`-f DOCKERFILE`、`--target STAGE`、`--no-cache`、`--build-arg KEY=VAL` 参数，自包含日志函数（不依赖 `docker/local/lib/`），默认构建目标为 `runtime`。

#### Scenario: 默认构建

- **WHEN** 在 WSL2 环境执行 `cd docker/origin && ./build.sh`
- **THEN** 脚本调用 `docker build --target runtime -t caffe-cpu:latest -f Dockerfile ../../..`
- **THEN** 构建成功后输出镜像大小与构建耗时

#### Scenario: 容器工具检测

- **WHEN** 系统中 `docker` 命令不存在
- **THEN** 脚本检测 `wslc` 作为替代
- **THEN** 若两者均不存在，输出错误信息与安装指引并退出码 1

### Requirement: 运行脚本（run.sh）

系统 SHALL 在 `docker/origin/run.sh` 提供运行脚本，启动容器并挂载本地 `caffex/` 源码到 `/workspace`，设置 `CAFFE_ROOT`、`PYTHONPATH`、`LD_LIBRARY_PATH` 环境变量，默认以交互式 bash 进入容器。

#### Scenario: 默认交互式启动

- **WHEN** 执行 `./run.sh`
- **THEN** 启动容器 `caffe-dev`，挂载项目根目录到 `/workspace`
- **THEN** 容器内 `pwd` 显示 `/workspace/caffex`
- **THEN** 容器内 `python3 -c "import caffe"` 无错误

#### Scenario: 一次性命令执行

- **WHEN** 执行 `./run.sh -- python3 -c "import caffe; print(caffe.__version__)"`
- **THEN** 容器执行命令后自动删除（`--rm`）
- **THEN** 输出 Caffe 版本号

### Requirement: Makefile.config 生成脚本（generate-makefile-config.sh）

系统 SHALL 在 `docker/origin/scripts/generate-makefile-config.sh` 提供脚本，自动检测 Python 版本、Python 头文件路径、NumPy 头文件路径、Boost.Python 库名称、HDF5 路径，生成符合 CPU-only 构建要求的 `Makefile.config`。

#### Scenario: 自动检测 Python 路径

- **WHEN** 脚本在容器内执行
- **THEN** 通过 `python3 -c "import sysconfig; print(sysconfig.get_path('include'))"` 获取 Python 头文件路径
- **THEN** 通过 `python3 -c "import numpy; print(numpy.get_include())"` 获取 NumPy 头文件路径
- **THEN** 通过 `ldconfig -p | grep libboost_python` 检测可用的 Boost.Python 库

#### Scenario: Python 3.10 默认 Boost.Python

- **WHEN** `ldconfig` 未找到匹配的 `libboost_python*.so`
- **THEN** 根据 Python 版本回退到默认名称（Python 3.10 → `boost_python310`）

### Requirement: 验证脚本（verify-caffe.sh）

系统 SHALL 在 `docker/origin/scripts/verify-caffe.sh` 提供脚本，设置 `LD_LIBRARY_PATH` 与 `PYTHONPATH`，依次验证 Caffe 库文件、Python 依赖、`import caffe`、`caffe_pb2` 模块、Caffe 工具链。

#### Scenario: 验证失败时退出码非零

- **WHEN** `import caffe` 失败（如 `_caffe.so` 缺失或链接错误）
- **THEN** 脚本因 `set -e` 立即退出，退出码非零
- **THEN** Docker 构建在 `runtime` 阶段失败

### Requirement: 使用说明文档（README.md）

系统 SHALL 在 `docker/origin/README.md` 提供文档，包含：构建方法、运行方法、环境变量说明、目录挂载说明、与 `docker/local/conda` 的差异说明、常见问题排查、Python 3.10 兼容性说明。

#### Scenario: 文档结构完整

- **WHEN** 阅读 `docker/origin/README.md`
- **THEN** 包含「快速开始」「构建」「运行」「环境变量」「与 conda 版本的差异」「常见问题」六个章节
- **THEN** 每个章节有具体的命令示例

### Requirement: 脚本自包含

系统 SHALL 确保 `docker/origin/build.sh` 与 `docker/origin/run.sh` 自包含日志函数（`log_info`、`log_error`、`log_success`、`log_warn`、`log_header`、`log_section`、`log_kv`、`log_blank`），不依赖 `docker/local/lib/log.sh` 或 `docker/local/lib/check_env.sh`。

#### Scenario: 脚本独立运行

- **WHEN** 删除 `docker/local/lib/` 目录后执行 `docker/origin/build.sh`
- **THEN** 脚本正常执行，日志输出正常
- **THEN** 不报 `source: command not found` 或 `No such file` 错误

## MODIFIED Requirements

无。本次为新建 `docker/origin/` 目录，不修改 `docker/local/conda/` 或其他既有文件。

## REMOVED Requirements

无。本 spec 是新增 spec，不删除任何既有需求。

<!-- changelog -->
- 2026-07-24 | add | v1.0：初始版本，基于方法论编排（F→V→I→C）产出，定义 docker/origin/ 目录下 caffex/python CPU 构建 Dockerfile 的 9 项需求
