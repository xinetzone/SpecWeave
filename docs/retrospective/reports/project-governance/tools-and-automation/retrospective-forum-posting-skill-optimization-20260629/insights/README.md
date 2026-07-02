---
id: "forum-posting-skill-optimization-insights-index"
title: "forum-posting Skill优化复盘洞察索引"
source: "../insight-extraction.md"
x-toml-ref: "../../../../../../../.meta/toml/docs/retrospective/reports/project-governance/tools-and-automation/retrospective-forum-posting-skill-optimization-20260629/insights/README.toml"
---
# forum-posting Skill优化复盘洞察索引

> 本目录存放从 forum-posting Skill 优化复盘中萃取的核心洞察。通用规律已归档至正式模式库，本目录文件保留事件发现叙事。
>
> 📖 **已入库正式模式（9个L1）**：
> - [skill-five-elements-model.md](../../../../../patterns/methodology-patterns/ai-collaboration/skill-five-elements-model.md)（Skill五要素模型）
> - [process-vs-experience-intuition.md](../../../../../patterns/methodology-patterns/governance-strategy/process-vs-experience-intuition.md)（流程合规vs经验直觉区分）
> - [nonlinear-correction-cost.md](../../../../../patterns/methodology-patterns/governance-strategy/nonlinear-correction-cost.md)（协议违规非线性纠偏成本）
> - [feedback-wording-diagnosis.md](../../../../../patterns/methodology-patterns/governance-strategy/feedback-wording-diagnosis.md)（用户反馈措辞诊断）
> - [availability-heuristic-structural-guard.md](../../../../../patterns/methodology-patterns/governance-strategy/availability-heuristic-structural-guard.md)（可得性启发结构性防范）
> - [context-recovery-protocol.md](../../../../../patterns/methodology-patterns/ai-collaboration/context-recovery-protocol.md)（Context恢复协议重执行）
> - [template-variance-control.md](../../../../../patterns/methodology-patterns/ai-collaboration/template-variance-control.md)（模板质量方差控制）
> - [task-type-first-indexing.md](../../../../../patterns/methodology-patterns/governance-strategy/task-type-first-indexing.md)（任务类型优先索引）
> - [spec-as-code-automated-gates.md](../../../../../patterns/methodology-patterns/tools-automation/spec-as-code-automated-gates.md)（规范即代码自动化门禁）
>
> 🔗 **整合进现有模式**：
> - Skill Description SEO模式 → 整合进skill-five-elements-model要素1
> - 浏览器自动化双方案决策树模式 → 整合进skill-five-elements-model要素2
> - 优化前资产盘点 → 整合进skill-five-elements-model前置步骤
>
> ⏸️ **待后续评估**：
> - MCP工具函数封装模式（代码级模式，本次先不入库）

## 洞察清单

### 关键发现

| 文件 | 核心发现 | 归档状态 |
|------|---------|---------|
| [finding-01-three-layer-routing-non-symmetric-trigger.md](finding-01-three-layer-routing-non-symmetric-trigger.md) | 三层路由"非对称触发"陷阱——工作目录驱动导致根目录任务遗漏vendor资产 | ✅ 沉淀为AGENTS.md任务类型预检+步骤2.0 |
| [finding-02-skill-description-seo.md](finding-02-skill-description-seo.md) | Skill description是"触发广告"而非"功能文档"，需要SEO式设计 | ✅ 整合进skill-five-elements-model要素1 |
| [finding-03-why-explanation-principle.md](finding-03-why-explanation-principle.md) | 解释Why比罗列MUST更重要，帮助AI在边界情况做出正确判断 | ✅ 整合进skill-five-elements-model要素4 |
| [finding-04-progressive-disclosure.md](finding-04-progressive-disclosure.md) | 渐进式披露的上下文节省效应——按使用频率分层组织内容 | ✅ 整合进skill-five-elements-model要素3 |
| [finding-05-dual-scheme-decision-tree.md](finding-05-dual-scheme-decision-tree.md) | 双方案共存需要"决策树"而非"并列罗列"，降低Agent决策负担 | ✅ 整合进skill-five-elements-model要素2 |

### 规律认知

| 文件 | 核心规律 | 归档状态 |
|------|---------|---------|
| [law-01-skill-five-elements-model.md](law-01-skill-five-elements-model.md) | 高质量Skill五要素模型：触发就绪描述/方案决策树/渐进式披露/Why解释/安全检查清单 | ✅ 独立入库ai-collaboration/ |
| [law-02-three-layer-routing-task-type-precheck.md](law-02-three-layer-routing-task-type-precheck.md) | 三层路由应是任务类型驱动而非仅工作目录驱动，增加任务类型预检 | ✅ 沉淀为AGENTS.md步骤2.0+vendor方法论资产表 |
| [law-03-browser-automation-general-pattern.md](law-03-browser-automation-general-pattern.md) | 浏览器自动化Skill五层模式：检测/操作/安全/验证/清理 | ⏸️ 待后续验证后入库 |

### Meta级洞察（执行过程元层面发现）

| 文件 | 核心元洞察 | 归档状态 |
|------|----------|---------|
| [meta-01-process-vs-experience.md](meta-01-process-vs-experience.md) | "凭经验做对"vs"按方法论做对"的本质区别——可预测性优于偶然正确性 | ✅ 独立入库governance-strategy/ |
| [meta-02-nonlinear-correction-cost.md](meta-02-nonlinear-correction-cost.md) | 协议违规纠偏成本呈非线性——前置5分钟读规范避免30分钟返工 | ✅ 独立入库governance-strategy/ |
| [meta-03-context-compression-cognitive-narrowing.md](meta-03-context-compression-cognitive-narrowing.md) | 上下文压缩不仅是信息丢失，更是认知视野收窄——Context恢复需重执行协议 | ✅ 独立入库context-recovery-protocol |
| [meta-04-feedback-wording-diagnosis.md](meta-04-feedback-wording-diagnosis.md) | 用户反馈措辞是诊断线索——"为何没有X"=流程缺失，"X不好用"=质量问题 | ✅ 独立入库feedback-wording-diagnosis |
| [meta-05-availability-heuristic-structural-guard.md](meta-05-availability-heuristic-structural-guard.md) | "就近直觉"是系统性认知偏差，需要结构性机制防范而非"更认真" | ✅ 独立入库availability-heuristic-structural-guard |
| [meta-06-startup-protocol-self-checkpoint.md](meta-06-startup-protocol-self-checkpoint.md) | 启动协议缺少自检检查点容易跳步，需要结构化自检问题清单 | ✅ 沉淀为AGENTS.md步骤3.5 |

## 落地状态总览

8项改进建议全部落地：
- ✅ 三层路由任务类型预检 → AGENTS.md步骤2.0+vendor方法论资产表
- ✅ 启动协议自检检查点 → AGENTS.md步骤3.5
- ✅ SpecWeave Skill开发补充规范 → .agents/rules/skill-development.md
- ✅ Skill标准化模板 → .agents/skills/SKILL-TEMPLATE.md
- ✅ vendor按任务类型索引 → vendor/AGENTS.md任务类型索引章节
- ✅ Context恢复协议重执行 → AGENTS.md步骤2.2
- ✅ Skill质量自动化检查脚本 → .agents/scripts/check-skill-quality.py
- ✅ 用户反馈分类框架 → feedback-wording-diagnosis模式入库

---
*数据来源：[forum-posting Skill优化复盘](../README.md)*
