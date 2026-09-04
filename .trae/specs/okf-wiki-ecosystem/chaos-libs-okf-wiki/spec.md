# .chaos/libs 全量子项目 OKF Wiki 教程生成 - 产品需求文档

## Overview

- **Summary**: 对 `d:\AI\.chaos\libs\` 下全部 18 个子项目执行系统化源码学习，遵循 source-code-to-okf-wiki 工作流（R→I→E→V→C 五阶段），在 `d:\AI\bundles\` 下按主题分组生成 7 个符合 OKF v0.2 规范的中文 Wiki 教程 bundle。每个 bundle 包含 concepts/（概念文档）、examples/（示例文档）、references/（信源登记）、index.md（导航）和 log.md（变更日志）。
- **Purpose**: 将零散的第三方依赖库源码转化为可溯源、结构化、AI 可读的知识包，使后续开发任务能直接通过文件读取获取项目架构、核心 API、设计模式等知识，避免重复探索和 AI 虚构 API。
- **Target Users**: AI 智能体（通过文件读取获取项目知识）、人类开发者（系统化学习这些开源项目）、项目维护者（快速回顾架构决策）。

## Goals

- 对全部 18 个子项目完成源码阅读与事实采集，事实清单覆盖每个项目的核心模块、关键类/函数、数据流和继承关系
- 按主题分组生成 7 个 OKF v0.2 规范 bundle，每个 bundle 的根 index.md 含 `okf_version: "0.2"` frontmatter
- 所有概念文档包含完整 YAML frontmatter（type, title, description, tags, generated, verified, status, stale_after, sources）
- 文档中引用的每个类名/方法名/API 必须通过 Grep 在源码中验证存在性，零虚构 API
- 所有交叉链接使用 `/` 开头的 bundle-relative 路径，无断裂链接
- 大型项目（TuyaOpen 6396 文件、TVM 1773 文件、Home Assistant 9647 文件）采用系统化全量精读策略：按模块/子系统分批阅读，每批覆盖一个完整子系统，不跳过核心模块

## Non-Goals (Out of Scope)

- 不修改任何 `.chaos/libs/` 下的源码（这些是 vendor 第三方依赖，禁止本地修改）
- 不生成英文文档（全部使用中文撰写，英文技术术语首次出现时括号注释）
- 不为纯文档/已弃用项目（tuya-home-assistant、tuya-smart-life、awesun-mcp）单独生成概念教程，它们作为相关 bundle 的 references/ 信源登记
- 不构建可运行的代码示例（examples/ 中的代码片段从源码中提取并标注来源，不要求独立运行）
- 不生成 OKF bundle 之外的额外文档（如独立的博客文章、演示文稿）
- 不执行源码的编译/测试（源码学习以静态阅读为主）

## Background & Context

`.chaos/libs/` 目录包含 18 个通过 git submodule 或独立克隆管理的第三方开源项目，涵盖 IoT SDK、AI Agent 框架、MCP 服务器、机器学习编译器、智能家居平台、移动自动化、OKF 工具链等多个技术领域。当前这些项目以原始源码形式存在，缺乏结构化的中文知识文档。

项目已有 `bundles/laozi-lineage/` 作为 OKF v0.2 规范的参考实现，展示了 bundle 目录结构、frontmatter 格式和交叉链接规范。source-code-to-okf-wiki Skill 提供了经过实战验证的五阶段工作流，包含信源先行、分批生成、Grep 级 API 验证等防护机制。

七概念方法论（R→I→E→V→C）为本任务提供质量保障：R 阶段零推测事实采集、I 阶段架构洞察、E 阶段批量文档生成、V 阶段独立验证、C 阶段模式沉淀。

### 7 个主题 Bundle 规划

| Bundle 名称 | 包含子项目 | 源码规模 | 特点 |
|-------------|-----------|---------|------|
| `tuya-iot` | TuyaOpen, TuyaOpen-dev-skills, tuya-openclaw-skills, tuya-home-assistant(参考), tuya-smart-life(参考) | 6396 C/H + 技能文件 | 嵌入式 IoT SDK + AI 开发技能 |
| `ai-agent-skills` | agency-agents, awesun-mcp(文档), awesun-skill, awesun-ui-locator, jira-skill, retro-skill | 200+ Markdown + 脚本 | AI Agent 人格/技能/插件集合 |
| `apache-tvm` | ffi/tvm, ffi/tvm-ffi | 893+29 C++/H, 880+49 Python | ML 编译器框架 + FFI 系统 |
| `home-assistant` | home-assistant/core | 9647 Python | 智能家居自动化平台 |
| `mobile-use` | mobile-use | 109 Python | 自然语言移动设备自动化 |
| `okf-ecosystem` | okf-kit, okf-desktop | 29 Python + React/Python | OKF 知识包工具链 |
| `veadk-python` | veadk-python | 438 Python | 火山引擎 Agent 开发套件 |

## Functional Requirements

- **FR-1**: R 阶段——对每个子项目逐模块阅读源码，提取编号事实清单（F-xxx），每条事实指向具体文件路径和行号，无推断性表述。事实清单存入对应 bundle 的 `references/facts-<project>.md`。
- **FR-2**: I 阶段——基于事实清单提炼 3-5 个核心架构洞察（陈述+证据+反常识+行动四元组），设计知识地图（概念文档分组、依赖关系、学习路径）。洞察文档存入对应 bundle 的 `references/insights-<project>.md`。
- **FR-3**: E 阶段——按 OKF v0.2 规范批量生成文档：先生成 references/ 信源文件，再分批生成 concepts/（每批 ≤7 文件），然后 examples/，最后写各级 index.md。
- **FR-4**: V 阶段——对每个 bundle 执行独立验证：结构检查、frontmatter 检查、链接检查、Grep 级 API 真实性验证、代码示例检查、index 完整性检查。输出验证报告并修复所有问题。
- **FR-5**: 大型项目（TuyaOpen/TVM/Home Assistant）的 R 阶段按子系统/模块分批执行，每批覆盖一个完整子系统，事实清单按模块编号（如 F-tvm-ir-001）。
- **FR-6**: 每个 bundle 的根 index.md 包含 `okf_version: "0.2"` frontmatter，子目录 index.md 不含 frontmatter。
- **FR-7**: 所有概念文档 500-5000 字，使用 `##` 二级标题分节，结尾有"## 相关概念"章节。
- **FR-8**: 文档交叉链接使用 `/` 开头的 bundle-relative 绝对路径（如 `/concepts/02-ir-basics.md`）。
- **FR-9**: C 阶段——回顾工作流执行过程，更新 source-code-to-okf-wiki 模式文档（如发现新的反模式或改进点）。

## Non-Functional Requirements

- **NFR-1**: 事实准确性——文档中引用的每个 API（类名、方法名、函数签名、参数）必须在源码中存在，V 阶段 Grep 验证零虚构。
- **NFR-2**: 溯源完整性——每个概念文档的 `sources` 字段必须指向 references/ 下已存在的信源文件，信源文件中必须列出对应的源码路径。
- **NFR-3**: 知识覆盖度——每个子项目的核心模块（按其 README/AGENTS.md/架构文档定义）必须有至少一个概念文档覆盖，不遗漏关键子系统。
- **NFR-4**: 学习路径合理性——concepts/ 文档按编号（00-99）排列，形成从入门到高级的递进学习路径，前置依赖文档编号更小。
- **NFR-5**: 格式一致性——所有 bundle 遵循统一的 OKF v0.2 目录结构、frontmatter 字段和 Markdown 风格。
- **NFR-6**: 增量可验证——每个 bundle 独立完成 R→I→E→V 闭环，可单独验证和交付，不依赖其他 bundle 的完成状态。

## Constraints

- **Technical**: 运行环境为 Windows + PowerShell；源码路径使用反斜杠但 Grep 命令需正确处理路径分隔符；不得修改 vendor 目录下任何文件。
- **Business**: 全部 18 个子项目必须覆盖，不得跳过；用户明确要求"全量精读"，大型项目不采用分层采样简化。
- **Dependencies**: source-code-to-okf-wiki Skill 的五阶段工作流和 Prompt 模板；七概念方法论的质量门标准；现有 `bundles/laozi-lineage/` 作为格式参考。
- **Scale**: 总源码量约 19,000+ 文件（含 HA 9647、TuyaOpen 6396、TVM 1773），需大量分批委派子代理执行。

## Assumptions

- 所有子项目的 git submodule 已正确初始化，源码文件完整可读（LS 结果显示文件存在）。
- awesun-mcp 仓库仅含文档（MCP 服务器为二进制分发包），其知识从 README.md 和 docs/mcp_tools.md 提取。
- agency-agents 项目主要由 Markdown 人格文件组成，"源码学习"对象为其文件组织结构、脚本逻辑和 agent 定义格式。
- TuyaOpen 项目的 6396 个 C/H 文件中可能包含大量第三方库和平台适配代码，核心框架代码集中在 src/ 子目录的特定模块中。
- Home Assistant 的 9647 个 Python 文件中绝大多数是组件集成（components/），核心架构代码在 homeassistant/ 根目录和核心子目录中，集成模块按类别/模式批量处理。
- OKF v0.2 规范以现有 `bundles/laozi-lineage/` 的实际做法为权威标准，而非仅依赖 Skill 文档描述。
- 子代理（general_purpose_task）每次可处理一个原子任务（一个模块的事实采集或一批文档生成），不合并多个任务。

## Acceptance Criteria

### AC-1: 全部 18 个子项目被覆盖

- **Given**: `.chaos/libs/` 下的 18 个子项目
- **When**: 所有 bundle 生成完毕
- **Then**: 每个子项目至少在一个 bundle 的 references/ 中有信源登记，有源码的项目至少有一个概念文档覆盖其核心功能
- **Verification**: `programmatic`——检查每个项目名称出现在至少一个 bundle 的 references/ 和 concepts/ 中
- **Notes**: 纯文档项目可仅在 references/ 中登记

### AC-2: OKF v0.2 目录结构合规

- **Given**: 生成的 7 个 bundle
- **When**: 检查每个 bundle 的目录结构
- **Then**: 每个 bundle 包含 index.md（含 okf_version frontmatter）、log.md、concepts/index.md、references/index.md；有示例的 bundle 包含 examples/index.md
- **Verification**: `programmatic`——目录结构检查脚本验证
- **Notes**: 子目录 index.md 不含 frontmatter

### AC-3: Frontmatter 字段完整

- **Given**: 所有 concepts/、examples/、references/ 下的 .md 文件（不含 index.md）
- **When**: 检查每个文件的 YAML frontmatter
- **Then**: 每个文件包含 type, title, description, tags, generated, verified, status, stale_after, sources 全部字段，sources 指向的文件存在
- **Verification**: `programmatic`——frontmatter 字段检查

### AC-4: 零虚构 API

- **Given**: 所有概念文档和示例文档中出现的类名、方法名、函数名、import 语句
- **When**: 在对应源码目录中执行 Grep 验证
- **Then**: 每个引用的 API 在源码中存在，无凭空编造的类/方法/参数
- **Verification**: `programmatic`——Grep 验证每个 API 名称
- **Notes**: 这是最关键的验收标准，发现任何虚构 API 必须修复

### AC-5: 交叉链接无断裂

- **Given**: 所有 Markdown 文件中的交叉链接
- **When**: 检查每个链接目标文件是否存在
- **Then**: 所有 `/` 开头的 bundle-relative 链接指向存在的文件，无 404
- **Verification**: `programmatic`——链接检查

### AC-6: 事实清单零推测

- **Given**: 每个项目的 facts 文件
- **When**: 检查事实表述
- **Then**: 事实中不出现"用于"、"目的是"、"设计为"等推断性表述，每条事实包含源码文件路径
- **Verification**: `human-judgment`——审查事实表述
- **Notes**: 这是 G1 质量门

### AC-7: 洞察四元组完整

- **Given**: 每个项目的 insights 文件
- **When**: 检查洞察结构
- **Then**: 每条洞察包含陈述、证据（引用 F-xxx 编号）、反常识、行动四个要素
- **Verification**: `human-judgment`——审查洞察质量
- **Notes**: 这是 G2 质量门

### AC-8: 分批生成纪律

- **Given**: E 阶段的文档生成记录
- **When**: 检查生成批次
- **Then**: references/ 先于 concepts/ 生成，index.md 最后生成，每批 concepts/ 文档数 ≤7
- **Verification**: `programmatic`——检查文件时间戳和生成日志
- **Notes**: 这是 G3 质量门的关键纪律

### AC-9: 大型项目模块全覆盖

- **Given**: TuyaOpen、TVM、Home Assistant 三个大型项目
- **When**: 检查事实清单覆盖的模块
- **Then**: 核心架构模块全部覆盖（TVM: IR/TIR/Relax/topi/runtime/target；HA: core/helpers/components核心模式；TuyaOpen: src/ 下各核心子系统）
- **Verification**: `human-judgment`——对照各项目 AGENTS.md 中定义的仓库结构
- **Notes**: 集成模块/平台适配可按模式批量处理

### AC-10: 中文撰写规范

- **Given**: 所有生成的文档
- **When**: 审查文档语言
- **Then**: 使用规范现代汉语，英文技术术语首次出现时括号注释，无网络流行语
- **Verification**: `human-judgment`

## Open Questions

- [ ] TuyaOpen 的 6396 个 C/H 文件中，哪些目录是核心框架代码、哪些是第三方库/平台适配？需在 R 阶段首个子任务中通过目录结构分析确定。
- [ ] Home Assistant 的 9647 个 Python 文件中，components/ 下数千个集成是否需要逐一阅读，还是按集成类别（light/switch/sensor 等）提取共性模式？倾向于后者，但需 R 阶段确认。
- [ ] agency-agents 的 200+ Markdown 人格文件是否需要逐一分析，还是选取代表性样本并总结模式？倾向于按 division（engineering/marketing/design 等）分类总结模式。
