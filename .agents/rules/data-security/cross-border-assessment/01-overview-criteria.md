---
id: "ds-crossborder-overview"
title: "规范说明与出境判定标准"
source: "cross-border-assessment.md#01-overview-criteria"
x-toml-ref: "../../../../.meta/toml/.agents/rules/data-security/cross-border-assessment/01-overview-criteria.toml"
---
# 规范说明与出境判定标准

## 规范说明

### 目的

规范跨境数据流动，防范数据出境安全风险，满足《数据出境安全评估办法》和国标要求，确保向境外AI服务提供商传输数据的行为合法合规，保障国家安全、公共利益、个人权益和企业合法权益。

### 适用范围

本规范适用于TRAE系统向境外服务器发送数据的所有场景，包括但不限于：

- 境外大模型API调用（GPT、Claude、Gemini等）
- 模型训练、微调数据上传至境外服务器
- 数据备份至境外云存储服务
- 境外团队访问境内数据系统
- 日志、监控数据传输至境外分析平台
- 与境外第三方进行数据共享、联合分析

### 法规依据

- 《中华人民共和国数据安全法》
- 《中华人民共和国个人信息保护法》
- 《中华人民共和国网络安全法》
- 《数据出境安全评估办法》（国家互联网信息办公室）
- 《个人信息出境标准合同办法》
- 《信息安全技术 数据出境安全评估指南》（GB/T 39335）
- AI智能体互联相关国家标准与行业规范

### 基本原则

- **数据最小化**：仅传输实现业务目的所必需的最少数据，禁止过度收集和传输
- **必要性评估**：每一项数据出境必须经过必要性论证，可在境内完成的处理不得出境
- **风险可控**：出境前必须完成风险评估并落实相应管控措施，确保风险在可接受范围内
- **全程审计**：所有数据出境活动必须全程留痕，日志留存不少于3年，支持事后追溯审计


---

## 相关模式

- [数据分类分级标准](../data-classification.md)
- [数据加密与密钥管理规范](../data-encryption.md)
- [数据安全监控体系](../security-monitoring.md)
- [第三方API供应商安全准入制度](../vendor-admission.md)
- [第三方API供应商持续审计制度](../vendor-audit.md)
- [数据出境安全评估机制](../cross-border-assessment.md)
- [数据安全治理角色职责矩阵](../role-responsibilities.md)

**[返回索引](../cross-border-assessment.md)** | 下一章 → [出境风险自评估清单](02-self-assessment.md)
