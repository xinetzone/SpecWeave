---
id: "rules-data-security-data-masking"
title: "数据脱敏技术规范"
source: "AGENTS.md#规则体系"
x-toml-ref: "../../../.meta/toml/.agents/rules/data-security/data-masking.toml"
---
# 数据脱敏技术规范

> 本规范是AI智能体互联数据安全治理体系的技术防护模块，与[数据分类分级标准](data-classification.md)配套使用，定义静态脱敏与动态脱敏的适用场景、各类脱敏技术实施指南、AI场景特殊脱敏规则及脱敏有效性验证方法。

## 文档导航

| 文档 | 主题 | 说明 |
|------|------|------|
| [data-masking/01-overview-principles.md](data-masking/01-overview-principles.md) | 概述与基本原则 | 目的、适用范围、基本原则、脱敏vs加密对比 |
| [data-masking/02-scenarios-and-matrix.md](data-masking/02-scenarios-and-matrix.md) | 场景分类与四级矩阵 | 静态/动态脱敏、L1-L4脱敏要求矩阵 |
| [data-masking/03-basic-techniques.md](data-masking/03-basic-techniques.md) | 基础脱敏技术 | 掩码、替换、泛化、扰动四种不可逆技术 |
| [data-masking/04-reversible-and-strict-techniques.md](data-masking/04-reversible-and-strict-techniques.md) | 可逆与严格脱敏技术 | FPE加密脱敏、令牌化、删除/抑制 |
| [data-masking/05-ai-scenario-rules.md](data-masking/05-ai-scenario-rules.md) | AI场景特殊脱敏规则 | 提示词PII、对话历史、训练数据、系统提示词、模型输出、RAG检索 |
| [data-masking/06-validation-methods.md](data-masking/06-validation-methods.md) | 有效性验证方法 | 定性审查、定量评估、可用性验证、工具推荐 |
| [data-masking/07-implementation-checklist.md](data-masking/07-implementation-checklist.md) | 实施检查清单 | 20项实施自查清单 |

**[返回上级](../README.md)**
