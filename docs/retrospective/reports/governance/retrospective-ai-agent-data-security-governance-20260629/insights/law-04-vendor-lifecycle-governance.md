+++
id = "law-vendor-lifecycle-governance"
date = "2026-06-29"
type = "insight"
scope = "vendor-management,lifecycle,third-party-risk"
source = "../insight-extraction.md#洞察5供应商管理的全生命周期闭环模型"
archived_to = "docs/retrospective/patterns/methodology-patterns/governance-strategy/vendor-lifecycle-governance.md"
+++

# 规律4：供应商全生命周期闭环模型

→ 正式模式：[vendor-lifecycle-governance.md](../../../../patterns/methodology-patterns/governance-strategy/vendor-lifecycle-governance.md)（已入库L1）

## 事件事实

本次将第三方API供应商管理拆分为两个文档——vendor-admission（准入）和vendor-audit（持续审计），形成准入→审计→评级→处置的闭环。

## "准入即终点"的常见错误

传统供应商管理常犯的错误是"准入即终点"——通过准入评估后不再持续监督。但数据安全风险是动态的：

- 供应商可能被收购、更换数据中心位置
- 供应商可能发生安全事件但未主动通报
- 供应商的安全策略可能随业务变化而调整
- 新的漏洞和攻击手段不断出现

## 四阶段闭环模型

| 阶段 | 核心活动 | 关键产出 |
|------|---------|---------|
| 准入 | 资质审查、安全评估、合规承诺、接入测试 | 准入评估报告、安全协议、黑白名单 |
| 审计 | 定期评估、日志审计、合规检查、渗透测试 | 审计报告、安全评级、问题清单 |
| 评级 | 根据审计结果动态调整安全等级 | A/B/C/D级供应商分类 |
| 处置 | 整改通知、暂停接入、永久拉黑、退出机制 | 处置记录、供应商状态更新 |

## 洞察结论

供应商管理不是一次性动作而是持续循环——审计结果反馈回准入标准（发现新风险点更新准入checklist），评级结果影响审计频率（C级供应商加密审计频次），处置结果更新黑白名单。

## 适用场景

这个闭环模型适用于所有外部依赖管理：
- 云服务商
- SaaS工具
- 开源组件
- API供应商
- 第三方外包团队

## 关联洞察

- [law-01-five-layer-governance-architecture.md](law-01-five-layer-governance-architecture.md) — 供应商管理属于流程控制层
- [finding-03-multi-doc-single-task-granularity.md](finding-03-multi-doc-single-task-granularity.md) — 准入+审计曾被错误合并为单任务

---
*来源：[AI智能体数据安全治理复盘](../README.md)*
