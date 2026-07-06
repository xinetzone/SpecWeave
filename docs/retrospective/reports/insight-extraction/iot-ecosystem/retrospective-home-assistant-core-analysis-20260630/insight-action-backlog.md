---
title: Home Assistant Core源码复盘 - 洞察行动项 Backlog
version: "1.0"
date: 2026-07-06
type: insight-action-backlog
source: "comprehensive-retrospective-template/insight-action-backlog.md"
project: retrospective-home-assistant-core-analysis-20260630
template_upgrade: 2026-07-06 v1.2
ssot:
  suggestions_source: export-suggestions.md
  insight_source: insight-extraction.md
---

# 洞察行动项 Backlog

> 本文件记录从本次复盘洞察和改进建议转化的可执行行动项。2个高优先级模式萃取+3个改进项待实施。

## 行动项总览

| ID | 来源 | 标题 | 优先级 | 状态 | DoD（完成定义） | 完成日期 |
|---|---|---|---|---|---|---|
| IMP-001 | 行动计划 | 选型决策：嵌入vs外挂集成 | 高 | ⏳ 待规划 | 明确集成目标：需要设备接入生态还是运行时内核能力；优先走外挂式集成（HTTP/WebSocket API、Webhook、Sidecar） | - |
| IMP-002 | 行动计划 | 模式落地：分阶段启动 | 高 | ⏳ 待规划 | 在自研系统中实现stage启动（基础能力优先、长尾并发），为每个stage定义超时策略 | - |
| IMP-003 | 行动计划 | 模式落地：装配并发去重 | 高 | ⏳ 待规划 | 对domain/component/setup做Future去重与异常一致传播，减少并发竞态 | - |
| IMP-004 | 行动计划 | 可观测性：启动阻塞告警 | 中 | ⏳ 待规划 | 启动阶段聚合pending tasks，输出可定位信息与"继续推进"策略 | - |
| IMP-005 | 行动计划 | 研究：HA config entries机制 | 低 | ⏳ 待规划 | 若需要插件化配置，评估其config entries + storage的可迁移点 | - |
| IMP-006 | 模式成熟度 | staged-startup-integration-loading模式入库 | 中 | ⏳ 待规划 | 分阶段启动集成加载模式沉淀至模式库，L1成熟度 | - |
| IMP-007 | 模式成熟度 | async-setup-future-deduplication模式入库 | 中 | ⏳ 待规划 | 异步装配Future去重模式沉淀至模式库，L1成熟度 | - |

## 行动项详情

### IMP-001: 选型决策：嵌入vs外挂集成
- **优先级**: 高
- **状态**: ⏳ 待规划
- **建议时间**: 2026-07-01
- **DoD**: 明确集成目标决策，优先选择外挂式集成（HTTP/WebSocket API、Webhook、Sidecar模式），避免Python版本/依赖冲突与升级成本
- **背景**: HA Core要求Python 3.14+，依赖严格pin，嵌入式引入成本极高

---

### IMP-002: 模式落地：分阶段启动
- **优先级**: 高
- **状态**: ⏳ 待规划
- **建议时间**: 2026-07-03
- **DoD**: 在自研系统中实现stage 0/1/2分阶段启动机制，基础能力优先可用，长尾集成并发加载，每个stage定义超时策略，降低长尾集成拖垮启动概率
- **参考**: HA Core bootstrap.py的stage启动机制

---

### IMP-003: 模式落地：装配并发去重
- **优先级**: 高
- **状态**: ⏳ 待规划
- **建议时间**: 2026-07-03
- **DoD**: 对domain/component/setup做Future去重，保证同一组件不重复初始化；异常一致传播，避免静默失败；参考HA async_setup_component实现

---

### IMP-004: 可观测性：启动阻塞告警
- **优先级**: 中
- **状态**: ⏳ 待规划
- **建议时间**: 2026-07-05
- **DoD**: 启动阶段聚合pending tasks列表，输出可定位信息（哪个组件卡住、等待多久）；提供"继续推进"策略，超时后跳过阻塞组件

---

### IMP-005: 研究：HA config entries机制
- **优先级**: 低
- **状态**: ⏳ 待规划
- **建议时间**: 2026-07-10
- **DoD**: 若需要插件化配置，评估HA config entries + storage机制的可迁移点，包括配置流、持久化、迁移机制

---

### IMP-006: staged-startup-integration-loading模式入库
- **优先级**: 中
- **状态**: ⏳ 待规划
- **DoD**: 分阶段启动集成加载模式沉淀至模式库，L1成熟度（从HA Core萃取，待自研系统验证）
- **核心内容**: stage 0/1/2分阶段、超时推进、关键基础优先可用

---

### IMP-007: async-setup-future-deduplication模式入库
- **优先级**: 中
- **状态**: ⏳ 待规划
- **DoD**: 异步装配Future去重模式沉淀至模式库，L1成熟度（从HA Core萃取，待自研系统验证）
- **核心内容**: Future去重、依赖/after_dependencies闭包、并发去重、异常一致传播

## 执行记录

| IMP-ID | 完成日期 | 提交/变更 | 执行结果 |
|---|---|---|---|
| IMP-001~007 | - | - | 全部待规划，建议按优先级顺序实施 |

## Changelog

- 2026-07-06 | create | 模板v1.2升级：从export-suggestions.md迁移行动项至独立backlog文件
