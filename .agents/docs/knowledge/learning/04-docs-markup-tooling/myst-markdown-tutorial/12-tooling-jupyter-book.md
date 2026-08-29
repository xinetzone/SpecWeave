---
id: "myst-tutorial-jupyter-book"
title: "第12章：工具链集成 - Jupyter Book v1"
x-toml-ref: "../../../../../../.meta/toml/.agents/docs/knowledge/learning/04-docs-markup-tooling/myst-markdown-tutorial/12-tooling-jupyter-book.toml"
---
# 第12章：工具链集成 - Jupyter Book v1

本章深入介绍 **Jupyter Book v1** 的完整生产配置。[第0章快速上手](00-quick-start.md) 提供了极简配置，本章覆盖环境准备、完整配置、可执行内容特色与发布流程。

:::{note}
Jupyter Book 基于 Sphinx 构建，专为**计算叙事（computational narrative）**设计，原生支持 Notebook 代码执行、交互式可视化、跨单元格变量共享。
:::

## 12.1 环境准备与安装

- **Python ≥ 3.8**（推荐 3.9+）
- 建议使用虚拟环境隔离依赖：

```bash
python -m venv .venv
.venv\Scripts\activate          # Windows
source .venv/bin/activate       # macOS/Linux
pip install -U jupyter-book
jupyter-book create mybookname  # 创建示例项目
cd mybookname
```

项目结构：
```
mybookname/
├── _config.yml       # 核心配置（见12.2）
├── _toc.yml          # 目录配置（见12.3）
├── intro.md          # 首页
├── notebooks.ipynb   # 示例Notebook
├── references.bib    # 参考文献
└── _build/           # 构建输出（自动生成）
```
:::{tip}
与 Quick Start 最小配置相比：本章提供生产级完整配置，包含所有常用项与注释。
:::

## 12.2 _config.yml 完整配置

`_config.yml` 控制书籍元数据、执行策略、解析选项、主题等。以下是完整可复制的生产配置：

```yaml
# ===== 基本信息 =====
title: "我的数据科学教材"
author: "作者姓名"
copyright: "2024"
logo: "logo.png"
bibtex_bibfiles:
  - references.bib

# ===== 代码执行配置 =====
execute:
  execute_notebooks: auto  # auto/force/off/cache
  timeout: 120            # 单元格超时（秒）
  allow_errors: false
  exclude_patterns: ['_build', '**.ipynb_checkpoints']
  cache: .jupyter_cache

# ===== MyST 解析配置 =====
parse:
  myst_enable_extensions:
    - dollarmath
    - amsmath
    - colon_fence
    - deflist
    - fieldlist
    - html_admonition
    - html_image
    - linkify
    - replacements
    - smartquotes
    - substitution
    - tasklist
  myst_dmath_double_inline: true
  myst_heading_anchors: 3

# ===== HTML 配置 =====
html:
  theme: sphinx_book_theme
  use_repository_button: true
  use_issues_button: true
  use_edit_page_button: true
  repository_url: https://github.com/your-username/your-repo
  repository_branch: main
  extra_footer: |
    <div>使用 <a href="https://jupyterbook.org">Jupyter Book</a> 构建。</div>
  extra_static_path: [_static]

# ===== LaTeX/PDF 配置 =====
latex:
  latex_engine: xelatex
  latex_documents:
    targetname: book.tex
  latex_elements:
    preamble: \usepackage{ctex}

# ===== 交互式内容 =====
launch_buttons:
  notebook_interface: "classic"
  binderhub_url: "https://mybinder.org"
  thebe: true
  colab_url: "https://colab.research.google.com"

# ===== Sphinx 扩展 =====
sphinx:
  extra_extensions: [sphinx_copybutton]
  config:
    language: zh_CN
    mathjax_path: https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js
```

| 配置项 | 说明 |
|--------|------|
| `execute_notebooks` | `auto`：修改时执行；`force`：每次重跑；`off`：不执行；`cache`：哈希缓存 |
| `myst_enable_extensions` | 与 Sphinx myst-parser 配置一致 |
| `launch_buttons` | 配置 Binder/Colab/Thebe，读者可直接在浏览器运行代码 |

## 12.3 _toc.yml 目录配置

Jupyter Book v1 使用 `jb-book` 格式，支持分层组织：

```yaml
format: jb-book
root: intro  # 根文件（首页，不带.md后缀）

parts:
  - caption: 入门篇
    chapters:
    - file: chapters/01-installation
    - file: chapters/02-quickstart
    - file: chapters/03-basic-syntax
      sections:
      - file: chapters/03-01-headings
      - file: chapters/03-02-lists
      - url: https://example.com
        title: 外部参考资料
    - glob: chapters/04-*  # glob模式批量匹配

  - caption: 进阶篇
    chapters:
    - file: chapters/05-math
    - file: notebooks/07-data-analysis  # 直接包含.ipynb

  - caption: 参考
    chapters:
    - file: reference/api
    - file: references
```

| 类型 | 用法 | 说明 |
|------|------|------|
| `file` | `- file: path/to/file` | 本地 `.md`/`.ipynb`，路径不带后缀 |
| `glob` | `- glob: pattern/*` | 通配符批量匹配 |
| `url` | `- url: https://...` | 外部链接，需配合 `title:` |

:::{note}
路径相对于 `_toc.yml` 所在目录。建议将内容放在 `content/` 或 `chapters/` 子目录。
:::

## 12.4 编写内容与构建

### 12.4.1 混合内容格式

- **叙述文字**：推荐 `.md`，版本控制友好
- **可执行代码**：使用 `.ipynb`，或在 `.md` 中用 `{code-cell}` 指令：

````markdown
```{code-cell} python3
:tags: [hide-input]
import numpy as np, matplotlib.pyplot as plt
x = np.linspace(0, 2*np.pi, 100)
plt.plot(x, np.sin(x))
plt.show()
```
````

Notebook 的 Markdown 单元格可直接使用所有 MyST 语法。

### 12.4.2 构建命令

在包含 `_config.yml` 的目录执行：

```bash
jupyter-book build .                  # HTML（_build/html）
jupyter-book build . --builder pdfhtml  # PDF（需pyppeteer）
jupyter-book build . --builder latex    # LaTeX
jupyter-book clean .                   # 清理缓存
```

| 参数 | 说明 |
|------|------|
| `-W` | 警告视为错误（CI推荐） |
| `-n` | 严格检查引用 |
| `--all` | 强制全量重建 |

## 12.5 可执行内容特色（核心优势）

### 12.5.1 单元格显示控制

使用标签控制代码/输出显示：

| 标签 | 作用 |
|------|------|
| `hide-input` | 隐藏代码，只显示输出 |
| `hide-output` | 隐藏输出，只显示代码 |
| `hide-cell` | 隐藏整个单元格 |
| `remove-input` | 完全移除输入 |
| `raises-exception` | 标记预期报错，不中断构建 |

### 12.5.2 Glue变量跨单元格共享

在一个单元格中"粘贴"变量，任意位置引用：

````markdown
```{code-cell} python3
from myst_nb import glue
import pandas as pd
df = pd.DataFrame({"a": [1,2,3], "b": [4,5,6]})
glue("df_shape", df.shape)
glue("df_table", df, display=False)
```

数据框形状：{glue:}`df_shape`

```{glue:} df_table
```
````

### 12.5.3 交互式内容

- **Thebe**：启用 `launch_buttons.thebe: true` 后，读者点击"Live Code"可在页面内直接运行修改代码
- **交互式图表**：支持 Plotly、Bokeh、Altair，输出保留交互能力
- **Binder/Colab**：配置后读者可一键在云端环境中执行整本书代码

## 12.6 发布到GitHub Pages

手动发布：
```bash
pip install ghp-import
jupyter-book build .
ghp-import -n -p -f _build/html
```

GitHub Actions 自动部署（`.github/workflows/deploy.yml`）：
```yaml
name: Deploy Jupyter Book
on: {push: {branches: [main]}}
jobs:
  build-deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with: {python-version: "3.10"}
      - run: pip install -r requirements.txt ghp-import
      - run: jupyter-book build .
      - run: ghp-import -n -p -f _build/html
        env: {GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}}
```

在仓库 Settings → Pages 设置 Source 为 `gh-pages` 分支。

## 12.7 排错指南

| 问题 | 解决方案 |
|------|----------|
| Notebook执行超时 | 增大 `execute.timeout`，或设 `execute_notebooks: off` 提交预执行的notebook |
| MyST语法不生效 | 检查 `myst_enable_extensions`；确认使用 `:::` 语法；`jupyter-book clean .` 后重建 |
| 构建不更新 | `jupyter-book clean . --all && jupyter-book build . --all` |
| 交叉引用失效 | 确认文件在 `_toc.yml` 中；用 `{doc}`path`` 引用（不带.md后缀）；加 `-n` 检查 |
| PDF中文乱码 | `latex_engine: xelatex` + `\usepackage{ctex}`，安装中文字体 |

## 12.8 适用场景

Jupyter Book 是计算叙事场景的最佳选择：

1. **课程教材/讲义**：学生直接运行代码，交互式学习
2. **数据科学报告**：代码+图表+文字一体化，可复现
3. **可复现研究论文**：配合Binder，审稿人一键验证结果
4. **带代码的技术书籍**：支持隐藏代码/输出，兼顾读者与作者
5. **教程/Workshop**：Thebe让参与者无需安装环境即可实践

:::{note}
纯API文档选 Sphinx；偏好轻量工具链选 mystmd；需要代码执行和交互时选 Jupyter Book。
:::

## 12.9 小结

- 环境：Python 3.8+，虚拟环境推荐
- 核心配置：`_config.yml` 控制执行/解析/主题；`_toc.yml` 定义章节结构
- 构建：`jupyter-book build .`，支持 HTML/PDF/LaTeX
- 独有优势：可执行单元格、glue变量、Thebe交互、Binder/Colab一键启动
- 发布：`ghp-import` 或 GitHub Actions 部署到 Pages

## 导航
[« 上一章：Sphinx 集成](11-tooling-sphinx.md) | [返回目录](README.md) | [下一章：mystmd 工具链 »](13-tooling-mystmd.md)
