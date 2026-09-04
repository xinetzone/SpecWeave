---
id: "xmnn-whl-build-workflow-tutorial-spec"
title: "XMNN Wheel 从零构建打包流程学习教程（AI 规范文档）"
source: "seven-concepts knowledge-scenario: external/chaos/xmtools（本地构建打包系统源码）"
date: "2026-08-10"
tags: ["XMNN", "xmtools", "wheel打包", "Nuitka", "scikit-build-core", "CMake", "知识沉淀", "构建教程"]
---

# XMNN Wheel 从零构建打包流程学习教程 - Product Requirement Document

## Overview
- **Summary**: 系统学习 `external/chaos/xmtools` 的 xmnn wheel 从零构建打包完整流程，将所学知识沉淀为一篇综合性的 AI 规范文档（教程），放置于 `external/chaos/ai/.agents/docs/` 目录，覆盖 Docker 一键构建、本地 invoke 构建、wheel 验证标准、CMake 打包原理四条路径。xmtools 是 XMNN NPU 推理工具包的 wheel 打包系统，使用 scikit-build-core + CMake + Nuitka + Ninja 工具链，将 TVM/VTA 原生库与 Python 代码打包为自包含 wheel，并提供 Docker 运行时镜像与 REST API 推理服务。
- **Purpose**: 帮助 AI 开发者、NPU 工具链开发者、构建工程师快速掌握 xmnn wheel 从零构建的完整链路——从 Docker 构建环境搭建，到 Nuitka 编译 tvm/vta/xmnn 三大 Python 包，再到 scikit-build-core + CMake 打包 wheel，最后到 9 项验证标准的闭环流程。
- **Target Users**: AI 协作者（Agent）、XMNN/NPU 工具链开发者、构建工程师、chaos/ai 开发环境用户。

## Goals
- 从 xmtools 源码提炼 xmnn wheel 从零构建的完整事实与流程
- 覆盖 Docker 一键构建路径（Dockerfile 环境 + build-and-test.sh + run-build.sh + verify-wheel.sh）
- 覆盖本地 invoke 构建路径（tasks.py 的 inv build-all / build-tvm / nuitka-* / build-wheel / verify）
- 覆盖 wheel 验证标准（verify-wheel.sh 9 项测试 + auditwheel + 依赖解析）
- 覆盖 CMake 打包原理（CMakeLists.txt 的 _libs 打包、RPATH、数据目录安装、bootstrap 注入）
- 产出物为综合 AI 规范文档，置于 chaos/ai/.agents/docs/ 下，与既有 build/mount/verify 规则形成互补
- 完成知识沉淀方法论闭环（R→I→E→V→入库）

## Non-Goals (Out of Scope)
- 不实现或修改 xmtools / npu_tvm / npuusertools 的任何源码
- 不覆盖 chaos/ai 镜像本身的构建（已有 chaos-ai-npu-devcontainer spec 与 build.md 规则）
- 不覆盖 xmnn 推理服务（REST API / Docker Compose）的部署细节（xmtools README 已覆盖）
- 不覆盖 npuusertools / npu_tvm 内部源码实现细节（仅作为构建输入路径引用）
- 不实际执行 wheel 构建（受环境限制，教程以源码为依据 + 标注"需验证"）

## Background & Context
- xmtools 位于 `external/chaos/xmtools`，是 xmnn wheel 的构建打包系统（独立 git 仓库）
- 依赖三个源码目录：`xmtools`（构建配置）、`../npu_tvm`（TVM C++/Python 源码）、`../npuusertools`（xmnn Python 源码）
- 核心工具链：scikit-build-core (PEP 517) + CMake + Ninja + LLVM/Clang 22 + Nuitka（Python 编译为原生 .so）
- Python 硬性要求 ≥ 3.14，平台仅支持 Linux x86_64（Windows/macOS 通过 WSL2/Docker 构建）
- 构建产物：`dist/xmnn-1.2.1.dev0-cp314-cp314-linux_x86_64.whl`（约 157MB，含 libtvm.so 72.8MB + libLLVM.so.22.1 186.4MB）
- 镜像体系：dev（构建）→ runtime（运行时）→ serve（API 服务）三层
- chaos/ai 的 `.agents/docs/` 当前仅有 task-summary 文档，新增本教程可丰富 AI 知识库

## Functional Requirements
- **FR-1**: 教程为综合 Markdown 文档，置于 `external/chaos/ai/.agents/docs/xmnn-whl-build-workflow.md`
- **FR-2**: frontmatter 遵循现有 `.agents/` 规范文档格式（id/title/source/date/tags）
- **FR-3**: 覆盖 Docker 一键构建路径（推荐）：Dockerfile 环境搭建、build-and-test.sh 三阶段流程
- **FR-4**: 覆盖容器内构建 run-build.sh：环境检查、pyproject 补丁、Nuitka 编译 vta/xmnn、python -m build
- **FR-5**: 覆盖本地 invoke 构建路径：tasks.py 的 build-all / build-tvm / nuitka-tvm / nuitka-vta / nuitka-xmnn / build-wheel / verify
- **FR-6**: 覆盖 wheel 验证标准：verify-wheel.sh 9 项测试 + auditwheel show + 依赖解析（19 个 Requires-Dist）
- **FR-7**: 覆盖 CMake 打包原理：_libs 目录打包、install_real_lib + patchelf RPATH、数据目录安装、bootstrap 注入
- **FR-8**: 覆盖 AST 兼容层（Python 3.14 Monkey-patch）机制：_xmnn_bootstrap.py / xmnn_bootstrap.pth / PREAMBLE 注入
- **FR-9**: 提供常见问题排查表（Conda 超时、pip --user、--no-isolation、entrypoint su、LLVM 版本冲突等）
- **FR-10**: 与 chaos/ai 既有规则（build.md/mount.md/verify.md）及 docs/ 文档建立交叉引用

## Non-Functional Requirements
- **NFR-1**: 所有内容使用标准现代汉语书面语，专业术语（Nuitka/scikit-build-core/RPATH/PREAMBLE 等）首次出现给出解释
- **NFR-2**: 代码示例（Docker 命令、构建脚本、CMake 片段）完整可复制，标注预期输出或"需验证"
- **NFR-3**: 版本提示明确（xmnn 持续演进，命令/路径可能变化，以 xmtools 源码为准）
- **NFR-4**: 交叉链接使用相对路径，禁止 `file:///` 绝对路径
- **NFR-5**: 不虚构未验证信息；所有命令/路径有 xmtools 源码依据，或明确标注为"需验证"
- **NFR-6**: 文档结构与现有 `.agents/rules/` 规范文档风格一致（标题层级、表格、代码块）

## Constraints
- **Technical**: 输出为单个 Markdown 文件 + YAML frontmatter，无额外依赖
- **Business**: 基于 xmtools 本地源码整理，不虚构；命令与路径有据可查
- **Dependencies**:
  - 资料来源：`external/chaos/xmtools/`（README.md、Dockerfile、build-and-test.sh、run-build.sh、verify-wheel.sh、tasks.py、pyproject.toml、CMakeLists.txt、_xmnn_bootstrap.py、xmnn_bootstrap.pth、AGENTS.md）
  - 输出路径：`external/chaos/ai/.agents/docs/xmnn-whl-build-workflow.md`

## Assumptions
- 输出目录归类在 chaos/ai `.agents/docs/` 下是合理的（用户明确指定"AI 规范区"）
- 综合单文件教程（而非多文件 wiki）适合该主题——构建流程有强顺序依赖，单文件便于通读
- 教程聚焦"如何从零构建打包 xmnn wheel"，chaos/ai 镜像构建已由既有 spec/规则覆盖，不重复
- 本任务是"学习/知识沉淀"类产出（knowledge-scenario），非源码改动
- xmtools 源码是唯一权威依据，构建命令/路径以其为准

## Acceptance Criteria

### AC-1: 文档位置与命名合规
- **Given**: 教程创建完成
- **When**: 检查 chaos/ai/.agents/docs/
- **Then**: 存在 `xmnn-whl-build-workflow.md` 文件，命名符合 kebab-case
- **Verification**: `programmatic`

### AC-2: Frontmatter 格式合规
- **Given**: 文档文件
- **When**: 检查 frontmatter
- **Then**: 包含 id/title/source/date/tags 字段，格式为 YAML
- **Verification**: `programmatic`

### AC-3: Docker 一键构建路径覆盖完整
- **Given**: 教程 Docker 章节
- **When**: 阅读
- **Then**: 覆盖 Dockerfile 环境搭建（ubuntu 26.04 + Miniconda + LLVM22 + 国内镜像）、build-and-test.sh 三阶段（构建镜像→打包 wheel→验证）、三种模式（--verify-only/--no-build/--shell）
- **Verification**: `human-judgment`

### AC-4: 容器内构建 run-build.sh 覆盖完整
- **Given**: 教程 run-build.sh 章节
- **When**: 阅读
- **Then**: 覆盖环境检查、pyproject.toml 系统 cmake/ninja 补丁、Nuitka 编译 vta/xmnn 的 PREAMBLE 注入、python -m build --no-isolation 与 cmake.define 参数
- **Verification**: `human-judgment`

### AC-5: 本地 invoke 构建路径覆盖完整
- **Given**: 教程 invoke 章节
- **When**: 阅读
- **Then**: 覆盖 inv build-all / build-tvm / nuitka-tvm / nuitka-vta / nuitka-xmnn / build-wheel / verify / clean / check-deps
- **Verification**: `human-judgment`

### AC-6: wheel 验证标准覆盖完整
- **Given**: 教程验证章节
- **When**: 阅读
- **Then**: 覆盖 verify-wheel.sh 9 项测试（import tvm/vta/xmnn、_libs、libtvm.so 加载、tvm.build(llvm)、relay/std、.pth、数据目录）、auditwheel、依赖解析
- **Verification**: `human-judgment`

### AC-7: CMake 打包原理覆盖完整
- **Given**: 教程 CMake 章节
- **When**: 阅读
- **Then**: 覆盖 _libs 目录打包、install_real_lib 符号链接、patchelf RPATH $ORIGIN、数据目录安装（autolibs/tools_cpp/fonts、vta_hw/config、relay/std）、tools_cpp chmod +x
- **Verification**: `human-judgment`

### AC-8: AST 兼容层与 bootstrap 机制覆盖完整
- **Given**: 教程 bootstrap 章节
- **When**: 阅读
- **Then**: 覆盖 _xmnn_bootstrap.py 的 AST Monkey-patch（NameConstant/Num/Str/Bytes/Index/ExtSlice）、xmnn_bootstrap.pth、PREAMBLE 注入与还原机制、TVM_LIBRARY_PATH 设置
- **Verification**: `human-judgment`

### AC-9: 常见问题排查表覆盖
- **Given**: 教程 FAQ 章节
- **When**: 检查
- **Then**: 覆盖 Conda 超时、pip --user 报错、--no-isolation、entrypoint su、LLVM 版本冲突、Python 3.14 AST、运行时镜像 ENTRYPOINT 等
- **Verification**: `programmatic`

### AC-10: 交叉引用与索引有效
- **Given**: 文档
- **When**: 检查链接
- **Then**: 与 chaos/ai 既有规则（build/mount/verify）及 xmtools 源码的相对链接指向存在文件，无断链
- **Verification**: `programmatic`

## Open Questions
- [ ] 是否需要在教程中补充 xmnn 推理服务（REST API）章节？（默认不覆盖，仅交叉引用 xmtools README）
- [ ] 是否需要在 chaos/ai `.agents/README.md` 中登记该文档入口？（视现有 README 结构而定）

## Impact
- **Affected specs**: 无既有 spec 冲突；与 `chaos-ai-npu-devcontainer` spec（镜像构建）互补
- **Affected code**: 无源代码变更；仅新增一篇 AI 规范文档
- **Affected docs**: `external/chaos/ai/.agents/docs/xmnn-whl-build-workflow.md`（新建）
