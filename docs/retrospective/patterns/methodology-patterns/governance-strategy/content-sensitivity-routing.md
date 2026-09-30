---
type: Pattern
id: "content-sensitivity-routing"
title: "公私域内容分离路由"
source: "SpecWeave 100天全面系统性复盘（specweave-seven-concepts-project-review-20260930）洞察3"
source_report: "../../../../../docs/retrospective/reports/concepts/milestone/specweave-seven-concepts-project-review-20260930.md"
x-toml-ref: "../../../../../.meta/toml/docs/retrospective/patterns/methodology-patterns/governance-strategy/content-sensitivity-routing.toml"
maturity: "L1-draft"
maturity_note: "单案例（SpecWeave 全仓，2026-08-31 docs/ 唯一文档中心确立后验证）；规则落地于 .agents/rules/content-sensitivity-precheck.md，本模式为其方法论抽象，待第二个独立工作区验证升级 L2"
date: "2026-09-30"
validation_count: 1
reuse_count: 0
documentation_level: "complete"
abstract_level: "domain-general"
tags: ["内容敏感度", "公私域分离", "文档治理", "工作区规范", "路径路由", "知识资产"]
related_patterns:
  - "blog-article-to-okf-bundle"
  - "agent-workspace-template"
  - "bootstrap-driven-self-evolution"
  - "self-contained-build-no-private-dependency"
---

# 公私域内容分离路由

## 模式概述

任何长期演进的工作区（仓库/知识库/文档中心）都会同时承载两类资产：**可对外公开消费的内容**（公开教程、开源代码、官方文档）与**仅限内部或个人使用的内容**（内部会议纪要、带 token 的私域链接分析、个人笔记、商业培训材料、含 PII 的数据）。若不在一开始就按内容敏感度做存储路由，两类内容会相互污染：

- 私域内容混入公共目录 → 敏感信息泄漏风险、无法对外发布、审查负担
- 公开内容混入私域目录 → 资产不可被发现、不可复用、重复劳动

该模式由 SpecWeave 项目 100 天演进验证：2026-08-31 将 `.agents/docs/` 整体迁移废止，确立 `docs/` 为唯一文档中心（公开）、`playground/` 为私域区，并配套「内容敏感度预检」规则与「落盘前三查」约束。此后 docs/ 成为可导航、可审计、可对外消费的中心，私域报告（如副业调研、故障根因分析）则安全留在 playground/。

核心思想：**内容存储位置不是风格问题，而是安全与资产可用性问题——公开/私域必须在入口处（任务启动时）分流，而非在出口处补救。**

## 触发场景

**适用于**：

- 任何同时承载公开与私域内容的 monorepo / 工作区 / 文档中心
- 任务输入源含访问控制信号（`share?code=`/`token=`/企业内部域名/登录态）
- 需要向外部发布或分享部分内容，但同一工作区还有内部材料
- 文档资产规模扩大后需要长期、可审计的归档边界

**不适用于**：

- 单一用途的私有仓库（全部内容本就私有，无需双区路由）
- 纯公开项目（无私域输入，一条公开路径即可）
- 一次性草稿（可用临时目录，无需治理）

## 核心做法（4 步）

1. **任务启动时判定敏感度**：按信号清单（URL 特征/用户标注/内容主题）判定任务输入为公开或私域；不确定时默认按私域处理。
2. **按级别选择工作流与存储路径**：
   - 公开 → 标准工作流，规划入公共 spec 区，最终产出物入公开文档中心（`docs/`）
   - 私域 → 简化工作流，跳过公共规划区，产出物直接入私域区（`playground/`）或用户指定目录
3. **私域转公开走显式流程**：私域内容中的可复用方法论，经脱敏 + 抽象后单独提取为公开资产，并在原私域文档留链接。
4. **落盘前自查三查**：查目标目录是否在公开中心下、查同类产出物现有位置、查所依据规范是否磁盘原文（防过期内联副本）。

## 反模式

| 反模式 | 表现 | 后果 | 防御 |
|--------|------|------|------|
| **事后补救** | 先按公开流程执行，事后再清理私域 spec 目录 | 规划痕迹残留、敏感内容短暂暴露、清理成本 | 入口判定，就高不就低 |
| **隐式默认公开** | 没有预检环节，所有内容默认走标准流程 | 私域流入公共索引，不可复现 | 强制预检步骤不可跳过 |
| **路径残留迁移** | 旧公共路径废止后仍向其写入 | 双中心混乱、断链 | 落盘前三查 + 废止路径显式声明 |
| **凭经验分流** | 依赖个体判断而非清单/决策树 | 不一致、不可审计 | 信号清单 + 决策树固化 |

## 实施检查清单

- [ ] 任务启动时是否执行内容敏感度预检？
- [ ] 判定信号是否可审计（URL/标注/内容源）？
- [ ] 私域内容产出物是否落在私域目录且不入公共索引？
- [ ] 私域转公开是否经用户同意并显式提取？
- [ ] 落盘前是否执行三查（目录/同类位置/磁盘规范）？

## 复用场景

- 任何 monorepo / 多用途工作区的目录边界设计
- Agent 工作区模板（与 `agent-workspace-template` 组合，将内容敏感度分流作为模板保留项）
- 对外发布与内部归档并存的文档治理

## 关联模式

- [blog-article-to-okf-bundle.md](../../documentation-patterns/blog-article-to-okf-bundle.md)：步骤 1 即内容敏感度预检（工作流分流）——本模式为其抽象化方法论
- [agent-workspace-template.md](../../architecture-patterns/agent-workspace-template.md)：工作区模板保留内容敏感度分流机制
- [self-contained-build-no-private-dependency.md](../../code-patterns/self-contained-build-no-private-dependency.md)：公开项目不耦合个人私域依赖（同为公私域边界治理）
- [bootstrap-driven-self-evolution.md](bootstrap-driven-self-evolution.md)：规范自举后路由决策自动归位，公私域分离是自举点判断维度之一

## Changelog

- 2026-09-30 | feat | 初始版本，来源：SpecWeave 全项目七概念全面复盘洞察 3（公私域文档分离），规则源：.agents/rules/content-sensitivity-precheck.md

> AI生成
