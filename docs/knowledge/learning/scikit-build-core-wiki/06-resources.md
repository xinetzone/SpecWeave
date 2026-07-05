---
title: "参考资料与扩展阅读"
source: "spec:create-scikit-build-core-wiki-tutorial"
date: 2026-07-04
tags: [scikit-build-core, resources, glossary, references, ecosystem]
category: "learning"
status: "stable"
author: "SpecWeave"
summary: "汇总 scikit-build-core 官方资源、教程资料、术语表与扩展阅读路径，含生态项目与进阶学习建议"
---

# 参考资料与扩展阅读

本章汇总 scikit-build-core 的官方资源、教程资料、术语表与扩展阅读路径，是读者继续深入探索的索引。本章也是本 Wiki 教程的最后一章，建议结合 [05 - 常见问题与最佳实践](05-faq-and-best-practices.md) 一起作为日常查阅参考。

## 官方资源

### 官方文档

scikit-build-core 的官方文档托管在 readthedocs，是配置项、CLI、API 的唯一权威来源。

| 板块 | 链接 | 内容要点 |
|---|---|---|
| 首页 | <https://scikit-build-core.readthedocs.io/en/latest/> | 特性列表、最小示例、配置速览、同类后端对比 |
| Getting started | <https://scikit-build-core.readthedocs.io/en/latest/guide/getting_started.html> | 8 种语言绑定后端示例、快速启动渠道 |
| CMakeLists 指南 | <https://scikit-build-core.readthedocs.io/en/latest/guide/cmakelists.html> | `${SKBUILD_*}` 变量、FindPython 写法、安装目录 |
| Dynamic linking | <https://scikit-build-core.readthedocs.io/en/latest/guide/dynamic_link.html> | 动态库链接与打包 |
| Cross-compiling | <https://scikit-build-core.readthedocs.io/en/latest/guide/crosscompile.html> | macOS/Windows/WebAssembly 交叉编译 |
| Migration guide | <https://scikit-build-core.readthedocs.io/en/latest/guide/migration_guide.html> | 从 classic scikit-build 迁移 |
| Build procedure | <https://scikit-build-core.readthedocs.io/en/latest/guide/build.html> | SDist/Wheel 构建流程 |
| FAQs | <https://scikit-build-core.readthedocs.io/en/latest/guide/faqs.html> | 高频问题官方解答 |
| Configuration | <https://scikit-build-core.readthedocs.io/en/latest/configuration/index.html> | 配置项总览 |
| Overrides | <https://scikit-build-core.readthedocs.io/en/latest/configuration/overrides.html> | 条件覆盖系统 |
| Dynamic metadata | <https://scikit-build-core.readthedocs.io/en/latest/configuration/dynamic.html> | 动态元数据 provider |
| Schema | <https://scikit-build-core.readthedocs.io/en/latest/schema.html> | JSON Schema |
| Config Reference | <https://scikit-build-core.readthedocs.io/en/latest/reference/configs.html> | 配置项逐项参考 |
| CLI Reference | <https://scikit-build-core.readthedocs.io/en/latest/reference/cli.html> | `scikit-build` 命令行 |
| Plugins: setuptools | <https://scikit-build-core.readthedocs.io/en/latest/plugins/setuptools.html> | setuptools 兼容层 |
| Plugins: hatchling | <https://scikit-build-core.readthedocs.io/en/latest/plugins/hatchling.html> | hatchling 插件 |
| Projects | <https://scikit-build-core.readthedocs.io/en/latest/about/projects.html> | 使用 scikit-build-core 的项目列表 |

### 源码仓库

- **GitHub 主仓库**：<https://github.com/scikit-build/scikit-build-core>
- **本地克隆位置**：`external/tools/scikit-build-core/`（本 Wiki 教程所有源码锚点均相对此路径）
- **示例项目仓库**：<https://github.com/scikit-build/scikit-build-sample-projects>（含 free-threading 与 8 种后端综合示例）
- **pybind11 示例**：<https://github.com/pybind/scikit_build_example>
- **nanobind 示例**：<https://github.com/wjakob/nanobind_example>

### Changelog 与版本

- **Changelog**：<https://scikit-build-core.readthedocs.io/en/latest/about/changelog.html>
- **当前稳定版**：0.12.2
- **本 Wiki 引用源码版本**：v0.12.2-164-g4f0a4b6

近期重要版本变更要点：

| 版本 | 重要变更 |
|---|---|
| 0.12.x | 新增 `sdist.inclusion-mode`（`default`/`classic`/`manual`）；改进交叉编译；支持 fancy-pypi-readme 25.1；强制规范化 SDist 名 |
| 0.11.x | 新增 `build.requires` 动态注入；新增 `metadata.template` provider；改进 fancy-pypi-readme 版本号支持 |
| 0.10.x | `cmake.minimum-version`/`ninja.minimum-version` 重命名为 `cmake.version`/`ninja.version`（完整 specifier set）；`cmake.verbose`/`cmake.targets` 重命名为 `build.verbose`/`build.targets`；`wheel.packages` 支持 table 形式；新增 `from-sdist`/`system-cmake`/`cmake-wheel`/`failed` override 条件；`minimum-version` 支持 `"build-system.requires"` |

## 教程资源

### 中文资源

- **daobook pygallery**：<https://daobook.github.io/pygallery/study/fields/scikit-build-core/index.html>
  - 作者：xinetzone
  - 内容定位：官方首页的中文翻译，提供"是什么 + 最小示例 + 配置字段速览 + 同类对比"概述级介绍
  - 术语本地化：`wheel` 译为"轮子"，`SDist` 保留原文，`Stable ABI` 译为"稳定 ABI"，`free-threaded` 译为"自由线程"
  - 注意事项：内容存在时滞（落后 1-2 个版本）；仅翻译首页，未覆盖 Guide/Configuration/Plugins/API 等深度文档；`minimum-version = "0.11"` 在站点中标注为 "current version"，而官方已到 0.12.2
  - 生态关联：与 cibuildwheel、Conan、pybind11、CMake、Ninja 教程同站，形成工具链视角
- **CSDN 博客**：基础介绍性文章，注意部分内容混淆了 classic scikit-build（setup.py 风格）与 scikit-build-core（pyproject.toml 风格），参考需谨慎

### 英文资源

- **SciPy 2024 论文**：<https://doi.org/10.25080/FMKR8387>
  - 标题：*Scikit-build-core: A modern build-backend for CPython C/C++/Fortran/Cython extensions*
  - 作者：Henry Schreiner 等人
  - 内容：涵盖 Python 打包历史、scikit-build-core 设计动机与内部实现、采用案例
  - 价值：是深入了解"为什么这样设计"与内部架构的权威资料，补足官方文档未详述的设计原理
- **pydevtools.com 实战教程**：使用 uv + scikit-build-core + pybind11 构建 C++ 扩展的端到端示例，含完整 `pyproject.toml` 与 `CMakeLists.txt`，补足"从零到可用"的实战流程
- **pybind11 官方文档**：<https://pybind11.readthedocs.io/>，推荐 scikit-build-core 作为构建后端
- **nanobind 官方文档**：<https://nanobind.readthedocs.io/>，给出推荐配置 `minimum-version="0.4"`、`build-dir="build/{wheel_tag}"`、`wheel.py-api="cp312"`

## 同类工具对比

下表汇总主流 Python 二进制构建后端，帮助读者按场景选型。

| 工具 | 构建系统 | PEP 517 | CMake 集成 | 跨平台 wheel | 可编辑安装 | 学习曲线 | 社区活跃度 |
|---|---|---|---|---|---|---|---|
| **scikit-build-core** | CMake | 原生 | 原生（三层抽象） | 支持 | 支持（redirect/inplace） | 中 | 高 |
| classic scikit-build | CMake | 通过 setuptools | 原生 | 支持 | 不支持 | 中 | 维护模式 |
| meson-python | Meson | 原生 | 无 | 支持 | 支持 | 中 | 高 |
| maturin | Cargo（Rust） | 原生 | 无 | 支持 | 支持 | 低 | 高 |
| py-build-cmake | CMake | 原生 | 原生 | 支持 | 部分 | 低 | 中 |
| cmeel | CMake | 原生 | 原生 | 支持 | 不支持 | 中 | 低 |
| enscons | SCons | 原生 | 无 | 支持 | 不支持 | 中 | 低 |
| setuptools | distutils/setuptools | 原生 | 无 | 支持 | 支持 | 低 | 高 |

**选型建议**：

- 项目已用 CMake 或需多语言绑定（C/C++/Fortran/Cython/SWIG/pybind11/nanobind）→ **scikit-build-core**
- 项目使用 Meson 构建系统 → meson-python
- Rust 扩展或 PyO3 绑定 → maturin
- 纯 Python 项目 → hatchling / flit / setuptools
- 需要轻量 CMake 集成且无 PEP 660 需求 → py-build-cmake

## 术语表（Glossary）

按字母顺序排列，覆盖 scikit-build-core 生态的核心术语。

| 术语 | 释义 |
|---|---|
| **ABI3（Stable ABI）** | Python 稳定 ABI（PEP 384），一个 wheel 可支持多 Python 版本。scikit-build-core 通过 `wheel.py-api = "cp38"` 与 CMake `Development.SABIModule` 启用 |
| **ABI3t（free-threaded Stable ABI）** | 自由线程 Python 3.13+ 的 Stable ABI（PEP 703/793），通过 `wheel.py-api = "cp315.cp315t"` 启用 |
| **auditwheel** | Linux wheel 修复工具，将 `linux_*` 标签转为 manylinux/musllinux，使 wheel 可上传 PyPI |
| **CMake** | 跨平台构建系统生成器，scikit-build-core 的底层构建引擎 |
| **cibuildwheel** | 跨平台 wheel 构建自动化工具，在 CI 中一站式产出 Linux/macOS/Windows wheel |
| **config-settings** | PEP 517 配置传递机制，扁平点号键（如 `-Cskbuild.logging.level=INFO`），优先级介于环境变量与 TOML 之间 |
| **delocate** | macOS wheel 修复工具，处理动态库依赖与跨架构（universal2） |
| **delvewheel** | Windows wheel 修复工具，处理 DLL 依赖 |
| **dynamic metadata** | PEP 621 中标记为 `dynamic` 的字段，由 provider 在构建时填充。scikit-build-core 内置 `regex`/`template`/`setuptools_scm`/`fancy_pypi_readme` 四个 provider |
| **editable install** | PEP 660 可编辑安装，`pip install -e .`。scikit-build-core 支持 `redirect`（默认，含 rebuild-on-import）与 `inplace` 两种模式 |
| **File API** | CMake 文件 API（CMake 3.14+），scikit-build-core 通过 `file_api/query.py` 写 stateless query、`file_api/reply.py` 解析响应，用于 wheel 文件结构推断与 stale cache 检测 |
| **FindPython** | CMake 内置模块（`find_package(Python ...)`），scikit-build-core 推荐仅请求 `Interpreter Development.Module`，manylinux 缺 libpython 故禁止请求 `Development.Embed` |
| **manylinux / musllinux** | Linux wheel 兼容性规范（PEP 513/571/599/656），定义 glibc/musl 最低版本与允许的符号集 |
| **minimum-version** | scikit-build-core 向后兼容门，建议设为 `"build-system.requires"` 自动同步 |
| **Ninja** | 高性能构建系统，scikit-build-core 默认 generator（优先级 Ninja > Make > MSVC） |
| **PEP 517** | Python 构建后端标准，定义 `build_wheel`/`build_sdist`/`get_requires_for_build_*`/`prepare_metadata_for_build_*` 等钩子 |
| **PEP 660** | 可编辑安装支持，新增 `build_editable`/`get_requires_for_build_editable`/`prepare_metadata_for_build_editable` 钩子 |
| **PEP 621** | 项目元数据标准，定义 `pyproject.toml` 的 `[project]` 表 |
| **PEP 817** | wheel 变体（实验性），scikit-build-core 通过 `variant`/`variant_name`/`variant_label`/`null_variant` 支持，需 `experimental=true` |
| **pyproject.toml** | Python 项目配置文件标准（PEP 518），scikit-build-core 配置位于 `[tool.scikit-build]` 表 |
| **SDist** | 源码分发（Source Distribution），`tar.gz` 格式，由 `build_sdist` 钩子产出 |
| **SOABI** | 共享对象 ABI 标签，标识 Python 扩展模块的二进制兼容性。交叉编译时应使用 `${SKBUILD_SOABI}` 而非 `Python_SOABI` |
| **Wheel** | 二进制分发格式（PEP 427），文件名五段：`name-version-pythontag-abitag-platformtag` |

## 生态工具

scikit-build-core 与以下生态工具协同工作，构成完整的 Python 扩展模块构建与分发工具链。

| 工具 | 类别 | 用途 |
|---|---|---|
| **pybind11** | 语言绑定 | C++ 与 Python 桥接库，scikit-build-core 内置脚手架模板 |
| **nanobind** | 语言绑定 | pybind11 的轻量继任者，推荐配置 `minimum-version="0.4"`、`wheel.py-api="cp312"` |
| **Cython** | 语言绑定 | Python 超集编译器，需配合 `cython-cmake` CMake 包 |
| **SWIG** | 语言绑定 | 多语言绑定生成器 |
| **f2py-cmake** | 语言绑定 | Fortran 扩展（f2py）的 CMake 包装 |
| **pydevtools** | 开发工具 | scikit-build-core 等工具的命令行包装与诊断 |
| **hatchling** | 构建后端 | scikit-build-core 提供 `hatch.scikit-build` 插件入口点（实验性） |
| **setuptools-scm** | 版本管理 | 从 git tag 读版本，scikit-build-core 内置 `metadata.setuptools_scm` provider |
| **hatch-fancy-pypi-readme** | README 渲染 | 复杂 README 渲染，scikit-build-core 内置 `metadata.fancy_pypi_readme` provider |
| **cibuildwheel** | CI 集成 | 跨平台 wheel 一站式构建 |
| **auditwheel / delocate / delvewheel / repairwheel** | wheel 修复 | 平台 wheel 修复工具，将 `linux_*` 标签转为 manylinux/musllinux 等 |
| **uv** | 包管理 | 推荐通过 `uv init --lib --build-backend=scikit` 与 `uv build` 快速启动 |
| **build** | 构建前端 | PEP 517 构建前端，`python -m build` 是标准构建方式 |
| **validate-pyproject** | 配置校验 | 校验 `pyproject.toml`，scikit-build-core 注册了 `tool_schema.scikit-build` 入口点 |

## 关联本项目知识库条目

本 Wiki 教程与 SpecWeave 项目其他知识库条目存在主题关联，建议结合阅读。

- [interface-api-abi-protocol-wiki](../interface-api-abi-protocol-wiki/00-overview.md)：构建工具链 ABI 层。本 Wiki 的 Stable ABI/ABI3/SOABI 等概念与该 Wiki 的 ABI 协议层直接相关，理解 ABI 协议有助于编写正确的 CMakeLists.txt 与选择 `wheel.py-api`
- [karpathy-llm-coding-guidelines](../karpathy-llm-coding-guidelines-tutorial.md)：Python 工程实践。该教程的代码风格、项目组织与测试实践建议适用于 scikit-build-core 项目的 CMake 与 Python 协同开发
- [ffi-wiki](../ffi-wiki/00-overview.md)：FFI 跨语言调用。scikit-build-core 构建的扩展模块属于 FFI 范畴，该 Wiki 详解 FFI 设计模式与 ABI 兼容性
- [idl-wiki](../idl-wiki/00-overview.md)：接口定义语言。Python 扩展模块的接口设计与 IDL 设计有共通之处

## 扩展阅读建议

### 方向 1：Python 打包生态

深入理解 PEP 标准与打包生态，有助于正确使用 scikit-build-core。

- **PEP 标准**：
  - PEP 517（构建后端）/ PEP 518（pyproject.toml）/ PEP 621（项目元数据）/ PEP 660（可编辑安装）/ PEP 808（extendable 字段）
- **Python Packaging User Guide**：<https://packaging.python.org/>
- **同类后端文档**：setuptools / hatchling / flit / maturin / meson-python

### 方向 2：CMake 深入

scikit-build-core 的核心是 CMake 集成，深入 CMake 有助于编写高效可维护的 CMakeLists.txt。

- **CMake 官方文档**：<https://cmake.org/documentation/>
- **《Professional CMake: A Practical Guide》**（Craig Scott）
- **《CMake 实践》**（中文）
- **CMake File API 文档**：<https://cmake.org/cmake/help/latest/manual/cmake-file-api.7.html>

### 方向 3：跨平台 wheel 构建

wheel 分发是 scikit-build-core 项目落地的关键环节。

- **cibuildwheel 文档**：<https://cibuildwheel.readthedocs.io/>
- **manylinux 规范**：PEP 513/571/599
- **musllinux 规范**：PEP 656
- **repairwheel**：统一 wheel 修复工具

### 方向 4：Python 扩展模块开发

scikit-build-core 支持多种语言绑定后端，按需深入学习。

- **pybind11 文档**：<https://pybind11.readthedocs.io/>
- **nanobind 文档**：<https://nanobind.readthedocs.io/>
- **Cython 文档**：<https://cython.readthedocs.io/>
- **Python C API 文档**：<https://docs.python.org/3/c-api/>
- **Stable ABI 文档**：<https://docs.python.org/3/c-api/stable.html>

### 方向 5：scikit-build-core 内部架构

如需深入理解 scikit-build-core 的设计与实现，参考以下资料。

- **SciPy 2024 论文**：<https://doi.org/10.25080/FMKR8387>（设计动机与内部架构）
- **本 Wiki 第二章**：[02 - 项目目录结构：源码模块树解析](02-project-structure.md)
- **本 Wiki 第一章**：[01 - 概念与架构：PEP 517 构建后端与 CMake 集成](01-concepts-architecture.md)
- **本地源码**：`external/tools/scikit-build-core/src/scikit_build_core/`

## 结语

scikit-build-core 的核心价值在于：**现代 PEP 517 构建后端 + 原生 CMake 集成 + 多语言绑定支持**。它是目前唯一同时具备这三项特性的 Python 打包后端，适合需要将 C/C++/Fortran/Cython/SWIG/pybind11/nanobind 代码集成到 Python 的项目。

鼓励读者在以下方向参与社区贡献：

- **报告问题与提交 PR**：<https://github.com/scikit-build/scikit-build-core/issues>
- **补充示例项目**：<https://github.com/scikit-build/scikit-build-sample-projects>
- **改进文档**：官方文档源码位于 `external/tools/scikit-build-core/docs/`
- **分享采用案例**：通过 `about/projects.html` 页面提交使用 scikit-build-core 的项目

本 Wiki 教程基于源码研究（v0.12.2-164-g4f0a4b6）+ 官方文档（0.12.2）+ SciPy 2024 论文 + daobook 中文教程编写，关联 spec：`create-scikit-build-core-wiki-tutorial`。

---

← 上一章：[常见问题与最佳实践](05-faq-and-best-practices.md) | [返回目录](00-overview.md) | 下一章：无 →
