---
spec_id: ai-agents-okf-wiki
created: 2026-08-23
status: draft
source_skills: [seven-concepts-cmd, source-code-to-okf-wiki]
source_dir: external/libs/ai/agents
target_dir: projects/awesome-okf-xs/bundles/ai-agent
---

# AI Agents 源码 OKF Wiki 教程生成

## Problem Statement

`external/libs/ai/agents/` 目录下收录了 7 个 AI Agent/Coding Agent 开源项目的源码，但目前缺乏系统化的中文源码级教程。这些项目涵盖了不同语言生态（Rust、Go、TypeScript、Python）、不同 Agent 架构模式（CLI Agent、TUI Agent、Web Agent、Desktop Agent、多代理编排），是学习 AI Agent 运行时架构的重要参考素材。需要使用 `source-code-to-okf-wiki` 技能（R→I→E→V→C 五阶段链路），在 `seven-concepts-cmd` 方法论编排指导下，为这些项目生成符合 OKF v0.2 规范的知识束。

## Users

- AI Agent 框架开发者——需要深入理解主流 Agent 的架构设计
- 源码学习者——需要中文系统化教程降低阅读门槛
- 框架选型者——需要对比不同 Agent 项目的设计取舍

## Goals

1. 为 `external/libs/ai/agents/` 下的全部 7 个子项目生成 OKF v0.2 规范知识束
2. 每个知识束包含 concepts/、examples/、references/ 三层结构
3. 所有 API 引用经 Grep 级源码验证，杜绝虚构
4. 更新 `bundles/ai-agent/index.md` 分组索引，将新生成的知识束纳入导航
5. 更新 `bundles/index.md` 总索引的统计数据

## Non-Goals

- 不覆盖 `external/libs/ai/` 下 agents 目录之外的项目（如 coze-dev、langchain-ai、deepseek-ai、ThePocket、Anything 等，这些属于其他分组或未来任务）
- 不修改子项目源码（vendor 禁止本地修改原则）
- 不生成模式沉淀文档（C 阶段仅做本次流程总结，跨项目模式沉淀留给后续任务）
- 不为已存在的 ai-agent/ 下的知识束（hermes-agent、veadk-python 等）做更新

## Source Projects

| # | 目录名 | 项目名称 | 主要语言 | 技术栈 | 规模评估 |
|---|--------|---------|---------|--------|---------|
| 1 | CodeWhale | CodeWhale Coding Agent | Rust + TypeScript | Cargo + npm/web (Next.js) | 大型（含完整 TUI、Web UI、Docker、MCP、Subagent、Skills 系统） |
| 2 | DeepSeek-Reasonix | DeepSeek Reasonix | Go + TypeScript | Go modules + Wails (Desktop) | 大型（含 ACP 协议、Agent 运行时、Bot 网关、Desktop App、CLI TUI、MCP、Checkpoint） |
| 3 | codex | OpenAI Codex CLI | TypeScript + Rust + Python | pnpm workspace + Bazel + Cargo | 大型（含 CLI、Rust TUI、Python SDK、Skills、Sandbox、agents.md 支持） |
| 4 | deepcode-cli | DeepCode CLI | TypeScript | Node.js + npm | 中小型（CLI 编码助手，含 MCP 支持） |
| 5 | nanobot | Nanobot Agent | Python + TypeScript | Hatch + Bun | 中型（Python Agent 核心 + TUI + WebUI + Bus 系统 + SDK） |
| 6 | opencode | OpenCode | TypeScript | Bun + Turbo + SST | 中型（Terminal Coding Agent + TUI + MCP + 插件系统） |
| 7 | pi | Pi AI CLI | TypeScript | npm + Biome | 中型（AI CLI 含多包架构：ai/client/server/tui/agent/evals） |

## Functional Requirements

### FR1: R 阶段——源码事实采集

- 为每个子项目扫描核心源码目录，识别核心模块/文件/类/函数
- 提取编号事实 F-xxx（零推测，不含推断性表述）
- 事实清单写入各 bundle 下 `spec/facts.md`

### FR2: I 阶段——架构洞察与知识地图

- 基于事实清单提炼 3-5 个核心洞察（陈述+证据+反常识+行动四元组）
- 设计知识地图：文档分组（入门/核心/高级）、依赖关系、学习路径
- 洞察写入各 bundle 下 `spec/insights.md`

### FR3: E 阶段——OKF 文档批量生成

- 为每个子项目创建标准 OKF bundle 目录结构
- **信源先行**：先生成 references/ 信源登记文件
- 分批生成 concepts/ 概念文档（每批 ≤ 7 文件）
- 生成 examples/ 实战示例文档
- **Index 最后写**：所有内容文档定稿后统一生成各级 index.md
- 每个 bundle 包含 log.md 变更日志

### FR4: V 阶段——独立验证

- Frontmatter 完整性检查（type、title、description、sources、generated、verified、status、stale_after）
- 内部链接有效性检查（使用 / 开头 bundle-relative 路径）
- Grep 级 API 真实性验证（文档中引用的类名/方法名/函数名在源码中存在）
- Index 完整性检查（列出目录中全部内容文档，无遗漏无虚构）
- 发现的问题逐一修复

### FR5: 导航索引更新

- 更新 `bundles/ai-agent/index.md`：添加 7 个新知识束的条目和统计
- 更新 `bundles/index.md`：更新总束数、总文档数、分组详情

### FR6: Bundle 目录命名

| 源码目录 | Bundle 目录名 | 说明 |
|---------|-------------|------|
| CodeWhale | `codewhale` | 原名直接使用 |
| DeepSeek-Reasonix | `deepseek-reasonix` | kebab-case 转换 |
| codex | `openai-codex` | 加 openai- 前缀避免歧义 |
| deepcode-cli | `deepcode-cli` | 原名直接使用 |
| nanobot | `nanobot` | 原名直接使用 |
| opencode | `opencode` | 原名直接使用 |
| pi | `pi-cli` | 加 -cli 后缀避免歧义（pi 过于通用） |

## Non-Functional Requirements

### NFR1: 文档质量

- 所有正文中文撰写，英文技术术语首次出现时括号注释
- 代码块标注语言，API 调用必须与源码事实一致
- 每个概念/示例文档结尾包含"## 相关概念"章节
- 概念文档按学习路径顺序编号（00-xxx.md, 01-xxx.md, ...）

### NFR2: OKF 规范符合性

- 每个非保留 .md 文件包含可解析 YAML frontmatter
- 每个 frontmatter 包含非空 `type` 字段
- 子目录 index.md 不含 frontmatter（仅 bundle 根 index.md 带 okf_version）
- 交叉引用使用 `/` 开头的 bundle-relative 路径
- bundle 根 index.md 包含 `okf_version: "0.2"` 声明

### NFR3: 溯源与验证

- references/ 文件列出核心源码文件路径与对应事实编号
- concepts/ 和 examples/ 的 frontmatter 中 sources 字段指向 references/
- verified 字段标注 `process:grep-verification` 验证方法
- stale_after 统一设置为文档生成日期 + 1 年

## Constraints

- 源码位于 git submodule 中（external/libs/ai/agents/），禁止修改源码文件
- 输出文件位于 `projects/awesome-okf-xs/bundles/ai-agent/` 下
- 遵循 awesome-okf-xs AGENTS.md 启动协议与 frontmatter 规范
- 遵循 source-code-to-okf-wiki 技能的五阶段工作流和质量门（G1-G5）
- 遵循 seven-concepts-cmd 方法论编排（知识沉淀场景 R→I→E 链路）
- 工作在 Windows + WSL 环境，文件路径使用正斜杠

## Assumptions

- external/libs/ai/agents/ 下的 7 个子项目已通过 git submodule 初始化且源码可读
- CodeWhale 目录中 `web/` 子目录是独立 web 前端，作为子模块或独立部分处理
- DeepSeek-Reasonix 内部包含 Go 后端 + Wails Desktop + React 前端，核心 Agent 逻辑在 `internal/` 目录
- deepcode-cli 项目规模较小，文档数量相应减少
- 用户期望类似 ONNX wiki（8 bundles, 150 files）的产出量级，但 Agent 项目语言更多样

## Acceptance Criteria

### Rules (binary verification)

- **AC-R1**: 7 个 bundle 目录全部创建于 `bundles/ai-agent/` 下，目录名符合 FR6 命名表
- **AC-R2**: 每个 bundle 包含 `index.md`、`log.md`、`concepts/`、`examples/`、`references/` 标准结构
- **AC-R3**: 每个 bundle 根 index.md 包含 `okf_version: "0.2"` 和 `type: bundle` frontmatter
- **AC-R4**: 所有 concepts/*.md、examples/*.md、references/*.md 文件包含有效 YAML frontmatter，且 type 字段非空
- **AC-R5**: references/ 信源文件先于 concepts/examples 生成（信源先行原则）
- **AC-R6**: 各级 index.md 在所有内容文档定稿后最后生成
- **AC-R7**: 文档中引用的类名/方法名/函数名经 Grep 验证在源码中存在（V 阶段）
- **AC-R8**: 内部交叉链接使用 `/` 开头 bundle-relative 路径，无断链
- **AC-R9**: `bundles/ai-agent/index.md` 已更新，包含 7 个新知识束条目
- **AC-R10**: `bundles/index.md` 已更新，反映新的束数和文档数统计
- **AC-R11**: 未修改任何源码文件（external/ 目录零变更）

### Rubrics (evaluative quality)

- **AC-RU1: 架构覆盖度** (0-3)
  - 3: 每个 bundle 覆盖核心架构组件（Agent 循环/工具系统/记忆/Provider/通信协议等），概念文档 5-12 篇
  - 2: 覆盖主要架构组件，概念文档 3-5 篇
  - 1: 仅有表层 API 文档，缺乏架构深度
  - 0: 文档零散不成体系
  - **Threshold**: ≥ 2（大型项目 CodeWhale/DeepSeek-Reasonix/codex 必须 ≥ 3）

- **AC-RU2: 代码示例质量** (0-3)
  - 3: 代码示例可运行、与源码 API 完全一致、有注释说明
  - 2: 代码示例 API 正确但可能缺少运行上下文
  - 1: 代码示例有小错误或缺少关键参数
  - 0: 代码示例虚构 API 或无法使用
  - **Threshold**: ≥ 2

- **AC-RU3: 事实溯源完整性** (0-3)
  - 3: 每个技术声明均可追溯到 facts.md 编号事实和 references/ 信源文件
  - 2: 大部分声明有溯源，少数缺少事实编号
  - 1: 溯源不完整，存在无法验证的声明
  - 0: 无溯源，纯 AI 生成内容
  - **Threshold**: ≥ 2

## Dependencies

- 已完成的 ONNX wiki 生成经验（2026-08-23 会话）作为参考模式
- awesome-okf-xs 的 OKF v0.2 frontmatter 规范
- source-code-to-okf-wiki 技能的 Prompt 模板

## Open Questions

1. DeepSeek-Reasonix 的 Go 源码量非常大（internal/ 下数十个包），是否需要聚焦核心 Agent 包而非全覆盖？（建议聚焦 internal/agent、internal/acp、internal/bot、internal/cli 核心包）
2. codex 包含 Rust TUI、Node.js CLI、Python SDK 三部分，是否按语言子模块组织 references？
3. CodeWhale 的 web/ 前端部分是否纳入文档范围？（建议纳入架构概述，但不深入前端细节）
