---
id: "xuanspace-mono-repo-spec"
version: "1.4"
source: "seven-concepts innovation scenario (F→V→I) + naming alignment with zhujian-wudao + AGENTS.md/Sphinx+MyST docs requirement + build system (cmake/ninja/scikit-build-core) + submodule placement analysis + frontmatter content-metadata dichotomy"
x-toml-ref: "../../../.meta/toml/.trae/specs/xuanspace-mono-repo/spec.toml"
---

# Xuanspace（玄境）Monorepo - Product Requirement Document

## Overview

* **Summary**: 在 GitHub 账号 `xinetzone` 下创建名为 **xuanspace**（中文品牌名**玄境**，取自《老子》"玄之又玄，众妙之门"）的 monorepo 主项目。玄境是所有子项目的容器空间——既能承载以竹简悟道为代表的东方哲思类文化项目，也能承载 AI 工具链、NPU/TVM 等技术类项目。提供清晰的目录结构区分不同类型子项目，统一管理版本控制、依赖关系和文档系统，支持第三方库与自建库的高效维护与同步更新。

* **Purpose**: 解决多个分散仓库管理混乱、依赖版本不一致、文档分散难以查找、第三方库更新不同步等问题，通过 monorepo 架构实现统一管理、降低维护成本、提升协作效率。"玄境"之名取"众妙之门"意涵，寓意这是一个孕育和容纳各种项目的空间。

* **Target Users**: xinetzone 账号所有者、项目贡献者、使用这些开源项目的开发者。

## Goals

* 建立物理隔离的清晰目录结构，区分 apps/libs/vendor/tools/docs/scripts/attic/.agents 等不同类型目录

* 实现基于 pyproject.toml (PEP 517/621) 的标准化依赖管理，PDM 作为推荐但非强制工具，支持 uv/pip 作为替代方案

* **Python 环境严格要求 3.13 及更高版本**，所有依赖包必须验证与 Python 3.13+ 的兼容性

* 提供基于语义化版本的版本控制与发布机制，tag 格式 `<project>@<version>`

* 设计就近文档 + 全局 Sphinx+MyST 导航的双层文档系统，记录功能/使用/维护状态

* 包含完整的 AGENTS.md 智能体入口文件与 .agents/ 规范目录，支持 AI 辅助协作

* docs/ 目录必须使用 Sphinx + MyST Markdown 进行文档管理，支持编译为 HTML 等可发布格式

* 正确集成 CMake + Ninja + scikit-build-core 构建工具链，支持 C/C++ 原生扩展包的标准化构建

* 提供幂等的批量依赖更新脚本，支持 dry-run 预览

* 设计可演进的架构，支持从几个子项目平滑扩展到数十个子项目

* 包含完善的贡献指南和5分钟快速开始，降低新成员上手门槛

* CLI 工具命名为 `xs`（xuanspace 缩写），简洁易记

* 明确 xuanspace 作为 SpecWeave 项目 git 子模块的存放位置与管理策略

## Non-Goals (Out of Scope)

* 不实现具体子项目的业务逻辑开发

* 不强制引入 Bazel/Buck/Pants/Meson 等通用构建系统（CMake+Ninja 为原生扩展专用，纯 Python 项目无需 CMake）

* 不设计跨团队复杂权限管理流程（当前为个人/小团队开源项目）

* 不强制所有子项目使用同一种编程语言

* 不强制 PDM 作为唯一包管理器（PDM 为推荐工具，但支持 uv/pip 等 PEP 517 兼容工具）

* 不实现完整的 CI/CD 平台（仅提供基础 GitHub Actions 配置模板）

* 不做私有代码管理（当前假设所有子项目均为公开开源项目）

* 不立即引入 Changesets（先手动维护 CHANGELOG，待子项目数量增多后再平滑引入）

* 不提供 Windows/macOS/Linux 三平台的 wheel 预编译分发服务（初期仅保证构建脚本跨平台兼容）

## Background & Context

* xinetzone 是用户的 GitHub 账号，现有多个分散的开源项目

* 现有项目包括技术类（NPU/TVM/AI 工具链）和文化类（竹简悟道——以帛书《老子》为哲学根基的 AI 反思引导工具）

* "玄境"命名呼应竹简悟道的哲学根基（《老子》"玄之又玄，众妙之门"），使文化类项目有归属感，技术类项目作为"器"层共存于"境"中

* 多仓库管理存在痛点：依赖版本漂移、重复配置、文档分散、更新需要逐个操作

* monorepo 是业界成熟方案（React、Angular、Babel、Vue3 等大型开源项目均采用）

* 现代 Python 打包标准（PEP 517/518/621/660）已确立"构建后端隔离"模型，pyproject.toml 是统一的依赖声明格式，不强制绑定特定包管理器

* scikit-build-core 是基于 CMake 的现代 PEP 517 构建后端，原生支持 C/C++/Fortran/pybind11/nanobind 等扩展，无需 setuptools

* CMake + Ninja 是 C/C++ 跨平台构建的事实标准组合

* 用户偏好：Python 3.13+、YAML 配置、typer+dataclass 编写 CLI 脚本，PDM 为推荐包管理器但不强制

* xuanspace 需作为子模块纳入 SpecWeave 项目统一管理，存放位置候选方案已分析

* 本方案基于第一性原理推导（6条公理）+ 对抗审查（12个攻击点），已防御已知风险

## 文档元数据格式约定（YAML/TOML 内容-元数据二分法）

项目中所有 Markdown 文档（含 spec.md、tasks.md、checklist.md 及各类技术文档）统一采用"YAML 存核心标识 + TOML 存完整元数据"的内容-元数据二分法格式，遵循以下规范：

### YAML Frontmatter（文件内，扁平结构）

每个 Markdown 文件头部使用 `---` 分隔的 YAML frontmatter，**仅保留核心标识字段和内容配置字段**，禁止多行缩进嵌套：

| 字段           | 必填   | 说明                                                     |
| ------------ | ---- | ------------------------------------------------------ |
| `id`         | 是    | kebab-case 唯一标识符，如 `xuanspace-mono-repo-spec`          |
| `x-toml-ref` | 是    | 外部 TOML 元数据文件的相对路径（从当前 MD 文件目录出发）                      |
| `source`     | 条件必填 | 派生产物的来源溯源，格式为 `"<相对路径>#<锚点>"` 或 `"<URL>"`；多个来源用逗号+空格分隔 |
| `version`    | 按需   | 内容配置字段——当 version 是文档内容的一部分（如 spec 版本号）时保留在 YAML 中     |
| 其他内容配置字段     | 按需   | 如 MCP 配置的 name/description 等直接被正文引用的字段                 |

**YAML 禁止事项**：禁止多行数组缩进、禁止嵌套对象、禁止 category/date/tags 等描述性元数据（这些移至 TOML）。

YAML frontmatter 示例（spec.md）：

```yaml
---
id: "xuanspace-mono-repo-spec"
version: "1.4"
source: "seven-concepts innovation scenario (F→V→I) + naming alignment"
x-toml-ref: "../../../.meta/toml/.trae/specs/xuanspace-mono-repo/spec.toml"
---
```

### 外部 TOML 元数据文件（.meta/toml/）

复杂/描述性元数据存储在 `.meta/toml/` 目录下的外部 TOML 文件中，路径镜像 Markdown 文件的项目内路径：

| Markdown 文件                               | TOML 元数据文件                                             |
| ----------------------------------------- | ------------------------------------------------------ |
| `.trae/specs/xuanspace-mono-repo/spec.md` | `.meta/toml/.trae/specs/xuanspace-mono-repo/spec.toml` |
| `docs/architecture.md`                    | `.meta/toml/docs/architecture.toml`                    |
| `.agents/rules/example.md`                | `.meta/toml/.agents/rules/example.toml`                |

**TOML 必填字段**：`title`（文档标题）、`category`（分类）。

**TOML 推荐字段**：`tags`（标签数组）、`date`（YYYY-MM-DD）、`version`（版本号）、`status`（draft/stable/deprecated）、`part_of`（所属集合）、`summary`（摘要）、`changelog`（变更日志数组）。

TOML 元数据示例：

```toml
title = "Xuanspace（玄境）Monorepo - Product Requirement Document"
category = "spec"
tags = ["monorepo", "python3.13", "cmake", "scikit-build-core"]
date = "2026-07-24"
version = "1.4"
status = "in-review"
part_of = "xuanspace-mono-repo"
summary = "玄境Python monorepo产品需求文档"
changelog = [
  "2026-07-24 | v1.4 | docs+config | 新增文档元数据格式约定章节",
  "2026-07-21 | v1.0 | initial | 初始版本"
]
```

### x-toml-ref 路径计算

`x-toml-ref` 是从 MD 文件所在目录到 TOML 文件的**相对路径**，按目录深度使用 `../` 回退到项目根后拼接：

| MD 文件位置                    | 距根深度 | x-toml-ref 前缀          |
| -------------------------- | ---- | ---------------------- |
| 项目根目录（AGENTS.md/README.md） | 0    | `.meta/toml/`          |
| `.trae/specs/<name>/`      | 3    | `../../../.meta/toml/` |
| `docs/`                    | 1    | `../.meta/toml/`       |
| `.agents/rules/`           | 2    | `../../.meta/toml/`    |

### 字段合并规则

YAML frontmatter 中的字段**优先于**外部 TOML 文件的同名字段。核心标识字段保留在 YAML，复杂/描述性元数据存储在外部 TOML。

### 适用范围

本约定适用于 xuanspace 项目中的所有 Markdown 文档，包括但不限于：

* `.trae/specs/` 下的 spec.md/tasks.md/checklist.md（spec 规划文档）

* `docs/` 下的 Sphinx 文档（知识文档、指南、教程）

* `.agents/` 下的规则、角色定义、协议文档

* 各子项目根目录的 README.md

* `.meta/toml/` 目录下的 TOML 文件需与对应 MD 文件同步创建和维护

## Functional Requirements

* **FR-1**: 项目必须具备标准目录结构：apps/（应用）、libs/（自建库）、vendor/（第三方）、tools/（工具）、docs/（全局文档）、scripts/（自动化脚本）、attic/（归档）

* **FR-2**: 每个顶层目录必须有 README.md 说明该目录的用途、准入标准和命名规范

* **FR-3**: 所有 Python 项目使用标准 pyproject.toml (PEP 621) 声明依赖和元数据，`requires-python = "&gt;=3.13"` 严格锁定；PDM 作为推荐的 workspace 管理工具（支持本地依赖自动链接），但同时提供 uv/pip 等 PEP 517 兼容工具的安装流程文档

* **FR-4**: 支持多语言混合（Python/Node.js/C-C++/其他），各语言使用原生工具链；非 Python 项目独立管理但遵循统一目录规范；C/C++ 原生扩展项目使用 CMake + Ninja + scikit-build-core 构建工具链

* **FR-4a**: 提供不使用 PDM 时的替代依赖管理方案：基于标准 pyproject.toml 的 `[project.optional-dependencies]` 依赖声明格式，支持 `pip install -e ".[docs]"` / `pip install -e ".[dev]"` 可编辑安装和 `uv pip install` 快速安装，不使用独立的 requirements.txt（根 pyproject.toml 为依赖单一真相源）

* **FR-4b**: CMake 与 Ninja 的集成配置：scikit-build-core 通过 `[tool.scikit-build]` 表配置 CMake 参数（`cmake.args = ["-G", "Ninja", "-DCMAKE_BUILD_TYPE:STRING=Release"]`），使用 Ninja 作为默认生成器加速构建；支持通过环境变量 `SKBUILD_CMAKE_ARGS` 传递额外 CMake 参数

* **FR-4c**: scikit-build-core 正确配置构建流程：`build-backend = "scikit_build_core.build"`，支持 sdist 和 wheel 构建，编译选项通过 CMakePresets.json 或 `cmake.define` 配置，输出目录遵循 Python wheel 标准布局

* **FR-4d**: 提供 `xs build` 子命令封装构建流程：自动检测项目类型（纯Python/C扩展），纯Python项目使用 `python -m build`，C扩展项目使用 `pip install .` 或 `python -m build` 触发 scikit-build-core + CMake + Ninja 构建链

* **FR-5**: 每个子项目根目录必须包含 README.md（功能说明+使用方法）和 CHANGELOG.md（变更历史）

* **FR-6**: 根目录提供项目导航总览，列出所有子项目及其维护状态（活跃/维护中/归档/实验性）

* **FR-7**: 提供依赖检查脚本（`xs deps check`），检测过时依赖并输出报告，同时验证 Python 3.13 兼容性

* **FR-8**: 提供批量依赖更新脚本（`xs deps update`），支持 dry-run 模式预览变更，支持逐项目升级，支持限制更新类型（major/minor/patch）

* **FR-9**: 版本管理采用独立版本模式，tag 格式为 `&lt;project&gt;@&lt;version&gt;`，通过 `xs version` 辅助版本号和 CHANGELOG 更新

* **FR-10**: 提供受影响项目检测脚本（`xs affected`），根据 Git 变更范围确定需要构建/测试的子项目

* **FR-11**: 提供一键初始化脚本（`xs init`），新成员 clone 后可快速配置开发环境（检查工具链：Python≥3.13、Git、Git LFS、CMake≥3.26、Ninja；推荐安装PDM；安装依赖；配置 hooks）；工具缺失时给出安装指引而非强制失败

* **FR-11a**: 提供 `xs doctor` 子命令，诊断当前环境的工具链状态（Python版本、PDM/uv/pip可用性、CMake/Ninja版本、Sphinx可用性），输出诊断报告和修复建议

* **FR-12**: 根目录必须包含 CONTRIBUTING.md，说明贡献流程、代码规范、PR 要求、Python 版本要求

* **FR-13**: vendor/ 目录仅在需要对第三方库打 patch 时使用，优先通过包管理器引入

* **FR-14**: 二进制大文件必须使用 Git LFS 管理，`.gitattributes` 配置常见二进制格式

* **FR-15**: 提供项目归档机制（`xs archive`），不活跃项目移至 attic/ 目录保留历史但不主动维护

* **FR-16**: 所有批量操作脚本必须是幂等的，支持失败后安全重试

* **FR-17**: 提供 `xs list` 递归发现所有子项目，支持 --json 和 --table 输出格式

* **FR-18**: 提供 `xs py-compat` 子命令，验证指定依赖包与 Python 3.13+ 的兼容性（通过查询 PyPI 元数据或安装测试）

* **FR-19**: 根目录必须包含 AGENTS.md 智能体入口文件，作为 AI 智能体协作的最高优先级路由，包含启动协议、上下文路由表、核心规范入口等内容

* **FR-20**: 根目录必须包含 .agents/ 规范目录，存放角色定义、协作协议、工作流、模板、脚本、Skill 门面等 AI 协作所需的规范资产，结构参考 SpecWeave 项目

* **FR-21**: docs/ 目录必须使用 Sphinx 文档生成工具结合 MyST Markdown 语法进行内容管理，配置正确的 Sphinx 项目结构

* **FR-22**: Sphinx 文档必须支持 Markdown 格式解析（通过 myst-parser），配置必要的扩展（sphinx-design、sphinx-copybutton、sphinxcontrib-mermaid、sphinx-book-theme 等）

* **FR-23**: Sphinx 文档必须能够成功编译为 HTML 等可发布格式，包含清晰的目录结构、导航链接、代码示例和说明文字

* **FR-24**: docs/ 目录包含必要的 Sphinx 配置文件：conf.py、index.md、\_static/ 静态资源目录、\_templates/ 模板目录；文档依赖统一在根 pyproject.toml 的 `[project.optional-dependencies].docs` 中配置，不使用独立的 requirements.txt

* **FR-25**: 根 README.md 与 Sphinx 文档首页内容保持同步，README.md 可通过 MyST include 指令嵌入文档首页

* **FR-26**: 提供 `xs docs build` 和 `xs docs serve` 子命令，支持文档构建和本地预览

* **FR-27**: 提供 C/C++ 原生扩展项目模板（通过 `xs new --type native` 创建），包含正确配置的 pyproject.toml（scikit-build-core后端）、CMakeLists.txt、src/ 目录结构、示例 C++ 扩展代码、测试配置

* **FR-28**: 提供纯 Python 项目模板（通过 `xs new --type python` 创建），包含标准 pyproject.toml（setuptools/hatch后端可选）、src/ 目录结构，不强制依赖 PDM

* **FR-29**: 构建系统支持跨平台：CMake + Ninja + scikit-build-core 在 Windows（MSVC/MinGW）、macOS（Clang）、Linux（GCC/Clang）三大平台上配置正确，编译选项适配各平台（如 Windows 下 `/EHsc`、macOS 下 `-mmacosx-version-min`）

* **FR-30**: 提供 CMakePresets.json 配置预设，定义 debug/release/relwithdebinfo 等标准构建预设，跨平台统一构建入口

* **FR-31**: 提供 `xs toolchain` 子命令管理工具链依赖：检测/安装 CMake、Ninja、scikit-build-core 等构建工具；支持通过 `pip install cmake ninja` 获取 Python 包版本的工具作为 fallback

* **FR-32**: 明确 xuanspace 作为 SpecWeave 项目 git 子模块的存放策略：放置于 `projects/xuanspace/`（SpecWeave 根目录新建 projects/ 目录存放第一方自有子项目），与 vendor/（第三方依赖子模块）形成明确区分

* **FR-33**: 在 SpecWeave 的 AGENTS.md/路由文档中记录 xuanspace 子模块的位置、更新策略（通过 git submodule update --remote）、开发工作流（在子模块内独立开发，通过 PR 更新主仓库引用）

* **FR-34**: 提供跨环境测试验证脚本（`xs test --matrix`），在本地或 CI 中验证构建目标在不同操作系统和 Python 版本下的一致性，确保构建成功率100%

* **FR-35**: 项目中所有 Markdown 文档统一采用 YAML/TOML 内容-元数据二分法格式：YAML frontmatter 仅保留 id/x-toml-ref/source/version 等核心标识和内容配置字段，复杂元数据（title/category/tags/date/changelog/summary）存储于 `.meta/toml/` 镜像路径的外部 TOML 文件中；提供 `xs meta check` 命令验证 frontmatter 格式合规性和 TOML 引用有效性；提供 `xs meta init` 命令为新文档自动创建配套 TOML 元数据文件骨架

## Non-Functional Requirements

* **NFR-1（性能）**: 仓库初始 clone 时间应控制在合理范围；浅克隆（--depth=1）应作为推荐选项；增量构建脚本应能在秒级确定受影响项目；Sphinx 文档全量构建应控制在 30 秒内

* **NFR-2（可扩展性）**: 目录结构支持按语言/领域分子目录分组（如 libs/python/、libs/ai/、apps/culture/）；脚本不硬编码项目列表，支持递归自动发现；Sphinx 文档支持按子项目自动生成 API 文档

* **NFR-3（可维护性）**: 所有脚本必须有清晰注释和 --help 文档；目录分类标准必须有明确文档；AGENTS.md 和 .agents/ 目录内容与项目实际状态保持同步

* **NFR-4（可靠性）**: 批量更新脚本必须支持 dry-run；失败时提供清晰的回滚指引；所有批量操作在 Git 分支上执行，成功后再合并；Sphinx 文档构建无警告和错误；CMake 构建失败时输出清晰的错误定位（哪个子项目、哪个编译单元、什么错误）

* **NFR-5（可发现性）**: 根目录 README 必须有项目索引表格，包含名称、描述、语言、状态、最新版本、文档链接；Sphinx 文档包含清晰的 toctree 导航和搜索功能

* **NFR-6（工具最小依赖）**: 核心工具链基于 PEP 517/621 标准（pyproject.toml），不绑定单一包管理器；PDM 为推荐 workspace 工具，uv/pip 为兼容替代；CMake+Ninja+scikit-build-core 仅在有 C/C++ 扩展的子项目中必需，纯 Python 项目无需安装；Sphinx 扩展选择优先使用成熟稳定的插件

* **NFR-7（Python兼容性）**: 所有 Python 子项目的 `requires-python` 必须设置为 `">=3.13"`；CI 必须在 Python 3.13 上运行测试；新引入依赖必须验证 3.13 兼容性；Sphinx 及相关扩展必须兼容 Python 3.13；scikit-build-core、CMake、Ninja 必须兼容 Python 3.13

* **NFR-8（文档质量）**: 所有技术文档必须符合技术文档编写规范，包含必要的目录结构、导航链接、代码示例和说明文字；代码示例必须可运行；文档内容需经过拼写检查和链接验证

* **NFR-9（跨平台一致性）**: 构建脚本和配置在 Windows/macOS/Linux 三大平台上行为一致；CMake 配置避免硬编码平台特定路径；路径分隔符使用 CMake 内置变量或 Python pathlib 处理；CI 至少覆盖 Linux + Windows 双平台测试

* **NFR-10（构建可重现性）**: CMake 构建使用预设（CMakePresets.json）确保相同配置产生相同结果；构建依赖版本锁定（scikit-build-core、ninja、cmake 版本在 dev 依赖中指定）；不依赖系统全局安装的库版本

## Constraints

* **Technical**:

  * 基于 Git + GitHub 生态

  * Python 版本要求：**>=3.13**（严格要求，不兼容 3.12 及以下）

  * 包管理器：PDM ≥ 2.10 为推荐 workspace 工具（非强制），需兼容 uv/pip 等 PEP 517 工具

  * 脚本使用 Python (typer+dataclass) 实现跨平台 CLI（工具名 `xs`）

  * C/C++ 扩展构建：CMake ≥ 3.26、Ninja（首选生成器）、scikit-build-core ≥ 0.10

  * 不依赖 Bazel/Buck 等重型通用构建系统

  * 作为 SpecWeave 的 git 子模块，存放于 projects/xuanspace/

* **Business**:

  * 所有项目默认公开开源（MIT 或兼容协议）

  * 面向个人开发者和小团队协作，无需复杂权限系统

* **Dependencies**:

  * Git ≥ 2.30（支持 sparse-checkout、submodules 等现代特性）

  * Python ≥ 3.13

  * PDM ≥ 2.10（推荐，完善的 Python 3.13 + workspace 支持）

  * uv ≥ 0.4（可选替代包管理器，快速安装）

  * CMake ≥ 3.26（原生扩展构建必需）

  * Ninja（CMake 生成器，跨平台快速构建）

  * scikit-build-core ≥ 0.10（PEP 517 CMake 构建后端）

  * build ≥ 1.2（标准 Python 构建前端，`python -m build`）

  * Node.js ≥ 18（如需管理 JS 子项目，使用 pnpm；可选）

  * Git LFS（用于二进制文件）

  * Sphinx ≥ 8.0 + MyST-Parser ≥ 4.0（文档生成）

  * sphinx-book-theme ≥ 1.1（文档主题）

## Assumptions

* 所有子项目均为公开开源项目，无私有代码混合（若未来需要私有项目，将通过 submodule 或独立仓库方式引入）

* 初始阶段子项目数量在 20 个以内，当前架构可平滑扩展

* 用户主要技术栈为 Python 3.13+，但不排除其他语言项目（如纯 HTML/JS 项目竹简悟道，以及 C/C++ 原生扩展项目）

* 贡献者具备基本的 Git 和 GitHub 使用能力

* GitHub Actions 作为 CI/CD 基础平台

* 竹简悟道这类纯静态 HTML 项目直接放入 apps/，不需要 PDM/CMake 管理，但需遵循目录和文档规范

* 大多数子项目为纯 Python 包，不需要 CMake；CMake+Ninja+scikit-build-core 仅用于有 C/C++ 扩展的子项目

* CMake 和 Ninja 可通过系统包管理器（apt/brew/choco）或 pip 安装（pip install cmake ninja），xs toolchain 命令提供 fallback 安装

* xuanspace 初期在 SpecWeave 内开发，通过 git submodule 放置于 projects/xuanspace/，成熟后可独立推送至 GitHub

## Acceptance Criteria

### AC-1: 标准目录结构已建立

* **Given**: 仓库初始化完成

* **When**: 查看根目录结构

* **Then**: 存在 apps/、libs/、vendor/、tools/、docs/、scripts/、attic/、.agents/ 目录，以及 AGENTS.md、README.md 文件；每个顶层目录有 README.md 说明用途和准入标准（.agents/ 除外，由 AGENTS.md 路由）

* **Verification**: `programmatic`

* **Notes**: 通过目录检查和文件存在性验证；.agents/ 是隐藏目录用于 AI 协作规范

### AC-2: 标准 pyproject.toml 与 Python 3.13 配置正确

* **Given**: 根目录有 pyproject.toml

* **When**: 查看配置并使用不同包管理器安装

* **Then**: `requires-python = "&gt;=3.13"` 已设置；pyproject.toml 符合 PEP 621 标准；使用 `pdm install` 时 workspace 包自动链接；使用 `pip install -e .` 时纯 Python 包可正确安装；使用 `uv pip install -e .` 时可快速安装；Python 版本不满足时所有包管理器均给出明确错误

* **Verification**: `programmatic`

* **Notes**: 创建示例纯 Python 子项目验证三种安装方式；在 Python 3.12 环境下测试应给出版本不满足提示

### AC-3: 子项目文档完整

* **Given**: 子项目已添加到仓库

* **When**: 查看任意子项目根目录

* **Then**: 包含 README.md（功能/安装/使用示例）、CHANGELOG.md（版本历史）、明确的维护状态徽章

* **Verification**: `human-judgment`

* **Notes**: 通过模板强制 + 检查脚本验证

### AC-4: 根目录导航清晰

* **Given**: 仓库根目录

* **When**: 打开 README.md

* **Then**: 包含"玄境"品牌介绍与设计理念（呼应《老子》"玄之又玄"）、项目索引表格（名称/描述/语言/状态/版本/文档链接）、5 分钟快速开始指南、Mermaid 架构图、贡献指南入口

* **Verification**: `human-judgment`

### AC-5: 依赖检查与 Python 3.13 兼容性脚本可用

* **Given**: 项目已配置依赖

* **When**: 运行 `xs deps check` 和 `xs py-compat`

* **Then**: `xs deps check` 输出过时依赖列表按子项目分组；`xs py-compat` 验证依赖与 Python 3.13 的兼容性，标记不兼容的包

* **Verification**: `programmatic`

### AC-6: 批量更新脚本支持 dry-run

* **Given**: 存在过时依赖

* **When**: 运行 `xs deps update --dry-run`

* **Then**: 显示将要执行的变更但不实际修改文件；无 --dry-run 时执行更新并生成变更摘要

* **Verification**: `programmatic`

### AC-7: 版本管理工作流

* **Given**: 子项目有变更需要发布

* **When**: 运行 `xs version` 并按流程操作

* **Then**: 自动更新版本号、生成 CHANGELOG 条目、创建 Git tag 格式为 `&lt;project&gt;@&lt;version&gt;`

* **Verification**: `programmatic`

### AC-8: 受影响项目检测准确

* **Given**: 修改了某个 lib 子项目的代码

* **When**: 运行 `xs affected`

* **Then**: 正确列出依赖该 lib 的所有子项目，以及该 lib 自身

* **Verification**: `programmatic`

### AC-9: 贡献指南完整

* **Given**: 新贡献者查看仓库

* **When**: 打开 CONTRIBUTING.md

* **Then**: 包含环境搭建步骤（含 Python 3.13 安装指引）、分支策略、PR 提交流程、代码规范、Commit message 规范、新增子项目流程

* **Verification**: `human-judgment`

### AC-10: 初始化与诊断脚本可用

* **Given**: 新成员完成 git clone

* **When**: 运行 `xs init` 和 `xs doctor`

* **Then**: `xs init` 检查 Python ≥3.13、Git、Git LFS、CMake（如需要）、Ninja（如需要）是否安装；推荐但不强制安装 PDM；自动安装依赖；配置 Git hooks；提示下一步操作；`xs doctor` 输出完整环境诊断报告（工具版本、可用性、修复建议）

* **Verification**: `programmatic`

### AC-11: 目录分类标准明确

* **Given**: 开发者需要添加新子项目

* **When**: 查看各顶层目录的 README.md

* **Then**: 清楚了解 apps/ vs libs/ vs tools/ vs vendor/ 的区别和准入标准；知道纯 HTML/JS 项目（如竹简悟道）应如何放置

* **Verification**: `human-judgment`

### AC-12: 可扩展性设计

* **Given**: 子项目数量增长到需要分组

* **When**: 在 libs/ 下创建子目录（如 libs/python/、libs/ai/）或在 apps/ 下分组（如 apps/culture/）

* **Then**: 所有脚本仍然正常工作，支持递归自动发现子项目

* **Verification**: `programmatic`

### AC-13: CLI 工具 xs 基础命令可用

* **Given**: 项目初始化完成

* **When**: 运行 `xs --help`、`xs list`、`xs list --json`

* **Then**: 帮助信息完整；list 正确列出所有子项目；--json 输出有效 JSON

* **Verification**: `programmatic`

### AC-14: AGENTS.md 智能体入口文件完整

* **Given**: 仓库根目录

* **When**: 打开 AGENTS.md

* **Then**: 包含启动协议（步骤1-4）、上下文路由表、核心规范入口表、快速开始一句话装载指引、开发规范要点；作为 AI 智能体的最高优先级入口

* **Verification**: `human-judgment`

### AC-15: .agents/ 规范目录结构正确

* **Given**: 仓库根目录

* **When**: 查看 .agents/ 目录结构

* **Then**: 包含必要的子目录结构（rules/、templates/、prompts/、protocols/、commands/、skills/ 等核心模块）；内容与 xuanspace 项目特性匹配，不是简单复制 SpecWeave 的全部内容

* **Verification**: `human-judgment`

### AC-16: Sphinx 文档项目配置正确

* **Given**: docs/ 目录已配置

* **When**: 查看 docs/conf.py 并运行 `xs docs build`

* **Then**: conf.py 正确配置 myst\_parser、sphinx-book-theme、sphinx-design、sphinx-copybutton、sphinxcontrib-mermaid 等扩展；source\_suffix 支持 .md；MyST 扩展启用 dollarmath、amsmath、deflist、colon\_fence 等；`xs docs build` 成功生成 HTML 无错误

* **Verification**: `programmatic`

### AC-17: Sphinx 文档结构与导航清晰

* **Given**: docs/ 目录

* **When**: 查看 docs/index.md 并构建文档

* **Then**: 包含清晰的 toctree 导航（快速开始、用户指南、API 参考、贡献指南等章节）；根 README.md 通过 MyST include 嵌入首页；文档包含代码示例且可运行；搜索功能正常

* **Verification**: `human-judgment`

### AC-18: 文档构建与预览命令可用

* **Given**: 项目初始化完成

* **When**: 运行 `xs docs build` 和 `xs docs serve`

* **Then**: `xs docs build` 成功构建 HTML 到 docs/\_build/html/；`xs docs serve` 启动本地 HTTP 服务器可预览文档；构建过程无警告和错误

* **Verification**: `programmatic`

### AC-19: 文档内容质量符合规范

* **Given**: 文档已编写完成

* **When**: 人工审核文档内容

* **Then**: 包含必要的目录结构、导航链接、代码示例和说明文字；代码示例可运行；链接有效无断链；术语一致；风格统一

* **Verification**: `human-judgment`

### AC-20: C/C++ 原生扩展构建（scikit-build-core + CMake + Ninja）正常工作

* **Given**: 使用 `xs new --type native` 创建了一个示例 C++ 扩展子项目

* **When**: 在项目目录中运行 `pip install .` 或 `xs build`

* **Then**: scikit-build-core 正确调用 CMake（使用 Ninja 生成器），C++ 代码编译成功，wheel 打包正确，安装后可在 Python 中 import 并调用 C++ 扩展函数；构建产物遵循 wheel 标准布局

* **Verification**: `programmatic`

* **Notes**: 创建一个包含 pybind11 绑定的最小 C++ 扩展示例验证

### AC-21: 纯 Python 项目不强制依赖 PDM 或 CMake

* **Given**: 创建了一个纯 Python 子项目（使用 `xs new --type python`），环境中未安装 PDM 和 CMake

* **When**: 使用 `pip install -e .` 安装项目

* **Then**: 安装成功，无需 PDM 或 CMake；项目使用标准 pyproject.toml（setuptools 或 hatch 后端）

* **Verification**: `programmatic`

### AC-22: uv 包管理器兼容

* **Given**: 环境中安装了 uv（未安装 PDM）

* **When**: 运行 `uv pip install -e .` 和 `uv run xs --help`

* **Then**: 依赖安装成功；xs CLI 工具可正常运行

* **Verification**: `programmatic`

### AC-23: 跨平台构建一致性

* **Given**: 同一个 C++ 扩展子项目

* **When**: 分别在 Windows、Linux（WSL/Ubuntu）、macOS 环境中执行构建

* **Then**: 构建均成功，wheel 文件名包含正确的平台标签；C++ 扩展功能行为一致；CMakePresets.json 预设在三平台均可正常使用

* **Verification**: `programmatic`

* **Notes**: 初期至少验证 Windows 和 Linux 双平台

### AC-24: xs build 和 xs toolchain 命令可用

* **Given**: 项目初始化完成

* **When**: 运行 `xs build`、`xs build --help`、`xs toolchain check`、`xs toolchain install cmake`

* **Then**: `xs build` 自动检测项目类型并触发正确构建流程；`xs toolchain check` 输出工具链状态；`xs toolchain install` 可通过 pip 安装缺失工具（cmake、ninja）

* **Verification**: `programmatic`

### AC-25: 项目模板正确生成

* **Given**: 初始化完成的仓库

* **When**: 运行 `xs new --type python mypkg` 和 `xs new --type native myext`

* **Then**: 生成的项目结构包含正确的 pyproject.toml（正确的 build-backend、requires-python）、README.md、CHANGELOG.md、src/ 目录结构、测试配置；原生项目额外包含 CMakeLists.txt 和 CMakePresets.json；生成的项目可立即安装和运行

* **Verification**: `programmatic`

### AC-26: xuanspace 作为 SpecWeave 子模块位置正确

* **Given**: xuanspace 项目已初始化

* **When**: 查看 SpecWeave 项目结构

* **Then**: xuanspace 通过 git submodule 放置于 `projects/xuanspace/`；SpecWeave 的 AGENTS.md 或相关路由文档中记录了子模块位置、更新策略和开发工作流；`git submodule update --init projects/xuanspace/` 可正确拉取

* **Verification**: `programmatic` + `human-judgment`

* **Notes**: projects/ 目录为第一方自有子项目目录（与 vendor/ 第三方依赖区分）；xuanspace 是首个放入 projects/ 的第一方子模块

### AC-27: CONTRIBUTING.md 包含非 PDM 环境说明

* **Given**: 贡献者未安装 PDM

* **When**: 阅读 CONTRIBUTING.md

* **Then**: 包含 PDM、uv、pip 三种安装方式的说明；包含 CMake/Ninja 工具链安装说明（分平台）；包含纯 Python 项目和 C++ 扩展项目的不同构建流程

* **Verification**: `human-judgment`

## Open Questions

* [ ] 初始阶段需要迁移哪些现有项目到玄境 monorepo？（不阻塞架构搭建，但影响后续迁移任务）

* [ ] 是否需要 Node.js 子项目支持（决定是否配置 pnpm workspace）？

* [ ] 维护状态徽章的具体标准定义（活跃/维护中/归档/实验性的判断标准）？

* [ ] 是否需要在根 README 中加入《老子》"玄之又玄"的设计理念阐述段落？

* [ ] 纯 Python 子项目的默认构建后端选择：setuptools（成熟稳定）vs hatch（现代推荐）vs pdm-backend（PDM生态）？初始建议 setuptools 以获得最大兼容性

* [ ] C++ 扩展示例项目使用 pybind11 还是 nanobind？（nanobind 更现代但生态较新，pybind11 更成熟）

