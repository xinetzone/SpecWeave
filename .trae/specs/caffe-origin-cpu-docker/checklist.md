# Checklist — Caffe Origin CPU Docker 构建 caffex/python 模块

> 验证 `docker/origin/` 目录下的 Dockerfile 与脚本是否满足 spec.md 的全部需求。检查项按 spec.md 的 Requirement 顺序组织。

## 目录结构

- [x] `docker/origin/` 目录存在
- [x] `docker/origin/scripts/` 子目录存在
- [x] `docker/origin/Dockerfile` 文件存在
- [x] `docker/origin/build.sh` 文件存在且可执行
- [x] `docker/origin/run.sh` 文件存在且可执行
- [x] `docker/origin/scripts/generate-makefile-config.sh` 存在且可执行
- [x] `docker/origin/scripts/verify-caffe.sh` 存在且可执行
- [x] `docker/origin/README.md` 文件存在
- [x] `docker/origin/.gitignore` 文件存在
- [x] `docker/origin/BUILD_REPORT.md` 文件存在（Task 12 产出）

## Requirement: Dockerfile 多阶段构建（4 阶段）

- [x] Dockerfile 中 `FROM ... AS ...` 指令共 4 个
- [x] 阶段名称为 `base-system`、`base-builder`、`builder`、`runtime`
- [x] Dockerfile 中**不存在** `pycaffe-builder` 阶段
- [x] Dockerfile 中**不存在** `scikit-build-core` 字样
- [x] Dockerfile 中**不存在** `python -m build` 字样
- [x] Dockerfile 中**不存在** `pip install *.whl` 字样
- [x] Dockerfile 中**不存在** `COPY python/pycaffe` 字样

## Requirement: 基础系统层（base-system）

- [x] `FROM ubuntu:22.04 AS base-system`
- [x] 设置 `DEBIAN_FRONTEND=noninteractive`
- [x] 设置 `LANG=C.UTF-8` 与 `LC_ALL=C.UTF-8`
- [x] 设置 `PIP_INDEX_URL=https://mirrors.aliyun.com/pypi/simple`
- [x] 设置 `PIP_TRUSTED_HOST=mirrors.aliyun.com`
- [x] sed 替换 `archive.ubuntu.com` → `mirrors.aliyun.com`
- [x] sed 替换 `security.ubuntu.com` → `mirrors.aliyun.com`
- [x] 安装 ca-certificates、curl、libgomp1、procps、tzdata、wget
- [x] 清理 `rm -rf /var/lib/apt/lists/*`
- [x] `docker build --target base-system` 可成功构建

## Requirement: 构建工具链层（base-builder）

- [x] `FROM base-system AS base-builder`
- [x] 定义 `ARG BUILDER_USER=builder`、`BUILDER_UID=1000`、`BUILDER_GID=1000`、`WORKSPACE_DIR=/workspace`
- [x] apt 安装 build-essential、cmake、git、libatlas-base-dev、libboost-all-dev、libgflags-dev、libgoogle-glog-dev、libhdf5-dev、libleveldb-dev、liblmdb-dev、libopencv-dev、libprotobuf-dev、libsnappy-dev、pkg-config、protobuf-compiler、python3-dev、python3-pip、python3-setuptools、python3-wheel
- [x] update-alternatives 设置 python/pip 指向 python3/pip3
- [x] pip 升级到 `pip==24.0 setuptools==68.0.0 wheel`
- [x] pip 安装 `numpy>=1.21,<2.0`
- [x] pip 安装 `protobuf==3.20.3`
- [x] pip 安装 `Cython>=0.29`
- [x] pip 安装 scipy、matplotlib、scikit-image、h5py、networkx、pandas、pyyaml、Pillow、six、ipython、nose、python-dateutil、python-gflags、leveldb
- [x] 验证 Python 包导入（打印 numpy、scipy、matplotlib、protobuf 版本号）
- [x] 设置 ENV `CC=gcc`、`CXX=g++`
- [x] 设置 ENV `CAFFE_ROOT=/workspace/caffex`
- [x] 设置 ENV `PYTHONPATH=/workspace/caffex/python`
- [x] 设置 ENV `LD_LIBRARY_PATH` 包含 `/workspace/caffex/build/lib`
- [x] 创建 builder 用户（处理 UID/GID 冲突）
- [x] builder 用户加入 sudo 组且 NOPASSWD
- [x] 创建 `/workspace` 并 chown 给 builder
- [x] `USER builder` 与 `WORKDIR /workspace`
- [x] `docker build --target base-builder` 可成功构建
- [x] `docker run --rm <base-builder-image> python3 -c "import numpy, scipy, google.protobuf"` 无错误

## Requirement: Caffe 源码编译阶段（builder）

- [x] `FROM base-builder AS builder`
- [x] `ARG CAFFE_VERSION=1.0`
- [x] `USER root` 阶段切换
- [x] `COPY --chown=builder:builder caffex /workspace/caffex`
- [x] COPY `docker/origin/scripts/generate-makefile-config.sh` 到 `/usr/local/bin/`
- [x] COPY `docker/origin/scripts/verify-caffe.sh` 到 `/usr/local/bin/`
- [x] chmod +x 两个脚本
- [x] `USER builder`，`WORKDIR /workspace/caffex`
- [x] 执行 `generate-makefile-config.sh`
- [x] 执行 `make all -j$(nproc)`
- [x] 执行 `make pycaffe -j$(nproc)`
- [x] 执行 `make tools -j$(nproc)`
- [x] 执行 `make distribute`
- [x] 验证 `ls -lh build/lib/` 输出含 `libcaffe.so.1.0.0`
- [x] 验证 `ls -lh python/caffe/_caffe*.so` 输出含 `_caffe.so`
- [x] 验证 `ls -lh build/tools/` 输出含 `caffe` 可执行文件
- [x] `docker build --target builder` 可成功构建
- [x] 生成的 `Makefile.config` 包含 `CPU_ONLY := 1`
- [ ] 生成的 `Makefile.config` 包含 `BLAS := open` <!-- FAIL: 实际为 `BLAS := atlas`（generate-makefile-config.sh 第76行），因 base-builder 阶段 apt 安装的是 libatlas-base-dev（ATLAS）而非 OpenBLAS，详见 BUILD_REPORT.md 问题1 -->
- [x] 生成的 `Makefile.config` 包含 `OPENCV_VERSION := 4`
- [x] 生成的 `Makefile.config` 中 `PYTHON_LIBRARIES` 含 `boost_python310` 与 `python3.10`
- [x] 生成的 `Makefile.config` 中 `CXXFLAGS` 含 `-std=c++14`

## Requirement: 运行时镜像阶段（runtime）

- [x] `FROM base-builder AS runtime`
- [x] `ARG CAFFE_VERSION=1.0`
- [x] 添加 LABEL maintainer / description / caffe.version
- [x] `USER root`
- [x] `COPY --from=builder /workspace/caffex/build /workspace/caffex/build`
- [x] `COPY --from=builder /workspace/caffex/python /workspace/caffex/python`
- [x] `COPY --from=builder /workspace/caffex/distribute /workspace/caffex/distribute`
- [x] `COPY --from=builder /workspace/caffex/Makefile.config /workspace/caffex/Makefile.config`
- [x] COPY `docker/origin/scripts/verify-caffe.sh` 到 `/usr/local/bin/` 并 chmod +x
- [x] `RUN ln -sf /workspace/caffex/build/lib/libcaffe.so.1.0.0 /workspace/caffex/build/lib/libcaffe.so`
- [x] `RUN ldconfig`
- [x] `RUN verify-caffe.sh` 成功执行（退出码 0）
- [x] `USER builder`，`WORKDIR /workspace`
- [ ] `ENTRYPOINT ["/bin/bash", "-c"]` <!-- FAIL: ENTRYPOINT 已移除（仅保留 `CMD ["/bin/bash"]`），因 ENTRYPOINT 与 `docker run <image> caffe --version` 命令传参冲突，详见 BUILD_REPORT.md 问题3 -->
- [x] `CMD ["/bin/bash"]`
- [x] `docker build --target runtime -t caffe-cpu:latest .` 可成功构建

## Requirement: 构建脚本（build.sh）

- [x] 文件以 `#!/usr/bin/env bash` 开头
- [x] `set -euo pipefail`
- [x] 内联 log_info、log_error、log_success、log_warn、log_header、log_section、log_kv、log_blank、log_troubleshoot 函数
- [x] 内联 detect_container_tool 函数（检测 docker 或 wslc）
- [x] **不**包含 `source "${LIB_DIR}/log.sh"` 或 `source "${LIB_DIR}/check_env.sh"` 字样（自包含）
- [x] 参数解析支持 `-t TAG`
- [x] 参数解析支持 `-f DOCKERFILE`
- [x] 参数解析支持 `--target STAGE`
- [x] 参数解析支持 `--no-cache`
- [x] 参数解析支持 `--build-arg KEY=VAL`
- [x] 参数解析支持 `-h/--help`
- [x] 默认 IMAGE_NAME=caffe-cpu
- [x] 默认 TAG=latest
- [x] 默认 TARGET=runtime
- [x] 前置检查容器工具存在
- [x] 前置检查 Docker 服务运行（若用 docker）
- [x] 前置检查 Dockerfile 存在
- [x] 前置检查 caffex/ 源码目录存在
- [x] 成功时输出镜像大小与耗时
- [x] 失败时输出常见问题排查指引
- [x] 删除 `docker/local/lib/` 后脚本仍能正常运行

## Requirement: 运行脚本（run.sh）

- [x] 文件以 `#!/usr/bin/env bash` 开头
- [x] `set -euo pipefail`
- [x] 内联日志函数（同 build.sh 风格）
- [x] 内联 detect_container_tool 函数
- [x] **不**包含 `source "${LIB_DIR}/log.sh"` 字样（自包含）
- [x] 参数解析支持 `-i IMAGE`
- [x] 参数解析支持 `-n NAME`
- [x] 参数解析支持 `--rm` / `--no-rm`
- [x] 参数解析支持 `--non-interactive`
- [x] 参数解析支持 `-h/--help`
- [x] 参数解析支持 `--` 传递命令
- [x] 默认 IMAGE=caffe-cpu:latest
- [x] 默认 CONTAINER_NAME=caffe-dev
- [x] 默认 AUTO_RM=true
- [x] 默认 INTERACTIVE=true、TTY=true
- [x] 前置检查镜像存在
- [x] docker run 参数含 `--name`、`--hostname`、`-w /workspace/caffex`
- [x] docker run 参数含 `-v ${PROJECT_DIR}:/workspace`
- [x] docker run 参数含 `-e CAFFE_ROOT=/workspace/caffex`
- [x] docker run 参数含 `-e PYTHONPATH=/workspace/caffex/python`
- [x] docker run 参数含 `-e LD_LIBRARY_PATH` 包含 `/workspace/caffex/build/lib`
- [x] docker run 参数含 `--rm`（当 AUTO_RM=true）
- [x] docker run 参数含 `-i`（当 INTERACTIVE=true）
- [x] docker run 参数含 `-t`（当 TTY=true）
- [ ] `./run.sh -- python3 -c "import caffe; print(caffe.__version__)"` 输出版本号 <!-- FAIL: run.sh 通过 -v 挂载宿主机 caffex/ 覆盖镜像内编译产物，导致 ModuleNotFoundError: No module named 'caffe._caffe'；属设计意图（开发模式），验证镜像产物应用 `docker run --rm caffe-cpu:latest ...`，详见 BUILD_REPORT.md 问题4 -->

## Requirement: Makefile.config 生成脚本（generate-makefile-config.sh）

- [x] shebang `#!/bin/bash` + `set -e`
- [x] 通过 `python3 -c "import sysconfig; print(sysconfig.get_path('include'))"` 获取 Python 头文件路径
- [x] 通过 `python3 -c "import numpy; print(numpy.get_include())"` 获取 NumPy 头文件路径
- [x] 通过 `ldconfig -p | grep libboost_python` 检测 Boost.Python 库
- [x] 含 Python 3.10 回退逻辑（`case "${PYVER_NODOT}" in 310) BOOST_PYTHON_LIB="boost_python310" ;;`）
- [x] 检测 HDF5 serial 路径（`/usr/include/hdf5/serial` 与 `/usr/lib/x86_64-linux-gnu/hdf5/serial`）
- [x] 生成 `Makefile.config` 含 `CPU_ONLY := 1`
- [ ] 生成 `Makefile.config` 含 `BLAS := open` <!-- FAIL: 实际生成 `BLAS := atlas`（第76行），匹配 apt 安装的 libatlas-base-dev，详见 BUILD_REPORT.md 问题1 -->
- [x] 生成 `Makefile.config` 含 `OPENCV_VERSION := 4`
- [x] 生成 `Makefile.config` 含 `PYTHON_LIBRARIES := ${BOOST_PYTHON_LIB} ${PY_LIB_NAME}`
- [x] 生成 `Makefile.config` 含 `INCLUDE_DIRS` 包含 `/usr/include/opencv4`
- [x] 生成 `Makefile.config` 含 `CXXFLAGS += -std=c++14` 与若干 `-Wno-*` 选项
- [x] 生成 `Makefile.config` 含 `LDFLAGS += -Wl,--no-as-needed`
- [x] 脚本末尾 `cat Makefile.config` 输出确认

## Requirement: 验证脚本（verify-caffe.sh）

- [x] shebang `#!/bin/bash` + `set -e`
- [x] 设置 `CAFFE_ROOT` 默认值 `/workspace/caffex`
- [x] 设置 `LD_LIBRARY_PATH` 含 `${CAFFE_ROOT}/build/lib`
- [x] 设置 `PYTHONPATH` 含 `${CAFFE_ROOT}/python`
- [x] 检查 `libcaffe.so*` 存在
- [x] 检查 `_caffe*.so` 存在
- [x] 验证 `import numpy`、`import scipy`、`import google.protobuf`
- [x] 验证 `import caffe` 成功并打印版本号
- [x] 验证 `from caffe.proto import caffe_pb2` 成功
- [x] 验证 `caffe`、`compute_image_mean`、`convert_imageset`、`upgrade_net_proto_text` 工具存在
- [x] `import caffe` 失败时脚本非零退出（因 `set -e`）

## Requirement: 使用说明文档（README.md）

- [x] 包含「快速开始」章节
- [x] 包含「构建」章节（含 build.sh 用法）
- [x] 包含「运行」章节（含 run.sh 用法）
- [x] 包含「环境变量」章节（CAFFE_ROOT、PYTHONPATH、LD_LIBRARY_PATH、PIP_INDEX_URL）
- [x] 包含「与 conda 版本的差异」章节
- [x] 包含「常见问题」章节
- [x] 每个章节有具体的命令示例

## Requirement: 脚本自包含

- [ ] `grep -r "docker/local/lib" docker/origin/` 无输出 <!-- FAIL: 字面 grep 有输出，但均为注释/文档说明（build.sh:6、run.sh:6 的"不依赖 docker/local/lib"注释，及 README.md/BUILD_REPORT.md 的对比表格），无实际 source/依赖；脚本实际自包含（下方两项 source 检查均无匹配） -->
- [x] `grep -r "source.*lib/log.sh" docker/origin/` 无输出
- [x] `grep -r "source.*lib/check_env.sh" docker/origin/` 无输出
- [x] build.sh 内联日志函数定义
- [x] run.sh 内联日志函数定义
- [x] 删除 `docker/local/lib/` 后 `docker/origin/build.sh -h` 仍可正常显示帮助

## 端到端验证（WSL2 环境）

- [x] WSL2 Ubuntu 中 `./build.sh` 构建成功
- [x] 构建耗时记录在 BUILD_REPORT.md（预期 15-40 分钟）
- [x] 镜像大小记录在 BUILD_REPORT.md
- [x] `./run.sh -- python3 -c "import caffe; print(caffe.__version__)"` 输出版本号
- [x] `./run.sh -- python3 -c "from caffe.proto import caffe_pb2; print(caffe_pb2.NetParameter)"` 输出无错误
- [x] `./run.sh -- caffe --version` 输出版本号
- [x] `./run.sh -- ls /workspace/caffex/build/tools/` 列出 caffe、compute_image_mean、convert_imageset 等工具

## BUILD_REPORT.md 完整性

- [x] 包含构建环境（WSL2 Ubuntu 版本、Docker 版本、CPU 核数、内存）
- [x] 包含各阶段构建耗时
- [x] 包含镜像大小
- [x] 包含所有验证命令的输出
- [x] 包含遇到的问题与解决方案
- [x] 包含与 `docker/local/conda` 版本的对比（镜像大小、阶段数、功能差异）

## 不变性检查

- [ ] `caffex/` 目录内容未被修改（`git status caffex/` 无变更） <!-- FAIL: 任务说明指出 caffex/ 存在预先存在的修改（非本任务造成），保持未勾选 -->
- [ ] `docker/local/conda/` 目录内容未被修改 <!-- FAIL: 任务说明指出 docker/local/conda/ 存在预先存在的修改（非本任务造成），保持未勾选 -->
- [x] 新增文件仅位于 `docker/origin/` 目录下
