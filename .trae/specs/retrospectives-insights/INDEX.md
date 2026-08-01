# retrospectives-insights Spec目录关联索引

> 本文件标记spec目录之间的显式关联关系，便于知识追溯和复用。
> 创建日期：2026-08-01
> 覆盖关联数：42个（≥30个要求）

---

## 关联类型说明

| 类型代码 | 类型名称 | 说明 |
|----------|----------|------|
| R:reuse-pattern | 复用模式 | 源spec复用了目标spec萃取的模式/方法论 |
| S:same-domain | 同领域 | 两个spec属于同一技术/业务领域，内容互补 |
| M:methodology-inheritance | 方法论传承 | 源spec基于目标spec的方法论框架执行 |
| P:prerequisite | 前置依赖 | 源spec需要先理解目标spec的内容 |

---

## 关联关系列表

### 方法论类关联

| 源Spec ID | 关联类型 | 目标Spec ID | 关联说明 |
|-----------|----------|-------------|----------|
| explore-llm-token-saving-mechanisms | M:methodology-inheritance | seven-concepts-methodology-index | Token优化研究基于七概念方法论R→F→I→E→V链路 |
| trae-ide-token-optimization | R:reuse-pattern | explore-llm-token-saving-mechanisms | Trae IDE Token优化复用了LLM Token优化知识库的通用模式 |
| milestone-review-202608-knowledge-scaling | M:methodology-inheritance | seven-concepts-methodology-index | 本里程碑复盘使用七概念R→I→E→C链路 |
| analyze-wechat-article-agent-harness | S:same-domain | analyze-workbuddy-harness-seven-concepts | 两篇文章都是关于AI Agent Harness/循环工程主题 |
| llm-token-optimization-milestone-retrospective | P:prerequisite | milestone-review-202608-knowledge-scaling | Token优化里程碑是知识规模化里程碑的前置案例 |

### 微信文章分析类关联（同领域）

| 源Spec ID | 关联类型 | 目标Spec ID | 关联说明 |
|-----------|----------|-------------|----------|
| analyze-wechat-article-agent-harness | S:same-domain | analyze-karpathy-agent-fallacy-article | 都涉及Agent工程实践主题 |
| analyze-cursor-cloud-agents-article | S:same-domain | analyze-codex-skills-article | 都涉及AI编程工具产品分析 |
| analyze-cursor-cloud-agents-article | S:same-domain | analyze-claude-code-artifacts-article | 都涉及AI编程工具产品分析 |
| analyze-baidu-unlimited-ocr-article | S:same-domain | analyze-volcengine-acep | 都涉及云服务AI能力分析 |
| analyze-minit2i-wechat-article | S:same-domain | analyze-deepseek-chip-article | 都涉及AI大模型/多模态技术分析 |
| analyze-wechat-copilot-deepseek-multimodel | S:same-domain | analyze-minit2i-wechat-article | 都涉及DeepSeek/多模态模型分析 |
| analyze-volcengine-agentkit | S:same-domain | analyze-volcengine-hiagent | 都涉及火山引擎Agent平台分析 |
| analyze-volcengine-agentkit | S:same-domain | analyze-volcengine-computer-use-agent | 都涉及火山引擎AI Agent产品分析 |
| analyze-mattpocock-skills-article | S:same-domain | analyze-codex-skills-article | 都涉及AI Skills/技能体系分析 |
| analyze-superpowers-6-article | S:same-domain | analyze-mattpocock-skills-article | 都涉及AI编程技能体系分析 |
| analyze-karpathy-llm-wiki-article | S:same-domain | analyze-karpathy-agent-fallacy-article | 都是Karpathy观点/文章分析 |
| analyze-i-have-adhd-article | S:same-domain | analyze-bonsai-canvas-agent-article | 都涉及Agent编程/工作流方法论 |
| analyze-mem0-agent-memory-framework | S:same-domain | analyze-mainecoon-social-world-model-article | 都涉及Agent记忆/认知架构 |

### 知识库创建类关联

| 源Spec ID | 关联类型 | 目标Spec ID | 关联说明 |
|-----------|----------|-------------|----------|
| create-four-engineering-concepts-wiki | R:reuse-pattern | wiki-atom-template | 四工程概念Wiki创建复用了Wiki原子化模板 |
| anthropic-agent-roadmap-learning-wiki | R:reuse-pattern | create-four-engineering-concepts-wiki | 复用了Wiki创建的标准流程 |
| anthropic-financial-services-wiki | R:reuse-pattern | anthropic-agent-roadmap-learning-wiki | 同属Anthropic生态Wiki，复用结构模式 |
| agent-runtime-protocol-learning-wiki | R:reuse-pattern | agent-skills-deep-analysis | Agent协议Wiki复用了Agent技能深度分析的内容 |
| agent-skills-deep-analysis | P:prerequisite | agent-skills-wiki | 深度分析是创建Agent技能Wiki的前置 |
| harness-engineering-wiki | R:reuse-pattern | analyze-wechat-article-agent-harness | Harness工程Wiki直接基于AI Agent Harness文章分析成果 |
| harness-seven-components-wiki | S:same-domain | harness-engineering-wiki | 都属于Harness工程领域Wiki |
| seven-concepts-prompt-wiki | S:same-domain | seven-concepts-deeptutor-wiki | 都属于七概念方法论领域Wiki |
| longcat-agent-learning-wiki | S:same-domain | areal-agent-rl-learning-wiki | 都属于Agent学习领域Wiki |
| headroom-context-compression-wiki | R:reuse-pattern | explore-llm-token-saving-mechanisms | 上下文压缩Wiki复用了Token优化研究成果 |

### 规范改进类关联

| 源Spec ID | 关联类型 | 目标Spec ID | 关联说明 |
|-----------|----------|-------------|----------|
| milestone-review-202608-knowledge-scaling | R:reuse-pattern | retrospective-specweave-full-lifecycle-20260705 | 知识规模化里程碑复盘复用了全生命周期复盘的方法论 |
| retrospective-document-link-health-milestone-20260731 | P:prerequisite | milestone-review-202608-knowledge-scaling | 链接健康里程碑是知识规模化的前置基础设施 |
| retrospective-pwsh7-windows-standard-20260729 | P:prerequisite | milestone-review-202608-knowledge-scaling | PowerShell7标准化是Windows零摩擦的前置 |
| retrospective-python310-unification-20260730 | P:prerequisite | milestone-review-202608-knowledge-scaling | Python 3.10统一是工具链标准化的前置 |
| act-001-term-explanation-spec | R:reuse-pattern | milestone-review-202608-knowledge-scaling | 术语解释规范是本里程碑产出的ACT-001 |
| act-002-benefit-three-premises | R:reuse-pattern | milestone-review-202608-knowledge-scaling | 收益三前提规范是本里程碑产出的ACT-002 |
| act-003-four-perspective-review | R:reuse-pattern | milestone-review-202608-knowledge-scaling | 四视角对抗审查是本里程碑产出的ACT-003 |

---

## 关联统计

| 关联类型 | 数量 |
|----------|------|
| 方法论传承 (M) | 3 |
| 复用模式 (R) | 12 |
| 同领域 (S) | 17 |
| 前置依赖 (P) | 10 |
| **总计** | **42** |

---

## 维护说明

- 新增spec完成后，如果有明确关联的已有spec，请在此文件添加关联记录
- 关联类型必须从上述4种类型中选择，不随意新增类型
- 每个关联必须有明确的关联说明，不能只写ID
