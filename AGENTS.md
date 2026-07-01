# 智能体全局契约 (AGENTS Manifest)

> **🚨 启动协议（PRIORITY ZERO — 所有智能体必须在收到任务后立即执行，优先级高于 Skill 工具选择与任何其他操作）**
>
> **步骤 1**：读取本文件全文
>
> **步骤 2**：按「上下文路由表」确定本次任务需要读取的规范文件
> - **步骤 2.0**（任务类型预检·必做）：无论工作目录是否在 `vendor/` 内，先检查任务类型是否命中 vendor 方法论资产。命中则必须读取对应 vendor 规范，不得跳过
> - **步骤 2.1**（跨项目嵌套·条件触发）：若任务工作目录位于 `vendor/` 内，先读取 [vendor/AGENTS.md](vendor/AGENTS.md)（vendor 区域入口路由），再按其「子模块路由表」进入对应子模块的 AGENTS.md 路由体系（`vendor/flexloop/AGENTS.md` → `vendor/flexloop/apps/chaos/AGENTS.md`），遵循"嵌套优先"规则；退出 `vendor/` 目录后恢复 SpecWeave 路由。三层路由：SpecWeave → vendor → flexloop
> - **步骤 2.2**（Context 恢复·条件触发）：若本会话是先前对话的延续（收到会话历史摘要/summary），必须重新执行步骤1-2，不得假设摘要中已包含完整路由信息——上下文压缩会导致认知视野收窄，只依赖摘要容易遗漏 vendor 资产
>
> **步骤 3**：读取对应的规范文件（角色定义/复盘模板/知识库等）
>
> **步骤 3.5**（自检·必做）：加载 Skill 或开始生成产出物之前，逐项确认：
> - □ 当前任务类型是否命中 vendor 方法论资产？如命中，对应规范是否已读取？
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
| 📜 全局核心规则 | [.agents/global-core-rules.md](.agents/global-core-rules.md) | 8条全局核心规则，所有角色必须遵守 |
| 🧭 上下文路由表 | [.agents/context-routing.md](.agents/context-routing.md) | 任务类型→必读规范映射表（vendor方法论资产+常规任务路由） |
| 🎭 角色定义 | [.agents/roles/](.agents/roles/) | 7个角色定义、职责矩阵、协作场景 |
| 🧬 自我演进模块 | [.agents/modules/](.agents/modules/) | 8个自我演进模块定义（感知层/认知层/执行层/治理层） |
| 🚧 能力边界声明 | [.agents/capability-boundaries.md](.agents/capability-boundaries.md) | 各角色职责边界与禁止事项 |
| 🤝 协作协议 | [.agents/protocols/](.agents/protocols/) | 会话启动、任务交接、消息传递、冲突解决等协议 |
| 📏 规则体系 | [.agents/rules/](.agents/rules/) | 阶段守卫、硬编码治理、数据安全、RACI规范等 |
| 🔧 工具规范 | [.agents/tools/](.agents/tools/) | 文件操作、代码执行、搜索、通信工具规范 |
| 🔄 标准工作流 | [.agents/workflows/](.agents/workflows/) | 功能开发、代码审查、测试流程 |
| 📋 模板 | [.agents/templates/](.agents/templates/) | 任务模板、交接模板、Mermaid模板 |
| 💬 提示词 | [.agents/prompts/](.agents/prompts/) | 各角色系统提示词与few-shot示例 |
| ⚡ 指令集 | [.agents/commands/](.agents/commands/) | 复盘、洞察、导出报告、原子化、原子提交、Mermaid管理 |
| 👥 团队管理 | [.agents/teams/](.agents/teams/) | 团队创建、权限分配、专项团队（flexloop/mermaid等） |
| 🛠️ 脚本工具库 | [.agents/scripts/](.agents/scripts/) | 自动化验证脚本与共享工具库 |
| 🎯 能力注册中心 | [.agents/capabilities/](.agents/capabilities/) | 渐进式披露三层架构（L0/L1/L2） |

## 开发规范

完整开发规范（代码风格、提交规范、Mermaid编码、路径引用、原子化操作等）见 [docs/development-standards.md](docs/development-standards.md)。

- **代码风格**：遵循现有代码风格，新增 `.agents/scripts/` 脚本前先查阅 [lib/README.md](.agents/scripts/lib/README.md) 共享库，禁止重复实现已有功能
- **提交规范**：遵循 Conventional Commits（`type(scope): subject`），主体使用中文描述
- **文档边界**：`AGENTS.md`/`.agents/` 面向 AI 智能体，`README.md`/`docs/` 面向人类读者，职责分离
- **派生产物溯源**：派生产物须在 TOML frontmatter 携带 `source` 字段标注来源
- **测试要求**：单元测试覆盖率不低于 80%，关键模块不低于 90%，所有测试用例通过无回归

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
- 2026-07-01 | refactor | AGENTS.md 原子化：将全局核心规则拆分为 .agents/global-core-rules.md，上下文路由表拆分为 .agents/context-routing.md，删除重复的能力边界/开发规范内容（已有独立文件），AGENTS.md 精简为入口索引（296行→约70行）；修复启动协议代码块嵌套导致Markdown链接不渲染的问题
