---
type: Translation
title: Awesome OKF Kit 中文翻译
description: vinodborole/awesome-okf-kit 项目 README 的中文翻译，OKF 即用型知识包社区注册表
source: vendor/awesome-okf-kit/README.md
x-toml-ref: "../../../../../.meta/toml/docs/knowledge/learning/01-agent-protocols-interfaces/okf-wiki/awesome-okf-kit-README.zh-CN.toml"
tags:
  - OKF
  - 开放知识格式
  - 知识包
  - Bundle Registry
  - AI Agent
  - 翻译
---
# awesome-okf-kit

**一个面向即用型 [OKF](https://github.com/GoogleCloudPlatform/knowledge-catalog/blob/main/okf/SPEC.md)（开放知识格式，Open Knowledge Format）知识包的社区注册表。**

预构建、智能体就绪、自更新的流行文档站点知识库——两条命令即可拉取一个，使用您自己的大语言模型或完全离线地与之对话：

```bash
pip install okf-kit
okf get rust-book              # 下载并验证已发布的知识包
okf chat rust-book --provider ollama
```

基于 **[okf-kit](https://github.com/vinodborole/okf-kit)**（库）构建
——隶属于 [calknowledge](https://github.com/vinodborole/calknowledge)
生态系统。

## 工作原理

本仓库是一个**索引**，而非知识包存储库。每个知识包位于其各自的仓库中，以发布 zip 包的形式分发；[`registry.yaml`](registry.yaml) 指向它们，`okf get` 下载 zip 包、验证它，并安装到
`~/.okf/bundles/` 目录。

## 目录

<!-- CATALOG:START (generated from registry.yaml) -->
### AI 与智能体

| 知识包 | 来源 | 许可证 | 页数 |
|---|---|---|---|
| [`dspy-book`](https://github.com/vinodborole/dspy-book-okf) | [dspy.ai](https://dspy.ai/) | MIT | 70 |
| [`mcp-book`](https://github.com/vinodborole/mcp-book-okf) | [modelcontextprotocol.io](https://modelcontextprotocol.io/docs) | CC-BY-4.0 | 16 |
| [`pydantic-ai-book`](https://github.com/vinodborole/pydantic-ai-book-okf) | [ai.pydantic.dev](https://ai.pydantic.dev/) | MIT | 90 |

### Web 与框架

| 知识包 | 来源 | 许可证 | 页数 |
|---|---|---|---|
| [`astro-book`](https://github.com/vinodborole/astro-book-okf) | [docs.astro.build](https://docs.astro.build/) | MIT | 90 |
| [`fastapi-book`](https://github.com/vinodborole/fastapi-book-okf) | [fastapi.tiangolo.com](https://fastapi.tiangolo.com/tutorial/) | MIT | 51 |
| [`flask-book`](https://github.com/vinodborole/flask-book-okf) | [flask.palletsprojects.com](https://flask.palletsprojects.com/en/stable/) | BSD-3-Clause | 74 |
| [`svelte-book`](https://github.com/vinodborole/svelte-book-okf) | [svelte.dev](https://svelte.dev/docs) | MIT | 90 |
| [`tailwind-book`](https://github.com/vinodborole/tailwind-book-okf) | [tailwindcss.com](https://tailwindcss.com/docs) | MIT | 87 |

### 数据与机器学习

| 知识包 | 来源 | 许可证 | 页数 |
|---|---|---|---|
| [`dbt-book`](https://github.com/vinodborole/dbt-book-okf) | [docs.getdbt.com](https://docs.getdbt.com/) | Apache-2.0 | 90 |
| [`duckdb-book`](https://github.com/vinodborole/duckdb-book-okf) | [duckdb.org](https://duckdb.org/docs/) | MIT | 80 |
| [`polars-book`](https://github.com/vinodborole/polars-book-okf) | [docs.pola.rs](https://docs.pola.rs/) | MIT | 90 |

### 库与工具

| 知识包 | 来源 | 许可证 | 页数 |
|---|---|---|---|
| [`bun-book`](https://github.com/vinodborole/bun-book-okf) | [bun.sh](https://bun.sh/docs) | MIT | 90 |
| [`httpx-book`](https://github.com/vinodborole/httpx-book-okf) | [python-httpx.org](https://www.python-httpx.org/) | BSD-3-Clause | 23 |

### 平台与 DevOps

| 知识包 | 来源 | 许可证 | 页数 |
|---|---|---|---|
| [`backstage-book`](https://github.com/vinodborole/backstage-book-okf) | [backstage.io](https://backstage.io/docs/) | Apache-2.0 | 139 |
| [`meshapi-book`](https://github.com/vinodborole/meshapi-book) | [developers.meshapi.ai](https://developers.meshapi.ai/) |  | 23 | 138 |

### 编程语言与学习

| 知识包 | 来源 | 许可证 | 页数 |
|---|---|---|---|
| [`rust-book`](https://github.com/vinodborole/rust-book-okf) | [doc.rust-lang.org](https://doc.rust-lang.org/book/) | MIT OR Apache-2.0 | 109 |
<!-- CATALOG:END -->

## 发布您的知识包

请参阅 **[CONTRIBUTING.md](CONTRIBUTING.md)** 和 okf-kit 的
[docs/PUBLISHING.md](https://github.com/vinodborole/okf-kit/blob/main/docs/PUBLISHING.md)。
简而言之：`okf build` → 以发布 zip 包形式发布，附带每周自同步 GitHub Action →
提交 PR 添加 `registry.yaml` 条目。CI 验证 schema 并在您的知识包上运行
`okf validate`。

> **许可说明：**仅发布您有权再分发的内容——您自己的站点，或
> 宽松许可的内容（CC-BY、CC-BY-SA、开源项目文档、
> 公有领域）。`license` 和 `source_url` 为必填字段。请参阅
> [policies/LICENSING.md](policies/LICENSING.md) 和
> [policies/TAKEDOWN.md](policies/TAKEDOWN.md)。

## 许可证

注册表索引和工具采用 MIT 许可。每个知识包携带其自己的内容
许可证（其条目的 `license` 字段）。
