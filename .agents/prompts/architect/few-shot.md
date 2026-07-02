---
id: "prompts-architect-few-shot"
title: "Architect Few-shot 示例"
source: "AGENTS.md#提示词"
x-toml-ref: "../../../.meta/toml/.agents/prompts/architect/few-shot.toml"
---
# Architect Few-shot 示例

## 示例 1: 用户登录模块架构设计

**输入**: 需求：设计用户登录模块，支持邮箱密码与 OAuth 第三方登录，需保证安全性与可扩展性。

**输出**:
架构设计文档：

- 背景与目标：为系统提供统一的用户认证入口，支持多种登录方式，便于后续扩展。
- 整体架构：采用策略模式封装不同登录方式，通过统一认证门面对外暴露。
- 模块说明：
  - AuthFacade：统一认证入口，接收登录请求并路由至对应策略。
  - EmailLoginStrategy：邮箱密码登录策略，负责密码校验与令牌签发。
  - OAuthLoginStrategy：第三方 OAuth 登录策略，负责令牌交换与用户绑定。
- 接口定义：LoginRequest、LoginResponse、ILoginStrategy。
- 非功能需求：密码使用 bcrypt 加盐存储，登录令牌采用 JWT，有效期 2 小时。
- 风险与缓解：OAuth 提供方不可用风险，通过降级为邮箱登录缓解。

## 示例 2: 技术选型评估

**输入**: 需要为日志收集模块选择技术方案，候选方案为 ELK 与 Loki。

**输出**:
技术选型对比：

| 维度 | ELK | Loki | 最终选择 |
|---|---|---|---|
| 部署复杂度 | 高，需独立集群 | 低，可与 Grafana 集成 | Loki |
| 资源占用 | 高，全文索引 | 低，仅索引标签 | Loki |
| 查询能力 | 强，支持全文检索 | 中，基于标签查询 | ELK |
| 成本 | 高 | 低 | Loki |

最终选择：Loki。理由：当前日志量中等，资源敏感，标签查询能力满足需求，后续如需全文检索可扩展接入 ELK。
