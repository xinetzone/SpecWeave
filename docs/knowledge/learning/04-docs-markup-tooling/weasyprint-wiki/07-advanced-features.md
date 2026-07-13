---
id: "weasyprint-07-advanced"
title: "高级功能详解"
x-toml-ref: "../../../../../.meta/toml/docs/knowledge/learning/04-docs-markup-tooling/weasyprint-wiki/07-advanced-features.toml"
source: "https://weasyprint.org/ | https://weasyprint.com/ | 源码 d:\\spaces\\SpecWeave\\external\\WeasyPrint"
category: "learning"
tags: ["weasyprint","pdf-variants","caching","fonts","svg","cmyk"]
date: "2026-07-13"
status: "stable"
author: "SpecWeave"
summary: "WeasyPrint高级功能：PDF/A/UA/X变体配置、图片缓存、自定义字体配置、SVG支持、CMYK色彩管理"
---
# 高级功能详解

## 8.1 PDF 变体（PDF/A, PDF/UA, PDF/X）

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

## 8.2 图片缓存

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

## 8.3 字体配置

```python
from weasyprint import HTML, CSS
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

## 8.4 SVG 支持

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

## 8.5 CMYK 色彩

```python
HTML(string=html).write_pdf(
    "print.pdf",
    output_intent="cmyk-profile.icc"  # ICC 色彩配置文件路径
)
```

---

| [返回总览](00-overview.md) | [上一章：CSS 分页与打印特性](06-css-paged-media.md) | [下一章：源码模块导览](08-source-module-guide.md) |
|---|---|---|
