# Caffe-FFI 萃取迁移与Docker化 - Product Requirement Document

## Overview
- **Summary**: 将vendor/caffe/caffe-ffi萃取为独立C++原生扩展库（libs/caffe-ffi），并创建基于jupyter-ssh-base的Docker开发环境（apps/caffe-ffi-jupyter），支持Python 3.14+和WSL编译。
- **Purpose**: 消除vendor路径依赖，使caffe-ffi成为可独立编译、测试、安装和分发的第一方库；提供开箱即用的Docker开发环境降低使用门槛。
- **Target Users**: 深度学习框架开发者、需要使用Caffe模型推理的研究人员、caffe-ffi贡献者。

## Goals
- 将caffe-ffi从vendor/caffe/caffe-ffi完整复制到libs/caffe-ffi，作为独立第一方项目
- 修复CMake硬编码路径问题，使项目可独立编译（不依赖vendor父目录结构）
- 对齐libs/目录现有项目（npu-ffi）的标准结构和开发脚本
- 创建apps/caffe-ffi-jupyter Docker开发环境，基于jupyter-ssh-base
- Docker镜像保留SSH+Jupyter双服务，使用Miniconda提供Python 3.14环境
- 提供完整的构建、运行、测试脚本和文档

## Non-Goals (Out of Scope)
- 不删除或修改vendor/caffe/caffe-ffi原始文件（vendor submodule保持原位）
- 不重构caffe-ffi的核心C++实现逻辑（仅做迁移必要的构建系统调整）
- 不实现GPU/CUDA支持（当前CPU_ONLY模式保持）
- 不发布到PyPI或Conda Forge（仅本地可安装）
- 不修改jupyter-ssh-base基础镜像本身
- 不在当前Windows环境执行实际C++编译（编译测试在WSL中进行）

## Background & Context
- caffe-ffi是基于tvm-ffi原生对象系统的Caffe深度学习框架FFI绑定
- 当前位于vendor/caffe/caffe-ffi（第三方依赖子模块），CMake中硬编码了`../../tvm-ffi`路径
- xuanspace monorepo中libs/目录存放可复用C++/Python库，参考项目npu-ffi已有标准结构
- apps/jupyter-ssh-base提供了标准化的SSH+Jupyter基础镜像（ubuntu:26.04 + supervisord + /opt/venv）
- Python 3.14+是xuanspace项目的硬性要求
- WSL是Windows下进行C++编译和Docker构建的标准环境

## Functional Requirements

### FR-1: 项目文件复制与结构调整
- 完整复制vendor/caffe/caffe-ffi的所有源代码、头文件、Python包、proto文件、测试、示例、文档到libs/caffe-ffi/
- 保留include/caffe_ffi/、src/caffe_ffi/、python/caffe_ffi/、proto/caffe/proto/、tests/cpp/、tests/python/、examples/、docs/的现有目录结构
- 保留cmake/模块化CMake文件（已拆分为Options/Dependencies/CompilerConfig等10个模块）

### FR-2: CMake构建系统独立化
- 修改cmake/Dependencies.cmake：`find_package(tvm_ffi CONFIG REQUIRED)`为默认查找方式
- 添加`CAFFE_FFI_TVM_FFI_DIR`缓存选项，允许显式指定tvm-ffi源码目录（开发模式）
- 保留自动检测逻辑：当CAFFE_FFI_TVM_FFI_DIR未指定且`../../tvm-ffi`存在时自动使用本地源码（开发友好）
- 移除对vendor父目录结构的任何隐式依赖
- 顶层CMakeLists.txt保持精简模块化include结构

### FR-3: 标准开发脚本与配置
- 参考npu-ffi添加CMakePresets.json（release/debug/developer预设）
- 添加scripts/dev.sh（Linux/WSL开发环境设置和构建脚本）
- 添加scripts/dev.ps1（Windows开发环境设置脚本）
- 添加scripts/check_ffi_prefix.py（FFI命名前缀检查）
- 添加scripts/verify_install.py（安装验证脚本）
- 添加scripts/gen_proto.py（protobuf代码生成脚本）
- 添加conda.recipe/目录：meta.yaml、build.sh、bld.bat（参考npu-ffi）
- 更新environment.yml：移除硬编码`-e ../../tvm-ffi`，添加开发模式注释说明
- 添加.gitignore、LICENSE、CHANGELOG.md（如不存在）

### FR-4: pyproject.toml适配
- 保持scikit-build-core构建系统
- requires-python = ">=3.14"（已满足）
- 依赖保持：numpy>=2.3, protobuf>=7.0.0, apache-tvm-ffi
- 完善sdist配置确保源码分发包包含所有必要文件
- 添加项目URL和分类器信息

### FR-5: Docker开发环境创建（apps/caffe-ffi-jupyter）
- 在apps/下创建caffe-ffi-jupyter子项目
- 创建AGENTS.md（遵循apps规范）
- 创建Dockerfile，基于jupyter-ssh-base镜像构建
- Dockerfile安装Miniconda，创建Python 3.14 conda环境
- 在conda环境中安装caffe-ffi的所有依赖和编译工具链
- 预装caffe-ffi（从libs/caffe-ffi源码编译安装到conda环境）
- 注册conda环境为Jupyter内核（"Python 3.14 (caffe-ffi)"）
- 保留jupyter-ssh-base的所有基础功能：SSH(22)、Jupyter(8888)、supervisord、jupyteruser、中文环境
- 支持volume挂载开发模式：-v $(pwd)/libs/caffe-ffi:/workspace/caffe-ffi

### FR-6: Docker构建脚本与编排
- 创建docker-compose.yml示例文件
- 创建scripts/build.sh构建脚本（支持国内镜像源参数）
- 创建README.md使用文档（构建、运行、SSH连接、Jupyter访问、测试验证）
- 创建.dockerignore排除不必要文件

### FR-7: 文档
- libs/caffe-ffi/README.md：安装说明、快速开始、开发指南
- apps/caffe-ffi-jupyter/README.md：镜像构建、运行、使用说明
- 文档包含WSL环境下的完整构建和测试步骤

## Non-Functional Requirements

### NFR-1: 构建性能
- CMake配置时间<30秒（WSL环境）
- C++编译时间<5分钟（WSL环境，Release模式，并行编译）
- Docker镜像构建时间<15分钟（含C++编译）

### NFR-2: 兼容性
- Python 3.14+兼容（无低版本语法/API）
- Linux（WSL Ubuntu）原生编译支持
- Docker镜像基于ubuntu:26.04，兼容Docker Engine 24+
- 保留对CPU_ONLY模式的支持（CUDA可选不实现）

### NFR-3: 可维护性
- CMake模块单一职责（已实现，保留）
- 目录结构与npu-ffi保持一致，降低跨项目认知成本
- 脚本有注释说明关键步骤

### NFR-4: 镜像体验
- 容器启动后SSH和Jupyter均可用，健康检查通过
- Jupyter中可import caffe_ffi并运行基础测试
- SSH登录后默认激活caffe-ffi conda环境

## Constraints
- **Technical**: 
  - 构建系统必须使用cmake + scikit-build-core（setuptools/setup.py禁止）
  - Python版本必须>=3.14
  - 必须使用find_package(tvm_ffi CONFIG REQUIRED)依赖预安装的apache-tvm-ffi包（vendored add_subdirectory方式禁止用于发布，仅开发模式允许）
  - Windows下需os.add_dll_directory()，但编译在WSL Linux环境进行
  - protobuf版本必须>=7
- **Business**: 
  - 所有文件在Windows环境创建（编辑），编译测试在WSL执行
  - 遵循xuanspace目录约定：libs/放库，apps/放应用
- **Dependencies**: 
  - 基础镜像：jupyter-ssh-base（本地构建或预构建）
  - C++依赖：libopenblas, libprotobuf-dev, protobuf-compiler
  - Python依赖：numpy>=2.3, protobuf>=7, apache-tvm-ffi, scikit-build-core, pytest
  - Conda：Miniconda3提供Python 3.14环境

## Assumptions
- WSL环境已安装Docker且服务可用（用户准备）
- WSL环境中可构建jupyter-ssh-base基础镜像（先构建base再构建caffe-ffi-jupyter）
- tvm-ffi（apache-tvm-ffi）可通过pip或conda安装Python 3.14兼容版本
- libs/tvm-ffi在本地开发环境中存在（用于开发模式editable安装）；若不存在则使用pip安装的apache-tvm-ffi
- ubuntu:26.04容器中通过Miniconda安装Python 3.14是可行的
- vendor/caffe/caffe-ffi当前代码在Linux下可编译（已做过CMake模块化，有conda_build.sh脚本）

## Acceptance Criteria

### AC-1: libs/caffe-ffi目录结构完整
- **Given**: 迁移任务执行完成
- **When**: 检查libs/caffe-ffi/目录
- **Then**: 包含以下文件和目录：CMakeLists.txt, pyproject.toml, environment.yml, include/caffe_ffi/, src/caffe_ffi/, python/caffe_ffi/, proto/caffe/proto/, cmake/, tests/cpp/, tests/python/, examples/, docs/, scripts/, conda.recipe/, CMakePresets.json, LICENSE, README.md, CHANGELOG.md, .gitignore
- **Verification**: `programmatic`

### AC-2: CMake独立配置成功
- **Given**: WSL环境，conda环境已激活（Python 3.14, cmake, ninja, apache-tvm-ffi已安装）
- **When**: 在libs/caffe-ffi/build目录执行`cmake .. -DCMAKE_BUILD_TYPE=Release`
- **Then**: CMake配置成功，无硬编码路径错误，正确找到tvm_ffi、Protobuf、BLAS、Threads
- **Verification**: `programmatic`（WSL中执行）

### AC-3: Python包可pip安装
- **Given**: WSL环境，conda环境已激活
- **When**: 在libs/caffe-ffi/执行`pip install --no-build-isolation -e .`
- **Then**: 编译成功，caffe_ffi包可导入，`import caffe_ffi`无错误
- **Verification**: `programmatic`（WSL中执行）

### AC-4: C++和Python测试通过
- **Given**: caffe-ffi已pip安装到WSL conda环境
- **When**: 执行pytest tests/python/
- **Then**: 101个Python测试全部通过（19个skipped是纯Python模式正常跳过）
- **Verification**: `programmatic`（WSL中执行）

### AC-5: Docker镜像构建成功
- **Given**: WSL环境，Docker服务运行，jupyter-ssh-base镜像已构建
- **When**: 在xuanspace根目录执行`docker build -f apps/caffe-ffi-jupyter/Dockerfile -t caffe-ffi-jupyter .`
- **Then**: 镜像构建成功，无编译错误
- **Verification**: `programmatic`（WSL中执行）

### AC-6: Docker容器SSH访问正常
- **Given**: caffe-ffi-jupyter镜像已构建
- **When**: 启动容器`docker run -d -p 2222:22 -p 8888:8888 -e USER_PASSWORD=testpass -e JUPYTER_TOKEN=testtoken caffe-ffi-jupyter`
- **Then**: SSH连接`ssh -p 2222 jupyteruser@localhost`使用密码testpass可登录
- **Verification**: `programmatic`（WSL中执行）

### AC-7: Docker容器Jupyter可访问
- **Given**: 容器运行中
- **When**: 浏览器访问http://localhost:8888/?token=testtoken 或curl检查
- **Then**: Jupyter Notebook/Lab界面可访问，存在"Python 3.14 (caffe-ffi)"内核
- **Verification**: `programmatic`（WSL中执行）

### AC-8: Docker容器中caffe-ffi可导入
- **Given**: 容器运行中，通过SSH登录或docker exec
- **When**: 在Python 3.14内核或`/opt/conda/envs/caffe-ffi/bin/python`中执行`import caffe_ffi; print(caffe_ffi.__version__)`
- **Then**: 导入成功，输出版本号0.1.0
- **Verification**: `programmatic`（WSL中执行）

### AC-9: Docker容器中测试通过
- **Given**: 容器运行中
- **When**: 在容器内conda环境中执行pytest（caffe-ffi预装位置）
- **Then**: 核心功能测试通过（Blob/Net/Layer基础测试）
- **Verification**: `programmatic`（WSL中执行）

### AC-10: 目录结构与npu-ffi风格一致
- **Given**: libs/caffe-ffi创建完成
- **When**: 对比libs/npu-ffi和libs/caffe-ffi的顶层目录结构
- **Then**: 两者具有相同的顶层组织方式（include/src/python/proto/cmake/tests/examples/scripts/docs/conda.recipe）
- **Verification**: `human-judgment`

### AC-11: 文档完整性
- **Given**: 所有文件创建完成
- **When**: 阅读libs/caffe-ffi/README.md和apps/caffe-ffi-jupyter/README.md
- **Then**: 包含安装步骤、构建命令、Docker使用说明、WSL环境准备、测试验证步骤
- **Verification**: `human-judgment`

## Open Questions
- [ ] ubuntu:26.04默认Python版本是3.13还是3.14？如果是3.14是否可以不用Miniconda直接用系统Python？（待WSL验证后决定，当前方案使用Miniconda确保Python 3.14）
- [ ] libs/tvm-ffi是否已存在于xuanspace中？如果存在，开发模式的相对路径应为`../tvm-ffi`（从libs/caffe-ffi视角）
- [ ] caffe-ffi-jupyter的Dockerfile中，是否需要在builder阶段单独编译C++库然后COPY到runtime（类似jupyter-ssh-base的多阶段构建）？还是直接在最终镜像中编译（开发镜像大小可接受）？当前方案采用直接在最终镜像中编译（开发镜像无需极致精简）
- [ ] 是否需要docker-compose.yml中包含volume挂载示例用于开发模式？（当前方案：包含）
