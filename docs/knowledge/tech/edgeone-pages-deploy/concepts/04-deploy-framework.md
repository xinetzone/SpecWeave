---
type: Concept
title: 部署需构建的前端项目
description: 含 package.json 的框架项目由平台自动检测框架并执行安装与构建命令，上传输出目录，无需手写构建配置；此类项目不可使用 --ignore-scripts 安装 CLI
tags: [edgeone, deploy, framework, vite, next, build]
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

# 部署需构建的前端项目

含 `package.json` 的前端框架项目（Vite / Next.js / Vue / Nuxt 等）不需要你手写构建配置——平台在部署时自动检测框架、执行安装与构建命令，然后上传框架的输出目录（如 `dist/`、`build/`、`.next/`）。

## 与静态部署的差异

| 维度 | 静态站点（无 package.json） | 框架项目（有 package.json） |
|---|---|---|
| 构建器 | `StaticAssetsBuilder`（纯拷贝） | 框架构建器（安装 + 构建） |
| 安装命令 | 跳过（`InstallCommand is empty`） | 自动执行依赖安装 |
| 上传内容 | 项目目录本身（排除 `.edgeone`/`.env`） | 构建输出目录 |
| 本次实测耗时 | 构建 81ms | 本次未实测（视依赖体积而定） |
| CLI 安装方式 | 可用 `--ignore-scripts` 绕过 esbuild | 不可绕过，需修复 esbuild 平台二进制 |

## 部署命令

命令形式与静态站点完全一致——平台根据目录内容自动分流：

```bash
# 在项目根目录执行
edgeone pages deploy -n <project-name>
```

## 关键差异：CLI 安装不能绕过 esbuild

静态站点场景可以用 `--ignore-scripts` 跳过 esbuild 的 postinstall（因为不触发 esbuild 变换）。**框架项目不行**——构建过程依赖完整的工具链，跳过安装脚本可能导致 esbuild 二进制缺失，构建阶段失败。

框架项目遇到 esbuild postinstall 失败时，应修复平台二进制本身：

1. 确认平台包缺失：检查 `edgeone/node_modules/@esbuild` 是否存在
2. 安装对应平台包（如 Windows x64 的 `@esbuild/win32-x64`）或修复网络后重新常规安装
3. 用 `edgeone -v` 验证后再部署

## 常见构建失败原因

构建阶段报错时，优先排查两类：

- **依赖缺失**：`package.json` 的依赖未正确声明，或锁文件与依赖不一致
- **构建脚本错误**：`build` 脚本本身在本地也无法跑通——先在本地执行 `npm run build` 复现并修复，再交给平台构建

本地能构建成功是平台能构建成功的前提；平台不会修复你项目里的构建错误。

## 环境变量

项目若需要构建期环境变量，平台会从项目设置中拉取。本地 `.env` 文件在部署时会被排除（实测日志显示 `Skipping excluded item: .env`），敏感配置应通过控制台的项目环境变量配置，而非随代码上传。

## 相关概念

- [部署静态站点](/concepts/03-deploy-static.md)
- [CLI 安装与排错](/concepts/01-cli-install.md)
- [故障排查速查表](/concepts/06-troubleshooting.md)
