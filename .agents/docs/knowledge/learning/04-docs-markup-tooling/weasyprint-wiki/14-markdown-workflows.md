---
id: "weasyprint-14-markdown-workflows"
title: "十四、Markdown 工作流实战：Pandoc & MyST 组合指南"
x-toml-ref: "../../../../../../.meta/toml/.agents/docs/knowledge/learning/04-docs-markup-tooling/weasyprint-wiki/14-markdown-workflows.toml"
source: "实战经验沉淀 | https://pandoc.org/MANUAL.html | https://mystmd.org/guide"
category: "learning"
tags: ["weasyprint","pandoc","myst","markdown","workflow","best-practice","integration"]
date: "2026-07-13"
status: "stable"
author: "SpecWeave"
summary: "Pandoc+WeasyPrint/MyST+WeasyPrint Markdown转PDF完整工作流实战，含Windows最简安装、CSS分页模板、Mermaid处理、封面页、Python构建脚本"
---
# 十四、Markdown 工作流实战：Pandoc & MyST 组合指南

本章是实战章节，基于项目中实际使用经验，讲解如何用 Pandoc/MyST + WeasyPrint 构建高质量的 Markdown→PDF 工作流。

---

## 14.1 Windows 最简环境搭建（5分钟）

不需要装 Python、不需要 MSYS2、不需要 LaTeX、不需要 GTK 运行时。

### 步骤1：下载两个单文件 exe

| 工具 | 下载地址 | 文件大小 |
|---|---|---|
| Pandoc | https://github.com/jgm/pandoc/releases （下载 `pandoc-windows-x86_64.zip`） | ~25MB |
| WeasyPrint | https://github.com/Kozea/WeasyPrint/releases （下载 `weasyprint-windows-x86_64.exe`） | ~20MB |

### 步骤2：放到 PATH 目录

把两个 exe 放到同一个目录（例如 `C:\tools\`），然后把该目录加入系统 PATH：
- `pandoc.exe`（解压后重命名或直接用）
- `weasyprint.exe`（重命名，原文件名可能带版本号）

### 步骤3：验证

```cmd
pandoc --version
weasyprint --info
```

两个命令都能输出版本信息即成功。总共下载约 50MB，不需要任何其他依赖。

---

## 14.2 Pandoc + WeasyPrint 两种使用方式

### 方式A：一步法（Pandoc直接调用WeasyPrint引擎）

最简单，适合简单文档：

```bash
pandoc input.md -o output.pdf --pdf-engine=weasyprint -c style.css
```

参数说明：
- `--pdf-engine=weasyprint`：指定用 WeasyPrint 而非默认的 LaTeX
- `-c style.css`：指定CSS样式表（WeasyPrint用它来排版）
- `-s` / `--standalone`：生成完整HTML（推荐加上）
- `--toc`：自动生成目录
- `--toc-depth=3`：目录深度到三级标题
- `--metadata title="文档标题"`：设置文档标题

**缺点**：Pandoc 传给 WeasyPrint 时对 CSS 控制有限，复杂封面/分页场景推荐方式B。

### 方式B：两步法（推荐，更灵活可控）

```bash
# 第一步：Pandoc 把 Markdown 转为完整 HTML
pandoc input.md -o temp.html \
  --standalone \
  --toc \
  --toc-depth=3 \
  --css=style.css \
  --metadata title="我的文档" \
  --include-in-header=header.html

# 第二步：WeasyPrint 把 HTML 转为 PDF
weasyprint temp.html output.pdf
```

**优势**：
- 可以在两步之间检查/处理 HTML（例如后处理 Mermaid 图表、注入额外内容）
- CSS 完全可控
- 可以重用 HTML 输出（网页版 + PDF 版共用）

---

## 14.3 中文友好的打印 CSS 模板

保存为 `print-style.css`，可直接用于 Pandoc+WeasyPrint：

```css
@page {
  size: A4;
  margin: 2.5cm 2cm 2.5cm 2cm;
  
  @top-center {
    content: string(doc-title);
    font-family: "Noto Serif SC", "Source Han Serif SC", "SimSun", serif;
    font-size: 9pt;
    color: #666;
  }
  
  @bottom-center {
    content: counter(page) " / " counter(pages);
    font-family: "Noto Serif SC", "Source Han Serif SC", "SimSun", serif;
    font-size: 9pt;
    color: #666;
  }
}

@page :first {
  margin-top: 0;
  @top-center { content: none; }
}

* { box-sizing: border-box; }

html { font-size: 10.5pt; }

body {
  font-family: "Noto Serif SC", "Source Han Serif SC", "SimSun",
               "Microsoft YaHei", "PingFang SC", serif;
  font-size: 10.5pt;
  line-height: 1.8;
  color: #333;
}

h1 {
  font-size: 22pt;
  text-align: center;
  margin-top: 0;
  margin-bottom: 0.8em;
  padding-bottom: 0.3em;
  border-bottom: 2px solid #333;
  page-break-before: always;
  string-set: doc-title content();
}

h1:first-of-type,
.title-page + h1 {
  page-break-before: avoid;
}

h2 {
  font-size: 16pt;
  margin-top: 1.5em;
  margin-bottom: 0.6em;
  padding-left: 0.5em;
  border-left: 4px solid #333;
  page-break-after: avoid;
}

h3 {
  font-size: 13pt;
  margin-top: 1.2em;
  margin-bottom: 0.5em;
  page-break-after: avoid;
}

p {
  margin: 0.6em 0;
  text-align: justify;
  text-indent: 2em;
}

/* 封面页（Markdown里用 ::: cover 包裹） */
.cover, .title-page {
  text-align: center;
  padding-top: 6cm;
  page-break-after: always;
  min-height: 24cm;
}

.cover h1, .title-page h1 {
  font-size: 28pt;
  border: none;
  page-break-before: avoid;
  text-indent: 0;
}

/* 目录样式 */
#TOC, nav#toc {
  page-break-after: always;
}
#TOC ul, nav#toc ul {
  list-style: none;
  padding-left: 0;
}
#TOC li, nav#toc li {
  margin: 0.3em 0;
}
#TOC a, nav#toc a {
  text-decoration: none;
  color: #333;
}

/* 表格 */
table {
  width: 100%;
  border-collapse: collapse;
  margin: 1em 0;
  font-size: 9.5pt;
  page-break-inside: avoid;
}
th {
  background: #f0f0f0;
  padding: 0.5em 0.8em;
  text-align: left;
  border-bottom: 2px solid #333;
}
td {
  padding: 0.5em 0.8em;
  border-bottom: 1px solid #ddd;
}

/* 代码块 */
code {
  font-family: "Consolas", "Source Code Pro", "Courier New", monospace;
  background: #f5f5f5;
  padding: 0.15em 0.4em;
  border-radius: 3px;
  font-size: 9pt;
}
pre {
  background: #f8f8f8;
  border: 1px solid #ddd;
  border-radius: 4px;
  padding: 1em;
  margin: 1em 0;
  font-size: 8.5pt;
  line-height: 1.5;
  page-break-inside: avoid;
  white-space: pre-wrap;
  word-wrap: break-word;
}
pre code {
  background: none;
  padding: 0;
}

/* 引用 */
blockquote {
  margin: 1em 2em;
  padding: 0.8em 1.2em;
  background: #f9f9f9;
  border-left: 4px solid #ccc;
  color: #555;
  font-style: italic;
}
blockquote p { text-indent: 0; }

/* 列表 */
ul, ol { padding-left: 2em; }
li { margin: 0.3em 0; }
li p { text-indent: 0; }

/* 图片 */
img {
  max-width: 100%;
  page-break-inside: avoid;
}
figure {
  margin: 1em 0;
  text-align: center;
  page-break-inside: avoid;
}
figcaption {
  font-size: 9pt;
  color: #666;
  margin-top: 0.5em;
}

/* 分页控制 */
h1, h2, h3 { page-break-after: avoid; }
table, pre, blockquote, figure { page-break-inside: avoid; }
.page-break { page-break-after: always; }

/* 链接 */
a {
  color: #0066cc;
  text-decoration: none;
  border-bottom: 1px dotted #0066cc;
}

/* 背景色打印 */
* {
  -webkit-print-color-adjust: exact;
  print-color-adjust: exact;
}
```

---

## 14.4 处理封面页

Pandoc 默认不生成复杂封面，可以通过以下方式实现：

### 方法：Markdown 里用 div 包裹封面内容

```markdown
::: title-page

# 文档标题

## 副标题

作者：XXX  
日期：2026年7月13日

:::

# 第一章

正文内容...
```

Pandoc 支持 `fenced_divs` 扩展（默认开启），`::: title-page` 会转换为 `<div class="title-page">`，CSS 中 `.title-page` 的样式就会生效。

---

## 14.5 处理 Mermaid 图表

WeasyPrint 不执行 JavaScript，无法直接渲染 Mermaid。有三种解决方案：

### 方案1：Pandoc Lua Filter 预渲染为图片（推荐）

使用 [pandoc-mermaid-filter](https://github.com/TheMrSheep/pandoc-mermaid-filter) 或自己写一个简单的 Lua filter，在 Pandoc 转换阶段调用 mmdc（mermaid-cli）把代码块转为图片。

### 方案2：先转 HTML 再后处理（项目中已有实现）

参考项目中的 mermaid-filter.lua（位于 `playground/reports/_tools/`），在 Lua filter 中标记 Mermaid 块，然后在 HTML 阶段做处理。

### 方案3：转换时占位，PDF中标注（最简单）

如果只是需要 PDF 可读，可以把 Mermaid 代码块显示为带标签的代码块：

```css
pre.mermaid {
  background: linear-gradient(135deg, #faf6f0 0%, #f5f0e8 100%);
  border: 2px dashed #c9b896;
  position: relative;
  padding-top: 2.5em;
}
pre.mermaid::before {
  content: "📊 Mermaid 图表（请在Markdown阅读器中查看交互版本）";
  position: absolute;
  top: 0.5em;
  left: 0;
  right: 0;
  text-align: center;
  font-weight: bold;
  color: #8b7355;
}
```

---

## 14.6 Python 构建脚本（项目可复用模板）

以下是一个生产级的 Python 构建脚本，融合了项目中的实际经验：

```python
import subprocess
import re
from pathlib import Path
import sys

def build_pdf(
    md_file: str | Path,
    output_pdf: str | Path | None = None,
    css_file: str | Path | None = None,
    title: str | None = None,
    toc: bool = True,
    toc_depth: int = 3,
    cover_page: str | None = None,
    keep_html: bool = False,
):
    """
    Pandoc + WeasyPrint 两步法构建 PDF
    
    Args:
        md_file: Markdown源文件路径
        output_pdf: 输出PDF路径，默认与md同目录同名
        css_file: CSS样式文件路径，可选
        title: 文档标题，默认从Markdown第一个h1提取
        toc: 是否生成目录
        toc_depth: 目录深度
        cover_page: 封面页HTML内容，可选
        keep_html: 是否保留中间HTML文件
    """
    md_file = Path(md_file)
    if not output_pdf:
        output_pdf = md_file.with_suffix('.pdf')
    output_pdf = Path(output_pdf)
    
    base_dir = md_file.parent
    
    # 读取Markdown
    with open(md_file, 'r', encoding='utf-8') as f:
        md_content = f.read()
    
    # 移除YAML frontmatter
    md_content = re.sub(r'^---\s*\n.*?\n---\s*\n', '', md_content, flags=re.DOTALL, count=1)
    
    # 添加封面（如果有）
    if cover_page:
        md_content = cover_page + '\n\n' + md_content
    
    # 提取标题（如果未指定）
    if not title:
        title_match = re.search(r'^#\s+(.+)$', md_content, re.MULTILINE)
        title = title_match.group(1).strip() if title_match else md_file.stem
    
    # 写入临时Markdown
    temp_md = base_dir / f'_build_temp_{md_file.stem}.md'
    with open(temp_md, 'w', encoding='utf-8') as f:
        f.write(md_content)
    
    temp_html = base_dir / f'_build_temp_{md_file.stem}.html'
    
    # 构建Pandoc命令
    pandoc_cmd = [
        'pandoc',
        str(temp_md),
        '-f', 'markdown+task_lists+pipe_tables+fenced_code_blocks+fenced_divs',
        '-t', 'html5',
        '--standalone',
        '--metadata', f'title={title}',
        '-o', str(temp_html),
    ]
    
    if toc:
        pandoc_cmd.extend(['--toc', '--toc-depth', str(toc_depth)])
    
    if css_file:
        pandoc_cmd.extend(['--css', str(Path(css_file).name)])
    
    print(f'[1/2] Pandoc: {md_file.name} -> HTML ...')
    result = subprocess.run(
        pandoc_cmd,
        cwd=str(base_dir),
        capture_output=True,
        text=True,
        encoding='utf-8'
    )
    
    if result.returncode != 0:
        print(f'Pandoc 错误:\n{result.stderr}')
        temp_md.unlink(missing_ok=True)
        return False
    
    # 构建WeasyPrint命令
    weasyprint_cmd = ['weasyprint', str(temp_html), str(output_pdf)]
    
    if css_file:
        # WeasyPrint可以额外指定stylesheet（Pandoc已经嵌入了CSS，这里可选）
        pass
    
    print(f'[2/2] WeasyPrint: HTML -> {output_pdf.name} ...')
    result = subprocess.run(
        weasyprint_cmd,
        cwd=str(base_dir),
        capture_output=True,
        text=True,
        encoding='utf-8'
    )
    
    # 清理临时文件
    temp_md.unlink(missing_ok=True)
    if not keep_html:
        temp_html.unlink(missing_ok=True)
    
    if result.returncode != 0:
        print(f'WeasyPrint 错误:\n{result.stderr}')
        return False
    
    size_kb = output_pdf.stat().st_size / 1024
    print(f'✅ 成功! {output_pdf} ({size_kb:.1f} KB)')
    return True


if __name__ == '__main__':
    if len(sys.argv) > 1:
        md_file = sys.argv[1]
    else:
        print('用法: python build_pdf.py <input.md> [output.pdf] [style.css]')
        sys.exit(1)
    
    css = sys.argv[3] if len(sys.argv) > 3 else None
    out = sys.argv[2] if len(sys.argv) > 2 else None
    
    success = build_pdf(md_file, out, css)
    sys.exit(0 if success else 1)
```

---

## 14.7 MyST (mystmd) 与 WeasyPrint 配合

MyST (Markedly Structured Text) 是比普通 Markdown 更强大的技术文档标记语言，是 Executable Books / Jupyter Book 生态的核心。

### 安装 mystmd

```bash
npm install -g mystmd
```

### 基本使用

```bash
# 初始化项目
myst init

# 写文档（MyST Markdown 格式）
# 构建 HTML（默认）
myst build --html

# 构建 PDF（MyST 内置了基于 LaTeX 的 PDF 导出）
myst build --pdf
```

### MyST + WeasyPrint 组合方案

MyST 内置的 PDF 导出通常走 LaTeX 路线。如果你想用 WeasyPrint（CSS 控制更简单、Windows 上更轻量），可以：

1. 先用 `myst build --html` 输出 HTML
2. 再用 WeasyPrint 把 HTML 转为 PDF：
   ```bash
   myst build --html
   weasyprint _build/html/index.html output.pdf
   ```

注意：MyST 输出的 HTML 是多页结构，要生成单页 PDF 需要配置 MyST 为单页输出或后处理合并 HTML。

### MyST vs Pandoc 怎么选？

| 维度 | Pandoc | MyST md |
|---|---|---|
| **学习曲线** | 低，标准Markdown即可 | 中，有角色/指令概念 |
| **适用场景** | 通用文档转换、一次性导出 | 技术文档/书籍/项目文档长期维护 |
| **生态** | 30+格式，模板极多 | Jupyter/Executable Books 科研生态 |
| **可执行代码块** | ❌ | ✅ 内置支持（Jupyter内核） |
| **交叉引用** | 基础 | ✅ 强大（{numref}, {doc}, {eq}等） |
| **多项目/多文档** | 需脚本编排 | ✅ 原生支持（myst.yml配置） |
| **安装** | 单文件exe | 需要Node.js |
| **推荐场景** | 简单文档转换、脚本集成、已有Markdown管线 | 技术书籍、项目文档站点、研究文档 |

---

## 14.8 常见问题速查

### Q: Pandoc 找不到 weasyprint 引擎？
确保 `weasyprint.exe` 在系统 PATH 中，重启终端后再试。

### Q: PDF 中文字显示为方块？
在 CSS 的 `font-family` 中指定系统已安装的中文字体（如 `"Microsoft YaHei"`、`"SimSun"`）。

### Q: 封面和目录之间有空白页？
在 CSS 中给 `.title-page` 设置 `page-break-after: always`，并给第一个 `h1` 设置 `page-break-before: avoid`。

### Q: 代码块太长被截断？
在 CSS 中给 `pre` 设置 `white-space: pre-wrap; word-wrap: break-word;` 让长代码自动换行。

### Q: 表格在页脚处被截断？
给 `table` 设置 `page-break-inside: avoid;`（简单表格有效，复杂长表格无法完全避免）。

### Q: 页眉显示的是最后一个标题而不是文档标题？
使用 CSS `string-set` 配合 `string(doc-title)` 来固定页眉标题，而不是用 `content: flow()` 动态获取。

---

| [返回总览](00-overview.md) | [上一章：十三、参考资源](13-resources.md) | 下一章：无 |
|---|---|---|
