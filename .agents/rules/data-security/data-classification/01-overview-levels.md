---
id: "ds-classify-overview"
title: "规范说明与分级定义"
source: "data-classification.md#01-overview-levels"
x-toml-ref: "../../../../.meta/toml/.agents/rules/data-security/data-classification/01-overview-levels.toml"
---
# 规范说明与分级定义

## 规范说明

### 目的

本规范旨在建立统一的数据分类分级体系，保障跨模型数据流转安全，明确不同级别数据在AI智能体互联场景下的保护要求、流转边界与处理规范，防范数据泄露、滥用与合规风险。

### 适用范围

本规范适用于TRAE系统接入第三方AI API的全场景，包括但不限于：

- 国内大模型API接入（如豆包、文心一言、通义千问等）
- 境外大模型API接入（如GPT、Claude、Gemini等）
- 用户提示词处理、对话历史存储、模型输入输出管理
- 微调数据集上传、系统提示词配置、API密钥管理
- 多智能体协作场景下的数据共享与流转

### 分级原则

- **就高不就低**：当一份数据同时包含多个级别特征时，按最高级别定级
- **场景定级**：同一数据在不同场景下可能适用不同级别，需结合具体使用场景判定
- **动态调整**：数据级别可随时间、业务状态、公开程度变化进行升降级
- **可审计**：所有分级判定与级别变更必须留痕，支持事后审计

### 与国标合规关系

本规范在《数据安全法》《个人信息保护法》《网络安全法》及《数据出境安全评估办法》等法律法规框架下制定，与GB/T 35273《信息安全技术 个人信息安全规范》、GB/T 37973《信息安全技术 大数据安全管理指南》等国家标准保持一致，并针对AI智能体互联场景做了专项细化。


---

## 相关模式

- [数据分类分级标准](../data-classification.md)
- [数据加密与密钥管理规范](../data-encryption.md)
- [数据安全监控体系](../security-monitoring.md)
- [第三方API供应商安全准入制度](../vendor-admission.md)
- [第三方API供应商持续审计制度](../vendor-audit.md)
- [数据出境安全评估机制](../cross-border-assessment.md)
- [数据安全治理角色职责矩阵](../role-responsibilities.md)

**[返回索引](../data-classification.md)** | 下一章 → [AI场景数据分类映射](02-ai-scenarios.md)
