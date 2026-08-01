---
id: "docs-retrospective-patterns-methodology-patterns-ai-collaboration-index"
title: "AI 协作模式"
x-toml-ref: "../../../../../../.meta/toml/.agents/docs/retrospective/patterns/methodology-patterns/ai-collaboration/README.toml"
category: "retrospective"
date: "2026-07-09"
---
# AI 协作模式

> 本目录 README 由 `generate-readme.py` 自动生成，可根据需要补充概述和导航说明。

<!-- README_INDEX_START -->

## 📄 文档索引

| 文档 | 说明 | 成熟度 | 标签 |
|------|------|--------|------|
| [行动优先输出范式（Action-First Output Paradigm）](action-first-output-paradigm.md) | 默认结论前置、分层展开的Agent输出结构，包含答案第一行、步骤编号单步、进度重述、压制离题四大规则，以及首屏核心区/中间详细区/可选补充区黄金结构 | L2 | `AI输出` `行动优先` `结论前置` `结构化输出` |
| [对抗式审查 Prompt 模式（Adversarial Review Prompt Pattern）](adversarial-review-prompt-pattern.md) | 对抗式审查 Prompt 模式（Adversarial Review Prompt Pattern） | L2 | `提示词工程` `对抗式审查` `代码审查` |
| [AI Agent 工作手册模式：.agents/ 目录让智能体高效参与项目](ai-agent-workspace-handbook.md) | AI Agent 工作手册模式：.agents/ 目录让智能体高效参与项目 | - |  |
| [AI Skill 判断层设计模式](ai-skill-judgment-layer.md) | AI Skill 判断层设计模式 | L2 |  |
| [主动介入 Agent 模式（Ambient Proactive Agent）](ambient-proactive-agent.md) | 主动介入 Agent 模式（Ambient Proactive Agent） | - |  |
| [分批创作+独立质检模式](batched-creation-independent-review.md) | 分批创作+独立质检模式 | L2 |  |
| [双语提示词工程（Bilingual Prompt Engineering）](bilingual-prompt-engineering.md) | 双语提示词工程（Bilingual Prompt Engineering） | L2 |  |
| [Context 恢复协议重执行模式（Context Recovery Protocol Rerun）](context-recovery-protocol.md) | Context 恢复协议重执行模式（Context Recovery Protocol Rerun） | L2 |  |
| [上下文生命周期分层管理模式（Context Lifecycle Layering）](context-lifecycle-layering.md) | 五层生命周期光谱：从全局事实→局部规则→懒加载技能→隔离执行→代码硬护栏，沿"信任模型→机制保障"连续光谱排列，解决全局文件膨胀、护栏提示词化、主会话干脏活等问题 | L2 | `agent架构` `上下文管理` `生命周期分层` `护栏下沉` `子代理隔离` |
| [双区开发模型](dual-zone-development-model.md) | 双区开发模型 | L2 |  |
| [生态壁垒评估框架（Ecosystem Barrier Evaluation）](ecosystem-barrier-evaluation.md) | 生态壁垒评估框架（Ecosystem Barrier Evaluation） | L2 |  |
| [编辑-验证分离模式](edit-verify-separation.md) | 编辑-验证分离模式 | L2 | `ai-collaboration` `quality-assurance` `workflow` |
| [外部内容事实验证](external-content-fact-verification.md) | 外部内容事实验证 | L2 | `ai-collaboration` `fact-checking` `hallucination-defense` |
| [细粒度最小权限模式](fine-grained-least-privilege.md) | 细粒度最小权限模式 | L1 | `security` `least-privilege` `permission-model` |
| [一等公民抽象模式](first-citizen-abstraction.md) | 一等公民抽象模式 | - |  |
| [第一性原理 Prompt 模式（First-Principles Prompt Pattern）](first-principles-prompt-pattern.md) | 第一性原理 Prompt 模式（First-Principles Prompt Pattern） | L3 | `提示词工程` `第一性原理` `Prompt模式` |
| [PS5防御性Prompt模板模式（PS5-Defensive-Prompt）](ps5-defensive-prompt.md) | PS5防御性Prompt模板模式：完整版系统Prompt（7大约束：版本/禁用语法/API/编码/CLM/安全/质量）+精简版快速Prompt+3种场景变体（脚本开发/CI-CD/系统管理），解决AI默认生成PS7+语法在Windows PowerShell 5.1下ParserError问题 | L1 | `powershell` `defensive-prompt` `ai-coding` `version-compatibility` `clm` `security` `prompt-engineering` |
| [提示词到产品七步法（Prompt-to-Product Seven Steps）](prompt-to-product-seven-steps.md) | 从一段能跑的提示词到产品级AI Skill的七步工程化框架：场景细分→统一设计语言→知识盲区补全→反模式规避→精确约束→语义层处理→QA闭环，解决AI生成内容的一致性、准确性、质量可控问题 | L1 | `Skill开发` `提示词工程` `产品化` `工程化方法论` `AI工具开发` `质量闭环` |
| [生成-验证闭环模式（Generation-Validation Closed Loop）](generation-validation-closed-loop.md) | 生成-验证闭环模式（Generation-Validation Closed Loop） | L2 | `生成-验证闭环` `first-principles` `adversarial-review` |
| [Gotchas 领域特化：在通用模板框架上补充模块特有陷阱](gotchas-domain-specialization.md) | Gotchas 领域特化：在通用模板框架上补充模块特有陷阱 | L1 |  |
| [诚实承认局限性信任构建策略](honest-limitation-acknowledgment.md) | 诚实承认局限性信任构建策略 | L1 | `信任构建` `局限性承认` `诚实沟通` |
| [人机协作70/30分工定律（Human-AI Collaboration 70/30 Rule）](human-ai-collaboration-70-30-rule.md) | 人机协作70/30分工定律（Human-AI Collaboration 70/30 Rule） | L2 | `人机协作` `70/30定律` `分工` |
| [「辅助人工」而非「全自动」的人机协作设计](human-in-the-loop-augmentation.md) | 「辅助人工」而非「全自动」的人机协作设计 | L2 | `人机协作` `Human-in-the-loop` `AI辅助` |
| [隔离优于共享模式](isolation-over-sharing.md) | 隔离优于共享模式 | - |  |
| [Markdown即接口：用Markdown同时承载人类阅读与机器调用](markdown-as-interface.md) | Markdown即接口：用Markdown同时承载人类阅读与机器调用 | L4 |  |
| [分层缓存模式（Layered Caching Pattern）](layered-caching-pattern.md) | 三层缓存架构（系统提示层/会话记忆层/语义相似层），整体成本降低60-85%，TTFT降低50-80%，适用于多轮对话、代码助手、Agent等有大量重复内容的场景 | L2 | `LLM` `Token优化` `缓存` `Prompt Caching` `语义缓存` |
| [按需加载懒加载模式（Lazy Loading Pattern）](lazy-loading-pattern.md) | 初始只加载元数据，真正需要时才加载完整内容，MCP场景token降低46.9%+，适用于多工具Agent、代码助手、RAG系统 | L2 | `LLM` `Token优化` `懒加载` `MCP` `按需加载` |
| [LLM Token优化反模式集](llm-token-optimization-anti-patterns.md) | 7个最常见的Token优化反模式（过度压缩/为优化而优化/忽略缓存预热/一刀切/忽视输出/无限重试/不监控），附现象、根因、正确做法、真实案例 | L2 | `LLM` `Token优化` `反模式` `陷阱` `误区` |
| [分层分治MapReduce模式（MapReduce Divide and Conquer）](mapreduce-divide-conquer.md) | 超长文档处理模式：语义分块→并行Map→递归Reduce，100K文档成本降低70-85%，解决O(n²)复杂度和Lost in the Middle问题 | L2 | `LLM` `Token优化` `长上下文` `MapReduce` `分治` |
| [中等规模任务合并委派策略（Medium-Scale Task Merged Delegation Strategy）](medium-task-merged-delegation-strategy.md) | 中等规模任务合并委派策略（Medium-Scale Task Merged Delegation Strategy） | L2 | `子代理委派` `任务合并` `任务拆分` |
| [模块级 .agents/ 扩展模式：通过继承避免重复，仅补充模块特化](module-level-agents-extension.md) | 模块级 .agents/ 扩展模式：通过继承避免重复，仅补充模块特化 | L1 |  |
| [导航枢纽文件名契约模式：全局清单 vs 局部清单](navigation-hub-filename-contract.md) | [引言内容] | L1 |  |
| [安全不打扰UX模式](non-intrusive-security-ux.md) | 安全不打扰UX模式 | L1 | `security` `ux` `ai-agent` |
| [输出行为规范（Output Behavior Specification）](output-behavior-specification.md) | 输出行为规范（Output Behavior Specification） | L2 |  |
| [输出格式-协作能力映射（Output Format – Collaboration Capability Mapping）](output-format-collaboration-capability.md) | 输出格式-协作能力映射（Output Format – Collaboration Capability Mapping） | - |  |
| [决策前三查检查清单（Pre-Decision Three Checks）](pre-decision-three-checks.md) | 决策前三查检查清单（Pre-Decision Three Checks） | L2 | `决策检查` `第一性原理` `防错机制` |
| [上下文渐进式披露（Progressive Context Disclosure）](progressive-context-disclosure.md) | 上下文渐进式披露（Progressive Context Disclosure） | L2 |  |
| [渐进式优化模式（Progressive Optimization Pattern）](progressive-optimization-pattern.md) | 按ROI分层递进优化：可观测性→Quick Wins→场景化优化→高级优化→持续迭代，5步实现85-95%成本降低，适用于所有LLM成本优化场景 | L2 | `LLM` `Token优化` `渐进式优化` `ROI` `成本优化` |
| [渐进式模板化（Progressive Templating）](progressive-templating.md) | 渐进式模板化（Progressive Templating） | L1 |  |
| [质量-成本动态平衡模式（Quality-Cost Dynamic Balance）](quality-cost-dynamic-balance.md) | 三级模型路由+分级压缩+A/B测试，在质量约束下最小化成本，成本降低40-85%且质量保持率>95%，解决一刀切问题 | L2 | `LLM` `Token优化` `质量平衡` `模型路由` `A/B测试` |
| [references/ 渐进式披露：通过引用已有知识文档避免内容重复](references-progressive-disclosure.md) | references/ 渐进式披露：通过引用已有知识文档避免内容重复 | L1 |  |
| [Skill 发现协议增强 SOP](skill-discovery-protocol.md) | Skill 发现协议增强 SOP | L1 |  |
| [Skill 五要素模型（Skill Five Elements Model）](skill-five-elements-model.md) | Skill 五要素模型（Skill Five Elements Model） | L1 |  |
| [Skill渐进式披露封装模式（SKILL.md Metadata + Python Executor）](skill-progressive-disclosure-encapsulation.md) | Skill渐进式披露封装模式（SKILL.md Metadata + Python Executor） | L1 |  |
| [Skill标准化操作流程模式（Four Principles for Workflow Skill Design）](skill-standardized-workflow-pattern.md) | Skill标准化操作流程模式（Four Principles for Workflow Skill Design） | L1 |  |
| [AI Skill 三层价值模型](skill-three-layer-value-model.md) | AI Skill 三层价值模型 | L2 |  |
| [苏格拉底提问纠错模式（Socratic Questioning Correction）](socratic-questioning-correction.md) | 苏格拉底提问纠错模式（Socratic Questioning Correction） | L1 | `苏格拉底提问` `纠错方式` `协作模式` |
| [源码锚点二次校验协议：研究-编写阶段的质量传递契约](source-anchor-verification-protocol.md) | 源码锚点二次校验协议：研究-编写阶段的质量传递契约 | L1 |  |
| [Spec 驱动 + 知识库驱动的文档批量产出模式](spec-driven-batch-doc-generation.md) | Spec 驱动 + 知识库驱动的文档批量产出模式 | - |  |
| [Spec 驱动子代理执行模式](spec-driven-subagent-execution.md) | Spec 驱动子代理执行模式 | - |  |
| [Spec Mode文档创建工作流：前置规划→原子执行→门禁验证](spec-mode-doc-creation-workflow.md) | Spec Mode文档创建工作流：前置规划→原子执行→门禁验证 | L2 |  |
| [Spec 模式第七阶段独立验证机制](spec-stage7-independent-validation.md) | Spec 模式第七阶段独立验证机制 | L1 | `spec-mode` `independent-validation` `checklist` |
| [风格-创意分离控制（Style-Creativity Separation Control）](style-creativity-separation-control.md) | 风格-创意分离控制（Style-Creativity Separation Control） | L2 |  |
| [子代理原子任务描述模板：六要素精确委托法](subagent-atomic-task-template.md) | [...按照要素3的结构化大纲写正文内容...] | L2 |  |
| [子代理"三不准"执行规范（Subagent Git Three Prohibitions）](subagent-git-three-prohibitions.md) | 子代理"三不准"执行规范（Subagent Git Three Prohibitions） | L1 |  |
| [症状-处方 QA 系统（Symptom-Prescription QA）](symptom-prescription-qa.md) | 症状-处方 QA 系统（Symptom-Prescription QA） | L2 |  |
| [任务类型预检防偏差](task-type-precheck-bias-defense.md) | 任务类型预检防偏差 | L2 |  |
| [团队共享 AI 同事模式（Team Shared AI Colleague）](team-shared-ai-colleague.md) | 团队共享 AI 同事模式（Team Shared AI Colleague） | - |  |
| [模板质量方差控制模式（Template Variance Control）](template-variance-control.md) | 模板质量方差控制模式（Template Variance Control） | L1 |  |
| [工具采纳漏斗（Tool Adoption Funnel）](tool-adoption-funnel.md) | 工具采纳漏斗（Tool Adoption Funnel） | - |  |
| [篇幅控制两阶段模式：先大纲后展开](two-stage-outline-then-expand.md) | 篇幅控制两阶段模式：先大纲后展开 | L1 |  |
| [用户主权默认模式](user-sovereignty-default.md) | 用户主权默认模式 | L1 | `security` `ai-agent` `trust` |
| [视觉操作闭环模式（Screenshot-Locate-Operate-Verify Loop）](visual-operation-closed-loop.md) | 视觉操作闭环模式（Screenshot-Locate-Operate-Verify Loop） | L1 |  |
| [视觉通用操作模式（Visual-based Universal Operation）](visual-universal-operation.md) | 视觉通用操作模式（Visual-based Universal Operation） | L2 |  |


<!-- README_INDEX_END -->

## 🔗 相关资源

- [🏠 返回上级：方法论模式](../README.md)
- [📚 文档首页](../../../../README.md)

---

<!-- generated by generate-readme.py on 2026-07-18 -->
