---
title: "AI Agent 源码深度 OKF Wiki 教程 - 产品需求文档"
status: "draft"
---

# AI Agent 源码深度 OKF Wiki 教程 - 产品需求文档

## Overview

* **Summary**: 为 `external/libs/models/ai/` 目录下全部 12 个 AI Agent 相关开源项目逐一生成项目级深度 OKF v0.2 Wiki 教程，取代之前仅做跨项目概念概述的浅层产出。

* **Purpose**: 之前的 ai-agent bundle 仅生成了跨项目概念概述（10 concepts + 4 examples），8/12 个项目只在概念文档中被简略提及，没有项目专属的架构解析、核心模块走读、API/类参考、代码示例。用户要求每个项目都要有"深度分析"——即像 cpython bundle 那样，针对项目自身架构产出完整的 concepts/examples/references 三层文档。

* **Target Users**: 需要系统化学习 AI Agent 框架源码的开发者、架构师；通过 OKF Wiki 逐项目深入理解 Agent 运行时、工具系统、记忆架构、多代理编排、插件系统等核心机制。

## Goals

* 为 12 个项目分别创建独立的 OKF bundle（每个项目一个 bundle）

* 每个 bundle 包含：项目专属 concepts/（核心模块与架构概念）、examples/（关键代码路径走读）、references/（源码信源登记+核心API索引）

* 每个项目 concepts 数量与项目规模匹配（Tier 1 大项目 8-12 篇、Tier 2 中项目 5-8 篇、Tier 3 小/内容型项目 3-6 篇）

* 保留并重组原跨项目 ai-agent bundle 为"AI Agent 架构基础"（fundamentals），作为跨项目概念总览入口

* 所有文档遵循 source-code-to-okf-wiki 五阶段流程（R→I→E→V→C），杜绝虚构 API，所有类名/方法名/函数签名必须经 Grep 验证

* 更新 bundles 总索引，反映新的 bundle 结构

## Non-Goals

* 不翻译或改写项目官方文档（必须基于源码阅读生成原创分析）

* 不为项目生成完整 API 参考手册（只覆盖核心类/关键方法，非全量 API 文档）

* 不修改 external/libs/models/ai/ 下的任何源码文件

* 不为项目生成英文文档（全部中文撰写）

* 不覆盖 node\_modules、.git、dist/build、__pycache__、测试文件等非核心代码

* intelligent-terminal 作为 Windows Terminal 超大规模 C++ 项目，不覆盖终端渲染/控制台宿主等非 Agent 相关模块（只聚焦 Agent/ACP 集成部分）

## Background & Context

* 源码目录：`d:\spaces\SpecWeave\external\libs\models\ai\`

* 输出目录：`d:\spaces\SpecWeave\projects\awesome-okf-xs\bundles\ai-agent\`

* OKF 规范：`d:\spaces\SpecWeave\projects\awesome-okf-xs\.agents\rules\frontmatter.md`

* 之前已生成浅层 bundle（`ai-agent/ai-agent`，15 docs），作为本需求的基础但需要重组为 fundamentals 概述 bundle

* 12 个项目及其规模分级：

### 项目分级

**Tier 1 — 大型 Agent 框架**（核心源码 >100 文件或核心模块 >10 个）：

| 项目                   | 语言                        | 规模特征                                                                                                                          |
| -------------------- | ------------------------- | ----------------------------------------------------------------------------------------------------------------------------- |
| hermes-agent         | Python (802 py)           | agent/核心模块 + plugins/ + providers/ + tools/ + gateway/ + skills/ + acp\_adapter/ + mcp/ 等，MoA 多代理、ToolRegistry、75+参数 AIAgent  |
| veadk-python         | Python+TS (大)             | veadk/ 核心包（Agent/Runner/Memory/Model/Tools）+ frontend/ React UI + 15 examples + tests/，运行时委托（adk/codex/piagent）               |
| Zleap-Agent          | TypeScript (12 packages)  | monorepo: agent/ai/avatar/cli/core/desktop/gateway/host/runtime/store/tasks/web，Run/Work/Step 三级状态机，Workspace-first 隔离        |
| deepseek-harness     | TypeScript (50+ packages) | monorepo: core/agent+tools+session + llm/ + mcp/ + acp/ + sdk/ + fs/ + lsp/ + shell/ + sandbox/ + goal/ 等，"一切皆插件" Cordis 架构   |
| intelligent-terminal | C++ (src/巨大)              | Windows Terminal 集成 Agent/ACP：src/cascadia/ + src/host/ft\_host + helper+master 双进程 + COM/NamedPipe + OSC 133（只覆盖 Agent 相关部分） |

**Tier 2 — 中型库/框架**（核心源码 20-100 文件或独特架构价值高）：

| 项目                     | 语言                      | 规模特征                                                                                                               |
| ---------------------- | ----------------------- | ------------------------------------------------------------------------------------------------------------------ |
| cordis                 | TypeScript (9 packages) | 元框架：core（context/fiber/events/service/registry）+ hmr/loader/logger/include/create/group/timer/utils，时空可组合性         |
| second-me (mindverse/) | Python+TS (中)           | lpm\_kernel/：L0（原始摄取）+ L1（身份洞察/shade）+ L2（SelfQA/Preference/LoRA/DPO/GraphRAG）+ api/ 路由服务 + lpm\_frontend/ Next.js |

**Tier 3 — 专项工具/技能系统**（核心源码 <20 文件或内容/配置驱动）：

| 项目                | 语言                              | 规模特征                                                                                    |
| ----------------- | ------------------------------- | --------------------------------------------------------------------------------------- |
| agency-agents     | Markdown (315 md)               | 280+ 专业 Agent persona 库，按 21 个部门（academic/design/engineering/finance 等）组织，含 SKILL.md 体系 |
| agency-agents-app | Svelte+Rust/Tauri (40 ts+23 rs) | 桌面应用：Agent 目录浏览器/部署/Playbook 执行/多工具适配，Svelte store + Rust Tauri 后端                      |
| anthropics        | Python+MD (67 py+109 md)        | Anthropic 官方 Skills 参考实现：skills/ 目录结构 + Python skill 代码，SKILL.md 标准定义                   |
| book-to-skill     | Python (24 py)                  | 知识编译系统：book\_to\_skill/ 四层产出（summary/cards/prompts/evaluation）+ scripts/ + tools/       |
| i-have-adhd       | MD+Shell (1 py)                 | 认知适配技能：skills/ 风格规则 + hooks/ + scripts/，10 条输出规则                                        |

## Functional Requirements

* **FR-1**: 每个项目有独立的 OKF bundle 目录，遵循 OKF v0.2 目录结构（concepts/examples/references/index.md/log.md）

* **FR-2**: 每个 bundle 包含项目专属信源登记簿（references/），登记项目版本、目录结构、核心文件路径、核心类/函数索引

* **FR-3**: concepts/ 覆盖项目核心架构模块，每篇概念文档聚焦一个模块/机制，包含代码片段（来自真实源码）、数据流说明、与其他模块的关系

* **FR-4**: examples/ 提供关键代码路径的深度走读，展示核心类/函数的调用链、状态转换、典型用法

* **FR-5**: 所有文档的 YAML frontmatter 包含必填字段（type/title/description/tags/generated/verified/status/stale\_after/sources）

* **FR-6**: 文档内所有类名、方法名、函数签名必须对应源码中真实存在的实体（经 Grep 验证），代码块标注语言

* **FR-7**: 原有跨项目 ai-agent bundle 重组为 `ai-agent/ai-agent-fundamentals`（架构基础），更新内容指向各项目 bundle 的深度文档

* **FR-8**: 交叉链接使用 `/` 开头的 bundle-relative 路径，不使用 `../` 相对路径；跨 bundle 链接使用 OKF 标准路径

* **FR-9**: 更新 bundles/index.md 总索引，列出所有新建 bundle，更新 total\_bundles 和 groups 计数

* **FR-10**: 每批并行生成的文档数 ≤7（遵循 source-code-to-okf-wiki 安全清单），分批生成时每批独立获取格式规范和事实清单

## Non-Functional Requirements

* **NFR-1**: 文档质量——概念文档平均 150-400 行，示例文档平均 200-500 行，信源文档 100-300 行

* **NFR-2**: 每个项目 bundle 的 concepts 文档覆盖项目 README/ARCHITECTURE.md 中提到的所有核心模块（如有），覆盖率 ≥ 80%

* **NFR-3**: 代码片段必须是从源码中提取的真实片段（可适当省略非关键部分但不能编造），每个代码片段标注源文件路径

* **NFR-4**: 文档之间的内部链接 0 断裂（Python 脚本验证）

* **NFR-5**: 中文撰写，技术术语首次出现时附英文原文括号注释

## Constraints

* **Technical**:

  * 输出路径限定在 `d:\spaces\SpecWeave\projects\awesome-okf-xs\bundles\ai-agent\` 下

  * 必须遵循 OKF v0.2 frontmatter 规范

  * 必须遵循 source-code-to-okf-wiki 工作流五阶段（R→I→E→V→C）

  * Windows 环境，路径使用反斜杠或正斜杠需一致

  * 使用 general\_purpose\_task 并行委派时，子任务不能写同一文件

* **Business**:

  * 基于公开开源代码分析，内容属公开内容（Public），存放在标准 bundles/ 目录

* **Dependencies**:

  * 依赖已有 OKF v0.2 规范文件

  * 依赖源码文件可读（已在 external/libs/models/ai/ 下）

  * 依赖 existing bundles 作为格式参考（cpython, pyinvoke, sphinx 等）

## Assumptions

* 12 个项目源码完整存在于 `external/libs/models/ai/` 下，均可读取

* intelligent-terminal 的 Agent 相关代码集中在 src/cascadia/ 和 src/host/ft\_host/ 等少数目录，不需要通读全部 C++ 源码

* agency-agents 和 i-have-adhd 以 Markdown 内容为主，深度分析重点在内容组织结构、SKILL.md 格式规范、persona 分类体系

* book-to-skill 核心逻辑在 book\_to\_skill/ Python 包中

* anthropics 核心在 skills/ 目录的 SKILL.md 模板和 Python 参考实现

* 允许在 Implement 阶段通过 general\_purpose\_task 并行委派独立项目的 R 阶段事实采集和 E 阶段文档生成

## Acceptance Criteria

### AC-1: 12 个项目 bundle 目录结构完整

* **Type**: `rule`

* **Given**: 所有文档生成完毕

* **When**: 检查 `bundles/ai-agent/` 目录

* **Then**: 存在 12 个项目 bundle 目录（hermes-agent, veadk-python, zleap-agent, deepseek-harness, intelligent-terminal, cordis, second-me, agency-agents, agency-agents-app, anthropics-skills, book-to-skill, i-have-adhd）+ 1 个 fundamentals bundle，每个都有 index.md、log.md、concepts/、examples/、references/ 子目录

* **Pass Condition**: 所有 13 个 bundle 目录结构符合 OKF 规范，Python 脚本验证 0 缺失

* **Evidence**: 目录列表 + Python 结构验证脚本输出

### AC-2: 每个 bundle 文档数量达到深度标准

* **Type**: `rule`

* **Given**: 所有文档生成完毕

* **When**: 统计每个 bundle 的 concepts/、examples/、references/ 中文档数

* **Then**:

  * Tier 1（5 个大项目）：≥8 concepts + ≥3 examples + ≥1 references = ≥12 docs/bundle

  * Tier 2（2 个中项目）：≥5 concepts + ≥2 examples + ≥1 references = ≥8 docs/bundle

  * Tier 3（5 个小项目）：≥3 concepts + ≥1 examples + ≥1 references = ≥5 docs/bundle

  * fundamentals：保持 ≥10 concepts，更新 examples 指向项目 bundles

* **Pass Condition**: 所有 bundle 达到最低文档数量要求

* **Evidence**: 文件计数脚本输出

### AC-3: 无虚构 API（Grep 级验证）

* **Type**: `rule`

* **Given**: V 阶段独立审查

* **When**: 对每个文档中出现的类名/方法名/函数名，在对应项目源码中 Grep 验证

* **Then**: 所有在代码块或正文中以代码格式出现的类名、函数名、方法名在源码中存在；允许引用项目 README/文档中提到但源码中是接口/抽象的名称，但需标注

* **Pass Condition**: 虚构 API 数量为 0

* **Evidence**: Grep 验证脚本输出 + 审查报告

### AC-4: Frontmatter 和链接完整性

* **Type**: `rule`

* **Given**: V 阶段独立审查

* **When**: Python 脚本检查所有 .md 文件

* **Then**:

  * 所有内容文档（非 index/log）有合法 YAML frontmatter，含 type/title/description 字段

  * type 值正确（concepts 下为 Concept，examples 下为 Example，references 下为 Reference）

  * 内部 Markdown 链接 0 断裂

  * 子目录 index.md 无 frontmatter

  * bundle 根 index.md 含 okf\_version

* **Pass Condition**: 验证脚本 0 errors

* **Evidence**: Python 验证脚本输出

### AC-5: 代码片段真实性与溯源

* **Type**: `rubric`

* **Dimension**: 代码片段质量

* **Scale**: 1-5

* **Anchors**:

  * 1 = 代码片段是编造的或与源码无关

  * 3 = 代码片段来自源码但缺少源文件标注，或省略了关键上下文

  * 5 = 代码片段精确来自源码（标注源文件路径），关键逻辑完整保留，非关键部分适当省略不影响理解

* **Pass Threshold**: ≥ 4

* **Evidence**: V 阶段抽查每个 bundle 至少 3 个代码片段，对照源码验证

### AC-6: 文档深度与学习价值

* **Type**: `rubric`

* **Dimension**: 架构分析深度

* **Scale**: 1-5

* **Anchors**:

  * 1 = 仅翻译 README 或罗列文件，无架构洞察

  * 3 = 覆盖核心模块但缺乏数据流/调用链分析，或模块间关系描述不清

  * 5 = 每个核心模块有清晰的架构分析（职责、数据流、关键类/方法、与其他模块关系），examples 提供真实的调用链走读，读者能据此理解项目架构

* **Pass Threshold**: ≥ 4

* **Evidence**: 独立审查者逐 bundle 阅读评分

### AC-7: 总索引更新正确

* **Type**: `rule`

* **Given**: 所有 bundle 生成完毕

* **When**: 检查 bundles/index.md

* **Then**: total\_bundles 数字准确反映实际 bundle 数量，ai-agent 分组下列出所有新建 bundle，生态关系图更新

* **Pass Condition**: 计数一致，无遗漏 bundle

* **Evidence**: 目录列表与 index.md 内容对比

## Open Questions

* [ ] fundamentals bundle 是保留现有 ai-agent/ai-agent 内容并更新，还是新建 ai-agent-fundamentals 后删除旧的？（建议：重命名/迁移为 fundamentals，避免 confusion）

* [ ] intelligent-terminal 中 Agent 集成部分的范围界定——src/cascadia/ 下哪些子目录是 Agent 相关的？需要 R 阶段探索确认

* [ ] agency-agents-app 是否包含足够的架构深度 warrant 独立 bundle，还是应并入 agency-agents？（建议：独立 bundle，因为是 Tauri 桌面应用，有独特的 Svelte+Rust 架构）

