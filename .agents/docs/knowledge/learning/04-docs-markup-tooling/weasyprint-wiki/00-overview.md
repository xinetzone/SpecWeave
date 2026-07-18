---
id: "weasyprint-wiki-overview"
title: "WeasyPrint 教程总览"
x-toml-ref: "../../../../../../.meta/toml/.agents/docs/knowledge/learning/04-docs-markup-tooling/weasyprint-wiki/00-overview.toml"
source: "https://weasyprint.org/ | https://weasyprint.com/ | 源码 d:\\spaces\\SpecWeave\\external\\WeasyPrint"
category: "learning"
tags: ["weasyprint", "pdf", "html", "css", "rendering-engine", "python", "overview", "tutorial"]
date: "2026-07-13"
status: "stable"
author: "SpecWeave"
summary: "WeasyPrint 是用 Python 编写的面向打印媒体的 HTML/CSS 渲染引擎，无需浏览器即可生成高质量 PDF。本教程从第一性原理出发，覆盖架构解析、安装配置、API 指南、CSS 分页特性、高级功能、源码导览、方案对比、最佳实践与常见问题。"
---
# WeasyPrint：从 HTML/CSS 到 PDF 的渲染引擎深度解析

## 教程简介

**WeasyPrint** 是一个用 Python 编写的、面向打印媒体的 HTML/CSS 视觉渲染引擎，它将 HTML/CSS 文档渲染为高质量 PDF，不依赖任何浏览器引擎。

本教程基于 WeasyPrint v69.0（BSD 许可证）源码和官方文档深度分析，遵循**「技术wiki四层需求结构」**组织：先讲清"为什么需要WeasyPrint"，再教"怎么快速上手"，然后覆盖"遇到问题怎么办"，最后深入"为什么这么设计"，适合从新手到资深开发者的全场景需求。

> **官方网站**: https://weasyprint.org/
> **商业支持**: https://weasyprint.com/
> **GitHub**: https://github.com/Kozea/WeasyPrint
> **官方文档**: https://doc.courtbouillon.org/weasyprint

## 核心特性一览

| 特性类别 | 支持情况 |
|----------|----------|
| HTML 解析 | HTML5（通过 tinyhtml5） |
| CSS 选择器 | CSS2.1 + 大部分 CSS3 Selectors |
| 盒模型 | Block/Inline/Table/Flex/Grid/Inline-block |
| 分页媒体 | `@page`、分页符、页码、边距盒、交叉引用、脚注 |
| 文本排版 | 连字符、字体子集化、行内对齐、复杂脚本 |
| 图形 | 内联 SVG、渐变、边框圆角、阴影、变换 |
| PDF 特性 | 书签、链接、PDF/A、PDF/UA、PDF/X、表单、标签、附件 |
| 色彩 | sRGB、CMYK ICC 色彩配置文件 |

**关键取舍**：不支持 JavaScript、不支持 CSS 动画、CSS Grid/Flex 高级特性支持不如现代浏览器完整——这是"面向打印"设计的主动选择，而非缺陷。

## 章节导航

| 层级 | 章节 | 标题 | 内容概要 | 文件 |
|------|------|------|----------|------|
| **① 动机层** | 1 | 第一性原理与核心定位 | PDF生成本质矛盾、现有方案痛点、WeasyPrint定位、特性矩阵、不支持什么 | [01-first-principles-positioning.md](01-first-principles-positioning.md) |
| **② 上手层** | 2 | 六步渲染管线架构 | 从HTML到PDF的六步管线：解析→CSS→计算→盒树→布局→绘制 | [02-rendering-pipeline.md](02-rendering-pipeline.md) |
| | 3 | 技术栈与依赖 | Python包依赖、系统C库、垂直工具链架构 | [03-tech-stack-dependencies.md](03-tech-stack-dependencies.md) |
| | 4 | 安装与快速开始 | 系统依赖、pip安装、命令行使用、验证方法 | [04-installation-cli.md](04-installation-cli.md) |
| | 5 | Python API 完全指南 | 核心类、多种输入源、自定义CSS、渲染选项、分步渲染、URL获取器、finisher钩子 | [05-python-api-guide.md](05-python-api-guide.md) |
| | 6 | CSS 分页与打印特性 | @page规则、16个边距盒、分页控制、交叉引用、计数器、脚注 | [06-css-paged-media.md](06-css-paged-media.md) |
| **③ 问题层** | 7 | 高级功能详解 | PDF变体、图片缓存、字体配置、SVG、CMYK色彩 | [07-advanced-features.md](07-advanced-features.md) |
| | 8 | 源码模块导览 | 完整目录结构说明、各模块职责、源码阅读路径 | [08-source-module-guide.md](08-source-module-guide.md) |
| | 9 | 方案对比与选型 | 与Puppeteer/Playwright/wkhtmltopdf/PrinceXML多维度对比、选型决策树 | [09-comparison-selection.md](09-comparison-selection.md) |
| | 10 | 局限性与最佳实践 | 5大核心局限性、10条生产级最佳实践 | [10-limitations-best-practices.md](10-limitations-best-practices.md) |
| | 11 | 常见问题与故障排查 | 中文乱码、图片不显示、表格断页、安装失败、PDF太大等7个高频问题 | [11-faq-troubleshooting.md](11-faq-troubleshooting.md) |
| **④ 原理层** | 12 | 架构洞察与设计思考 | 自研CSS引擎的哲学、六步管线设计智慧、多遍分页本质、垂直工具链策略、开源商业模型 | [12-architecture-insights.md](12-architecture-insights.md) |
| | 13 | 相关资源链接 | 官方资源、自有工具链、CSS规范、应用场景 | [13-resources.md](13-resources.md) |

## 目标读者

本教程适合以下读者：

- **后端开发者**：需要在服务端批量生成 PDF 报告、发票、票据
- **Python 开发者**：寻找轻量级 HTML→PDF 方案，不想依赖浏览器
- **文档系统开发者**：构建文档导出、电子书生成、印刷出版系统
- **技术架构师**：评估 PDF 生成技术选型，理解渲染引擎架构设计
- **开源项目学习者**：想学习编译器式管线架构、CSS 布局引擎实现

**前置知识**：基础 Python 编程知识，了解 HTML/CSS 基本概念。

## 阅读路径建议

### 线性阅读（推荐新手）

按章节顺序从 1 到 13 完整阅读，建立从动机到原理的完整知识体系：

1. 先理解 **为什么需要 WeasyPrint**（第 1 章）
2. 了解 **整体架构**（第 2-3 章）
3. **快速上手**（第 4-6 章）——安装、API、CSS特性
4. 解决 **实际问题**（第 7-11 章）——高级功能、源码、对比、最佳实践、FAQ
5. 深入 **设计原理**（第 12-13 章）——架构洞察、资源延伸

### 按需查阅（推荐有经验者）

- 想快速生成 PDF → 直接看 [第4章安装](04-installation-cli.md) + [第5章API](05-python-api-guide.md)
- 想控制分页/页眉页脚 → [第6章CSS分页特性](06-css-paged-media.md)
- 遇到中文乱码/图片问题 → [第11章FAQ](11-faq-troubleshooting.md)
- 想评估选型 → [第1章定位](01-first-principles-positioning.md) + [第9章对比](09-comparison-selection.md) + [第10章局限性](10-limitations-best-practices.md)
- 想读源码做扩展 → [第8章源码导览](08-source-module-guide.md) + [第12章架构洞察](12-architecture-insights.md)

## 方法论溯源

本教程的内容组织遵循以下可复用方法论模式：

- [本质矛盾三步法](../../../../retrospective/patterns/methodology-patterns/research-knowledge/essential-contradiction-three-step.md)：第1章使用该方法分析PDF生成本质矛盾
- [管线穿透法](../../../../retrospective/patterns/methodology-patterns/research-knowledge/source-pipeline-penetration-method.md)：第2章和第8章使用该方法从入口到出口分析源码
- [技术wiki四层需求结构](../../../../retrospective/patterns/methodology-patterns/document-architecture/tech-wiki-four-layer-need-structure.md)：整个教程的四层组织框架

---

> **开始阅读**：[第 1 章 — 第一性原理与核心定位 →](01-first-principles-positioning.md)
