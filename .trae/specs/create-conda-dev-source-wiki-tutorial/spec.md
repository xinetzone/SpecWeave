# conda-dev/conda 源码 + conda-docs 文档 Wiki 教程 - Spec

## Why
`conda` 是 Python 数据科学生态的核心包管理与环境管理工具（本地镜像位于 `external/libs/conda-dev/conda`），其源码是理解包管理器内部机理、求解器（solver）、环境隔离、虚拟包（virtual packages）、插件体系（plugins）等关键机制的权威范本；`conda-docs`（本地镜像 `external/libs/conda-dev/conda-docs`）则是 conda.io 官方文档站点的 Sphinx 源码。当前知识库对 conda 的沉淀仅覆盖了 `.github` 元仓库治理（`conda-dev-github-wiki`），**尚未系统梳理 conda 源码本身的架构、模块、公开 API 与文档构建机制**。

本教程旨在填补这一空白：通过对两个文件夹的逐文件学习与事实采集，将 conda 源码的分层架构、11 个核心包模块、公开 Python API、典型使用场景、常见问题与最佳实践沉淀为通俗易读、适合不同技术水平的 wiki 教程。

## What Changes
- **新增** 11 个原子化 Markdown 文档，构成完整的 conda 源码与文档 wiki 教程，放置于 `.agents/docs/knowledge/learning/08-systems-infrastructure/conda-dev-source-wiki/` 目录
- **新增** 教程总览与导航索引（`00-overview.md`），含 Mermaid 分层架构定位图与学习路径
- **新增** 整体架构章节（`01-architecture.md`），说明 `conda` 源码分层架构、`conda-docs` 文档架构及二者关系
- **新增** 核心模块章节（`02-core-modules.md`），覆盖 `base`/`common`/`models`/`core` 及根级模块（`api`/`resolve`/`exports`/`activate` 等）
- **新增** CLI 命令层章节（`03-cli-commands.md`），覆盖 `cli/` 下 `main_*.py` 命令注册与分发体系
- **新增** 网关与扩展章节（`04-gateways-plugins-env.md`），覆盖 `gateways`/`plugins`/`env`/`notices`/`auxlib`/`shell`
- **新增** 关键 API 章节（`05-key-apis.md`），含 conda Python API、`MatchSpec`/`PrefixData`/`SubdirData`/`Context`/`History` 等用法与 conda-docs 构建扩展 API
- **新增** 典型应用场景章节（`06-scenarios.md`），含环境创建/包安装/求解器/虚拟包/插件/自定义命令等示例
- **新增** 常见问题解决章节（`07-faq.md`）
- **新增** 最佳实践章节（`08-best-practices.md`）
- **新增** 术语表与参考资料章节（`09-resources.md`）
- **新增** `README.md` 教程入口
- **不修改** 目标仓库 `external/libs/conda-dev/conda` 与 `external/libs/conda-dev/conda-docs` 的任何内容（只读学习，不写回第三方依赖）

## Impact
- **Affected specs**: 无（独立新增 wiki 教程，不修改已有 spec）
- **Affected code**: 无代码改动，仅文档新增
- **Affected files**:
  - 新增：`.agents/docs/knowledge/learning/08-systems-infrastructure/conda-dev-source-wiki/` 下 11 个文件（`00-overview.md` ~ `09-resources.md` + `README.md`）
  - 可能由 `docgen-cmd` 后续自动纳入 Learning Wiki 索引（不在本 spec 范围内）
- **Related wikis**:
  - [conda-dev-github-wiki](../08-systems-infrastructure/conda-dev-github-wiki/00-overview.md) — 同属 conda-dev 主题，聚焦 `.github` 组织治理，与本教程（源码架构）互补

## Background & Context
`conda` 采用分层架构：`base`（基础常量与上下文）→ `common`（跨平台工具：路径/序列化/配置/URL/signal）→ `models`（数据模型：`Channel`/`Dist`/`MatchSpec`/`PackageRecord`/`Version`）→ `core`（核心业务：索引/求解/链接/前缀数据/子目录数据/包缓存）→ `gateways`（I/O 网关：HTTP/FTP/S3/LocalFS 适配器、磁盘、子进程、repodata）→ `cli`（命令层）→ `plugins`（插件体系：hookspec 与默认实现）。`conda-docs` 则是一个独立的 Sphinx 文档站点仓库，通过 `.rst` + `conf.py` 构建 conda.io 文档。

本教程以本地 `external/libs/conda-dev/conda`（源码）与 `external/libs/conda-dev/conda-docs`（文档）为事实来源，逐目录核实后撰写，采用七概念方法论中的"知识沉淀链路（R→I→E）"：先事实采集（R，记录目录结构与模块职责），再架构洞察（I，提炼分层与设计意图），最后萃取为 wiki（E，原子化文档），保证内容专业、准确、可追溯。

## ADDED Requirements

### Requirement: 教程总览与导航
The system SHALL provide a `00-overview.md` file containing the tutorial overview, target audience, reading path, chapter navigation table, and a Mermaid diagram positioning the conda codebase layered architecture.

#### Scenario: 用户访问教程入口
- **WHEN** 用户打开 `00-overview.md`
- **THEN** 文档包含：教程简介、章节导航表（00-09 + README）、Mermaid 分层架构定位图、目标读者说明（区分初学者/进阶/源码研究者三级）、学习路径建议、与 conda-dev-github-wiki 的关联指引

### Requirement: 整体架构文档
The system SHALL provide a `01-architecture.md` file explaining the complete layered architecture of the `conda` source, the `conda-docs` documentation structure, and the relationship between the two folders.

#### Scenario: 用户理解全貌
- **WHEN** 用户阅读 `01-architecture.md`
- **THEN** 文档包含：`conda` 源码完整目录树（11 个包 + 根级模块）、分层依赖关系说明、`conda-docs` 目录树（`docs/source` + `conf.py` + 扩展）、`conda` 内嵌 `docs/` 与独立 `conda-docs` 的关系/差异、Mermaid 分层图

### Requirement: 核心模块文档
The system SHALL provide a `02-core-modules.md` file explaining the foundational packages (`base`/`common`/`models`/`core`) and root-level modules.

#### Scenario: 用户学习核心模块
- **WHEN** 用户阅读 `02-core-modules.md`
- **THEN** 文档覆盖：`base`（`constants.py`/`context.py`）、`common`（`path`/`serialize`/`configuration`/`signals`/`toposort`/`url`）、`models`（`channel`/`match_spec`/`records`/`version`/`prefix_graph`/`package_info`）、`core`（`solve`/`index`/`link`/`prefix_data`/`subdir_data`/`package_cache_data`）、根级模块（`api.py`/`resolve.py`/`exports.py`/`activate.py`/`deprecations.py`/`exceptions.py`/`history.py`），每项含职责说明与关键符号

### Requirement: CLI 命令层文档
The system SHALL provide a `03-cli-commands.md` file explaining the `cli/` command layer, command registration, and dispatch mechanism.

#### Scenario: 用户学习 CLI 命令体系
- **WHEN** 用户阅读 `03-cli-commands.md`
- **THEN** 文档覆盖：`cli/main.py` 入口与 `conda_argparse.py`/`condarc.py`/`common.py`/`find_commands.py`、`main_*.py` 各命令（install/create/remove/list/search/update/env/config/info/clean/run/export/notices 等）、`conda run`/`conda activate` 等命令的注册与分发流程、命令与 `core`/`gateways` 的调用关系

### Requirement: 网关与扩展文档
The system SHALL provide a `04-gateways-plugins-env.md` file explaining the I/O gateways, plugin system, env management, notices, auxlib, and shell integration.

#### Scenario: 用户学习网关与插件
- **WHEN** 用户阅读 `04-gateways-plugins-env.md`
- **THEN** 文档覆盖：`gateways`（`connection/adapters`（http/ftp/s3/localfs）、`disk`、`subprocess`、`repodata`、`shards`）、`plugins`（`hookspec` + 默认 impl：`virtual_packages`/`subcommands`/`solvers`/`reporter_backends`/`package_extractors`/`prefix_data_loaders`）、`env`（`specs`/`installers`）、`notices`、`auxlib`、`shell`（激活脚本）

### Requirement: 关键 API 文档
The system SHALL provide a `05-key-apis.md` file documenting key public Python APIs with usage examples, and the conda-docs build/extension APIs.

#### Scenario: 用户使用关键 API
- **WHEN** 用户阅读 `05-key-apis.md`
- **THEN** 文档包含（每项含签名、参数说明、可运行代码示例）：`conda.api`（`create`/`install`/`remove`/`update`/`Solver`）、`MatchSpec`/`Channel`/`Version` 的构造与匹配、`PrefixData`/`SubdirData`/`PackageCacheData` 的查询、`Context` 配置读取、`History` 历史记录、`conda.exports` 重导出入口、以及 `conda-docs` 的 Sphinx 扩展（`_extensions/conda_umls.py`/`nav_glossary.py`）与 `conf.py` 配置要点

### Requirement: 典型应用场景文档
The system SHALL provide a `06-scenarios.md` file with typical application scenarios and runnable examples.

#### Scenario: 用户参考应用场景
- **WHEN** 用户阅读 `06-scenarios.md`
- **THEN** 文档包含（每场景含背景/步骤/示例/预期结果）：①程序化环境创建与包安装（`conda.api`）；②MatchSpec 匹配与依赖解析；③自定义子目录数据（SubdirData）与 solv 索引；④虚拟包（virtual package）与 CUDA/archspec 检测；⑤插件子命令开发（hookspec）；⑥conda-docs 本地构建与文档贡献；⑦channel/adapter 自定义下载

### Requirement: 常见问题解决文档
The system SHALL provide a `07-faq.md` file listing common problems and solutions.

#### Scenario: 用户排查问题
- **WHEN** 用户阅读 `07-faq.md`
- **THEN** 文档包含（每问含现象/原因/解决步骤）：求解器冲突（Solver/unsatisfiable）、通道优先级与 `channel_priority`、conda 与 pip 混用环境污染、代理与网络（`ssl_verify`/`proxy_servers`）、权限与文件锁、激活脚本失效、插件/hookspec 兼容、文档构建报错等 ≥8 条常见问题

### Requirement: 最佳实践文档
The system SHALL provide a `08-best-practices.md` file distilling reusable practices and anti-patterns.

#### Scenario: 用户借鉴最佳实践
- **WHEN** 用户阅读 `08-best-practices.md`
- **THEN** 文档包含：环境管理最佳实践（命名/隔离/复现）、通道与求解器配置建议、程序化调用 conda API 的健壮性建议、插件开发规范、conda 源码贡献（测试/类型标注/`news/` 片段）、conda-docs 写作规范、≥3 个反模式与规避方式

### Requirement: 术语表与参考资料文档
The system SHALL provide a `09-resources.md` file with a glossary and authoritative references.

#### Scenario: 用户深入学习
- **WHEN** 用户阅读 `09-resources.md`
- **THEN** 文档包含：术语表（≥15 条：package/channel/subdir/NOTICE/MatchSpec/prefix/solver/virtual package/hookspec/repodata/condarc/environment.yml 等）、权威参考资料链接（conda 官方文档、conda GitHub 仓库、conda-docs、CEP 规范）、按难度分级的扩展阅读建议

### Requirement: 文档元数据与导航规范
The system SHALL ensure all wiki files follow consistent metadata and navigation conventions matching the existing `conda-dev-github-wiki` pattern.

#### Scenario: 验证文档元数据
- **WHEN** 检查任意 wiki 文件 frontmatter
- **THEN** 包含完整 YAML frontmatter 字段：`id`、`title`、`source`（值为 `spec:create-conda-dev-source-wiki-tutorial`）、`category`（值为 `learning`）、`tags`、`date`、`status`、`author`、`summary`

#### Scenario: 验证双向导航
- **WHEN** 检查分章文档（01-08）
- **THEN** 每个文档底部包含双向导航：上一章、返回目录（`00-overview.md`）、下一章

## Non-Functional Requirements
- **NFR-1**: 每个原子文档不超过 350 行，遵循单一职责原则
- **NFR-2**: 技术术语与模块/API 名称准确，所有解析基于本地仓库文件事实（`external/libs/conda-dev/conda` 与 `conda-docs`），禁止臆造未验证的符号与函数签名
- **NFR-3**: 语言通俗易懂、由浅入深，适合不同技术水平读者（初学者侧重概念与场景，进阶/源码研究者侧重架构与 API）
- **NFR-4**: 所有内部链接使用相对路径，无 `file:///` 绝对路径，通过链接检查
- **NFR-5**: 代码示例标注语言类型（python/bash/yaml/mermaid），示例可运行或明确标注为"示意"
- **NFR-6**: 遵循项目文档命名规范（kebab-case，数字前缀排序）

## Constraints
- **Technical**: 使用 Markdown + Mermaid 图表，遵循项目现有 wiki 格式（参考 `08-systems-infrastructure/conda-dev-github-wiki/` 结构）
- **Business**: 教程聚焦 conda 源码架构与文档构建可复用知识，与 conda-dev 主题下 `.github` wiki 形成互补
- **Dependencies**:
  - 依赖本地仓库 `external/libs/conda-dev/conda` 与 `conda-docs` 的只读事实来源
  - 依赖项目现有知识库结构与链接检查工具

## Assumptions
- 读者具备基础 Python 与包管理概念（环境/包/依赖），部分章节面向有用源码研究需求的读者
- 教程放置于 `.agents/docs/knowledge/learning/08-systems-infrastructure/conda-dev-source-wiki/` 目录
- 完成后可由 `docgen-cmd` 自动纳入 Learning Wiki 索引（不在本 spec 验收范围内）

## Acceptance Criteria

### AC-1: 目录结构完整
- **Given**: 教程创建完成
- **When**: 查看目标目录
- **Then**: 包含 `00-overview.md` ~ `09-resources.md` + `README.md` 共 11 个文件，每个原子文档 < 350 行
- **Verification**: `programmatic`

### AC-2: 模块覆盖完整
- **Given**: 教程完成
- **When**: 阅读 `02` ~ `04` 章节
- **Then**: 覆盖 `conda` 源码全部主要包（base/common/models/core/cli/gateways/plugins/env/notices/auxlib/shell）与根级关键模块
- **Verification**: `human-judgment`

### AC-3: 内容准确可追溯
- **Given**: 全部章节中的模块名/API/签名引用
- **When**: 对照本地仓库 `external/libs/conda-dev/conda` 与 `conda-docs` 逐项核对
- **Then**: 每个被引用的模块名、函数签名、参数与本地仓库一致，无臆造
- **Verification**: `programmatic`（抽样核对）

### AC-4: 含 Mermaid 图
- **Given**: 教程完成
- **When**: 检索 Mermaid 代码块
- **Then**: 至少包含 2 处 Mermaid 图（00-overview 分层定位图、01-architecture 分层依赖图）
- **Verification**: `programmatic`

### AC-5: 元数据规范
- **Given**: 所有 11 个文档
- **When**: 检查 frontmatter
- **Then**: 每个文档 `source` 字段值为 `spec:create-conda-dev-source-wiki-tutorial`，`category` 为 `learning`
- **Verification**: `programmatic`

### AC-6: 六大要素齐备
- **Given**: 教程完成
- **When**: 检查章节映射
- **Then**: 六大要素均有对应章节——整体架构（01）、子模块功能（02/03/04）、关键 API（05）、应用场景（06）、常见问题（07）、最佳实践（08）
- **Verification**: `human-judgment`

### AC-7: 链接有效
- **Given**: 教程完成
- **When**: 运行链接检查
- **Then**: 所有内部相对路径链接有效，无 `file:///` 绝对路径断链
- **Verification**: `programmatic`

### AC-8: 示例可复现
- **Given**: `05-key-apis.md` 与 `06-scenarios.md`
- **When**: 阅读示例
- **Then**: 代码示例语言标注正确、逻辑自洽（可运行或明确标注示意）
- **Verification**: `human-judgment`

## Open Questions
- [ ] 是否需将 `conda` 内嵌 `docs/source/dev-guide`（架构/求解器深度剖析）单独成章，还是并入 `01-architecture.md` 与 `05-key-apis.md`？
- [ ] 教程是否需要覆盖 `conda-docs` 与 `conda` 内嵌 `docs` 的历史演进关系，还是仅描述当前状态（默认：仅当前状态，标注差异即可）？