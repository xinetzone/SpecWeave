# 构建 TVM/VTA 纯净运行时 Docker 镜像 - Product Requirement Document

## Overview
- **Summary**: 构建一个纯净的、可分发的 Docker 运行时镜像，该镜像基于官方 Conda 基础镜像，包含预配置的 Conda Python 环境以及预安装的 TVM 和 VTA Nuitka 编译 wheel 包。镜像需优化大小、配置正确的环境变量，并导出为 tar 文件便于分发，同时提供使用说明文档。
- **Purpose**: 为 TVM/VTA 提供一个独立、干净、可直接使用的运行环境，用户无需从源码编译即可直接使用 Nuitka 编译后的 TVM 和 VTA 模块，避免依赖冲突和环境配置问题。
- **Target Users**: TVM/VTA 开发者、需要部署 TVM 运行时的运维人员、使用 VTA 进行深度学习推理的用户。

## Goals
- 基于官方 `continuumio/miniconda3` 基础镜像构建纯净运行环境
- 创建独立 Conda 环境，支持通过 `${python_version}` 参数指定 Python 版本（默认 3.14）
- 预安装 TVM 和 VTA 的 wheel 包及其所有必需依赖（numpy, ml_dtypes, typing_extensions）
- 优化镜像体积：清理 apt 缓存、conda 缓存、pip 缓存、临时文件
- 配置正确的环境变量（LD_LIBRARY_PATH, PATH, CONDA_DEFAULT_ENV 等）确保 TVM/VTA 能正常加载动态库
- 将构建完成的镜像保存为 tar 文件，便于离线分发和部署
- 提供清晰的镜像使用文档，包含启动方式、验证步骤、基本用法示例

## Non-Goals (Out of Scope)
- 不包含 TVM/VTA 的编译工具链（LLVM, GCC, CMake, Ninja 等）
- 不包含源码开发环境（不挂载 npu_tvm 源码目录）
- 不包含 CUDA/GPU 支持（初始版本仅 CPU 运行时）
- 不包含 Jupyter Notebook 或 RPC 服务（仅基础 Python 运行时）
- 不构建多架构镜像（仅 x86_64 Linux）

## Background & Context
- 此前已完成 TVM 和 VTA 的 Nuitka 编译，生成了两个独立的 wheel 包：
  - `tvm-0.19.0-cp314-cp314-linux_x86_64.whl` (~60 MB)：包含 Nuitka 编译的 tvm.so 和 C++ 动态库 libtvm.so, libtvm_runtime.so
  - `vta-0.1.0-cp314-cp314-linux_x86_64.whl` (~3.7 MB)：包含 Nuitka 编译的 vta.so 和 VTA 模拟器库，依赖 tvm>=0.19.0
- 已有一个基础的 `Dockerfile.runtime` 位于 [Dockerfile.runtime](file:///d:/spaces/SpecWeave/external/xmhub/npu_tvm/docker/local/conda/Dockerfile.runtime)，但该文件仅配置了基础 Conda 环境，未安装 wheel 包，也未提供镜像导出和使用文档。
- wheel 包位于 `docker/local/nuitka/tvm/dist/` 和 `docker/local/nuitka/vta/dist/` 目录。
- 已通过 [test_wheel.py](file:///d:/spaces/SpecWeave/external/xmhub/npu_tvm/docker/local/nuitka/test_wheel.py) 验证 wheel 包可正常导入和运行。

## Functional Requirements
- **FR-1**: Dockerfile 支持通过 `PYTHON_VERSION` build-arg 指定 Python 版本，默认 3.14
- **FR-2**: 镜像中创建独立的 Conda 环境（默认名 `tvm-runtime`），不使用 base 环境
- **FR-3**: 在构建时将本地的 TVM 和 VTA wheel 包复制到镜像中并安装
- **FR-4**: wheel 包的所有必需依赖（numpy, ml_dtypes, typing_extensions）需正确安装
- **FR-5**: 配置 `LD_LIBRARY_PATH` 确保 TVM 的 C++ 动态库（libtvm.so, libtvm_runtime.so）能被正确加载
- **FR-6**: 配置 Conda 环境自动激活，用户进入容器后直接在 tvm-runtime 环境中
- **FR-7**: 镜像构建时执行基本验证：Python 版本正确、tvm 可导入并打印版本、vta 可导入
- **FR-8**: 提供构建脚本 `build_runtime_image.sh`，支持一键构建镜像
- **FR-9**: 提供导出脚本 `export_runtime_image.sh`，将镜像保存为 tar 文件
- **FR-10**: 提供使用说明文档 `RUNTIME_IMAGE_USAGE.md`，包含镜像加载、启动、验证、示例用法
- **FR-11**: 镜像中包含测试脚本 `test_wheel.py`，用户可在容器内运行验证安装

## Non-Functional Requirements
- **NFR-1**: 镜像体积应尽可能小，目标控制在 1 GB 以内（基础镜像 ~400 MB + Conda 环境 ~300 MB + TVM/VTA ~200 MB）
- **NFR-2**: 镜像构建过程中应清理所有缓存（apt, conda, pip, /tmp），不留下不必要的文件
- **NFR-3**: 镜像应可在无网络环境中使用（所有依赖在构建时预装）
- **NFR-4**: 镜像启动时间应 < 5 秒（无需初始化编译工具）
- **NFR-5**: 镜像标签应包含版本信息，格式为 `tvm-runtime:<tvm_version>-py<python_version>`

## Constraints
- **Technical**: 
  - 基础镜像必须使用官方 `continuumio/miniconda3:latest`
  - Conda 包优先使用 conda-forge 频道
  - pip 使用国内镜像源加速（阿里云镜像）
  - 仅支持 Linux x86_64 平台
- **Business**: 
  - 镜像需可离线分发（tar 格式）
  - 不引入额外的商业依赖
- **Dependencies**: 
  - 依赖已有的 TVM/VTA wheel 包（位于 docker/local/nuitka/*/dist/）
  - 依赖 Docker 和 Docker Compose 环境
  - wheel 包是为 Python 3.14 编译的，默认 Python 版本需与 wheel 包匹配

## Assumptions
- 用户已安装 Docker 环境
- wheel 包已通过 `manual_package.sh` 或其他方式成功构建并位于 dist 目录
- 默认 Python 版本为 3.14，与当前编译的 wheel 包匹配
- 用户可能需要为其他 Python 版本重新编译 wheel 包，Dockerfile 需支持版本参数化
- 国内网络环境下需要配置镜像源加速下载

## Acceptance Criteria

### AC-1: Dockerfile 可成功构建镜像
- **Given**: 本地存在 TVM 和 VTA 的 wheel 包，Docker 环境正常
- **When**: 执行 `docker build` 命令构建镜像
- **Then**: 镜像构建成功，无错误退出，构建过程中有清晰的日志输出
- **Verification**: `programmatic`

### AC-2: 镜像内 Conda 环境配置正确
- **Given**: 镜像已成功构建
- **When**: 启动容器并执行 `python --version` 和 `conda env list`
- **Then**: Python 版本为指定的 ${python_version}，默认激活 tvm-runtime 环境
- **Verification**: `programmatic`

### AC-3: TVM 和 VTA 可正常导入
- **Given**: 容器已启动
- **When**: 在容器内执行 `python -c "import tvm; print(tvm.__version__); import vta; print(vta.__file__)"`
- **Then**: TVM 版本号正确打印，VTA 模块路径正确显示，无导入错误
- **Verification**: `programmatic`

### AC-4: 动态库路径配置正确
- **Given**: 容器已启动
- **When**: 在容器内执行 TVM 基本功能测试（创建张量、TE 计算）
- **Then**: 张量创建成功，计算正常执行，无动态库加载错误
- **Verification**: `programmatic`

### AC-5: 镜像体积优化
- **Given**: 镜像已构建完成
- **When**: 执行 `docker images` 查看镜像大小
- **Then**: 镜像体积 < 1 GB，无明显冗余文件
- **Verification**: `programmatic`

### AC-6: 镜像可导出为 tar 文件
- **Given**: 镜像已构建完成
- **When**: 执行导出脚本生成 tar 文件
- **Then**: tar 文件生成成功，可通过 `docker load` 在另一台机器上导入
- **Verification**: `programmatic`

### AC-7: 测试脚本可在容器内运行
- **Given**: 容器已启动
- **When**: 在容器内执行 `python /opt/test_wheel.py`
- **Then**: 所有测试项通过，输出 "All tests passed"
- **Verification**: `programmatic`

### AC-8: 使用文档完整清晰
- **Given**: 所有文件已创建
- **When**: 阅读使用文档
- **Then**: 文档包含镜像构建、加载、启动、验证、示例用法等完整步骤，说明清晰
- **Verification**: `human-judgment`

## Open Questions
- [ ] 是否需要同时提供 GPU (CUDA) 版本的运行时镜像？（当前 PRD 仅覆盖 CPU）
- [ ] 是否需要将镜像推送到 Docker Hub 或私有镜像仓库？（当前仅导出 tar）
- [ ] wheel 包的版本号是否需要动态从 pyproject.toml 中读取？（当前硬编码为 0.19.0）
