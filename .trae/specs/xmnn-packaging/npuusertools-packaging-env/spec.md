# npuusertools 打包环境 (vta-dev) - 产品需求文档

## Overview
- **Summary**: 基于 `devcontainer-base:onnx-quantized-latest` 镜像，为 `external/chaos/npuusertools`（XMNN NPU用户工具链）创建一套Docker化的打包构建与运行时环境。使用 invoke 作为任务编排器，scikit-build-core + CMake + Ninja 作为Python wheel构建系统，两阶段Docker构建（builder→final）产出可复用的wheel包和vta-dev运行时镜像。最终产物部署在 `external/dao/runtime/vta-dev/` 目录下。
- **Purpose**: 解决npuusertools缺乏标准化、可复现、容器化打包环境的问题。当前npuusertools依赖开发者本地Python环境（py313z），无法保证构建一致性；预编译C++库的RPATH和依赖管理需要标准化流程；需要与chaos/ai体系的xmnn-whl-builder保持架构一致性。
- **Target Users**: XMNN工具链开发者、需要在标准环境中编译/验证/使用npuusertools的工程师、CI/CD系统。

## Goals
- G1: 创建两阶段Dockerfile（vta-dev-builder → vta-dev:latest），builder阶段基于onnx-quantized安装Nuitka/ccache/clang等构建依赖，使用Nuitka将xmnn Python源码编译为.so扩展模块后产出wheel；final阶段安装wheel、运行verify-wheel.sh验证并保留wheel副本到/opt/vta-dist/
- G2: 实现invoke任务编排（tasks/ namespace包形式），提供 config/docker.toolchain/docker.build/package.extract/package.verify/clean.clean/all 七个核心任务
- G3: 支持BuildKit bind mount方式挂载npuusertools源码（不复制进镜像），源码修改可直接重建；支持pip cache和ccache cache加速增量构建
- G4: 产出的wheel包含Nuitka编译的xmnn.cpython-*.so扩展模块、预编译C++库（RPATH已修复为$ORIGIN）、数据目录（tools_cpp/fonts/autolibs），可在final镜像中正常import和运行
- G5: 提供一键构建脚本（build.sh），自动处理build context定位、BuildKit启用、错误提示，支持--verify-only/--no-cache/--debug/--extract/--verbose选项；通过DOCKER_BIN环境变量兼容docker和WSL下的podman
- G6: 提供verify-wheel.sh对wheel做13项验证检查（Nuitka .so验证、文件存在性、import测试、API模块导入、7个CLI工具可用性、预编译库加载+ldd、RPATH=$ORIGIN、Python>=3.14、GIL disabled状态、核心依赖、可选依赖、数据目录、wheel文件）
- G7: 遵循SpecWeave workspace discovery协议，提供AGENTS.md（含启动协议/路由表/核心红线）和README.md（含环境要求/快速开始/目录结构/排错指南）
- G8: 最终产物（Dockerfile、pyproject.toml、CMakeLists.txt、tasks/ namespace包、scripts/、configs/、build.sh、docker-compose.yml、AGENTS.md、README.md、.gitignore）全部位于 `external/dao/runtime/vta-dev/`

## Non-Goals (Out of Scope)
- NG1: 不修改npuusertools子模块内的任何文件（它是git submodule，不可直接修改）
- NG2: 不集成npu_tvm编译器源码（npuusertools已有预编译库，无需npu_tvm绑定）
- NG3: 不在默认镜像中安装PyTorch（torch是可选依赖，镜像体积控制优先）
- NG4: 不创建多Python版本矩阵（第一版固定cp314t free-threading，与onnx-quantized基础镜像一致）
- NG5: 不集成TVM/VTA的Nuitka编译（vta-dev仅编译xmnn包，不包含npu_tvm源码和tvm/vta运行时编译）
- NG6: 不推送到Docker Registry或制作release tarball（本地构建环境，非分发渠道）

## Background & Context
- **基础镜像链**: devcontainer-base:base → conda-llvm → onnx-dev → onnx-quantized（继承Python 3.14.6 cp314t free-threading、LLVM/Clang 22.1.8、cmake 3.x、ninja、ONNX/ONNX Runtime生态、无PyTorch）
- **npuusertools构建特点**: pyproject.toml使用scikit-build-core>=0.5 + setuptools-scm>=8.0；CMakeLists.txt使用`LANGUAGES NONE`（不编译C++），仅做版本文件生成（xmnn/_version.py）、Python包+数据目录安装、patchelf RPATH修复；预编译库位于xmnn/tools_cpp/libs/*/*/*.so和xmnn/tools_cpp/bin/*/*/
- **参考架构**: external/chaos/ai/xmnn-whl-builder/ 两阶段Docker模式（BuildKit bind mount、pip/ccache cache mount、/opt/xmnn-dist/ wheel输出、verify-wheel.sh验证、docker-compose.yml开发模式）
- **invoke参考**: external/chaos/npu_tvm/tasks.py 的@task模式和BuildConfig dataclass；projects/awesome-okf-xs/doc/bundles/build/tooling/pyinvoke/ 和 invocations/ 的知识体系
- **Python包名**: xmnn（注意：目录名是npuusertools，但pip包名是xmnn）；CLI使用typer框架，统一入口为`xmflow`命令（包含compile/infer/accuracy/performance/bandwidth/excelreport 6个子命令），vta-dev通过`xmnn_cli_launchers.py`薄封装层+`[project.scripts]`暴露7个console_scripts入口点（xmflow + 6个xmnn-*命令）

## Functional Requirements
- **FR-1**: Dockerfile支持两阶段构建（语法=docker/dockerfile:1.7-labs），builder阶段必须使用Nuitka编译xmnn Python源码为.so扩展模块
  - builder阶段（vta-dev-builder）: 基于onnx-quantized，安装nuitka、ccache、scikit-build-core、setuptools-scm、build、invoke、patchelf、auditwheel、cloudpickle、typer等构建依赖；配置CC/CXX/LLVM_CONFIG指向conda clang；使用BuildKit bind挂载npuusertools源码和本地Nuitka源码（external/libs/tools/Nuitka/Nuitka，含Python 3.14t free-threading补丁）；通过build-wheel.sh脚本执行AST PREAMBLE注入→Nuitka --module编译xmnn包→scikit-build-core打包wheel；vta-dev自带pyproject.toml和CMakeLists.txt用于打包Nuitka编译产物（安装.so到site-packages根目录、CLI启动器到site-packages根目录、数据目录到xmnn/）；wheel输出到/opt/vta-dist/
  - final阶段（vta-dev:latest）: 基于onnx-quantized，从builder复制wheel，pip安装wheel，运行verify-wheel.sh验证，保留wheel副本到/opt/vta-dist/
- **FR-2**: invoke 使用namespace包形式（tasks/目录），提供以下任务:
  - `invoke docker.toolchain`: 检查docker版本、BuildKit支持、npuusertools源码路径、磁盘空间
  - `invoke config`: 显示/验证构建配置（镜像名、tag、源码路径、输出目录、容器运行时）
  - `invoke docker.build`: 执行docker build构建两阶段镜像，支持--no-cache、--debug参数
  - `invoke package.extract`: 从final镜像提取wheel到本地dist/目录
  - `invoke package.verify`: 运行容器内的verify-wheel.sh和本地smoke test
  - `invoke clean.clean`: 清理构建产物（dist/、logs/、<none>镜像）
  - `invoke all`: 依次执行toolchain→build→verify→extract
- **FR-3**: build.sh主机端构建脚本:
  - 自动定位SpecWeave根目录作为Docker build context（解决V2问题）
  - 自动设置DOCKER_BIN（支持docker和podman）
  - 检查docker>=23.0或podman>=4.0
  - 支持--debug、--no-cache、--verify-only、--extract参数
  - 错误时给出可操作的提示信息
- **FR-4**: verify-wheel.sh容器内验证脚本，至少检查:
  1. Python版本>=3.14且为cp314t free-threading（abiflags包含't'，sys._is_gil_enabled()为False）
  2. wheel可正常pip install
  3. xmnn.cpython-*.so（Nuitka编译产物）存在于site-packages根目录（Nuitka包模式将整个包编译为单个.so）
  4. `import xmnn` 不报错，且 `type(xmnn.__loader__).__name__ == 'nuitka_module_loader'`（Nuitka包模式下__file__为虚拟路径，__loader__是可靠标识）
  5. `import xmnn.compile_api` / `infer_api` / `accuracy_api` / `performance_api` / `bandwidth_api` / `excel_report_api`（tvm依赖的模块按NG5跳过）
  6. 7个CLI工具（xmflow + xmnn-compile/infer/accuracy/performance/bandwidth/excelreport）的--help可正常运行（os._exit(0)绕过Py_Finalize()段错误）
  7. 核心依赖（numpy/scipy/cloudpickle）和可选依赖（pandas/matplotlib/onnx/typer/Pillow等）可import
  8. xmnn数据目录（tools_cpp/、fonts/、autolibs/）存在
  9. 预编译.so库存在且可被ldd找到（无not found依赖）
  10. 所有tools_cpp/libs/下.so的RPATH设置为$ORIGIN
  11. xmnn子模块（config/op_registration/utils等）由Nuitka编译（__loader__为nuitka_module_loader）
  12. wheel文件存在且大小>0
  13. xmnn版本可获取（dev build无版本号为WARN非FAIL）
- **FR-5**: docker-compose.yml支持开发模式:
  - 挂载npuusertools源码到容器内（用于开发调试）
  - 暴露Jupyter端口（8888）
  - 设置工作目录为/workspace
  - 支持privileged模式（如需）
- **FR-6**: AGENTS.md遵循SpecWeave workspace discovery协议:
  - 包含启动协议、核心红线、按需阅读路由表
  - 说明与chaos/ai的关系、与npuusertools子模块的边界
  - 快速开始三步流程
- **FR-7**: README.md包含:
  - 环境要求（docker版本、BuildKit、磁盘空间）
  - 快速开始（3条命令）
  - 目录结构说明
  - 常见问题排查

## Non-Functional Requirements
- **NFR-1 (可复现性)**: 相同源码在不同机器上构建出的wheel功能一致（排除时间戳等元数据差异）
- **NFR-2 (构建性能)**: 首次构建（含基础镜像pull）<15分钟；增量构建（源码改动后）<5分钟；使用pip cache mount和BuildKit缓存
- **NFR-3 (镜像体积)**: final镜像大小不超过onnx-quantized基础镜像+500MB（不含模型数据）
- **NFR-4 (可维护性)**: 与xmnn-whl-builder架构模式一致（两阶段、bind mount、verify脚本、/opt/*-dist/输出），降低认知负担
- **NFR-5 (健壮性)**: build.sh和invoke任务在前置条件不满足时给出清晰错误信息，不以静默方式失败
- **NFR-6 (源码保护)**: npuusertools源码通过bind mount挂载，不COPY进镜像层，避免源码意外打包进镜像分发

## Constraints
- **Technical**: 
  - 必须基于 `devcontainer-base:onnx-quantized-latest`（用户指定）
  - 必须使用 invoke（namespace包形式） + scikit-build-core + cmake + ninja（用户指定）
  - **必须使用 Nuitka 将 xmnn Python 源码编译为 .so 扩展模块**（用户约束）
  - Python包名是xmnn（不是npuusertools）
  - vta-dev自带独立的pyproject.toml和CMakeLists.txt用于打包Nuitka编译产物（不修改npuusertools内的构建文件）
  - CMakeLists.txt使用LANGUAGES NONE，不编译C++代码（仅安装Nuitka产物+预编译库+数据文件）
  - Docker BuildKit必须启用（使用--mount=type=bind/cache）
  - Docker syntax版本: docker/dockerfile:1.7-labs
  - 构建context必须是SpecWeave根目录，使得bind mount source路径可解析
  - 容器运行时兼容：支持docker（默认）和WSL下的podman（通过DOCKER_BIN环境变量）
- **Business**: 
  - 产物必须放在 `external/dao/runtime/vta-dev/`（用户指定）
  - 不修改external/chaos/npuusertools/内的任何文件（git submodule保护）
- **Dependencies**: 
  - Docker >= 23.0 或 Podman >= 4.0（BuildKit bind mount支持）
  - npuusertools子模块已存在且包含完整源码+预编译库
  - devcontainer-base:onnx-quantized-latest镜像已构建或可从registry拉取
  - 本地Nuitka源码（external/libs/tools/Nuitka/Nuitka）已应用Python 3.14t free-threading兼容补丁

## Assumptions
- A1: devcontainer-base:onnx-quantized-latest镜像本地可用或可构建（如不可用，需先构建该variant）
- A2: npuusertools的预编译.so库与cp314t free-threading Python兼容（final镜像的smoke test会验证此假设）
- A3: patchelf在onnx-quantized基础镜像中可用（若不可用，builder阶段需apt-get安装）
- A4: 用户在WSL2或Linux环境下运行Docker（Windows原生Docker Desktop可能有权限/bind mount路径问题，但build.sh会处理路径转换）
- A5: npuusertools/.git目录在bind mount时可访问（setuptools-scm需要；如不可用，通过SETUPTOOLS_SCM_PRETEND_VERSION兜底）
- A6: 构建时不需要网络代理特殊配置（如需代理，通过~/.docker/config.json或HTTP_PROXY环境变量）

## Acceptance Criteria

### AC-1: Docker两阶段构建成功
- **Given**: Docker >=23.0（或Podman >=4.0）已安装，devcontainer-base:onnx-quantized-latest镜像可用，npuusertools子模块完整，本地Nuitka源码已应用Python 3.14t补丁
- **When**: 在 `external/dao/runtime/vta-dev/` 下执行 `bash build.sh` 或 `inv docker.build`
- **Then**: 构建成功完成，生成vta-dev:latest镜像（builder镜像仅在--debug模式保留），退出码为0；final阶段verify-wheel.sh所有检查PASS
- **Verification**: `programmatic`

### AC-2: wheel包正确产出
- **Given**: 两阶段构建完成
- **When**: 执行 `invoke package`
- **Then**: dist/目录下生成xmnn-*.whl文件，wheel包含xmnn/包、xmnn/tools_cpp/libs/预编译库、xmnn/_version.py
- **Verification**: `programmatic`

### AC-3: wheel验证全部通过
- **Given**: 构建完成且final镜像可用
- **When**: 执行 `invoke package.verify` 或在容器内运行verify-wheel.sh
- **Then**: verify-wheel.sh的13项检查全部PASS，无FAIL项；特别确认Nuitka编译的xmnn.cpython-*.so存在于site-packages根目录、`type(xmnn.__loader__).__name__ == 'nuitka_module_loader'`、import xmnn成功、7个CLI工具（xmflow + 6个xmnn-*）--help正常、GIL为disabled状态、tools_cpp/libs/下.so的RPATH=$ORIGIN
- **Verification**: `programmatic`

### AC-4: invoke任务编排完整可用
- **Given**: 在vta-dev/目录下，Python环境已安装invoke
- **When**: 执行 `invoke --list`
- **Then**: 列出config、all、docker.toolchain、docker.build、package.extract、package.verify、clean.clean七个任务（namespace组织为docker/package/clean子集合）；每个任务执行时输出清晰的日志，失败时返回非零退出码
- **Verification**: `programmatic`

### AC-5: 7个CLI工具在容器内可用
- **Given**: vta-dev:latest镜像已构建
- **When**: 运行 `docker run --rm vta-dev:latest xmnn-compile --help`（以及其他6个命令：xmnn-infer/xmnn-accuracy/xmnn-performance/xmnn-bandwidth/xmnn-excelreport/xmflow）
- **Then**: 每个命令都能正常输出帮助信息，无ModuleNotFoundError或ImportError，无退出码139（段错误）
- **Verification**: `programmatic`

### AC-6: build.sh自动处理路径和BuildKit
- **Given**: 在任意子目录下调用build.sh（不要求在vta-dev/下）
- **When**: 执行 `bash build.sh`
- **Then**: 自动定位SpecWeave根目录作为build context，自动设置DOCKER_BUILDKIT=1，给出清晰的构建进度输出
- **Verification**: `programmatic`

### AC-7: AGENTS.md和README.md符合规范
- **Given**: vta-dev/目录下的AGENTS.md和README.md
- **When**: 新人开发者阅读文档
- **Then**: AGENTS.md包含启动协议、路由表、核心红线、三步快速开始；README.md包含环境要求、快速开始、目录结构、排错指南
- **Verification**: `human-judgment`

### AC-8: 不修改npuusertools子模块
- **Given**: 构建前后
- **When**: 在npuusertools/目录执行 `git status`
- **Then**: 工作区干净，无被修改/新增的文件
- **Verification**: `programmatic`

### AC-9: 预编译库RPATH正确
- **Given**: final镜像已安装wheel
- **When**: 在容器内检查xmnn/tools_cpp/libs/下所有.so文件的RPATH
- **Then**: 所有.so的RPATH包含$ORIGIN，ldd检查无"not found"依赖
- **Verification**: `programmatic`

### AC-10: 与chaos/ai架构模式一致
- **Given**: 对比xmnn-whl-builder和vta-dev的结构
- **When**: 架构师审查
- **Then**: 两阶段构建模式、BuildKit bind/cache mount、/opt/*-dist/输出、verify-wheel.sh验证等核心模式保持一致，仅在构建步骤（Nuitka→scikit-build-core）和任务编排（新增invoke）上有差异
- **Verification**: `human-judgment`

## Open Questions
- [ ] Q1: devcontainer-base:onnx-quantized-latest镜像当前是否已本地构建？如果没有，是否需要在vta-dev构建流程中自动检测并触发基础镜像构建？（建议：invoke toolchain检查基础镜像是否存在，不存在时给出构建指引，但不自动触发以避免耗时）
- [ ] Q2: final镜像是否需要Jupyter支持（xmnn-whl-builder有注册Jupyter kernel）？（建议：包含Jupyter，因为基础镜像已有Jupyter生态，增量成本低）
- [ ] Q3: docker-compose.yml是否必需？用户没有明确要求，但xmnn-whl-builder有。（建议：包含最小化的compose文件用于开发调试）
