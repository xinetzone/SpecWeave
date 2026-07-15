---
title: AI智能体互联数据安全治理体系建设复盘 - 洞察行动项 Backlog
version: "1.0"
date: 2026-07-06
type: insight-action-backlog
source: "external: 模板引用-comprehensive-retrospective-template/insight-action-backlog.md"
x-toml-ref: "../../../../../../../.meta/toml/docs/retrospective/reports/project-governance/process-and-compliance/retrospective-ai-agent-data-security-governance-20260629/insight-action-backlog.toml"
project: retrospective-ai-agent-data-security-governance-20260629
template_upgrade: 2026-07-06（模板v1.2补建）
ssot:
  suggestions_source: export-suggestions.md
  insight_source: insight-extraction.md
---
# 洞察行动项 Backlog

> 本文件记录从本次复盘洞察和改进建议转化的可执行行动项。本次项目已完成10份数据安全规则文档交付，剩余改进项待后续迭代执行。

## 行动项总览

| ID | 来源 | 标题 | 优先级 | 状态 | DoD（完成定义） | 完成日期 |
|---|---|---|---|---|---|---|
| IMP-001 | 项目交付 | 10份数据安全规则文档交付 | 高 | ✅ 已完成 | 五层架构全覆盖，10份规则文档含Mermaid流程图、矩阵表格、checklist | 2026-06-29 |
| IMP-002 | 知识更新§1 | AGENTS.md上下文路由表更新 | 高 | ✅ 已完成 | data-security模块索引+导航入口同步更新 | 2026-06-29 |
| IMP-003 | 知识更新§2 | .agents/rules/README.md模块登记 | 高 | ✅ 已完成 | data-security/模块登记完成 | 2026-06-29 |
| IMP-004 | 知识更新§3 | roles-governance主题看板更新 | 高 | ✅ 已完成 | 新增establish-ai-agent-data-security-governance条目+路线图 | 2026-06-29 |
| IMP-005 | 知识更新§4 | 全局看板统计更新 | 高 | ✅ 已完成 | spec总数36→37 | 2026-06-29 |
| IMP-006 | 改进建议I-01 | 开发check-data-security.py自动化检查脚本 | P0 | ⏳ 待规划 | 支持PII硬编码检测、数据分级标注检查、出境评估流程验证 | - |
| IMP-007 | 改进建议I-02 | 补充脱敏/加密代码示例 | P0 | ⏳ 待补充 | data-masking.md和data-encryption.md补充Python/TypeScript代码片段 | - |
| IMP-008 | 改进建议I-03 | 建立国标条文映射表 | P1 | ⏳ 待规划 | 创建compliance-mapping.md逐条映射国标到规则条款 | - |
| IMP-009 | 改进建议I-04 | spec模板增加"文档风格确认"检查项 | P1 | ⏳ 待更新 | spec任务模板前置步骤增加读取3份同类文档确认格式 | - |
| IMP-010 | 改进建议I-05 | 任务模板明确"一个交付物=一个Task"原则 | P1 | ⏳ 待更新 | tasks模板或spec编写指南加入任务粒度原则 | - |
| IMP-011 | 改进建议I-06 | 评估AI场景专项防护规范必要性 | P2 | ⏳ 待评估 | 决定是否新增ai-specific-data-protection.md | - |
| IMP-012 | 改进建议I-07 | 设计[DS-LOG]结构化日志规范 | P2 | ⏳ 待规划 | 参考[SG-LOG]设计数据安全日志格式和采集方案 | - |
| IMP-013 | 可复用模式 | 萃取M-DS-01至M-DS-08为独立模式文档 | - | ⏳ 待规划 | 8个模式入库patterns目录 | - |

## 行动项详情

### IMP-001: 10份数据安全规则文档交付
- **优先级**: 高
- **执行结果**: 五层架构全覆盖，交付10份规则文档（模块总览、数据分类分级、出境评估、脱敏规范、加密管理、供应商准入、供应商审计、监控体系、应急响应、角色职责）
- **产出物**: [data-security/README.md](../../../../../../rules/data-security/README.md) 等10份文档
- **验证**: check-links.py通过，10文件、108个本地链接全部有效

---

### IMP-002: AGENTS.md上下文路由表更新
- **优先级**: 高
- **执行结果**: AGENTS.md规则体系索引表+上下文路由表同步更新
- **产出物**: [AGENTS.md](../../../../../../../AGENTS.md)

---

### IMP-003: .agents/rules/README.md模块登记
- **优先级**: 高
- **执行结果**: .agents/rules/README.md完成data-security/模块登记
- **产出物**: [.agents/rules/README.md](../../../../../../rules/README.md)

---

### IMP-004: roles-governance主题看板更新
- **优先级**: 高
- **执行结果**: roles-governance/README.md新增establish-ai-agent-data-security-governance条目+路线图更新
- **产出物**: [roles-governance/README.md](../../../../../../../.trae/specs/roles-governance/README.md)

---

### IMP-005: 全局看板统计更新
- **优先级**: 高
- **执行结果**: 全局看板spec总数从36更新为37
- **产出物**: [全局看板](../../../../../../../.trae/specs/README.md)

---

### IMP-006: 开发check-data-security.py自动化检查脚本
- **优先级**: P0
- **状态**: ⏳ 待规划
- **执行结果**: 待执行
- **验收标准**: 实现PII硬编码检测、数据分级标注检查、第三方API调用安全评估记录验证

---

### IMP-007: 补充脱敏/加密代码示例
- **优先级**: P0
- **状态**: ⏳ 待补充
- **执行结果**: 待执行
- **验收标准**: data-masking.md添加7种脱敏技术Python函数示例；data-encryption.md添加AES-256加解密代码片段

---

### IMP-008: 建立国标条文映射表
- **优先级**: P1
- **状态**: ⏳ 待规划
- **执行结果**: 待执行
- **验收标准**: 创建compliance-mapping.md，逐条映射数据安全法、PIPL、出境评估办法、AI智能体国标到具体规则条款

---

### IMP-009: spec模板增加"文档风格确认"检查项
- **优先级**: P1
- **状态**: ⏳ 待更新
- **执行结果**: 待执行
- **验收标准**: spec任务模板前置步骤增加"读取3份同类文档确认格式规范"强制检查项

---

### IMP-010: 任务模板明确"一个交付物=一个Task"原则
- **优先级**: P1
- **状态**: ⏳ 待更新
- **执行结果**: 待执行
- **验收标准**: .trae/specs/的tasks模板或spec编写指南加入任务粒度原则

---

### IMP-011: 评估AI场景专项防护规范必要性
- **优先级**: P2
- **状态**: ⏳ 待评估
- **执行结果**: 待评估
- **验收标准**: 决定是否新增ai-specific-data-protection.md，覆盖prompt/对话/输出三个AI特有数据形态

---

### IMP-012: 设计[DS-LOG]结构化日志规范
- **优先级**: P2
- **状态**: ⏳ 待规划
- **执行结果**: 待执行
- **验收标准**: 参考[SG-LOG]格式设计数据安全日志规范，覆盖18项监控指标

---

### IMP-013: 萃取M-DS-01至M-DS-08为独立模式文档
- **优先级**: -
- **状态**: ⏳ 待规划
- **执行结果**: 待萃取
- **验收标准**: 治理体系五层架构、合规驱动五步法、供应商生命周期管理、RACI矩阵应用等8个模式入库patterns目录

## 执行记录

| IMP-ID | 完成日期 | 提交/变更 | 执行结果 |
|---|---|---|---|
| IMP-001~005 | 2026-06-29 | 本次交付 | 10份规则文档+4处索引/看板同步更新完成 |
| IMP-006~013 | - | - | 待后续迭代规划执行 |

## Changelog

- 2026-07-06 | create | 模板v1.2升级补建：从export-suggestions.md迁移行动项至独立backlog文件（5项已交付完成，8项待规划/待执行）
