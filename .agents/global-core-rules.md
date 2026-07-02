---
id: "global-core-rules"
title: "全局核心规则"
source: "AGENTS.md#全局核心规则"
x-toml-ref: "../.meta/toml/.agents/global-core-rules.toml"
---
# 全局核心规则

本文件定义项目 AI 智能体必须遵守的全局核心规则，所有角色在执行任何任务时均须遵循。

## 规则列表

- **启动协议优先**：收到任何任务后，首先执行 [AGENTS.md](../AGENTS.md) 顶部的启动协议。在完成步骤 1-3.5（含自检）之前，不得加载任何 Skill 或调用任何生成工具。这是所有其他规则的先决条件——违反此规则会导致所有下游决策失去规范依据，并产生非线性返工成本。特别注意：即使工作目录不在 `vendor/` 内，也必须执行步骤 2.0（任务类型预检）检查是否需要 vendor 方法论资产。
- **沟通语言**：必须使用中文与用户交流，所有输出、注释、提交信息、文档均以中文为主。
- **按需读取**：执行特定领域任务前，只读取与当前任务直接相关的 `.agents/` 规范，避免一次性加载全部上下文。
- **上下文节省**：遵循"先搜索、再精读、只保留相关上下文"的原则，优先使用语义检索与精确匹配工具，剔除无关片段。多文件差异分析场景下采用「结构对比优先、全文精读兜底」策略：先用 Grep 提取标题/签名做结构对比确定差异集，再对差异集文件精读全文确定修改方案，避免全量精读带来的边际收益递减。
- **Mermaid 优先**：流程、架构、关系、状态机等可视化逻辑优先使用 Mermaid 表达，确保可渲染、可版本化。Mermaid 图表须遵循安全编码六规则，详见 [docs/development-standards.md](../docs/development-standards.md#mermaid-编码规范)。
- **代码修改**：遵循"约定优于配置"，优先参考现有代码风格、命名规范与目录结构，不引入与项目不一致的新风格。
- **歧义主动澄清**：遇到需求不明确、存在多种理解方式、或发现更简单方案时，必须先向用户提问澄清或列出选项供用户选择，禁止自行猜测意图并直接实施。若发现用户指定方案存在更优解，应主动提出建议而非静默修改。澄清成本远低于返工成本——提前澄清30秒，可能避免40分钟的错误分支执行。
- **Spec 目录规范**：执行 `/spec` 工作流时，新 spec 目录必须创建在 `.trae/specs/<theme-subdir>/` 对应的 7 大主题子目录下，禁止直接创建在 `.trae/specs/` 根目录。创建前必须查阅 [.trae/specs/README.md](../.trae/specs/README.md) 的归类决策树确定归属主题。
- **禁止提交临时依赖**：禁止将 `.temp/`、`__pycache__/`、`.venv/`、`node_modules/` 等临时依赖和中间产物提交至 Git 仓库。`vendor/` 目录通过 git 子模块管理第三方依赖（追踪 gitlink），仅 `vendor/README.md` 和 `vendor/VERSION.md` 元数据文件直接纳入版本管理，其余 vendor 内容默认忽略。
- **查阅知识库**：执行任务前应主动查阅 [docs/knowledge/README.md](../docs/knowledge/README.md) 技术知识库与 [docs/retrospective/README.md](../docs/retrospective/README.md) 复盘文档体系，了解已有经验、架构决策、可复用模式与最佳实践，避免重复踩坑。

## 关联规范

- 完整开发规范（代码风格、提交规范、文档边界等）：[docs/development-standards.md](../docs/development-standards.md)
- 角色能力边界：[capability-boundaries.md](capability-boundaries.md)
- 上下文路由表：[context-routing.md](context-routing.md)
