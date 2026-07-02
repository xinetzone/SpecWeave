---
id: "ds-roles-raci"
title: "RACI责任矩阵与审批权限边界"
source: "role-responsibilities.md#02-raci-approvals"
x-toml-ref: "../../../../.meta/toml/.agents/rules/data-security/role-responsibilities/02-raci-approvals.toml"
---
# RACI责任矩阵与审批权限边界

## RACI责任分配矩阵

**RACI模型说明**：
- **R** = 负责执行（Responsible）：实际完成工作的角色
- **A** = 最终审批（Accountable）：对结果负最终责任，拥有最终决策权，每项活动有且仅有一个A
- **C** = 需咨询（Consulted）：决策前需征求意见、提供专业输入的角色，双向沟通
- **I** = 需知会（Informed）：决策后需告知进展与结果的角色，单向沟通

| 数据安全核心活动 | orchestrator | architect | developer | reviewer | tester | co-founder |
|:---|:---:|:---:|:---:|:---:|:---:|:---:|
| 数据分级标注 | I | C | **R** | **A** | C | I |
| 数据分类标准维护 | C | **R** | I | **A** | I | C |
| 脱敏方案设计 | C | **R** | C | **A** | I | I |
| 脱敏实施 | I | C | **R** | **A** | C | I |
| 加密方案设计 | C | **R** | C | **A** | I | I |
| 密钥管理（含轮换策略） | I | **R** | C | **A** | I | C |
| 密钥轮换执行 | I | C | C | **R/A** | I | I |
| 数据出境自评估 | C | C | I | **R/A** | I | C |
| 出境评估审批（一般/L3） | **A** | C | I | R | I | I |
| 出境评估审批（重大/国家级） | C | C | I | R | I | **A** |
| 供应商准入评估 | **A** | C | I | **R** | I | I |
| 供应商准入技术评审 | C | **A** | I | R | I | I |
| 供应商定期审计 | I | C | I | **R/A** | I | I |
| 监控告警处置（一般） | I | C | C | **R/A** | C | I |
| 监控告警处置（紧急） | **A** | C | C | R | I | I |
| 安全事件应急响应（III/IV级） | **R/A** | C | C | C | C | I |
| 安全事件应急响应（I/II级） | R | C | C | C | C | **A** |
| 安全事件复盘 | **R** | C | C | **A** | C | I |
| 安全规则更新 | C | C | I | **R** | I | **A** |
| 安全培训组织 | **R** | C | I | **A** | I | C |
| 代码安全审查 | I | I | C | **R/A** | I | I |
| 安全测试用例编写与执行 | I | C | C | C | **R/A** | I |
| 安全漏洞修复 | I | C | **R** | **A** | C | I |
| L4数据相关操作审批 | C | C | I | R | I | **A** |


## 关键数据安全活动审批权限边界

| 活动 | 审批权限级别 | 需提交材料 | 审批时限 |
|:---|:---|:---|:---|
| L4数据相关操作（访问/导出/修改/删除） | co-founder + architect 双审批 | ① 操作申请单（说明目的、范围、时间） ② 数据影响评估报告 ③ 安全防护方案 ④ 操作回滚预案 | 2个工作日 |
| 数据出境（L3级） | orchestrator审批，co-founder知会 | ① 数据出境自评估报告 ② 数据接收方安全资质证明 ③ 数据传输加密方案 ④ 合规性声明 | 3个工作日 |
| 数据出境（L4级/重大/国家级） | co-founder终审，orchestrator+architect联合评审 | ① 数据出境自评估报告（含法务审核） ② 监管机构报备材料（如需要） ③ 接收方安全评估报告 ④ 数据最小化方案 ⑤ 应急切断机制说明 | 5个工作日 |
| 新供应商接入 | architect技术评审 + orchestrator审批 | ① 供应商安全评估问卷 ② 供应商安全资质证明（ISO27001/等保等） ③ 数据处理协议（DPA）草案 ④ 接入技术方案 ⑤ 数据流向图 | 3个工作日 |
| 安全事件II级及以上响应 | co-founder总指挥，orchestrator协调 | ① 事件初步研判报告 ② 影响范围评估 ③ 遏制方案 ④ 通报范围建议 | 立即响应，30分钟内启动 |
| 加密方案变更 | architect审批 | ① 变更原因说明 ② 新旧方案对比 ③ 兼容性影响评估 ④ 迁移方案 ⑤ 回滚预案 | 2个工作日 |
| 密钥轮换（常规） | reviewer执行，orchestrator知会 | ① 密钥轮换计划 ② 轮换影响范围评估 ③ 验证方案 | 按计划执行，提前1个工作日报备 |
| 密钥轮换（紧急/泄露疑似） | reviewer立即执行，orchestrator+architect即时知会，事后co-founder报备 | ① 泄露风险说明 ② 紧急轮换操作记录 ③ 影响排查结果 | 立即执行，2小时内补交书面报告 |
| 紧急响应（I/II级安全事件） | 先执行遏制，后24小时内补审批 | ① 紧急处置记录 ② 遏制措施说明 ③ 后续整改计划 | 立即执行，事后补审 |
| 数据脱敏方案变更 | architect审批，reviewer会签 | ① 变更前后脱敏规则对比 ② 脱敏有效性验证方案 ③ 数据可用性影响评估 | 2个工作日 |
| 安全规则/策略更新 | reviewer起草，co-founder终审发布 | ① 规则更新说明 ② 影响范围评估 ③ 培训计划 | 3个工作日 |


---

## 相关模式

- [数据分类分级标准](../data-classification.md)
- [数据加密与密钥管理规范](../data-encryption.md)
- [数据安全监控体系](../security-monitoring.md)
- [第三方API供应商安全准入制度](../vendor-admission.md)
- [第三方API供应商持续审计制度](../vendor-audit.md)
- [数据出境安全评估机制](../cross-border-assessment.md)
- [数据安全治理角色职责矩阵](../role-responsibilities.md)

← 上一章: [规范说明与角色职责映射](01-overview-roles.md) | **[返回索引](../role-responsibilities.md)** | 下一章 → [数据安全门禁与角色能力培训](03-gates-training.md)
