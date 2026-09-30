---
type: Example
title: 实战：把 designer-portfolio 静态作品集部署上线
description: 在 SpecWeave 单体仓库中定位并部署纯静态作品集站点到 EdgeOne Pages 国内站的完整过程，含安装故障修复、登录、部署与产物解析
tags: [edgeone, example, static-site, portfolio, hands-on]
generated:
  by: agent-workbuddy
  at: "2026-09-29T14:47:00+08:00"
verified:
  by: process:seven-concepts-v
  at: "2026-09-29T14:47:00+08:00"
status: draft
stale_after: "2027-09-29"
sources:
  - id: S-002
    resource: /references/00-sources.md
    title: designer-portfolio 部署里程碑复盘报告
  - id: S-004
    resource: /references/00-sources.md
    title: edgeone CLI 实测输出（v1.2.30+）
---

# 实战：把 designer-portfolio 静态作品集部署上线

本例复盘 2026-09-29 一次真实部署：在 SpecWeave 单体仓库中，把 `apps/samples/designer-portfolio`（纯静态作品集）部署到 EdgeOne Pages。全程约 3 分钟，中间修掉一个 CLI 安装故障。

## 背景与目标

- **环境**：Windows，受管 Node 22.22.2，Git Bash
- **目标项目**：`apps/samples/designer-portfolio`（6 个顶层条目：`README.md`、`assets/`、`index.html`、`projects/`、`script.js`、`style.css`；无 `package.json`；`assets` 2.1M，`projects` 含 4 个页面）
- **目标站点**：China（国内站）
- **起点状态**：CLI 未安装、未登录、项目未关联

## 步骤 1：环境预检

```bash
export PAGES_SOURCE=skills
edgeone -v        # → command not found: edgeone
edgeone whoami    # → command not found
```

三个检查项全部落空：CLI 未安装、未登录、无 `edgeone.json`。

## 步骤 2：在单体仓库中定位项目（消歧）

仓库根没有 `package.json`，用两个 `find` 摸清候选：

```bash
find . -maxdepth 4 -name package.json -not -path "*/node_modules/*" | wc -l   # → 11
find . -maxdepth 4 \( -name "vite.config.*" -o -name "next.config.*" \
  -o -name "vue.config.*" -o -name "angular.json" -o -name "index.html" \) \
  -not -path "*/node_modules/*" | wc -l                                        # → 11
```

11 个 `package.json` + 11 个前端配置——「把这个前端项目部署」存在指代歧义。列举候选后由使用者确认，选定 `apps/samples/designer-portfolio`，站点选 China。

> 这一步不能跳过。凭直觉猜会部署错误产物，既浪费一次部署，也会在账号下留下错误项目记录。

## 步骤 3：安装 CLI（踩坑与修复）

常规安装失败：

```bash
npm install -g edgeone@latest
# 1m38s 后失败
# npm error spawnargs: [ '.../esbuild/bin/esbuild', '--version' ]
# npm error status: null, pid: 0

edgeone -v
# Error: Cannot find module 'open'
# Require stack: .../edgeone/edgeone-dist/cli.js
```

下钻一层定位根因：

```bash
ls <全局>/edgeone/node_modules/@esbuild          # → No such file or directory
ls <全局>/edgeone/node_modules/esbuild/node_modules/@esbuild  # → No such file or directory
```

平台二进制目录不存在 → esbuild postinstall 失败 → npm 中止安装 → `open` 未装上。目标项目是纯静态站点（构建为文件拷贝，不触发 esbuild），因此可以安全绕过：

```bash
npm install -g edgeone@latest --ignore-scripts
# added 6 packages, and changed 162 packages in 38s  （42s 完成）

edgeone -v        # → 正常输出版本横幅
edgeone whoami    # → You are not authenticated  （正常，尚未登录）
```

## 步骤 4：登录

```bash
edgeone login --site china
```

输出跳转 URL 并自动打开浏览器：

```
[cli] Jumping to login page...
[cli] Please come back after login.
If the browser does not open automatically, please visit:
https://cloud.tencent.com/login?s_url=...&state=2d5c9b9a-e89b-4422-848a-1cd520c8baa4
[cli][✔] .gitignore updated!
[cli][✔] Login successfully!
```

约 11 秒完成。

## 步骤 5：部署

在项目根目录执行（首次部署，无 `edgeone.json`，需 `-n`）：

```bash
cd apps/samples/designer-portfolio
edgeone pages deploy -n designer-portfolio
```

构建阶段（81ms，纯拷贝）：

```
[StaticAssetsBuilder] Copying files from ... to .../.edgeone/assets
[StaticAssetsBuilder] Skipping excluded item: .edgeone
[StaticAssetsBuilder] Skipping excluded item: .env
[StaticAssetsBuilder] Copied directory: assets
[StaticAssetsBuilder] Copied file: index.html
[StaticAssetsBuilder] Copied directory: projects
[StaticAssetsBuilder] Copied file: README.md
[StaticAssetsBuilder] Copied file: script.js
[StaticAssetsBuilder] Copied file: style.css
build time 81ms
```

部署阶段（上传 + 2 次状态轮询）：

```
[cli][✔] Using Project ID: makers-kibjgortw1bl
[cli] Uploading folder to EdgeOne COS...
[cli][Uploader] Uploading file: 100%
[cli][✔] Created deployment with Deployment ID: dpebpaq47jjs
[cli] Deployment in progress... (status: Process, elapsed: ~10s)
[cli] Deployment in progress... (status: Process, elapsed: ~20s)
[cli][✔] Deploy Success
```

整体 36 秒。

## 步骤 6：解析产物

```
[cli][✔] Deploy URL: https://designer-portfolio-w1ras6ms.edgeone.cool?eo_token=629627c63dd4e9bc9254e0518735a4b4&eo_time=1790663452
[cli][✔] Console URL: https://console.cloud.tencent.com/edgeone/pages/project/makers-kibjgortw1bl/deployment/dpebpaq47jjs
```

- **访问 URL**：必须整串保留，含 `?eo_token=...&eo_time=...`
- **Project ID**：`makers-kibjgortw1bl`
- **Deployment ID**：`dpebpaq47jjs`

## 结果核对清单

| 项 | 结果 |
|---|---|
| 站点是否可访问 | ✅ 部署成功，URL 可打开 |
| 构建方式 | `StaticAssetsBuilder`（无安装、无编译） |
| 构建耗时 | 81ms |
| 部署总耗时 | 36s |
| 落区 | CLI 输出 `global area`（与 `--site china` 不一致，以控制台为准） |
| 长期访问 | ⚠️ 预览链接可能过期，需绑定已备案自定义域名 |

## 本例的三条经验

1. **安装报错要下钻一层**：`Cannot find module 'open'` 的根因是 esbuild postinstall 失败，不是包损坏。
2. **monorepo 必须消歧**：11 + 11 个候选下，「这个项目」没有唯一指代。
3. **URL 不能截断**：query 里的 `eo_token`/`eo_time` 是访问鉴权，去掉就打不开。

## 相关概念

- [部署静态站点](/concepts/03-deploy-static.md)
- [CLI 安装与排错](/concepts/01-cli-install.md)
- [解析部署产物](/concepts/05-deploy-output.md)
