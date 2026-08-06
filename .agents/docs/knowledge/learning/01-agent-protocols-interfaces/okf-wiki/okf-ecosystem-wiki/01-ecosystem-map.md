---
id: okf-ecosystem-infrastructure-01-ecosystem-map
title: "01 OKF 生态资源图谱"
version: "1.0"
source: ".chaos/libs/awesome-okf 上游英文版深度分析"
type: "Wiki Tutorial"
description: "OKF 上游生态资源九大分类图谱、build-okf-bundle.mjs 批转实现原理、社区工具清单"
tags: ["OKF", "生态图谱", "ecosystem", "build-okf-bundle", "awesome-okf"]
category: "learning"
date: "2026-08-06"
status: "stable"
author: "seven-concepts knowledge-scenario"
summary: "OKF上游英文生态（awesome-okf/linyiru）的资源分类图谱与'awesome 列表批转合规范 bundle'的 dogfooding 工程实现原理"
last_verified: "2026-08-06"
wiki_version: "1.0"
okf_version_target: "v0.2"
---

# 01 OKF 生态资源图谱

> 本页属于 [OKF 生态基建知识](./README.md) 系列，聚焦 [awesome-okf](https://github.com/linyiru/awesome-okf)（**上游英文版**）的生态资源分类与工程实现。OKF 通用规范概念请参考 [okf-wiki 主教程](../README.md)。

## 1.1 定位与来源

`awesome-okf`（上游英文版）仓库位于 `d:\AI\.chaos\libs\awesome-okf`，是一个 **Awesome 风格资源列表**，也是一个 **dogfooding 范例**——它既是一个人工维护的资源清单（README.md），又通过脚本自动生成一份**符合 OKF v0.2 规范的 bundle**（存放于 `bundle/` 目录），实现"列表即规范成员的活证明"。

| 仓库文件 | 作用 |
|---------|------|
| [README.md](../../../../../../../.chaos/libs/awesome-okf/README.md) | 人类可读的 Awesome 列表（资源主入口） |
| [bundle/index.md](../../../../../../../.chaos/libs/awesome-okf/bundle/index.md) | 由 README 生成的 OKF v0.2 合规范 bundle 索引 |
| [scripts/build-okf-bundle.mjs](../../../../../../../.chaos/libs/awesome-okf/scripts/build-okf-bundle.mjs) | 批转脚本：README → 合规范 bundle 的自动化实现 |

> **为什么不能直接让仓库根目录是 bundle？** OKF 要求每个非保留 `.md` 文件都带非空 `type` 的 frontmatter，而 Awesome 列表的 README.md 因 awesome-lint 校验无法强制加 frontmatter。因此用 `bundle/` 子目录镜像资源，README 与 bundle 解耦。

## 1.2 生态资源九大分类

上游 awesome-okf 将 OKF 生态资源划分为以下分类（对应 `build-okf-bundle.mjs` 中的 `TYPE_BY_SECTION` 映射表）：

| 分类 | OKF concept type | 说明 |
|------|------------------|------|
| Specification | `Specification` | OKF v0.2 规范、home 仓库、README |
| Official Tools & Reference Implementations | `Reference Implementation` | 官方参考 Agent、Enrichment toolbox、mdcode |
| Sample Bundles | `Sample Bundle` | GA4 / Stack Overflow / Bitcoin / ACME Retail 示例 |
| Community Tools | `Tool` | okft、okf-gem、okf-skills、knowledge-mcp 等社区工具 |
| Articles & Guides | `Article` | 官方博客、社区解读、SEO 视角文章 |
| Background & Origins | `Origin` | Karpathy LLM-Wiki、Vannevar Bush《As We May Think》 |
| Built on the LLM-Wiki Pattern | `Implementation` | AutoSci、llmwiki、Synto 等 LLM-wiki 模式实现 |
| Related Formats & Concepts | `Related Concept` | ARD、llms.txt、MCP、AGENTS.md、Obsidian 等 |
| Community | `Community` | 官方社媒、HN 讨论、中文 sister 列表 |

> **生态定位洞察**：OKF 生态 ≠ 只有规范，而是"规范 + 官方参考实现 + 生成工具 + 社区工具 + 相关格式 + 思想源头"的完整图谱。消费 OKF 时，可按需从不同分类取资源。

## 1.3 官方工具与参考实现

- **Reference Agent**（Python，基于 Google ADK）：从 BigQuery 源起草 OKF 文档，v0.2 起增强 web-crawled provenance（`sources` frontmatter + per-claim 脚注归因），附 `viewer/generator.py` 渲染自包含交互图谱
- **Knowledge Catalog Enrichment toolbox**（TypeScript）：生产/演进/维护元数据的 Agent 与可定制 harness，含把 Markdown 文件集暴露为 MCP server 的服务器
- **Knowledge Catalog mdcode**：把元数据当作源码产物管理，提供 git 风格 pull/push 在 OKF Markdown 与 BigQuery/Dataplex 间同步

## 1.4 社区工具速览

| 工具 | 语言 | 定位 | 关键能力 |
|------|------|------|---------|
| [okft](https://github.com/PoorvaJ-WW/okft) | Python | Linter + MCP server | `okft lint` 校验规范符合性与卫生（断链/孤儿/时间戳），`okft serve` 暴露 bundle 导航工具 |
| [okf-gem](https://github.com/serradura/okf-gem) | Ruby | bundle 全生命周期 harness | `validate`/`lint`/`search`/`server`/`render`，本地运行或 Docker |
| [okf-skills](https://github.com/scaccogatto/okf-skills) | Python | Claude Code 工具集 | 基于 v0.2（trust/provenance/staleness/attested computations） |
| [knowledge-mcp](https://github.com/chirag127/knowledge-mcp) | - | MCP server | `search`/`read`/`list`/`related`，Cloudflare Workers 部署 |
| [okf-kit](https://github.com/vinodborole/okf-kit) | Python | 构建/消费工具链 | `okf build/get/sync/zip/chat/visualize`（详见 [03-bundle-template.md](03-bundle-template.md)） |
| [OWOX Model Canvas](https://github.com/OWOX/models) | TS | 可视化建模编辑器 | Miro 风格，原生读写 OKF |
| [samemind](https://github.com/alexgrebeshok-coder/samemind) | Python | 个人记忆 | 以 OKF bundle 存储身份/工作台账/看板，零依赖 CLI + MCP server |

## 1.5 build-okf-bundle.mjs 批转实现原理

这是上游 awesome-okf 的 dogfooding 核心，把人工维护的 README 自动批转为合规范 bundle：

### 1.5.1 章节 → type 映射
`TYPE_BY_SECTION` 对象把 README 的 `##` 章节标题映射到 OKF concept `type`。未列入映射的章节（Contents / OKF at a Glance / Contributing）被跳过。

### 1.5.2 条目解析
正则 `^- \[([^\]]+)\]\(([^)]+)\) - (.+)$` 解析列表项，提取 `name`（链接文本）、`url`（链接地址）、`desc`（`-` 后描述）。

### 1.5.3 slug 规则
`slug()` 函数：转小写 → 去反引号 → 非字母数字转 `-` → 去首尾 `-`。用于生成目录名与文件名（如 `Official Tools & Reference Implementations` → `official-tools-reference-implementations`）。

### 1.5.4 frontmatter 生成
每个资源条目生成一个 concept 文件，frontmatter 含：
```yaml
type: <映射type>
title: <资源名>
description: <描述>
resource: <URL>
tags: [<章节slug>]
generated: { by: "process:build-okf-bundle", at: "2026-07-31T00:00:00Z" }
```

### 1.5.5 保留文件与结构
- `bundle/index.md`：根索引，frontmatter 仅声明 `okf_version: "0.2"`（符合 §12 规则）
- `bundle/log.md`：追加式变更历史，批转时**保留不清除**
- 每次构建先清除除 `log.md` 外的所有生成内容再重建

### 1.5.6 符合性自校验
`validate()` 遍历所有 `.md`，跳过 `index.md`/`log.md` 保留文件，检查每个 concept 文件都有 frontmatter 且 `type` 非空。不符合则 `process.exit(1)`，保证产物永远符合 OKF v0.2。

## 1.6 与中英文两版的关系

| 版本 | 仓库作者 | 定位 | 覆盖 |
|------|---------|------|------|
| 上游英文版 | linyiru | 国际生态资源图谱 | 九大分类、官方+社区工具、相关格式 |
| 中文版 | yzfly（云中江树） | 中文生态落地 | 规范翻译、7 producer 插件、7 Skill、3 扩展提案 |

中文版的深度分析见 [awesome-okf-analysis](../awesome-okf-analysis/README.md)，本页聚焦英文版生态图谱与批转工程实现。

---

| 上一页 | 目录 | 下一页 |
|--------|------|--------|
| [README](./README.md) | [OKF 生态基建](./README.md) | [02 Bundle 分发注册机制](./02-bundle-registry.md) |