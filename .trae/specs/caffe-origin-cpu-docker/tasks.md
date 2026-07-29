# Tasks

> 基于 `docker/local/conda/Dockerfile` 参考模板，在 `docker/origin/` 目录从零构建 `caffex/python` CPU 版本 Dockerfile。所有任务文件路径相对于 `projects/xuanspace/vendor/caffe/`。

- [x] Task 1: 创建 `docker/origin/` 目录结构
  - [x] SubTask 1.1: 创建 `docker/origin/` 主目录
  - [x] SubTask 1.2: 创建 `docker/origin/scripts/` 子目录
  - [x] SubTask 1.3: 创建 `.gitignore`（忽略 docker build 缓存与临时文件）
  - **Acceptance Criteria**: [AC-DIR] 目录结构存在且为空
  - **Test**: `ls -la docker/origin/` 与 `ls -la docker/origin/scripts/` 均可执行

- [x] Task 2: 编写 `scripts/generate-makefile-config.sh`
  - [x] SubTask 2.1: 参考 `docker/local/conda/scripts/generate-makefile-config.sh` 编写脚本，自动检测 Python 版本与头文件路径
  - [x] SubTask 2.2: 实现 Boost.Python 库名称自动检测（含 Python 3.10 回退逻辑）
  - [x] SubTask 2.3: 生成 `Makefile.config` 内容（CPU_ONLY=1、BLAS=open、OPENCV_VERSION=4、CXXFLAGS=-std=c++14 + -Wno-* 选项）
  - [x] SubTask 2.4: 添加 `set -e` 与 echo 调试输出
  - **Acceptance Criteria**: [AC-MAKEFILE-GEN] 脚本可执行，在 Ubuntu 22.04 + Python 3.10 容器内运行后生成正确 `Makefile.config`
  - **Test**: 在 base-builder 阶段执行脚本，检查 `Makefile.config` 包含 `CPU_ONLY := 1`、`BLAS := open`、`PYTHON_LIBRARIES := boost_python310 python3.10`

- [x] Task 3: 编写 `scripts/verify-caffe.sh`
  - [x] SubTask 3.1: 参考 `docker/local/conda/scripts/verify-caffe.sh` 编写脚本
  - [x] SubTask 3.2: 设置 `LD_LIBRARY_PATH` 与 `PYTHONPATH` 环境变量
  - [x] SubTask 3.3: 验证 Caffe 库文件（`libcaffe.so*`、`_caffe*.so`）存在
  - [x] SubTask 3.4: 验证 Python 依赖（numpy、scipy、protobuf）可导入
  - [x] SubTask 3.5: 验证 `import caffe` 成功并打印版本号
  - [x] SubTask 3.6: 验证 `caffe_pb2` 模块可导入
  - [x] SubTask 3.7: 验证 Caffe 工具链（caffe、compute_image_mean、convert_imageset、upgrade_net_proto_text）
  - **Acceptance Criteria**: [AC-VERIFY] 脚本执行成功退出码 0；若 `import caffe` 失败则非零退出
  - **Test**: 在 runtime 阶段执行脚本，输出 `Caffe imported successfully!`

- [x] Task 4: 编写 `Dockerfile` 的 `base-system` 阶段
  - [x] SubTask 4.1: `FROM ubuntu:22.04 AS base-system`
  - [x] SubTask 4.2: 设置 `DEBIAN_FRONTEND=noninteractive`、`LANG=C.UTF-8`、`LC_ALL=C.UTF-8`、`PIP_INDEX_URL=https://mirrors.aliyun.com/pypi/simple`、`PIP_TRUSTED_HOST=mirrors.aliyun.com`、`PIP_DISABLE_PIP_VERSION_CHECK=1`、`PIP_NO_CACHE_DIR=1`
  - [x] SubTask 4.3: sed 替换 apt 源为 aliyun
  - [x] SubTask 4.4: 安装 ca-certificates、curl、libgomp1、procps、tzdata、wget
  - [x] SubTask 4.5: 清理 `rm -rf /var/lib/apt/lists/*`
  - **Acceptance Criteria**: [AC-BASE-SYSTEM] 阶段可独立构建，apt update 无错误
  - **Test**: `docker build --target base-system -f docker/origin/Dockerfile .` 成功

- [x] Task 5: 编写 `Dockerfile` 的 `base-builder` 阶段
  - [x] SubTask 5.1: `FROM base-system AS base-builder`
  - [x] SubTask 5.2: 定义 `ARG BUILDER_USER=builder`、`BUILDER_UID=1000`、`BUILDER_GID=1000`、`WORKSPACE_DIR=/workspace`
  - [x] SubTask 5.3: apt 安装系统构建依赖（build-essential、cmake、git、libatlas-base-dev、libboost-all-dev、libgflags-dev、libgoogle-glog-dev、libhdf5-dev、libleveldb-dev、liblmdb-dev、libopencv-dev、libprotobuf-dev、libsnappy-dev、pkg-config、protobuf-compiler、python3-dev、python3-pip、python3-setuptools、python3-wheel、sudo、vim、bash-completion、gdb、less）
  - [x] SubTask 5.4: update-alternatives 设置 python/pip 指向 python3/pip3
  - [x] SubTask 5.5: pip 升级到 pip==24.0 setuptools==68.0.0 wheel
  - [x] SubTask 5.6: pip 安装 Python 依赖（numpy>=1.21,<2.0、scipy、matplotlib、scikit-image、h5py、networkx、pandas、pyyaml、Pillow、six、Cython、ipython、nose、python-dateutil、protobuf==3.20.3、python-gflags、leveldb）
  - [x] SubTask 5.7: 验证 Python 包导入（打印版本号）
  - [x] SubTask 5.8: 设置 ENV `CC=gcc`、`CXX=g++`、`CAFFE_ROOT=/workspace/caffex`、`LD_LIBRARY_PATH`、`PYTHONPATH=/workspace/caffex/python`
  - [x] SubTask 5.9: 创建 builder 用户（条件性 groupadd/useradd，处理 UID/GID 冲突），加入 sudo 组，NOPASSWD
  - [x] SubTask 5.10: 创建 `/workspace` 并 chown，`USER builder`，`WORKDIR /workspace`
  - **Acceptance Criteria**: [AC-BASE-BUILDER] 阶段构建成功，`docker run --rm <image> python3 -c "import numpy, scipy, google.protobuf"` 无错误
  - **Test**: `docker build --target base-builder -f docker/origin/Dockerfile .` 成功

- [x] Task 6: 编写 `Dockerfile` 的 `builder` 阶段
  - [x] SubTask 6.1: `FROM base-builder AS builder`
  - [x] SubTask 6.2: `ARG CAFFE_VERSION=1.0`，添加 LABEL
  - [x] SubTask 6.3: `USER root`，`COPY --chown=builder:builder caffex /workspace/caffex`
  - [x] SubTask 6.4: `COPY docker/origin/scripts/generate-makefile-config.sh /usr/local/bin/`，`COPY docker/origin/scripts/verify-caffe.sh /usr/local/bin/`，chmod +x
  - [x] SubTask 6.5: `USER builder`，`WORKDIR /workspace/caffex`
  - [x] SubTask 6.6: 执行 `generate-makefile-config.sh`
  - [x] SubTask 6.7: 执行 `make all -j$(nproc)`，tail -30 输出
  - [x] SubTask 6.8: 执行 `make pycaffe -j$(nproc)`，tail -20 输出
  - [x] SubTask 6.9: 执行 `make tools -j$(nproc)`，tail -20 输出
  - [x] SubTask 6.10: 验证产物 `ls -lh build/lib/`、`ls -lh python/caffe/_caffe*.so`、`ls -lh build/tools/`
  - [x] SubTask 6.11: 执行 `make distribute`，tail -10 输出
  - **Acceptance Criteria**: [AC-BUILDER] 阶段构建成功，`build/lib/libcaffe.so.1.0.0`、`python/caffe/_caffe.so`、`build/tools/caffe` 均存在
  - **Test**: `docker build --target builder -f docker/origin/Dockerfile .` 成功

- [x] Task 7: 编写 `Dockerfile` 的 `runtime` 阶段
  - [x] SubTask 7.1: `FROM base-builder AS runtime`（复用 base-builder 系统依赖层）
  - [x] SubTask 7.2: `ARG CAFFE_VERSION=1.0`，添加 LABEL
  - [x] SubTask 7.3: `USER root`
  - [x] SubTask 7.4: `COPY --from=builder /workspace/caffex/build /workspace/caffex/build`
  - [x] SubTask 7.5: `COPY --from=builder /workspace/caffex/python /workspace/caffex/python`
  - [x] SubTask 7.6: `COPY --from=builder /workspace/caffex/distribute /workspace/caffex/distribute`
  - [x] SubTask 7.7: `COPY --from=builder /workspace/caffex/Makefile.config /workspace/caffex/Makefile.config`
  - [x] SubTask 7.8: `COPY docker/origin/scripts/verify-caffe.sh /usr/local/bin/`，chmod +x
  - [x] SubTask 7.9: `RUN ln -sf /workspace/caffex/build/lib/libcaffe.so.1.0.0 /workspace/caffex/build/lib/libcaffe.so && ldconfig`
  - [x] SubTask 7.10: `RUN verify-caffe.sh`（验证 import caffe 成功）
  - [x] SubTask 7.11: `USER builder`，`WORKDIR /workspace`
  - [x] SubTask 7.12: `ENTRYPOINT ["/bin/bash", "-c"]`，`CMD ["/bin/bash"]`
  - **Acceptance Criteria**: [AC-RUNTIME] 阶段构建成功，`docker run --rm <image> python3 -c "import caffe; print(caffe.__version__)"` 输出版本号
  - **Test**: `docker build --target runtime -f docker/origin/Dockerfile -t caffe-cpu:latest .` 成功

- [x] Task 8: 编写 `build.sh` 构建脚本
  - [x] SubTask 8.1: shebang `#!/usr/bin/env bash`，`set -euo pipefail`
  - [x] SubTask 8.2: 内联日志函数（log_info、log_error、log_success、log_warn、log_header、log_section、log_kv、log_blank、log_troubleshoot）— **不依赖 docker/local/lib/**
  - [x] SubTask 8.3: 内联容器工具检测函数（detect_container_tool，检测 docker 或 wslc）
  - [x] SubTask 8.4: 参数解析（-t、-f、--target、--no-cache、--build-arg、-h）
  - [x] SubTask 8.5: 默认值：IMAGE_NAME=caffe-cpu、TAG=latest、DOCKERFILE=脚本目录/Dockerfile、TARGET=runtime
  - [x] SubTask 8.6: 前置检查（容器工具存在、Docker 服务运行、Dockerfile 存在、caffex/ 源码目录存在）
  - [x] SubTask 8.7: 执行 `docker build --target ${TARGET} -t ${IMAGE_SPEC} -f ${DOCKERFILE} ${NO_CACHE} ${BUILD_ARGS} ${PROJECT_DIR}`
  - [x] SubTask 8.8: 构建结果输出（镜像大小、耗时、下一步操作提示）
  - [x] SubTask 8.9: 失败时输出常见问题排查指引
  - **Acceptance Criteria**: [AC-BUILD-SH] 脚本可执行，删除 `docker/local/lib/` 后仍能正常工作
  - **Test**: 在 WSL2 中 `cd docker/origin && ./build.sh -h` 显示帮助；`./build.sh` 触发构建

- [x] Task 9: 编写 `run.sh` 运行脚本
  - [x] SubTask 9.1: shebang `#!/usr/bin/env bash`，`set -euo pipefail`
  - [x] SubTask 9.2: 内联日志函数（同 build.sh 风格，自包含）
  - [x] SubTask 9.3: 内联 detect_container_tool 函数
  - [x] SubTask 9.4: 参数解析（-i、-n、--rm、--no-rm、--non-interactive、-h、--、命令）
  - [x] SubTask 9.5: 默认值：IMAGE=caffe-cpu:latest、CONTAINER_NAME=caffe-dev、AUTO_RM=true、INTERACTIVE=true、TTY=true
  - [x] SubTask 9.6: 前置检查（容器工具、Docker 服务、镜像存在）
  - [x] SubTask 9.7: 构造 docker run 参数（--name、--hostname、-w、-v 挂载项目根到 /workspace、-e CAFFE_ROOT、-e PYTHONPATH、-e LD_LIBRARY_PATH、--rm、-i、-t）
  - [x] SubTask 9.8: exec docker run
  - **Acceptance Criteria**: [AC-RUN-SH] 脚本可执行，`./run.sh -- python3 -c "import caffe"` 输出版本号
  - **Test**: 构建镜像后 `./run.sh -- python3 -c "import caffe; print(caffe.__version__)"` 成功

- [x] Task 10: 编写 `README.md` 使用说明文档
  - [x] SubTask 10.1: 标题与简介（caffex/python CPU 版本 Docker 镜像）
  - [x] SubTask 10.2: 「快速开始」章节（一键构建、运行、import caffe 验证）
  - [x] SubTask 10.3: 「构建」章节（build.sh 用法、--target 选项、构建参数、构建耗时说明）
  - [x] SubTask 10.4: 「运行」章节（run.sh 用法、交互式模式、一次性命令、目录挂载）
  - [x] SubTask 10.5: 「环境变量」章节（CAFFE_ROOT、PYTHONPATH、LD_LIBRARY_PATH、PIP_INDEX_URL）
  - [x] SubTask 10.6: 「与 conda 版本的差异」章节（4 阶段 vs 5 阶段、无 pycaffe-builder、无 scikit-build-core、Make 构建系统）
  - [x] SubTask 10.7: 「常见问题」章节（Python 3.10 兼容性、Boost.Python 检测、protobuf 版本冲突、HDF5 路径、镜像体积优化建议）
  - **Acceptance Criteria**: [AC-README] 文档包含 7 个章节，每节有命令示例
  - **Test**: 人工阅读检查文档完整性

- [x] Task 11: WSL2 端到端构建验证
  - [x] SubTask 11.1: 在 WSL2 Ubuntu 24.04 中执行 `cd docker/origin && ./build.sh`（缓存命中耗时 1分2秒）
  - [x] SubTask 11.2: 记录构建耗时（缓存命中 62 秒；首次冷构建预期 15-40 分钟）
  - [x] SubTask 11.3: 验证镜像大小（`docker images caffe-cpu:latest` → 3.36GB）
  - [x] SubTask 11.4: 执行 `docker run --rm caffe-cpu:latest python3 -c "import caffe; print(caffe.__version__)"` → `CAFFE_VERSION: 1.0.0`
  - [x] SubTask 11.5: 执行 `docker run --rm caffe-cpu:latest python3 -c "from caffe.proto import caffe_pb2; print(caffe_pb2.NetParameter)"` → `OK: <class 'caffe.proto.caffe_pb2.NetParameter'>`
  - [x] SubTask 11.6: 执行 `docker run --rm caffe-cpu:latest caffe --version` → `caffe version 1.0.0`
  - [x] SubTask 11.7: 执行 `docker run --rm caffe-cpu:latest ls /workspace/caffex/build/tools/` → 列出 caffe、compute_image_mean、convert_imageset、extract_features、upgrade_net_proto_text 等
  - [x] SubTask 11.8: 已解决的问题（BLAS:=open→atlas、PATH 加入 build/tools、移除 ENTRYPOINT）
  - **Acceptance Criteria**: [AC-E2E] 全部验证通过，`import caffe` 成功，`caffe --version` 输出版本号
  - **Test**: 所有子任务通过

- [x] Task 12: 编写测试验证报告
  - [x] SubTask 12.1: 在 `docker/origin/` 下创建 `BUILD_REPORT.md`（构建验证报告）
  - [x] SubTask 12.2: 记录构建环境（WSL2 Ubuntu 24.04.3 LTS、Docker 29.6.1、16 核、15Gi 内存）
  - [x] SubTask 12.3: 记录构建耗时与各阶段耗时（缓存命中 1分2秒；各层大小分布已记录）
  - [x] SubTask 12.4: 记录镜像大小（3.36GB，对比 conda 版本小 2.1-2.2GB）
  - [x] SubTask 12.5: 记录所有验证命令的输出（7 项验证 + 环境变量检查）
  - [x] SubTask 12.6: 记录遇到的问题与解决方案（BLAS 链接、PATH 缺失、ENTRYPOINT 冲突、挂载覆盖）
  - [x] SubTask 12.7: 记录与 `docker/local/conda` 版本的对比（镜像大小、构建阶段数、功能差异）
  - **Acceptance Criteria**: [AC-REPORT] 报告包含环境、耗时、大小、验证输出、问题、对比 6 部分
  - **Test**: 人工阅读检查报告完整性

# Task Dependencies

- Task 2, Task 3 可并行（独立脚本）
- Task 4 → Task 5 → Task 6 → Task 7（Dockerfile 阶段顺序依赖）
- Task 6 依赖 Task 2（builder 阶段调用 generate-makefile-config.sh）
- Task 7 依赖 Task 3, Task 6（runtime 阶段调用 verify-caffe.sh，复制 builder 产物）
- Task 8, Task 9 可并行（独立脚本）
- Task 10 依赖 Task 8, Task 9（文档需引用脚本用法）
- Task 11 依赖 Task 7, Task 8, Task 9（端到端验证需完整 Dockerfile + 脚本）
- Task 12 依赖 Task 11（报告基于端到端验证结果）

# Parallelizable Work

- **Wave 1（并行）**: Task 1（目录）+ Task 2（generate-makefile-config.sh）+ Task 3（verify-caffe.sh）
- **Wave 2（并行）**: Task 4（base-system）+ Task 8（build.sh）+ Task 9（run.sh）
- **Wave 3（串行）**: Task 5 → Task 6 → Task 7（Dockerfile 后三个阶段）
- **Wave 4（串行）**: Task 10（README）→ Task 11（E2E 验证）→ Task 12（报告）
