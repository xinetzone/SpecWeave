---
id: okf-ecosystem-infrastructure-02-bundle-registry
title: "02 OKF Bundle 分发注册机制"
version: "1.0"
source: ".chaos/libs/awesome-okf-kit 深度分析"
type: "Wiki Tutorial"
description: "OKF bundle 社区注册表机制：registry.yaml 字段 Schema、okf get 消费流程、validate_registry.py 校验规则、发布流程与许可政策"
tags: ["OKF", "bundle", "registry", "okf-kit", "分发", "awesome-okf-kit"]
category: "learning"
date: "2026-08-06"
status: "stable"
author: "seven-concepts knowledge-scenario"
summary: "OKF bundle 如何通过 registry.yaml 机器可读索引实现社区分发与消费，含字段schema、消费流程、校验规则与许可政策"
last_verified: "2026-08-06"
wiki_version: "1.0"
okf_version_target: "v0.1/v0.2"
---

# 02 OKF Bundle 分发注册机制

> 本页属于 [OKF 生态基建知识](./README.md) 系列，聚焦 [awesome-okf-kit](https://github.com/vinodborole/awesome-okf-kit)（社区 bundle 注册表）。OKF 通用概念请参考 [okf-wiki 主教程](../README.md)。

## 2.1 定位与核心思想

`awesome-okf-kit`（位于 `d:\AI\.chaos\libs\awesome-okf-kit`）是一个 **OKF bundle 的社区注册表（registry）**，解决"OKF bundle 如何被发现、如何被消费"的分发问题。

**核心理念：索引而非存储。** 它不是 bundle 存储库，而是一个**机器可读索引**。每个 bundle 独立托管在自己的仓库并作为 release zip 发布，`registry.yaml` 只记录指向它们的元数据，`okf get` 据此下载、校验、安装。

## 2.2 两命令快速上手

```bash
pip install okf-kit
okf get rust-book              # 下载 + 校验一个已发布的 bundle
okf chat rust-book --provider ollama   # 用本地模型与知识库对话
```

## 2.3 registry.yaml 字段 Schema

`registry.yaml`（位于 `d:\AI\.chaos\libs\awesome-okf-kit\registry.yaml`）是 YAML 条目列表，每条记录一个 bundle 的元数据：

| 字段 | 必填 | 类型 | 说明 |
|------|:---:|------|------|
| `name` | ✅ | string | 唯一 bundle 名，**kebab-case**（`^[a-z0-9][a-z0-9-]*$`） |
| `source_url` | ✅ | string | 内容来源网站的 URL（校验以 `http://`/`https://` 开头） |
| `description` | ✅ | string | 一句话描述 |
| `license` | ✅ | string | **内容**的许可证（SPDX 标识符），非 okf-kit 的 |
| `download` | ✅ | string | release zip 的 https URL（必须以 `.zip` 结尾） |
| `category` | ❌ | string | 分类，用于网站分组 |
| `publisher` | ❌ | string | 发布者标识（如 `github.com/vinodborole`） |
| `repo` | ❌ | string | bundle 所在仓库 URL |
| `okf_version` | ❌ | string | 遵循的 OKF 版本（如 `"0.1"`） |
| `pages` | ❌ | int | 页面/概念数 |
| `tags` | ❌ | list | 标签数组 |

### 示例条目
```yaml
- name: rust-book
  source_url: https://doc.rust-lang.org/book/
  description: "The Rust Programming Language — the official book."
  license: "MIT OR Apache-2.0"
  category: Languages & Learning
  publisher: github.com/vinodborole
  repo: https://github.com/vinodborole/rust-book-okf
  download: https://github.com/vinodborole/rust-book-okf/releases/latest/download/rust-book-okf.zip
  okf_version: "0.1"
  pages: 109
  tags: [rust, programming, book, docs]
```

## 2.4 okf get 消费流程

`okf get <name>` 的完整流程：
1. **读取 registry**：从 `registry.yaml` 找到对应 `name` 的条目
2. **下载**：访问 `download` 字段的 release zip URL
3. **校验**：解压并验证 bundle 符合 OKF 规范
4. **安装**：安装到 `~/.okf/bundles/` 用户目录，供后续 `okf chat` 等命令使用

## 2.5 validate_registry.py 校验规则

`scripts/validate_registry.py` 在 CI 中对每次 PR 运行，有任何问题则非零退出：

| 校验项 | 规则 |
|--------|------|
| 顶层结构 | `registry.yaml` 必须是 YAML 列表，否则报错 |
| 必填字段 | 每个条目必须含 `name`/`source_url`/`description`/`license`/`download` |
| name 格式 | 必须匹配 kebab-case 正则 `^[az0-9][a-z0-9-]*$` |
| name 唯一性 | 不允许重复 name |
| download | 必须是 `https://` 开头且以 `.zip` 结尾 |
| source_url | 必须是合法的 `http://` 或 `https://` URL |

## 2.6 发布流程

1. **构建并发布** bundle（详见 [03-bundle-template.md](03-bundle-template.md)）：
   ```bash
   okf build https://your-docs.example.com -o your-docs-okf
   okf validate your-docs-okf     # 必须 CONFORMANT
   okf zip your-docs-okf
   ```
2. 将 bundle 放入独立仓库（推荐用 [okf-bundle-template](https://github.com/vinodborole/okf-bundle-template)），把 zip 附加到 GitHub Release
3. **开 PR** 向 `registry.yaml` 添加一个条目
4. **CI 校验** schema 与条目，维护者审查许可

## 2.7 许可政策

`policies/LICENSING.md` 规定 bundle 是网站内容的镜像，**仅当允许再分发时**才被接受：
- 你拥有内容源（自己的站点/文档），或
- 内容在允许再分发的许可下（CC-BY、CC-BY-SA、CC0/公有领域、MIT/Apache 等开源项目文档）

每个条目必须提供 `license`（内容许可，非工具许可）与 `source_url`（便于核验许可）。无法核验许可的 bundle 会被拒绝。`policies/TAKEDOWN.md` 提供移除机制。

> **生态定位洞察**：OKF 的分发不依赖中心化平台，而是"独立仓库 + release zip + 社区索引"的**去中心化 BSD 模式**。registry 只做发现与校验，不持有内容，规避了内容托管的法律与存储负担。

---

| 上一页 | 目录 | 下一页 |
|--------|------|--------|
| [01 生态资源图谱](./01-ecosystem-map.md) | [OKF 生态基建](./README.md) | [03 Bundle 工程化模板](./03-bundle-template.md) |