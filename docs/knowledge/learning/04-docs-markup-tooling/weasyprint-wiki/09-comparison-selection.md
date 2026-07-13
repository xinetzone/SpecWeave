---
id: "weasyprint-09-comparison"
title: "九、与浏览器 PDF 方案的对比"
x-toml-ref: "../../../../../.meta/toml/docs/knowledge/learning/04-docs-markup-tooling/weasyprint-wiki/09-comparison-selection.toml"
source: "https://weasyprint.org/ | https://weasyprint.com/ | 源码 d:\\spaces\\SpecWeave\\external\\WeasyPrint"
category: "learning"
tags: ["weasyprint","comparison","puppeteer","playwright","wkhtmltopdf","princexml","selection"]
date: "2026-07-13"
status: "stable"
author: "SpecWeave"
summary: "WeasyPrint与Puppeteer/Playwright/wkhtmltopdf/PrinceXML多维度对比（12项指标对比表）、详细选型建议"
---

# 九、与浏览器 PDF 方案的对比

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

## 选型建议

- **选 WeasyPrint**：服务端批量生成 PDF 报告/发票/票据，内容在服务端渲染（无需 JS），需要精确分页控制，追求部署轻量
- **选 Puppeteer**：PDF 内容依赖 JS 动态渲染（SPA 页面），需要与浏览器渲染完全一致，页面本身就是为屏幕设计的
- **选 PrinceXML**：出版级排版需求，预算充足
- **不选 wkhtmltopdf**：新项目不应考虑，已停止维护

---

| [返回总览](00-overview.md) | [上一章：八、源码模块导览](08-source-module-guide.md) | [下一章：十、局限性与最佳实践 →](10-limitations-best-practices.md) |
|---|---|---|
