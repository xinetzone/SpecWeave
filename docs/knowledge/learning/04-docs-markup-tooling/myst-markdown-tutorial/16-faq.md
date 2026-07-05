---
id: "myst-tutorial-faq"
title: "第16章：常见问题解答（FAQ）"
---

# 第16章：常见问题解答（FAQ）

本章汇总 MyST 学习和使用中最常见问题，按类别组织，每个问题点击标题展开答案。

---

## 入门与安装

:::{dropdown} Q: MyST和CommonMark/GFM有什么区别？我应该学哪个？
- **CommonMark/GFM**：标准 Markdown，语法简单生态广，适合 README、博客、简单笔记
- **MyST**：CommonMark 超集，兼容所有标准语法，增加了指令/角色/交叉引用/数学公式/学术引用/UI组件等出版级功能

**选择**：只写简单文档 → GFM；写技术文档/论文/书籍/需要交叉引用和多格式导出 → MyST。MyST 向下兼容，学会后写普通 Markdown 无压力。
:::

:::{dropdown} Q: 三个工具链（mystmd/Jupyter Book/Sphinx）我该选哪个？
| 工具链 | 最佳场景 | 特点 |
|--------|---------|------|
| mystmd | 新项目、现代文档、多格式导出 | Node.js 生态，速度快，原生支持所有特性 |
| Jupyter Book | 可计算文档、Notebook 集成、教学 | 基于 Sphinx，内置代码执行 |
| Sphinx+MyST Parser | 已有 Sphinx 项目、Python 文档 | 最成熟，扩展生态最丰富 |

**快速决策**：新项目 → mystmd；需要执行 Notebook → Jupyter Book；已有 Sphinx 项目 → Sphinx。
:::

:::{dropdown} Q: 安装mystmd失败/Node版本不兼容怎么办？
mystmd 需要 Node.js ≥ 18：
1. 检查版本：`node --version`
2. 升级 Node（推荐 nvm）：`nvm install 20 && nvm use 20`
3. 国内镜像：`npm config set registry https://registry.npmmirror.com && npm install -g mystmd`
4. 权限问题（Linux/macOS）：`sudo npm install -g mystmd`
5. 验证：`myst --version`
:::

:::{dropdown} Q: 可以只写MyST Markdown不安装任何构建工具吗？
完全可以：
1. 用任意文本编辑器（VS Code/Typora/Obsidian）写 `.md`，MyST 语法标记可识别
2. VS Code 安装 MyST 扩展获得语法高亮和预览
3. 在线用 [mystmd.org/guide](https://mystmd.org/guide) playground 预览
4. 需要导出/建站时再安装工具链
:::

:::{dropdown} Q: 已有Markdown文档如何迁移到MyST？
迁移非常简单：
1. **零改动直接用**：90% 现有 Markdown 直接可用
2. **渐进式增强**：需要图表编号用 `{figure}`，需要交叉引用加 `:label:`
3. 在项目目录运行 `myst init` 自动配置
4. RST 迁移：`pip install rst-to-myst && rst2myst convert docs/**/*.rst`
:::

---

## 语法问题

:::{dropdown} Q: 为什么我的Directive不渲染，显示成纯文本？
按顺序排查：
1. **围栏数量**：简单指令用3个，嵌套时外层用4个
2. **拼写**：`{note}` 不是 `{notes}`，`{figure}` 不是 `{image}`
3. **换行**：指令名后必须换行，不能直接写内容
4. **选项格式**：`:label: xxx` 必须独占一行
5. **工具链支持**：Sphinx 可能需要安装对应扩展
:::

:::{dropdown} Q: :::和```围栏怎么选？什么时候用哪个？
功能等价，约定如下：
| 场景 | 推荐 |
|------|------|
| 代码块 | ```` ``` ```` |
| 包含代码块的指令 | 外层 `:::`，内层 ```` ``` ```` |
| UI组件（card/dropdown/tab） | `:::` |
| 普通提示框（note/warning） | 团队统一即可 |

**核心原则**：嵌套时围栏数量必须不同（外层4内层3）。
:::

:::{dropdown} Q: 如何在代码块中展示MyST语法本身？（围栏嵌套问题）
**增加外层围栏数量**即可：展示3个反引号的例子→外层用4个反引号，以此类推：
`````markdown
````markdown
```{note}
这是一个提示框
```
````
`````
冒号围栏同理，外层用更多冒号。
:::

:::{dropdown} Q: 中文标题的锚点链接如何正确生成？
1. **自动生成**：中文保留，空格变`-`，如 `## 入门与安装` → `#入门与安装`
2. **显式指定**（推荐，避免改标题后链接失效）：
   ```markdown
   (myst-faq)=
   ## 常见问题解答
   ```
   链接用 `[文字](#myst-faq)`，跨文档用 <code>{ref}`myst-faq`</code> 最可靠。
:::

:::{dropdown} Q: 注释%语法和HTML注释<!-- -->有什么区别？
| 特性 | `%` 注释 | `<!-- -->` 注释 |
|------|---------|----------------|
| 输出可见性 | ❌ 完全移除，不出现在任何输出 | ⚠️ HTML源码中可见 |
| 能否注释指令 | ✅ 解析前移除，可靠 | ❌ 可能被当内容 |
| 适用场景 | 作者备注、临时注释、注释大段内容 | 需要保留在HTML源码中的说明 |

```markdown
% 作者备注，不输出
<!-- HTML源码可见 -->
```
:::

---

## 交叉引用

:::{dropdown} Q: 交叉引用显示"??"或"undefined label"怎么办？
1. **检查标签定义**：目标处有 `:label: fig-xxx` 或 `(label)= ## 标题`
2. **检查拼写**：大小写/连字符/下划线完全一致
3. **跨文档引用**：确保在 `myst.yml`/`_toc.yml` 中配置了文档顺序
4. **清理重建**：
   ```bash
   myst clean && myst start  # mystmd
   jupyter-book clean . && jupyter-book build .  # Jupyter Book
   ```
5. 检查无重复标签定义
:::

:::{dropdown} Q: 如何引用其他文档中的内容？
1. 在 `myst.yml` 配置 TOC：
   ```yaml
   project:
     toc:
       - file: ch1.md
       - file: ch2.md
   ```
2. 目标文档定义标签：`(ch2-method)= ## 研究方法`
3. 源文档引用：写 <code>{ref}`ch2-method`</code> → 自动显示"研究方法"并带链接
4. 自定义文字：<code>{ref}`第二章 <ch2-method>`</code>
:::

:::{dropdown} Q: {ref}和{numref}有什么区别？什么时候用哪个？
| Role | 显示效果 | 适用场景 |
|------|---------|---------|
| `{ref}` | 标题文本（如"引言"、"模型架构"） | 引用章节、无编号元素 |
| `{numref}` | 编号（如"图 3"、"表 2"） | 引用图、表、公式等自动编号元素 |

- 引用章节 → <code>{ref}</code>
- 引用图表公式 → <code>{numref}</code>
- 不确定 → <code>{ref}</code> 更通用

自定义编号格式：<code>{numref}`图 %s <fig-model>`</code>
:::

:::{dropdown} Q: 如何自定义编号格式（如"图1-1"而非"Figure 1"）？
在 `myst.yml` 配置：
```yaml
project:
  numbering:
    figures:
      template: "图%s"
      within: sections  # 按章节编号，得到"图1-1"
    tables:
      template: "表%s"
    equations:
      template: "(%s)"
```
单处自定义用 <code>{numref}`见图 %s <fig1>`</code>。
:::

---

## 工具链问题

:::{dropdown} Q: Jupyter Book构建很慢怎么办？
1. **增量构建**：不要每次 `clean`，直接 `jupyter-book build .`
2. **禁用Notebook执行**：`_config.yml` 中设置 `execute_notebooks: off` 或 `cache`，或命令行加 `--execute-notebooks off`
3. **并行构建**：`jupyter-book build . -j 4`
4. **排除文件**：`exclude_patterns` 排除 draft 目录
5. **考虑迁移mystmd**：构建速度快5-10倍
:::

:::{dropdown} Q: mystmd构建PDF时中文乱码/字体缺失怎么办？
需要 XeLaTeX/LuaLaTeX 引擎和中文字体：
1. 安装 TeX Live/MacTeX（Windows/Mac），Linux：`sudo apt install texlive-xetex texlive-lang-chinese`
2. `myst.yml` 配置：
   ```yaml
   project:
     exports:
       - format: pdf
         pdf:
           engine: xelatex
           fonts:
             cjk: "SimSun"  # Windows宋体；macOS用"Songti SC"；Linux用"Noto Serif CJK SC"
             sans: "SimHei"
   ```
3. 加 `--verbose` 查看详细错误：`myst build --pdf --verbose`
:::

:::{dropdown} Q: 如何导入已有的Sphinx项目？
**方案一（推荐）：现有 Sphinx 项目启用 MyST**
```python
# conf.py
extensions = ["myst_parser"]
source_suffix = {".rst": "restructuredtext", ".md": "myst-parser"}
```
可同时用 `.rst` 和 `.md`，渐进式迁移。

**方案二：转 mystmd 项目**
```bash
pip install rst-to-myst && rst2myst convert docs/**/*.rst
myst init
```
:::

:::{dropdown} Q: 如何部署到GitHub Pages/Read the Docs？
**GitHub Pages（mystmd）**：
```bash
npm install -g gh-pages
myst build --html && gh-pages -d _build/html
```
或用 GitHub Actions，参考官方文档 workflow 模板。

**Read the Docs**：项目根目录创建 `.readthedocs.yaml`：
```yaml
version: 2
build:
  os: ubuntu-22.04
  tools: {python: "3.11"}
  commands:
    - pip install jupyter-book
    - jupyter-book build .
    - cp -r _build/html $READTHEDOCS_OUTPUT/html
```
:::

---

## 高级问题

:::{dropdown} Q: 如何自定义Directive/Role？
**mystmd 简单自定义**（`myst.yml`）：
```yaml
plugins:
  - type: directive
    name: my-note
    run: {type: admonition, class: note, title: "我的提示"}
```

**复杂功能**：写 JavaScript 插件（参考 mystmd 文档），Sphinx 用 Python 扩展。

**更简单的替代**：大多数场景用 Substitutions 变量、admonition 自定义 class、`{include}` 复用内容即可，无需自定义指令。
:::

:::{dropdown} Q: MyST支持导出到Confluence/Notion等平台吗？
| 平台 | 支持 | 方案 |
|------|------|------|
| Word/LaTeX/PDF/HTML/EPUB | ✅ 原生 | `myst build --docx/--tex/--pdf/--html/--epub` |
| GFM Markdown | ✅ | `myst build --md` |
| Confluence | ⚠️ | 先转 Markdown/HTML 再导入 |
| Notion | ⚠️ | 导出 Markdown 后用 Notion 导入功能 |

优先用原生格式，其他平台先转 GFM Markdown 再导入。
:::

:::{dropdown} Q: 团队协作写MyST文档有什么最佳实践？
1. **锁定版本**：`package.json`（mystmd）或 `requirements.txt`（Jupyter Book）锁定版本
2. **统一风格**：约定围栏风格、标签命名（`fig-xxx`/`sec-xxx`）、文件命名（小写+连字符）
3. **Git忽略**：`_build/`、`_static/`、`.myst/`、`*.pdf`、`*.docx`、`.ipynb_checkpoints/`
4. **CI检查**：PR 时自动跑 `myst build --html` 确保构建通过
5. **复用内容**：用 Substitutions 统一术语，`{include}` 复用公共片段
:::

---

## 反馈与更多问题

本章未覆盖的问题：
1. 查阅官方文档：[mystmd.org/guide](https://mystmd.org/guide)、[jupyterbook.org](https://jupyterbook.org)
2. GitHub Discussions：mystmd 和 Jupyter Book 仓库均有讨论区
3. 附录速查表：[附录：速查表](appendix/cheat-sheet.md)

提问时请提供：工具链版本（`myst --version`）、最小复现示例、期望vs实际效果、完整错误信息。

## 导航

[« 上一章：学术论文与书籍](15-case-study-academic.md) | [返回目录](README.md) | [下一章：附录：速查表 »](appendix/cheat-sheet.md)
