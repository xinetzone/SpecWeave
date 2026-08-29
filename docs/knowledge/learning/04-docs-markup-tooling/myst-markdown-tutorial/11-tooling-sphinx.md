---
id: "myst-tutorial-sphinx"
title: "第11章：工具链集成 - Sphinx + myst-parser"
x-toml-ref: "../../../../../../.meta/toml/.agents/docs/knowledge/learning/04-docs-markup-tooling/myst-markdown-tutorial/11-tooling-sphinx.toml"
---
# 第11章：工具链集成 - Sphinx + myst-parser

本章深入介绍 **Sphinx + myst-parser** 工具链的完整配置。[第0章快速上手](00-quick-start.md) 提供了极简配置，本章覆盖生产环境所需的完整配置、常用扩展与排错指南。

:::{note}
Sphinx 是 Python 生态最成熟的标准文档工具，传统仅支持 reStructuredText（reST）。通过 `myst-parser` 插件，Sphinx 可原生支持 MyST Markdown，让你在享受 Sphinx 强大生态的同时使用 Markdown 的简洁语法。
:::

## 11.1 环境准备

- **Python ≥ 3.8**（推荐 3.9+）
- 建议使用虚拟环境隔离依赖：

```bash
python -m venv .venv
# Windows 激活
.venv\Scripts\activate
# macOS/Linux 激活
source .venv/bin/activate
```

## 11.2 完整安装步骤

### 11.2.1 安装与初始化

```bash
pip install sphinx myst-parser
mkdir my-docs && cd my-docs
sphinx-quickstart
```

`sphinx-quickstart` 交互式提示中，建议选择：
- 分离源目录和构建目录：`y`
- 语言：`zh_CN`（中文文档）

初始化后目录结构：
```
my-docs/
├── Makefile / make.bat
├── build/           # 构建输出
└── source/
    ├── _static/
    ├── conf.py      # 核心配置
    └── index.rst
```

### 11.2.2 完整 conf.py 配置

编辑 `source/conf.py`：

```python
project = '我的技术文档'
copyright = '2024, 作者名'
author = '作者名'
release = '0.1.0'

extensions = [
    "myst_parser",
    # "sphinx_design",       # UI组件（需安装）
    # "sphinx_copybutton",   # 代码复制按钮（需安装）
]

source_suffix = {
    ".rst": "restructuredtext",
    ".md": "markdown",
}

myst_enable_extensions = [
    "dollarmath",      # $...$ 数学公式
    "amsmath",         # LaTeX amsmath 环境
    "deflist",         # 定义列表
    "fieldlist",       # 字段列表
    "html_admonition",
    "html_image",
    "colon_fence",     # ::: 围栏语法
    "smartquotes",
    "replacements",
    "substitution",
    "tasklist",        # 任务列表
]

html_theme = "alabaster"
html_static_path = ["_static"]
language = "zh_CN"
```

:::{tip}
与 Quick Start 最小配置相比：启用了完整 MyST 扩展集、添加常用扩展注释、包含语言配置，适合生产环境。
:::

### 11.2.3 入口文件配置

**使用 index.md（推荐）**：创建 `source/index.md` 替代默认的 `index.rst`：

```markdown
# 欢迎使用我的文档

这是 MyST Markdown 编写的 Sphinx 文档。

```{toctree}
:maxdepth: 2
:caption: 目录:

install
usage
api
```
```

**混用 reST**：保留 `index.rst` 也可以链接 `.md` 文件：
```rst
.. toctree::

   install.md
   usage.md
```

## 11.3 构建命令

```bash
# Linux/macOS
make html
# Windows
make.bat html
```

| 命令 | 说明 |
|------|------|
| `make clean` | 清理缓存 |
| `make html SPHINXOPTS="-a"` | 强制全量重建 |
| `make linkcheck` | 检查链接有效性 |

热重载预览：
```bash
pip install sphinx-autobuild
sphinx-autobuild source build/html
```
访问 http://localhost:8000

## 11.4 与 reST 混用

`.md` 和 `.rst` 文件可在同一项目中共存：

- 交叉引用：`[安装指南](install.rst)` 或 `{doc}`install``
- 在 Markdown 中使用 reST 指令：

````markdown
```{eval-rst}
.. only:: html
   仅HTML输出显示
```
````

## 11.5 启用扩展组件

| 扩展 | 功能 | 安装命令 |
|------|------|---------|
| `sphinx-design` | 卡片/标签页/网格布局 | `pip install sphinx-design` |
| `sphinx-copybutton` | 代码块复制按钮 | `pip install sphinx-copybutton` |
| `sphinxcontrib-bibtex` | BibTeX 参考文献 | `pip install sphinxcontrib-bibtex` |
| `sphinx-rtd-theme` | Read the Docs 主题 | `pip install sphinx-rtd-theme` |
| `sphinx-book-theme` | 书籍风格主题 | `pip install sphinx-book-theme` |
| `myst-nb` | Jupyter Notebook 支持 | `pip install myst-nb` |

安装后在 `conf.py` 的 `extensions` 列表中添加即可启用。

## 11.6 常见配置选项

```python
# 标题锚点深度（1-6），启用后可直接用 #标题名 跳转
myst_heading_anchors = 3

# 指定语言代码块自动编号
myst_number_code_blocks = ["python", "bash"]

# 允许 $$...$$ 作为行内公式
myst_dmath_double_inline = True

# 全局替换变量
myst_substitutions = {
    "version": "0.1.0",
}
```

使用替换变量：`当前版本：{{version}}`

## 11.7 排错指南

### "Unknown directive type" 错误
**原因**：扩展未启用。检查 `extensions` 列表，MyST 指令需在 `myst_enable_extensions` 中启用对应项。

### 交叉引用不工作（undefined label / 404）
1. 文档必须加入 `toctree` 指令
2. 使用 `{ref}` 时目标需有 `:label:`
3. 推荐用 `{doc}`install`` 而非相对路径

### 数学公式不渲染
确保 `myst_enable_extensions` 包含 `"dollarmath"` 和 `"amsmath"`。

### 中文乱码
`conf.py` 中设置 `language = "zh_CN"`；PDF 输出需配置 `latex_engine = "xelatex"` 和 ctex 包。

### 构建问题
```bash
make clean && make html          # 清理后重建
make html SPHINXOPTS="-W"        # 警告视为错误
```

## 11.8 适用场景

1. **Python 项目文档**：与 `sphinx-autodoc` 配合自动生成 API 文档
2. **已有 Sphinx 项目迁移**：逐步将 `.rst` 转为 `.md`，无缝过渡
3. **需要 reST 生态扩展**：插件丰富，支持版本管理、多语言、PDF输出
4. **企业级技术文档**：稳定可定制，适合大型项目长期维护

:::{note}
新手入门或偏好现代UI建议从 mystmd 开始；学术写作/Notebook 支持考虑 Jupyter Book。
:::

## 11.9 小结

- 环境：Python 3.8+，推荐虚拟环境
- 核心配置：`extensions` 添加 `myst_parser`，`source_suffix` 映射 `.md`，配置 `myst_enable_extensions`
- 构建：`make html`，`sphinx-autobuild` 热重载
- 混用：`.md`/`.rst` 共存，`{eval-rst}` 嵌入 reST
- 排错顺序：扩展是否启用 → 文档是否在 toctree → 路径是否正确

## 导航

[« 上一章：图片与表格](10-components-figures.md) | [返回目录](README.md) | [下一章：Jupyter Book 集成 »](12-tooling-jupyter-book.md)
