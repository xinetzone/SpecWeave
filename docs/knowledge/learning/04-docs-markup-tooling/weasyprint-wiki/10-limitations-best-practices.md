---
id: "weasyprint-10-best-practices"
title: "十、局限性与最佳实践"
x-toml-ref: "../../../../../.meta/toml/docs/knowledge/learning/04-docs-markup-tooling/weasyprint-wiki/10-limitations-best-practices.toml"
source: "https://weasyprint.org/ | https://weasyprint.com/ | 源码 d:\\spaces\\SpecWeave\\external\\WeasyPrint"
category: "learning"
tags: ["weasyprint","limitations","best-practices","production"]
date: "2026-07-13"
status: "stable"
author: "SpecWeave"
summary: "WeasyPrint 5大核心局限性详解、10条生产级最佳实践（含CSS和Python代码示例）"
---

# 十、局限性与最佳实践

## 10.1 核心局限性

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

## 10.2 最佳实践

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

| [返回总览](00-overview.md) | [上一章：九、与浏览器 PDF 方案的对比](09-comparison-selection.md) | [下一章：十一、常见问题与故障排查 →](11-faq-troubleshooting.md) |
|---|---|---|
