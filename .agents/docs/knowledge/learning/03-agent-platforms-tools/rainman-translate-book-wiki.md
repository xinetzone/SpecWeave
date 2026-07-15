---
id: "rainman-translate-book-wiki"
title: "Rainman Translate Book Wiki 教程"
source: "https://mp.weixin.qq.com/s/99dnIuSUL4WHkm-_UzQYAw"
x-toml-ref: "../../../../../.meta/toml/docs/knowledge/learning/03-agent-platforms-tools/rainman-translate-book-wiki.toml"
---
# Rainman Translate Book Wiki 教程

> **原文来源**: [微信公众号文章](https://mp.weixin.qq.com/s/99dnIuSUL4WHkm-_UzQYAw) | **GitHub**: [deusyu/translate-book](https://github.com/deusyu/translate-book)

---

## 概述

**Rainman Translate Book** 是一个基于 Claude Code Skill 的开源整书翻译项目，由开发者 deusyu 创建。它利用 Claude Code 的子代理机制，将整本书拆分为多个小块，启动 8 个并行子代理同时翻译，再通过术语表（Glossary）和相邻上下文机制保证翻译质量的一致性。支持 PDF、DOCX、EPUB 输入，输出 HTML、DOCX、EPUB、PDF 五种格式。

**核心认知**：大模型上下文窗口有限，整书翻译不能硬塞。Rainman Translate Book 的思路不是"塞进更多 token"，而是"切碎 + 并行 + 术语锁定 + 上下文关联"，通过精巧的 Agent 架构设计解决翻译质量与效率的矛盾。

---

## 目录导航

| 序号 | 章节 | 文件 | 内容概要 |
|---|---|---|---|
| 00 | 教程概述与学习目标 | [rainman-translate-book-wiki/00-overview.md](rainman-translate-book-wiki/00-overview.md) | 项目背景介绍、学习目标、前置知识要求、文档导航 |
| 01 | 核心功能详解 | [rainman-translate-book-wiki/01-core-concepts.md](rainman-translate-book-wiki/01-core-concepts.md) | 五大核心功能：并行子代理翻译、术语表锁定、相邻上下文、断点续传、多格式输出 |
| 02 | 安装部署指南 | [rainman-translate-book-wiki/02-installation.md](rainman-translate-book-wiki/02-installation.md) | 环境要求、分平台安装步骤（macOS/Linux/Windows）、三种 Skill 安装方式、验证安装 |
| 03 | 使用流程 | [rainman-translate-book-wiki/03-usage.md](rainman-translate-book-wiki/03-usage.md) | 快速上手、指定 EPUB 封面、修改术语表后重新翻译、完整工作流程图解 |
| 04 | 局限性与注意事项 | [rainman-translate-book-wiki/04-limitations.md](rainman-translate-book-wiki/04-limitations.md) | 环境依赖门槛、Calibre 格式丢失风险、适用场景边界、与 Claude 网页版/CAT 工具对比 |
| 05 | 总结与回顾 | [rainman-translate-book-wiki/05-summary.md](rainman-translate-book-wiki/05-summary.md) | 核心要点回顾、关键 Takeaway、下一步学习建议 |
| 06 | 常见问题 | [rainman-translate-book-wiki/06-faq.md](rainman-translate-book-wiki/06-faq.md) | 翻译质量、费用、语言支持、中断恢复、术语修正、图片翻译、与 Claude 网页版区别 |
| 07 | 资源链接 | [rainman-translate-book-wiki/07-resources.md](rainman-translate-book-wiki/07-resources.md) | 原始资源、官方仓库、依赖工具、本项目内相关 Wiki |

---

> **最后更新**：2026年7月
>
> 本教程基于微信公众号文章《整书翻译神器！GitHub 爆火 NPM 包，一键将整本书翻译成中文》（作者：小黑，极客之家公众号）编写，所有技术信息均来自公开可验证的来源。