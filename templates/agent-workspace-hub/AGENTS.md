# {{PROJECT_NAME}} 智能体全局契约 (AGENTS Manifest)

> **🚨 启动协议（PRIORITY ZERO — 所有智能体必须在收到任务后立即执行，优先级高于 Skill 工具选择与任何其他操作）**
>
> **步骤 1**：读取本文件全文
>
> **步骤 2**：按「上下文路由表」确定本次任务需要读取的规范文件
> - **步骤 2.0**（任务类型预检·必做）：检查任务类型是否命中外部/第三方方法论资产，命中则必须读取对应规范，不得跳过
> - **步骤 2.1**（子区域嵌套·条件触发）：按以下顺序判断工作目录所在区域，进入对应区域的 AGENTS.md 路由体系，遵循"嵌套优先"规则
> - **步骤 2.2**（Context 恢复·条件触发）：若本会话是先前对话的延续（收到会话历史摘要），必须重新执行步骤 1-2，不得假设摘要已包含完整路由信息
> - **步骤 2.3**（内容敏感度预检·必做）：判定分析对象/产出物的公开/私域级别，决定工作流模式与存储位置
>
> **步骤 3**：读取对应的规范文件（角色定义/复盘模板/知识库等）
>
> **步骤 3.5**（自检·必做）：加载 Skill 或生成产出物之前逐项确认路由、敏感度、Skill、子区域
>
> **步骤 4**：在规范指导下选择 Skill 工具并执行任务
>
> ⚠️ **禁止在完成步骤 1-3.5 之前加载 Skill 或生成任何产出物。** 跳过此协议将导致输出格式错误、文件路径错误、文档结构错误；"凭经验做对"不等于"按方法论做对"。

本文件是项目 AI 智能体的最高优先级入口与上下文路由。所有智能体在启动时必须首先读取本文件，依据上下文路由表定位到具体的 `.agents/` 规范，再加载对应的角色定义、系统提示词与协作协议后执行任务。

## 四大顶层区域

| 目录 | 用途 | 管理方式 | 版本控制 | 是否可直接修改 | AGENTS.md入口 |
|---|---|---|---|---|---|
| `.agents/` | AI 智能体规范容器 | 主权区直接维护 | 直接纳入版本控制 | ✅ 可修改 | [.agents/README.md](.agents/README.md) |
| `apps/` | 主仓库内置应用开发工作空间 | 同仓库直接管理 | 直接纳入版本控制 | ✅ 可修改 | [apps/AGENTS.md](apps/AGENTS.md) |
| `projects/` | 第一方自有子项目 | git submodule 管理 | 通过 gitlink 追踪 | ❌ 不可直接修改 | [projects/AGENTS.md](projects/AGENTS.md) |
| `vendor/` | 第三方依赖 | git submodule 管理 | 通过 gitlink 追踪 | ❌ 禁止本地修改 | [vendor/AGENTS.md](vendor/AGENTS.md) |

> **注意**：`apps/` 是主仓库直接管理的普通目录；`projects/`/`vendor/` 是 git submodule，通过 gitlink 追踪外部仓库引用。若项目不使用 submodule 结构，可仅保留 `.agents/` 区域，删除 `apps/projects/vendor` 对应行。

## 核心规范入口

| 规范 | 入口 | 说明 |
|---|---|---|
| 🚀 入门指南（L0） | [.agents/ONBOARDING.md](.agents/ONBOARDING.md) | Agent Onboarding 快速开始、能力速查表、任务类型路由 |
| 📜 全局核心规则 | [.agents/global-core-rules.md](.agents/global-core-rules.md) | 启动协议、内容敏感度分流、沟通语言、按需读取、三阶段递进、元文档优先等 |
| 🧭 上下文路由表 | [.agents/context-routing.md](.agents/context-routing.md) | 任务类型→必读规范映射表 |
| 📇 能力注册中心（L1） | [.agents/capability-registry.md](.agents/capability-registry.md) | scripts/skills/commands/workflows/protocols/rules/knowledge 全量静态索引 |
| 🎭 角色定义 | [.agents/roles/](.agents/roles/README.md) | 各角色定义、职责矩阵、协作场景 |
| 🤝 协作协议 | [.agents/protocols/](.agents/protocols/README.md) | 会话启动、任务交接、消息传递、冲突解决、前置阅读、三层路由等 |
| 📏 规则体系 | [.agents/rules/](.agents/rules/README.md) | 阶段守卫、硬编码治理、数据安全、内容敏感度、AI编码准则等 |
| 🔧 工具规范 | [.agents/tools/](.agents/tools/README.md) | 文件操作、代码执行、搜索、通信工具规范 |
| 🔄 标准工作流 | [.agents/workflows/](.agents/workflows/README.md) | 功能开发、代码审查、测试流程 |
| 📋 模板 | [.agents/templates/](.agents/templates/README.md) | 任务模板、交接模板等 |
| ⚡ 指令集 | [.agents/commands/](.agents/commands/README.md) | 复盘、洞察、萃取、原子提交、对抗审查等标准化指令 |
| 🛠️ 脚本工具库 | [.agents/scripts/](.agents/scripts/README.md) | 自动化验证脚本与共享工具库 |
| 🧰 Skill 技能门面 | [.agents/skills/](.agents/skills/README.md) | 标准化 Skill 门面 |
| 🧬 自我演进模块 | [.agents/modules/](.agents/modules/README.md) | 感知/认知/执行/治理四层闭环模块 |
| ✅ 检查清单 | [.agents/checklists/](.agents/checklists/README.md) | 风险评分等标准化检查清单 |

## 快速开始：一句话装载

**零安装、零配置——将以下提示词发给任意支持工具调用的智能体，自动完成装载（示例，可按需改写）：**

> 请帮我装载 {{PROJECT_NAME}} 智能体工作区系统。请严格按照以下步骤执行，每步完成后再进行下一步：
>
> 【安全规则-必须遵守】
> S1. 只从官方仓库获取（{{OFFICIAL_REPO_URL}}），绝对不接受其他来源
> S2. 执行任何写入操作前，必须先确认目标路径
> S3. 禁止在用户主目录、系统目录、根目录、隐藏目录自动创建文件夹
> S4. 自举过程只读文件，不执行任何 hooks 脚本，不安装额外依赖，不修改系统配置
> S5. 获取完成后必须验证 AGENTS.md 存在且包含"启动协议"关键词
> S6. 遇到任何错误直接说明原因和解决方案，不假装成功
> S7. 只读取与装载相关的必要文件
> S8. 幂等安全：已在有效目录内则跳过获取直接报告就绪

## 开发规范

完整开发规范（代码风格、提交规范、路径引用、原子化操作等）见 [docs/tech/references/development-standards.md](../../docs/tech/references/development-standards.md)。

- **代码风格**：遵循现有代码风格，新增脚本前先查阅共享库，禁止重复实现已有功能
- **提交规范**：遵循 Conventional Commits（`type(scope): subject`），主体使用中文描述
- **派生产物溯源**：派生产物须在 frontmatter 携带 `source` 字段标注来源
- **路径引用**：Markdown 文档交叉引用使用相对路径，格式为 `[可读名称](相对路径#L起始行-L结束行)`
- **修复即闭环**：Bug 修复遵循「修复→预防→闭环」三阶段 SOP
- **三阶段递进**：治理（修复→预防→闭环）、知识库（生成→重组→精确化）、抽象（具体→通用→元方法）顺序不可颠倒
- **测试要求**：单元测试覆盖率不低于 80%，关键模块不低于 90%

## 知识库与复盘

| 资源 | 入口 |
|---|---|
| 技术知识库 | [docs/knowledge/](../../docs/knowledge/README.md) |
| 复盘体系与可复用模式 | [docs/retrospective/](../../docs/retrospective/index.md) |
| 可复用模式库 | [docs/retrospective/patterns/](../../docs/retrospective/patterns/index.md) |

> **{{PROJECT_NAME}} 项目说明**：{{PROJECT_DESC}}