# 智能体全局契约 (AGENTS Manifest)

本文件是项目 AI 智能体的最高优先级入口与上下文路由。所有智能体在启动时必须首先读取本文件，依据上下文路由表定位到具体的 `.agents/` 规范，再加载对应的角色定义、系统提示词与协作协议后执行任务。

## 全局核心规则

- **沟通语言**：必须使用中文与用户交流，所有输出、注释、提交信息、文档均以中文为主。
- **按需读取**：执行特定领域任务前，只读取与当前任务直接相关的 `.agents/` 规范，避免一次性加载全部上下文。
- **上下文节省**：遵循"先搜索、再精读、只保留相关上下文"的原则，优先使用语义检索与精确匹配工具，剔除无关片段。
- **Mermaid 优先**：流程、架构、关系、状态机等可视化逻辑优先使用 Mermaid 表达，确保可渲染、可版本化。
- **代码修改**：遵循"约定优于配置"，优先参考现有代码风格、命名规范与目录结构，不引入与项目不一致的新风格。
- **禁止提交临时依赖**：禁止将 `vendor/`、`.temp/`、`__pycache__/`、`.venv/`、`node_modules/` 等临时依赖和中间产物提交至 Git 仓库。
- **查阅知识库**：执行任务前应主动查阅 [docs/knowledge/README.md](docs/knowledge/README.md) 知识库索引，了解已有经验、架构决策与最佳实践，避免重复踩坑。

## 角色定义索引

| 角色 | ID | 职责 | 入口 |
|---|---|---|---|
| 编排协调者 | orchestrator | 任务分配、流程协调、冲突仲裁 | .agents/roles/orchestrator.md |
| 架构师 | architect | 技术方案设计、架构决策 | .agents/roles/architect.md |
| 开发者 | developer | 代码实现、重构、缺陷修复 | .agents/roles/developer.md |
| 代码审查者 | reviewer | 代码质量审查、规范校验 | .agents/roles/reviewer.md |
| 测试工程师 | tester | 测试用例编写、执行、覆盖率 | .agents/roles/tester.md |

## 能力边界声明

- **编排协调者 (orchestrator)**：不直接编写业务代码；不替代架构师做技术决策。
- **架构师 (architect)**：不负责代码实现细节；不执行测试用例编写。
- **开发者 (developer)**：不擅自变更架构决策；不绕过审查直接合并代码。
- **代码审查者 (reviewer)**：不直接修改业务代码；不替代测试工程师执行验收测试。
- **测试工程师 (tester)**：不负责生产环境部署；不擅自修改业务逻辑代码。

## 协作协议概要

| 协议 | 用途 | 入口 |
|---|---|---|
| 任务交接 | 智能体间任务转移 | .agents/protocols/handoff.md |
| 消息传递 | 智能体间通信 | .agents/protocols/messaging.md |
| 冲突解决 | 分歧仲裁 | .agents/protocols/conflict-resolution.md |
| 临时依赖管理 | 依赖存放与清理 | .agents/protocols/dependency-management.md |

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
| 系统提示词、few-shot | .agents/prompts/ |
| 工具调用规范 | .agents/tools/ |
| 协作协议、通信机制 | .agents/protocols/ |
| 标准工作流 | .agents/workflows/ |
| 任务与交接模板 | .agents/templates/ |
| Git 忽略规则验证 | .agents/scripts/check-gitignore.py |
