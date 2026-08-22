---
id: "zleap-agent-wiki-memory-system"
title: "分区记忆系统"
source: "https://github.com/Zleap-AI/Zleap-Agent + 本地源码 d:\spaces\SpecWeave\external\libs\Zleap-Agent"
category: "learning"
tags: ["zleap-agent", "memory", "person-memory", "event-memory", "experience-memory", "rrf", "recall", "postgresql", "extraction"]
date: "2026-08-04"
status: "stable"
author: "seven-concepts knowledge-scenario"
summary: "Zleap-Agent 分区记忆系统：person/event/experience 三类记忆、A 线（people notes）+ B 线（core records）双线、prefetch 快速读取与 recall 精排、RRF 多路径召回融合、抽取管线。"
last_verified: "2026-08-04"
wiki_version: "1.0"
---

# 03 分区记忆系统

Zleap-Agent 的记忆不是"一个泛化的长期记忆桶"，而是**分区管理**，并且存储于 PostgreSQL——因为记忆参与 Agent 每一轮运行，需要检索、隔离、审计与回滚能力。

## 3.1 三类记忆分区

| 分区 | 含义 | 典型内容 |
|------|------|---------|
| **Person（对人记忆）** | 用户偏好与稳定事实 | 用户喜欢什么、习惯、身份信息 |
| **Event（对事记忆）** | 与用户、任务或 Workspace 相关的事件与状态 | 一次任务完成情况、某空间的当前状态 |
| **Experience（经验记忆）** | 从已完成任务中沉淀的可复用方法 | "下次遇到 X 类任务应该怎么做" |

## 3.2 两条写入线（A 线 + B 线）

`packages/core/src/memory/orchestrator.ts` 的 `MemoryOrchestrator` 统一了两条线：

| 线 | 内容 | 特点 |
|----|------|------|
| **A 线（people notes）** | 对人记忆（impressions），简单最新列表 | **无模型**，快速写入/读取 |
| **B 线（core records）** | 对事 work + 经验 experience，抽取/写入 + 召回 | 参与抽取管线与召回 |

### 上下文编排原则（用户约定）

> **prefetch 只做快速读取（people 最新列表 + core 摘要，fast），不走 LLM；只有主动 recall 才用 precise（LLM 精排）。**

- `prepareContext()`：快速预取，返回 impressions + experiences + recent records，无 LLM，保证启动速度。
- `recall()`：主动召回，默认 `mode: 'precise'`（LLM 精排），返回 `RecordHit[]`。

## 3.3 记忆写入与重合

`remember()` 分流：

- `kind === 'experience'` → 走 B 线：先经 `assessExperienceMemory` 做**经验记忆评估**（不合格抛 `ExperienceMemoryRejectedError`），再 `writeExperience`。
- 否则（对人/对事）→ 走 A 线 people notes：通过 `fallbackRememberPeopleDecision` 决定是 `update_profile`（同标题更新）还是 `keep_both`（新档案），再由 `applyPeopleReconcileDecision` 落库。

## 3.4 RRF（Reciprocal Rank Fusion）多路径召回融合

`packages/store/src/core/rrf.ts` 实现了 RRF 算法，用于把多条召回路径（person/event/experience、向量/词法/实体/图）的排名融合成一个总排序。

核心公式：

```text
score(item) = Σ over paths  1 / (k + rank_path(item))
```

其中默认 `k = 60`。实现要点：

- 同一 item 在多条路径出现时，取**最小 rank**（`pathRanks[path] = Math.min(...)`）。
- 最终按 `score` 降序，同分按 `createdAt` 降序。
- 目的是让"在多个路径中都排名靠前"的条目获得更高总分，从而提升召回质量。

### 架构洞察

> **洞察 6：RRF 让"多路召回"比"单路精排"更稳。** 向量检索、词法匹配、实体/图召回各自有盲区，RRF 用秩融合而非分数加和，对量纲和分布不敏感，鲁棒性更好（来源：`packages/store/src/core/rrf.ts`）。

## 3.5 抽取管线

`packages/store/src/core/extract.ts` 的 `ingestFragment` 是 B 线核心：

```text
会话片段 → LLM 抽取器 → 结构化 event(+entity) → 落库
```

关键环节：

- **可插拔抽取器**：`CoreExtractor` 缺失、失败或返回空时不写事件。
- **幂等**：用 `contentHash`（sha256）作为事件幂等键，重复抽取不重复入库（`findEventByHash`）。
- **批量向量化**：`EmbedBatch` 批量计算 embedding，缺失时优雅降级（无向量仍可入库，靠词法/实体/图召回）。
- **实体去重**：实体名按 source 归一化去重。
- **关系融合**：`reconcileDraft` 用 `CoreMemoryReconciler` 决定 `keep_both` / `replace_old` / `keep_old` / `skip`，避免记忆堆积或重复。

## 3.6 记忆与上下文的关系

记忆在 `assembleContext`（02 章）中如何进入上下文：

- **stable 块**：`impressionsText`（对人记忆）作为系统提示词的一部分，稳定、不进入缓存断点之后。
- **variable 块**：匹配召回（老 event ∪ experience）作为可变部分，随轮次变化。

正因为"变化的记忆永不进入缓存前缀"，记忆的更新不会污染缓存前缀，从而保证缓存的高命中率。

## 本章小结

- 记忆分 **person / event / experience** 三类，存储于 PostgreSQL。
- 双线：**A 线 people notes（无模型）+ B 线 core records（抽取/召回）**。
- prefetch 快速读取无 LLM，主动 recall 走 LLM 精排。
- **RRF** 融合多路径召回，提升稳健性。
- 抽取管线用 LLM 抽取器 + content_hash 幂等 + 可插拔 reconciler，保证记忆质量与去重。

---

| 上一章 | 返回目录 | 下一章 |
|--------|---------|--------|
| ← [02 Workspace 隔离与上下文组装](./02-workspace-context.md) | [README](./README.md) | → [04 Skill 与工具权限](./04-skills-tools-permissions.md) |