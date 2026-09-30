---
type: Reference
title: EdgeOne Pages 部署教程信源登记
description: 本教程束的全部信源登记，含本地技能文档、本次实战部署记录、官方控制台与 CLI 实测输出
tags: [edgeone, pages, sources, reference]
generated:
  by: agent-workbuddy
  at: "2026-09-29T14:47:00+08:00"
verified:
  by: process:seven-concepts-v
  at: "2026-09-29T14:47:00+08:00"
status: draft
stale_after: "2027-09-29"
sources:
  - id: S-000
    resource: /references/00-sources.md
    title: 本文件（信源自登记）
---

# EdgeOne Pages 部署教程信源登记

本文件登记 OKF 教程束 `edgeone-pages-deploy` 引用的全部信源。所有概念文档与示例文档的 `sources` 字段均指向本文件中的信源条目，保证事实可溯源。

## 信源清单

| 信源 ID | 标题 | 类型 | 获取方式 | 稳定性 |
|---|---|---|---|---|
| S-001 | EdgeOne Pages Deploy 技能文档 | 本地技能文档 | `~/.workbuddy/skills/edgeone-pages-deploy/SKILL.md` | stable |
| S-002 | designer-portfolio 部署里程碑复盘报告 | 本仓库复盘报告 | `docs/retrospective/reports/2026-09-29-edgeone-pages-deploy-milestone-retro.md` | stable |
| S-003 | EdgeOne Pages 官方控制台 | 官方站点 | https://console.cloud.tencent.com/edgeone/pages | stable |
| S-004 | edgeone CLI 实测输出（v1.2.30+） | 命令实测记录 | 2026-09-29 于 Windows 受管 Node 22.22.2 环境执行 `edgeone` 各子命令采集 | stable |
| S-005 | EdgeOne Pages 国际站控制台 | 官方站点 | https://console.intl.cloud.tencent.com/edgeone/pages | stable |

## 信源说明

### S-001 EdgeOne Pages Deploy 技能文档

本地技能门面，定义「环境检查 → 安装 → 登录 → 部署 → 解析产物」五段流程、站点选择（China/Global）、登录方式决策（浏览器/Token）、以及错误速查表。本教程的主干流程与该技能一致。

记录时间：2026-09-29。该文件在本次实战中已增补两处排错结论：`--ignore-scripts` 安装绕过、`edgeone pages` 弃用提示说明。

### S-002 designer-portfolio 部署里程碑复盘报告

本次实战的一手记录，含 21 条客观事实（F1–F21）、3 条洞察、1 个可复用模式。本教程中的命令输出片段、耗时数据、项目 ID 与部署 ID 均以此为准。

报告路径：`docs/retrospective/reports/2026-09-29-edgeone-pages-deploy-milestone-retro.md`
导出副本：`docs/retrospective/reports/exported/edgeone-pages-deploy-milestone-retrospective-20260929-v1.0.md`

### S-003 EdgeOne Pages 官方控制台（国内站）

用于登录授权、查看部署记录、获取 API Token、绑定自定义域名。国内站域名为 `console.cloud.tencent.com`。

### S-004 edgeone CLI 实测输出

2026-09-29 实际执行的命令与输出，包括：

- `edgeone -v`：版本横幅输出
- `edgeone whoami`：`You are not authenticated`
- `edgeone login --site china`：跳转 URL 与 `Login successfully`
- `edgeone pages deploy -n designer-portfolio`：完整构建与部署日志

CLI 版本要求 ≥ 1.2.30。实测安装耗时 42s（`--ignore-scripts`），部署耗时 36s。

### S-005 EdgeOne Pages 国际站控制台

面向中国大陆以外用户的控制台，域名为 `console.intl.cloud.tencent.com`。站点选择影响登录与项目归属，需与部署目标区域一并确认。

## 信源稳定性说明

本束无临时克隆或 `file:///` 绝对路径引用——全部信源为本地仓库内文件、官方站点 URL 与实测命令输出，不依赖易失效的临时目录。因此本束无需执行 GATE-SPS 临时信源升级流程。

## 相关概念

- [EdgeOne Pages 平台概览](/concepts/00-overview.md)
- [CLI 安装与排错](/concepts/01-cli-install.md)
