---
id: "retrospective-adversarial-review-kg-20260710"
title: "对抗性审查知识图谱生成复盘"
category: "retrospective"
date: "2026-07-10"
version: "1.0"
status: "completed"
source: "session: adversarial-review-knowledge-graph-generation"
retro_type: "task"
---
<!-- meta_type: retrospective -->

# 对抗性审查知识图谱生成复盘

> **复盘类型**: 任务复盘 | **日期**: 2026-07-10 | **Commit**: 2254b19c

---

## 执行摘要

本次任务为对抗性审查知识库（`adversarial-review-wiki/`）创建交互式知识图谱，使用 `knowledge-graph-generator` Skill 的 TOML 声明式配置方案。从术语表（6类50+术语）和文档导航表自动提取80个节点，生成 `knowledge-graph.html`（97.4 KB）。过程中发现 Python `tomllib` 对中文引用键 inline table 的兼容性缺陷，通过 `extra_links` 数组格式成功规避。全程耗时约20分钟，2轮迭代完成。

**关键数字**:
- 80个节点，7种类型，13条关系
- 2个新文件（config 259行 + HTML 97.4 KB）
- 1个阻塞问题（tomllib中文inline table）
- 2个配置错误被Skill Gotchas提前预防

---

## 1. 事实数据

### 1.1 产出物

| 文件 | 路径 | 行数/大小 |
|------|------|----------|
| TOML配置 | `adversarial-review-wiki/knowledge-graph-config.toml` | 259行 |
| 知识图谱 | `adversarial-review-wiki/knowledge-graph.html` | 97.4 KB |

### 1.2 节点类型分布

| 类型 | 颜色 | 数量 | 来源 |
|------|------|------|------|
| 核心概念 | #43A047 | 8 | 术语表2.1 + 3个手工根节点 |
| 来源可信度 | #FB8C00 | 10 | 术语表2.2 |
| 认知偏差 | #E53935 | 11 | 术语表2.3 |
| AI协作/代码审查 | #1E88E5 | 14 | 术语表2.4 |
| 标准与工具 | #00897B | 10 | 术语表2.5 |
| 方法论 | #8E24AA | 12 | 术语表2.6 |
| 文档 | #546E7A | 15 | 00-overview文件导航表 |

### 1.3 执行时间线

| 步骤 | 动作 | 耗时 | 结果 |
|------|------|------|------|
| 1 | 读取Skill指引 + 文档结构 | 3min | ✅ |
| 2 | 创建TOML配置 | 5min | ✅ |
| 3 | 首次运行 → 失败 | 1min | ❌ tomllib错误 |
| 4 | 定位根因 + 验证参照实现 | 2min | ✅ 确认是tomllib层面问题 |
| 5 | 改用extra_links方案 | 3min | ✅ |
| 6 | 二次运行 → 成功 | 1min | ✅ 80节点生成 |
| 7 | 验证统计 + 原子提交 | 3min | ✅ |

---

## 2. 过程分析

### 2.1 成功因素

1. **参照实现加速设计**: 直接复用第一性原理 `knowledge-graph-config.toml` 作为模板，7节点类型/3边类型/7解析器配置从0到1仅需1轮迭代
2. **数据源天然适配**: 术语表的6个分类子表恰好对应6种语义不同的节点类型，无需额外数据清洗
3. **Skill Gotchas预防错误**: 精确section匹配提示和TOML数组表位置约束提前规避了2个高频配置错误
4. **参照验证快速定位**: 第一时间验证第一性原理config也存在相同错误，确认问题在工具层面而非配置层面

### 2.2 问题与根因

| 问题 | 严重度 | 根因 | 影响 |
|------|--------|------|------|
| tomllib中文inline table不兼容 | 🔴 阻塞 | Python 3.11+ `tomllib` 对inline table中引用键的支持有限制 | 首次运行失败 |
| 边数偏低（13条） | 🟡 中等 | `concept_doc_map` 无法使用，大量概念→文档映射丢失 | 图谱关联密度不足 |
| 第一性原理config潜伏同问题 | 🟡 中等 | 可能从未在当前Python版本下成功运行过 | 工具链兼容性盲区 |

---

## 3. 关键洞察

详见 [insight-extraction.md](insight-extraction.md)

| ID | 洞察 | 严重度 |
|----|------|--------|
| INSIGHT-1 | tomllib对中文引用键inline table存在兼容性缺陷 | 🔴 高 |
| INSIGHT-2 | extra_links数组格式是concept_doc_map的有效降级方案 | 🟡 中 |
| INSIGHT-3 | 参照实现优先验证是高效调试策略 | 🟢 低 |
| INSIGHT-4 | Skill Gotchas机制有效预防了配置错误 | 🟢 低 |

---

## 4. 改进行动项

| ID | 行动项 | 优先级 | 验收标准 | 关联洞察 |
|----|--------|--------|---------|---------|
| ACT-1 | 为 `knowledge_graph_core.py` 添加 `tomli` fallback | P0 | `pip install tomli` 后中文inline table配置可正常解析 | INSIGHT-1 |
| ACT-2 | 在Skill Gotchas中增加tomllib中文inline table已知限制 | P1 | Gotchas章节新增1条说明，含错误信息示例和workaround | INSIGHT-1 |
| ACT-3 | 为 `generate-graph.py` 添加CI兼容性测试 | P2 | 使用含中文键名的测试配置，验证两种解析器均可用 | INSIGHT-1 |
| ACT-4 | 修复第一性原理知识图谱config（同问题） | P2 | 验证第一性原理config可正常生成图谱 | INSIGHT-1 |
| ACT-5 | 同步更新对抗性审查config（concept_doc_map补充） | P3 | 解决tomllib问题后，补充完整概念→文档映射，提升边数 | INSIGHT-2 |

---

## 5. 模式沉淀

本次复盘沉淀/更新以下模式：

| 模式 | 动作 | 说明 |
|------|------|------|
| `reference-verify-first` | 新建 (L1) | 参照实现优先验证：遇到工具错误时先验证参照实现是否存在同样问题，再决定调试方向 |
| `extra-links-fallback` | 新建 (L1) | extra_links数组降级：当concept_doc_map不可用时，使用extra_links数组格式等效替代 |

---

*本报告版本：v1.0 | 创建日期：2026-07-10 | 数据验证：✅ 三查法通过*