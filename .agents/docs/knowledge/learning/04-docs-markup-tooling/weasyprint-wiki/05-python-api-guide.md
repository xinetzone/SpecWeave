---
id: "weasyprint-05-api"
title: "Python API 完全指南"
x-toml-ref: "../../../../../../.meta/toml/docs/knowledge/learning/04-docs-markup-tooling/weasyprint-wiki/05-python-api-guide.toml"
source: "https://weasyprint.org/ | https://weasyprint.com/ | 源码 d:\\spaces\\SpecWeave\\external\\WeasyPrint"
category: "learning"
tags: ["weasyprint","python-api","programming","code-examples"]
date: "2026-07-13"
status: "stable"
author: "SpecWeave"
summary: "WeasyPrint Python API完全指南：5个核心类、多种输入源（文件/URL/字符串/文件对象）、自定义CSS、渲染选项详解、分步渲染、自定义URL获取器、PDF finisher后处理钩子"
---
# Python API 完全指南

## 6.1 核心类

WeasyPrint 的公共 API 仅暴露 5 个入口（见 [__init__.py](../../../../../../external/WeasyPrint/weasyprint/__init__.py#L88-L90)）：

| 类/常量 | 作用 |
|---------|------|
| `HTML` | HTML 文档入口，解析并渲染 |
| `CSS` | CSS 样式表，可传入自定义样式 |
| `Attachment` | PDF 文件附件 |
| `Document` | 渲染后的文档，提供页面访问和 PDF 输出 |
| `Page` | 单页表示，含尺寸、书签、链接、锚点 |
| `DEFAULT_OPTIONS` | 默认渲染选项字典 |

## 6.2 HTML 类——多种输入源

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

## 6.3 自定义 CSS

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

## 6.4 渲染选项

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

## 6.5 分步渲染（render → 操作 → write_pdf）

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

## 6.6 自定义 URL 获取器

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

## 6.7 PDF Finisher（后处理钩子）

```python
def add_watermark(document, pdf):
    """在 PDF 写入前添加水印或其他修改"""
    # pdf 是 pydyf.PDF 对象，可以添加额外内容
    pass

HTML(string=html).write_pdf("output.pdf", finisher=add_watermark)
```

---

| [返回总览](00-overview.md) | [上一章：安装与快速开始](04-installation-cli.md) | [下一章：CSS 分页与打印特性](06-css-paged-media.md) |
|---|---|---|
