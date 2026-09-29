---
type: Concept
title: EdgeOne Pages 平台概览与适用场景
description: EdgeOne Pages 是腾讯云边缘安全加速平台提供的静态与前端托管服务，支持框架自动构建、全球 CDN 加速与自动 HTTPS，个人项目免费额度通常够用
tags: [edgeone, pages, hosting, cdn, overview]
generated:
  by: agent-workbuddy
  at: "2026-09-29T14:47:00+08:00"
verified:
  by: process:seven-concepts-v
  at: "2026-09-29T14:47:00+08:00"
status: draft
stale_after: "2027-09-29"
sources:
  - id: S-001
    resource: /references/00-sources.md
    title: EdgeOne Pages Deploy 技能文档
  - id: S-003
    resource: /references/00-sources.md
    title: EdgeOne Pages 官方控制台
---

# EdgeOne Pages 平台概览与适用场景

EdgeOne Pages 是腾讯云 EdgeOne（边缘安全加速平台）配套的前端托管服务，把本地的前端项目构建产物上传到你的账号下，生成独立的访问 URL 与项目记录。它覆盖两类场景：纯静态站点直接上传目录，需要构建的项目由平台自动检测框架、执行构建后再上传输出目录。

对于习惯把 demo、作品集、文档站快速分享出去的前端开发者，它的价值在于省掉自己搭服务器、配证书、接 CDN 这三件事。

## 核心能力

- **框架自动检测与构建**：平台识别 Vite / Next.js / Vue / Nuxt 等框架，自动执行安装与构建命令，上传输出目录；无需手写构建配置。
- **静态资源直传**：无构建步骤的纯静态目录（仅 `index.html` + CSS/JS/资源）由 `StaticAssetsBuilder` 直接拷贝上传。
- **全球 CDN 加速与自动 HTTPS**：默认获得加速节点与 HTTPS 证书，无需自行申请证书。
- **自定义域名绑定**：可绑定自有域名；面向长期对外访问时，这是预览链接的替代方案。
- **免费额度**：个人项目通常完全够用（具体额度以官方控制台为准）。

## 两个站点：China 与 Global

部署前必须明确站点，它决定账号归属与控制台入口：

| 站点 | 控制台域名 | 适用 |
|---|---|---|
| China（国内站） | `console.cloud.tencent.com` | 中国大陆用户，便于绑定已备案域名 |
| Global（国际站） | `console.intl.cloud.tencent.com` | 中国大陆以外用户 |

> ⚠️ 站点选择需要在登录前确认，不要由 AI 代为假定。实测中即使以 `--site china` 登录，CLI 创建项目时仍可能输出 `global area`（指加速区域），项目真实区域以控制台显示为准。

## 适用与不适用

| 场景 | 是否适用 | 说明 |
|---|---|---|
| 个人作品集 / 落地页 / 文档站 | ✅ 适用 | 静态直传，数十秒完成 |
| 前端框架应用（React/Vue/Next 等） | ✅ 适用 | 平台自动构建 |
| 需要长期稳定对外访问的生产站点 | ⚠️ 需额外配置 | 必须绑定已备案自定义域名，不依赖预览链接 |
| 需要后端服务 / 数据库的应用 | ❌ 不适用 | Pages 只托管前端静态产物 |
| 含敏感信息的内部材料 | ❌ 不适用 | 公开托管，不适合私密内容 |

## 本次实战环境

本教程基于 2026-09-29 的一次真实部署：Windows 环境、受管 Node 22.22.2、目标项目为 `apps/samples/designer-portfolio`（纯静态作品集，无 `package.json`）。整体耗时：CLI 安装 42s，登录 11s，部署 36s（其中构建 81ms）。

## 相关概念

- [CLI 安装与排错](/concepts/01-cli-install.md)
- [登录与鉴权](/concepts/02-login-auth.md)
- [部署静态站点](/concepts/03-deploy-static.md)
