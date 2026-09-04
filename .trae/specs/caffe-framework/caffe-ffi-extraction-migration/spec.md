# Caffe-FFI 萃取迁移与Docker化 - Product Requirement Document

## Overview
- **Summary**: 将vendor/caffe/caffe-ffi萃取为独立C++原生扩展库（libs/caffe-ffi），并创建基于jupyter-ssh-base的Docker开发环境（apps/caffe-ffi-jupyter），支持Python 3.14+和WSL编译；同时建立统一结构化日志、PowerShell-WSL跨Shell包装器、一键部署、环境诊断、文档版本标注等可复用工程化机制。
- **Purpose**: 消除vendor路径依赖，使caffe-ffi成为可独立编译、测试、安装和分发的第一方库；提供开箱即用的Docker开发环境降低使用门槛；沉淀跨项目可复用的工程化脚本和文档规范。
- **Target Users**: 深度学习框架开发者、需要使用Caffe模型推理的研究人员、caffe-ffi贡献者、SpecWeave项目其他子项目维护者。

## Goals
- 将caffe-ffi从vendor/caffe/caffe-ffi完整复制到libs/caffe-ffi，作为独立第一方项目
- 修复CMake硬编码路径问题，使项目可独立编译（不依赖vendor父目录结构）
- 对齐libs/目录现有项目（npu-ffi）的标准结构和开发脚本
- 创建apps/caffe-ffi-jupyter Docker开发环境，基于jupyter-ssh-base
- Docker镜像保留SSH+Jupyter双服务，使用Miniconda提供Python 3.14环境
- 提供完整的构建、运行、测试脚本和文档
- 建立统一结构化日志库（Bash+PowerShell双版本），支持自动化监控接入
- 提供WSL/Windows双平台一键部署脚本和环境诊断脚本
- 创建WSL专项部署指南，包含Docker方案对比和版本标注
- 沉淀可跨项目复用的PowerShell-WSL包装器模式和文档规范模板
- 为apps目录下其他WSL-first项目补充PowerShell包装器

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

### FR-8: 统一结构化日志库
- 创建scripts/lib/logging.sh（Bash）和scripts/lib/logging.ps1（PowerShell）双版本统一日志库
- 支持日志级别：INFO/WARN/ERROR/DEBUG
- 支持输出格式：text（人类可读）和json（自动化监控）
- JSON日志统一字段：timestamp, level, script, message
- 支持参数：--log-format, --log-level, --log-json
- 所有shell脚本（build.sh/wsl-deploy.sh/diagnose.sh/deploy.ps1/diagnose.ps1）统一引用此日志库

### FR-9: 一键部署脚本（WSL + Windows）
- 创建scripts/wsl-deploy.sh：WSL环境全流程自动化部署
  - 功能链：WSL环境检测 → Docker服务检查 → jupyter-ssh-base基础镜像构建 → caffe-ffi-jupyter镜像构建 → 容器启动 → 健康检查 → 自动化验证 → 结果报告
  - 支持参数：--cn(国内镜像源)、--no-cache、--verify
- 创建scripts/deploy.ps1：Windows PowerShell部署入口
  - 自动检测WSL环境和可用发行版
  - Windows路径自动转换为WSL路径（/mnt/盘符/路径）
  - 参数透传至wsl-deploy.sh
  - 集成统一结构化日志库，支持JSON输出

### FR-10: 环境诊断脚本
- 创建scripts/diagnose.sh和scripts/diagnose.ps1双版本诊断工具
- 诊断项覆盖：WSL状态、Docker服务可用性、基础镜像存在性、端口占用(22/8888)、容器运行状态、_caffe_ffi.so共享库依赖ldd检查、Jupyter内核注册
- 输出问题定位提示和修复建议
- 集成统一结构化日志库
- 支持text/json输出格式

### FR-11: WSL专项部署指南（WSL-DEPLOY-GUIDE.md）
- 创建专门面向WSL用户的详细部署指南
- 内容包含：前置条件检查、WSL2安装配置、Docker安装方案选型（Docker Desktop vs 原生Docker）、性能对比数据、一键部署步骤、手动部署步骤、验证方法、常见问题排查、诊断工具使用
- 包含Docker Desktop vs 原生Docker在WSL2中的性能对比表格
- 应用文档版本标注机制（见FR-12）
- 推荐Ubuntu版本：24.04 / 26.04

### FR-12: 文档版本标注机制（跨项目复用）
- 建立文档版本标注规范，解决硬编码版本号漂移问题
- Frontmatter标准字段：title, last_verified（最后验证日期）, versions_validated（已验证组件版本列表）
- 内联验证注释：<!-- verified: YYYY-MM-DD -->标记具体命令/配置的验证日期
- 版本兼容性附录：组件版本对照表，含推荐版本、最后验证日期、备注
- 沉淀为可复用模板：.agents/templates/shell-snippets/docs-version-annotation.md
- WSL-DEPLOY-GUIDE.md作为首个应用示例

### FR-13: 技术方案对比小节规范（跨项目复用）
- 建立技术文档中方案对比章节的标准化模板
- 标准结构：性能对比表、场景推荐矩阵、已知坑点/注意事项
- 性能对比表列：指标、方案A、方案B、优势方
- 场景推荐矩阵：场景特征、推荐方案、原因说明
- 沉淀为可复用模板：.agents/templates/shell-snippets/deployment-guide-comparison-section.md
- Docker Desktop vs原生Docker对比作为首个应用示例

### FR-14: PowerShell-WSL跨Shell包装器模式（跨项目推广）
- 萃取标准化的PowerShell调用WSL bash脚本模式
- 统一流程：WSL检测→发行版选择→路径转换→参数透传→前置检查→结构化日志
- 为apps/目录下其他WSL-first项目补充PowerShell包装器：
  - apps/jupyter-ssh-base/scripts/build.ps1
  - apps/pytorch-base/build.ps1
  - apps/xmnn-runtime/docker/build.ps1
- 沉淀为可复用模式文档和模板

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

### NFR-5: 可观测性与运维友好
- 所有shell脚本提供统一结构化日志输出，支持JSON格式便于自动化监控平台接入
- 提供一键部署脚本降低用户使用门槛
- 提供诊断脚本，出现问题时可快速定位故障点并给出修复建议
- 日志字段标准化（timestamp/level/script/message），便于日志聚合分析

### NFR-6: 跨平台一致性
- Windows PowerShell和WSL Bash提供功能对齐的脚本入口
- PowerShell包装器自动检测WSL环境，用户无需手动切换环境
- 双平台脚本API保持一致（参数名称、行为、输出格式）
- Windows路径自动转换为WSL路径，用户无需手动处理路径差异

### NFR-7: 文档可维护性
- 技术文档携带版本标注信息，明确标注验证日期和适用版本
- 提供版本兼容性附录，清晰展示各组件版本适配关系
- 方案对比章节标准化，便于读者快速决策
- 文档版本标注机制可跨项目复用，避免版本漂移问题

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

### AC-12: 统一结构化日志库可用
- **Given**: 项目脚本目录存在
- **When**: 检查scripts/lib/目录
- **Then**: logging.sh和logging.ps1均存在，API对齐，支持text/json双格式输出
- **Verification**: `programmatic`

### AC-13: 一键部署脚本可执行
- **Given**: WSL环境可用，Docker服务运行
- **When**: 在apps/caffe-ffi-jupyter/执行`bash scripts/wsl-deploy.sh`（或PowerShell中执行`.\scripts\deploy.ps1`）
- **Then**: 自动完成环境检测→镜像构建→容器启动→健康检查→全量验证流程，输出结构化报告
- **Verification**: `programmatic`（WSL中执行）

### AC-14: 诊断脚本可定位问题
- **Given**: 任意部署状态（成功/失败）
- **When**: 执行`bash scripts/diagnose.sh`（或PowerShell中执行`.\scripts\diagnose.ps1`）
- **Then**: 输出各组件状态诊断结果，对异常项给出明确的修复建议
- **Verification**: `human-judgment`

### AC-15: WSL部署指南完整可用
- **Given**: WSL-DEPLOY-GUIDE.md创建完成
- **When**: 阅读文档
- **Then**: 包含WSL2配置、Docker方案对比（含性能数据）、一键/手动部署、验证方法、排错指南、版本兼容性表
- **Verification**: `human-judgment`

### AC-16: 文档版本标注机制应用
- **Given**: WSL-DEPLOY-GUIDE.md已应用版本标注
- **When**: 检查文档frontmatter和内容
- **Then**: frontmatter包含last_verified和versions_validated，内联有<!-- verified -->注释，附录有版本兼容性表
- **Verification**: `programmatic`

### AC-17: 跨项目PowerShell包装器创建完成
- **Given**: apps目录下其他WSL-first项目存在
- **When**: 检查jupyter-ssh-base/pytorch-base/xmnn-runtime目录
- **Then**: 各项目均存在遵循统一模式的build.ps1包装器
- **Verification**: `programmatic`

### AC-18: 文档规范模板沉淀完成
- **Given**: shell-snippets模板目录存在
- **When**: 检查模板文件
- **Then**: deployment-guide-comparison-section.md和docs-version-annotation.md模板存在，README索引已更新
- **Verification**: `programmatic`

## Open Questions (Resolved)
- [x] ubuntu:26.04默认Python版本是3.13还是3.14？如果是3.14是否可以不用Miniconda直接用系统Python？→ **已解决**: 使用Miniconda确保Python 3.14环境，推荐Ubuntu版本24.04/26.04
- [x] libs/tvm-ffi是否已存在于xuanspace中？如果存在，开发模式的相对路径应为`../tvm-ffi`（从libs/caffe-ffi视角）→ **已解决**: CMake已配置自动检测../tvm-ffi，不存在时使用find_package
- [x] caffe-ffi-jupyter的Dockerfile中，是否需要在builder阶段单独编译C++库然后COPY到runtime？→ **已解决**: 采用双阶段构建（builder + runtime），builder编译，runtime仅复制conda环境和配置运行时
- [x] 是否需要docker-compose.yml中包含volume挂载示例用于开发模式？→ **已解决**: 已包含volume挂载示例，README和WSL-DEPLOY-GUIDE.md均有开发模式说明
- [x] 是否需要统一脚本日志格式便于自动化监控？→ **已解决**: 已创建scripts/lib/统一日志库，所有脚本集成支持JSON输出
- [x] Windows用户如何方便地在WSL中执行部署？→ **已解决**: 已创建deploy.ps1/diagnose.ps1等PowerShell包装器，自动WSL检测和路径转换
- [x] 部署失败如何快速定位问题？→ **已解决**: 已创建diagnose.sh/diagnose.ps1诊断脚本，提供详细的故障排查
- [x] Docker Desktop vs 原生Docker在WSL2中如何选择？→ **已解决**: WSL-DEPLOY-GUIDE.md包含性能对比数据表格和场景推荐矩阵

## Progress

**状态**: ✅ 主体完成（待WSL环境Docker完整构建验证）
**完成日期**: 2026-07-30
**原子提交**: xuanspace子模块 ef5827d

### 已完成项
- ✅ **libs/caffe-ffi独立项目**: 完整迁移、CMake独立化、标准结构对齐npu-ffi
- ✅ **Docker开发环境**: apps/caffe-ffi-jupyter基于jupyter-ssh-base，双阶段构建
- ✅ **Python 3.14+支持**: conda环境、RPATH配置、运行时链接修复
- ✅ **SSH+Jupyter双服务**: 完整保留基础镜像功能，自动conda环境激活
- ✅ **C++单元测试**: 40/40通过（含Per-suite耗时统计和Top 5 slowest报告）
- ✅ **Python单元测试**: 65/65通过（test_python_api.py，含耗时统计）
- ✅ **统一结构化日志库**: Bash+PowerShell双版本，JSON输出支持
- ✅ **一键部署脚本**: wsl-deploy.sh(WSL) + deploy.ps1(PowerShell)，集成全量验证
- ✅ **诊断脚本**: diagnose.sh/diagnose.ps1双版本
- ✅ **WSL部署指南**: WSL-DEPLOY-GUIDE.md含Docker方案对比和版本标注
- ✅ **跨项目模式沉淀**: PowerShell-WSL包装器、文档版本标注、方案对比模板
- ✅ **项目文档**: README.md(含Docker指引)、CHANGELOG.md(记录迁移来源)、LICENSE

### 待用户在WSL环境执行
- ⏳ Docker容器完整构建验证：`bash apps/caffe-ffi-jupyter/scripts/wsl-deploy.sh`
