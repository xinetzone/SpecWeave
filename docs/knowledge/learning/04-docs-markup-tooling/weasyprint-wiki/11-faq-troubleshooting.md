---
id: "weasyprint-11-faq"
title: "十一、常见问题与故障排查"
x-toml-ref: "../../../../../.meta/toml/docs/knowledge/learning/04-docs-markup-tooling/weasyprint-wiki/11-faq-troubleshooting.toml"
source: "https://weasyprint.org/ | https://weasyprint.com/ | 源码 d:\\spaces\\SpecWeave\\external\\WeasyPrint"
category: "learning"
tags: ["weasyprint","faq","troubleshooting","debugging"]
date: "2026-07-13"
status: "stable"
author: "SpecWeave"
summary: "WeasyPrint常见问题解答：中文乱码、图片不显示、表格跨页断裂、安装失败、PDF文件过大、页眉页脚不显示、counter(pages)显示为0等7个高频问题的原因分析和解决方案"
---

# 十一、常见问题与故障排查

## Q1: 中文显示为方块/乱码

**原因**：未找到中文字体。

**解决**：
1. 安装中文字体：`apt-get install fonts-noto-cjk`
2. 在 CSS 中显式指定中文字体：`font-family: "Noto Sans CJK SC", sans-serif;`
3. 使用 `@font-face` 嵌入字体文件

## Q2: 图片不显示

**原因**：相对路径无法解析；图片 URL 不可达；图片格式不支持。

**解决**：
1. 使用绝对路径或设置正确的 `base_url`：`HTML(filename="report.html", base_url=".")`
2. 本地文件使用 `file://` 协议或绝对路径
3. 确保 Pillow 支持该图片格式

## Q3: 表格跨页断裂

**解决**：
```css
tr { break-inside: avoid; }
thead { display: table-header-group; } /* 表头在每页重复 */
tfoot { display: table-footer-group; } /* 表脚在每页重复 */
```

## Q4: 安装失败（cffi/libpango 错误）

**原因**：缺少系统 C 库。

**解决**：
- Linux: `sudo apt-get install libpango-1.0-0 libcairo2 libffi-dev`
- macOS: `brew install pango cairo`
- Windows: 使用 WSL2

## Q5: PDF 文件太大

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

## Q6: 页眉页脚不显示

**原因**：边距太小放不下内容，或 `@page` 规则未正确应用。

**解决**：确保 `@page` 的 margin 足够大以容纳边距盒内容。

## Q7: `counter(pages)` 显示为 0

**原因**：多遍重排尚未收敛，或 CSS 中有导致内容无限变化的循环。

**解决**：检查是否有依赖 `counter(pages)` 的内容改变了页数。这是定点迭代的固有限制。

---

| [返回总览](00-overview.md) | [上一章：十、局限性与最佳实践](10-limitations-best-practices.md) | [下一章：十二、架构洞察与个人理解 →](12-architecture-insights.md) |
|---|---|---|
