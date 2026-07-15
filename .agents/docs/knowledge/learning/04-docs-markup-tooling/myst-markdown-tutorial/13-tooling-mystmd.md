---
id: "myst-tutorial-mystmd"
title: "第13章：工具链集成 - mystmd（新一代）"
x-toml-ref: "../../../../../../.meta/toml/docs/knowledge/learning/04-docs-markup-tooling/myst-markdown-tutorial/13-tooling-mystmd.toml"
---
# 第13章：工具链集成 - mystmd（新一代）

:::{important}
**mystmd（MyST Markdown Tools）是 Executable Books 团队推出的新一代工具链**，基于 JavaScript/TypeScript 开发，速度极快、现代化开发体验、支持多格式导出与 React 组件嵌入，是新项目的**首选推荐方案**，代表 MyST 工具链的未来方向。
:::

## 13.1 mystmd 简介

mystmd 核心特性：
- **极速构建**：JS/TS 原生，比 Python 工具链快 5-10 倍
- **现代化开发体验**：单文件 CLI、热重载开发服务器、即时预览
- **多格式原生导出**：HTML/PDF/Word/LaTeX/Markdown/JATS 一键输出
- **React 组件支持**：直接嵌入交互式 React 组件
- **单一配置文件**：`myst.yml` 统一管理，无需分离 config/toc
- **出版级质量**：支持学术出版所需的交叉引用、参考文献、DOI

## 13.2 与 Jupyter Book v1 对比

| 维度 | mystmd（新一代） | Jupyter Book v1 |
|------|-----------------|-----------------|
| 技术栈 | JavaScript/TypeScript | Python |
| 构建速度 | 极快（增量毫秒级） | 较慢 |
| 配置文件 | 单一 `myst.yml` | `_config.yml` + `_toc.yml` |
| 开发体验 | `myst start` 热重载（3000端口） | 需额外安装 sphinx-autobuild |
| 多格式导出 | 原生支持 PDF/TeX/Docx/JATS | 需额外 builder |
| React 组件 | 原生支持 | 不支持 |
| 推荐场景 | **新项目首选** | 现有项目/计算叙事 |

## 13.3 环境准备与安装

- **Node.js ≥ 18**（推荐 20+ LTS）
- 包管理器：npm（自带）、pnpm 或 yarn

```bash
node --version  # 检查版本
npm install -g mystmd
myst --version  # 验证安装
```

:::{tip}
推荐使用 nvm（macOS/Linux）或 nvm-windows 管理 Node.js 版本。
:::

初始化项目：
```bash
mkdir my-myst-project && cd my-myst-project
myst init  # 交互式初始化，生成 myst.yml
```

项目结构：
```
my-myst-project/
├── myst.yml      # 核心配置
├── content/      # 文档内容
├── public/       # 静态资源
└── _build/       # 构建输出（自动生成）
```

## 13.4 myst.yml 完整配置

以下是完整可复制的生产级配置：

```yaml
project:
  id: my-myst-docs
  title: "我的技术文档"
  description: "使用 mystmd 构建的现代化文档"
  authors:
    - name: "作者姓名"
      email: "author@example.com"
  license: CC-BY-4.0
  keywords: [MyST, Markdown, Documentation]

site:
  title: "我的技术文档"
  template: book-theme
  options:
    logo: public/logo.png
    logo_text: "我的文档"
  nav:
    - title: 快速开始
      children:
        - title: 简介
          url: /content/index
        - title: 安装
          url: /content/install
    - title: 使用指南
      children:
        - title: 基本语法
          url: /content/syntax
  footer:
    copyright: "© 2024 作者姓名"

math:
  dollar: true
  double: true

abbreviations:
  MyST: Markedly Structured Text
  API: Application Programming Interface

bibliography:
  - references.bib

exports:
  - format: pdf
    output: _build/outputs/document.pdf
  - format: tex
    output: _build/outputs/document.tex
  - format: docx
    output: _build/outputs/document.docx

execute:
  execute_notebooks: auto  # auto/force/off/cache
  timeout: 120
  allow_errors: false
```

| 配置段 | 说明 |
|--------|------|
| `project` | 项目元数据：标题、作者、许可证 |
| `site` | 站点配置：主题、导航栏、页脚 |
| `math` | 数学公式解析 |
| `abbreviations` | 全局缩写词 |
| `bibliography` | BibTeX 参考文献 |
| `exports` | 多格式导出 |
| `execute` | Notebook 执行策略 |

## 13.5 目录与导航

mystmd 在 `site.nav` 中直接配置导航，无需单独 TOC 文件：

```yaml
site:
  nav:
    - title: 首页
      url: /index
    - title: 入门
      children:
        - title: 安装
          url: /install
        - title: 快速开始
          url: /quickstart
```

页面内标题（H1-H3）自动生成右侧目录导航。

:::{note}
也可使用 `_toc.yml`，mystmd 自动识别。推荐优先使用 `myst.yml` 统一配置。
:::

## 13.6 开发命令

| 命令 | 说明 |
|------|------|
| `myst init` | 交互式初始化项目 |
| `myst start` | 启动热重载开发服务器（localhost:3000） |
| `myst build` | 构建静态 HTML |
| `myst build --pdf` | 导出 PDF |
| `myst build --tex` | 导出 LaTeX |
| `myst build --docx` | 导出 Word |
| `myst deploy` | 部署到 Curvenote 等平台 |
| `myst clean` | 清理构建缓存 |

常用流程：
```bash
myst init        # 初始化
myst start       # 本地预览
myst build       # 构建生产版
myst build --pdf # 导出 PDF
```

## 13.7 Jupyter Notebook 集成

- **直接支持 .ipynb**：放入 `content/` 目录，导航链接即可
- **Markdown 中写代码**：使用 `{code-cell}` 指令：

````markdown
```{code-cell} python3
:tags: [hide-input]
import numpy as np, matplotlib.pyplot as plt
x = np.linspace(0, 2*np.pi, 100)
plt.plot(x, np.sin(x))
plt.show()
```
````

执行策略：
- `auto`：文件修改时重新执行（推荐）
- `force`：每次构建强制执行
- `off`：使用 Notebook 已保存输出
- `cache`：基于内容哈希缓存

## 13.8 主题与高级功能

### 内置主题
- `book-theme`（默认）、`article-theme`、`slide-theme`
- 切换：`site.template: article-theme`
- 支持自定义模板和 React 组件嵌入

### 高级功能
- **交叉引用**：`[](./syntax.md)` 跨文档引用，`{eq}`euler`` 引用公式
- **参考文献**：配置 `bibliography` 后用 `{cite:p}`key`` 引用
- **外部引用**：直接链接 DOI/URL，自动识别
- **草稿版本**：`project.version` 标记版本

## 13.9 排错指南

| 问题 | 解决方案 |
|------|----------|
| 端口 3000 占用 | `myst start --port 3001` |
| Node.js 版本低 | 升级到 18+，使用 nvm 管理 |
| PDF 中文乱码 | 安装中文字体 |
| 构建不更新 | `myst clean` 后重建 |
| Notebook 失败 | 增大 timeout 或设 `execute_notebooks: off` |
| 引用失效 | `myst build --check-links` 检查链接 |
| 命令未找到 | 确认 npm 全局 bin 在 PATH 中 |

## 13.10 适用场景

mystmd 是以下场景首选：
1. **新项目启动**：面向未来的现代化工具链
2. **快速构建预览**：热重载 + 极速构建
3. **多格式导出**：一键输出 HTML/PDF/Word/LaTeX
4. **现代团队工作流**：JS 生态友好
5. **出版级文档**：学术出版特性完备
6. **简洁配置偏好**：单一配置文件易上手

## 13.11 工具链选择总结

| 场景/需求 | mystmd | Jupyter Book v1 | Sphinx + myst-parser |
|-----------|--------|-----------------|---------------------|
| **新项目启动** | ✅ **首选** | ⚠️ 可选 | ❌ 不推荐 |
| **已有 Jupyter Book** | ⚠️ 可迁移 | ✅ 继续使用 | ❌ 不推荐 |
| **Python API 文档** | ⚠️ 有限支持 | ⚠️ 需扩展 | ✅ **首选** |
| **Notebook 代码执行** | ✅ 支持 | ✅ **成熟稳定** | ⚠️ 需 myst-nb |
| **极速构建/热重载** | ✅ **极快** | ❌ 较慢 | ❌ 较慢 |
| **多格式导出** | ✅ **原生支持** | ⚠️ 需配置 | ⚠️ 需配置 |
| **React 组件** | ✅ **原生支持** | ❌ 不支持 | ❌ 不支持 |
| **大型企业文档** | ⚠️ 发展中 | ✅ 可用 | ✅ **成熟稳定** |
| **配置复杂度** | ✅ 单一文件简单 | ⚠️ 双文件 | ⚠️ conf.py 复杂 |

:::{important}
**最终建议**：
- 新项目 → **直接用 mystmd**（未来方向，开发体验最佳）
- 计算叙事/Notebook 重度使用 → Jupyter Book v1
- Python 项目 API 文档 → Sphinx + myst-parser + autodoc
:::

## 13.12 小结

- mystmd 是 Executable Books 新一代 JS/TS 工具链，极速体验
- 环境：Node.js 18+，`npm install -g mystmd` 一键安装
- 配置：单一 `myst.yml` 统一管理项目、站点、导航、导出、执行
- 命令：`myst start` 热重载，`myst build --pdf/--docx/--tex` 多格式导出
- Notebook：原生支持 `.ipynb` 和 `{code-cell}` 指令
- 选择：新项目首选 mystmd，API 文档选 Sphinx，计算叙事选 Jupyter Book

## 导航
[« 上一章：Jupyter Book v1 集成](12-tooling-jupyter-book.md) | [返回目录](README.md) | [下一章：实战案例 - 技术文档写作 »](14-case-study-tech-docs.md)
