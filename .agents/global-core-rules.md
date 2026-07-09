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
- **三阶段递进原则**：所有演化过程（治理、知识库建设、抽象层级提升）严格遵循三阶段递进规律，顺序不可颠倒、中间阶段不可跳过：治理（修复→预防→闭环）、知识库（生成→重组→精确化）、抽象（具体→通用→元方法）。跳过中间阶段必然导致返工或问题复发，详见 [rules/three-stage-universal-principle.md](rules/three-stage-universal-principle.md)。
- **元文档优先原则**：资源有限时，优先优化入口文档、索引、L1门面等元文档（描述文档的文档），而非深化L2内容。元文档篇幅占比<20%但对采纳率贡献>50%，ROI最高。入口文档>100行时优先精简，新增模块时先更新索引再写深度内容，详见 [rules/meta-document-priority-principle.md](rules/meta-document-priority-principle.md)。
- **修复即闭环**：所有Bug修复必须遵循"修复→预防→闭环"三阶段SOP（详见 [rules/fix-prevent-close-loop.md](rules/fix-prevent-close-loop.md)），禁止纯点修复（只修当前问题不建立预防机制）。平凡修复（拼写错误、格式调整、注释修正等）可豁免，但必须在自查时确认符合豁免条件。修复提交必须在commit message中标注预防措施类型。
- **查阅知识库**：执行任务前应主动查阅 [docs/knowledge/README.md](../docs/knowledge/README.md) 技术知识库与 [docs/retrospective/README.md](../docs/retrospective/README.md) 复盘文档体系，了解已有经验、架构决策、可复用模式与最佳实践，避免重复踩坑。
- **简单任务验证原则**：越是"看起来简单、不用想、批量执行"的任务（如格式统一、路径替换、批量修改），越要有意识执行基本验证。简单任务因为缺少Spec流程、代码审查等复杂任务保护层，大脑倾向走直觉捷径（类比推理），错误率反而可能更高。格式/路径/规范类决策必须执行"决策前三查"（查权威文档、查现有实例、查本质目标），详见 [pre-decision-three-checks.md](../docs/retrospective/patterns/methodology-patterns/ai-collaboration/pre-decision-three-checks.md)。来源：[第一性原理类比推理错误事件复盘](../docs/retrospective/reports/incident-reports/retrospective-first-principles-analogy-error-20260709/README.md)。

## 关联规范

- 完整开发规范（代码风格、提交规范、文档边界等）：[docs/development-standards.md](../docs/development-standards.md)
- 角色能力边界：[capability-boundaries.md](capability-boundaries.md)
- 上下文路由表：[context-routing.md](context-routing.md)
