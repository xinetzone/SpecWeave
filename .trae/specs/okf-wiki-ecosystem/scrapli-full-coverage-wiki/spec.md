---
title: "scrapli 全子文件夹覆盖 OKF Wiki 扩展"
status: "draft"
---

# scrapli 全子文件夹覆盖 OKF Wiki 扩展 Spec

## Why

现有 `comm/networking/scrapli/` 知识束（由 `ssh-python-okf-wiki` Task 7 于 2026-08-23 生成）仅系统学习了 `scrapli/` Python 包的核心模块（133 条事实、14 篇文档）。用户要求学习 `external/libs/scrapli` 下**全部子文件夹**——`examples/`（16 个官方示例目录）、`tests/`（golden 文件测试体系 + Go 编写的 dummy_ssh_server）、`scrapli/definitions/`（44 个平台 YAML，当前仅读 2 个）、`docs/`（含 migration.md 旧版迁移指南）、`.github/`（CI 工作流）尚未覆盖。这些内容包含大量可直接溯源的实战用法与工程实践，是知识束的重要增量。

## What Changes

- **R 阶段扩展**：系统阅读未覆盖子文件夹，新增编号事实（追加至新文件 `scrapli-facts-2.md`，目标 ≥60 条）：
  - `examples/cli/` 12 个示例目录（async_usage、custom_definition、handling_interactions、input_modes、logging_setup、misc_options、output_parsing、proxy_jump_cli、read_callbacks、sending_configs、sending_inputs、session_recorder）+ README.md
  - `examples/netconf/` 4 个示例目录（edit_config、get_operations、proxy_jump_netconf、subscriptions）
  - `tests/functional/`（golden 文件组织方式、conftest.py、test_cli.py/test_netconf.py/test_transport_*.py）与 `tests/unit/`（dummy_ssh_server Go 程序、fixtures）
  - `scrapli/definitions/` 其余 42 个平台 YAML（采样 + 分类归纳，重点读 5-8 个代表性平台）
  - `docs/`（index.md、details.md、installation.md、migration.md、examples/python.md 等）
  - `scrapli/lib/`（README.md——libscrapli 共享库加载说明）
  - `.github/workflows/`（7 个 CI 工作流的检查矩阵）
- **I 阶段扩展**：基于新事实提炼 2-3 条新洞察（更新 `scrapli-insights.md` 或追加至 `scrapli-insights-2.md`），候选方向：golden 文件测试法与 TEST Transport 的闭环设计、官方示例的渐进式教学法、平台定义 YAML 的分类学
- **E 阶段扩展**（扩展现有 `comm/networking/scrapli/` bundle，不新建 bundle）：
  - 新增概念文档 4 篇：09-testing-system（测试体系与 golden 文件法）、10-platform-catalog（44 平台定义分类目录）、11-migration（旧版 scrapli→scrapli2 迁移）、12-repository-examples（官方示例体系解读）
  - 新增示例文档 3 篇：proxy-jump、output-parsing、session-recorder（均源自 examples/ 真实示例改写）
  - 更新 `references/scrapli-source.md`（补充子文件夹覆盖清单与事实数）
  - 最后更新各级 index.md 与 log.md
- **V 阶段**：Grep 验证所有新文档中的类名/方法名/参数；链接完整性检查；`invoke gates.toctrees` 验证
- **C 阶段**：log.md 追加扩展记录；spec 目录保留事实与洞察产物

## Impact

- **Affected specs**: `ssh-python-okf-wiki`（前置依赖，其产出物为本扩展的基础，不修改）
- **Affected code**: 无代码变更；产出物全部位于 `projects/awesome-okf-xs/doc/bundles/comm/networking/scrapli/`（awesome-okf-xs 子项目，git submodule，允许在子项目开发流程内新增文档）
- **不修改**现有 14 篇内容文档（00-08 概念、4 示例、1 信源）——仅追加与更新索引类文件

## ADDED Requirements

### Requirement: 全子文件夹事实采集
系统 SHALL 对 `external/libs/scrapli` 下所有含实质内容的子文件夹（examples/、tests/、docs/、scrapli/definitions/、scrapli/lib/、.github/）进行阅读并提取编号事实，新增事实数 ≥60，事实中不得出现推断性表述。

#### Scenario: R 阶段完成
- **WHEN** 事实采集完成
- **THEN** `.trae/specs/okf-wiki-ecosystem/scrapli-full-coverage-wiki/scrapli-facts-2.md` 存在且含 ≥60 条 F-xxx 事实，每条可溯源至具体源码文件

### Requirement: 测试体系概念文档
系统 SHALL 生成 `concepts/09-testing-system.md`，覆盖 golden 文件测试法、tests/functional 与 tests/unit 结构、dummy_ssh_server（Go）的角色、TransportKind.TEST 传输与测试闭环。

#### Scenario: 文档生成
- **WHEN** E 阶段执行
- **THEN** 文档存在，符合 OKF v0.2 frontmatter，文中引用的测试文件名与 golden 文件名真实存在于源码

### Requirement: 平台定义目录概念文档
系统 SHALL 生成 `concepts/10-platform-catalog.md`，将 44 个平台 YAML 按厂商/家族分类（Cisco 系、Nokia 系、Arista/Juniper 等），归纳共性结构（prompt、modes、on_open、failure_indicators），并列出 definition_options Python 钩子的适用场景。

#### Scenario: 分类完整性
- **WHEN** 文档生成完成
- **THEN** 44 个 YAML 文件全部被提及或归类，数量与 `ls scrapli/definitions/*.yaml` 一致

### Requirement: 迁移指南概念文档
系统 SHALL 生成 `concepts/11-migration.md`，基于 `docs/migration.md` 源码记录旧版 scrapli → scrapli2 的 API 映射关系（Scrapli→Cli、AsyncScrapli→Cli 异步 API、send_command→send_input 等），标注差异与不兼容点。

#### Scenario: 映射准确
- **WHEN** 文档生成完成
- **THEN** 旧版类名标注为"不存在于新版"（与 F-010 一致），新版类名/方法名经 Grep 验证存在

### Requirement: 官方示例体系文档
系统 SHALL 生成 `concepts/12-repository-examples.md`（解读 16 个示例目录的主题矩阵）及 examples/ 下 3 篇新示例文档（proxy-jump、output-parsing、session-recorder），代码示例 SHALL 基于官方示例真实代码改写，API 调用与事实清单一致。

#### Scenario: 示例可溯源
- **WHEN** V 阶段验证
- **THEN** 3 篇示例文档中的 API 调用（如 send_prompted_input、set_recording_path、forward_jump 等）Grep 验证存在于源码

### Requirement: 索引与信源同步更新
系统 SHALL 在所有内容文档定稿后更新：`references/scrapli-source.md`（子文件夹覆盖清单）、`concepts/index.md`、`examples/index.md`、根 `index.md`（文档计数 14→21）、`log.md`（追加 2026-08-28 扩展记录）。

#### Scenario: toctree 完整
- **WHEN** 索引更新完成
- **THEN** `invoke gates.toctrees` 在 awesome-okf-xs 子项目内通过，无断链、无孤立文档

## MODIFIED Requirements

### Requirement: scrapli 知识束覆盖范围
原 `ssh-python-okf-wiki` AC-7 定义 scrapli 知识束为"≥8 概念 + ≥4 示例 + ≥1 信源"。本扩展将其提升为：**13 篇概念（00-12）+ 7 篇示例 + 1 信源**，覆盖仓库全部实质子文件夹。

## REMOVED Requirements

（无——本变更纯增量，不删除任何现有文档）
