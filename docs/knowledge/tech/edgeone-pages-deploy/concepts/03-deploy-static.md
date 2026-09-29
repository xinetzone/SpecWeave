---
type: Concept
title: 部署静态站点（无构建步骤）
description: 纯静态目录（无 package.json）在项目根目录执行 deploy 即可，平台用 StaticAssetsBuilder 直接拷贝上传，实测构建仅 81ms
tags: [edgeone, deploy, static, html, tutorial]
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

# 部署静态站点（无构建步骤）

纯静态站点指不含 `package.json`、无需构建命令的目录——通常只有 `index.html`、`style.css`、`script.js` 与资源目录。这类项目部署最简单：不需要配置构建，平台直接把目录内容拷进产物目录再上传。

## 前置检查

在项目目录内确认三件事：

```bash
# 1. 确认是静态站点（无 package.json 即无需构建）
cat package.json 2>/dev/null || echo "NO package.json"

# 2. 确认是否已关联过项目（有 edgeone.json 说明已关联）
cat edgeone.json 2>/dev/null

# 3. 确认登录态
edgeone whoami
```

## 部署命令

在**项目根目录**执行：

```bash
# 新项目（无 edgeone.json）：用 -n 指定项目名
edgeone pages deploy -n <project-name>

# 已关联项目（有 edgeone.json）：直接部署
edgeone pages deploy
```

项目名建议取目录名（如 `designer-portfolio`）。首次部署会自动生成 `edgeone.json`，把本地目录与远端项目绑定，之后无需再带 `-n`。

## 实测执行过程

以 `apps/samples/designer-portfolio` 为例（目录含 `README.md`、`assets/`、`index.html`、`projects/`、`script.js`、`style.css`，共 6 个顶层条目，无 `package.json`）：

```
[cli][✔] Using local login token for deployment...
[cli] WARNING: Project designer-portfolio doesn't exist. Creating new project.
[cli] [CreatePagesProject] Creating new project with name: designer-portfolio in global area
[builder] InstallCommand is empty, skipping installation

🔍 [Logger Plugin] Pre-build hook triggered
📂 Working directory: D:\spaces\SpecWeave\apps\samples\designer-portfolio

[StaticAssetsBuilder] Start to execute...
[StaticAssetsBuilder] Copying files from <项目目录> to <项目目录>/.edgeone/assets
[StaticAssetsBuilder] Skipping excluded item: .edgeone
[StaticAssetsBuilder] Skipping excluded item: .env
[StaticAssetsBuilder] Copied directory: assets
[StaticAssetsBuilder] Copied file: index.html
[StaticAssetsBuilder] Copied directory: projects
[StaticAssetsBuilder] Copied file: README.md
[StaticAssetsBuilder] Copied file: script.js
[StaticAssetsBuilder] Copied file: style.css
[StaticAssetsBuilder] MoveProjectToAssets time: 80ms
build time 81ms
```

关键观察：

- 构建器识别为 **`StaticAssetsBuilder`**，无安装、无编译步骤（`InstallCommand is empty, skipping installation`）。
- 产物目录是项目下的 `.edgeone/assets`；`.edgeone` 与 `.env` 被自动排除，不会递归自拷贝。
- 构建耗时 **81ms**——纯文件拷贝，与项目大小线性相关（`assets` 2.1M 的本次案例也在此量级）。
- 顶层文件（含 `README.md`）会一并上传；若不想公开 README，部署前移出目录或改用框架模式配置输出目录。

## 部署阶段

```
[cli][✔] Deploying <项目目录>/.edgeone to project designer-portfolio (Production environment, global area)...
[cli][✔] Using Project ID: makers-kibjgortw1bl
[cli] Uploading folder to EdgeOne COS...
[cli][Uploader] Uploading file: 100%
[cli][✔] File uploaded successfully
[cli][✔] Creating deployment in Production environment...
[cli][✔] Created deployment with Deployment ID: dpebpaq47jjs
[cli] Waiting for deployment to complete...
[cli] Deployment in progress... (status: Process, elapsed: ~10s)
[cli] Deployment in progress... (status: Process, elapsed: ~20s)
[cli][✔] Deploy Success
```

部署阶段包含上传与状态轮询，本次实测共 36 秒、轮询 2 次。

## 部署到其他环境

默认部署到 Production（生产）环境。需要预览环境时加 `-e preview`：

```bash
edgeone pages deploy -e preview
```

## 单体仓库注意事项

在 monorepo 中部署前**必须先确认目标目录**。本仓库根无 `package.json`，`find` 命中 11 个 `package.json` 与 11 个前端配置文件——「把这个前端项目部署」这类指令存在指代歧义，凭直觉猜会部署错误产物。做法是列出候选目录让使用者确认后再执行。

另外注意：`vendor/` 为 git submodule，其下的前端项目不应作为本地部署修改对象。

## 相关概念

- [登录与鉴权](/concepts/02-login-auth.md)
- [部署需构建的前端项目](/concepts/04-deploy-framework.md)
- [解析部署产物](/concepts/05-deploy-output.md)
