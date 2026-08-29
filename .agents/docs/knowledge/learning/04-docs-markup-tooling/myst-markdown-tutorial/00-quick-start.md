---
id: "myst-tutorial-quick-start"
title: "第0章：快速上手（Quick Start）"
x-toml-ref: "../../../../../../.meta/toml/.agents/docs/knowledge/learning/04-docs-markup-tooling/myst-markdown-tutorial/00-quick-start.toml"
---
# 第0章：快速上手（Quick Start）

本章将带你在5分钟内快速启动MyST Markdown项目，分别介绍三种主流工具链的使用方式：mystmd（新一代官方工具链）、Jupyter Book v1（学术出版首选）、Sphinx + myst-parser（传统技术文档生态）。

---

## 0.1 前置条件

:::{note}
在开始之前，请确保你的系统已安装以下环境：
- **Node.js ≥ 18**（用于 mystmd 工具链）
- **Python ≥ 3.9**（用于 Jupyter Book 和 Sphinx）
- 包管理器：npm/pnpm/yarn（Node.js）或 pip/conda（Python）
:::

---

## 0.2 工具链一：mystmd（推荐新手）

**mystmd** 是MyST官方推出的新一代命令行工具，提供开箱即用的开发体验，支持热重载预览、多格式导出（HTML/PDF/Word/LaTeX）。

### 0.2.1 安装步骤

```bash
npm install -g mystmd
```

验证安装：
```bash
myst --version
```

### 0.2.2 初始化项目

```bash
mkdir my-first-myst && cd my-first-myst
myst init
```

`myst init` 会交互式引导你创建项目配置，或者直接手动创建配置文件。

### 0.2.3 最小配置文件

创建 `myst.yml`：

```yaml
version: 1
project:
  title: 我的第一个MyST文档
  author: 你的名字
site:
  template: book-theme
```

:::{tip}
关键配置项说明：
- `version`：配置文件版本，固定为1
- `project.title`：文档标题
- `site.template`：站点主题，可选 `book-theme`（书籍主题）或 `article-theme`（文章主题）
:::

### 0.2.4 创建第一篇文档

创建 `index.md`：

```markdown
# 欢迎使用MyST

这是我的第一篇MyST文档！

:::{note}
MyST支持丰富的提示框组件
:::
```

### 0.2.5 构建与预览

启动本地开发服务器（带热重载）：
```bash
myst start
```

:::{tip}
访问地址：http://localhost:3000

构建静态HTML站点：
```bash
myst build --html
```
构建产物输出到 `_build/html/` 目录。
:::

---

## 0.3 工具链二：Jupyter Book v1

**Jupyter Book** 是Executable Books社区推出的开源工具，专为可计算书籍、学术课程材料设计，完美支持Jupyter Notebook嵌入。

### 0.3.1 安装步骤

```bash
pip install jupyter-book
```

验证安装：
```bash
jupyter-book --version
```

### 0.3.2 初始化项目

```bash
jupyter-book create mybook
cd mybook
```

这会生成一个包含示例内容的项目模板。

### 0.3.3 最小配置文件

编辑 `_config.yml`：

```yaml
title: 我的Jupyter Book
author: 你的名字
execute:
  execute_notebooks: off  # 不执行Notebook，加快构建速度
```

编辑 `_toc.yml`（目录配置）：

```yaml
format: jb-book
root: intro
chapters:
- file: markdown  # 对应 markdown.md 文件
```

:::{tip}
关键配置项说明：
- `execute.execute_notebooks`：控制Notebook执行行为，`off` 表示不执行，`force` 表示强制执行
- `_toc.yml` 中的 `root` 是首页，`chapters` 是章节列表
:::

### 0.3.4 构建命令

```bash
jupyter-book build .
```

:::{tip}
访问地址：打开 `_build/html/index.html` 即可在浏览器中查看。

如需强制全量重建：
```bash
jupyter-book build . --all
```
:::

---

## 0.4 工具链三：Sphinx + myst-parser

**Sphinx** 是Python生态最成熟的文档系统，通过 `myst-parser` 插件可以原生支持MyST Markdown，适合已有Sphinx项目迁移或需要深度定制的技术文档场景。

### 0.4.1 安装步骤

```bash
pip install sphinx myst-parser
```

### 0.4.2 初始化项目

```bash
mkdir my-sphinx-docs && cd my-sphinx-docs
sphinx-quickstart
```

按交互式提示完成初始化（建议选择"分离源目录和构建目录"）。

### 0.4.3 最小配置文件

编辑 `source/conf.py`，添加以下内容：

```python
# -- 项目信息 -----------------------------------------------------
project = '我的Sphinx + MyST文档'
copyright = '2024, 你的名字'
author = '你的名字'
release = '0.1.0'

# -- 通用配置 -----------------------------------------------------
extensions = [
    'myst_parser',  # 启用MyST解析器
]

# 支持的文件扩展名
source_suffix = {
    '.rst': 'restructuredtext',
    '.md': 'markdown',
}

# -- HTML输出配置 -------------------------------------------------
html_theme = 'alabaster'  # 默认主题，可替换为sphinx_rtd_theme等
```

:::{tip}
关键配置项说明：
- `extensions` 列表中必须包含 `'myst_parser'`
- `source_suffix` 配置 `.md` 文件使用Markdown解析器
- 如需支持MyST的高级功能（如dollarmath数学公式），可添加 `'myst_parser'` 的额外配置
:::

编辑 `source/index.md`（将默认的 `.rst` 替换为 `.md`）：

```markdown
# 欢迎使用Sphinx + MyST

这是一个使用MyST Markdown编写的Sphinx文档。

```{toctree}
:maxdepth: 2
:caption: 目录:

```
```

### 0.4.4 构建命令

```bash
make html
```

（Windows用户使用 `make.bat html`）

:::{tip}
访问地址：打开 `build/html/index.html` 即可在浏览器中查看。

清理构建缓存：
```bash
make clean
```
:::

---

## 0.5 如何选择工具链

| 场景 | 推荐工具链 | 理由 |
|------|-----------|------|
| 新手入门、快速原型 | mystmd | 零配置、热重载、现代UI、多格式导出 |
| 学术写作、课程材料、含Jupyter Notebook | Jupyter Book | 原生Notebook支持、学术引用、可计算文档 |
| 已有Sphinx项目、Python技术文档、需要深度定制 | Sphinx + myst-parser | 生态成熟、插件丰富、高度可扩展 |

:::{note}
**新手建议**：从 mystmd 开始，它的学习曲线最平缓，体验最现代。后续根据需要再迁移到 Jupyter Book 或 Sphinx。
:::

---

## 0.6 下一步学习建议

恭喜你完成了快速上手！接下来：

1. 阅读 [下一章：MyST 简介与对比](01-introduction.md)，了解MyST的设计理念和与其他Markdown方言的区别
2. 准备好后继续阅读基础语法章节，系统学习MyST的核心语法
3. 动手修改示例文件，体验MyST的提示框、数学公式等特性

---

## 导航

[« 返回目录](README.md) | [下一章：MyST 简介与对比 »](01-introduction.md)
