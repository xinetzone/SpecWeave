---
id: "weasyprint-01-first-principles"
title: "第一性原理与核心定位"
x-toml-ref: "../../../../../.meta/toml/docs/knowledge/learning/04-docs-markup-tooling/weasyprint-wiki/01-first-principles-positioning.toml"
source: "https://weasyprint.org/ | https://weasyprint.com/ | 源码 d:\\spaces\\SpecWeave\\external\\WeasyPrint"
category: "learning"
tags: ["weasyprint","first-principles","positioning"]
date: "2026-07-13"
status: "stable"
author: "SpecWeave"
summary: "PDF生成本质矛盾分析、现有5大方案痛点、WeasyPrint一句话定位、关键数据、核心特性矩阵、不支持的特性说明"
---

# 第一性原理与核心定位

> **官方网站**: https://weasyprint.org/
> **商业支持**: https://weasyprint.com/
> **源码版本**: v69.0（BSD 许可证）
> **GitHub**: https://github.com/Kozea/WeasyPrint
> **官方文档**: https://doc.courtbouillon.org/weasyprint

---

## 一、第一性原理：为什么需要 WeasyPrint

### 1.1 PDF 生成的本质问题

从第一性原理出发，PDF 生成的核心矛盾是：

> **你想在服务器端稳定地生成排版精美的 PDF，但浏览器太重且不稳定，手写 PDF 太低效且不可维护。**

HTML/CSS 是人类发明的最好的文档描述语言——分离内容与样式、有成熟的生态、设计师熟悉、模板引擎丰富。但 HTML 是为**屏幕连续媒体**设计的，PDF 是为**分页打印媒体**设计的。这两者之间存在根本的语义鸿沟：

| 维度 | HTML（屏幕媒体） | PDF（打印媒体） |
|------|------------------|-----------------|
| 流模型 | 无限滚动 | 固定页面、分页断点 |
| 布局单位 | 相对（px, em, rem, vw） | 绝对物理单位（cm, mm, pt） |
| 页面元素 | 无页眉页脚概念 | 页眉、页脚、页码、边距盒 |
| 交互性 | JavaScript 动态交互 | 静态文档、书签、链接 |
| 字体 | 系统安装/网络字体 | 必须嵌入文档 |

### 1.2 现有方案的痛点

回到问题本质，现有的 HTML→PDF 方案各有硬伤：

| 方案 | 痛点 |
|------|------|
| **wkhtmltopdf** | 基于过时的 QtWebKit，CSS 支持停留在 2012 年，项目已停止维护 |
| **Puppeteer/Playwright** | 需要启动完整 Chromium，内存占用大（300MB+），无头模式稳定性差，Docker 部署复杂 |
| **ReportLab** | 纯代码绘制 PDF，无法复用 HTML/CSS 生态，需要学习专用 API |
| **xhtml2pdf** | 基于 ReportLab 的 HTML 解析，CSS 支持极其有限，bug 多 |
| **PrinceXML/PDFreactor** | 昂贵的许可证费用（数千美元/年），黑盒无法调试 |

### 1.3 WeasyPrint 的本质答案

WeasyPrint 的回答是第一性原理的：

> **不依赖浏览器引擎，用 Python 重新实现一个面向打印的 CSS 布局引擎，直接输出 PDF。**

这意味着：
- **无浏览器依赖**：不需要 Chromium/WebKit/Gecko，部署简单
- **面向分页设计**：原生支持 `@page`、分页符、页眉页脚、页码、交叉引用
- **Python 原生**：可以在 Python 进程中直接调用，无 IPC 开销
- **可 Hack**：布局引擎用 Python 写成，源码可读可改
- **开源免费**：BSD 许可证，商业友好

但这个选择也带来了根本性的取舍——见后续章节的局限性与最佳实践。

---

## 二、核心定位：Web 标准打印引擎

### 2.1 一句话定义

**WeasyPrint 是一个用 Python 编写的、面向打印媒体的 HTML/CSS 视觉渲染引擎，它将 HTML/CSS 文档渲染为高质量 PDF，不依赖任何浏览器引擎。**

### 2.2 关键数据

- **15 年**持续开发（2011 年至今）
- **2500 万**月下载量（PyPI）
- **9.3k** GitHub Stars
- **Python 3.10+**（支持 CPython 和 PyPy）
- **BSD 3-Clause** 许可证

### 2.3 核心特性矩阵

| 特性类别 | 支持情况 |
|----------|----------|
| HTML 解析 | HTML5（通过 tinyhtml5） |
| CSS 选择器 | CSS2.1 + 大部分 CSS3 Selectors |
| 盒模型 | Block/Inline/Table/Flex/Grid/Inline-block |
| 分页媒体 | `@page`、分页符、页码、边距盒、交叉引用 |
| 文本排版 | 连字符（Pyphen）、字体子集化、行内对齐、复杂脚本 |
| 图形 | 内联 SVG、渐变、边框圆角、阴影、变换 |
| PDF 特性 | 书签、内部/外部链接、PDF/A、PDF/UA、PDF/X、表单、标签、附件、元数据 |
| 色彩 | sRGB、CMYK ICC 色彩配置文件 |
| 图片 | PNG/JPEG/GIF/SVG（通过 Pillow） |
| 字体 | WOFF/WOFF2/OTF/TTF（通过 fonttools） |

### 2.4 不支持的特性（重要！）

了解不支持什么比了解支持什么更重要：

- ❌ **JavaScript**——不执行任何 JS，所有数据必须在 HTML 中准备好
- ❌ **CSS Grid/Flex 高级特性**——部分支持，但不如现代浏览器完整
- ❌ **CSS 动画/过渡**——PDF 是静态媒体
- ❌ **Web Components/Shadow DOM**
- ❌ **`<canvas>` 绘制**
- ❌ **`<video>`/`<audio>`**

---

| [返回总览](00-overview.md) | 上一章：无 | [下一章：渲染管线架构](02-rendering-pipeline.md) |
|---|---|---|
