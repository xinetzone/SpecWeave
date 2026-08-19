---
id: "deepseek-v4-free-plan-overview"
title: "00 DeepSeek-V4 免费方案全景"
version: "1.0"
source: "官方API文档 + DeepSeek官网 + 14个权威来源交叉验证"
type: "Research Report"
description: "DeepSeek-V4正式版免费方案全景：三层免费路径对比、核心结论速览、适用人群推荐"
tags: ["DeepSeek", "DeepSeek-V4", "免费方案", "API定价", "大模型", "AI工具"]
category: "learning/07-vendor-product-learning"
date: "2026-08-19"
status: "stable"
author: "seven-concepts knowledge-scenario"
summary: "DeepSeek-V4正式版采用三层免费金字塔：网页/App永久免费无会员、API新用户赠500万tokens、V4-Flash开源可自托管。API峰谷定价于8月17日生效，普通用户完全不受影响。"
last_verified: "2026-08-19"
research_session: "sc-20260819-deepseek-v4-free-plan"
---

# 00 DeepSeek-V4 免费方案全景

> **信息更新时间**：2026年8月19日 | **定价生效时间**：2026年8月17日0时（北京时间）

## 0.1 三条核心结论

1. **普通用户完全免费，无会员计划**：网页端（chat.deepseek.com）和官方App使用V4-Pro满血版，无需付费，官方明确表示不设个人订阅/会员。
2. **API新用户赠送500万tokens**：注册platform.deepseek.com即赠，无需信用卡，有效期约30天，覆盖V4-Pro和V4-Flash。
3. **8月17日API涨价仅影响开发者**：峰谷定价（高峰9:00-12:00/14:00-18:00价格翻倍）仅针对API调用，网页/App使用完全不受影响。

## 0.2 三层免费路径对比

DeepSeek的免费体系是一个**三层金字塔结构**，而非单一的"免费vs付费"二元划分：

| 维度 | 网页/App聊天 | API新用户赠送额度 | 开源自托管 |
|------|-------------|-----------------|-----------|
| **入口** | chat.deepseek.com / App | platform.deepseek.com | HuggingFace下载权重 |
| **是否免费** | ✅ 完全免费 | ✅ 赠送额度内免费 | ✅ 权重免费（需自备GPU） |
| **默认模型** | V4-Pro | V4-Pro + V4-Flash | V4-Flash（Pro未开源） |
| **免费额度** | 无硬性限制（fair-use软节流） | 500万tokens（约30天） | 无调用限制 |
| **需要信用卡** | ❌ 不需要 | ❌ 不需要 | ❌ 不需要 |
| **上下文长度** | 1M tokens | 1M tokens | 1M tokens（自部署配置） |
| **最大输出** | 384K tokens | 384K tokens | 384K tokens（自部署配置） |
| **联网搜索** | ✅ 支持 | ❌ 需自行实现 | ❌ 需自行实现 |
| **文件上传** | ✅ PDF/图片/代码 | ❌ API方式传入 | ❌ 自行处理 |
| **Tool Calls** | 内置功能 | ✅ 支持 | ✅ 支持（自部署） |
| **SLA保障** | 无（尽力服务） | 无（免费额度） | 自控 |
| **隐私/数据** | 数据经DeepSeek服务器 | 数据经DeepSeek服务器 | ✅ 完全本地 |
| **适合人群** | 普通用户/学生/日常使用 | 开发者/原型验证/小规模应用 | 企业/合规/有GPU团队 |

## 0.3 文档导航

| 章节 | 内容 | 适合读者 |
|------|------|---------|
| [01 网页/App免费使用](01-web-app-free.md) | 功能范围、登录方式、限流说明 | 所有用户 |
| [02 API免费额度详解](02-api-free-tier.md) | 500万tokens规则、注册流程、消耗估算 | 开发者 |
| [03 API定价与对比](03-api-pricing-comparison.md) | 峰谷价格表、缓存机制、竞品对比 | 开发者/企业 |
| [04 V4-Pro能力详解](04-v4-pro-capabilities.md) | 技术规格、Agent能力、推理模式 | 技术用户 |
| [05 V4-Flash能力详解](05-v4-flash-capabilities.md) | 轻量模型定位、与Pro差异 | 开发者 |
| [06 开源自托管](06-self-hosting.md) | 硬件需求、部署步骤、MIT协议 | 技术团队 |
| [07 第三方免费路径](07-third-party-free.md) | OpenRouter/HF/Colab等途径 | 进阶用户 |
| [08 免费vs付费决策](08-free-vs-paid.md) | 多维对比、选型决策树、成本估算 | 决策者 |
| [09 FAQ与误区澄清](09-faq-mythbusting.md) | 常见疑问、谣言驳斥 | 所有用户 |
| [10 术语表](10-glossary.md) | 专业术语解释 | 初学者 |

## 0.4 你适合哪种免费路径？

```
你是谁？
├─ 只想聊天/写文案/查资料 → 网页/App直接用，零成本，无需注册付费
├─ 想开发AI应用/写脚本调用
│   ├─ 先试试/做原型 → API注册送500万tokens，够跑2-4周原型
│   ├─ 正式上线有一定量 → V4-Flash空闲时段调用，成本可控
│   └─ 大规模/对价格敏感 → V4-Flash自托管 + API闲时调度混合方案
├─ 企业/有合规要求 → 自托管V4-Flash或联系企业服务
└─ 想白嫖体验不同平台 → 第三方免费层（注意风险）
```

## 0.5 重要提醒

- ⚠️ **警惕不实信息**：部分自媒体传播"79.9元会员"、"每日50次API限制"等信息，均与官方政策不符，详见 [09 FAQ](09-faq-mythbusting.md)。
- ⚠️ **价格以官方为准**：API价格可能变动，请以 [api-docs.deepseek.com](https://api-docs.deepseek.com/zh-cn/quick_start/pricing/) 实时显示为准。
- ⚠️ **英文文档滞后**：截至2026年8月19日，英文API定价页面尚未更新峰谷价格，仍显示旧美元定价；峰谷定价仅在中文文档中公布。
