---
id: "kc-insights-index"
title: "Knowledge Catalog Wiki——洞察索引"
date: "2026-08-15"
source: "../insight-extraction.md"
x-toml-ref: "../../../../../../../.meta/toml/.agents/docs/retrospective/reports/competitive-analysis/retrospective-knowledge-catalog-wiki-20260815/insights/README.toml"
category: "retrospective"
---
# Knowledge Catalog Wiki 洞察索引

> 从Knowledge Catalog（Google Cloud）学习与Wiki创建过程中提炼的核心洞察。每条洞察包含标准四元组：**陈述+反常识+证据+行动建议**。

## 洞察清单

| # | 洞察 | 标签 | 成熟度 | 核心反常识 | 模式状态 |
|---|------|------|--------|-----------|---------|
| 1 | [规范开放、工具绑定是成熟厂商开源项目的三层策略](insight-01-three-layer-strategy.md) | open-source, vendor-strategy | L1 | 开源≠完全开放，三层架构是商业策略不是慈善 | ✅ 已萃取：[vendor-neutral-three-layer-learning](../../../../patterns/methodology-patterns/research-knowledge/vendor-neutral-three-layer-learning.md) |
| 2 | [知识即代码——软件工程范式向知识管理的迁移](insight-02-knowledge-as-code.md) | knowledge-management, paradigm-transfer | L1 | 知识管理不需要发明新范式，直接复用SE 50年实践即可 | ✅ 已萃取：[knowledge-as-code-paradigm](../../../../patterns/architecture-patterns/knowledge-as-code-paradigm.md) |
| 3 | [AI原生元数据的核心问题不是"如何表示"而是"如何建立信任"](insight-03-trust-first.md) | ai-agent, trust, metadata | L1 | Agent时代，信任字段比内容字段优先级更高 | ✅ 已萃取：[trust-first-metadata](../../../../patterns/architecture-patterns/trust-first-metadata.md) |
| 4 | [Attested Computation是知识领域的OpenAPI——从描述到可执行](insight-04-attested-computation.md) | verifiable-computation, agent-safety | L1 | 自然语言指标定义永远有歧义，必须可执行+可验证 | ✅ 已萃取：[verifiable-knowledge-claim](../../../../patterns/architecture-patterns/verifiable-knowledge-claim.md) |
| 5 | [渐进式披露是Agent上下文窗口受限下的必要设计](insight-05-progressive-disclosure.md) | progressive-disclosure, context-window | L1 | index.md主要是给Agent导航用的，不是给人看的 | ✅ 已萃取：[agent-knowledge-graph-navigation](../../../../patterns/architecture-patterns/agent-knowledge-graph-navigation.md) |

## 洞察分类

### 🏗️ 架构与策略类（厂商开源策略）
- 洞察1：三层开源策略 → 已萃取为学习方法论模式

### 📚 知识管理范式类
- 洞察2：知识即代码（SE→KM范式迁移）→ ✅ 已萃取为架构模式 [knowledge-as-code-paradigm](../../../../patterns/architecture-patterns/knowledge-as-code-paradigm.md)

### 🤖 AI Agent类
- 洞察3：信任优先元数据 → ✅ 已萃取为架构模式 [trust-first-metadata](../../../../patterns/architecture-patterns/trust-first-metadata.md)
- 洞察4：Attested Computation可验证知识 → ✅ 已萃取为架构模式 [verifiable-knowledge-claim](../../../../patterns/architecture-patterns/verifiable-knowledge-claim.md)
- 洞察5：渐进式披露 → ✅ 已萃取为架构模式 [agent-knowledge-graph-navigation](../../../../patterns/architecture-patterns/agent-knowledge-graph-navigation.md)

## 萃取模式汇总

从本次复盘萃取的7个可复用模式已入库至统一模式库：

| 模式 | 分类 | 入库位置 |
|------|------|---------|
| 开源仓库四层架构识别法 | methodology-patterns/research-knowledge | [open-source-repo-four-layer-identification.md](../../../../patterns/methodology-patterns/research-knowledge/open-source-repo-four-layer-identification.md) |
| 反模式优先最佳实践写作法 | methodology-patterns/document-architecture | [antipattern-first-best-practices.md](../../../../patterns/methodology-patterns/document-architecture/antipattern-first-best-practices.md) |
| 厂商项目三层剥离学习法 | methodology-patterns/research-knowledge | [vendor-neutral-three-layer-learning.md](../../../../patterns/methodology-patterns/research-knowledge/vendor-neutral-three-layer-learning.md) |
| 知识即代码范式迁移法 | architecture-patterns | [knowledge-as-code-paradigm.md](../../../../patterns/architecture-patterns/knowledge-as-code-paradigm.md) |
| 可验证知识声明法 | architecture-patterns | [verifiable-knowledge-claim.md](../../../../patterns/architecture-patterns/verifiable-knowledge-claim.md) |
| 信任优先元数据法 | architecture-patterns | [trust-first-metadata.md](../../../../patterns/architecture-patterns/trust-first-metadata.md) |
| Agent知识图谱导航法 | architecture-patterns | [agent-knowledge-graph-navigation.md](../../../../patterns/architecture-patterns/agent-knowledge-graph-navigation.md) |

> **注意**：前3个是**学习/写作方法论模式**（"怎么学"、"怎么写"），后4个是**知识系统架构模式**（"怎么设计知识管理/信任/导航体系"）。5条洞察已全部萃取为独立模式。

## 存放位置说明

遵循现有项目惯例（参考 [retrospective-specweave-contest](../../../retrospective-specweave-contest-advantage-analysis-20260624/insights/README.md) 和 [retrospective-tuyaopen](../../../retrospective-tuyaopen-learning-report-optimization-20260630/insights/README.md)）：

| 产出物类型 | 存放位置 | 说明 |
|-----------|---------|------|
| 单次复盘洞察（insights） | `reports/xxx/insights/` | 本次复盘的原子化洞察文件，标注模式状态 |
| 跨场景可复用模式（patterns） | `patterns/` 统一模式库 | 经过≥2案例验证，按分类入对应子目录 |
| 基础概念（concepts） | `concepts/` | 元概念/原则层，最稳定 |

## 质量门验证

| 质量门 | 标准 | 结果 |
|--------|------|------|
| G2（洞察四元组） | 陈述+证据+反常识+行动四元组完整，洞察之间维度独立 | ✅ 通过：5条均含完整四元组，维度独立 |
| V（对抗审查） | 4视角12条攻击，均已回应修正 | ✅ 通过（在 [insight-extraction.md](../insight-extraction.md) 中完成） |
| 模式入库（G3） | 7个模式已入库并更新索引（3个方法论模式+4个架构模式） | ✅ 通过：research-knowledge/document-architecture/architecture-patterns 索引均已更新，5条洞察全部完成双向引用 |

## 🔗 相关资源

- [🏠 返回上级：Knowledge Catalog Wiki复盘](../README.md)
- [📚 洞察萃取主文件](../insight-extraction.md)
- [📚 模式库索引](../../../../patterns/methodology-patterns/README.md)

---
