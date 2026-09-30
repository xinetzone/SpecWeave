---
id: "inurl-byok-api-reference"
title: "接口清单"
source: "../README.md"
---
# 接口清单

> 内容迁移自根 README §4。鉴权与错误状态码语义见 [05-auth-and-errors.md](05-auth-and-errors.md)。

## 本地代理（`/v1`）

| 路由 | 鉴权 | 说明 |
|---|---|---|
| `GET /v1/models` | 用户 | 逻辑别名 + 已录入厂商的真实模型 |
| `POST /v1/chat/completions` | 用户 | OpenAI 兼容；响应含 `_route`（最终厂商/策略/切换次数/跳过原因） |
| `GET /v1/metrics` | 用户 | 控制台轮询的代理状态 |
| `GET/PUT /v1/settings` | 用户 | 路由策略、Combo、压缩档、限池 |
| `GET /v1/capabilities` | 用户 | 别名与能力标签映射 |

## 账户与密钥库（`/api`）

`POST /api/register`、`POST /api/login`、`POST /api/unlock`、`POST /api/unlock/recover`、
`GET/POST /api/escrow`、`POST /api/recover`、`POST /api/password`、
`GET/POST/DELETE /api/keys`、`GET/POST /api/orders`、`POST /api/orders/{id}/proof`

## 公开（无鉴权）

`GET /api/catalog`（`?all=1` 与默认同一份数据）、`GET /api/billing/plans`、
`GET /api/turnstile`（默认 `enabled:false`）、`GET /api/ads`、`GET /api/news`

## 管理员后台（`/api/admin`，非管理员 403）

八模块（[services/ops_service.py](../src/inurl_byok_token_hub/services/ops_service.py) 的 `ADMIN_MODULES`，`GET /api/admin/modules` 返回同一清单）：
`users` 用户管理 / `catalog` 厂商目录（含 `POST /api/admin/catalog/reload`）/ `plans` 套餐与订单（含 `confirm`、`reject` 人工核销）/ `redemption` 待核销订单 / `usage` 用量总览 / `content` 公告与广告位 / `config` 系统配置 / `audit` 审计日志。

端点：`GET /api/admin/{modules,users,catalog,keys,usage,orders,audit,config}`、`POST /api/admin/config`、`POST /api/admin/catalog/reload`、`POST /api/admin/orders/{id}/{confirm,reject}`。

> 口径差异见 [08-assumptions-and-differences.md](08-assumptions-and-differences.md) A24：F-097 记录的后台八模块是「Turnstile 配置/邀请码/用户管理/广告/资讯/官网链接/catalog-overrides/待核销订单」，与本复刻的枚举不同。

## 控制台（`/console`）

`/console/login`、`/console/keys`、`/console/usage`、`/console/routes`、`/console/plans`、`/console/logout`
