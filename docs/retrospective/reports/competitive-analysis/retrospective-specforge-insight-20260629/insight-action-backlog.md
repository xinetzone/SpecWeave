---
title: SpecForge竞品洞察复盘 - 洞察行动项 Backlog
version: "1.0"
date: 2026-07-06
type: insight-action-backlog
source: "external: 模板引用-comprehensive-retrospective-template/insight-action-backlog.md"
x-toml-ref: "../../../../../.meta/toml/docs/retrospective/reports/competitive-analysis/retrospective-specforge-insight-20260629/insight-action-backlog.toml"
project: retrospective-specforge-insight-20260629
template_upgrade: 2026-07-06（模板v1.2补建）
ssot:
  suggestions_source: export-suggestions.md
  insight_source: insight-extraction.md
---
# 洞察行动项 Backlog

> 本文件记录从本次复盘洞察和改进建议转化的可执行行动项。本项目为竞品分析型复盘，所有行动项均待执行。

## 行动项总览

| ID | 来源 | 标题 | 优先级 | 状态 | DoD（完成定义） | 完成日期 |
|---|---|---|---|---|---|---|
| IMP-001 | 改进建议§高优 | 实现阶段守卫机制 | 高 | ⏳ 待执行 | feature-development.md新增"阶段守卫"章节，定义阶段序列和允许/禁止操作；AI跨阶段操作时主动拦截提示 | - |
| IMP-002 | 改进建议§高优 | 增加前置文档强制读取检查点 | 高 | ⏳ 待执行 | feature-development.md每个步骤增加前置文档检查项；developer编码前输出已读取文档确认 | - |
| IMP-003 | 改进建议§高优 | 增加功能演进分支 | 高 | ⏳ 待执行 | 区分新功能/功能扩展/功能重构三类变更流程；萃取为独立方法论模式 | - |
| IMP-004 | 改进建议§中优 | BUG修复回归测试闭环 | 中 | ⏳ 待执行 | testing.md增加BUG修复回归测试章节；developer/tester职责更新；每个BUG修复PR包含测试用例 | - |
| IMP-005 | 改进建议§中优 | 萃取苏格拉底引导提问模式 | 中 | ⏳ 待执行 | ai-collaboration/下新增socratic-questioning.md，含五项核心原则、正反例对比，更新CATEGORIES.md索引 | - |
| IMP-006 | 改进建议§低优 | 编写贯穿式教学案例 | 低 | ⏳ 待执行 | docs/guides/tutorials/下新增完整案例（用户登录功能），按角色分工展示每个阶段输入/输出/交互 | - |
| IMP-007 | 改进建议§低优 | 增强AGENTS.md显式指令入口 | 低 | ⏳ 待执行 | AGENTS.md上下文路由表增加"常用指令快捷入口"区域，列出5个指令集触发关键词 | - |

## 行动项详情

### IMP-001: 实现阶段守卫机制
- **优先级**: 高
- **目标**: 为feature-development工作流增加阶段边界硬约束，防止AI跨阶段操作
- **落地步骤**:
  1. 在[feature-development.md](../../../../../.agents/workflows/feature-development.md)中新增"阶段守卫"章节，定义标准阶段序列和每个阶段的允许/禁止操作
  2. 在AGENTS.md的启动协议中增加阶段守卫检查规则
  3. 为每个阶段定义明确的"进入条件"和"退出标准"
- **验收标准**: AI在需求阶段被要求写代码时，能主动拦截并提示"当前为需求阶段，请先完成需求澄清"
- **状态**: ⏳ 待执行

---

### IMP-002: 增加前置文档强制读取检查点
- **优先级**: 高
- **目标**: 确保每个角色开始工作前已读取必要的前置文档
- **落地步骤**:
  1. 为feature-development.md的每个步骤增加"前置文档"检查项
  2. 明确每个步骤开始前必须确认读取的文档清单
  3. 将此规则纳入developer/architect/tester/reviewer的角色定义
- **验收标准**: developer开始编码前，输出中包含"已读取：技术方案文档、任务分解清单、开发规范"的确认
- **状态**: ⏳ 待执行

---

### IMP-003: 增加功能演进分支
- **优先级**: 高
- **目标**: 区分新功能、功能扩展、功能重构三类变更的处理流程
- **落地步骤**:
  1. 在feature-development.md中新增"功能演进"章节
  2. 定义三类变更的判定标准和对应流程
  3. 明确功能扩展的轻量流程（影响分析→增量方案→增量实现→回归测试）
  4. 明确功能重构的重量流程（方案重审→全量影响评估→全量回归）
  5. 萃取为独立的方法论模式
- **验收标准**: 当用户说"给X加个Y功能"时，AI能自动判断变更类型并选择对应流程
- **状态**: ⏳ 待执行

---

### IMP-004: BUG修复回归测试闭环
- **优先级**: 中
- **目标**: 每个BUG修复后自动生成回归测试，防止复发
- **落地步骤**:
  1. 在[testing.md](../../../../../.agents/workflows/testing.md)中增加"BUG修复回归测试"章节
  2. 在[developer.md](../../../../../.agents/roles/developer.md)中增加"修复后提交回归测试"的职责
  3. 在[tester.md](../../../../../.agents/roles/tester.md)中增加"验证回归测试覆盖"的检查项
  4. 考虑新增一个check-bug-regression.py脚本（可选）
- **验收标准**: 每个BUG修复PR中包含针对该BUG的测试用例
- **状态**: ⏳ 待执行

---

### IMP-005: 萃取苏格拉底引导提问模式
- **优先级**: 中
- **目标**: 将引导式提问方法论形式化为可复用模式
- **落地步骤**:
  1. 在[ai-collaboration/](../../../patterns/methodology-patterns/ai-collaboration/)下新增socratic-questioning.md
  2. 包含五项核心原则（选项优先、单维度聚焦、解释附带、推荐引导、迭代允许）
  3. 提供正反例对比
  4. 更新CATEGORIES.md索引
- **验收标准**: AI在需求不清时，自动使用引导式提问而非开放式大问题
- **状态**: ⏳ 待执行

---

### IMP-006: 编写贯穿式教学案例
- **优先级**: 低
- **目标**: 用一个完整案例串联所有角色/协议/工作流
- **落地步骤**:
  1. 选择"用户登录功能"作为贯穿案例
  2. 从需求提出到最终上线，按角色分工展示每个阶段的输入/输出/交互
  3. 在docs/下新增guides/tutorials目录存放
- **备注**: 此为文档完善项，不影响核心机制，可在高/中优先级项完成后进行
- **状态**: ⏳ 待执行

---

### IMP-007: 增强AGENTS.md显式指令入口
- **优先级**: 低
- **目标**: 让用户能通过关键词直接触发指令集
- **落地步骤**:
  1. 在AGENTS.md上下文路由表中增加"常用指令快捷入口"区域
  2. 列出retrospective/insight/export-report/atomization/atomic-commit五个指令集的触发关键词
  3. 保持现有自动路由能力不变，显式入口是补充而非替代
- **备注**: 简单改动，可在其他工作完成后顺便做
- **状态**: ⏳ 待执行

## 执行记录

| IMP-ID | 完成日期 | 提交/变更 | 执行结果 |
|---|---|---|---|
| - | - | - | 尚无执行记录 |

## 推荐执行顺序

```
1. IMP-002（前置文档读取）→ 最小改动，立即见效
2. IMP-001（阶段守卫）→ 核心机制增强
3. IMP-003（功能演进分类）→ 流程补全
4. IMP-004（BUG回归测试）→ 质量闭环
5. IMP-005（引导提问模式）→ 交互优化
6. IMP-007（显式指令入口）→ 小改动
7. IMP-006（贯穿案例）→ 大文档，最后做
```

建议IMP-001~003可以在一个Spec中打包实现（均为feature-development工作流增强），IMP-004~005分别独立实现，IMP-006~007择机进行。

## Changelog

- 2026-07-06 | create | 模板v1.2升级补建：从export-suggestions.md迁移7个行动项至独立backlog文件
