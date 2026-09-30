---
type: Concept
title: edgeone CLI 安装与 Windows 排错
description: edgeone CLI 要求版本不低于 1.2.30；Windows 受管 Node 环境下常规安装会因 esbuild postinstall 失败而中断，静态站点场景可用 --ignore-scripts 绕过
tags: [edgeone, cli, npm, install, troubleshooting, windows]
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
  - id: S-004
    resource: /references/00-sources.md
    title: edgeone CLI 实测输出（v1.2.30+）
---

# edgeone CLI 安装与 Windows 排错

`edgeone` 是 EdgeOne Pages 的命令行工具，负责登录、构建与上传。安装本身只有一条命令，但在 Windows 受管 Node 环境下存在一处高频故障，本节给出根因与绕过方法。

## 版本要求

CLI 版本必须 **≥ 1.2.30**，低于该版本不要继续后续流程，直接重装。

```bash
edgeone -v
```

正常时输出 ASCII 版本横幅（含 logo）。若返回 `command not found: edgeone`，说明尚未安装或 PATH 未生效。

## 标准安装

```bash
npm install -g edgeone@latest
```

安装后再次执行 `edgeone -v` 验证。若版本低于 1.2.30，重试安装。

## 环境变量

在执行任何 `edgeone` 命令前，建议设置来源标识（技能场景要求）：

```bash
export PAGES_SOURCE=skills
```

若使用受管 Node（非系统 Node），需把受管 Node 加入 PATH，否则命令找不到：

```bash
export PATH="/c/Users/<user>/.workbuddy/binaries/node/versions/<ver>:$PATH"
```

## Windows 受管 Node 环境的安装故障

### 现象

常规安装执行约 1 分 38 秒后失败，npm 报错包含：

```
spawnargs: [ '.../edgeone/node_modules/esbuild/bin/esbuild', '--version' ]
status: null
signal: null
pid: 0
```

此时若直接运行 `edgeone -v`，Node 抛出：

```
Error: Cannot find module 'open'
Require stack:
- .../edgeone/edgeone-dist/cli.js
```

### 根因

两处报错不在同一层，需要下钻一层才能定位：

1. **真实断点**：esbuild 的 `postinstall` 脚本尝试执行其平台二进制（`esbuild --version`）时 spawn 失败（表现为 `pid: 0`）。检查可见平台包目录 `edgeone/node_modules/@esbuild` 不存在。
2. **连锁后果**：npm 判定整包安装失败并中止，依赖未装全——`open` 模块缺失。
3. **表象**：CLI 启动时 `require('open')` 失败，抛出 `Cannot find module 'open'`。

若只按表象处理，会误判为「edgeone 包损坏」而反复重装，问题依旧。

### 绕过方法（静态站点场景）

```bash
npm install -g edgeone@latest --ignore-scripts
```

`--ignore-scripts` 跳过 esbuild 的 postinstall，使安装正常终态。实测耗时 42 秒，输出 `added 6 packages, and changed 162 packages in 38s`，随后 `edgeone -v` 正常。

**为什么静态站点可以这样做**：纯静态项目的构建阶段是 `StaticAssetsBuilder` 的文件拷贝（实测 build time 81ms），不触发 esbuild 变换，因此缺少 esbuild 二进制不影响部署。

**含构建步骤的项目**：不要用此绕过——需单独修复 esbuild 平台二进制（安装对应 `@esbuild/<platform>` 包或修复网络后重装），再进行正常安装。

### 验证安装成功

```bash
edgeone -v          # 应输出版本横幅，不再报 Cannot find module
edgeone whoami      # 未登录时返回 "You are not authenticated"，属正常
```

`whoami` 返回未登录是正常的——它只表示尚未鉴权，不代表安装失败。

## 相关概念

- [EdgeOne Pages 平台概览](/concepts/00-overview.md)
- [登录与鉴权](/concepts/02-login-auth.md)
- [故障排查速查表](/concepts/06-troubleshooting.md)
