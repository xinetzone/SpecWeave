---
id: "weasyprint-03-dependencies"
title: "核心依赖与技术栈"
x-toml-ref: "../../../../../../.meta/toml/.agents/docs/knowledge/learning/04-docs-markup-tooling/weasyprint-wiki/03-tech-stack-dependencies.toml"
source: "https://weasyprint.org/ | https://weasyprint.com/ | 源码 d:\\spaces\\SpecWeave\\external\\WeasyPrint"
category: "learning"
tags: ["weasyprint","dependencies","tech-stack","cffi","cairo","pango"]
date: "2026-07-13"
status: "stable"
author: "SpecWeave"
summary: "WeasyPrint核心依赖解析：8个Python包依赖、3个系统C库、垂直工具链策略、依赖架构图"
---
# 核心依赖与技术栈

### 4.1 Python 包依赖

从 [pyproject.toml](../../../../../../external/WeasyPrint/pyproject.toml#L14-L23)：

| 包 | 作用 |
|----|------|
| **pydyf** ≥0.11.0 | 低层 PDF 生成（CourtBouillon 自有） |
| **cffi** ≥0.6 | C 外部函数接口，调用 Cairo/Pango |
| **tinyhtml5** ≥2.0.0b1 | HTML5 解析器（CourtBouillon 自有） |
| **tinycss2** ≥1.5.0 | CSS 解析器（CourtBouillon 自有） |
| **cssselect2** ≥0.8.0 | CSS3 选择器匹配（CourtBouillon 自有） |
| **Pyphen** ≥0.9.1 | 纯 Python 连字符库 |
| **Pillow** ≥9.1.0 | 图片处理 |
| **fonttools**[woff] ≥4.59.2 | 字体处理与子集化 |

**关键洞察**：tinyhtml5、tinycss2、cssselect2、pydyf 都是 CourtBouillon 自己开发维护的——他们构建了完整的 HTML/CSS→PDF 垂直工具链，而非拼凑第三方组件。这保证了管线的一致性和可调试性。

### 4.2 系统 C 库依赖

| 库 | 作用 |
|----|------|
| **Cairo** | 2D 矢量图形库，提供 PDF 表面输出、路径绘制、变换 |
| **Pango** | 文本布局引擎，复杂脚本、双向文本、字形定位、换行 |
| **HarfBuzz** | 文本整形（shaping），Pango 底层依赖 |

### 4.3 依赖架构图

```
┌──────────────────────────────────────────────────┐
│              WeasyPrint (Python)                 │
├──────────┬──────────┬──────────┬────────────────┤
│ HTML/CSS │  Layout  │   Draw   │   PDF Output   │
│ Parsing  │  Engine  │(Stacking)│(Bookmarks/     │
│+ Cascade │ (BoxTree)│          │ Links/Meta/    │
│          │          │          │ Variants)      │
├──────────┴──────────┴──────────┴────────────────┤
│ tinyhtml5 tinycss2 cssselect2 pydyf (自有)       │
│ Pillow Pyphen fonttools (社区)                   │
├─────────────────────────────────────────────────┤
│                 cffi (FFI 桥接)                  │
├─────────────────────────────────────────────────┤
│    Cairo (2D)   Pango (文本)   HarfBuzz (整形)  │
└─────────────────────────────────────────────────┘
```

---

| [返回总览](00-overview.md) | [上一章：渲染管线架构](02-rendering-pipeline.md) | [下一章：安装与配置指南](04-installation-cli.md) |
|---|---|---|
