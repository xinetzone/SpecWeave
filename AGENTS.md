# 智能体全局契约 (AGENTS Manifest)

> **🚨 启动协议（PRIORITY ZERO — 所有智能体必须在收到任务后立即执行，优先级高于 Skill 工具选择与任何其他操作）**
>
> ```
> 步骤 1：读取本文件全文
> 步骤 2：按「上下文路由表」确定本次任务需要读取的规范文件
>   步骤 2.0（任务类型预检·必做）：无论工作目录是否在 vendor/ 内，先检查任务类型是否命中下表中的 vendor 方法论资产。命中则必须读取对应 vendor 规范，不得跳过：
>     • Skill 创建/优化 → vendor/flexloop/apps/chaos/.agents/skills/skill-creator/SKILL.md（Skill开发方法论权威来源）
>     • 跨项目子模块协同 → docs/knowledge/VENDOR-INTEGRATION.md + vendor/AGENTS.md
>     • （其他vendor资产持续补充中，见上下文路由表「vendor 方法论资产」区块）
>   步骤 2.1（跨项目嵌套·条件触发）：若任务工作目录位于 `vendor/` 内，先读取 [vendor/AGENTS.md](vendor/AGENTS.md)（vendor 区域入口路由），再按其「子模块路由表」进入对应子模块的 AGENTS.md 路由体系（`vendor/flexloop/AGENTS.md` → `vendor/flexloop/apps/chaos/AGENTS.md`），遵循"嵌套优先"规则；退出 `vendor/` 目录后恢复 SpecWeave 路由。三层路由：SpecWeave → vendor → flexloop
>   步骤 2.2（Context 恢复·条件触发）：若本会话是先前对话的延续（收到会话历史摘要/summary），必须重新执行步骤1-2，不得假设摘要中已包含完整路由信息——上下文压缩会导致认知视野收窄，只依赖摘要容易遗漏 vendor 资产。
> 步骤 3：读取对应的规范文件（角色定义/复盘模板/知识库等）
> 步骤 3.5（自检·必做）：加载 Skill 或开始生成产出物之前，逐项确认：
>   □ 当前任务类型是否命中 vendor 方法论资产？如命中，对应规范是否已读取？
>   □ 是否已读取上下文路由表中所有与当前任务直接相关的入口？
>   □ 是否有相关 Skill 应被加载？（禁止在无 Skill 指导下手动操作有对应 Skill 的领域）
> 步骤 4：在规范指导下选择 Skill 工具并执行任务
> ```
>
> ⚠️ **禁止在完成步骤 1-3.5 之前加载 Skill 或生成任何产出物。跳过此协议将导致三重连锁错误：输出格式错误（DOCX 替代 Markdown）、文件路径错误（根目录替代项目约定路径）、文档结构错误（单文件替代原子化模板）。更严重的是，协议违规具有非线性返工成本——跳过5分钟的规范读取可能导致30分钟以上的重构返工。同时，"凭经验做对"不等于"按方法论做对"：经验直觉不可复用，无法保证下次同类任务也能做对；遵循协议才能保证产出的可预测性和可审计性。**

本文件是项目 AI 智能体的最高优先级入口与上下文路由。所有智能体在启动时必须首先读取本文件，依据上下文路由表定位到具体的 `.agents/` 规范，再加载对应的角色定义、系统提示词与协作协议后执行任务。

详细规范容器见 [.agents/README.md](.agents/README.md)。

## 全局核心规则

- **启动协议优先**：收到任何任务后，首先执行本文件顶部的启动协议。在完成步骤 1-3.5（含自检）之前，不得加载任何 Skill 或调用任何生成工具。这是所有其他规则的先决条件——违反此规则会导致所有下游决策失去规范依据，并产生非线性返工成本。特别注意：即使工作目录不在 `vendor/` 内，也必须执行步骤 2.0（任务类型预检）检查是否需要 vendor 方法论资产。
- **沟通语言**：必须使用中文与用户交流，所有输出、注释、提交信息、文档均以中文为主。
- **按需读取**：执行特定领域任务前，只读取与当前任务直接相关的 `.agents/` 规范，避免一次性加载全部上下文。
- **上下文节省**：遵循"先搜索、再精读、只保留相关上下文"的原则，优先使用语义检索与精确匹配工具，剔除无关片段。多文件差异分析场景下采用「结构对比优先、全文精读兜底」策略：先用 Grep 提取标题/签名做结构对比确定差异集，再对差异集文件精读全文确定修改方案，避免全量精读带来的边际收益递减。
- **Mermaid 优先**：流程、架构、关系、状态机等可视化逻辑优先使用 Mermaid 表达，确保可渲染、可版本化。
- **代码修改**：遵循"约定优于配置"，优先参考现有代码风格、命名规范与目录结构，不引入与项目不一致的新风格。
- **Spec 目录规范**：执行 `/spec` 工作流时，新 spec 目录必须创建在 `.trae/specs/<theme-subdir>/` 对应的 7 大主题子目录下，禁止直接创建在 `.trae/specs/` 根目录。创建前必须查阅 [.trae/specs/README.md](.trae/specs/README.md) 的归类决策树确定归属主题。
- **禁止提交临时依赖**：禁止将 `.temp/`、`__pycache__/`、`.venv/`、`node_modules/` 等临时依赖和中间产物提交至 Git 仓库。`vendor/` 目录通过 git 子模块管理第三方依赖（追踪 gitlink），仅 `vendor/README.md` 和 `vendor/VERSION.md` 元数据文件直接纳入版本管理，其余 vendor 内容默认忽略。
- **查阅知识库**：执行任务前应主动查阅 [docs/knowledge/README.md](docs/knowledge/README.md) 技术知识库与 [docs/retrospective/README.md](docs/retrospective/README.md) 复盘文档体系，了解已有经验、架构决策、可复用模式与最佳实践，避免重复踩坑。

## 角色定义索引

详细角色定义、职责矩阵、协作场景见 [.agents/roles/README.md](.agents/roles/README.md)。

| 角色 | ID | 职责 | 入口 |
|---|---|---|---|
| 编排协调者 | orchestrator | 任务分配、流程协调、冲突仲裁 | [.agents/roles/orchestrator.md](.agents/roles/orchestrator.md) |
| 架构师 | architect | 技术方案设计、架构决策 | [.agents/roles/architect.md](.agents/roles/architect.md) |
| 开发者 | developer | 代码实现、重构、缺陷修复 | [.agents/roles/developer.md](.agents/roles/developer.md) |
| 代码审查者 | reviewer | 代码质量审查、规范校验 | [.agents/roles/reviewer.md](.agents/roles/reviewer.md) |
| 测试工程师 | tester | 测试用例编写、执行、覆盖率 | [.agents/roles/tester.md](.agents/roles/tester.md) |
| 联合创始者 | co-founder | 愿景确立、协作契约奠基、关键决策仲裁 | [.agents/roles/co-founder.md](.agents/roles/co-founder.md) |
| 团队管理员 | team-admin | 团队创建管理、权限分配、新角色自动创建 | [.agents/teams/team-admin.md](.agents/teams/team-admin.md) |

## 自我演进模块索引

详细模块定义、四层架构、数据流向见 [.agents/modules/README.md](.agents/modules/README.md)。

| 模块 | ID | 所属层级 | 入口 |
|---|---|---|---|
| 自我洞察 | self-insight | 感知层 | [.agents/modules/self-insight.md](.agents/modules/self-insight.md) |
| 自我复盘 | self-retrospective | 感知层 | [.agents/modules/self-retrospective.md](.agents/modules/self-retrospective.md) |
| 自我萃取 | self-extraction | 认知层 | [.agents/modules/self-extraction.md](.agents/modules/self-extraction.md) |
| 自我进化 | self-evolution | 认知层 | [.agents/modules/self-evolution.md](.agents/modules/self-evolution.md) |
| 自我迭代 | self-iteration | 执行层 | [.agents/modules/self-iteration.md](.agents/modules/self-iteration.md) |
| 自我验证 | self-verification | 执行层 | [.agents/modules/self-verification.md](.agents/modules/self-verification.md) |
| 自我管理 | self-management | 治理层 | [.agents/modules/self-management.md](.agents/modules/self-management.md) |
| 自我发展 | self-development | 治理层 | [.agents/modules/self-development.md](.agents/modules/self-development.md) |

## 能力边界声明

各角色的职责边界与能力限制详见 [.agents/capability-boundaries.md](.agents/capability-boundaries.md)。

- **编排协调者 (orchestrator)**：不直接编写业务代码；不替代架构师做技术决策。
- **架构师 (architect)**：不负责代码实现细节；不执行测试用例编写。
- **开发者 (developer)**：不擅自变更架构决策；不绕过审查直接合并代码。
- **代码审查者 (reviewer)**：不直接修改业务代码；不替代测试工程师执行验收测试。
- **测试工程师 (tester)**：不负责生产环境部署；不擅自修改业务逻辑代码。
- **团队管理员 (team-admin)**：不直接编写业务代码；不擅自变更架构决策；不越权管理其他团队；新角色创建须满足触发条件。

## 协作协议概要

详细协议定义、使用流程、场景示例见 [.agents/protocols/README.md](.agents/protocols/README.md)。

| 协议 | 用途 | 入口 |
|---|---|---|
| 任务交接 | 智能体间任务转移 | [.agents/protocols/handoff.md](.agents/protocols/handoff.md) |
| 消息传递 | 智能体间通信 | [.agents/protocols/messaging.md](.agents/protocols/messaging.md) |
| 冲突解决 | 分歧仲裁 | [.agents/protocols/conflict-resolution.md](.agents/protocols/conflict-resolution.md) |
| 临时依赖管理 | 依赖存放与清理 | [.agents/protocols/dependency-management.md](.agents/protocols/dependency-management.md) |
| 前置文档强制读取 | 必读文档清单、读取确认机制、结构化日志规范（[PDR-LOG]） | [.agents/protocols/pre-document-reading.md](.agents/protocols/pre-document-reading.md) |
| 应用开发生命周期 | .temp/ 暂存开发 → apps/ 稳定迁移 | [.agents/protocols/app-development-workflow.md](.agents/protocols/app-development-workflow.md) |

## 规则体系索引

详细规则体系、使用流程、场景导航见 [.agents/rules/README.md](.agents/rules/README.md)。

| 规则文档 | 用途 | 适用角色 | 入口 |
|---|---|---|---|
| 规则体系总览 | 体系架构、快速导航、使用流程 | 全部角色 | [.agents/rules/README.md](.agents/rules/README.md) |
| 开发流程阶段守卫 | 阶段边界定义、跨阶段拦截机制、阶段跳转审批流程、关键节点结构化日志规范（[SG-LOG]） | 全部角色 | [.agents/rules/stage-guardrails.md](.agents/rules/stage-guardrails.md) |
| 硬编码识别标准 | 8 大类硬编码定义、正例反例、检测要点 | developer, reviewer | [.agents/rules/identification-standards.md](.agents/rules/identification-standards.md) |
| 允许场景与审批 | 允许场景清单、例外审批流程、例外清单模板 | developer, reviewer, architect, orchestrator | [.agents/rules/allowable-scenarios.md](.agents/rules/allowable-scenarios.md) |
| 替代方案指南 | 7 种替代方案实施指南、代码示例、模板脚手架 | developer | [.agents/rules/alternatives-guide.md](.agents/rules/alternatives-guide.md) |
| 检测与报告机制 | 三层检测体系（自动化扫描、人工审查、定期报告） | developer, reviewer, orchestrator | [.agents/rules/detection-and-reporting.md](.agents/rules/detection-and-reporting.md) |
| 执行与验证规则 | 6 条可执行治理规则、验证手段、合规等级 | 全部角色 | [.agents/rules/enforcement-guidelines.md](.agents/rules/enforcement-guidelines.md) |

## 工具规范索引

详细工具分类、使用说明、最佳实践见 [.agents/tools/README.md](.agents/tools/README.md)。

| 类别 | 涵盖工具 | 适用场景 | 入口 |
|---|---|---|---|
| 文件操作 | read_file、write_file、edit_file、delete_file、list_directory | 文件读写、编辑、删除、目录列举 | [.agents/tools/file-operations.md](.agents/tools/file-operations.md) |
| 代码执行 | run_command、run_tests、build_project | 终端命令执行、测试运行、项目构建 | [.agents/tools/code-execution.md](.agents/tools/code-execution.md) |
| 搜索 | grep_search、glob_find、semantic_search | 内容正则搜索、文件名匹配、语义搜索 | [.agents/tools/search.md](.agents/tools/search.md) |
| 通信 | send_message、handoff_task、sync_status | 智能体间消息传递、任务交接、状态同步 | [.agents/tools/communication.md](.agents/tools/communication.md) |

## 标准工作流索引

详细工作流定义、角色参与表、Mermaid 流程图见 [.agents/workflows/README.md](.agents/workflows/README.md)。

| 工作流 | 适用场景 | 参与角色 | 入口 |
|---|---|---|---|
| 功能开发（新功能/扩展/重构三路径） | 新功能、功能扩展、功能重构 | 全部角色 | [.agents/workflows/feature-development.md](.agents/workflows/feature-development.md) |
| 代码审查 | PR 审查 | developer, reviewer, orchestrator | [.agents/workflows/code-review.md](.agents/workflows/code-review.md) |
| 测试流程 | 测试执行 | tester, developer, reviewer | [.agents/workflows/testing.md](.agents/workflows/testing.md) |

## 模板索引

详细模板清单、使用方法、主题模板见 [.agents/templates/README.md](.agents/templates/README.md)。

| 模板 | 用途 | 使用场景 | 入口 |
|---|---|---|---|
| 任务模板 | 任务定义 | 创建新任务时 | [.agents/templates/task-template.md](.agents/templates/task-template.md) |
| 交接模板 | 任务交接 | 智能体间任务转移时 | [.agents/templates/handoff-template.md](.agents/templates/handoff-template.md) |

## 提示词索引

详细目录结构、角色映射、使用方法见 [.agents/prompts/README.md](.agents/prompts/README.md)。

| 角色 | 系统提示词 | Few-shot 示例 |
|---|---|---|
| 编排协调者 | [.agents/prompts/orchestrator/system-prompt.md](.agents/prompts/orchestrator/system-prompt.md) | [.agents/prompts/orchestrator/few-shot.md](.agents/prompts/orchestrator/few-shot.md) |
| 架构师 | [.agents/prompts/architect/system-prompt.md](.agents/prompts/architect/system-prompt.md) | [.agents/prompts/architect/few-shot.md](.agents/prompts/architect/few-shot.md) |
| 开发者 | [.agents/prompts/developer/system-prompt.md](.agents/prompts/developer/system-prompt.md) | [.agents/prompts/developer/few-shot.md](.agents/prompts/developer/few-shot.md) |
| 代码审查者 | [.agents/prompts/reviewer/system-prompt.md](.agents/prompts/reviewer/system-prompt.md) | [.agents/prompts/reviewer/few-shot.md](.agents/prompts/reviewer/few-shot.md) |
| 测试工程师 | [.agents/prompts/tester/system-prompt.md](.agents/prompts/tester/system-prompt.md) | [.agents/prompts/tester/few-shot.md](.agents/prompts/tester/few-shot.md) |

## 指令集索引

详细指令集定义、执行流程、设计理念见 [.agents/commands/README.md](.agents/commands/README.md)。

| 指令集 | ID | 用途 | 入口 |
|---|---|---|---|
| 复盘 | retrospective | 项目复盘流程，生成复盘报告与改进建议 | [.agents/commands/retrospective.md](.agents/commands/retrospective.md) |
| 洞察 | insight | 数据分析与问题诊断，识别优化机会与异常 | [.agents/commands/insight.md](.agents/commands/insight.md) |
| 导出报告 | export-report | 结构化报告导出，支持多格式与归档 | [.agents/commands/export-report.md](.agents/commands/export-report.md) |
| 原子化 | atomization | 文档与代码的原子化拆分，确保单一职责 | [.agents/commands/atomization.md](.agents/commands/atomization.md) |
| 原子提交 | atomic-commit | Git 原子化提交规范，确保单次提交单一职责 | [.agents/commands/atomic-commit.md](.agents/commands/atomic-commit.md) |

## 开发规范

完整开发规范（代码风格、提交规范、Markdown 表格修改、派生产物溯源、路径引用规范等）见 [docs/development-standards.md](docs/development-standards.md)。

### 代码风格

- 遵循现有代码风格，不引入与项目不一致的新风格。
- 命名、缩进、注释、文件组织均以仓库内既有约定为准。
- 新增依赖前先评估必要性，优先复用现有工具链。
- **新增 `.agents/scripts/` 脚本前必须先查阅 [lib/README.md](.agents/scripts/lib/README.md)**，确认共享库中是否已有可复用函数（路径解析、CLI输出、frontmatter解析、Markdown处理、链接修复、模式扫描等），禁止重复实现已有功能；提交前运行 `python .agents/scripts/check-duplication.py` 确认未引入跨文件重复代码。

### 提交规范

- 遵循 Conventional Commits 规范，格式为 `type(scope): subject`。
- 常用类型：`feat`、`fix`、`refactor`、`test`、`docs`、`chore`、`perf`。
- 提交信息主体使用中文描述，简明扼要说明"为什么"而非仅"做了什么"。

### 文档边界

- `AGENTS.md` 面向 AI 智能体，是最高优先级入口与上下文路由，定义启动协议、全局规则与索引表。
- `.agents/` 面向 AI 智能体，存放角色定义、提示词、协议、工作流、脚本等机器可读规范的详细内容。
- `README.md` 面向人类读者，作为项目简介入口，介绍用途、快速开始、核心亮点与文档导航。
- `docs/` 面向人类读者，存放项目文档、开发规范、技术知识库、复盘体系与可复用模式的详细内容。
- 两者职责分离，不相互混用；人类文档与 AI 文档各有入口，互不干扰。

### 派生产物溯源

- 从源文档（如 `README.md`、spec 文档）派生出的结构化产物，须在 TOML frontmatter 携带 `source` 字段标注来源，格式为 `source = "<文件>#<章节>"`。
- 使用 `.agents/scripts/check-source-traceability.py --affected <源文件>` 可查询源变更的受影响产物清单。

## 测试要求

完整测试规范（测试骨架生成、覆盖率阈值、验收标准）见 [docs/development-standards.md](docs/development-standards.md)。

- 每个模块必须有对应的单元测试，覆盖核心逻辑与边界条件。
- 整体测试覆盖率不低于 80%，关键模块与核心业务逻辑覆盖率应达到 90% 以上。
- 所有测试用例通过，无新增失败用例，无回归问题，关键路径均有断言。

## 上下文路由表

### 🧭 vendor 方法论资产（任务类型预检·必查）

> 以下资产位于 vendor 子模块中，是对应任务类型最权威的方法论来源。**无论当前工作目录是否在 vendor/ 内，只要任务类型命中就必须读取。** 这防范了"就近直觉"偏差——只看工作目录附近文件而忽略 vendor 中更成熟的方法论资产。

| 任务类型 | 必读入口 | 为什么必须读 |
|---|---|---|
| Skill 创建/优化/调试 | [vendor/flexloop/apps/chaos/.agents/skills/skill-creator/SKILL.md](vendor/flexloop/apps/chaos/.agents/skills/skill-creator/SKILL.md) + [.agents/rules/skill-development.md](.agents/rules/skill-development.md)（SpecWeave补充规范） | Skill 开发方法论权威来源：description触发词优化、渐进式披露、长度控制、Why解释原则；补充规范增加三层路由合规、五要素模型、双方案模式、资产盘点、验证清单等SpecWeave特有要求 |
| Skill 目录结构与规范 | [vendor/flexloop/apps/chaos/.agents/rules/skills.md](vendor/flexloop/apps/chaos/.agents/rules/skills.md) | Skill 的SKILL.md格式、目录组织、验证机制等规范定义 |
| 跨项目子模块协同 | [docs/knowledge/VENDOR-INTEGRATION.md](docs/knowledge/VENDOR-INTEGRATION.md)（边界划分/版本控制/更新同步/测试隔离/模式萃取）+ [vendor/AGENTS.md](vendor/AGENTS.md) | 三层路由体系与 vendor 子模块协作规范 |

### 📋 常规任务路由

| 任务类型 | 必读入口 |
|---|---|
| Skill 创建/优化/调试（SpecWeave 主权区补充规范） | [.agents/rules/skill-development.md](.agents/rules/skill-development.md)（五要素模型、双方案模式、资产盘点、验证清单） |
| 角色定义、职责分工 | [.agents/roles/](.agents/roles/) |
| 角色协作场景、触发条件 | [.agents/roles/collaboration-scenarios.md](.agents/roles/collaboration-scenarios.md) |
| 自我演进模块定义 | [.agents/modules/](.agents/modules/) |
| 系统提示词、few-shot | [.agents/prompts/](.agents/prompts/) |
| 工具调用规范 | [.agents/tools/](.agents/tools/) |
| 协作协议、通信机制 | [.agents/protocols/](.agents/protocols/) |
| 标准工作流 | [.agents/workflows/](.agents/workflows/) |
| 任务与交接模板 | [.agents/templates/](.agents/templates/) |
| 团队管理、权限系统、角色创建 | [.agents/teams/](.agents/teams/) |
| flexloop 子模块治理团队（版本管理/边界合规/沙箱安全/模式萃取） | [.agents/teams/flexloop-team.md](.agents/teams/flexloop-team.md) |
| flexloop 团队工作流操作手册（详细步骤/验证清单/应急处理） | [.agents/teams/flexloop-team-operations.md](.agents/teams/flexloop-team-operations.md) |
| Trae 边界情况处理（IDE集成/论坛操作/工具链/Work） | [.agents/teams/trae-edge-case-handler.md](.agents/teams/trae-edge-case-handler.md) |
| 团队协作执行、环境管理 | [.agents/worlds/](.agents/worlds/) |
| Git 忽略规则验证 | [.agents/scripts/check-gitignore.py](.agents/scripts/check-gitignore.py) |
| vendor 目录合规性验证 | [.agents/scripts/check-vendor.py](.agents/scripts/check-vendor.py)（`--deep` 执行 submodule 深度集成验证：初始化状态、工作树清洁度、元数据一致性、非法引用、测试隔离） |
| 链接有效性验证与自动修复 | [.agents/scripts/check-links.py](.agents/scripts/check-links.py)（`--fix` 自动修复相对路径层级错误、绝对路径转换；`--check-external` 检查外部 URL 可达性，结果缓存7天） |
| 文件路径迁移 | [.agents/scripts/check-move.py](.agents/scripts/check-move.py) |
| 角色权限验证 | [.agents/scripts/check-role-permissions.py](.agents/scripts/check-role-permissions.py) |
| 派生产物溯源 | [.agents/scripts/check-source-traceability.py](.agents/scripts/check-source-traceability.py) |
| 阶段守卫日志分析 | [.agents/scripts/check-stage-guardrails.py](.agents/scripts/check-stage-guardrails.py)（`--log-file <path>` 分析SG-LOG/PDR-LOG，检测拦截/跳转/缺失异常；`--demo` 演示） |
| 阶段守卫日志可视化仪表盘 | [.agents/scripts/generate-sg-dashboard.py](.agents/scripts/generate-sg-dashboard.py)（`--demo` 生成8会话示例仪表盘；默认扫描 `.agents/logs/` 聚合多会话日志输出HTML到 `.agents/reports/sg-dashboard.html`；`--json` 输出JSON数据） |
| 规格一致性验证 | [.agents/scripts/check-spec-consistency.py](.agents/scripts/check-spec-consistency.py) |
| Spec 全局看板与7主题分类体系 | [.trae/specs/README.md](.trae/specs/README.md)（创建新 spec 前必读：归类决策树、主题边界定义、命名规范） |
| Spec 主题目录看板 | [.trae/specs/](.trae/specs/)（core-foundation/roles-governance/standards-tools/readme-branding/docs-restructure/retrospectives-insights/migration-archival 各主题 README.md） |
| 导航表生成 | [.agents/scripts/generate-nav.py](.agents/scripts/generate-nav.py) |
| Spec 执行进度看板自动生成 | [.agents/scripts/generate-dashboard.py](.agents/scripts/generate-dashboard.py)（扫描 `.trae/specs/` 聚合状态，自动更新根 README.md 看板） |
| 原子化操作一键收尾 | [.agents/scripts/finalize-atomization.py](.agents/scripts/finalize-atomization.py)（原子化/文件移动后自动断链修复、导航更新、看板刷新） |
| 文件引用反向索引 | [.agents/scripts/build-ref-index.py](.agents/scripts/build-ref-index.py)（构建 `{目标:[引用方]}` 索引，移动/删除文件前查询受影响范围） |
| 测试骨架生成 | [.agents/scripts/generate-tests.py](.agents/scripts/generate-tests.py) |
| 项目脚手架初始化 | [.agents/scripts/agents.py](.agents/scripts/agents.py) init |
| 共享工具库 | [.agents/scripts/lib/](.agents/scripts/lib/) |
| CI 综合检查 | [.agents/scripts/ci-check.ps1](.agents/scripts/ci-check.ps1) / [ci-check.sh](.agents/scripts/ci-check.sh) |
| 原子化覆盖率预检 | [.agents/scripts/check-atomization-coverage.py](.agents/scripts/check-atomization-coverage.py) |
| 原子化内容一致性 | [.agents/scripts/check-atomization-duplication.py](.agents/scripts/check-atomization-duplication.py) |
| 复盘报告归类验证 | [.agents/scripts/check-report-categorization.py](.agents/scripts/check-report-categorization.py) |
| 技术知识库查阅 | [docs/knowledge/README.md](docs/knowledge/README.md) |
| 复盘体系与可复用模式 | [docs/retrospective/README.md](docs/retrospective/README.md) |
| 可复用模式库（架构/代码/方法论） | [docs/retrospective/patterns/](docs/retrospective/patterns/) |
| 资产清单与复用指南 | [docs/retrospective/assets/asset-inventory.md](docs/retrospective/assets/asset-inventory.md) |
| 任务执行总结 | [docs/task-summaries/](docs/task-summaries/) |
| 提示词工程模式 | [docs/retrospective/prompt-extraction.md](docs/retrospective/prompt-extraction.md) |
| 提示词萃取系统 | [prompt_extraction/](prompt_extraction/) |
| 提示词萃取系统架构 | [.agents/systems/prompt-extraction.md](.agents/systems/prompt-extraction.md) |
| 项目复用案例 | [.agents/cases/agentforge-adoption.md](.agents/cases/agentforge-adoption.md) |
| 指令集（复盘/洞察/导出报告/原子化/原子提交） | [.agents/commands/](.agents/commands/) |
| 硬编码治理规则体系 | [.agents/rules/](.agents/rules/) |
| 硬编码识别与判断 | [.agents/rules/identification-standards.md](.agents/rules/identification-standards.md) |
| 硬编码替代方案查找 | [.agents/rules/alternatives-guide.md](.agents/rules/alternatives-guide.md) |
| 硬编码例外申请与审批 | [.agents/rules/allowable-scenarios.md](.agents/rules/allowable-scenarios.md) |
| 硬编码检测与报告 | [.agents/rules/detection-and-reporting.md](.agents/rules/detection-and-reporting.md) |
| 硬编码治理规则执行 | [.agents/rules/enforcement-guidelines.md](.agents/rules/enforcement-guidelines.md) |
| 开发流程阶段守卫（阶段边界/拦截/审批/结构化日志SG-LOG） | [.agents/rules/stage-guardrails.md](.agents/rules/stage-guardrails.md) |
| 前置文档强制读取协议（必读清单/确认机制/结构化日志PDR-LOG） | [.agents/protocols/pre-document-reading.md](.agents/protocols/pre-document-reading.md) |
| 阶段守卫日志分析工具（SG-LOG/PDR-LOG离线检测拦截/跳转/缺失异常） | [.agents/scripts/check-stage-guardrails.py](.agents/scripts/check-stage-guardrails.py) |
| 阶段守卫运行时强制执行（状态管理/边界校验/拦截格式化/运行时门面） | [.agents/scripts/check-stage-guardrail-runtime.py](.agents/scripts/check-stage-guardrail-runtime.py) |
| 阶段守卫日志聚合可视化仪表盘 | [.agents/scripts/generate-sg-dashboard.py](.agents/scripts/generate-sg-dashboard.py) |
| 功能演进分类（新功能/扩展/重构三路径） | [.agents/workflows/feature-development.md](.agents/workflows/feature-development.md) |
| 应用开发生命周期（.temp/ → apps/ 迁移） | [.agents/protocols/app-development-workflow.md](.agents/protocols/app-development-workflow.md) |
| vendor 区域入口路由（三层路由中间层） | [vendor/AGENTS.md](vendor/AGENTS.md)（子模块路由表、可用资产索引、跨边界调用规范、边界声明） |
| 外部子模块协同集成方案（git submodule） | [docs/knowledge/VENDOR-INTEGRATION.md](docs/knowledge/VENDOR-INTEGRATION.md)（边界划分、版本控制、更新同步、测试隔离、模式萃取） |
| 能力边界声明 | [.agents/capability-boundaries.md](.agents/capability-boundaries.md) |
| 完整开发规范 | [docs/development-standards.md](docs/development-standards.md) |
