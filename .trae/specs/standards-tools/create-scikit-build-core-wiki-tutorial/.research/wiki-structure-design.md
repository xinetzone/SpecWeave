---
title: "scikit-build-core Wiki 章节结构设计契约"
source: "spec:create-scikit-build-core-wiki-tutorial"
x-toml-ref: "../../../../../.meta/toml/.trae/specs/standards-tools/create-scikit-build-core-wiki-tutorial/.research/wiki-structure-design.toml"
date: 2026-07-04
tags: [scikit-build-core, wiki, design, contract, structure]
status: "draft"
author: "SpecWeave"
summary: "Task 4 产出物：7 个 Wiki 章节文件的详细大纲、导航关系、文档规范契约，供 Task 5-11 章节编写参考"
---
# scikit-build-core Wiki 章节结构设计契约

> 本文档是 Task 4 产出物，作为 Task 5-11（章节编写）的契约依据。
> 章节编写者必须严格遵循此处定义的文件清单、章节大纲、导航链接格式与文档规范契约。
> 任何偏离须先更新本设计文档再编写章节，避免返工。

## 设计依据

本设计基于以下两份研究摘要：

- **源码研究摘要**：`source-code-analysis.md`（27KB，含 PEP 517 钩子入口表、配置系统四层架构、CMake 三层抽象、file-api 状态机、8 步 wheel 构建流程、16 项目录结构要点、模块树总览）
- **在线文档研究摘要**：`online-docs-summary.md`（264 行，含官方文档 9 页要点、daobook 教程分析、7 层 25 主题建议、三方互补关系）

设计目标：

1. 覆盖 spec 要求的 5 大核心内容（基本概念与架构、目录结构、核心 API 示例、常见问题最佳实践、入门到进阶指南）
2. 落地 Task 2 源码研究发现（PEP 517 钩子、配置四层、CMake 三层、file-api）
3. 落地 Task 3 文档研究发现（官方文档指南、配置项、故障排查、迁移指南）
4. 形成可追溯的源码锚点体系（每个关键论断可回溯到 `external/tools/scikit-build-core/src/scikit_build_core/` 下具体文件行号）

## 目标目录

所有 Wiki 文档统一存放于：

```
docs/knowledge/learning/scikit-build-core-wiki/
├── 00-overview.md
├── 01-concepts-architecture.md
├── 02-project-structure.md
├── 03-core-api-and-config.md
├── 04-quickstart-to-advanced.md
├── 05-faq-and-best-practices.md
└── 06-resources.md
```

并在 `docs/knowledge/learning/` 下生成入口索引 `scikit-build-core-wiki.md`（由 docgen 自动维护），指向 `00-overview.md`。

---

## 文件清单

| 序号 | 文件名 | 一句话职责 | 预估字数 |
|---|---|---|---|
| 00 | `00-overview.md` | 概述与导航枢纽：定位、对比、阅读路径、目录导航表 | ~3000 字 |
| 01 | `01-concepts-architecture.md` | 概念与架构：PEP 517/660、CMake 集成、wheel 构建流程、配置四层、file-api 状态机（含 5 张 Mermaid 图） | ~6500 字 |
| 02 | `02-project-structure.md` | 项目目录结构：基于源码 16 项要点，逐模块解析职责与源码锚点 | ~6000 字 |
| 03 | `03-core-api-and-config.md` | 核心 API 与配置：8 个 PEP 517 钩子、配置项全集、CMakeLists.txt 示例 | ~6500 字 |
| 04 | `04-quickstart-to-advanced.md` | 入门到进阶：三级递进路径（最小 CMake → 真实 C++ 扩展 → 高级配置），每级验收标准 | ~7000 字 |
| 05 | `05-faq-and-best-practices.md` | 常见问题与最佳实践：FAQ 主题清单、故障排查流程、CI/Conda/迁移实践 | ~5000 字 |
| 06 | `06-resources.md` | 参考资料与扩展阅读：官方链接、术语表、关联本项目条目 | ~2800 字 |

总计预估约 **36800 字**。

---

## 各章节详细大纲

### 00-overview.md（概述与导航枢纽）

**职责**：作为 Wiki 入口，让读者在 3 分钟内理解 scikit-build-core 是什么、为何存在、如何开始阅读。提供完整目录导航表与三条阅读路径。

**二级标题与要点**：

#### `## 引言：为什么需要 scikit-build-core`

- 痛点切入：Python 扩展模块构建的三大难题（CMake 集成复杂、跨平台 wheel 困难、setup.py 时代终结）
- scikit-build-core 的定位：现代 PEP 517 构建后端，桥接 CMake 与 Python 打包
- 一句话定义：基于 CMake 的 Python 包构建后端，支持 C/C++/Fortran/Cython/SWIG/pybind11/nanobind 等多语言绑定

#### `## 与同类工具的对比`

- 对比表格：scikit-build-core vs classic scikit-build vs setuptools vs meson-python vs maturin vs py-build-cmake vs cmeel vs enscons
- 对比维度：构建系统、PEP 517 支持、CMake 集成、跨平台 wheel、可编辑安装、学习曲线、社区活跃度
- 关键差异点：scikit-build-core 是唯一同时具备"原生 CMake 集成 + 完整 PEP 517 + 多语言绑定支持"的后端
- 配图建议：**Mermaid 维恩图**展示三类后端（CMake 系/PEP 517 系/多语言绑定系）的覆盖关系

#### `## 核心特性速览`

- 7 个核心特性列表（PEP 517 原生、CMake 集成、多语言绑定、配置系统四层、可编辑安装、Stable ABI/Free-threaded、实验性变体）
- 每个特性一句话说明 + 跳转到对应章节的链接
- 引用源码版本：v0.12.2（与 `external/tools/scikit-build-core` 同步）

#### `## 目标读者`

- 三类读者画像：Python 扩展模块开发者、科研计算包维护者、企业级 Python 工具链工程师
- 每类读者推荐阅读路径

#### `## 阅读路径指南`

- **路径 A：5 分钟快速上手**（00 → 04 第一级 → 03 最小示例）—— 适合立即开始项目
- **路径 B：深入理解架构**（00 → 01 → 02 → 03）—— 适合需要深度定制的开发者
- **路径 C：故障排查参考**（00 → 05 → 06）—— 适合已遇到问题的开发者
- 每条路径用 Mermaid 流程图展示

#### `## 目录导航`

- 完整目录导航表（Markdown 表格），含 7 个章节、每章二级标题速览、章节预估阅读时间
- 表格格式参照 `interface-api-abi-protocol-wiki/00-overview.md` 的"章节导航"小节

#### `## 版本与溯源`

- 当前源码版本：v0.12.2-164-g4f0a4b6
- 官方文档版本：0.12.2（main 分支 dev 0.12.3.dev149+gf0895076f）
- 源码克隆位置：`external/tools/scikit-build-core/`
- 三方资料来源说明（官方文档 + daobook 教程 + SciPy 2024 论文 + 源码研究）

#### `## 反馈与改进`

- 反馈渠道说明（issue、PR、文档改进流程）
- 关联 spec：`create-scikit-build-core-wiki-tutorial`

**章节末尾导航**：

```markdown
---
**下一章**：[01 - 概念与架构：PEP 517 构建后端与 CMake 集成](01-concepts-architecture.md)
```

---

### 01-concepts-architecture.md（概念与架构）

**职责**：系统讲解 scikit-build-core 的核心概念与内部架构，是理解后续章节的理论基础。包含 5 张 Mermaid 图。

**二级/三级标题与要点**：

#### `## PEP 517/660 构建后端机制`

##### `### PEP 517：构建后端标准`

- PEP 517 的核心目标：解耦构建系统与打包工具（pip、build）
- 5 个必备钩子：`build_wheel`、`build_sdist`、`get_requires_for_build_wheel`、`get_requires_for_build_sdist`、`prepare_metadata_for_build_wheel`
- 2 个可选钩子（PEP 660）：`build_editable`、`get_requires_for_build_editable`、`prepare_metadata_for_build_editable`
- 配置传递机制：`config-settings` 字典（扁平点号键，如 `-Cskbuild.logging.level=INFO`）

##### `### scikit-build-core 的后端声明`

- 下游 `pyproject.toml` 写法：`build-backend = "scikit_build_core.build"`
- 钩子从 `src/scikit_build_core/build/__init__.py` 导出
- 源码锚点：`external/tools/scikit-build-core/pyproject.toml#L1-L3`（自身用 hatchling 构建）
- 完整 8 钩子表（详见 03 章）

##### `### PEP 660：可编辑安装支持`

- 可编辑安装的两种模式：redirect（默认）vs inplace
- redirect 模式工作原理：`.pth` 文件 + `_editable_skbc_<pkg>.py` shim + `sys.meta_path` 映射
- rebuild-on-import 机制：`editable.rebuild=true` 时 import 触发 CMake 重建

**Mermaid 图位置 1**：PEP 517 钩子调用时序图（pip/build → `get_requires_for_build_*` → `build_wheel`/`build_sdist`）

#### `## CMake 集成机制`

##### `### 三层抽象架构`

- **第一层：`CMake` 值对象**（`src/scikit_build_core/cmake.py#L67-L99`）：frozen dataclass，持有版本与路径，`default_search` 在系统路径与 PyPI 包中查找
- **第二层：`CMaker` 重量级构建器**（`src/scikit_build_core/cmake.py#L102`）：管理构建目录生命周期，封装 `configure`/`build`/`install`
- **第三层：`Builder` 高层包装**（`src/scikit_build_core/builder/builder.py#L213`）：被 `build/wheel.py` 使用，注入 Python 发现变量、Stable ABI、macOS 跨编译

##### `### Generator 选择策略`

- `parse_generator`（`builder/generator.py#L39`）：从 CMake args 提取 `-G` 指定 generator
- 默认 generator 优先级：Ninja > Make > MSVC
- `set_environment_for_gen`：为 generator 设置环境变量

##### `### 程序查找`

- `Program` NamedTuple（`program_search.py#L39-L46`）
- `get_cmake_programs`/`get_ninja_programs`/`get_make_programs`：从 PATH 与 PyPI 安装位置枚举
- `best_program`：按 PEP 440 specifier 选择最佳
- macOS 特殊处理：`_macos_binary_is_x86`（`program_search.py#L57`）

**Mermaid 图位置 2**：CMake 集成三层调用图（Builder → CMaker → CMake 子进程）

#### `## Wheel 构建流程（8 步详解）`

- 完整调用链：`build_wheel` → `_build_wheel_impl` → `_build_wheel_impl_impl`
- 8 步详解（每步含源码锚点）：
  1. `SettingsReader.from_file`（`settings/skbuild_read_settings.py#L61`）—— 读取并合并配置
  2. `get_standard_metadata`（`build/metadata.py#L53`）—— 解析 PEP 621 元数据
  3. `CMake.default_search`（`cmake.py#L71`）—— 查找 CMake
  4. `Builder.configure`（`builder/builder.py#L257`）—— 写 file-api query + 运行 `cmake -S -B`
  5. `Builder.build`（`builder/builder.py#L488`）—— 运行 `cmake --build`
  6. `Builder.install`（`builder/builder.py#L502`）—— 运行 `cmake --install` 到 staging
  7. 打包 Python 文件（`build/_pathutil.py`、`build/_file_processor.py`）
  8. `WheelWriter`（`build/_wheelfile.py`）—— 写 .whl + 计算 tag（`builder/wheel_tag.py`）

**Mermaid 图位置 3**：8 步 wheel 构建流程图（含源码文件标注）

#### `## 配置系统四层架构`

##### `### 第一层：数据模型（settings/skbuild_model.py）`

- 主数据类 `ScikitBuildSettings`（`skbuild_model.py#L815-L933+`）聚合 11 个子节
- 11 个子节速览：`cmake`/`search`/`ninja`/`logging`/`sdist`/`wheel`/`backport`/`editable`/`build`/`install`/`generate`/`messages`/`metadata`/`env`
- 顶级字段：`strict_config`/`experimental`/`minimum_version`/`build_dir`/`fail`/`variant*`

##### `### 第二层：源链（settings/sources.py）`

- 三个 Source：`EnvSource`（环境变量）/`ConfSource`（config-settings）/`TOMLSource`（pyproject.toml）
- `SourceChain` 按顺序查询，dict 跨源合并而非替换
- 优先级：env > config-settings > TOML

##### `### 第三层：编排器（settings/skbuild_read_settings.py）`

- `SettingsReader` 处理步骤：合并三源 → 应用 overrides → 版本兼容改写 → 自动 CMake 版本检测 → 自动依赖检测 → 加载入口点配置提供者 → 校验
- 源码锚点：`settings/skbuild_read_settings.py#L61`

##### `### 第四层：JSON Schema（settings/skbuild_schema.py）`

- `generate_skbuild_schema`（`skbuild_schema.py#L41`）：从数据类生成完整 schema
- `get_skbuild_schema`（`skbuild_schema.py#L233`）：从打包资源读取已生成 schema
- 生成的 schema 落地于 `resources/scikit-build.schema.json`，由 `nox -t gen` 重新生成

**Mermaid 图位置 4**：配置源链合并示意图（三个 Source → SourceChain → SettingsReader → ScikitBuildSettings）

#### `## CMake File API 状态机`

- `stateless_query`（`file_api/query.py#L19`）：在 `build_dir/.cmake/api/v1/query/` 创建 4 个空文件（`codemodel-v2`、`cache-v2`、`cmakeFiles-v1`、`toolchains-v1`）
- CMake configure 时自动写入 `reply/` 目录响应
- `load_reply_dir`（`file_api/reply.py#L38`）：定位最新 `index-*.json`，通过 `Converter` 类解析
- 6 个 typed dataclass：`Index`/`CodeModel`/`Target`/`Cache`/`CMakeFiles`/`Toolchains`/`Directory`
- 用途：用于 wheel 文件结构推断、stale cache 检测

**Mermaid 图位置 5**：File API query/reply 时序图（CMaker.configure → 写 query → CMake 写 reply → load_reply_dir 解析）

#### `## 元数据插件机制`

- 两种声明形式：legacy `tool.scikit-build.metadata` 表 vs 新式 `[[tool.dynamic-metadata]]`
- 4 个内置 provider：`regex`/`template`/`setuptools_scm`/`fancy_pypi_readme`
- `get_standard_metadata`（`build/metadata.py#L53`）处理流程
- 第三方 provider 需 `experimental=true`

#### `## 可编辑安装原理`

- redirect 模式（默认）：`editable_redirect`（`build/_editable.py#L48`）+ `resources/_editable_redirect.py` 模板
- inplace 模式：简单 `.pth` 指向源码包目录
- rebuild-on-import：import 时触发 CMake 重建（`editable.rebuild=true`）

#### `## 后端适配层（实验性）`

- Hatchling 插件：`ScikitBuildHook`（`hatch/hooks.py#L18`），让 hatchling 驱动 CMake 构建
- Setuptools 兼容层：`BuildCMake` 命令 + `build_meta` 包装 + `setup()` wrapper
- 何时选择原生后端 vs 插件后端

**章节末尾导航**：

```markdown
---
**上一章**：[00 - 概述与导航枢纽](00-overview.md)
**下一章**：[02 - 项目目录结构：源码模块树解析](02-project-structure.md)
**返回目录**：[00 - 概述与导航枢纽](00-overview.md)
```

---

### 02-project-structure.md（项目目录结构）

**职责**：基于源码 16 项要点，逐模块解析 `src/scikit_build_core/` 模块树，每个模块说明标注源码锚点。是开发者阅读源码的导航地图。

**二级标题与要点**：

#### `## 源码总体结构`

- 源码根：`external/tools/scikit-build-core/`
- 关键目录：`src/scikit_build_core/`（核心代码）、`docs/`（官方文档源码）、`tests/`（测试用例）
- 一句话定位：14 个子目录 + 13 个顶层 .py 文件，按"核心/兼容/实验性/vendored"四类性质划分

**Mermaid 图位置 1**：模块依赖关系图（顶层文件 → 子目录）

#### `## 顶层文件职责表（13 个 .py + 类型标记）`

- 完整 13 项表格：文件名 + 一句话职责 + 源码锚点
- 每项锚点格式：`src/scikit_build_core/<file>.py#L<行号>`
- 示例：`__main__.py#L37` —— CLI 入口 `main()`，注册 4 个子命令
- 标注 4 类性质：核心（`cmake.py`、`_shutil.py`、`_logging.py`、`_reproducible.py`）/兼容（`_compat/`）/实验性（`_variants.py`）/vendored（`_vendor/`）

#### `## 子目录职责矩阵（14 个）`

- 14 项表格：目录名 + 一句话职责 + 性质分类（核心/兼容/实验性/vendored）+ 关键文件锚点
- 核心目录（8 个）：`build/`、`builder/`、`settings/`、`file_api/`、`metadata/`、`init/`、`resources/`、`utils/`
- 兼容目录（1 个）：`_compat/`
- 实验性目录（2 个）：`hatch/`、`setuptools/`
- vendored 目录（1 个）：`_vendor/pyproject_metadata/`
- 工具目录（2 个）：`ast/`、`program_search`（实际是顶层文件，须澄清）

#### `## PEP 517 钩子入口表`

- 8 个钩子函数完整表：钩子名 + 行号锚点 + 委托目标 + 调用时机
- 关键源码锚点：`src/scikit_build_core/build/__init__.py#L45-L182`
- `_has_safe_metadata()`（`build/__init__.py#L77-L90`）的禁用机制说明
- 入口点注册表（`pyproject.toml#L81-L98`）：6 类入口点

#### `## 构建流程调用图`

- 8 步构建流程详解（同 01 章，但此章侧重源码文件定位，01 章侧重概念）
- 每步对应文件:行号锚点
- 验收要求：每个步骤必须可点击锚点跳转到源码

#### `## 配置系统四层架构（源码视角）`

##### `### 数据模型层（settings/skbuild_model.py）`

- `ScikitBuildSettings`（`skbuild_model.py#L815-L933+`）11 个子节字段表
- 每个子节标注行号锚点
- `CMakeSettingsDefine`（`skbuild_model.py#L61-L82`）：str 子类型自动归一化
- `EnvValue`（`skbuild_model.py#L85-L120+`）：支持 `{env, default, force}` 表或裸字符串

##### `### 源链层（settings/sources.py）`

- `EnvSource`/`ConfSource`/`TOMLSource`/`SourceChain` 表
- 文件顶部 docstring（`settings/sources.py#L1-L79`）
- 优先级：env > config-settings > TOML

##### `### 编排层（settings/skbuild_read_settings.py）`

- `SettingsReader`（`skbuild_read_settings.py#L61`）处理步骤
- 5 个子调用：`process_overrides`/`_handle_minimum_version`/`find_min_cmake_version`/`get_min_requires`/`load_config_providers`

##### `### Schema 层（settings/skbuild_schema.py）`

- `generate_skbuild_schema`（`skbuild_schema.py#L41`）
- `get_skbuild_schema`（`skbuild_schema.py#L233`）
- 生成的 schema 落地于 `resources/scikit-build.schema.json`

#### `## 条件覆盖（overrides）系统`

- `process_overrides`（`settings/skbuild_overrides.py#L38`）
- 12 种 `if` 选择器（4 类）：版本类/字符串类/布尔类/复合类
- `inherit` 三模式：`none`/`append`/`prepend`
- `override-only` 字段约束
- `failed` 重试机制（0.10+）

#### `## CMake 集成三层抽象（源码视角）`

- 三个类完整方法表：`CMake`/`CMaker`/`Builder`
- 每个方法标注文件:行号锚点
- `CMaker.configure`（`cmake.py#L284`）详解：写 `CMakeInit.txt` + file-api query + 运行 cmake
- `Builder.configure`（`builder.py#L257`）详解：注入 Python 发现变量、Stable ABI、macOS 跨编译

#### `## CMake File API 工作流`

- `stateless_query`（`file_api/query.py#L19`）写 4 个 query 文件
- CMake configure 写 reply
- `load_reply_dir`（`file_api/reply.py#L38`）解析
- 6 个 typed dataclass 表：`Index`/`CodeModel`/`Target`/`Cache`/`CMakeFiles`/`Toolchains`/`Directory`
- CLI 子命令：`scikit-build file-api query/reply`

#### `## 元数据插件机制（源码视角）`

- `get_standard_metadata`（`build/metadata.py#L53`）4 步处理流程
- 4 个内置 provider 表：`regex`/`template`/`setuptools_scm`/`fancy_pypi_readme`
- 字段分类：`_STR_FIELDS`/`_LIST_STR_FIELDS`/`_DICT_STR_FIELDS`/`_LIST_DICT_FIELDS`/`_SCALAR_FIELDS`/`_EXTENDABLE_FIELDS`
- 入口点机制：`dynamic_metadata.provider`

#### `## 可编辑安装两种模式`

- redirect 模式（默认）：`editable_redirect`（`build/_editable.py#L48`）+ `resources/_editable_redirect.py`
- inplace 模式：简单 `.pth`
- 辅助函数：`get_packages`/`package_search_dirs`/`collect_search_locations`/`mapping_to_modules`/`libdir_to_installed`

#### `## 后端适配层`

##### `### Hatchling 插件（hatch/，实验性）`

- `hatch/hooks.py#L18` `hatch_register_build_hook`
- `hatch/plugin.py` `ScikitBuildHook`
- 入口点 `hatch.scikit-build`（`pyproject.toml#L90`）

##### `### Setuptools 兼容层（setuptools/，实验性）`

- `setuptools/build_meta.py#L14-L19`：重导出 setuptools 钩子
- `setuptools/build_cmake.py`：`BuildCMake` 命令 + 6 个 setup() 关键字
- `setuptools/wrapper.py#L25` `setup()`：兼容旧 scikit-build 项目

#### `## Init 脚手架（init/__main__.py）`

- `generate_project`（`init/__main__.py#L28`）
- 8 种后端模板表：`pybind11`/`nanobind`/`c`/`cython`/`swig`/`fortran`/`abi3`/`abi3t`
- 每个后端的依赖与 `py-api` 配置

#### `## CLI 子命令树`

- `scikit-build` 4 个子命令完整功能表
- 源码锚点：`src/scikit_build_core/__main__.py#L37-L82`
- 子命令：`build`/`builder`/`file-api`/`init`
- 8 个具体子命令（如 `build requires`、`build project-table`、`builder wheel-tag`、`builder sysconfig`）

#### `## 兼容性与 vendored 目录`

- `_compat/` 5 个垫片：`tomllib`/`typing`/`importlib`/`setuptools.errors`/`builtins`
- Ruff 强制规则：禁止直接 import 标准库对应模块
- `_vendor/pyproject_metadata/`：禁止 lint 或手改

#### `## 实验性特性`

- PEP 817 variants：`variant`/`variant_name`/`variant_label`/`null_variant`（override-only）
- `experimental` 字段控制开关
- 第三方动态元数据 provider 接口稳定性警告

#### `## 生成文件清单`

- `resources/scikit-build.schema.json`：由 `nox -t gen` 从 `skbuild_model.py` 重新生成
- `README.md` cog 段：配置项文档
- `docs/reference/configs.md` cog 段：配置参考文档
- 修改 model 后必须运行 `nox -t gen`

**章节末尾导航**：

```markdown
---
**上一章**：[01 - 概念与架构：PEP 517 构建后端与 CMake 集成](01-concepts-architecture.md)
**下一章**：[03 - 核心 API 与配置：钩子、配置项与 CMakeLists.txt 示例](03-core-api-and-config.md)
**返回目录**：[00 - 概述与导航枢纽](00-overview.md)
```

---

### 03-core-api-and-config.md（核心 API 与配置）

**职责**：覆盖 8 个 PEP 517 钩子、`[tool.scikit-build]` 全部配置项、CMakeLists.txt 集成示例。每个示例含可复制最小代码块。

**二级/三级标题与要点**：

#### `## PEP 517 钩子详解`

##### `### build_wheel 钩子`

- 签名：`build_wheel(wheel_directory, config_settings=None, metadata_directory=None)`
- 源码锚点：`src/scikit_build_core/build/__init__.py#L45-L58`
- 委托链：`_build_wheel_impl(..., editable=False)` → `_build_wheel_impl_impl`
- 调用时机：`pip install`、`python -m build --wheel`
- 最小调用示例：

```python
from scikit_build_core.build import build_wheel
build_wheel("dist/")
```

##### `### build_editable 钩子（PEP 660）`

- 签名：`build_editable(wheel_directory, config_settings=None, metadata_directory=None)`
- 源码锚点：`build/__init__.py#L61-L74`
- 委托链：`_build_wheel_impl(..., editable=True)`
- 两种模式：redirect（默认）/ inplace
- 最小调用示例：

```python
from scikit_build_core.build import build_editable
build_editable("dist/")
```

##### `### prepare_metadata_for_build_wheel / build_editable`

- 源码锚点：`build/__init__.py#L95-L116`
- `_has_safe_metadata()`（`build/__init__.py#L77-L90`）的禁用机制
- 当存在 `if.failed` override 时禁用 `prepare_metadata_*`，避免 metadata 阶段失败导致后续 retry 失效

##### `### build_sdist 钩子`

- 签名：`build_sdist(sdist_directory, config_settings=None)`
- 源码锚点：`build/__init__.py#L124-L131`
- 委托目标：`build.sdist.build_sdist`（`build/sdist.py#L129`）
- 默认 `sdist.cmake=false`，跳过 CMake

##### `### get_requires_for_build_* 钩子（4 个）`

- 4 个钩子完整表：`get_requires_for_build_sdist`/`get_requires_for_build_wheel`/`get_requires_for_build_editable`
- 源码锚点：`build/__init__.py#L134-L182`
- `GetRequires` 类（`builder/get_requires.py#L56`）：`cmake()`/`ninja()`/`variants()`/`dynamic_metadata()` 方法
- 关键规则：`build-system.requires` 中**不要**手动加 `cmake`/`ninja`/`setuptools`/`wheel`，scikit-build-core 智能注入

#### `## 配置项全集`

##### `### 配置三层来源`

- 三层来源表：`pyproject.toml`（静态首选）/ config-settings（动态首选）/ 环境变量 `SKBUILD_*`（应急）
- 优先级：env > config-settings > TOML
- 编码差异：env 与 config-settings 用 `a;b`（列表）/ `k=v;k2=v2`（dict），TOML 用原生类型
- 示例：同配置三种写法对照

##### `### 顶层配置项`

- 字段表：`build-dir`/`env`/`experimental`/`fail`/`metadata`/`minimum-version`/`strict-config`/`null-variant`
- 重点：`minimum-version` 建议 `"build-system.requires"` 自动同步
- 重点：`env` 表的 `setdefault` 语义与 `force=true` 行为

##### `### cmake.\* 配置项`

- 字段表：`version`/`args`/`define`/`build-type`/`source-dir`/`python-hints`
- `version` 可填 `"CMakeLists.txt"` 自动读取
- `define` 是 additive 表，支持多次累加
- 最小示例 + 完整示例

##### `### ninja.\* 与 search.\* 配置项`

- `ninja.version`（默认 >=1.5）、`ninja.make-fallback`（默认 true）
- `search.site-packages`（默认 true）

##### `### sdist.\* 配置项`

- 字段表：`include`/`exclude`/`inclusion-mode`/`reproducible`/`cmake`/`force-include`/`resolve-symlinks`/`strip`/`add`
- `inclusion-mode`（0.12 新增）：`default`/`classic`/`manual`
- gitignore 语法说明

##### `### wheel.\* 配置项`

- 字段表：`packages`/`py-api`/`expand-macos-universal-tags`/`install-dir`/`license-files`/`cmake`/`platlib`/`exclude`/`build-tag`/`force-include`/`reproducible`
- `py-api` 取值表：`cp38`/`py3`/`py2.py3`/`cp315t` 等
- `wheel.cmake=false` 关闭则纯 Python wheel
- `packages` 0.10 起支持 table 形式

##### `### editable.\* 配置项`

- 字段表：`mode`/`verbose`/`rebuild`/`rebuild-dir`
- `mode` 取值：`redirect`（默认）/ `inplace`

##### `### build.\* / install.\* 配置项`

- `build.tool-args`/`build.targets`/`build.verbose`/`build.requires`（0.11 新增）
- `install.components`/`install.targets`/`install.strip`（默认 true）

##### `### generate[] 配置项`

- 字段：`path`/`template`/`template-path`/`location`
- `location` 取值：`install`/`build`/`source`
- `string.Template` 语法
- 最小示例

##### `### logging.\* / backport.\* / messages.\* 配置项`

- `logging.level`（默认 WARNING）
- `backport.find-python`（默认 3.26.1）
- `messages.after-failure`/`messages.after-success`

##### `### variant\*（实验性 PEP 817）`

- `variant`/`variant-name`/`variant-label`/`null-variant`
- 需要 `experimental=true`
- 仅 config-settings 或 overrides 可设

#### `## Overrides 系统`

- `[[tool.scikit-build.overrides]]` 数组语法
- 12 种 `if` 选择器表（4 类）：版本类/字符串类/布尔类/复合类
- `if.any` 满足任一即可
- 多条件 `if` 全部满足才生效
- `inherit` 三模式：`none`/`append`/`prepend`
- `if.failed=true` 实现"构建失败则回退纯 Python wheel"（0.10+）
- 最小示例：按平台条件配置

#### `## 动态元数据`

##### `### 内置 4 个 provider`

- `scikit_build_core.metadata.setuptools_scm`（version）：从 git tag 或 `.git_archival.txt` 读版本
- `scikit_build_core.metadata.regex`（version）：从文件 regex 抽取，支持 `result`/`remove` 后处理（0.10+）
- `scikit_build_core.metadata.fancy_pypi_readme`（readme）：包装 hatch-fancy-pypi-readme
- `scikit_build_core.metadata.template`（任意字段）：引用其他 metadata 字段做模板输出（0.11.2+）

##### `### build.requires 注入`

- 0.11+ 新增
- 注入额外 `build-system.requires`
- 常与 overrides 配合：源码构建用本地路径，SDist 构建用 PyPI

##### `### generate[] 文件生成`

- `string.Template` 把 metadata 写到文件
- `location=source` 会自动加入 sdist.include 并覆盖现有文件

##### `### 第三方 provider 注意事项`

- 需 `experimental=true`
- 接口可能在 minor 版本间变化

#### `## CMakeLists.txt 集成示例`

##### `### 环境检测变量`

- `${SKBUILD}`（值为 "2"，classic 为 "1"）
- `${SKBUILD_CORE_VERSION}`（版本号）

##### `### 项目信息变量`

- `${SKBUILD_PROJECT_NAME}`
- `${SKBUILD_PROJECT_VERSION}`（1.0 起限制为四段 `major.minor.patch.tweak`）
- `${SKBUILD_PROJECT_VERSION_FULL}`（含 dev/local 后缀）
- `${SKBUILD_STATE}`（sdist/wheel/metadata_wheel/editable/metadata_editable）

##### `### FindPython 推荐写法`

- 推荐：`find_package(Python COMPONENTS Interpreter Development.Module REQUIRED)`
- 禁止：`Development`（含 Embed，manylinux 缺 libpython）
- Stable ABI：`Development.SABIModule`（CMake 3.26+），通过 `${SKBUILD_SABI_COMPONENT}` 与 `${SKBUILD_SABI_VERSION}` 条件注入

##### `### 安装目录变量`

- `${SKBUILD_PLATLIB_DIR}`（默认，→ site-packages）
- `${SKBUILD_PURELIB_DIR}`
- `${SKBUILD_DATA_DIR}`（→ 环境根，慎用）
- `${SKBUILD_HEADERS_DIR}`（→ Python include）
- `${SKBUILD_SCRIPTS_DIR}`（→ bin/Scripts）
- `${SKBUILD_METADATA_DIR}`（dist-info，仅 wheel 阶段可用）
- `${SKBUILD_NULL_DIR}`（丢弃）

##### `### SOABI 处理`

- 交叉编译时 FindPython 的 `Python_SOABI` 可能错误
- 应使用 `${SKBUILD_SOABI}`
- 可 `set(Python_SOABI ${SKBUILD_SOABI})` 覆盖

##### `### 语言助手`

- Cython：`cython-cmake`（`include(UseCython)` + `cython_transpile`）
- Fortran：`f2py-cmake`（`include(UseF2Py)`）
- 均为独立 CMake 包，加入 `build.requires`

##### `### 完整最小 CMakeLists.txt 示例`

```cmake
cmake_minimum_required(VERSION 3.15...4.3)
project(${SKBUILD_PROJECT_NAME} LANGUAGES CXX)

find_package(Python COMPONENTS Interpreter Development.Module REQUIRED)
python_add_library(myext MODULE WITH_SOABI main.cpp)
install(TARGETS myext DESTINATION ${SKBUILD_PROJECT_NAME})
```

#### `## minimum-version 兼容机制`

- `"build-system.requires"` 自动同步
- 各版本默认行为差异（0.10/0.11/0.12 重要变更）
- 避免 upper cap 的最佳实践
- `nox -t gen` 工作流：修改 model 后重新生成 schema 与文档

**章节末尾导航**：

```markdown
---
**上一章**：[02 - 项目目录结构：源码模块树解析](02-project-structure.md)
**下一章**：[04 - 入门到进阶：三级递进操作指南](04-quickstart-to-advanced.md)
**返回目录**：[00 - 概述与导航枢纽](00-overview.md)
```

---

### 04-quickstart-to-advanced.md（入门到进阶操作指南）

**职责**：提供三级递进路径，每级有可验证验收标准。从最小 CMake 项目到真实 C++ 扩展再到高级配置。

**二级/三级标题与要点**：

#### `## 第一级：最小 CMake 项目（5 分钟快速上手）`

##### `### 三种快速启动渠道`

- `scikit-build init --backend pybind11`（1.0 新增脚手架命令）
- `uv init --lib --build-backend=scikit`
- `scientific-python/cookie` 模板
- `buildgen new myext -r py/pybind11`

##### `### 最小 pyproject.toml`

- 完整可复制示例（C 扩展）
- 关键字段说明：`build-system.requires`、`build-backend`、`project.name`、`project.version`

##### `### 最小 CMakeLists.txt`

- 完整可复制示例（同 03 章"完整最小 CMakeLists.txt 示例"）

##### `### 构建与安装`

- 三种构建方式：`pipx run build`、`uv build`、`pip install build && python -m build`
- 默认先 SDist 后 Wheel
- `--sdist`/`--wheel` 可分别从源码直接构建

##### `### 验收标准`

- ✅ 成功生成 `dist/<name>-<version>.tar.gz`（SDist）
- ✅ 成功生成 `dist/<name>-<version>-cp3XX-*.whl`（Wheel）
- ✅ `pip install dist/*.whl` 后可 `python -c "import <name>; <name>.<func>()"`
- ✅ `scikit-build builder` 输出 Python/CMake/Ninja 版本信息

#### `## 第二级：真实 C++ 扩展包（pybind11/nanobind）`

##### `### pybind11 完整示例`

- 完整 `pyproject.toml`（含 `build-system.requires = ["scikit-build-core", "pybind11"]`）
- 完整 `CMakeLists.txt`（含 `find_package(pybind11 CONFIG REQUIRED)`、`pybind11_add_module`）
- 完整 `main.cpp`（含 `PYBIND11_MODULE` 宏）
- 构建命令：`pip install build && python -m build`
- 参考仓库：`pybind/scikit_build_example`

##### `### nanobind 完整示例`

- 完整 `pyproject.toml`（含 nanobind 推荐配置：`minimum-version="0.4"`、`build-dir="build/{wheel_tag}"`、`wheel.py-api="cp312"`）
- 完整 `CMakeLists.txt`（含 `find_package(nanobind CONFIG REQUIRED)`、`nanobind_add_module`）
- 完整 `main.cpp`
- 参考仓库：`wjakob/nanobind_example`

##### `### 8 种语言/绑定后端对照表`

- 完整对照表：pybind11/nanobind/SWIG/Cython/C/ABI3/ABI3t/Fortran
- 每种后端的 `pyproject.toml` 关键字段、`CMakeLists.txt` 关键模块、依赖说明
- 8 种后端示例参考：`scikit-build/scikit-build-sample-projects`

##### `### 验收标准`

- ✅ 成功构建 wheel 并安装
- ✅ `python -c "import <name>; print(<name>.add(1, 2))"` 输出 `3`
- ✅ `python -c "import <name>; print(<name>.__file__)"` 显示 `.so`/`.pyd` 路径
- ✅ `auditwheel show dist/*.whl`（Linux）显示 wheel 标签信息

#### `## 第三级：高级配置`

##### `### 自定义 CMake 选项`

- `cmake.define` 传递 CMake 变量
- `cmake.args` 传递任意 CMake 参数
- `-Ccmake.define.<NAME>=<value>` 命令行覆盖
- 与 overrides 配合实现条件配置

##### `### Ninja 与多线程构建`

- Ninja 默认按核心数并行
- `CMAKE_BUILD_PARALLEL_LEVEL=8 pip install .`
- `-Ccmake.define.CMAKE_BUILD_PARALLEL_LEVEL=8`
- `[tool.scikit-build.env]` 转发 `MAX_JOBS` 到 `CMAKE_BUILD_PARALLEL_LEVEL`（`setdefault` 语义）

##### `### build-dir 缓存复用`

- 默认临时目录，每次构建重新 configure
- `build-dir = "build/{wheel_tag}"` 实现缓存复用
- 缓存失效检测：`.skbuild-info.json`

##### `### abi3（Stable ABI）`

- `wheel.py-api = "cp38"` 配置
- CMake `Development.SABIModule`（3.26+）
- `${SKBUILD_SABI_COMPONENT}` 与 `${SKBUILD_SABI_VERSION}` 条件注入
- 优势：一个 wheel 支持多 Python 版本

##### `### abi3t（free-threaded Stable ABI）`

- `wheel.py-api = "cp315.cp315t"`
- 自由线程 Python 3.13+ 支持
- Windows 特殊处理：需手动 `Py_GIL_DISABLED` C 定义

##### `### 交叉编译`

- Apple Silicon：`ARCHFLAGS="-arch arm64"` + `CMAKE_OSX_ARCHITECTURES`
- Windows ARM：`_PYTHON_HOST_PLATFORM`
- WebAssembly/Emscripten/Pyodide
- `builder/macos.py` 的 `normalize_macos_version` 处理

##### `### 可编辑安装进阶`

- `editable.mode = "redirect"`（默认）vs `"inplace"`
- `editable.rebuild = true` 实现 import 触发重建
- `editable.verbose = true` 显示重建日志

##### `### 动态元数据实战`

- setuptools-scm 集成：从 git tag 读版本
- regex provider：从 `__init__.py` 抽取 `__version__`
- generate[] 文件生成：把版本写入 `_version.py`

##### `### Wheel 修复与分发`

- `linux_*` 标签不能上 PyPI
- `auditwheel`（Linux）转 manylinux/musllinux
- `delocate`（macOS）+ 交叉编译 Apple Silicon
- `delvewheel`（Windows）
- `repairwheel` 统一工具
- `cibuildwheel` 一站式跨平台构建

##### `### 验收标准`

- ✅ `build-dir` 配置后第二次构建时间显著缩短（cache hit）
- ✅ abi3 wheel 在多个 Python 版本（3.8+）下可安装运行
- ✅ 交叉编译 wheel 在目标平台可安装运行
- ✅ `editable.rebuild=true` 修改源码后 `import` 触发自动重建
- ✅ `cibuildwheel` 在 GitHub Actions 成功构建多平台 wheel

**章节末尾导航**：

```markdown
---
**上一章**：[03 - 核心 API 与配置：钩子、配置项与 CMakeLists.txt 示例](03-core-api-and-config.md)
**下一章**：[05 - 常见问题与最佳实践](05-faq-and-best-practices.md)
**返回目录**：[00 - 概述与导航枢纽](00-overview.md)
```

---

### 05-faq-and-best-practices.md（常见问题与最佳实践）

**职责**：FAQ 主题清单 + 故障排查流程 + CI/Conda/迁移最佳实践。覆盖跨平台编译、依赖管理、可编辑安装失败、CI 集成等。

**二级/三级标题与要点**：

#### `## FAQ 主题清单`

- 12 个高频问题列表（每项链接到下文详细解答）：
  1. 如何启用多线程构建？
  2. FindPython 报错怎么办？
  3. 如何调试构建过程？
  4. 如何迁移 setup.py 动态选项？
  5. wheel 标签是 `linux` 不能上 PyPI 怎么办？
  6. Conda 打包要注意什么？
  7. Free-threaded Windows 怎么处理？
  8. `prepare_metadata_*` 为什么被禁用？
  9. `minimum-version` 该设什么值？
  10. `build-system.requires` 要加 `cmake`/`ninja` 吗？
  11. 如何实现"构建失败则回退纯 Python wheel"？
  12. 如何注入额外 `build-system.requires`？

#### `## 跨平台编译故障排查`

##### `### FindPython 常见错误`

- 错误：请求 `Development.Embed` 在 manylinux 失败
- 原因：manylinux 没有 libpython
- 解决：仅请求 `Development.Module`

##### `### SOABI 错误`

- 错误：交叉编译时 `Python_SOABI` 不正确
- 解决：使用 `${SKBUILD_SOABI}` 或 `set(Python_SOABI ${SKBUILD_SOABI})`

##### `### macOS 跨编译`

- `ARCHFLAGS="-arch arm64"` 触发 `CMAKE_OSX_ARCHITECTURES`
- `normalize_macos_version` 处理版本字符串
- universal2 wheel 配置

##### `### Windows 特殊处理`

- Free-threaded：手动 `Py_GIL_DISABLED` C 定义
- MSVC generator vs Ninja generator
- `delvewheel` 修复依赖

#### `## 依赖管理最佳实践`

##### `### build-system.requires 规则`

- 不要手动加 `cmake`/`ninja`/`setuptools`/`wheel`
- scikit-build-core 智能判断并按需注入
- 例外：Android/FreeBSD/WebAssembly/ClearLinux 已装系统版本

##### `### build.requires 动态注入（0.11+）`

- 用途：源码构建用本地路径，SDist 构建用 PyPI
- 与 overrides 配合实现条件注入
- 示例代码

##### `### 动态元数据 provider 选择`

- setuptools-scm：git 项目首选
- regex：非 git 项目或自定义版本文件
- fancy_pypi_readme：复杂 README 渲染
- template：跨字段模板填充

#### `## 可编辑安装故障排查`

- redirect 模式失败：检查 `.pth` 文件位置
- rebuild 不触发：检查 `editable.rebuild` 与 `editable.rebuild-dir`
- inplace 模式限制：不支持 CMake 重建

#### `## CI 集成最佳实践（GitHub Actions）`

##### `### 基本 workflow 示例`

- 完整可复制的 GitHub Actions workflow
- 矩阵构建：Python 3.8/3.9/3.10/3.11/3.12/3.13
- 操作系统：ubuntu/macos/windows

##### `### cibuildwheel 集成`

- 完整 cibuildwheel 配置示例
- 跨平台 wheel 一站式构建
- 自动修复 wheel 标签

##### `### 缓存策略`

- `build-dir = "build/{wheel_tag}"` 配置
- GitHub Actions `actions/cache` 缓存 build 目录
- 减少二次构建时间

##### `### Free-threaded CI`

- Python 3.13t 矩阵配置
- `Py_GIL_DISABLED` 处理
- `wheel.py-api = "cp315.cp315t"`

#### `## Conda 打包最佳实践`

- `host` 表重建 `build-system.requires`（conda 版本）
- `build` 表加 `cmake` 和 `make`/`ninja`
- conda-build 在 UNIX 硬编码 `CMAKE_GENERATOR="Unix Makefiles"`，需手动改用 Ninja
- `scikit-build-core` 配方不能依赖 cmake/make/ninja（会进错表）

#### `## 从 classic scikit-build 迁移`

##### `### 配置变更`

- `build-backend` 改为 `scikit_build_core.build`
- `requires` 中 `scikit-build` 改 `scikit-build-core`
- 移除 `cmake`/`ninja`
- 填 `[tool.scikit-build]` 表
- setup.py/cfg 配置迁移到 pyproject.toml（可临时改 `build-backend=setuptools` + `hatch new --init` 自动迁移）
- `MANIFEST.in` 改用 `sdist.include`/`sdist.exclude`

##### `### CMake 变更`

- 移除 `PythonExtensions` 模块
- 改用 `find_package(Python ... COMPONENTS Interpreter Development.Module)` + `python_add_library(... MODULE WITH_SOABI)`
- `UseCython` 模块暂不支持（参考 getting started）
- `SKBUILD_CONFIGURE_OPTIONS` 环境变量改名为 `SKBUILD_CMAKE_ARGS`
- `SKBUILD_BUILD_OPTIONS` 不再支持，用 `CMAKE_BUILD_PARALLEL_LEVEL`/`SKBUILD_CMAKE_VERBOSE` 替代

#### `## 调试方法`

- `pip` 必须加 `-v` 否则吞输出
- 提高 `logging.level=INFO`
- `build.verbose=true`
- `scikit-build builder` 打印当前所有设置
- `scikit-build builder wheel-tag` 查看 wheel 标签
- `scikit-build builder sysconfig` 查看 sysconfig 信息

#### `## 最佳实践清单`

- 12 条最佳实践要点（每条一句话 + 跳转详细说明）
- 涵盖：配置、CMake、wheel、CI、迁移、调试

**章节末尾导航**：

```markdown
---
**上一章**：[04 - 入门到进阶：三级递进操作指南](04-quickstart-to-advanced.md)
**下一章**：[06 - 参考资料与扩展阅读](06-resources.md)
**返回目录**：[00 - 概述与导航枢纽](00-overview.md)
```

---

### 06-resources.md（参考资料与扩展阅读）

**职责**：官方链接、术语表、关联本项目条目。是读者继续深入探索的索引。

**二级/三级标题与要点**：

#### `## 官方资源`

##### `### 官方文档`

- 主站：https://scikit-build-core.readthedocs.io/en/latest/
- Guide（7 篇）：getting-started、cmakelists、dynamic_link、crosscompile、migration_guide、build、faqs
- Configuration（5 篇）：index、overrides、dynamic、formatted、search_paths
- Plugins（2 篇）：setuptools、hatchling
- API docs（4 篇）：scikit_build_core package、Schema、Config Reference、CLI Reference

##### `### 源码仓库`

- GitHub：https://github.com/scikit-build/scikit-build-core
- 本地克隆：`external/tools/scikit-build-core/`
- 示例项目：`scikit-build/scikit-build-sample-projects`（含 free-threading）

##### `### Changelog 与版本`

- Changelog：https://scikit-build-core.readthedocs.io/en/latest/about/changelog.html
- 当前稳定版：0.12.2
- 0.12.0 重要变更：新增 `sdist.inclusion-mode`、改进交叉编译、支持 fancy-pypi-readme 25.1
- 0.11.x：新增 `build.requires`、`metadata.template` provider
- 0.10.x：`cmake.minimum-version`/`ninja.minimum-version` 重命名为 `cmake.version`/`ninja.version`

#### `## 教程资源`

##### `### 中文资源`

- daobook pygallery：https://daobook.github.io/pygallery/study/fields/scikit-build-core/index.html
  - 注意：内容时滞（落后 1-2 个版本），仅翻译首页
  - 术语本地化：`wheel` 译为"轮子"，`SDist` 保留原文
- CSDN 博客：基础介绍性文章，注意 classic scikit-build 与 scikit-build-core 混淆问题

##### `### 英文资源`

- SciPy 2024 论文：https://doi.org/10.25080/FMKR8387
  - Henry Schreiner 等人发表
  - 涵盖 Python 打包历史、scikit-build-core 设计与内部实现、采用案例
  - 是深入了解设计动机与内部架构的权威资料
- pydevtools.com 实战教程：使用 uv + scikit-build-core + pybind11 构建 C++ 扩展的端到端示例
- pybind11 官方文档：推荐 scikit-build-core 作为构建后端
- nanobind 官方文档：给出推荐配置 `minimum-version="0.4"`、`build-dir="build/{wheel_tag}"`、`wheel.py-api="cp312"`

#### `## 同类工具对比`

- 完整对比表：scikit-build-core vs classic scikit-build vs meson-python vs maturin vs py-build-cmake vs cmeel vs enscons
- 对比维度：构建系统、PEP 517 支持、CMake 集成、跨平台 wheel、可编辑安装、学习曲线、社区活跃度
- 选型建议：何时选 scikit-build-core，何时选其他

#### `## 术语表（Glossary）`

- 至少 15 个术语，按字母顺序排列
- 必含术语：
  - **ABI3（Stable ABI）**：Python 稳定 ABI，一个 wheel 支持多 Python 版本
  - **ABI3t（free-threaded Stable ABI）**：自由线程 Python 3.13+ 的 Stable ABI
  - **CMake**：跨平台构建系统生成器
  - **config-settings**：PEP 517 配置传递机制，扁平点号键
  - **cibuildwheel**：跨平台 wheel 构建自动化工具
  - **auditwheel**：Linux wheel 修复工具，转 manylinux/musllinux
  - **delocate**：macOS wheel 修复工具
  - **delvewheel**：Windows wheel 修复工具
  - **File API**：CMake 文件 API，用于查询构建信息
  - **manylinux/musllinux**：Linux wheel 兼容性规范
  - **Ninja**：高性能构建系统，scikit-build-core 默认 generator
  - **PEP 517**：Python 构建后端标准
  - **PEP 660**：可编辑安装支持
  - **PEP 621**：项目元数据标准（`[project]` 表）
  - **PEP 817**：wheel 变体（实验性）
  - **SDist**：源码分发（Source Distribution）
  - **SOABI**：共享对象 ABI 标签，标识 Python 扩展模块的二进制兼容性
  - **Wheel**：二进制分发格式
  - **pyproject.toml**：Python 项目配置文件标准

#### `## 关联本项目知识库条目`

- [interface-api-abi-protocol-wiki](../../interface-api-abi-protocol-wiki/00-overview.md)：构建工具链 ABI 层（与 Stable ABI/ABI3 概念相关）
- [karpathy-llm-coding-guidelines](../karpathy-llm-coding-guidelines-tutorial.md)：Python 工程实践
- [ffi-wiki](../ffi-wiki/00-overview.md)：FFI 跨语言调用（与 CMake 集成扩展模块相关）
- [idl-wiki](../idl-wiki/00-overview.md)：接口定义语言（与 Python 扩展接口设计相关）

#### `## 扩展阅读建议`

##### `### 方向 1：Python 打包生态`

- PEP 517/518/621/660/808 等标准文档
- 《Python Packaging User Guide》
- setuptools/hatchling/flit/maturin 文档

##### `### 方向 2：CMake 深入`

- 《CMake 实践》
- 《Professional CMake: A Practical Guide》
- CMake 官方文档：https://cmake.org/documentation/

##### `### 方向 3：跨平台 wheel 构建`

- cibuildwheel 文档：https://cibuildwheel.readthedocs.io/
- manylinux 规范：PEP 513/571/599
- musllinux 规范：PEP 656

##### `### 方向 4：Python 扩展模块开发`

- pybind11 文档：https://pybind11.readthedocs.io/
- nanobind 文档：https://nanobind.readthedocs.io/
- Cython 文档：https://cython.readthedocs.io/

#### `## 结语`

- 回顾 scikit-build-core 的核心价值：现代 PEP 517 + 原生 CMake + 多语言绑定
- 鼓励读者参与社区贡献
- 关联 spec：`create-scikit-build-core-wiki-tutorial`

**章节末尾导航**：

```markdown
---
**上一章**：[05 - 常见问题与最佳实践](05-faq-and-best-practices.md)
**返回目录**：[00 - 概述与导航枢纽](00-overview.md)
**本教程结束**
```

---

## 章节间导航关系

### 导航链接格式

每个章节文件末尾统一添加导航块，格式如下：

```markdown
---
**上一章**：[<上一章标题>](<上一章文件名>.md)
**下一章**：[<下一章标题>](<下一章文件名>.md)
**返回目录**：[00 - 概述与导航枢纽](00-overview.md)
```

### 完整导航链

```
00-overview.md
  └─ 下一章 → 01-concepts-architecture.md

01-concepts-architecture.md
  ├─ 上一章 → 00-overview.md
  └─ 下一章 → 02-project-structure.md

02-project-structure.md
  ├─ 上一章 → 01-concepts-architecture.md
  └─ 下一章 → 03-core-api-and-config.md

03-core-api-and-config.md
  ├─ 上一章 → 02-project-structure.md
  └─ 下一章 → 04-quickstart-to-advanced.md

04-quickstart-to-advanced.md
  ├─ 上一章 → 03-core-api-and-config.md
  └─ 下一章 → 05-faq-and-best-practices.md

05-faq-and-best-practices.md
  ├─ 上一章 → 04-quickstart-to-advanced.md
  └─ 下一章 → 06-resources.md

06-resources.md
  ├─ 上一章 → 05-faq-and-best-practices.md
  └─ 返回目录 → 00-overview.md（教程结束）
```

### 跨章节交叉引用规则

- **概念引用**：01 章详解概念，02-05 章引用时用 `[概念名](01-concepts-architecture.md#<锚点>)`
- **源码引用**：02 章汇总源码锚点，01/03 章引用时直接给出锚点（不跨文件链接）
- **配置项引用**：03 章详解配置项，04/05 章引用时用 `[配置项名](03-core-api-and-config.md#<锚点>)`
- **示例引用**：04 章含完整示例，03 章引用时用 `[完整示例](04-quickstart-to-advanced.md#<锚点>)`
- **FAQ 引用**：05 章含 FAQ 清单，其他章引用时用 `[FAQ](05-faq-and-best-practices.md#<锚点>)`

---

## 文档规范契约

### YAML frontmatter 模板

每个章节文件**必须**以如下 YAML frontmatter 开头：

```yaml
---
id: "scikit-build-core-wiki-<chapter-slug>"
title: "<中文章节标题>"
source: "spec:create-scikit-build-core-wiki-tutorial"
category: "learning"
tags: ["scikit-build-core", "<章节特定标签>"]
date: 2026-07-04
status: "stable"
author: "SpecWeave"
summary: "<一句话章节摘要>"
---
```

**字段规则**：

- `id`：唯一标识，格式 `scikit-build-core-wiki-<chapter-slug>`，如 `scikit-build-core-wiki-overview`、`scikit-build-core-wiki-concepts-architecture`
- `title`：中文章节标题，与一级标题（H1）一致
- `source`：固定值 `"spec:create-scikit-build-core-wiki-tutorial"`（溯源到 spec）
- `category`：固定值 `"learning"`（与 `docs/knowledge/learning/` 路径对应）
- `tags`：含 `scikit-build-core` 基础标签 + 章节特定标签（如 `pep517`、`cmake`、`wheel`、`configuration`）
- `date`：2026-07-04（与 spec 创建日期一致）
- `status`：`stable`（章节定稿后）
- `author`：`SpecWeave`
- `summary`：一句话章节摘要（30-50 字）

**示例**（`00-overview.md`）：

```yaml
---
id: "scikit-build-core-wiki-overview"
title: "scikit-build-core 概述与导航枢纽"
source: "spec:create-scikit-build-core-wiki-tutorial"
category: "learning"
tags: ["scikit-build-core", "overview", "navigation", "pep517"]
date: 2026-07-04
status: "stable"
author: "SpecWeave"
summary: "scikit-build-core 定位、特性速览、阅读路径与目录导航表"
---
```

### 相对路径规则

所有文档间引用**必须使用相对路径**，禁止 `file:///` 绝对路径。

#### 文档间引用（同目录）

| 引用场景 | 路径写法 | 示例 |
|---|---|---|
| 同目录文件互引 | 直接写文件名 | `[01 - 概念与架构](01-concepts-architecture.md)` |
| 同文件内引用 | 省略文件名，锚点以 `#` 开头 | `## PEP 517/660 构建后端机制` |
| 跨文件锚点引用 | 文件名 + `#` + 锚点 | `[配置项详解](03-core-api-and-config.md#cmake-配置项)` |

#### 跨目录引用（到项目其他文档）

| 引用场景 | 路径写法 | 示例 |
|---|---|---|
| 上级目录（`learning/`） | `../` + 文件名 | `[karpathy-llm-coding-guidelines](../karpathy-llm-coding-guidelines-tutorial.md)` |
| 同级目录（`learning/<wiki>/`） | `../../` + 目录 + 文件名 | `[interface-api-abi-protocol-wiki](../../interface-api-abi-protocol-wiki/00-overview.md)` |
| 项目根目录 | `../../../` + 路径 | `[AGENTS.md](../../../AGENTS.md)` |

#### 禁止事项

- ❌ **禁止**使用 `file:///d:/...` 等本地绝对路径（在不同机器/克隆位置会立即断链）
- ❌ **禁止**使用 `https://specweave.local/...` 等虚构 URL
- ✅ **建议**锚点使用 kebab-case（如 `#cmake-配置项`），与 Markdown 自动生成的锚点一致

### 源码锚点格式

所有引用 `external/tools/scikit-build-core/` 源码的位置**必须**标注文件路径与行号锚点。

#### 行号锚点格式

```
src/scikit_build_core/<path>#L<起始行>
src/scikit_build_core/<path>#L<起始行>-L<结束行>
```

**示例**：

- 单行：`src/scikit_build_core/build/__init__.py#L45`
- 行范围：`src/scikit_build_core/build/__init__.py#L45-L58`
- 顶级文件：`src/scikit_build_core/__main__.py#L37`

#### 行号锚点呈现方式

| 呈现场景 | 写法 | 示例 |
|---|---|---|
| 行内引用 | 反引号包裹路径 + 锚点 | `` `build/__init__.py#L45-L58` `` |
| 表格单元格 | 反引号包裹路径 + 锚点 | `\| build_wheel \| `build/__init__.py#L45-L58` \|` |
| 段落引用 | 反引号包裹完整路径 | `` 源码锚点：`src/scikit_build_core/build/__init__.py#L45-L58` `` |

#### 路径前缀规则

- **首次引用**：使用完整路径 `src/scikit_build_core/<path>#L<行号>`，建立上下文
- **后续引用**：可省略 `src/scikit_build_core/` 前缀，使用 `<path>#L<行号>`，避免冗余
- **跨章节引用**：统一使用完整路径 `src/scikit_build_core/<path>#L<行号>`

#### pyproject.toml 锚点

引用 `external/tools/scikit-build-core/pyproject.toml` 时：

```
pyproject.toml#L<行号>
pyproject.toml#L<起始行>-L<结束行>
```

**示例**：`pyproject.toml#L81-L98`（入口点注册段）

#### 锚点准确性要求

- 行号必须与 `external/tools/scikit-build-core/` 实际源码对应
- 章节编写者须打开源码文件验证行号准确性
- 行号锚点用于精确追溯，不允许使用模糊表述（如"约在第 50 行"）

### Mermaid 规则

所有 Mermaid 图表须遵循 `docs/development-standards.md` 的"Mermaid 编码规范"安全编码六规则。

#### 安全编码六规则要点

1. **禁止空行**：Mermaid 代码块内禁止使用空行，`subgraph` 块之间、边定义与 `style` 语句之间的空行会导致解析器误判图表结束
2. **禁止 Markdown 列表触发格式**：节点标签内禁止 `数字. ` / `- ` / `* ` 等列表触发模式，改用中文冒号 `：` 或去掉空格
3. **节点换行使用 `<br/>`**：禁止使用 `\n` 转义字符，统一使用 HTML `<br/>` 标签
4. **Subgraph 格式**：`subgraph ID ["标题文本"]`，ID 必须为英文标识符，标题放双引号内
5. **边标签格式**：`-->|"标签"|目标节点`，含中文/特殊字符的标签必须双引号包裹
6. **错误排查分层法**：语法结构层 → Subgraph 层 → 节点文本层 → 边标签层 → Style 层

#### 本 Wiki 必含的 Mermaid 图清单

| 章节 | 图表 | 类型 | 内容 |
|---|---|---|---|
| 00 | 维恩图 | `flowchart` | 三类后端覆盖关系（CMake 系/PEP 517 系/多语言绑定系） |
| 00 | 阅读路径图 | `flowchart` | 三条阅读路径（快速上手/深入理解/排错参考） |
| 01 | PEP 517 钩子时序图 | `sequenceDiagram` | pip/build → get_requires → build_wheel/build_sdist |
| 01 | CMake 集成三层调用图 | `flowchart` | Builder → CMaker → CMake 子进程 |
| 01 | 8 步 wheel 构建流程图 | `flowchart` | 8 步构建流程含源码文件标注 |
| 01 | 配置源链合并示意图 | `flowchart` | 三个 Source → SourceChain → SettingsReader → ScikitBuildSettings |
| 01 | File API query/reply 时序图 | `sequenceDiagram` | CMaker.configure → 写 query → CMake 写 reply → load_reply_dir |
| 02 | 模块依赖关系图 | `flowchart` | 顶层文件 → 子目录 |

#### Mermaid 图编写流程

章节编写者在编写 Mermaid 图时**必须**：

1. 先用 `mermaid-cmd` Skill 加载安全编码规则与模板
2. 编写 Mermaid 代码后运行 `python .agents/scripts/check-mermaid.py` 检测
3. 修复所有检测出的问题（特别是 `\n` → `<br/>`）
4. 在 PR 描述中附上 Mermaid 渲染截图验证

### 文档风格规范

#### 标题层级

- 一级标题（H1）：每文件 1 个，与 `title` 字段一致
- 二级标题（H2）：章节主要分节，必须含 `##` 前缀
- 三级标题（H3）：H2 内的细分，必须含 `###` 前缀
- 四级标题（H4）：仅在必要时使用

#### 代码块

- 所有代码块必须标注语言（如 ` ```python`、` ```cmake`、` ```toml`、` ```bash`）
- 代码块前后必须空一行
- 长代码块（>30 行）须拆分为多个小代码块或加注释分段

#### 表格

- 表格前后必须空一行
- 表格列分隔符 `|---|---|` 的列数必须与表头一致
- 单元格内禁止使用 `|` 字符（用 `\|` 转义或改用其他分隔符）

#### 引用块

- 引用块使用 `>` 前缀
- 多行引用块每行都须有 `>` 前缀
- 关键提示、警告、注意使用引用块

#### 列表

- 无序列表使用 `-` 前缀
- 有序列表使用 `1.` 前缀（Markdown 自动编号）
- 列表项前后必须空一行

### 文档生成与验证

#### 生成顺序

1. 按 00 → 01 → 02 → 03 → 04 → 05 → 06 顺序编写
2. 每章编写完成后立即运行 `python .agents/scripts/check-links.py --path docs/knowledge/learning/scikit-build-core-wiki/` 验证链接
3. 每章含 Mermaid 图时运行 `python .agents/scripts/check-mermaid.py` 验证 Mermaid 语法
4. 全部完成后运行 `python .agents/scripts/docgen.py` 更新 `docs/knowledge/README.md` 索引

#### 验证清单

每章编写完成后须确认：

- ✅ YAML frontmatter 完整（含 `id`/`title`/`source`/`category`/`tags`/`date`/`status`/`author`/`summary`）
- ✅ `source` 字段值为 `"spec:create-scikit-build-core-wiki-tutorial"`
- ✅ 文档间引用使用相对路径（无 `file:///`）
- ✅ 源码锚点格式正确（`src/scikit_build_core/<path>#L<行号>`）
- ✅ Mermaid 图符合安全编码六规则
- ✅ 章节末尾导航块完整（上一章/下一章/返回目录）
- ✅ 无断链（`check-links.py` 退出码为 0）
- ✅ 无 Mermaid 语法错误（`check-mermaid.py` 退出码为 0）

---

## 章节编写依赖与并行策略

### 编写依赖

```
00-overview.md（独立，可先写）
      ↓
01-concepts-architecture.md（依赖 00 的导航表）
      ↓
02-project-structure.md（依赖 01 的概念基础）
      ↓
03-core-api-and-config.md（依赖 01/02 的概念与源码锚点）
      ↓
04-quickstart-to-advanced.md（依赖 03 的配置项与示例）
      ↓
05-faq-and-best-practices.md（依赖 01-04 的全部内容）
      ↓
06-resources.md（依赖 01-05 的术语引用）
```

### 并行策略

- **可并行**：00 与 02（00 写导航表时 02 可先起草模块表）
- **可并行**：03 与 04（03 写配置项时 04 可先起草最小示例）
- **不可并行**：05 必须在 01-04 完成后编写（FAQ 引用前面章节）
- **不可并行**：06 必须在 01-05 完成后编写（术语表引用前面章节）

### 验收顺序

1. 00-overview.md 完成后，验证目录导航表链接可达
2. 01-02 完成后，验证 Mermaid 图渲染、源码锚点准确
3. 03-04 完成后，验证代码示例可复制运行
4. 05-06 完成后，验证交叉引用完整、术语表覆盖
5. 全部完成后，运行 `docgen` + `check-links` + `check-mermaid` 综合验证

---

## 附录：源码锚点速查表

以下是章节编写时高频引用的源码锚点，供快速查阅：

### PEP 517 钩子

| 钩子 | 源码锚点 |
|---|---|
| `build_wheel` | `src/scikit_build_core/build/__init__.py#L45-L58` |
| `build_editable` | `src/scikit_build_core/build/__init__.py#L61-L74` |
| `prepare_metadata_for_build_wheel` | `src/scikit_build_core/build/__init__.py#L95-L104` |
| `prepare_metadata_for_build_editable` | `src/scikit_build_core/build/__init__.py#L106-L116` |
| `build_sdist` | `src/scikit_build_core/build/__init__.py#L124-L131` |
| `get_requires_for_build_sdist` | `src/scikit_build_core/build/__init__.py#L134-L150` |
| `get_requires_for_build_wheel` | `src/scikit_build_core/build/__init__.py#L173-L176` |
| `get_requires_for_build_editable` | `src/scikit_build_core/build/__init__.py#L179-L182` |
| `_has_safe_metadata` | `src/scikit_build_core/build/__init__.py#L77-L90` |
| `_build_wheel_impl` | `src/scikit_build_core/build/wheel.py#L215` |
| `_build_wheel_impl_impl` | `src/scikit_build_core/build/wheel.py#L310` |
| `build_sdist` 实现 | `src/scikit_build_core/build/sdist.py#L129` |
| `get_standard_metadata` | `src/scikit_build_core/build/metadata.py#L53` |

### 配置系统

| 模块 | 源码锚点 |
|---|---|
| `ScikitBuildSettings` 主数据类 | `src/scikit_build_core/settings/skbuild_model.py#L815-L933` |
| `CMakeSettings` 子节 | `src/scikit_build_core/settings/skbuild_model.py#L164` |
| `WheelSettings` 子节 | `src/scikit_build_core/settings/skbuild_model.py#L434` |
| `EditableSettings` 子节 | `src/scikit_build_core/settings/skbuild_model.py#L636` |
| `GenerateSettings` 子节 | `src/scikit_build_core/settings/skbuild_model.py#L759` |
| `SettingsReader` 编排器 | `src/scikit_build_core/settings/skbuild_read_settings.py#L61` |
| `process_overrides` | `src/scikit_build_core/settings/skbuild_overrides.py#L38` |
| `generate_skbuild_schema` | `src/scikit_build_core/settings/skbuild_schema.py#L41` |
| `get_skbuild_schema` | `src/scikit_build_core/settings/skbuild_schema.py#L233` |
| 源链 docstring | `src/scikit_build_core/settings/sources.py#L1-L79` |

### CMake 集成

| 模块 | 源码锚点 |
|---|---|
| `CMake` 值对象 | `src/scikit_build_core/cmake.py#L67-L99` |
| `CMake.default_search` | `src/scikit_build_core/cmake.py#L71-L95` |
| `CMaker` 类 | `src/scikit_build_core/cmake.py#L102` |
| `CMaker.configure` | `src/scikit_build_core/cmake.py#L284` |
| `CMaker.build` | `src/scikit_build_core/cmake.py#L327` |
| `CMaker.install` | `src/scikit_build_core/cmake.py#L352` |
| `Builder` 类 | `src/scikit_build_core/builder/builder.py#L213` |
| `Builder.configure` | `src/scikit_build_core/builder/builder.py#L257` |
| `Builder.build` | `src/scikit_build_core/builder/builder.py#L488` |
| `Builder.install` | `src/scikit_build_core/builder/builder.py#L502` |
| `parse_generator` | `src/scikit_build_core/builder/generator.py#L39` |
| `GetRequires` 类 | `src/scikit_build_core/builder/get_requires.py#L56` |
| `Program` NamedTuple | `src/scikit_build_core/program_search.py#L39-L46` |

### File API

| 模块 | 源码锚点 |
|---|---|
| `stateless_query` | `src/scikit_build_core/file_api/query.py#L19` |
| `load_reply_dir` | `src/scikit_build_core/file_api/reply.py#L38` |
| `Converter` 类 | `src/scikit_build_core/file_api/reply.py#L50` |

### 元数据与可编辑安装

| 模块 | 源码锚点 |
|---|---|
| `editable_redirect` | `src/scikit_build_core/build/_editable.py#L48` |
| `generate_file_contents` | `src/scikit_build_core/build/generate.py#L20` |
| `WheelWriter` | `src/scikit_build_core/build/_wheelfile.py` |

### 入口点注册

| 入口点 | 源码锚点 |
|---|---|
| CLI 入口 | `external/tools/scikit-build-core/pyproject.toml#L74-L78` |
| distutils `build_cmake` | `external/tools/scikit-build-core/pyproject.toml#L81` |
| distutils setup 关键字 | `external/tools/scikit-build-core/pyproject.toml#L82-L87` |
| setuptools finalize | `external/tools/scikit-build-core/pyproject.toml#L88` |
| hatch 插件 | `external/tools/scikit-build-core/pyproject.toml#L90` |
| schema 入口 | `external/tools/scikit-build-core/pyproject.toml#L89` |
| dynamic_metadata provider | `external/tools/scikit-build-core/pyproject.toml#L95-L98` |

---

## 设计契约终止

本设计文档作为 Task 4 产出物，是 Task 5-11 章节编写的契约依据。章节编写者须严格遵循：

1. **文件清单与命名**：7 个文件名与职责不可变更
2. **章节大纲**：每章二级/三级标题与要点不可删减，可按需扩展
3. **导航关系**：章节间导航链接格式与顺序不可变更
4. **文档规范契约**：YAML frontmatter、相对路径、源码锚点、Mermaid 规则不可违反
5. **源码锚点准确性**：所有锚点必须与 `external/tools/scikit-build-core/` 实际源码对应

任何偏离须先更新本设计文档（提交 PR 修订本文件），再编写章节，避免返工。

**设计文档版本**：1.0
**设计日期**：2026-07-04
**设计依据**：source-code-analysis.md（v1.0）+ online-docs-summary.md（v1.0）
