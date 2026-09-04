# Jira Skill Wiki 供应商源码同步更新 - 产品需求文档

## Overview

- **Summary**: 基于已迁移至 `vendor/jira-skill`（v3.29.0, commit b0dba28）的正式 git submodule 源码，更新现有 OKF v0.2 Wiki 教程，修复信源路径失效、frontmatter 格式不合规、事实数字错误、API 文档遗漏等问题。
- **Purpose**: 现有 Wiki 初次生成时以临时克隆 `.chaos/libs/tests/jira-skill/` 为信源，该目录已删除，导致 8 处信源路径断裂；同时 frontmatter 使用了 OKF v0.2 规范之前的 `date:` 块格式而非规范要求的 `at:` inline flow 格式；另有测试文件数、参考文档数、changelog.py API 清单等事实性偏差需校正。
- **Target Users**: 学习 jira-skill 插件的开发者、维护 OKF 知识库的文档协作者、通过 AI 智能体消费 OKF Bundle 的工具链。

## Goals

- 将所有信源路径从已删除的 `.chaos/libs/tests/jira-skill/` 更新为 `vendor/jira-skill/`
- 将全部 17 个带 frontmatter 的文档从块格式 `date:` 修正为 OKF v0.2 inline flow `at:` 格式
- 修正测试文件数（23→25）、参考文档数（16→17）等事实数字
- 补全 api-reference.md 中 changelog.py 遗漏的 4 个公开函数
- 在 source-code.md 中补充 pyproject.toml 的准确说明（仅含 ruff/bandit 配置，依赖通过 PEP 723 声明）
- 更新 log.md 记录本次供应商同步变更
- 所有时间戳更新为本次变更日期
- 通过 V 阶段独立验证（Grep 级 API 真实性、链接完整性、frontmatter 合规性）

## Non-Goals

- 不重写现有文档的正文核心内容（仅做路径修正、格式修正和事实补全）
- 不新增概念文档或示例文档（现有 10+3 篇内容已覆盖 v3.29.0 全部功能点）
- 不修改 vendor/jira-skill 源码（third_party 只读子模块）
- 不改变 Bundle 目录结构（index.md/log.md/concepts/examples/references 保持不变）
- 不升级 jira-skill 版本（固定 v3.29.0）

## Background & Context

- 现有 Wiki 位于 `d:\AI\.agents\docs\knowledge\learning\01-agent-protocols-interfaces\jira-skill-wiki\`，共 22 个 Markdown 文件
- 初次转换规格：`.trae/specs/okf-wiki-ecosystem/jira-skill-okf-wiki/`（已完成，Review R1 通过）
- 源码已从临时克隆迁移为正式 git submodule：`vendor/jira-skill`（v3.29.0 tag, commit b0dba28, 提交 edda3939）
- 临时克隆 `.chaos/libs/tests/jira-skill/` 已删除，`.chaos/jira-skill/` 保留（含用户工作产物，不在本次范围）
- OKF v0.2 规范要求 frontmatter inline flow 格式：`generated: { by: ..., at: ... }`
- 本次更新遵循 source-code-to-okf-wiki 工作流的 V 阶段防护机制（Grep 级 API 验证）

### 已验证事实清单

| 编号 | 事实 | 验证方式 |
|------|------|----------|
| F-01 | 8 处信源路径包含 `.chaos`（source-code.md 3处、api-reference.md 4处、log.md 1处） | Grep 确认 |
| F-02 | 17 个文件使用块格式 `generated:\n  by: ...\n  date: ...`（根 index 仅 generated，其余 16 个含 generated+verified） | Grep 确认 |
| F-03 | tests/ 目录有 24 个 test_*.py + 1 个 conftest.py = 25 个 Python 文件（Wiki 写 23） | Glob 确认 |
| F-04 | jira-communication/references/ 有 17 个 .md 文件（01-architecture.md 写 16 份） | Glob 确认 |
| F-05 | changelog.py 导出 7 个公开函数（Wiki api-reference.md 仅列出 3 个） | Grep `^def ` 确认 |
| F-06 | pyproject.toml 仅 17 行，只含 `[tool.ruff]` 和 `[tool.bandit]` 配置，无 `[project]` 表 | Read 确认 |
| F-07 | no-editorializing.md 和 cross-project-refs.md 内容已在现有概念文档中覆盖（04/07 和 05） | Grep 确认 |
| F-08 | jira-syntax/references/ 有 2 个文件（jira-syntax-quick-reference.md、cross-project-refs.md），Wiki 描述正确 | Glob 确认 |

### changelog.py 函数对照

| 函数签名 | Wiki 当前状态 |
|----------|--------------|
| `parse_jira_datetime(s: str) -> datetime` | 缺失 |
| `extract_status_transitions(issue: dict) -> list[dict]` | 已记录 |
| `compute_time_in_status(...) -> dict[str, timedelta]` | 已记录 |
| `extract_status_transitions_with_authors(issue: dict) -> list[dict]` | 缺失 |
| `classify_transition(transition, status_sets) -> TransitionKind` | 已记录 |
| `find_transition_window(transitions, target_index) -> tuple[datetime \| None, datetime \| None]` | 缺失 |
| `format_timedelta(delta: timedelta) -> str` | 缺失 |

## Functional Requirements

- **FR-1**: 修复 references/source-code.md 中 3 处 `file:///d:/.chaos/libs/tests/jira-skill/` 路径为 `file:///d:/AI/vendor/jira-skill/`
- **FR-2**: 修复 references/api-reference.md 中 4 处 `file:///d:/.chaos/libs/tests/jira-skill/` 路径为 `file:///d:/AI/vendor/jira-skill/`
- **FR-3**: 更新 log.md 第 34 行源码路径从 `d:\AI\.chaos\libs\tests\jira-skill` 为 `d:\AI\vendor\jira-skill`，并新增 2026-08-29 变更记录
- **FR-4**: 将根 index.md 的 frontmatter 从块格式改为 `generated: { by: "source-code-to-okf-wiki", at: "2026-08-29T00:00:00Z" }`
- **FR-5**: 将 16 个内容文档（10 concepts + 3 examples + 3 references）的 frontmatter 从块格式改为 inline flow 格式，`date:` 改为 `at:`，`verified.by` 统一为 `"process:seven-concepts-v"`
- **FR-6**: 修正 source-code.md 第 62 行测试文件数从 "23个测试文件" 为 "24个 test_*.py + conftest.py（共25个 Python 文件）"
- **FR-7**: 修正 01-architecture.md 第 56 行参考文档数从 "16 份" 为 "17 份"
- **FR-8**: 在 api-reference.md 的 changelog.py 部分补全 4 个遗漏函数的签名和简要说明
- **FR-9**: 在 source-code.md 的目录结构或基本信息中补充 pyproject.toml 说明（仅含 ruff/bandit 工具配置，项目依赖通过 PEP 723 内联声明）
- **FR-10**: 所有 17 个文件的 `generated.at` 和 `verified.at` 时间戳更新为 "2026-08-29T00:00:00Z"，`stale_after` 相应顺延一年

## Non-Functional Requirements

- **NFR-1**: 所有变更不得引入虚构 API，补全的函数签名必须与源码逐字一致（Grep 验证）
- **NFR-2**: frontmatter 必须通过 YAML 解析，inline flow 格式无语法错误
- **NFR-3**: 不破坏现有 107 个 bundle-relative 交叉链接（V 阶段回归验证）
- **NFR-4**: 变更遵循"最小必要修改"原则——正文内容除事实修正外不做改写
- **NFR-5**: 使用中文撰写变更记录和新增说明

## Constraints

- **Technical**:
  - 源码目录 `vendor/jira-skill/` 为 third_party 只读子模块，禁止修改
  - 必须遵循 OKF v0.2 frontmatter 规范（inline flow 格式）
  - Windows 平台路径使用正斜杠 in file:/// URLs
  - 输出目录为现有 `jira-skill-wiki/`，不创建新 Bundle
- **Business**:
  - 现有 22 个文件一个不删、一个不增（仅修改内容）
  - 初次转换的 Review R1 已通过的内容（正文、交叉链接、示例）保持不变
- **Dependencies**:
  - vendor/jira-skill submodule 已在 commit b0dba28 初始化（提交 edda3939）
  - OKF v0.2 规范位于 `projects/awesome-okf-xs/doc/bundles/meta/okf-spec/`

## Assumptions

- vendor/jira-skill v3.29.0 与初次转换时的 `.chaos` 克隆指向同一版本（commit b0dba28），API 无差异
- no-editorializing.md 和 cross-project-refs.md 的内容已在概念文档中充分覆盖，无需新增文档
- 用户希望在现有 Bundle 内直接更新，而非创建新版本目录
- `verified.by` 统一为 `"process:seven-concepts-v"` 符合 OKF 规范和 source-code-to-okf-wiki 技能约定

## Acceptance Criteria

### AC-1: 信源路径全部修复

- **Type**: `rule`
- **Given**: 更新后的 jira-skill-wiki 目录
- **When**: Grep 搜索 `.chaos` 字符串
- **Then**: 零匹配结果；所有 `file:///` URL 指向 `d:/AI/vendor/jira-skill/`
- **Pass Condition**: Grep `.chaos` 返回无匹配
- **Evidence**: Grep 搜索结果

### AC-2: Frontmatter 格式合规

- **Type**: `rule`
- **Given**: 全部 17 个带 frontmatter 的 Markdown 文件
- **When**: 检查 YAML frontmatter
- **Then**: 所有 `generated` 和 `verified` 字段使用 inline flow 格式 `{ by: ..., at: ... }`；不存在 `date:` 键；`at` 值为 ISO 8601 格式
- **Pass Condition**: Grep `^  date:` 返回零匹配；Grep `generated: {` 返回 17 匹配
- **Evidence**: Grep 搜索结果

### AC-3: 事实数字准确

- **Type**: `rule`
- **Given**: source-code.md 和 01-architecture.md
- **When**: 检查测试文件数和参考文档数描述
- **Then**: source-code.md 描述测试文件为 25 个 Python 文件（24 test_*.py + conftest.py）；01-architecture.md 描述 jira-communication/references/ 为 17 份
- **Pass Condition**: 两处数字与 Glob 统计一致
- **Evidence**: Read 文件相关行 + Glob 源码统计

### AC-4: changelog.py API 完整

- **Type**: `rule`
- **Given**: api-reference.md 的 changelog.py 部分
- **When**: 对比源码 changelog.py 中 `^def ` 定义的函数
- **Then**: 7 个公开函数全部记录，函数签名与源码逐字一致
- **Pass Condition**: 文档列出的函数集合 == 源码 Grep 结果集合
- **Evidence**: Grep `^def ` changelog.py vs Read api-reference.md

### AC-5: pyproject.toml 描述准确

- **Type**: `rule`
- **Given**: source-code.md 中关于 pyproject.toml 的描述
- **When**: 对比实际 pyproject.toml 内容
- **Then**: 描述准确反映"仅含 ruff/bandit 配置，无 [project] 表，依赖通过 PEP 723 声明"
- **Pass Condition**: 描述中无"项目元数据"等不准确表述
- **Evidence**: Read pyproject.toml vs Read source-code.md

### AC-6: 交叉链接无回归

- **Type**: `rule`
- **Given**: 更新后的全部 Markdown 文件
- **When**: 检查所有 `/` 开头的 bundle-relative 链接
- **Then**: 107 个链接目标文件全部存在
- **Pass Condition**: 零断裂链接
- **Evidence**: 链接检查脚本或手动验证

### AC-7: 无虚构 API

- **Type**: `rule`
- **Given**: 文档中新增或修改的所有函数签名、类名、方法名
- **When**: 在 vendor/jira-skill 源码中 Grep 验证
- **Then**: 每个引用的 API 名称在源码中存在
- **Pass Condition**: 零虚构 API
- **Evidence**: Grep 验证报告

### AC-8: 变更记录完整

- **Type**: `rule`
- **Given**: log.md
- **When**: 检查变更日志
- **Then**: 包含 2026-08-29 日期条目，记录信源路径迁移、frontmatter 格式修正、事实校正、API 补全
- **Pass Condition**: log.md 包含本次变更的日期和内容摘要
- **Evidence**: Read log.md

### AC-9: 内容保留度

- **Type**: `rubric`
- **Dimension**: 现有正文内容的保留程度
- **Scale**: 1-5
- **Anchors**: 1 = 正文被大幅改写或丢失；3 = 核心内容保留但有非必要修改；5 = 正文仅做必要的事实修正，其余原样保留
- **Pass Threshold**: >= 4
- **Evidence**: 对比变更前后 diff
