---
id: "weasyprint-09-comparison"
title: "九、方案对比与选型指南"
x-toml-ref: "../../../../../../.meta/toml/docs/knowledge/learning/04-docs-markup-tooling/weasyprint-wiki/09-comparison-selection.toml"
source: "https://weasyprint.org/ | https://pandoc.org/ | https://mystmd.org/ | 经验沉淀"
category: "learning"
tags: ["weasyprint","comparison","pandoc","myst","puppeteer","playwright","wkhtmltopdf","princexml","selection"]
date: "2026-07-13"
status: "stable"
author: "SpecWeave"
summary: "WeasyPrint与Pandoc/MyST/Puppeteer/Playwright/wkhtmltopdf/PrinceXML多维度对比、分层工具链定位、选型决策树"
---

# 九、方案对比与选型指南

## 9.1 工具链分层定位

首先要明确：**这些工具不在同一层次竞争，很多时候是组合关系而非替代关系**。

```
┌─────────────────────────────────────────────────────────────────┐
│  创作层 (Authoring)                                             │
│  Markdown / MyST / reST / AsciiDoc / HTML / LaTeX              │
└────────────────────────┬────────────────────────────────────────┘
                         │
          ┌──────────────┼──────────────┐
          ▼              ▼              ▼
┌─────────────────┐ ┌──────────┐ ┌─────────────┐
│  Pandoc         │ │  MyST md │ │  手写HTML   │  ← 格式转换/标记层
│  (格式转换器)   │ │(工具链)  │ │             │
└────────┬────────┘ └────┬─────┘ └──────┬──────┘
         │               │              │
         └───────────────┼──────────────┘
                         │
          ┌──────────────┼──────────────┐
          ▼              ▼              ▼
┌─────────────────┐ ┌──────────┐ ┌─────────────┐
│  WeasyPrint     │ │LaTeX/xelatex│ │ 浏览器打印  │  ← PDF渲染引擎层
│  (HTML→PDF)     │ │(TeX→PDF) │ │(Chromium→PDF)│
└─────────────────┘ └──────────┘ └─────────────┘
         ↑               ↑              ↑
         │               │              │
    Pandoc可选用    Pandoc默认     Playwright/
    WeasyPrint作   PDF后端        Puppeteer
    为PDF后端
```

**关键认知**：
- Pandoc/MyST 是"文档格式转换器/标记语言工具链"，解决的是"怎么写、怎么转"的问题
- WeasyPrint/LaTeX/Chromium 是"PDF渲染引擎"，解决的是"怎么排版、怎么输出PDF"的问题
- Pandoc + WeasyPrint 是黄金组合：Pandoc 负责 Markdown→HTML，WeasyPrint 负责 HTML→PDF

---

## 9.2 多维度对比表

| 维度 | WeasyPrint | Pandoc | MyST (mystmd) | Puppeteer/Playwright | LaTeX (xelatex) | wkhtmltopdf |
|------|-----------|--------|---------------|---------------------|-----------------|-------------|
| **核心定位** | HTML→PDF 渲染引擎 | 通用文档格式转换器 | Markdown扩展+工具链 | 浏览器自动化→PDF | TeX排版引擎 | HTML→PDF(过时) |
| **主要输入** | HTML + CSS | 30+种格式互转 | MyST Markdown | HTML/URL | TeX | HTML |
| **PDF输出** | ✅ 原生 | ✅（依赖后端引擎） | ✅ | ✅ | ✅ | ✅ |
| **Windows安装难度** | ⭐⭐ 独立exe即用 | ⭐ 单文件exe | ⭐⭐ 需Node.js | ⭐⭐⭐ 需浏览器 | ⭐⭐⭐⭐ TeX Live~5GB | ⭐ 单文件exe |
| **安装体积** | ~20MB(独立exe) | ~50MB | ~100MB | ~300MB(Chromium) | ~1-5GB | ~30MB |
| **启动速度** | <1s | <1s | <2s | 2-5s | 慢 | <1s |
| **分页控制** | ⭐⭐⭐⭐⭐ CSS Paged Media | ⭐⭐⭐ 依赖后端 | ⭐⭐⭐ 依赖后端 | ⭐⭐ 模拟print CSS | ⭐⭐⭐⭐⭐ 最强 | ⭐⭐ 基础 |
| **CSS支持** | CSS2.1+部分CSS3+分页 | 依赖后端 | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ 完整 | 不适用 | CSS2.1(过时) |
| **JS渲染** | ❌ | ❌ | ❌ | ✅ 完整 | ❌ | ✅(过时引擎) |
| **中文支持** | ✅ 简单(字体配置) | ✅ 选WeasyPrint后端简单；选LaTeX需xeCJK配置 | ✅ 良好 | ✅ 良好 | ⚠️ 需配置 | ✅ 良好 |
| **数学公式** | ⚠️ 需MathML或转图片 | ✅ 强(LaTeX/Word公式) | ✅ 强(LaTeX原生) | ✅ (KaTeX/MathJax) | ✅ 原生最强 | ❌ |
| **引用/交叉引用** | ⚠️ 需自己实现 | ✅ 强(citeproc) | ✅ 强(学术标准) | ❌ | ✅ 最强 | ❌ |
| **模板生态** | 较少 | ⭐⭐⭐⭐⭐ 极丰富 | ⭐⭐⭐ 技术文档 | 无特定 | ⭐⭐⭐⭐⭐ 学术出版 | 少 |
| **Python API** | ✅ 原生优秀 | ⚠️ 子进程调用(pypandoc) | ⚠️ JS生态 | ⚠️ Playwright Python | ❌ | ⚠️ 子进程 |
| **Mermaid图表** | ⚠️ 需预渲染或图片 | ⭐⭐⭐ Lua Filter可处理 | ✅ 原生支持 | ✅ 原生支持 | ❌ 需外部工具 | ❌ |
| **TOC目录** | ⚠️ 需自己生成 | ✅ 自动 | ✅ 自动 | ⚠️ 需JS生成 | ✅ 自动 | ⚠️ 需JS |
| **Docker镜像** | ~150MB | ~200MB | ~300MB | ~500MB-1GB | ~2GB | ~200MB |
| **许可证** | BSD | GPLv2+ | MIT | Apache/MIT | LPPL/自由 | LGPL |
| **适合场景** | 服务端报告/票据、CSS精确排版、Python集成 | 多格式转换、文档工作流中心 | 技术文档/书籍/可执行文档 | JS动态页面、与浏览器一致 | 学术论文/出版级排版 | 遗留系统(不推荐新项目) |

---

## 9.3 选型决策树

```
你需要从文档生成PDF吗？
│
├─ 文档源是 Markdown/MyST/reST 等标记语言？
│  │
│  ├─ 需要转多种格式（PDF/HTML/DOCX/EPUB）？
│  │  └─ ✅ 选 Pandoc（核心）+ 选PDF后端：
│  │     ├─ 不想装LaTeX、想用CSS控制排版 → WeasyPrint后端 ⭐推荐
│  │     ├─ 学术论文/数学公式多/出版级 → LaTeX(xelatex)后端
│  │     └─ 文档含JS交互/需与浏览器完全一致 → wkhtmltopdf/Chrome后端
│  │
│  ├─ 是技术文档/项目文档/书籍 + 需要可执行代码块？
│  │  └─ ✅ 选 MyST md（内置导出，可配WeasyPrint后端）
│  │
│  └─ 只需要Markdown→PDF一种转换？
│     ├─ Windows上简单快速 → Pandoc + WeasyPrint独立exe
│     └─ Python项目内集成 → Python markdown库 + WeasyPrint Python API
│
├─ 文档源是 HTML / 你需要程序化生成？
│  │
│  ├─ 页面依赖JS动态渲染（SPA/图表/交互）？
│  │  └─ ✅ 选 Playwright/Puppeteer（无头浏览器打印）
│  │
│  ├─ 服务端批量生成（发票/报告/票据）、追求轻量部署？
│  │  └─ ✅ 选 WeasyPrint（Python API，Docker镜像小）
│  │
│  ├─ 需要精确分页媒体控制（页眉页脚页码、分页符、页面尺寸）？
│  │  └─ ✅ 选 WeasyPrint（原生CSS Paged Media支持最好）
│  │
│  └─ 预算充足、出版级排版需求？
│     └─ ✅ 选 PrinceXML
│
└─ 特殊场景：
   ├─ CI/CD环境 → Docker方案（Pandoc+WeasyPrint 或 纯WeasyPrint）
   ├─ 不想装任何东西 → 用Typora/VSCode插件（浏览器打印内核）
   └─ 遗留系统维护 → wkhtmltopdf（不建议新项目）
```

---

## 9.4 黄金组合详解

### ⭐ 组合一：Pandoc + WeasyPrint（最推荐的 Markdown→PDF 方案）

**为什么是黄金组合？**

| 层 | 工具 | 负责 |
|---|---|---|
| 转换层 | Pandoc | Markdown解析、TOC生成、交叉引用、引用文献、Lua Filter扩展 |
| 渲染层 | WeasyPrint | CSS Paged Media精确排版、页眉页脚页码、字体控制、PDF/A输出 |

**优势**：
- Pandoc单文件exe + WeasyPrint独立exe，Windows上两个exe即用，不需要装Python/LaTeX/GTK
- CSS知识完全复用，比学LaTeX快得多
- 中文友好，不需要xeCJK之类的配置
- Pandoc的Lua Filter生态可以扩展处理Mermaid等图表
- 比LaTeX快，比浏览器打印轻量，分页控制比两者都好

**基本命令**：
```bash
# 方式1：Pandoc直接调用WeasyPrint作为PDF引擎
pandoc input.md -o output.pdf --pdf-engine=weasyprint -c style.css

# 方式2：分两步（推荐，更灵活可控）
pandoc input.md -o temp.html --standalone --toc --css=style.css
weasyprint temp.html output.pdf
```

### ⭐ 组合二：MyST md + WeasyPrint

适合技术文档/项目文档作者：
- MyST 是专门为技术文档设计的 Markdown 扩展（支持角色/指令、交叉引用、可执行代码）
- 可以导出为多种格式
- 如果内置PDF输出不满足排版需求，可以导出HTML后用WeasyPrint精排

### ⭐ 组合三：Python 动态生成 HTML + WeasyPrint

适合程序员在应用中集成PDF生成：
```python
from jinja2 import Template
from weasyprint import HTML, CSS

# 用模板引擎渲染HTML
template = Template(open('report.html.j2').read())
html = template.render(data=my_data)

# WeasyPrint输出PDF
HTML(string=html).write_pdf('report.pdf', stylesheets=[CSS(filename='style.css')])
```

---

## 9.5 各方案Windows安装复杂度对比

| 方案 | Windows安装步骤数 | 下载体积 | 是否需要管理员 | 坑点 |
|---|---|---|---|---|
| **Pandoc + WeasyPrint exe** | 2个exe下载 + 加PATH | ~70MB | 否 | 基本无坑 |
| **WeasyPrint独立exe** | 1个exe下载 + 加PATH | ~20MB | 否 | 杀毒误报（加白名单） |
| **Playwright/Puppeteer** | npm install + 浏览器下载 | ~300MB | 否 | 浏览器下载慢 |
| **wkhtmltopdf** | 1个exe下载 + 加PATH | ~30MB | 否 | 引擎过时(CSS2.1) |
| **Pandoc + MikTeX** | 2个安装包 | ~200MB(按需安装) | 是 | 首次编译需联网下载宏包 |
| **Pandoc + TeX Live** | 1个大安装包 | ~5GB | 是 | 体积大、安装慢 |
| **WeasyPrint Python + MSYS2** | MSYS2安装 + pacman + PATH | ~500MB | 部分 | PATH/DLL路径问题 |
| **WeasyPrint Python + GTK3 Runtime** | GTK3安装包 + PATH | ~200MB | 是 | 安装器更新不及时 |

---

## 9.6 常见误区澄清

**❌ 误区1："Pandoc 是 WeasyPrint 的替代品"**
→ 实际上它们经常配合使用，Pandoc 转 HTML，WeasyPrint 出 PDF，各司其职。

**❌ 误区2："用Pandoc就一定要装LaTeX"**
→ Pandoc支持多种PDF后端，选WeasyPrint不需要LaTeX，Windows上体验更好。

**❌ 误区3："浏览器打印（Puppeteer）CSS支持最完整所以最好"**
→ 浏览器CSS是为屏幕设计的，分页媒体（@page、页眉页脚、页码、分页控制）反而支持最差；WeasyPrint专门为打印设计，这方面更强。

**❌ 误区4："WeasyPrint在Windows上安装很复杂"**
→ 那是用Python API的情况；如果只需要命令行转换，**直接下载独立exe即可**，比Pandoc+LaTeX简单一个数量级。

**❌ 误区5："wkhtmltopdf和WeasyPrint差不多"**
→ wkhtmltopdf基于2012年的QtWebKit，CSS支持停留在CSS2.1时代，已停止维护；WeasyPrint在持续更新。

---

| [返回总览](00-overview.md) | [上一章：八、源码模块导览](08-source-module-guide.md) | [下一章：十、局限性与最佳实践 →](10-limitations-best-practices.md) |
|---|---|---|
