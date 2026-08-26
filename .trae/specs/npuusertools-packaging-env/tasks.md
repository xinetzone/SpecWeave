# npuusertools 打包环境 (vta-dev) - 实现计划

## [x] Task 1: 创建vta-dev目录结构和AGENTS.md
- **Priority**: high
- **Depends On**: None
- **Description**: 
  - 创建 `external/dao/runtime/vta-dev/` 目录及子目录结构：`scripts/`、`configs/`、`tasks/`、`dist/`（gitignore）、`logs/`（gitignore）、`workspace/`（gitignore）
  - 创建 `external/dao/runtime/vta-dev/AGENTS.md`，遵循SpecWeave workspace discovery协议
  - AGENTS.md内容：启动协议、核心红线（不修改npuusertools子模块、禁止Docker Desktop GUI操作）、按需阅读路由表（指向tasks/包而非tasks.py）、与chaos/ai关系说明、三步快速开始（invoke docker.toolchain → invoke all / bash build.sh --extract）
  - 创建 `.gitignore` 排除 dist/、logs/、workspace/、__pycache__/、*.pyc、*.pyo、.env
  - 创建 `configs/.gitkeep` 使空目录被git跟踪
- **Acceptance Criteria Addressed**: AC-7, AC-8
- **Test Requirements**:
  - `programmatic` TR-1.1: `external/dao/runtime/vta-dev/AGENTS.md` 存在且包含"启动协议"关键词
  - `programmatic` TR-1.2: `external/dao/runtime/vta-dev/scripts/`、`configs/`、`tasks/` 目录存在
  - `programmatic` TR-1.3: `.gitignore` 存在且包含 dist/、logs/、workspace/
  - `human-judgement` TR-1.4: AGENTS.md路由表指向tasks/ namespace包（非tasks.py），新人能找到构建命令
- **Notes**: AGENTS.md参考npuusertools/AGENTS.md和xmnn-whl-builder/AGENTS.md的结构；嵌套路由关系图反映tasks/包结构

## [x] Task 2: 创建Nuitka构建系统（pyproject.toml + CMakeLists.txt + build-wheel.sh）
- **Priority**: high
- **Depends On**: Task 1
- **Description**: 
  - 创建 `external/dao/runtime/vta-dev/pyproject.toml`（独立于npuusertools的构建配置）：
    - scikit-build-core>=0.5 作为build-backend
    - 包名xmnn，固定版本1.2.1-dev（SETUPTOOLS_SCM_PRETEND_VERSION兜底）
    - 依赖列表：numpy, scipy, pandas, matplotlib, Pillow, onnx, protobuf, openpyxl, tabulate, rich, tqdm, tomlkit, decorator, attrs, psutil, cloudpickle, typing_extensions, pytest, telnetlib3
    - wheel.install-dir="."（wheel根目录），cmake.build-type=Release
  - 创建 `external/dao/runtime/vta-dev/CMakeLists.txt`（LANGUAGES NONE，不编译C++）：
    - cmake_minimum_required(VERSION 3.18...3.27)
    - CACHE变量：NUITKA_OUTPUT_DIR, XMN_PYTHON_DIR, XMN_NUITKA_OUT
    - 安装Nuitka编译产物 xmnn.cpython-*.so 到wheel根目录"."
    - 安装数据目录：xmnn/tools_cpp/、xmnn/fonts/ 通过install(DIRECTORY)
    - 安装xmnn/autolibs/（通过cp -a + .xmnn_autolibs_keep占位符解决空目录问题）
    - patchelf递归设置tools_cpp/libs/**/*.so的RPATH=$ORIGIN
    - chmod +x tools_cpp/bin/*
  - 创建 `external/dao/runtime/vta-dev/scripts/build-wheel.sh`（容器内构建脚本）：
    - 设置PATH=/opt/conda/bin，CC=clang，CXX=clang++，LLVM_CONFIG=/opt/conda/bin/llvm-config
    - ccache环境配置（CCACHE_DIR, CCACHE_COMPRESS, CCACHE_SLOPPINESS等）
    - AST PREAMBLE注入/恢复函数（Python 3.14兼容shim，恢复被移除的ast节点：NameConstant/Num/Str/Bytes/Index/ExtSlice）
    - 单Nuitka编译xmnn包：`python -m nuitka --module --include-package=xmnn --enable-plugin=dill-compat --nofollow-import-to=torch,torchvision,onnx2pytorch --jobs=8 --clang --lto=no`
    - 编译后恢复__init__.py（Nuitka编译过程中AST PREAMBLE会临时修改__init__.py）
    - `python -m build --wheel --no-isolation` 使用cmake.define传递NUITKA_OUTPUT_DIR/XMN_PYTHON_DIR/XMN_NUITKA_OUT路径
    - wheel输出到/opt/vta-dist/
- **Acceptance Criteria Addressed**: AC-1, AC-2, AC-9
- **Test Requirements**:
  - `programmatic` TR-2.1: pyproject.toml存在且包含scikit-build-core build-backend
  - `programmatic` TR-2.2: CMakeLists.txt存在且使用LANGUAGES NONE，包含patchelf RPATH=$ORIGIN设置
  - `programmatic` TR-2.3: build-wheel.sh存在且包含AST PREAMBLE注入/恢复逻辑、Nuitka编译命令、python -m build命令
  - `programmatic` TR-2.4: build-wheel.sh设置CC/CXX/LLVM_CONFIG指向/opt/conda/bin/
  - `human-judgement` TR-2.5: 构建模式与xmnn-whl-builder一致（独立pyproject.toml+CMakeLists.txt打包Nuitka产物）但仅编译xmnn（无tvm/vta）
- **Notes**: 
  - vta-dev自带pyproject.toml和CMakeLists.txt是关键设计——不修改npuusertools内的构建文件（NG1约束），参考xmnn-whl-builder模式在/builder/目录下独立打包Nuitka产物
  - AST PREAMBLE是Python 3.14+兼容必需（多个ast节点在3.14中被移除）
  - ccache用于Nuitka的C编译阶段加速增量构建

## [x] Task 3: 创建Dockerfile两阶段构建（含Nuitka builder）
- **Priority**: high
- **Depends On**: Task 2
- **Description**: 
  - 创建 `external/dao/runtime/vta-dev/Dockerfile`，第一行 `# syntax=docker/dockerfile:1.7-labs`
  - **Builder阶段** (as builder):
    - ARG BASE_IMAGE=devcontainer-base:onnx-quantized-latest
    - FROM ${BASE_IMAGE} AS builder
    - 安装系统依赖：ccache, patchelf（apt-get，conda fallback）
    - 安装Python构建依赖：nuitka, scikit-build-core>=0.5, setuptools-scm>=8.0, build>=1.0, invoke>=2.0, auditwheel>=5.0, decorator, attrs, cloudpickle, typing_extensions
    - 设置环境变量：PATH=/opt/conda/bin:$PATH, CC=/opt/conda/bin/clang, CXX=/opt/conda/bin/clang++, LLVM_CONFIG=/opt/conda/bin/llvm-config, PIP_USER=0, SETUPTOOLS_SCM_PRETEND_VERSION=1.2.1, CCACHE_DIR=/builder/.ccache
    - 创建工作目录 /builder
    - COPY vta-dev自有文件（相对SpecWeave根目录context）：
      - `COPY external/dao/runtime/vta-dev/pyproject.toml external/dao/runtime/vta-dev/CMakeLists.txt ./`
      - `COPY external/dao/runtime/vta-dev/scripts/ ./scripts/`
    - 使用 `--mount=type=cache,target=/root/.cache/pip` 缓存pip下载
    - 使用 `--mount=type=cache,target=/builder/.ccache` 缓存ccache
    - 使用 `--mount=type=bind,target=/source/npuusertools,source=external/chaos/npuusertools,rw` 挂载源码（rw用于AST PREAMBLE注入）
    - 构建wheel：`RUN bash scripts/build-wheel.sh`
    - 输出wheel到/opt/vta-dist/
  - **Final阶段**:
    - FROM ${BASE_IMAGE}
    - 复制verify脚本：`COPY external/dao/runtime/vta-dev/scripts/verify-wheel.sh /usr/local/bin/verify-wheel.sh`
    - 复制wheel: COPY --from=builder /opt/vta-dist/*.whl /tmp/
    - 安装wheel: pip install /tmp/*.whl
    - 运行验证: RUN verify-wheel.sh
    - 保留wheel副本：COPY --from=builder /opt/vta-dist/*.whl /opt/vta-dist/
    - 设置工作目录 /workspace
    - CMD ["/bin/bash"]
- **Acceptance Criteria Addressed**: AC-1, AC-2, AC-9
- **Test Requirements**:
  - `programmatic` TR-3.1: Dockerfile存在且第一行是 `# syntax=docker/dockerfile:1.7-labs`
  - `programmatic` TR-3.2: Dockerfile包含两个FROM指令（builder阶段和final阶段）
  - `programmatic` TR-3.3: Dockerfile包含 `--mount=type=bind` 挂载npuusertools（source=external/chaos/npuusertools）
  - `programmatic` TR-3.4: Dockerfile包含 `--mount=type=cache` 用于pip和ccache缓存
  - `programmatic` TR-3.5: builder阶段安装nuitka包，设置CC/CXX/LLVM_CONFIG
  - `programmatic` TR-3.6: COPY路径以external/dao/runtime/vta-dev/开头（build context为SpecWeave根目录）
  - `programmatic` TR-3.7: final阶段RUN verify-wheel.sh，COPY wheel到/opt/vta-dist/保留副本
  - `human-judgement` TR-3.8: Dockerfile结构与xmnn-whl-builder/Dockerfile模式一致（两阶段+bind mount+cache mount+verify脚本）
- **Notes**: 
  - 构建context必须是SpecWeave根目录（不是vta-dev/），否则COPY和bind mount路径无法解析
  - bind mount使用rw模式因为AST PREAMBLE需要临时写入__init__.py（编译后恢复）
  - 使用 `docker build`（非buildx），通过DOCKER_BUILDKIT=1环境变量启用BuildKit

## [x] Task 4: 创建verify-wheel.sh验证脚本（12项检查，含Nuitka .so验证）
- **Priority**: high
- **Depends On**: Task 3
- **Description**: 
  - 创建 `external/dao/runtime/vta-dev/scripts/verify-wheel.sh`
  - 设置PATH=/opt/conda/bin，set -e
  - 实现12项检查:
    1. wheel文件存在且非空（/opt/vta-dist/*.whl）
    2. pip install成功（final阶段已安装，验证importlib.metadata.version）
    3. **Nuitka .so验证**: xmnn.cpython-*.so存在于site-packages中，且xmnn.__file__指向.so（非__init__.py）
    4. `import xmnn` 无错
    5. 6个API模块import无错（compile_api, infer_api, accuracy_api, performance_api, bandwidth_api, excel_report_api）
    6. 6个CLI工具 --help 正常运行
    7. .so库存在且ldd无not found
    8. tools_cpp/libs/下.so RPATH包含$ORIGIN（递归检查）
    9. Python版本>=3.14
    10. GIL disabled验证（`sys._is_gil_enabled() is False`）
    11. 核心依赖import（numpy, onnx, pandas, matplotlib, Pillow, openpyxl, rich, tqdm等）
    12. xmnn数据目录存在（tools_cpp/, fonts/, autolibs/）
  - 每项检查输出PASS/FAIL（带颜色），统计TOTAL/PASSED/FAILED，有FAIL时exit 1
  - TEST_TYPE=full环境变量控制详细程度
- **Acceptance Criteria Addressed**: AC-3, AC-5, AC-9
- **Test Requirements**:
  - `programmatic` TR-4.1: verify-wheel.sh存在且有#!/bin/bash shebang
  - `programmatic` TR-4.2: 脚本包含12项检查（通过grep检查关键词，含Nuitka .so检查）
  - `programmatic` TR-4.3: 脚本有PASS/FAIL输出格式，有TOTAL统计
  - `programmatic` TR-4.4: 有FAIL时脚本exit code为1，全部PASS时exit code为0
  - `programmatic` TR-4.5: 脚本包含xmnn.__file__.endswith('.so')检查（Nuitka特有）
  - `human-judgement` TR-4.6: 检查项覆盖全面，错误信息可定位问题
- **Notes**: 参考xmnn-whl-builder/verify-wheel.sh但适配vta-dev（Nuitka .so验证、12项检查、RPATH递归检查tools_cpp/libs/）

## [x] Task 5: 创建invoke tasks/ namespace包
- **Priority**: high
- **Depends On**: Task 1
- **Description**: 
  - 创建 `external/dao/runtime/vta-dev/tasks/` 目录作为namespace包：
    - `tasks/__init__.py`：共享工具函数、BuildConfig dataclass、config/all任务、Collection组装
    - `tasks/docker.py`：docker.toolchain和docker.build任务
    - `tasks/package.py`：package.extract和package.verify任务
    - `tasks/clean.py`：clean.clean任务
  - BuildConfig dataclass包含：root_dir, dockerfile_path, source_path, image_name, builder_image_name, tag, base_image, dist_dir, logs_dir
  - `_get_project_root()`：从vta-dev/向上查找同时包含`.agents/`和`external/chaos/npuusertools/`的目录
  - `_get_container_bin()`：返回os.environ.get("DOCKER_BIN", "docker")，支持DOCKER_BIN=podman
  - `_run_docker_cmd()`：使用[_get_container_bin()]前缀执行容器命令
  - 任务定义:
    - `config(c)`: 打印当前构建配置（路径、镜像名、容器运行时等）
    - `docker.toolchain(c)`: 检查容器运行时版本>=23.0、BuildKit支持、npuusertools路径、Dockerfile、基础镜像、磁盘空间>10GB
    - `docker.build(c, no_cache=False, debug=False)`: 执行容器build，cwd=cfg.root_dir，-f使用绝对路径，--progress=plain，日志输出到logs/build-*.log；支持--no-cache和--debug（--target builder）
    - `package.extract(c)`: 从final镜像复制wheel到dist/（docker create + docker cp）
    - `package.verify(c)`: 在容器内运行verify-wheel.sh，本地检查dist/中wheel
    - `clean.clean(c, images=False)`: 清理dist/、logs/；--images清理dangling镜像
    - `all(c, default=True)`: 依次执行 docker.toolchain → docker.build → package.verify → package.extract
  - Collection组装：ns.add_collection(docker, name='docker'), ns.add_collection(package, name='package'), ns.add_collection(clean, name='clean')
  - 共享辅助函数：彩色日志（_log_header/_log_step/_log_info/_log_warn/_log_error/_log_success/_log_section）、_run_command（带超时和错误处理）、_clear_directory_contents
- **Acceptance Criteria Addressed**: AC-4, AC-6
- **Test Requirements**:
  - `programmatic` TR-5.1: tasks/__init__.py、tasks/docker.py、tasks/package.py、tasks/clean.py存在且可被Python解析（ast.parse无语法错误）
  - `programmatic` TR-5.2: `invoke --list` 列出namespace任务：config, all, docker.toolchain, docker.build, package.extract, package.verify, clean.clean
  - `programmatic` TR-5.3: docker.build使用`["docker", "build"]`改为`[container_bin, "build"]`，cwd=cfg.root_dir，-f用绝对路径
  - `programmatic` TR-5.4: `invoke config` 打印配置信息含容器运行时
  - `programmatic` TR-5.5: _get_project_root()通过`.agents/`+`external/chaos/npuusertools/`双marker查找根目录
  - `human-judgement` TR-5.6: 代码风格与npu_tvm/tasks.py一致（dataclass配置、日志辅助函数、错误处理模式），namespace组织符合pyinvoke namespace-organization.md参考
- **Notes**: 
  - 参考projects/awesome-okf-xs/doc/bundles/build/tooling/pyinvoke/examples/namespace-organization.md的namespace包模式
  - 原tasks.py已删除，替换为tasks/目录
  - docker.py中Popen使用绝对路径-f和绝对context路径，避免cwd切换问题

## [x] Task 6: 创建build.sh主机端构建脚本（含DOCKER_BIN/podman支持）
- **Priority**: high
- **Depends On**: Task 3, Task 4, Task 5
- **Description**: 
  - 创建 `external/dao/runtime/vta-dev/build.sh`（bash, set -euo pipefail）
  - 功能：
    - ANSI彩色输出（RED/GREEN/YELLOW/CYAN/BOLD/RESET）
    - 自动定位SpecWeave根目录（find_specweave_root函数，查找.agents/和external/chaos/npuusertools/双marker）
    - DOCKER_BIN环境变量支持（默认docker，DOCKER_BIN=podman切换到Podman）
    - 自动设置DOCKER_BUILDKIT=1
    - 检查容器运行时是否可用（command -v $DOCKER_BIN + $DOCKER_BIN info），Podman时给出不同的错误提示
    - 关键路径检查（pyproject.toml, CMakeLists.txt, build-wheel.sh, verify-wheel.sh, npuusertools源码目录）
    - 基础镜像检查（不存在时给出构建指引）
    - 支持参数：
      - `--verify-only, -V`：仅验证已有镜像（跳过构建）
      - `--no-cache, -F`：--no-cache全量重建
      - `--debug, -d`：仅构建到builder阶段（--target builder，镜像tag为vta-dev-builder:latest）
      - `--extract, -e`：构建后提取wheel到本地dist/
      - `--verbose, -v`：set -x详细模式
      - `-h, --help`：帮助信息
    - 日志tee到logs/build-<timestamp>.log
    - Docker build命令使用$DOCKER_BIN，context为$SPECWEAVE_ROOT绝对路径，-f为绝对DOCKERFILE路径
    - 构建后验证（verify_image函数：builder镜像验证wheel+构建工具，final镜像运行verify-wheel.sh+import测试）
    - 提取wheel（docker create + docker cp）
    - 构建结果展示（镜像ID、大小、层数、耗时）
    - 成功后打印快速参考命令
  - 不创建Windows build.bat（用户主要在WSL/Linux环境下使用）
- **Acceptance Criteria Addressed**: AC-6
- **Test Requirements**:
  - `programmatic` TR-6.1: build.sh存在且有#!/bin/bash shebang和set -euo pipefail
  - `programmatic` TR-6.2: build.sh --help 输出帮助信息（含DOCKER_BIN环境变量说明）
  - `programmatic` TR-6.3: 脚本中有DOCKER_BUILDKIT=1设置
  - `programmatic` TR-6.4: 脚本使用$DOCKER_BIN变量（不硬编码docker命令）
  - `programmatic` TR-6.5: 脚本支持--verify-only/--no-cache/--debug/--extract/--verbose/-h选项
  - `programmatic` TR-6.6: 构建context使用$SPECWEAVE_ROOT绝对路径
  - `human-judgement` TR-6.7: 错误信息清晰可操作，中文输出
- **Notes**: build.sh是主要用户入口，直接执行docker build而非委托给invoke（更简洁、日志更直观）；invoke tasks用于Python级编排和CI集成

## [x] Task 7: 创建README.md文档
- **Priority**: medium
- **Depends On**: Task 1
- **Description**: 
  - 创建 `external/dao/runtime/vta-dev/README.md`
  - 内容包含（中文）：
    - 项目简介（vta-dev是什么、基础镜像、Nuitka编译、构建技术栈）
    - 与xmnn-whl-builder的对比
    - 目录结构说明
    - 环境要求（Docker>=23.0/Podman、BuildKit、磁盘空间、invoke安装）
    - 快速开始（pip install invoke → invoke docker.toolchain → bash build.sh --extract）
    - Invoke任务参考（每个namespace任务的用途和常用参数）
    - build.sh参数说明
    - 构建产物说明（dist/中的wheel、镜像名、镜像tag）
    - Nuitka编译说明（AST PREAMBLE、编译时间、ccache加速）
    - 调试方法（--debug模式、-v详细日志）
    - 常见问题排查（Docker权限、BuildKit未启用、基础镜像不存在、bind mount路径错误、Nuitka内存不足、Podman使用）
- **Acceptance Criteria Addressed**: AC-7
- **Test Requirements**:
  - `programmatic` TR-7.1: README.md存在
  - `human-judgement` TR-7.2: 新人按README能独立完成首次构建
  - `human-judgement` TR-7.3: 常见问题覆盖了典型错误场景（含Podman说明）
- **Notes**: README面向工具链使用者（中文），AGENTS.md面向AI智能体

## [x] Task 8: 创建docker-compose.yml开发模式
- **Priority**: medium
- **Depends On**: Task 3
- **Description**: 
  - 创建 `external/dao/runtime/vta-dev/docker-compose.yml`
  - 服务定义（vta-dev服务）：
    - build.context: ../../..（相对于vta-dev/指向SpecWeave根目录）
    - build.dockerfile: external/dao/runtime/vta-dev/Dockerfile
    - volumes: 
      - ../../chaos/npuusertools:/source/npuusertools:ro（只读源码挂载用于开发调试）
      - ./workspace:/workspace
    - stdin_open: true, tty: true
    - command: /bin/bash
  - 精简版（无Jupyter端口暴露、无privileged、无多服务）
- **Acceptance Criteria Addressed**: AC-10
- **Test Requirements**:
  - `programmatic` TR-8.1: docker-compose.yml存在且为有效YAML
  - `programmatic` TR-8.2: build.context为../../..（SpecWeave根目录）
  - `programmatic` TR-8.3: build.dockerfile为external/dao/runtime/vta-dev/Dockerfile
  - `programmatic` TR-8.4: 包含npuusertools只读volume挂载
  - `programmatic` TR-8.5: stdin_open: true, tty: true
  - `human-judgement` TR-8.6: compose配置精简且实用
- **Notes**: 参考chaos/ai/docker-compose.yml但大幅简化（不需要DinD、Jupyter、多服务）

## [x] Task 9: 结构一致性验证
- **Priority**: high
- **Depends On**: Task 1-8
- **Description**: 
  - 执行静态结构验证（端到端Docker构建需基础镜像，此处做静态检查）：
    1. 所有文件存在性检查（14个文件+configs/.gitkeep）
    2. Python语法验证（ast.parse所有tasks/*.py）
    3. Bash脚本shebang和set选项验证
    4. Dockerfile COPY路径一致性验证（以external/dao/runtime/vta-dev/开头）
    5. CMakeLists.txt验证（cmake版本、LANGUAGES NONE、patchelf、chmod）
    6. build-wheel.sh验证（AST PREAMBLE、Nuitka参数、build命令、工作目录/builder）
    7. tasks包一致性验证（_get_project_root双marker、docker build命令、namespace组装、all default=True）
    8. verify-wheel.sh验证（12项检查含Nuitka .so、RPATH=$ORIGIN、PATH=/opt/conda/bin）
    9. build.sh验证（SpecWeave根目录查找、DOCKER_BIN支持、5个CLI选项、中文输出）
    10. docker-compose.yml验证（context、dockerfile路径、volumes、tty）
    11. .gitignore验证（dist/、logs/、workspace/、__pycache__/）
    12. AGENTS.md路由表指向tasks/而非tasks.py
  - 修复发现的问题：
    - AGENTS.md路由表tasks.py→tasks/修复
    - docker.py中docker buildx→docker build修复
    - docker.py中cwd和-f路径修复（绝对路径）
    - _get_project_root修复（双marker而非单AGENTS.md关键词）
    - DOCKER_BIN/podman支持添加
    - configs/.gitkeep创建
- **Acceptance Criteria Addressed**: AC-1 through AC-10 (structural verification)
- **Test Requirements**:
  - `programmatic` TR-9.1: 11项结构验证全部通过
  - `programmatic` TR-9.2: 所有Python文件ast.parse无语法错误
  - `programmatic` TR-9.3: AGENTS.md路由表不再引用已删除的tasks.py
  - `human-judgement` TR-9.4: 文件结构完整，无遗漏文件
- **Notes**: 端到端Docker构建验证（需devcontainer-base:onnx-quantized-latest镜像）需在基础镜像可用后手动执行 `bash build.sh --extract`

## [x] Task 10: 端到端Docker构建验证（已完成，含Nuitka补丁+CLI+Podman适配）
- **Priority**: high
- **Depends On**: Task 9
- **Description**: 
  - 前置条件：devcontainer-base:onnx-quantized-latest镜像已本地构建
  - 执行完整构建流程（WSL Podman 5.7.0，Python 3.14t cp314t free-threading）：
    1. 修复Nuitka 4.3rc1源码6处Python 3.14t free-threading兼容bug（allocator.h/python_internals_access.h/CompiledFrameType.c/HelpersAllocator.c）
    2. 诊断并解决Nuitka包模式__file__虚拟路径问题（改用__loader__=nuitka_module_loader检测）
    3. 解决shutdown segfault（exit code 139）：os._exit(0) workaround
    4. 创建CLI启动器（xmnn_cli_launchers.py + [project.scripts] 7个入口点）
    5. 修复invoke tasks的Podman版本检测（Podman>=4.0而非Docker>=23.0）
    6. 修复package.extract路径问题（/.复制目录内容而非目录本身）
    7. 修复verify-wheel.sh移除click误报（typer 0.27+内置click）
    8. 修复build.sh CRLF换行符问题
  - 最终验证结果：
    - verify-wheel.sh: **13 passed, 0 failed, 1 warning**（仅dev build版本号警告）
    - 7个CLI工具--help全部PASS（xmflow + xmnn-compile/infer/accuracy/performance/bandwidth/excelreport）
    - wheel: xmnn-1.2.1.dev0-cp314-cp314t-linux_x86_64.whl (34.5MB)
    - Nuitka .so: xmnn.cpython-314t-x86_64-linux-gnu.so (5.2MB)
    - 12个xmnn子模块全部nuitka_module_loader加载
    - 16个预编译.so库RPATH=$ORIGIN，ldd无not found
    - npuusertools子模块xmnn/__init__.py干净（AST PREAMBLE已恢复）
    - invoke 7个任务全部验证通过（config/toolchain/build/extract/verify/clean/all）
- **Acceptance Criteria Addressed**: AC-1, AC-2, AC-3, AC-4, AC-5, AC-6, AC-8, AC-9
- **Test Requirements**:
  - `programmatic` TR-10.1: Podman build exit code为0 ✅
  - `programmatic` TR-10.2: verify-wheel.sh 13项检查全部PASS（1 WARN dev version）✅
  - `programmatic` TR-10.3: type(xmnn.__loader__).__name__ == 'nuitka_module_loader' ✅
  - `programmatic` TR-10.4: 7个CLI工具--help均可运行 ✅
  - `programmatic` TR-10.5: npuusertools子模块git status干净 ✅
  - `programmatic` TR-10.6: dist/目录下xmnn-*.whl (34.5MB) ✅
  - `human-judgement` TR-10.7: 构建日志清晰，可追溯每个阶段 ✅
- **Notes**: 全程使用Python 3.14t（用户要求"我就要使用py314t"），Nuitka从本地patched源码安装（external/libs/tools/Nuitka/Nuitka），含6处free-threading兼容补丁
