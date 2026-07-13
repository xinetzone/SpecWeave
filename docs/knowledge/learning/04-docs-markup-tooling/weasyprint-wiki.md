---
title: "WeasyPrint 完整教程：从 HTML/CSS 到 PDF 的渲染引擎深度解析"
source: "https://weasyprint.org/ | https://weasyprint.com/ | 源码 d:\\spaces\\SpecWeave\\external\\WeasyPrint"
x-toml-ref: "../../../../.meta/toml/docs/knowledge/learning/04-docs-markup-tooling/weasyprint-wiki.toml"
date: "2026-07-13"
tags: ["weasyprint", "pdf", "html", "css", "rendering-engine", "python", "document-generation", "pydyf", "cairo", "pango"]
---
# WeasyPrint 完整教程：从 HTML/CSS 到 PDF 的渲染引擎深度解析

> **官方网站**: https://weasyprint.org/
> **商业支持**: https://weasyprint.com/
> **源码版本**: v69.0（BSD 许可证）
> **GitHub**: https://github.com/Kozea/WeasyPrint
> **官方文档**: https://doc.courtbouillon.org/weasyprint

---

## 📋 目录导航

- [一、第一性原理：为什么需要 WeasyPrint](#一第一性原理为什么需要-weasyprint)
- [二、核心定位：Web 标准打印引擎](#二核心定位web-标准打印引擎)
- [三、架构深度解析：六步渲染管线](#三架构深度解析六步渲染管线)
- [四、核心依赖与技术栈](#四核心依赖与技术栈)
- [五、安装与配置指南](#五安装与配置指南)
- [六、Python API 完全指南](#六python-api-完全指南)
- [七、CSS 分页与打印特性](#七css-分页与打印特性)
- [八、高级功能详解](#八高级功能详解)
- [九、源码模块导览](#九源码模块导览)
- [十、与浏览器 PDF 方案的对比](#十与浏览器-pdf-方案的对比)
- [十一、局限性与最佳实践](#十一局限性与最佳实践)
- [十二、常见问题与故障排查](#十二常见问题与故障排查)
- [十三、架构洞察与个人理解](#十三架构洞察与个人理解)
- [十四、相关资源链接](#十四相关资源链接)

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

但这个选择也带来了根本性的取舍——见[第十一节](#十一局限性与最佳实践)。

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

## 三、架构深度解析：六步渲染管线

通过源码分析（[__init__.py](../../../../external/WeasyPrint/weasyprint/__init__.py)、[document.py](../../../../external/WeasyPrint/weasyprint/document.py)），WeasyPrint 的渲染过程是一个清晰的**六步管线**：

```
Step 1: HTML 解析    →  DOM 树 (ElementTree)
Step 2: CSS 解析     →  样式表 + 匹配器 (Matcher)
Step 3: CSS 应用     →  带计算样式的 DOM（cascaded/computed）
Step 4: 盒树构建     →  "布局前"盒树（before-layout box tree）
Step 5: 布局排版     →  "布局后"盒树（after-layout box tree，多遍分页）
Step 6: 绘制输出     →  PDF 字节流
```

### 3.1 Step 1: HTML 解析

**入口**: [HTML.__init__()](../../../../external/WeasyPrint/weasyprint/__init__.py#L158-L183)

关键设计：
- **智能源检测**：`select_source()` 自动判断输入类型（文件名/URL/file object/string）
- **编码处理**：支持协议编码（HTTP Content-Type）、用户指定编码、BOM 检测
- **Base URL 解析**：`<base>` 标签优先，否则用输入源的 URL
- **UA Stylesheet**：内置 HTML5 用户代理样式表，确保默认渲染一致
- **媒体类型**：默认为 `print`，不是 `screen`——这是面向打印的核心决策

### 3.2 Step 2: CSS 解析

**入口**: [CSS.__init__()](../../../../external/WeasyPrint/weasyprint/__init__.py#L287-L319)

关键设计：
- **多源样式表**：UA → PH（呈现提示）→ User → Author
- **CSS 预处理**：处理 `@import`、`@media`、`@font-face`、`@page`、`@counter-style`
- **选择器匹配**：`cssselect2.Matcher` 构建选择器→声明的索引
- **`@font-face`**：通过 FontConfiguration 加载和管理字体

### 3.3 Step 3: CSS 应用（级联与计算）

**入口**: [StyleFor](../../../../external/WeasyPrint/weasyprint/css/__init__.py#L60-L100)

这是 CSS 规范中最复杂的部分，对应 CSS 值计算的六个阶段：

1. **收集声明**：遍历所有样式表匹配元素
2. **级联排序**：来源 → `!important` → 特异性 → `@layer` → 源码顺序
3. **指定值**：级联胜出值 / 继承值 / 初始值
4. **计算值**：相对单位转换为绝对值（无布局依赖的值）
5. **使用值**：布局阶段计算（百分比→px，依赖包含块尺寸）
6. **实际值**：根据设备限制调整

### 3.4 Step 4: 格式化结构构建（盒树）

**入口**: [build_formatting_structure()](../../../../external/WeasyPrint/weasyprint/formatting_structure/build.py#L63-L94)

将 DOM 元素树转换为 CSS 视觉格式化模型中的盒树：

- **盒类型映射**（[BOX_TYPE_FROM_DISPLAY](../../../../external/WeasyPrint/weasyprint/formatting_structure/build.py#L18-L42)）：block→BlockBox, inline→InlineBox, table→TableBox, flex→FlexBox, grid→GridBox 等
- **匿名盒创建**：表格/Flex/Grid 缺失的包装盒，Block-Inline 混排时的匿名盒
- **文本处理**：空白折叠、文本变换、引号替换
- **替换元素**：`<img>`/`<svg>`/`<embed>`/`<object>` 通过 `@handler` 装饰器注册

### 3.5 Step 5: 布局排版（多遍分页）

**入口**: [layout_document()](../../../../external/WeasyPrint/weasyprint/layout/__init__.py#L103-L216)

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
| [page.py](../../../../external/WeasyPrint/weasyprint/layout/page.py) | 页面创建、边距盒、分页决策 |
| [block.py](../../../../external/WeasyPrint/weasyprint/layout/block.py) | 块级布局、行盒、浮动 |
| [inline.py](../../../../external/WeasyPrint/weasyprint/layout/inline.py) | 行内布局、文本断行 |
| [table.py](../../../../external/WeasyPrint/weasyprint/layout/table.py) | 表格布局、边框折叠 |
| [flex.py](../../../../external/WeasyPrint/weasyprint/layout/flex.py) / [grid.py](../../../../external/WeasyPrint/weasyprint/layout/grid.py) | Flex/Grid 布局 |
| [absolute.py](../../../../external/WeasyPrint/weasyprint/layout/absolute.py) | 绝对/固定定位 |
| [float.py](../../../../external/WeasyPrint/weasyprint/layout/float.py) / [column.py](../../../../external/WeasyPrint/weasyprint/layout/column.py) | 浮动/多栏 |

### 3.6 Step 6: 绘制与 PDF 生成

**入口**: [draw_page()](../../../../external/WeasyPrint/weasyprint/draw/__init__.py#L18-L28) → [generate_pdf()](../../../../external/WeasyPrint/weasyprint/pdf/__init__.py)

按 CSS z-index 叠放顺序绘制：页面背景 → 根元素 → 负z-index → 块背景边框 → 浮动 → 行内 → z-index:auto/0 → 正z-index。最终通过 **Cairo** 渲染到 PDF 表面，**pydyf** 生成 PDF 指令流。

PDF 输出包含：字体嵌入与子集化、图片 XObject、链接注释、书签大纲、元数据、PDF/A/UA/X 变体、Tagged PDF 无障碍标签、表单字段。

---

## 四、核心依赖与技术栈

### 4.1 Python 包依赖

从 [pyproject.toml](../../../../external/WeasyPrint/pyproject.toml#L14-L23)：

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

## 五、安装与配置指南

### 5.1 系统依赖

**Linux (Ubuntu/Debian)**:
```bash
sudo apt-get install python3-pip python3-cffi libpango-1.0-0 libpangoft2-1.0-0 libharfbuzz-subset0 libjpeg-dev
```

**macOS**:
```bash
brew install python pango cairo libffi
```

**Windows**: 推荐 WSL2；原生 Windows 需安装 GTK3 Runtime。

### 5.2 Python 安装

```bash
pip install weasyprint
```

验证：
```python
from weasyprint import HTML
HTML(string="<h1>Hello WeasyPrint!</h1>").write_pdf("test.pdf")
```

### 5.3 命令行使用

```bash
# 基本用法
weasyprint input.html output.pdf

# 添加自定义 CSS
weasyprint input.html output.pdf -s style.css

# 指定媒体类型
weasyprint input.html output.pdf -m screen

# 设置 PDF 变体（PDF/A-1b, PDF/UA-1 等）
weasyprint input.html output.pdf --pdf-variant pdf/a-1b

# 编码指定
weasyprint input.html output.pdf -e utf-8

# 获取帮助
weasyprint --help
```

---

## 六、Python API 完全指南

### 6.1 核心类

WeasyPrint 的公共 API 仅暴露 5 个入口（见 [__init__.py](../../../../external/WeasyPrint/weasyprint/__init__.py#L88-L90)）：

| 类/常量 | 作用 |
|---------|------|
| `HTML` | HTML 文档入口，解析并渲染 |
| `CSS` | CSS 样式表，可传入自定义样式 |
| `Attachment` | PDF 文件附件 |
| `Document` | 渲染后的文档，提供页面访问和 PDF 输出 |
| `Page` | 单页表示，含尺寸、书签、链接、锚点 |
| `DEFAULT_OPTIONS` | 默认渲染选项字典 |

### 6.2 HTML 类——多种输入源

```python
from weasyprint import HTML

# 方式1：从文件
HTML(filename="report.html").write_pdf("report.pdf")

# 方式2：从 URL
HTML(url="https://example.com/report").write_pdf("report.pdf")

# 方式3：从字符串
html_content = "<h1>Hello</h1><p>World</p>"
HTML(string=html_content).write_pdf("output.pdf")

# 方式4：从文件对象
with open("template.html") as f:
    HTML(file_obj=f).write_pdf("output.pdf")

# 方式5：智能猜测（不推荐，显式优于隐式）
HTML("report.html").write_pdf("report.pdf")
```

### 6.3 自定义 CSS

```python
from weasyprint import HTML, CSS

# 添加外部 CSS 文件
HTML("report.html").write_pdf(
    "report.pdf",
    stylesheets=[CSS(filename="print.css")]
)

# 添加内联 CSS
HTML(string=html).write_pdf(
    "output.pdf",
    stylesheets=[CSS(string="@page { size: A4; margin: 2cm; }")]
)

# 多个样式表
HTML(string=html).write_pdf(
    "output.pdf",
    stylesheets=[
        CSS(filename="base.css"),
        CSS(string="@page { size: Letter; }")
    ]
)
```

### 6.4 渲染选项

```python
HTML(string=html).write_pdf(
    "output.pdf",
    # PDF 变体
    pdf_variant="pdf/a-1b",        # PDF/A-1b 归档格式
    pdf_tags=True,                 # Tagged PDF（无障碍）
    pdf_forms=True,                # 包含表单
    
    # 图片优化
    optimize_images=True,          # 无损优化图片
    jpeg_quality=85,               # JPEG 质量 0-95
    dpi=300,                       # 图片最大 DPI
    
    # 字体
    full_fonts=False,              # 字体子集化（默认False=子集化）
    hinting=False,                 # 不保留字体微调信息
    
    # 其他
    presentational_hints=True,     # 遵循 HTML 呈现提示（width/color 等属性）
    uncompressed_pdf=False,        # 压缩 PDF（默认压缩）
    custom_metadata=True,          # 包含自定义 HTML meta
    media_type="print",            # 媒体类型
)
```

### 6.5 分步渲染（render → 操作 → write_pdf）

```python
from weasyprint import HTML

# Step 1: 渲染但不输出 PDF（获得 Document 对象）
doc = HTML(string=html).render()

# 访问页面
print(f"总页数: {len(doc.pages)}")
for i, page in enumerate(doc.pages):
    print(f"Page {i+1}: {page.width}x{page.height}px")
    print(f"  书签数: {len(page.bookmarks)}")
    print(f"  链接数: {len(page.links)}")

# 页面操作：拆分/合并
doc.pages[0].paint  # 绘制单页
doc.copy(doc.pages[::2]).write_pdf("odd.pdf")   # 奇数页
doc.copy(doc.pages[1::2]).write_pdf("even.pdf") # 偶数页

# 获取书签树
bookmarks = doc.make_bookmark_tree()

# Step 2: 输出 PDF
doc.write_pdf("output.pdf")
```

### 6.6 自定义 URL 获取器

```python
from weasyprint import HTML

def custom_fetcher(url):
    """自定义 URL 获取器，可用于添加认证头、处理自定义协议等"""
    if url.startswith("asset://"):
        # 自定义协议处理
        path = url.replace("asset://", "./assets/")
        return {"file_obj": open(path, "rb"), "mime_type": "image/png"}
    # 返回 None 表示使用默认处理
    return None

HTML(string=html, url_fetcher=custom_fetcher).write_pdf("output.pdf")
```

### 6.7 PDF Finisher（后处理钩子）

```python
def add_watermark(document, pdf):
    """在 PDF 写入前添加水印或其他修改"""
    # pdf 是 pydyf.PDF 对象，可以添加额外内容
    pass

HTML(string=html).write_pdf("output.pdf", finisher=add_watermark)
```

---

## 七、CSS 分页与打印特性

WeasyPrint 的核心价值在于对**CSS Paged Media**规范的支持——这是浏览器方案长期薄弱的领域。

### 7.1 @page 规则

```css
@page {
    size: A4;                    /* 页面尺寸：A4, Letter, A3, 或自定义 210mm 297mm */
    margin: 2cm;                 /* 页边距 */
    marks: crop cross;           /* 裁切标记和对准标记 */
    bleed: 3mm;                  /* 出血区域 */
    
    @top-center {                /* 页眉边距盒 */
        content: "文档标题";
        font-family: "Noto Sans", sans-serif;
        font-size: 10pt;
        color: #666;
    }
    
    @bottom-center {             /* 页脚边距盒 */
        content: "第 " counter(page) " 页 / 共 " counter(pages) " 页";
        font-size: 9pt;
    }
    
    @bottom-right {
        content: string(doc-title); /* 命名字符串 */
    }
}

/* 第一页特殊样式 */
@page :first {
    margin-top: 5cm;            /* 第一页更大的上边距 */
    @top-center { content: none; } /* 第一页不显示页眉 */
}

/* 左页/右页（对开页） */
@page :left {
    margin-left: 3cm;
    margin-right: 2cm;
}
@page :right {
    margin-left: 2cm;
    margin-right: 3cm;
}
```

### 7.2 16 个边距盒（Margin Boxes）

```
┌─────────────────────────────────────────────────┐
│ top-left-corner  top-center  top-right-corner   │
│                                                 │
│ left-top      ┌───────────────┐    right-top    │
│               │               │                 │
│ left-middle   │   页面内容    │    right-middle │
│               │               │                 │
│ left-bottom   └───────────────┘    right-bottom │
│                                                 │
│ bottom-left-corner bottom-center bottom-right-corner │
└─────────────────────────────────────────────────┘
```

### 7.3 分页控制

```css
/* 分页符 */
.chapter {
    break-before: page;         /* 在元素前分页 */
    break-after: page;          /* 在元素后分页 */
    break-inside: avoid;        /* 避免在元素内部分页 */
}

/* 避免孤立行（widows/orphans） */
p {
    widows: 3;                  /* 页面顶部至少保留 3 行 */
    orphans: 3;                 /* 页面底部至少保留 3 行 */
}

/* 强制在某个元素后分页 */
.page-break {
    break-after: page;
}

/* 与下一个元素保持在一起 */
h2 {
    break-after: avoid;         /* 不在标题后立即分页 */
}
```

### 7.4 交叉引用与页码引用

```css
/* 使用 target-counter 引用其他位置的页码 */
.see-chapter-3::after {
    content: "（见第 " target-counter(attr(href), page) " 页）";
}

/* 使用 target-text 引用其他元素的文本 */
.cross-ref::after {
    content: " — " target-text(attr(href), content());
}

/* 命名字符串（用于页眉显示当前章节标题） */
h1 { string-set: doc-title content(); }
@page @top-center { content: string(doc-title); }

/* 运行元素（将内容移到页眉/页脚） */
.header { position: running(header); }
@page @top-center { content: element(header); }
```

### 7.5 计数器

```css
/* 自定义计数器 */
body { counter-reset: chapter figure; }

h1::before {
    counter-increment: chapter;
    content: "第 " counter(chapter) " 章 ";
}

figcaption::before {
    counter-increment: figure;
    content: "图 " counter(chapter) "." counter(figure) ": ";
}

/* 页码计数器 */
@page @bottom-center {
    content: counter(page) " / " counter(pages);
}
```

### 7.6 脚注

```css
.footnote {
    float: footnote;            /* 元素浮动到脚注区域 */
}

::footnote-call {
    content: counter(footnote);
    vertical-align: super;
    font-size: 0.7em;
}

::footnote-marker {
    content: counter(footnote) ". ";
}
```

---

## 八、高级功能详解

### 8.1 PDF 变体（PDF/A, PDF/UA, PDF/X）

```python
# PDF/A-1b（长期归档，要求所有字体嵌入，禁止透明、加密）
HTML(string=html).write_pdf("archive.pdf", pdf_variant="pdf/a-1b")

# PDF/A-2b（支持 JPEG2000、透明度、附件）
HTML(string=html).write_pdf("archive.pdf", pdf_variant="pdf/a-2b")

# PDF/A-3b（支持嵌入任意文件）
HTML(string=html).write_pdf("archive.pdf", pdf_variant="pdf/a-3b")

# PDF/UA-1（无障碍访问，要求 Tagged PDF、文档结构标签）
HTML(string=html).write_pdf("accessible.pdf", pdf_variant="pdf/ua-1")

# PDF/X-3（印刷出版，CMYK 色彩管理）
HTML(string=html).write_pdf("print.pdf", pdf_variant="pdf/x-3")
```

### 8.2 图片缓存

对于批量生成 PDF 时重复使用的图片，可以使用缓存避免重复加载：

```python
# 内存缓存（默认）
cache = {}
for data in documents:
    HTML(string=render_template(data)).write_pdf(
        f"output/{data['id']}.pdf",
        cache=cache  # 共享缓存
    )

# 磁盘缓存（适合大量图片的场景）
HTML(string=html).write_pdf("output.pdf", cache="/tmp/weasyprint-cache")
```

### 8.3 字体配置

```python
from weasyprint import HTML
from weasyprint.text.fonts import FontConfiguration

font_config = FontConfiguration()
html = HTML(string=html_content)
css = CSS(filename="styles.css", font_config=font_config)
html.write_pdf("output.pdf", stylesheets=[css], font_config=font_config)
```

CSS 中使用 `@font-face`：
```css
@font-face {
    font-family: "Noto Sans CJK SC";
    src: url("fonts/NotoSansSC-Regular.otf");
    font-weight: normal;
}
body { font-family: "Noto Sans CJK SC", sans-serif; }
```

### 8.4 SVG 支持

WeasyPrint 支持内联 SVG 和外部 SVG 图片：

```html
<!-- 内联 SVG -->
<svg width="200" height="100" viewBox="0 0 200 100">
    <rect x="10" y="10" width="180" height="80" fill="#3498db" rx="5"/>
    <text x="100" y="55" text-anchor="middle" fill="white" font-size="16">Hello SVG</text>
</svg>

<!-- 外部 SVG 作为图片 -->
<img src="chart.svg" alt="Chart">
```

### 8.5 CMYK 色彩

```python
HTML(string=html).write_pdf(
    "print.pdf",
    output_intent="cmyk-profile.icc"  # ICC 色彩配置文件路径
)
```

---

## 九、源码模块导览

WeasyPrint 源码（[weasyprint/](../../../../external/WeasyPrint/weasyprint/)）按功能清晰分层：

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

## 十、与浏览器 PDF 方案的对比

| 维度 | WeasyPrint | Puppeteer/Playwright | wkhtmltopdf | PrinceXML |
|------|-----------|---------------------|-------------|-----------|
| **渲染引擎** | 自研 Python CSS 引擎 | Chromium (Blink) | QtWebKit (2012) | 自研 Prince |
| **安装体积** | ~50MB (含系统库) | ~300MB (Chromium) | ~30MB | ~50MB |
| **启动速度** | <1s (Python 进程) | 2-5s (启动浏览器) | <1s | <1s |
| **内存占用** | ~50-100MB | ~200-500MB | ~50MB | ~50-100MB |
| **CSS 支持** | CSS2.1+部分CSS3+分页媒体 | 完整浏览器级 CSS | CSS2.1（过时） | 优秀（含分页） |
| **JS 支持** | ❌ | ✅ 完整 | ✅ 过时 | ❌ |
| **分页特性** | ✅ 原生优秀 | ⚠️ 模拟（print CSS） | ⚠️ 基础 | ✅ 优秀 |
| **PDF/A** | ✅ | ❌（需额外处理） | ❌ | ✅ |
| **部署复杂度** | 低（pip install） | 高（浏览器+依赖） | 中 | 低 |
| **Docker 镜像** | ~150MB | ~500MB-1GB | ~200MB | N/A |
| **许可证** | BSD | Apache/MIT | LGPL | 商业（$1000+） |
| **可调试性** | ✅ Python 源码可读 | ⚠️ DevTools | ❌ | ❌ 黑盒 |
| **适合场景** | 报告/发票/票据/文档 | 需要 JS 渲染的页面 | 遗留系统 | 出版级排版 |

### 选型建议

- **选 WeasyPrint**：服务端批量生成 PDF 报告/发票/票据，内容在服务端渲染（无需 JS），需要精确分页控制，追求部署轻量
- **选 Puppeteer**：PDF 内容依赖 JS 动态渲染（SPA 页面），需要与浏览器渲染完全一致，页面本身就是为屏幕设计的
- **选 PrinceXML**：出版级排版需求，预算充足
- **不选 wkhtmltopdf**：新项目不应考虑，已停止维护

---

## 十一、局限性与最佳实践

### 11.1 核心局限性

1. **无 JavaScript**：所有数据必须在传入 HTML 前准备好。对于需要 JS 渲染的 SPA 页面，先用 Puppeteer/Playwright 渲染出最终 HTML，再交给 WeasyPrint
2. **CSS 支持不完整**：
   - Flexbox：基本支持，但 `gap`、`flex-wrap: wrap` 等高级特性可能有问题
   - Grid：基本支持，但不如浏览器完整
   - 不支持 `position: sticky`
   - `float` 支持但复杂浮动场景可能有问题
   - CSS 变量 `var()` 支持，但 `calc()` 支持有限
3. **性能**：纯 Python 布局引擎，超长文档（1000+页）渲染较慢
4. **Windows 支持**：原生 Windows 需要 GTK 运行时，推荐 WSL2
5. **字体回退**：缺少字体时使用 Pango 的回退机制，可能导致中文字体显示异常

### 11.2 最佳实践

1. **为打印设计 CSS**：不要试图直接复用屏幕 CSS，编写专门的打印样式表
2. **使用物理单位**：打印用 `cm`/`mm`/`pt`，不用 `px` 做页面尺寸
3. **显式设置中文字体**：始终指定中文字体族，避免系统字体回退问题
   ```css
   body { font-family: "Noto Sans CJK SC", "Source Han Sans SC", "Microsoft YaHei", sans-serif; }
   ```
4. **图片预处理**：在传入 WeasyPrint 前压缩图片，控制 DPI
5. **测试分页**：使用 `break-inside: avoid` 避免表格行、代码块跨页断裂
6. **使用 `zoom=1`**：非 1 的 zoom 会导致物理单位（cm/mm）不准确
7. **缓存图片和字体**：批量生成时共享 `cache` 和 `FontConfiguration`
8. **两步渲染**：先用 `HTML.render()` 获取 Document，检查页数后再输出 PDF
9. **避免复杂嵌套表格**：表格布局是 CSS 中最复杂的部分，简单表格效果最好
10. **使用 `presentational_hints=True`**：如果你在 HTML 属性中使用了 width/color/bgcolor 等呈现属性

---

## 十二、常见问题与故障排查

### Q1: 中文显示为方块/乱码

**原因**：未找到中文字体。

**解决**：
1. 安装中文字体：`apt-get install fonts-noto-cjk`
2. 在 CSS 中显式指定中文字体：`font-family: "Noto Sans CJK SC", sans-serif;`
3. 使用 `@font-face` 嵌入字体文件

### Q2: 图片不显示

**原因**：相对路径无法解析；图片 URL 不可达；图片格式不支持。

**解决**：
1. 使用绝对路径或设置正确的 `base_url`：`HTML(filename="report.html", base_url=".")`
2. 本地文件使用 `file://` 协议或绝对路径
3. 确保 Pillow 支持该图片格式

### Q3: 表格跨页断裂

**解决**：
```css
tr { break-inside: avoid; }
thead { display: table-header-group; } /* 表头在每页重复 */
tfoot { display: table-footer-group; } /* 表脚在每页重复 */
```

### Q4: 安装失败（cffi/libpango 错误）

**原因**：缺少系统 C 库。

**解决**：
- Linux: `sudo apt-get install libpango-1.0-0 libcairo2 libffi-dev`
- macOS: `brew install pango cairo`
- Windows: 使用 WSL2

### Q5: PDF 文件太大

**解决**：
```python
HTML(string=html).write_pdf(
    "output.pdf",
    optimize_images=True,
    jpeg_quality=80,
    dpi=150,
    full_fonts=False  # 字体子集化（默认已开启）
)
```

### Q6: 页眉页脚不显示

**原因**：边距太小放不下内容，或 `@page` 规则未正确应用。

**解决**：确保 `@page` 的 margin 足够大以容纳边距盒内容。

### Q7: `counter(pages)` 显示为 0

**原因**：多遍重排尚未收敛，或 CSS 中有导致内容无限变化的循环。

**解决**：检查是否有依赖 `counter(pages)` 的内容改变了页数。这是定点迭代的固有限制。

---

## 十三、架构洞察与个人理解

### 13.1 "为什么自己写 CSS 引擎"的工程哲学

WeasyPrint 最值得学习的架构决策是：**不嵌入浏览器，自己实现 CSS 布局引擎**。

这个决策的代价是巨大的——CSS 布局引擎是浏览器中最复杂的组件之一。但收益也很明确：

1. **控制粒度**：分页媒体需要在布局过程中做浏览器不需要做的事（多遍重排、边距盒、脚注、交叉引用）。如果嵌入浏览器，这些功能需要 patch 浏览器源码。
2. **部署简单**：不依赖浏览器意味着 pip install 即可使用（除了系统 C 库）。
3. **可预测性**：没有 JS 意味着渲染结果完全由 HTML/CSS 决定，不存在时序问题。
4. **可 Hack 性**：Python 源码让开发者可以在任何阶段 hook 进管线——自定义 URL 获取器、finisher 后处理、甚至修改布局逻辑。

**与 SpecWeave 的关联性思考**：这种"垂直控制全管线"的架构思路与 SpecWeave 的原子化方法论有相通之处——当你对最终产出质量有高要求时，拥有对中间每一步的控制能力至关重要。

### 13.2 六步管线的设计智慧

WeasyPrint 的六步管线严格遵循了**关注点分离**原则：

- 解析（HTML/CSS）与布局分离——解析结果是纯数据结构，不包含布局决策
- 布局与绘制分离——"布局后"盒树是纯几何描述（位置+尺寸+样式），绘制只是将其翻译成 PDF 指令
- 每一步的输出是不可变的数据结构，而非可变对象——这使得多遍重排成为可能（可以丢弃旧结果重新布局）

这是经典的**编译器架构**（parse → analyze → transform → generate code）在文档渲染领域的映射。

### 13.3 多遍分页的本质

多遍重排的本质是解决**前向引用问题**：页码和交叉引用依赖于还未发生的布局结果。这与编译器中的**不动点分析**（fixed-point analysis）、LaTeX 的**多遍编译**（需要多次运行解决交叉引用）是同一个问题。

WeasyPrint 选择了最多 8 遍的定点迭代，而 LaTeX 选择的是写入 .aux 文件辅助多次编译。本质都是：**当依赖图中存在环时，你需要迭代直到收敛**。

### 13.4 依赖自有工具链的策略

CourtBouillon 团队没有选择使用现成的 html5lib/cssutils 等库，而是自己维护 tinyhtml5/tinycss2/cssselect2/pydyf 这一套工具链。这看似违反了"不要重复造轮子"的原则，但实际上是"造合适的轮子"：

- tinycss2 是一个底层 CSS tokenizer，而不是高级 CSS 框架——它恰好提供 WeasyPrint 需要的粒度
- cssselect2 是 CSS Selectors Level 4 的精确实现，不包含浏览器兼容逻辑
- pydyf 是一个极简 PDF 生成库，只提供 PDF 对象模型，不做布局
- 这四个库都可以被其他项目独立使用（tinycss2 是多个 Python CSS 工具的基础）

**启示**：当现有工具的抽象层级与你的需求不匹配时，可能需要自己造薄的底层库。核心是：让每个库只做一件事，且做好。

### 13.5 商业模型洞察

WeasyPrint 采用了**开源核心 + 商业服务**的模型（weasyprint.org 是开源项目站，weasyprint.com 是商业支持站）：
- 软件完全免费开源（BSD 许可证）
- 收入来自咨询套餐（€150-550/月）、定制开发、模板设计、工作流集成
- 商业支持由 CourtBouillon 公司提供，保证项目的长期可持续维护

这是一种健康的开源商业模式——不靠卖许可证、不靠双许可证陷阱，而是靠**专业服务**变现。

---

## 十四、相关资源链接

### 官方资源
- 🏠 官方网站：https://weasyprint.org/
- 💼 商业支持：https://weasyprint.com/
- 📖 官方文档：https://doc.courtbouillon.org/weasyprint/
- 🐙 GitHub：https://github.com/Kozea/WeasyPrint
- 📝 更新日志：https://github.com/Kozea/WeasyPrint/releases
- 💬 Matrix 社区：https://matrix.to/#/#CourtBouillon_WeasyPrint:gitter.im

### CourtBouillon 自有工具链
- tinyhtml5：https://github.com/CourtBouillon/tinyhtml5
- tinycss2：https://github.com/CourtBouillon/tinycss2
- cssselect2：https://github.com/CourtBouillon/cssselect2
- pydyf：https://github.com/CourtBouillon/pydyf

### CSS 分页媒体规范
- CSS Paged Media Module Level 3：https://www.w3.org/TR/css-page-3/
- CSS Generated Content for Paged Media：https://www.w3.org/TR/css-gcpm-3/
- CSS Fragmentation Module Level 3：https://www.w3.org/TR/css-break-3/

### 实际应用场景
- 发票/收据生成
- 业务报告/数据报表导出
- 电子票据/凭证
- 证书/合同自动化
- 电子书/出版排版
- 邮件 PDF 附件自动生成

---

> 📝 **学习笔记**：WeasyPrint 是"用正确的抽象解决正确的问题"的典范。它不试图成为浏览器（那是 Blink/WebKit 的战场），而是专注于"HTML/CSS→PDF 打印"这一特定领域，用自研布局引擎换取分页媒体的精确控制和部署的轻量性。对于需要在服务端批量生成高质量 PDF 的场景，它是 Python 生态中最好的开源选择。
