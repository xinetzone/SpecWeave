---
id: "weasyprint-08-source"
title: "源码模块导览"
x-toml-ref: "../../../../../../.meta/toml/docs/knowledge/learning/04-docs-markup-tooling/weasyprint-wiki/08-source-module-guide.toml"
source: "https://weasyprint.org/ | https://weasyprint.com/ | 源码 d:\\spaces\\SpecWeave\\external\\WeasyPrint"
category: "learning"
tags: ["weasyprint","source-code","modules","architecture"]
date: "2026-07-13"
status: "stable"
author: "SpecWeave"
summary: "WeasyPrint源码模块完整导览：css/、formatting_structure/、layout/、draw/、pdf/、text/、svg/各目录职责和核心文件说明，提供源码阅读路径建议"
---
# 源码模块导览

WeasyPrint 源码入口（[weasyprint/__init__.py](../../../../../../external/WeasyPrint/weasyprint/__init__.py)）及其主包目录按功能清晰分层：

```
weasyprint/
├── __init__.py          # 公共 API 入口：HTML, CSS, Document, Page, Attachment
├── __main__.py          # CLI 命令行入口
├── document.py          # Document/Page 类，渲染管线编排
├── html.py              # HTML 特殊元素处理、元数据提取、UA 样式表
├── urls.py              # URL 获取与源选择（URLFetcher, select_source）
├── images.py            # 图片加载（RasterImage/SVGImage）
├── logger.py            # 日志配置（PROGRESS_LOGGER 分步日志）
├── anchors.py           # 锚点、书签、链接收集
├── matrix.py            # 2D 变换矩阵
├── stacking.py          # CSS 叠放上下文（z-index 排序）
│
├── css/                 # CSS 解析与计算
│   ├── __init__.py      # 级联与计算值（get_all_computed_styles, StyleFor）
│   ├── computed_values.py # 计算值转换函数
│   ├── counters.py      # 计数器实现（CounterStyle）
│   ├── functions.py     # CSS 函数处理（var(), calc() 等）
│   ├── media_queries.py # @media 查询解析
│   ├── properties.py    # CSS 属性定义、初始值、继承性
│   ├── targets.py       # 交叉引用目标收集
│   ├── tokens.py        # CSS Token 类型与工具函数
│   ├── units.py         # 单位转换（px, pt, cm, em, rem 等）
│   ├── validation/      # 属性值验证
│   │   ├── __init__.py  # 预处理声明入口
│   │   ├── descriptors.py # @ 规则描述符验证
│   │   ├── expanders.py # CSS 简写属性展开
│   │   └── properties.py # 单个属性验证
│   ├── html5_ua.css     # HTML5 用户代理样式表（内置）
│   ├── html5_ua_form.css # HTML5 表单 UA 样式
│   └── html5_ph.css     # HTML5 呈现提示样式
│
├── formatting_structure/ # 格式化结构（盒树）
│   ├── boxes.py         # 所有盒类型定义（BlockBox, InlineBox, TextBox 等）
│   └── build.py         # DOM → 盒树构建（匿名盒、空白处理、替换元素）
│
├── layout/              # 布局引擎
│   ├── __init__.py      # 入口（layout_document, LayoutContext, make_all_pages）
│   ├── page.py          # 页面布局、分页、边距盒
│   ├── block.py         # 块级布局、行盒构建、断页决策
│   ├── inline.py        # 行内布局、文本断行
│   ├── table.py         # 表格布局、边框折叠、列宽计算
│   ├── flex.py          # Flexbox 布局
│   ├── grid.py          # Grid 布局
│   ├── absolute.py      # 绝对/固定定位
│   ├── float.py         # 浮动布局
│   ├── column.py        # 多栏布局
│   ├── replaced.py      # 替换元素（图片）布局
│   ├── background.py    # 背景布局
│   ├── percent.py       # 百分比解析
│   ├── min_max.py       # min/max 尺寸
│   ├── preferred.py     # 首选/最小宽度
│   └── leader.py        # 目录点线（leader）
│
├── draw/                # 绘制层
│   ├── __init__.py      # 入口（draw_page, draw_stacking_context）
│   ├── border.py        # 边框绘制（圆角、渐变边框）
│   ├── color.py         # 颜色处理（含透明度）
│   └── text.py          # 文本绘制（Pango→Cairo）
│
├── pdf/                 # PDF 生成
│   ├── __init__.py      # 入口（generate_pdf, VARIANTS）
│   ├── stream.py        # PDF 内容流包装（Stream 类）
│   ├── anchors.py       # PDF 注释、链接、书签、表单
│   ├── fonts.py         # PDF 字体嵌入与子集化
│   ├── metadata.py      # PDF 文档元数据（XMP, DocumentMetadata）
│   ├── tags.py          # Tagged PDF（无障碍结构标签）
│   ├── pdfa.py          # PDF/A 变体实现
│   ├── pdfua.py         # PDF/UA 变体实现
│   ├── pdfx.py          # PDF/X 变体实现
│   ├── debug.py         # 调试 PDF 变体
│   └── sRGB2014.icc     # 内置 sRGB ICC 配置文件
│
├── text/                # 文本处理
│   ├── constants.py     # 语言相关常量（引号等）
│   ├── ffi.py           # Pango/Cairo cffi 绑定
│   ├── fonts.py         # 字体配置与发现（FontConfiguration, Font）
│   └── line_break.py    # 换行算法
│
└── svg/                 # SVG 渲染
    ├── __init__.py      # SVG 处理入口
    ├── bounding_box.py  # SVG 边界盒计算
    ├── css.py           # SVG CSS 属性解析
    ├── defs.py          # SVG 定义（渐变、图案、剪裁路径等）
    ├── images.py        # SVG 图片处理
    ├── path.py          # SVG 路径解析与绘制
    ├── shapes.py        # SVG 基本形状（rect, circle, ellipse, line, polyline, polygon）
    ├── text.py          # SVG 文本渲染
    └── utils.py         # SVG 工具函数（坐标变换、单位解析）
```

---

### 源码阅读路径建议

1. **从入口开始**：先读 [__init__.py](../../../../../../external/WeasyPrint/weasyprint/__init__.py) 理解公共 API
2. **理解渲染流程**：读 [document.py](../../../../../../external/WeasyPrint/weasyprint/document.py) 的 `Document.render()` 方法了解六步管线
3. **CSS 级联**：读 [css/__init__.py](../../../../../../external/WeasyPrint/weasyprint/css/__init__.py) 的 `StyleFor` 类
4. **盒树构建**：读 [formatting_structure/build.py](../../../../../../external/WeasyPrint/weasyprint/formatting_structure/build.py)
5. **布局核心**：读 [layout/__init__.py](../../../../../../external/WeasyPrint/weasyprint/layout/__init__.py) 的 `layout_document()` 和 `make_all_pages()`
6. **页面布局**：深入 [layout/page.py](../../../../../../external/WeasyPrint/weasyprint/layout/page.py) 理解分页和边距盒
7. **绘制输出**：读 [draw/__init__.py](../../../../../../external/WeasyPrint/weasyprint/draw/__init__.py) 和 [pdf/__init__.py](../../../../../../external/WeasyPrint/weasyprint/pdf/__init__.py)

---

| [返回总览](00-overview.md) | [上一章：高级功能详解](07-advanced-features.md) | [下一章：方案对比与选型](09-comparison-selection.md) |
|---|---|---|
