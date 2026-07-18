---
id: "weasyprint-02-pipeline"
title: "架构深度解析：六步渲染管线"
x-toml-ref: "../../../../../../.meta/toml/.agents/docs/knowledge/learning/04-docs-markup-tooling/weasyprint-wiki/02-rendering-pipeline.toml"
source: "https://weasyprint.org/ | https://weasyprint.com/ | 源码 d:\\spaces\\SpecWeave\\external\\WeasyPrint"
category: "learning"
tags: ["weasyprint","architecture","pipeline","rendering"]
date: "2026-07-13"
status: "stable"
author: "SpecWeave"
summary: "WeasyPrint六步渲染管线深度解析：HTML解析→CSS解析→CSS应用→盒树构建→多遍布局→绘制输出，含各阶段源码入口和关键设计说明"
---
# 架构深度解析：六步渲染管线

通过源码分析（[__init__.py](../../../../../../external/WeasyPrint/weasyprint/__init__.py)、[document.py](../../../../../../external/WeasyPrint/weasyprint/document.py)），WeasyPrint 的渲染过程是一个清晰的**六步管线**：

```
Step 1: HTML 解析    →  DOM 树 (ElementTree)
Step 2: CSS 解析     →  样式表 + 匹配器 (Matcher)
Step 3: CSS 应用     →  带计算样式的 DOM（cascaded/computed）
Step 4: 盒树构建     →  "布局前"盒树（before-layout box tree）
Step 5: 布局排版     →  "布局后"盒树（after-layout box tree，多遍分页）
Step 6: 绘制输出     →  PDF 字节流
```

### 3.1 Step 1: HTML 解析

**入口**: [HTML.__init__()](../../../../../../external/WeasyPrint/weasyprint/__init__.py#L158-L183)

关键设计：
- **智能源检测**：`select_source()` 自动判断输入类型（文件名/URL/file object/string）
- **编码处理**：支持协议编码（HTTP Content-Type）、用户指定编码、BOM 检测
- **Base URL 解析**：`<base>` 标签优先，否则用输入源的 URL
- **UA Stylesheet**：内置 HTML5 用户代理样式表，确保默认渲染一致
- **媒体类型**：默认为 `print`，不是 `screen`——这是面向打印的核心决策

### 3.2 Step 2: CSS 解析

**入口**: [CSS.__init__()](../../../../../../external/WeasyPrint/weasyprint/__init__.py#L287-L319)

关键设计：
- **多源样式表**：UA → PH（呈现提示）→ User → Author
- **CSS 预处理**：处理 `@import`、`@media`、`@font-face`、`@page`、`@counter-style`
- **选择器匹配**：`cssselect2.Matcher` 构建选择器→声明的索引
- **`@font-face`**：通过 FontConfiguration 加载和管理字体

### 3.3 Step 3: CSS 应用（级联与计算）

**入口**: [StyleFor](../../../../../../external/WeasyPrint/weasyprint/css/__init__.py#L60-L100)

这是 CSS 规范中最复杂的部分，对应 CSS 值计算的六个阶段：

1. **收集声明**：遍历所有样式表匹配元素
2. **级联排序**：来源 → `!important` → 特异性 → `@layer` → 源码顺序
3. **指定值**：级联胜出值 / 继承值 / 初始值
4. **计算值**：相对单位转换为绝对值（无布局依赖的值）
5. **使用值**：布局阶段计算（百分比→px，依赖包含块尺寸）
6. **实际值**：根据设备限制调整

### 3.4 Step 4: 格式化结构构建（盒树）

**入口**: [build_formatting_structure()](../../../../../../external/WeasyPrint/weasyprint/formatting_structure/build.py#L63-L94)

将 DOM 元素树转换为 CSS 视觉格式化模型中的盒树：

- **盒类型映射**（[BOX_TYPE_FROM_DISPLAY](../../../../../../external/WeasyPrint/weasyprint/formatting_structure/build.py#L18-L42)）：block→BlockBox, inline→InlineBox, table→TableBox, flex→FlexBox, grid→GridBox 等
- **匿名盒创建**：表格/Flex/Grid 缺失的包装盒，Block-Inline 混排时的匿名盒
- **文本处理**：空白折叠、文本变换、引号替换
- **替换元素**：`<img>`/`<svg>`/`<embed>`/`<object>` 通过 `@handler` 装饰器注册

### 3.5 Step 5: 布局排版（多遍分页）

**入口**: [layout_document()](../../../../../../external/WeasyPrint/weasyprint/layout/__init__.py#L103-L216)

这是 WeasyPrint 最核心的部分——**分页布局**。

#### 多遍重排机制

```python
for loop in range(max_loops):  # 最多 8 遍
    pages = list(make_all_pages(context, root_box, html, pages))
    if content_changed or pages_wanted:
        continue  # 需要再排一遍
    break
```

为什么需要多遍？页码计数器 `counter(pages)` 排第一遍时不知道总页数；交叉引用 `target-counter()` 引用的目标可能在后面页面。这是**定点迭代**直到收敛。

#### 布局子模块

| 模块 | 职责 |
|------|------|
| [page.py](../../../../../../external/WeasyPrint/weasyprint/layout/page.py) | 页面创建、边距盒、分页决策 |
| [block.py](../../../../../../external/WeasyPrint/weasyprint/layout/block.py) | 块级布局、行盒、浮动 |
| [inline.py](../../../../../../external/WeasyPrint/weasyprint/layout/inline.py) | 行内布局、文本断行 |
| [table.py](../../../../../../external/WeasyPrint/weasyprint/layout/table.py) | 表格布局、边框折叠 |
| [flex.py](../../../../../../external/WeasyPrint/weasyprint/layout/flex.py) / [grid.py](../../../../../../external/WeasyPrint/weasyprint/layout/grid.py) | Flex/Grid 布局 |
| [absolute.py](../../../../../../external/WeasyPrint/weasyprint/layout/absolute.py) | 绝对/固定定位 |
| [float.py](../../../../../../external/WeasyPrint/weasyprint/layout/float.py) / [column.py](../../../../../../external/WeasyPrint/weasyprint/layout/column.py) | 浮动/多栏 |

### 3.6 Step 6: 绘制与 PDF 生成

**入口**: [draw_page()](../../../../../../external/WeasyPrint/weasyprint/draw/__init__.py#L18-L28) → [generate_pdf()](../../../../../../external/WeasyPrint/weasyprint/pdf/__init__.py)

按 CSS z-index 叠放顺序绘制：页面背景 → 根元素 → 负z-index → 块背景边框 → 浮动 → 行内 → z-index:auto/0 → 正z-index。最终通过 **Cairo** 渲染到 PDF 表面，**pydyf** 生成 PDF 指令流。

PDF 输出包含：字体嵌入与子集化、图片 XObject、链接注释、书签大纲、元数据、PDF/A/UA/X 变体、Tagged PDF 无障碍标签、表单字段。

---

| [返回总览](00-overview.md) | [上一章：第一性原理与核心定位](01-first-principles-positioning.md) | [下一章：核心依赖与技术栈](03-tech-stack-dependencies.md) |
|---|---|---|
