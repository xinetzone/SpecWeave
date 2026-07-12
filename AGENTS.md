# 智能体全局契约 (AGENTS Manifest)

> **🚨 启动协议（PRIORITY ZERO — 所有智能体必须在收到任务后立即执行，优先级高于 Skill 工具选择与任何其他操作）**
>
> **步骤 1**：读取本文件全文
>
> **步骤 2**：按「上下文路由表」确定本次任务需要读取的规范文件
> - **步骤 2.0**（任务类型预检·必做）：无论工作目录是否在 `vendor/` 内，先检查任务类型是否命中 vendor 方法论资产。命中则必须读取对应 vendor 规范，不得跳过
> - **步骤 2.1**（跨项目嵌套·条件触发）：若任务工作目录位于 `vendor/` 内，先读取 [vendor/AGENTS.md](vendor/AGENTS.md)（vendor 区域入口路由），再按其「子模块路由表」进入对应子模块的 AGENTS.md 路由体系（`vendor/flexloop/AGENTS.md` → `vendor/flexloop/apps/chaos/AGENTS.md`），遵循"嵌套优先"规则；退出 `vendor/` 目录后恢复 SpecWeave 路由。三层路由：SpecWeave → vendor → flexloop
> - **步骤 2.2**（Context 恢复·条件触发）：若本会话是先前对话的延续（收到会话历史摘要/summary），必须重新执行步骤1-2，不得假设摘要中已包含完整路由信息——上下文压缩会导致认知视野收窄，只依赖摘要容易遗漏 vendor 资产
> - **步骤 2.3**（内容敏感度预检·必做）：在读取规范文件之前，先判定分析对象/产出物的内容敏感度级别，决定工作流模式与存储位置（详见 [.agents/rules/content-sensitivity-precheck.md](.agents/rules/content-sensitivity-precheck.md)）：
>   - **公开内容（Public）**：公开发布的网页、开源代码、官方文档、公开新闻/文章等无访问控制内容 → 标准工作流，Spec 目录位于 `.trae/specs/<theme-subdir>/`，最终产出物位于 `docs/` 对应目录
>   - **私域内容（Private）**：内部会议记录、需 code/token 访问的私域分享链接、个人笔记、商业培训材料、含个人隐私/商业秘密的内容 → 私域工作流，跳过 `.trae/specs/` 公共规划区域，产出物直接存放于 `playground/` 下对应用户目录；若用户已指定目标目录则直接在目标目录执行
>   - 判定依据：URL特征（含 `share?code=`/`token=`/邀请码等访问控制参数）、域名特征（企业内部应用域名）、用户明确标注（"私域"/"内部"/"保密"/"个人"等关键词）、内容主题（内部会议/商业培训/个人笔记）
>   - 不确定时默认按私域处理，或向用户确认
>
> **步骤 3**：读取对应的规范文件（角色定义/复盘模板/知识库等）
>
> **步骤 3.5**（自检·必做）：加载 Skill 或开始生成产出物之前，逐项确认：
> - □ 当前任务类型是否命中 vendor 方法论资产？如命中，对应规范是否已读取？
> - □ 是否已完成内容敏感度预检（步骤 2.3）？内容级别（公开/私域）判定是否正确？产出物路径是否与级别匹配？
> - □ 是否已读取上下文路由表中所有与当前任务直接相关的入口？
> - □ 是否有相关 Skill 应被加载？（禁止在无 Skill 指导下手动操作有对应 Skill 的领域）
>
> **步骤 4**：在规范指导下选择 Skill 工具并执行任务
>
> ⚠️ **禁止在完成步骤 1-3.5 之前加载 Skill 或生成任何产出物。跳过此协议将导致三重连锁错误：输出格式错误（DOCX 替代 Markdown）、文件路径错误（根目录替代项目约定路径）、文档结构错误（单文件替代原子化模板）。更严重的是，协议违规具有非线性返工成本——跳过5分钟的规范读取可能导致30分钟以上的重构返工。同时，"凭经验做对"不等于"按方法论做对"：经验直觉不可复用，无法保证下次同类任务也能做对；遵循协议才能保证产出的可预测性和可审计性。**

本文件是项目 AI 智能体的最高优先级入口与上下文路由。所有智能体在启动时必须首先读取本文件，依据上下文路由表定位到具体的 `.agents/` 规范，再加载对应的角色定义、系统提示词与协作协议后执行任务。

详细规范容器见 [.agents/README.md](.agents/README.md)。

## 核心规范入口

| 规范 | 入口 | 说明 |
|---|---|---|
| 🚀 入门指南（L0） | [.agents/ONBOARDING.md](.agents/ONBOARDING.md) | Agent Onboarding 快速开始、能力速查表、任务类型路由 |
| 📜 全局核心规则 | [.agents/global-core-rules.md](.agents/global-core-rules.md) | 全局核心规则（启动协议、内容敏感度分流、沟通语言、按需读取、三阶段递进、元文档优先等） |
| 🧭 上下文路由表 | [.agents/context-routing.md](.agents/context-routing.md) | 任务类型→必读规范映射表（vendor方法论资产预检+常规任务路由） |
| 📇 能力注册中心（L1） | [.agents/capability-registry.md](.agents/capability-registry.md) | scripts/skills/commands/workflows/protocols/rules/knowledge 全量静态索引 |
| 🎭 角色定义 | [.agents/roles/](.agents/roles/) | 7个角色定义、职责矩阵、协作场景 |
| 🧬 自我演进模块 | [.agents/modules/](.agents/modules/) | 8个自我演进模块定义（感知层/认知层/执行层/治理层四层闭环） |
| 🚧 能力边界声明 | [.agents/capability-boundaries.md](.agents/capability-boundaries.md) | 各角色职责边界与禁止事项 |
| 🤝 协作协议 | [.agents/protocols/](.agents/protocols/) | 会话启动、任务交接、消息传递、冲突解决、PDR前置阅读、三层路由、应用生命周期、临时依赖管理 |
| 📏 规则体系 | [.agents/rules/](.agents/rules/) | 阶段守卫（含运行时）、硬编码治理、数据安全、内容敏感度预检、RACI规范、AI编码准则、前置文档阅读、元文档优先、三阶段递进、修复闭环等 |
| 🔧 工具规范 | [.agents/tools/](.agents/tools/) | 文件操作、代码执行、搜索、通信工具规范（规范层，非实现） |
| 🔄 标准工作流 | [.agents/workflows/](.agents/workflows/) | 功能开发、代码审查、测试流程 |
| 📋 模板 | [.agents/templates/](.agents/templates/) | 任务模板、交接模板、Mermaid模板 |
| 💬 提示词 | [.agents/prompts/](.agents/prompts/) | 各角色 system-prompt.md 与 few-shot 示例 |
| ⚡ 指令集 | [.agents/commands/](.agents/commands/) | 复盘、洞察、第一性原理、导出报告、原子化、原子提交、Mermaid管理、文件创建、Home Assistant、对抗性评审 |
| 👥 团队管理 | [.agents/teams/](.agents/teams/) | 团队创建、权限分配、专项团队（flexloop/mermaid/home-assistant/trae-edge-case） |
| 🌍 协作环境 | [.agents/worlds/](.agents/worlds/) | 团队协作执行、多用户权限管理、多环境配置、资源隔离 |
| 🛠️ 脚本工具库 | [.agents/scripts/](.agents/scripts/) | 自动化验证脚本与共享工具库（含 tests/、lib/、mdi/、sg_dashboard/） |
| 🎯 渐进式披露规范 | [.agents/capabilities/](.agents/capabilities/) | L0/L1/L2 三层架构规范与模板 |
| 🧰 Skill 技能门面 | [.agents/skills/](.agents/skills/) | 标准化 Skill 门面（ci-check/docgen/insight/mermaid/forum-posting/link-check等） |
| ✅ 检查清单 | [.agents/checklists/](.agents/checklists/) | 风险评分等标准化检查清单 |
| ⚙️ 工具配置 | [.agents/config/](.agents/config/) | discourse 等外部工具配置文件 |
| 🏗️ 系统架构 | [.agents/systems/](.agents/systems/) | 提示词萃取系统等系统级架构定义 |
| 📦 复用案例 | [.agents/cases/](.agents/cases/) | agentforge-adoption 等项目复用案例 |

## 开发规范

完整开发规范（代码风格、提交规范、Mermaid编码、路径引用、原子化操作等）见 [docs/development-standards.md](docs/development-standards.md)。

- **代码风格**：遵循现有代码风格，新增 `.agents/scripts/` 脚本前先查阅 [lib/README.md](.agents/scripts/lib/README.md) 共享库，禁止重复实现已有功能
- **提交规范**：遵循 Conventional Commits（`type(scope): subject`），主体使用中文描述；修复类提交须标注预防措施类型
- **文档边界**：`AGENTS.md`/`.agents/` 面向 AI 智能体（Core 规范层 + Tools 执行层），`README.md`/`docs/` 面向人类读者，职责分离
- **派生产物溯源**：派生产物须在 YAML/TOML frontmatter 携带 `source` 字段标注来源
- **路径引用**：Markdown 文档交叉引用使用相对路径，禁止 `file:///` 绝对路径；格式为 `[可读名称](相对路径#L起始行-L结束行)`
- **修复即闭环**：Bug 修复遵循「修复→预防→闭环」三阶段 SOP，禁止纯点修复（平凡修复可豁免）
- **三阶段递进**：治理（修复→预防→闭环）、知识库（生成→重组→精确化）、抽象（具体→通用→元方法）顺序不可颠倒
- **测试要求**：单元测试覆盖率不低于 80%，关键模块不低于 90%，所有测试用例通过无回归
- **简单任务验证**：格式/路径/规范类批量决策必须执行「决策前三查」（查权威文档、查现有实例、查本质目标）

## 知识库与复盘

| 资源 | 入口 |
|---|---|
| 技术知识库 | [docs/knowledge/](docs/knowledge/) |
| 复盘体系与可复用模式 | [docs/retrospective/](docs/retrospective/) |
| 可复用模式库（架构/代码/方法论） | [docs/retrospective/patterns/](docs/retrospective/patterns/) |
| 资产清单与复用指南 | [docs/retrospective/assets/asset-inventory.md](docs/retrospective/assets/asset-inventory.md) |
| vendor 子模块协同规范 | [.agents/VENDOR-INTEGRATION.md](.agents/VENDOR-INTEGRATION.md) |

## Changelog

<!-- changelog -->
- 2026-07-12 | docs | 核心数据自动更新：提交数1311+、模式438+、脚本309+、Skill16个、规则133+、指令集10个、核心规范入口22项、GitCode Stars4、Forks2、Issues0、PRs0。来源：docgen.py stats 自动统计
- 2026-07-12 | refactor | 第一性原理全面复盘更新：核心规范入口表从15项扩展至22项，补全 L0入门指南、L1能力注册中心、Skill门面、检查清单、工具配置、协作环境、系统架构、复用案例等新增模块；开发规范补充修复闭环、三阶段递进、简单任务验证、路径引用规范等关键规则；数据更新至1290+次提交节点。来源：第一性原理+全项目复盘
- 2026-07-11 | feat | AGENTS.md 启动协议新增步骤 2.3「内容敏感度预检」：判定公开/私域内容级别，私域内容跳过 `.trae/specs/` 公共规划区域直接进入 `playground/`；步骤 3.5 自检清单新增敏感度确认项；配套规则见 [.agents/rules/content-sensitivity-precheck.md](.agents/rules/content-sensitivity-precheck.md)。来源：联想AI妙记私域网页分析复盘
- 2026-07-01 | refactor | AGENTS.md 原子化：将全局核心规则拆分为 .agents/global-core-rules.md，上下文路由表拆分为 .agents/context-routing.md，删除重复的能力边界/开发规范内容（已有独立文件），AGENTS.md 精简为入口索引（296行→约70行）；修复启动协议代码块嵌套导致Markdown链接不渲染的问题
