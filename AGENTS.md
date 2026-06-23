# 智能体全局契约 (AGENTS Manifest)

本文件是项目 AI 智能体的最高优先级入口与上下文路由。所有智能体在启动时必须首先读取本文件，依据上下文路由表定位到具体的 `.agents/` 规范，再加载对应的角色定义、系统提示词与协作协议后执行任务。

## 全局核心规则

- **沟通语言**：必须使用中文与用户交流，所有输出、注释、提交信息、文档均以中文为主。
- **按需读取**：执行特定领域任务前，只读取与当前任务直接相关的 `.agents/` 规范，避免一次性加载全部上下文。
- **上下文节省**：遵循"先搜索、再精读、只保留相关上下文"的原则，优先使用语义检索与精确匹配工具，剔除无关片段。
- **Mermaid 优先**：流程、架构、关系、状态机等可视化逻辑优先使用 Mermaid 表达，确保可渲染、可版本化。
- **代码修改**：遵循"约定优于配置"，优先参考现有代码风格、命名规范与目录结构，不引入与项目不一致的新风格。
- **禁止提交临时依赖**：禁止将 `vendor/`、`.temp/`、`__pycache__/`、`.venv/`、`node_modules/` 等临时依赖和中间产物提交至 Git 仓库。
- **查阅知识库**：执行任务前应主动查阅 [docs/knowledge/README.md](docs/knowledge/README.md) 技术知识库与 [docs/retrospective/README.md](docs/retrospective/README.md) 复盘文档体系，了解已有经验、架构决策、可复用模式与最佳实践，避免重复踩坑。

## 角色定义索引

| 角色 | ID | 职责 | 入口 |
|---|---|---|---|
| 编排协调者 | orchestrator | 任务分配、流程协调、冲突仲裁 | .agents/roles/orchestrator.md |
| 架构师 | architect | 技术方案设计、架构决策 | .agents/roles/architect.md |
| 开发者 | developer | 代码实现、重构、缺陷修复 | .agents/roles/developer.md |
| 代码审查者 | reviewer | 代码质量审查、规范校验 | .agents/roles/reviewer.md |
| 测试工程师 | tester | 测试用例编写、执行、覆盖率 | .agents/roles/tester.md |
| 联合创始者 | co-founder | 愿景确立、协作契约奠基、关键决策仲裁 | .agents/roles/co-founder.md |
| 团队管理员 | team-admin | 团队创建管理、权限分配、新角色自动创建 | .agents/teams/team-admin.md |

## 自我演进模块索引

| 模块 | ID | 所属层级 | 入口 |
|---|---|---|---|
| 自我洞察 | self-insight | 感知层 | .agents/modules/self-insight.md |
| 自我复盘 | self-retrospective | 感知层 | .agents/modules/self-retrospective.md |
| 自我萃取 | self-extraction | 认知层 | .agents/modules/self-extraction.md |
| 自我进化 | self-evolution | 认知层 | .agents/modules/self-evolution.md |
| 自我迭代 | self-iteration | 执行层 | .agents/modules/self-iteration.md |
| 自我验证 | self-verification | 执行层 | .agents/modules/self-verification.md |
| 自我管理 | self-management | 治理层 | .agents/modules/self-management.md |
| 自我发展 | self-development | 治理层 | .agents/modules/self-development.md |

## 能力边界声明

- **编排协调者 (orchestrator)**：不直接编写业务代码；不替代架构师做技术决策。
- **架构师 (architect)**：不负责代码实现细节；不执行测试用例编写。
- **开发者 (developer)**：不擅自变更架构决策；不绕过审查直接合并代码。
- **代码审查者 (reviewer)**：不直接修改业务代码；不替代测试工程师执行验收测试。
- **测试工程师 (tester)**：不负责生产环境部署；不擅自修改业务逻辑代码。
- **团队管理员 (team-admin)**：不直接编写业务代码；不擅自变更架构决策；不越权管理其他团队；新角色创建须满足触发条件。

## 协作协议概要

| 协议 | 用途 | 入口 |
|---|---|---|
| 任务交接 | 智能体间任务转移 | .agents/protocols/handoff.md |
| 消息传递 | 智能体间通信 | .agents/protocols/messaging.md |
| 冲突解决 | 分歧仲裁 | .agents/protocols/conflict-resolution.md |
| 临时依赖管理 | 依赖存放与清理 | .agents/protocols/dependency-management.md |

## 工具规范索引

| 类别 | 规范文件 | 涵盖工具 | 适用场景 |
|---|---|---|---|
| 文件操作 | .agents/tools/file-operations.md | read_file、write_file、edit_file、delete_file、list_directory | 文件读写、编辑、删除、目录列举 |
| 代码执行 | .agents/tools/code-execution.md | run_command、run_tests、build_project | 终端命令执行、测试运行、项目构建 |
| 搜索 | .agents/tools/search.md | grep_search、glob_find、semantic_search | 内容正则搜索、文件名匹配、语义搜索 |
| 通信 | .agents/tools/communication.md | send_message、handoff_task、sync_status | 智能体间消息传递、任务交接、状态同步 |

## 标准工作流索引

| 工作流 | 适用场景 | 参与角色 | 入口 |
|---|---|---|---|
| 功能开发 | 新功能开发 | 全部角色 | .agents/workflows/feature-development.md |
| 代码审查 | PR 审查 | developer, reviewer, orchestrator | .agents/workflows/code-review.md |
| 测试流程 | 测试执行 | tester, developer, reviewer | .agents/workflows/testing.md |

## 模板索引

| 模板 | 用途 | 使用场景 | 入口 |
|---|---|---|---|
| 任务模板 | 任务定义 | 创建新任务时 | .agents/templates/task-template.md |
| 交接模板 | 任务交接 | 智能体间任务转移时 | .agents/templates/handoff-template.md |

## 提示词索引

| 角色 | 系统提示词 | Few-shot 示例 |
|---|---|---|
| 编排协调者 | .agents/prompts/orchestrator/system-prompt.md | .agents/prompts/orchestrator/few-shot.md |
| 架构师 | .agents/prompts/architect/system-prompt.md | .agents/prompts/architect/few-shot.md |
| 开发者 | .agents/prompts/developer/system-prompt.md | .agents/prompts/developer/few-shot.md |
| 代码审查者 | .agents/prompts/reviewer/system-prompt.md | .agents/prompts/reviewer/few-shot.md |
| 测试工程师 | .agents/prompts/tester/system-prompt.md | .agents/prompts/tester/few-shot.md |

## 开发规范

### 代码风格

- 遵循现有代码风格，不引入与项目不一致的新风格。
- 命名、缩进、注释、文件组织均以仓库内既有约定为准。
- 新增依赖前先评估必要性，优先复用现有工具链。

### 提交规范

- 遵循 Conventional Commits 规范，格式为 `type(scope): subject`。
- 常用类型：`feat`、`fix`、`refactor`、`test`、`docs`、`chore`、`perf`。
- 提交信息主体使用中文描述，简明扼要说明"为什么"而非仅"做了什么"。

### 文档边界

- `README.md` 面向人类读者，介绍项目用途、安装、使用与贡献方式。
- `.agents/` 面向 AI 智能体，存放角色、提示词、协议、工作流等机器可读规范。
- 两者职责分离，不相互混用。

### 派生产物溯源

- 从源文档（如 `README.md`、spec 文档）派生出的结构化产物，须在 TOML frontmatter 携带 `source` 字段标注来源，格式为 `source = "<文件>#<章节>"`。
- 使用 `.agents/scripts/check-source-traceability.py --affected <源文件>` 可查询源变更的受影响产物清单。详见 [开发规范](docs/development-standards.md)。

## 测试要求

### 单元测试

- 每个模块必须有对应的单元测试，覆盖核心逻辑与边界条件。
- 测试命名清晰，能够表达被测行为与预期结果。

### 覆盖率

- 整体测试覆盖率不低于 80%。
- 关键模块与核心业务逻辑覆盖率应达到 90% 以上。

### 验收标准

- 所有测试用例通过。
- 无新增失败用例，无回归问题。
- 覆盖率达标且关键路径均有断言。

## 上下文路由表

| 任务类型 | 必读入口 |
|---|---|
| 角色定义、职责分工 | .agents/roles/ |
| 自我演进模块定义 | .agents/modules/ |
| 系统提示词、few-shot | .agents/prompts/ |
| 工具调用规范 | .agents/tools/ |
| 协作协议、通信机制 | .agents/protocols/ |
| 标准工作流 | .agents/workflows/ |
| 任务与交接模板 | .agents/templates/ |
| 团队管理、权限系统、角色创建 | .agents/teams/ |
| 团队协作执行、环境管理 | .agents/worlds/ |
| Git 忽略规则验证 | .agents/scripts/check-gitignore.py |
| 链接有效性验证 | .agents/scripts/check-links.py |
| 文件路径迁移 | .agents/scripts/check-move.py |
| 角色权限验证 | .agents/scripts/check-role-permissions.py |
| 派生产物溯源 | .agents/scripts/check-source-traceability.py |
| 规格一致性验证 | .agents/scripts/check-spec-consistency.py |
| 导航表生成 | .agents/scripts/generate-nav.py |
| CI 综合检查 | .agents/scripts/ci-check.ps1 / ci-check.sh |
| 技术知识库查阅 | docs/knowledge/README.md |
| 复盘体系与可复用模式 | docs/retrospective/README.md |
| 可复用模式库（架构/代码/方法论） | docs/retrospective/patterns/ |
| 资产清单与复用指南 | docs/retrospective/assets/asset-inventory.md |
| 任务执行总结 | docs/task-summaries/ |
| 提示词工程模式 | docs/retrospective/prompt-extraction.md |
| 提示词萃取系统 | prompt_extraction/ |
