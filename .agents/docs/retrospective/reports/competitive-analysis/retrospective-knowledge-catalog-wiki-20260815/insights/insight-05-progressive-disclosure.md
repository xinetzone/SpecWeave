---
id: "kc-insight-05-progressive-disclosure-for-agents"
title: "洞察5：渐进式披露是Agent上下文窗口受限下的必要设计"
source: "../insight-extraction.md#洞察5渐进式披露是agent上下文窗口受限下的必要设计"
date: "2026-08-15"
archived_pattern: "../../../../patterns/architecture-patterns/agent-knowledge-graph-navigation.md"
tags:
  - progressive-disclosure
  - context-window
  - agent-ux
  - knowledge-organization
maturity: "L1"
---
# 洞察5：渐进式披露是Agent上下文窗口受限下的必要设计

> ✅ **已萃取为模式**：[agent-knowledge-graph-navigation](../../../../patterns/architecture-patterns/agent-knowledge-graph-navigation.md)（Agent知识图谱导航模式）

## 陈述（结论）

OKF显式设计了渐进式披露机制（根index.md→子目录index.md→单概念文件，Frontmatter/Body分离，图结构链接而非纯目录树）。这不是"文档组织偏好"，而是**面向LLM上下文窗口硬约束的必要架构设计**——让Agent像人类浏览网页一样逐层导航，而不是一次性加载全部内容。

## 反常识（挑战默认假设）

- ❌ 默认假设："知识库越全越好，一个大文件包含所有内容最方便"
- ✅ 反常识：LLM上下文窗口是硬成本约束（token费用+推理时间+信息丢失率）。1000个概念的Bundle一次性加载需要数百万token——既慢又贵，还容易在中间丢信息。分层导航的效率比全量加载高几个数量级。
- ❌ 默认假设："index.md是给人看的目录页"
- ✅ 反常识：OKF的index.md主要是给Agent做低成本导航用的——Agent先加载index做路由决策，再按需加载具体文件，这跟浏览器先加载HTML索引再懒加载图片是同一逻辑。
- ❌ 默认假设："目录树足够表达知识关系"
- ✅ 反常识：复杂知识是图结构不是树结构。Frontmatter元数据预过滤+Markdown显式链接比目录层级暗示更可靠。

## 证据（来源）

OKF渐进式披露设计：
1. 根`index.md`只列顶级目录/概念（最小导航成本）
2. 子目录`index.md`只列该目录内容（逐层细化）
3. Frontmatter可单独加载做初步过滤（元数据比正文成本低几个数量级）
4. 单个概念文件控制在合理大小（1-5KB）
5. 链接构成图结构，不强行塞进目录树

## 行动建议

1. **禁止巨型单文件知识库**：拆分成小文件（1-5KB/个）+目录索引
2. **认真写Frontmatter**：这是Agent做预过滤的依据，缺Frontmatter=Agent必须读全文才能判断
3. **显式表达关联**：概念之间的关联用Markdown链接显式表达，不要只靠目录层级暗示关系
4. **Agent检索策略**：先加载index做路由→加载Frontmatter做过滤→按需加载目标文件Body，不要一上来就全文检索

## 关联模式

- **✅ 本洞察已萃取为**：[agent-knowledge-graph-navigation](../../../../patterns/architecture-patterns/agent-knowledge-graph-navigation.md)（Agent知识图谱导航模式）
- [progressive-context-disclosure](../../../../patterns/methodology-patterns/ai-collaboration/progressive-context-disclosure.md)（Skill文档工作流阶段式加载，同家族不同场景）
- [lazy-loading-pattern](../../../../patterns/methodology-patterns/ai-collaboration/lazy-loading-pattern.md)（工具/MCP元数据懒加载，同家族不同场景）
- [context-lifecycle-layering](../../../../patterns/methodology-patterns/ai-collaboration/context-lifecycle-layering.md)（提示词五层生命周期管理）
- [开源仓库四层架构识别法](../../../../patterns/methodology-patterns/research-knowledge/open-source-repo-four-layer-identification.md)
- [渐进式披露三层架构](../../capabilities/ARCHITECTURE.md)
