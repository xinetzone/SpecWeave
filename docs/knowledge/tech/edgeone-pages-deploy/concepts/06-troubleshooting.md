---
type: Concept
title: 故障排查速查表
description: 覆盖 CLI 未安装、esbuild postinstall 失败、浏览器不弹出、鉴权错误、项目名冲突、构建失败、预览链接 401 等高频故障的定位与解法
tags: [edgeone, troubleshooting, faq, errors]
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
  - id: S-002
    resource: /references/00-sources.md
    title: designer-portfolio 部署里程碑复盘报告
  - id: S-004
    resource: /references/00-sources.md
    title: edgeone CLI 实测输出（v1.2.30+）
---

# 故障排查速查表

按「现象 → 定位 → 解法」组织。前三条是本次实战真实遇到或高度相关的故障。

## 速查表

| 现象 | 定位 | 解法 |
|---|---|---|
| `command not found: edgeone` | CLI 未安装，或受管 Node 未加入 PATH | `npm install -g edgeone@latest`；若用受管 Node，先 `export PATH="<受管node目录>:$PATH"` |
| 安装报 esbuild `spawnargs ... --version` 失败、`pid: 0` | esbuild postinstall 执行平台二进制失败 | 静态站点：`npm install -g edgeone@latest --ignore-scripts`；框架项目：修复 `@esbuild/<platform>` 平台包后重装 |
| `Cannot find module 'open'` | 上一条的连锁后果——安装未终态导致依赖缺失 | 同上行；不要用「重装」原地打转，先修根因 |
| `edgeone -v` 版本 < 1.2.30 | 装到了旧版 | 重新安装 `edgeone@latest` 并复查版本 |
| 浏览器登录时窗口未弹出 | 无头/远程环境，或浏览器调用被拦截 | 手动打开 CLI 输出的跳转 URL；或直接改用 Token 登录 |
| 登录显示成功，但 `deploy` 报鉴权错误 | 浏览器复用了**另一个站点**的旧 session，账号错位 | 在登录页点「使用其他账户登录」；或先从所有腾讯云控制台退出后重登 |
| `edgeone whoami` 显示意外账号 | 同上（session 复用） | 同上 |
| `You are not authenticated` | 尚未登录 | `edgeone login --site china`，或设置 `EDGEONE_PAGES_API_TOKEN` / 用 `-t` 传 Token |
| Token 鉴权失败 | Token 过期或被撤销 | 到控制台 `?tab=settings` 重新生成 Token |
| 项目名冲突 | 同名项目已存在 | 换一个项目名（`-n <新名称>`） |
| 构建失败 | 依赖缺失或 `build` 脚本本身有问题 | 先在本地 `npm run build` 复现并修复，再交给平台构建 |
| 部署后访问 401 | 预览 URL 的鉴权参数过期或被分享给他人 | 重新部署取新链接；长期访问绑定已备案自定义域名 |
| 项目落在非预期区域 | 站点参数与加速区域解耦，CLI 输出可能显示 `global area` | 以控制台显示为准核对；需要国内加速则绑定已备案域名 |
| CLI 提示 `edgeone pages is deprecated` | 命令别名更新 | 仅为弃用警告，旧命令仍可用；后续改用 `edgeone makers` |

## 排错心法：表层报错 ≠ 根因

本次实战最关键的一条经验——**安装失败的表层报错与真实根因不在同一层**：

```
表象：Error: Cannot find module 'open'      ← CLI 启动时 require 失败
      ↓ 下钻一层
根因：esbuild postinstall spawn 失败         ← npm 判定整包安装失败，依赖未装全
      ↓ 验证
证据：edgeone/node_modules/@esbuild 不存在
```

遇到「缺模块」类报错时，先问一句：是**这个模块本身**没装，还是**安装流程中途失败**导致一批模块都没装？检查相邻依赖目录是否存在，能快速区分这两种情况。

## 环境相关的两点提醒

- **受管 Node 与系统 Node**：使用受管 Node 时，全局安装的 CLI 位于受管目录，未加入 PATH 会报 `command not found`。每次新开 shell 都要确认 PATH。
- **Windows 路径分隔符**：在命令与脚本中引用路径时用 `/` 或正确转义的 `\\`，避免路径解析失败被误判为「命令不存在」。

## 相关概念

- [CLI 安装与排错](/concepts/01-cli-install.md)
- [登录与鉴权](/concepts/02-login-auth.md)
- [解析部署产物](/concepts/05-deploy-output.md)
