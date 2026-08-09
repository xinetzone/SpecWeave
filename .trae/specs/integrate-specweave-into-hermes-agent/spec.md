---
id: "integrate-specweave-into-hermes-agent-spec"
title: "将 SpecWeave 工作区集成到 Hermes Agent 的技术指导文档"
source: "seven-concepts knowledge-scenario: Hermes Agent 插件体系（NousResearch/hermes-agent）+ hermes-okf（EliaszDev/hermes-okf v0.5.9）+ SpecWeave 现状（AGENTS.md / .agents/ 能力体系）"
date: "2026-08-09"
tags: ["Hermes", "hermes-agent", "hermes-okf", "OKF", "集成指南", "插件开发", "SpecWeave", "知识沉淀"]
---

# 将 SpecWeave 工作区集成到 Hermes Agent 的技术指导文档

## Overview
- **Summary**: 系统创建一份原子化的技术指导文档，说明如何将 **SpecWeave 整个工作区**（AGENTS.md 契约、.agents/ 规范体系、skills/commands/scripts/roles、知识库 docs/knowledge、apps/ 应用、vendor/ 子模块）作为能力来源集成到 Hermes Agent 中，使 Hermes 能够正确识别、调用和执行 SpecWeave 的功能。指导同时覆盖两条集成路径：(1) **Hermes Agent 框架本体**——将 SpecWeave 能力注册为 Hermes 插件（tools / skills / memory provider / context engine），(2) **Hermes OKF 记忆层**——将 SpecWeave 知识库作为可持久化、可检索的 OKF memory bundle 挂接到 Hermes 会话。产出物为一份面向 AI 开发者 / Hermes 用户 / 知识工程师的中文技术指导 Wiki，输出到 `.agents/docs/knowledge/learning/03-agent-platforms-tools/hermes-agent-integration/`。
- **Purpose**: 帮助 Hermes Agent 使用者与 SpecWeave 维护者理解"如何把一套成熟的 AGENTS.md + .agents 能力体系（技能/命令/脚本/规范/知识）暴露给外部 Agent 宿主"，并提供可复制、可实操的接口规范、配置清单、数据格式转换、权限认证与调用示例。
- **Target Users**: AI Agent 开发者、Hermes Agent 用户、知识工程师、架构师、SpecWeave 维护者。

## Goals
- 明确 Hermes Agent 的插件接口规范（plugin.yaml / register(ctx) / MemoryProvider ABC / ContextEngine ABC / 发现路径 / 启用机制）
- 明确 Hermes OKF 的挂接方式（install-plugin 自动配置 / memory.provider / OKF bundle 路径 / 会话持久化）
- 给出把 SpecWeave 的 `skills/`、`commands/`、`scripts/`、`roles/`、`AGENTS.md` 契约映射到 Hermes 插件能力（tool / skill / hook）的映射方法与配置示例
- 说明数据格式转换（AGENTS.md/.agents 规范 → plugin.yaml + register(ctx) + tool schema；知识库 markdown → OKF concept/bundle）方法
- 说明权限认证流程（插件发现路径安全、plugin name 消毒、.hermes 目录、HERMES_HOME、API key 环境变量）
- 提供调用方式示例（`hermes plugins install`、`hermes okf ...`、Hermes 内部工具调用、`with_context` 召回）
- 提供集成常见问题及解决方案（发现失败、启用失败、schema 不匹配、Windows 路径、provider 单实例限制等）
- 与既有 hermes-okf-wiki 教程形成互补（彼为基础概念，此为"如何把 SpecWeave 自身接入"的实战指导）

## Non-Goals (Out of Scope)
- 不实现 Hermes Agent 源码或 SpecWeave 内部插件源码（仅提供指导与示例代码）
- 不重写 SpecWeave 现有 .agents/ 规范（仅说明如何暴露/映射到 Hermes）
- 不重复 hermes-okf-wiki 已覆盖的 hermes-okf 全部命令/架构细节（仅聚焦"接入 SpecWeave"相关部分，并做交叉引用）
- 不覆盖其他 Agent 宿主（Claude Code / OpenCode 等）的集成
- 不实际执行 Hermes 安装验证（受网络环境限制，以官方文档与现有知识库为准，标注"示例/验证建议"）

## Background & Context
- Hermes Agent（NousResearch/hermes-agent）是模块化 Agent 框架，插件系统是其扩展核心能力的关键机制；插件分三类：通用插件（General）、内存插件（Memory Provider）、上下文插件（Context Engine）
- 插件发现路径按优先级扫描：官方内置 `/plugins` → 用户插件 `~/.hermes/plugins` → 项目插件 `./.hermes/plugins` → Pip 插件（`hermes_agent.plugins` 入口点）；后加载覆盖同名先加载
- 插件默认禁用，需加入 `plugins.enabled` 允许列表；配置持久化于 `~/.hermes/config.yaml`
- 插件最小结构：`plugin.yaml` + `__init__.py`（register(ctx) 入口）+ 可选 `schemas.py` / `tools.py`；`plugin.yaml` 含 name/version/description/manifest_version
- Hermes OKF（EliaszDev/hermes-okf v0.5.9）是基于 Google OKF 的 Agent 持久记忆系统，`hermes-okf install-plugin` 自动写入 `~/.hermes/config.yaml`（plugins.enabled + memory.provider），可作 Hermes MemoryProvider 插件
- SpecWeave 自身已具备成熟的 AI 能力体系：AGENTS.md 启动协议 + 上下文路由、.agents/ 下 skills/（门面）、commands/（7+ 命令）、scripts/（25+ 脚本）、roles/（7 角色）、knowledge/（学习知识库）、vendor/（flexloop 等子模块技能）
- 项目知识库已有 OKF 生态基础（okf-wiki、hermes-okf-wiki、okf-ecosystem-wiki）与 Agent 平台学习（agency-agents-wiki、echobird-wiki 等），可交叉引用

## Functional Requirements
- **FR-1**: 指导文档采用原子化 wiki 结构（README + 编号章节文件），放置在 `03-agent-platforms-tools/hermes-agent-integration/` 目录
- **FR-2**: 包含 Hermes Agent 插件接口规范详解（插件类型/发现路径/启用机制/plugin.yaml 字段/register(ctx) API/tool schema）
- **FR-3**: 包含 SpecWeave 能力体系盘点与映射方案（skills/commands/scripts/roles/AGENTS.md → Hermes tool/skill/hook/memory provider 的映射矩阵）
- **FR-4**: 包含配置文件设置章节（`~/.hermes/config.yaml` 的 plugins.enabled / disabled / memory.provider / context_engine；HERMES_HOME 环境变量；project 级 `./.hermes/plugins`）
- **FR-5**: 包含数据格式转换方法（AGENTS.md 契约 → plugin.yaml + register(ctx)；知识库 markdown → OKF concept/bundle；tool schema JSON Schema 定义）
- **FR-6**: 包含权限认证流程（插件安装路径安全/name 消毒/manifest_version 校验/HERMES_HOME、API key 环境变量、project 插件权限开启）
- **FR-7**: 包含调用方式示例（`hermes plugins install owner/repo`、`hermes okf ...`、Hermes 会话内工具调用、`with_context` 记忆召回、`hermes memory setup`）
- **FR-8**: 包含常见问题及解决方案（插件未发现/未启用/工具 schema 不匹配/provider 单实例限制/Windows 路径/name 冲突/restart 要求）
- **FR-9**: 交叉引用既有知识（hermes-okf-wiki、okf-wiki、echobird-wiki 等），README 更新上级目录索引（如需要）
- **FR-10**: frontmatter 遵循现有原子化 wiki 格式（id/title/source/description/tags/category/date/status）
- **FR-11**: 所有示例命令与代码标注"示例/需验证"，避免把未实际验证的命令当作已确认事实

## Non-Functional Requirements
- **NFR-1**: 所有内容使用标准现代汉语书面语，专业术语统一（Hermes/plugin/MemoryProvider/OKF/concept/bundle/context engine 首次出现给出解释）
- **NFR-2**: 章节粒度适中，单文件 <300 行（遵循原子化原则）
- **NFR-3**: 代码示例（plugin.yaml / register(ctx) / CLI 命令）完整可复制，标注预期输出或"示例"
- **NFR-4**: 版本提示明确（hermes-agent 插件体系 v2.5.0、hermes-okf v0.5.9，API 可能演进）
- **NFR-5**: 交叉链接正确，文件间引用使用相对路径，禁止 `file:///` 绝对路径
- **NFR-6**: 三级标题使用 x.y 编号格式（1.1、2.3 等，从 x.1 开始）
- **NFR-7**: 不虚构未公开特性；所有命令/字段有官方依据或明确标注为示例

## Constraints
- **Technical**: 输出为纯 Markdown 文件 + YAML frontmatter，无额外依赖
- **Business**: 基于 Hermes Agent 官方插件文档与 hermes-okf 官方文档整理，不虚构；SpecWeave 能力盘点基于当前仓库真实目录
- **Dependencies**:
  - 参考现有 wiki 格式：`okf-wiki/hermes-okf-wiki/`、`okf-wiki/`、`echobird-wiki/`、`agency-agents-wiki/`
  - 资料来源：hermes-okf 官方 Wiki（Quick-Start / Home / 插件体系）、NousResearch/hermes-agent 插件文档、SpecWeave 仓库现状（AGENTS.md / .agents/capability-registry.md / skills / commands / scripts）
  - 输出路径：`.agents/docs/knowledge/learning/03-agent-platforms-tools/hermes-agent-integration/`

## Assumptions
- 输出目录归类在 `03-agent-platforms-tools/` 下是合理的（Hermes 属 Agent 平台/工具）
- 原子化 wiki 结构（而非单文件）更适合内容丰富、章节独立性高的主题
- 现有原子化 wiki 的 frontmatter 格式（含 category/tags/date/status 等字段）是当前标准
- 面向中国开发者的中文语境解读，命令与示例保留英文原文
- 本任务是"技术指导/文档"类产出（knowledge-scenario），非源码改动；是否落地为真实插件代码属于后续可选工作

## Acceptance Criteria

### AC-1: Wiki 目录结构完整
- **Given**: 指导文档创建完成
- **When**: 查看输出目录
- **Then**: 存在 `hermes-agent-integration/` 目录，包含 README.md 和编号章节文件（00-06 左右）
- **Verification**: `programmatic`
- **Notes**: 验证文件存在和命名规范（kebab-case）

### AC-2: Frontmatter 格式合规
- **Given**: 每个章节文件
- **When**: 检查 frontmatter
- **Then**: 包含 id/title/source/description/tags/category/date/status 字段，格式与现有原子化 wiki 一致（YAML）
- **Verification**: `programmatic`

### AC-3: Hermes 插件接口规范阐述清晰
- **Given**: 接口规范章节
- **When**: 阅读插件接口部分
- **Then**: 清晰说明插件三类、发现路径、启用机制、plugin.yaml 字段、register(ctx) 与 tool schema
- **Verification**: `human-judgment`

### AC-4: SpecWeave 能力映射矩阵完整
- **Given**: 能力盘点章节
- **When**: 阅读映射方案
- **Then**: 覆盖 skills/commands/scripts/roles/AGENTS.md 的盘点，并给出到 Hermes tool/skill/hook/memory provider 的映射矩阵
- **Verification**: `human-judgment`

### AC-5: 配置文件设置完整
- **Given**: 配置章节
- **When**: 检查配置清单
- **Then**: 覆盖 `~/.hermes/config.yaml` 的 plugins.enabled/disabled、memory.provider、HERMES_HOME、project 级 `./.hermes/plugins`
- **Verification**: `programmatic` + `human-judgment`

### AC-6: 数据格式转换方法清晰
- **Given**: 转换方法章节
- **When**: 阅读转换说明
- **Then**: 说明 AGENTS.md 契约 → plugin.yaml + register(ctx)、知识库 markdown → OKF concept/bundle、tool schema 的转换路径
- **Verification**: `human-judgment`

### AC-7: 权限认证流程完整
- **Given**: 权限章节
- **When**: 检查认证流程
- **Then**: 覆盖插件 name 消毒/路径安全/manifest_version/API key 环境变量/project 插件权限开启
- **Verification**: `human-judgment`

### AC-8: 调用方式示例正确
- **Given**: 调用示例章节
- **When**: 阅读代码示例
- **Then**: 包含 `hermes plugins install`、`hermes okf ...`、Hermes 会话内工具调用、`with_context` 召回示例
- **Verification**: `human-judgment`

### AC-9: 常见问题覆盖完整
- **Given**: 故障排查章节
- **When**: 检查问题清单
- **Then**: 覆盖插件未发现/未启用/schema 不匹配/provider 单实例/Windows 路径/name 冲突/restart 要求等
- **Verification**: `human-judgment`

### AC-10: 交叉链接有效
- **Given**: 所有章节文件
- **When**: 检查 markdown 链接
- **Then**: 文件间相对链接路径正确；与 hermes-okf-wiki / okf-wiki 等的交叉引用指向存在文件
- **Verification**: `programmatic`

## Open Questions
- [ ] 是否需要将"落地为真实 SpecWeave→Hermes 插件代码"纳入本任务范围？（本 spec 定位为技术指导文档，落地代码属后续可选项）
- [ ] 章节数量定为 7 章（00-06）还是更多（取决于是否拆分"接口规范"与"能力映射"）？
- [ ] 是否需要补充 Hermes 实际安装验证（受网络环境限制，建议以官方文档为准并标注"示例"）？

## Impact
- **Affected specs**: `03-agent-platforms-tools/` Agent 平台知识体系；与 `okf-wiki/hermes-okf-wiki/` 形成互补
- **Affected code**: 无源代码变更；仅新增知识文档（技术指导），可选更新上级 README 索引
- **Affected docs**: `.agents/docs/knowledge/learning/03-agent-platforms-tools/hermes-agent-integration/`（新建）
