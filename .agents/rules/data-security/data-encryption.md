---
id: "rules-data-security-data-encryption"
title: "数据加密与密钥管理规范"
source: "AGENTS.md#规则体系"
x-toml-ref: "../../../../.meta/toml/.agents/rules/data-security/data-encryption/rules-data-security-data-encryption.toml"
---
# 数据加密与密钥管理规范

> 本规范是AI智能体互联数据安全治理体系的技术防护核心模块，与[数据分类分级标准](data-classification.md)、[数据脱敏技术规范](data-masking.md)配套使用，定义传输加密、存储加密、字段级加密技术规范及全生命周期密钥管理要求，覆盖与第三方AI API通信的加密要求。


## 文档导航

| 章节 | 说明 |
|------|------|
| [规范说明与加密体系总览](data-encryption/01-overview-system.md) | 加密规范目的、适用范围、基本原则、加密体系总览 |
| [传输加密与存储加密规范](data-encryption/02-transport-storage.md) | TLS要求、密码套件、mTLS、证书管理、磁盘/数据库/备份加密 |
| [字段级加密规范](data-encryption/03-field-encryption.md) | 必须加密字段清单、算法选择、IV/Nonce要求、密文格式 |
| [密钥全生命周期管理](data-encryption/04-key-lifecycle.md) | 密钥生成、存储、分发、轮换、归档、销毁、访问控制 |
| [第三方API通信加密与实施检查清单](data-encryption/05-api-checklist.md) | API密钥传输、请求体加密、响应签名、检查清单 |

---

## 相关模式

- [数据分类分级标准](data-classification.md)
- [数据加密与密钥管理规范](data-encryption.md)
- [数据安全监控体系](security-monitoring.md)
- [第三方API供应商安全准入制度](vendor-admission.md)
- [第三方API供应商持续审计制度](vendor-audit.md)
- [数据出境安全评估机制](cross-border-assessment.md)
- [数据安全治理角色职责矩阵](role-responsibilities.md)
