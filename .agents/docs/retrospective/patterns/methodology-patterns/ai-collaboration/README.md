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
| [行动优先Agent输出模式](./action-first-output-paradigm.md) | 行动优先Agent输出模式 | L2 已验证 |  |
| [对抗式审查 Prompt 模式（Adversarial Review Prompt Pattern）](./adversarial-review-prompt-pattern.md) | 对抗式审查 Prompt 模式（Adversarial Review Prompt Pattern） | L2 | `提示词工程` `对抗式审查` `代码审查` |
| [AI Agent 工作手册模式：.agents/ 目录让智能体高效参与项目](./ai-agent-workspace-handbook.md) | AI Agent 工作手册模式：.agents/ 目录让智能体高效参与项目 | - |  |
| [AI 多模态全栈开发闭环（AI Multimodal Full-Stack Development Loop）](./ai-multimodal-fullstack-dev-loop.md) | AI 多模态全栈开发闭环（AI Multimodal Full-Stack Development Loop） | - |  |
| [AI Skill 判断层设计模式](./ai-skill-judgment-layer.md) | AI Skill 判断层设计模式 | L2 |  |
| [AI系统透明优先原则（Transparency Over Cleverness Principle / Human-in-the-Loop by Default）](./ai-transparency-over-cleverness.md) | AI系统透明优先原则（Transparency Over Cleverness Principle / Human-in-the-Loop by Default） | L2 |  |
| [主动介入 Agent 模式（Ambient Proactive Agent）](./ambient-proactive-agent.md) | 主动介入 Agent 模式（Ambient Proactive Agent） | - |  |
| [分批创作+独立质检模式](./batched-creation-independent-review.md) | 分批创作+独立质检模式 | L2 |  |
| [双语提示词工程（Bilingual Prompt Engineering）](./bilingual-prompt-engineering.md) | 双语提示词工程（Bilingual Prompt Engineering） | L2 |  |
| [上下文生命周期分层管理模式](./context-lifecycle-layering.md) | 上下文生命周期分层管理模式 | L2 |  |
| [Context 恢复协议重执行模式（Context Recovery Protocol Rerun）](./context-recovery-protocol.md) | Context 恢复协议重执行模式（Context Recovery Protocol Rerun） | L2 |  |
| [对话Agent四层评测模式（Dialog Agent Four-Layer Evaluation）](./dialog-agent-four-layer-evaluation.md) | 对话Agent四层评测模式（Dialog Agent Four-Layer Evaluation） | L1 | `Agent评测` `对话系统` `四层架构` |
| [双区开发模型](./dual-zone-development-model.md) | 双区开发模型 | L2 |  |
| [生态壁垒评估框架（Ecosystem Barrier Evaluation）](./ecosystem-barrier-evaluation.md) | 生态壁垒评估框架（Ecosystem Barrier Evaluation） | L2 |  |
| [编辑-验证分离模式](./edit-verify-separation.md) | 编辑-验证分离模式 | L2 | `ai-collaboration` `quality-assurance` `workflow` |
| [外部内容事实验证](./external-content-fact-verification.md) | 外部内容事实验证 | L2 | `ai-collaboration` `fact-checking` `hallucination-defense` |
| [外部技术文章学习三阶段闭环（LAV模型）](./external-tech-article-learning-closed-loop.md) | 外部技术文章学习三阶段闭环（LAV模型） | L1 | `ai-collaboration` `knowledge-management` `learning` |
| [文件存在性验证门模式（File Existence Verification Gate）](./file-existence-verification-gate.md) | 文件存在性验证门模式（File Existence Verification Gate） | L2 | `文件验证` `存在性检查` `上下文压缩幻觉` |
| [细粒度最小权限模式](./fine-grained-least-privilege.md) | 细粒度最小权限模式 | L1 | `security` `least-privilege` `permission-model` |
| [一等公民抽象模式](./first-citizen-abstraction.md) | 一等公民抽象模式 | - |  |
| [第一性原理 Prompt 模式（First-Principles Prompt Pattern）](./first-principles-prompt-pattern.md) | 第一性原理 Prompt 模式（First-Principles Prompt Pattern） | L3 | `提示词工程` `第一性原理` `Prompt模式` |
| [生成-验证闭环模式（Generation-Validation Closed Loop）](./generation-validation-closed-loop.md) | 生成-验证闭环模式（Generation-Validation Closed Loop） | L2 | `生成-验证闭环` `first-principles` `adversarial-review` |
| [Gotchas 领域特化：在通用模板框架上补充模块特有陷阱](./gotchas-domain-specialization.md) | Gotchas 领域特化：在通用模板框架上补充模块特有陷阱 | L1 |  |
| [诚实承认局限性信任构建策略](./honest-limitation-acknowledgment.md) | 诚实承认局限性信任构建策略 | L1 | `信任构建` `局限性承认` `诚实沟通` |
| [人机协作70/30分工定律（Human-AI Collaboration 70/30 Rule）](./human-ai-collaboration-70-30-rule.md) | 人机协作70/30分工定律（Human-AI Collaboration 70/30 Rule） | L2 | `人机协作` `70/30定律` `分工` |
| [「辅助人工」而非「全自动」的人机协作设计](./human-in-the-loop-augmentation.md) | 「辅助人工」而非「全自动」的人机协作设计 | L2 | `人机协作` `Human-in-the-loop` `AI辅助` |
| [隔离优于共享模式](./isolation-over-sharing.md) | 隔离优于共享模式 | - |  |
| [分层缓存模式](./layered-caching-pattern.md) | 分层缓存模式 | L2-validated | `LLM` `Token` `Caching` |
| [按需加载懒加载模式](./lazy-loading-pattern.md) | 按需加载懒加载模式 | L2-validated | `LLM` `Token` `Lazy-Loading` |
| [LLM Token优化反模式集](./llm-token-optimization-anti-patterns.md) | LLM Token优化反模式集 | L2-validated | `LLM` `Token` `Optimization` |
| [分层分治MapReduce模式](./mapreduce-divide-conquer.md) | 分层分治MapReduce模式 | L2-validated | `LLM` `Token` `Long-Context` |
| [Markdown即接口：用Markdown同时承载人类阅读与机器调用](./markdown-as-interface.md) | Markdown即接口：用Markdown同时承载人类阅读与机器调用 | L4 |  |
| [中等规模任务合并委派策略（Medium-Scale Task Merged Delegation Strategy）](./medium-task-merged-delegation-strategy.md) | 中等规模任务合并委派策略（Medium-Scale Task Merged Delegation Strategy） | L2 | `子代理委派` `任务合并` `任务拆分` |
| [模块级 .agents/ 扩展模式：通过继承避免重复，仅补充模块特化](./module-level-agents-extension.md) | 模块级 .agents/ 扩展模式：通过继承避免重复，仅补充模块特化 | L1 |  |
| [导航枢纽文件名契约模式：全局清单 vs 局部清单](./navigation-hub-filename-contract.md) | [引言内容] | L2 |  |
| [安全不打扰UX模式](./non-intrusive-security-ux.md) | 安全不打扰UX模式 | L1 | `security` `ux` `ai-agent` |
| [输出行为规范（Output Behavior Specification）](./output-behavior-specification.md) | 输出行为规范（Output Behavior Specification） | L2 |  |
| [输出格式-协作能力映射（Output Format – Collaboration Capability Mapping）](./output-format-collaboration-capability.md) | 输出格式-协作能力映射（Output Format – Collaboration Capability Mapping） | - |  |
| [决策前三查检查清单（Pre-Decision Three Checks）](./pre-decision-three-checks.md) | 决策前三查检查清单（Pre-Decision Three Checks） | L2 | `决策检查` `第一性原理` `防错机制` |
| [上下文渐进式披露（Progressive Context Disclosure）](./progressive-context-disclosure.md) | 上下文渐进式披露（Progressive Context Disclosure） | L2 |  |
| [渐进式优化模式](./progressive-optimization-pattern.md) | 渐进式优化模式 | L2-validated | `LLM` `Token` `Optimization` |
| [渐进式模板化（Progressive Templating）](./progressive-templating.md) | 渐进式模板化（Progressive Templating） | L1 |  |
| [提示词到产品七步法](./prompt-to-product-seven-steps.md) | 提示词到产品七步法 | L1 | `Skill开发` `提示词工程` `产品化` |
| [PS5防御性Prompt模板模式（PS5-Defensive-Prompt）](./ps5-defensive-prompt.md) | 你是Windows PowerShell 5.1兼容性专家。为用户生成代码时，必须严格遵守以下约束： | L1 | `powershell` `powershell-5.1` `defensive-prompt` |
| [质量-成本动态平衡模式](./quality-cost-dynamic-balance.md) | 质量-成本动态平衡模式 | L2-validated | `LLM` `Token` `Quality` |
| [references/ 渐进式披露：通过引用已有知识文档避免内容重复](./references-progressive-disclosure.md) | references/ 渐进式披露：通过引用已有知识文档避免内容重复 | L1 |  |
| [七概念驱动的技术Wiki创作方法论](./seven-concepts-wiki-creation-methodology.md) | 七概念驱动的技术Wiki创作方法论 | L1 |  |
| [Skill 发现协议增强 SOP](./skill-discovery-protocol.md) | Skill 发现协议增强 SOP | L1 |  |
| [Skill 五要素模型（Skill Five Elements Model）](./skill-five-elements-model.md) | Skill 五要素模型（Skill Five Elements Model） | L1 |  |
| [Skill渐进式披露封装模式（SKILL.md Metadata + Python Executor）](./skill-progressive-disclosure-encapsulation.md) | Skill渐进式披露封装模式（SKILL.md Metadata + Python Executor） | L1 |  |
| [Skill标准化操作流程模式（Four Principles for Workflow Skill Design）](./skill-standardized-workflow-pattern.md) | Skill标准化操作流程模式（Four Principles for Workflow Skill Design） | L1 |  |
| [AI Skill 三层价值模型](./skill-three-layer-value-model.md) | AI Skill 三层价值模型 | L2 |  |
| [苏格拉底提问纠错模式（Socratic Questioning Correction）](./socratic-questioning-correction.md) | 苏格拉底提问纠错模式（Socratic Questioning Correction） | L1 | `苏格拉底提问` `纠错方式` `协作模式` |
| [源码锚点二次校验协议：研究-编写阶段的质量传递契约](./source-anchor-verification-protocol.md) | 源码锚点二次校验协议：研究-编写阶段的质量传递契约 | L1 |  |
| [源码阅读→OKF Wiki生成工作流](./source-code-to-okf-wiki-workflow.md) | 源码阅读→OKF Wiki生成工作流 | L1 |  |
| [源码→OKF 对抗性更新工作流](./source-code-to-okf-adversarial-update.md) | 源码→OKF 对抗性更新工作流 | L1 |  |
| [Spec 驱动 + 知识库驱动的文档批量产出模式](./spec-driven-batch-doc-generation.md) | Spec 驱动 + 知识库驱动的文档批量产出模式 | - |  |
| [Spec 驱动子代理执行模式](./spec-driven-subagent-execution.md) | Spec 驱动子代理执行模式 | - |  |
| [Spec Mode文档创建工作流：前置规划→原子执行→门禁验证](./spec-mode-doc-creation-workflow.md) | Spec Mode文档创建工作流：前置规划→原子执行→门禁验证 | L2 |  |
| [Spec 模式第七阶段独立验证机制](./spec-stage7-independent-validation.md) | Spec 模式第七阶段独立验证机制 | L1 | `spec-mode` `independent-validation` `checklist` |
| [风格-创意分离控制（Style-Creativity Separation Control）](./style-creativity-separation-control.md) | 风格-创意分离控制（Style-Creativity Separation Control） | L2 |  |
| [子代理原子任务描述模板：六要素精确委托法](./subagent-atomic-task-template.md) | [...按照要素3的结构化大纲写正文内容...] | L2 |  |
| [子代理"三不准"执行规范（Subagent Git Three Prohibitions）](./subagent-git-three-prohibitions.md) | 子代理"三不准"执行规范（Subagent Git Three Prohibitions） | L1 |  |
| [症状-处方 QA 系统（Symptom-Prescription QA）](./symptom-prescription-qa.md) | 症状-处方 QA 系统（Symptom-Prescription QA） | L2 |  |
| [任务类型预检防偏差](./task-type-precheck-bias-defense.md) | 任务类型预检防偏差 | L2 |  |
| [团队共享 AI 同事模式（Team Shared AI Colleague）](./team-shared-ai-colleague.md) | 团队共享 AI 同事模式（Team Shared AI Colleague） | - |  |
| [模板质量方差控制模式（Template Variance Control）](./template-variance-control.md) | 模板质量方差控制模式（Template Variance Control） | L1 |  |
| [工具采纳漏斗（Tool Adoption Funnel）](./tool-adoption-funnel.md) | 工具采纳漏斗（Tool Adoption Funnel） | - |  |
| [篇幅控制两阶段模式：先大纲后展开](./two-stage-outline-then-expand.md) | 篇幅控制两阶段模式：先大纲后展开 | L1 |  |
| [用户主权默认模式](./user-sovereignty-default.md) | 用户主权默认模式 | L1 | `security` `ai-agent` `trust` |
| [视觉操作闭环模式（Screenshot-Locate-Operate-Verify Loop）](./visual-operation-closed-loop.md) | 视觉操作闭环模式（Screenshot-Locate-Operate-Verify Loop） | L1 |  |
| [视觉通用操作模式（Visual-based Universal Operation）](./visual-universal-operation.md) | 视觉通用操作模式（Visual-based Universal Operation） | L2 |  |


<!-- README_INDEX_END -->

## 🔗 相关资源

- [🏠 返回上级：方法论模式](../README.md)
- [📚 文档首页](../../../../README.md)

---

<!-- generated by generate-readme.py on 2026-08-21 -->
