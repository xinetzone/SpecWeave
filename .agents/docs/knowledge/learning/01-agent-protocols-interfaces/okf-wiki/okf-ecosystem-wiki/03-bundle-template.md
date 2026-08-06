---
id: okf-ecosystem-infrastructure-03-bundle-template
title: "03 OKF Bundle 工程化发布模板"
version: "1.0"
source: ".chaos/libs/okf-bundle-template 深度分析"
type: "Wiki Tutorial"
description: "okf-bundle-template 的 GitHub Actions 工作流（build.yml/sync.yml）、okf-kit CLI 命令速查、NOTICE.md 许可署名与 registry 接入流程"
tags: ["OKF", "bundle", "template", "okf-kit", "github-actions", "CI/CD"]
category: "learning"
date: "2026-08-06"
status: "stable"
author: "seven-concepts knowledge-scenario"
summary: "把网站发布为自更新 OKF bundle 的工程化模板：CI 构建、每周同步、release 打包、注册表接入的完整工作流"
last_verified: "2026-08-06"
wiki_version: "1.0"
okf_version_target: "v0.1"
---

# 03 OKF Bundle 工程化发布模板

> 本页属于 [OKF 生态基建知识](./README.md) 系列，聚焦 [okf-bundle-template](https://github.com/vinodborole/okf-bundle-template)（GitHub 模板仓库）。OKF 通用概念请参考 [okf-wiki 主教程](../README.md)。

## 3.1 定位

`okf-bundle-template`（位于 `d:\AI\.chaos\libs\okf-bundle-template`）是一个 **GitHub 模板仓库**，一键把一个网站发布为**自更新的 OKF bundle**，并接入 [awesome-okf-kit](https://github.com/vinodborole/awesome-okf-kit) 注册表。

**解决的问题**：手动把网站内容转成合规范 OKF bundle 并保持新鲜，是重复且易错的工作。模板通过 CI 自动化完成"爬取 → 构建 → 提交 → 发布 release"全流程，并用**每周同步**保持 bundle 新鲜且 commit 小。

## 3.2 使用流程（四步）

1. **从模板创建仓库**（GitHub "Use this template" 按钮）
2. **运行 _Build bundle_ 工作流**（Actions 标签 → Build bundle → Run workflow），填入站点 URL 与 bundle 名。它爬取站点、提交 bundle、发布 `v0.1.0` release zip
3. **编辑 `NOTICE.md`**，填写来源的许可/署名
4. **加入注册表**：向 [awesome-okf-kit](https://github.com/vinodborole/awesome-okf-kit) 开 PR，添加指向 release zip 的 `registry.yaml` 条目（`…/releases/latest/download/<name>-okf.zip`）

## 3.3 build.yml 工作流（手动触发构建）

`.github/workflows/build.yml` 是手动触发的构建工作流，可配置参数：

| 输入参数 | 默认值 | 说明 |
|---------|--------|------|
| `url` | 无（必填） | 要爬取的站点 URL |
| `name` | `my-bundle` | bundle 名（kebab-case） |
| `max_depth` | `3` | 最大爬取深度 |
| `max_pages` | `200` | 最大页面数 |
| `js` | `false` | 是否渲染 JavaScript（true 时安装 Playwright chromium） |
| `path_prefix` | 空 | 仅爬取该路径下（空 = 自动从 URL 推断） |
| `all_paths` | `false` | 是否爬取整个主机 |

**执行步骤**：
1. `pip install okf-kit`（`js=true` 时安装 `okf-kit[js]`）
2. `okf build <url> -o <name> --max-depth N --max-pages N [--js] [--path-prefix P] [--all-paths]`
3. 生成含使用说明的 `README.md`
4. **提交**：`git config user.name okf-bot` → `git add -A && git commit && git push`
5. **发布**：`okf zip <name> -o <name>-okf.zip` → `gh release create v0.1.0`（或 `gh release upload ... --clobber` 覆盖）

## 3.4 sync.yml 工作流（每周同步）

`.github/workflows/sync.yml` 通过 cron（`0 6 * * 1`，每周一 06:00 UTC）自动同步：

1. `pip install okf-kit`
2. **发现 bundle**：查找 `*/.okf-kit/state.json`，若无则跳过（模板本身或空仓库）
3. `okf sync <dir>`：**只重写变更页面**，保持 commit 小
4. **提交增量**：`okf-bot` commit `sync: <date>`（无变更则跳过）
5. **重打包 release**：`okf zip` 后 `gh release upload v0.1.0 --clobber` 覆盖

> **增量同步的价值**：`okf sync` 只重写变化的页面而非全量重建，使每次同步的 commit 差异最小化，便于审查与追溯。

## 3.5 okf-kit CLI 命令速查

| 命令 | 作用 |
|------|------|
| `okf build <url> -o <name>` | 从网站爬取构建 OKF bundle |
| `okf validate <dir>` | 校验 bundle 符合 OKF 规范 |
| `okf zip <dir> -o <zip>` | 打包 release zip |
| `okf get <name>` | 从注册表下载 + 校验 + 安装 bundle |
| `okf sync <dir>` | 增量同步 bundle（只重写变更页面） |
| `okf chat <name> --provider <p>` | 与知识库对话（如 `ollama`） |
| `okf visualize <name>` | 可视化 bundle 知识图谱 |

## 3.6 NOTICE.md 许可署名

`NOTICE.md` 是许可/署名占位文件，要求替换为来源的 attribution 与 license notice。这是发布到注册表的合规前提——**只发布允许再分发的内容**（自己站点，或 CC-BY、CC-BY-SA、MIT/Apache 项目文档、公有领域）。

## 3.7 生态闭环总结

结合 [02-bundle-registry.md](02-bundle-registry.md)，OKF bundle 的完整工程化闭环为：

```
okf-bundle-template        awesome-okf-kit
(生产端)                   (分发端)
网站 → okf build          registry.yaml 索引
    → okf validate    →   okf get 下载/校验/安装
    → okf zip              okf chat/visualize 消费
    → weekly sync(保鲜)
    → PR 加入 registry
```

> **生态定位洞察**：模板把"内容→OKF bundle→可发现→可消费→持续保鲜"全链路 CI 化，是 OKF 生态从"少量手工 bundle"走向"大规模文档知识库"的关键工程化组件。与 [01 生态图谱](01-ecosystem-map.md) 的 `okf-kit` 工具（社区工具分类）同源——okf-kit 既是构建工具也是消费工具。

---

| 上一页 | 目录 | 下一页 |
|--------|------|--------|
| [02 Bundle 分发注册机制](./02-bundle-registry.md) | [OKF 生态基建](./README.md) | （已完成，是本系列最后一章） |