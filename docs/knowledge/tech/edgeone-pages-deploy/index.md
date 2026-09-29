---
okf_version: "0.2"
title: EdgeOne Pages 前端部署教程
description: 面向前端开发者的 EdgeOne Pages 部署教程束——从 CLI 安装排错、登录鉴权到静态站点与框架项目部署，基于 2026-09-29 一次真实部署实战
tags: [edgeone, pages, deploy, frontend, tutorial]
status: draft
stale_after: "2027-09-29"
---

# EdgeOne Pages 前端部署教程

> 把本地前端项目部署到腾讯云 EdgeOne Pages 的完整教程：覆盖 CLI 安装排错、站点与登录方式选择、静态站点与框架项目两类部署路径、部署产物解析与故障排查。全部命令与数据来自 2026-09-29 的一次真实部署（`designer-portfolio` 作品集站点），非推测。

---

## 导航

```{toctree}
:hidden:
:maxdepth: 2

concepts/index
examples/index
references/index
log
```

| 类别 | 文档 | 说明 |
|------|------|------|
| **概览** | [平台概览与适用场景](/concepts/00-overview.md) | EdgeOne Pages 能力边界、China/Global 站点 |
| **准备** | [CLI 安装与 Windows 排错](/concepts/01-cli-install.md) | esbuild postinstall 故障根因与绕过 |
| **准备** | [登录与鉴权](/concepts/02-login-auth.md) | 浏览器登录 vs Token 登录 |
| **核心** | [部署静态站点](/concepts/03-deploy-static.md) | 无构建步骤项目，构建实测 81ms |
| **进阶** | [部署需构建的前端项目](/concepts/04-deploy-framework.md) | 框架自动检测与构建 |
| **收尾** | [解析部署产物](/concepts/05-deploy-output.md) | URL / 项目 ID / 落区 / 自定义域名 |
| **排错** | [故障排查速查表](/concepts/06-troubleshooting.md) | 14 类高频故障 |
| **实战** | [designer-portfolio 全流程](/examples/00-static-portfolio-full-flow.md) | 完整六步，含真实命令输出 |
| **信源** | [信源登记](/references/00-sources.md) | S-001～S-005 |
| **日志** | [变更日志](/log.md) | 文档版本记录 |

## 学习路径建议

1. **快速上手（10 分钟）**：平台概览 → CLI 安装与排错 → 登录与鉴权 → 部署静态站点
2. **照着做一遍**：直接跳到 [实战案例](/examples/00-static-portfolio-full-flow.md)，按六步复现
3. **上线后收尾**：解析部署产物（绑定自定义域名）→ 遇问题时查故障排查速查表
4. **框架项目部署**：部署需构建的前端项目（注意不可绕过 esbuild）

## 三条必须先知道的结论

1. **Windows 装 CLI 失败时，别被 `Cannot find module 'open'` 误导**——真实根因是 esbuild postinstall 失败。静态站点用 `npm install -g edgeone@latest --ignore-scripts` 绕过（详见 [CLI 安装与排错](/concepts/01-cli-install.md)）。
2. **访问 URL 必须整串复制**——`?eo_token=...&eo_time=...` 是鉴权参数，截断后页面打不开；长期对外访问要绑定已备案自定义域名（详见 [解析部署产物](/concepts/05-deploy-output.md)）。
3. **单体仓库部署前必须消歧**——「把这个前端项目部署」在含多个前端候选的仓库里没有唯一指代，先确认目标目录再执行（详见 [部署静态站点](/concepts/03-deploy-static.md)）。

---

**信源**：[本次部署里程碑复盘报告](../../../retrospective/reports/2026-09-29-edgeone-pages-deploy-milestone-retro.md)、EdgeOne Pages Deploy 技能文档（`~/.workbuddy/skills/edgeone-pages-deploy/SKILL.md`，仓库外路径）、[EdgeOne Pages 官方控制台](https://console.cloud.tencent.com/edgeone/pages)

**规范**：OKF v0.2（Open Knowledge Format）
