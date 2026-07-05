---
source: "https://mystmd.org/guide/quickstart, https://mystmd.org/guide/configuration"
x-toml-ref: "../../../../.meta/toml/docs/knowledge/learning/04-docs-markup-tooling/executablebooks-myst-guide/02-project-structure.toml"
id: "executablebooks-myst-guide-project-structure"
title: "MyST 项目结构与 myst.yml 配置"
---
# MyST 项目结构与 myst.yml 配置

本文档介绍 MyST 项目的标准目录结构、`myst.yml` 配置文件详解以及常用命令，帮助你快速搭建和管理 MyST 项目。

---

## 1. 标准 MyST 项目目录结构

一个典型的 MyST 项目遵循清晰的目录结构约定，便于内容组织和工具链识别。

### 1.1 目录树示例

```
my-myst-project/
├── myst.yml              # 项目和站点配置文件（必需）
├── index.md              # 首页内容文件
├── chapter1.md           # 其他内容文件
├── chapter2.ipynb        # Jupyter Notebook 内容文件
├── images/               # 图片资源目录
│   ├── logo.png
│   └── figure1.png
├── bibliography.bib      # 参考文献文件（BibTeX 格式）
├── _build/               # 构建输出目录（自动生成，应加入 .gitignore）
│   ├── site/             # 静态网站构建产物
│   ├── exports/          # 导出的 PDF/Word 等文件
│   ├── templates/        # 下载的模板缓存
│   └── temp/             # 临时文件
└── .gitignore            # Git 忽略规则
```

### 1.2 各文件/目录作用说明

| 文件/目录 | 作用 | 必需 |
|---|---|---|
| `myst.yml` | 项目和站点的核心配置文件，定义元数据、目录结构、网站主题、导出选项等 | ✅ 是 |
| `_build/` | 构建产物输出目录，所有生成的网站和导出文件都存放在此 | 自动生成 |
| `*.md` | MyST Markdown 内容文件，使用 `.md` 扩展名 | 至少一个 |
| `*.ipynb` | Jupyter Notebook 文件，可包含可执行代码和输出 | 可选 |
| `images/` | 图片资源目录，存放文档中引用的图片文件 | 推荐 |
| `bibliography.bib` | BibTeX 格式的参考文献文件，用于管理引用 | 可选 |
| `public/` | 静态资源目录，存放 favicon、自定义 CSS/JS 等资源 | 可选 |
| `templates/` | 自定义导出/网站模板目录 | 可选 |

---

## 2. myst.yml 配置文件详解

`myst.yml` 是 MyST 项目的核心配置文件，采用 YAML 格式，分为 `project`（项目元数据）和 `site`（网站配置）两大块。

### 2.1 version 字段

配置文件的版本号，当前固定为 `1`：

```yaml
version: 1
```

### 2.2 project 块（项目元数据配置）

`project` 块定义项目的基本元数据、目录结构、参考文献等信息。

#### 2.2.1 基础元数据字段

| 字段 | 类型 | 说明 |
|---|---|---|
| `title` | string | 项目标题，显示在文档和网站中 |
| `description` | string | 项目简短描述，用于 SEO 和页面元信息 |
| `keywords` | string[] | 关键词列表，用于 SEO |
| `authors` | list[] | 作者信息列表 |
| `github` | string | GitHub 仓库 URL |
| `bibliography` | string[] | 参考文献文件路径列表 |
| `license` | string/object | 许可证信息 |
| `toc` | list[] | 目录结构定义 |
| `exports` | list[] | 导出配置列表 |

#### 2.2.2 authors（作者列表）

作者信息支持多种格式：

```yaml
project:
  authors:
    - name: "张三"
      orcid: "0000-0000-0000-0000"
      affiliations:
        - "某大学计算机系"
      email: "zhangsan@example.com"
    - "李四"  # 简单格式：只写姓名
```

#### 2.2.3 bibliography（参考文献）

指定一个或多个 BibTeX 文件：

```yaml
project:
  bibliography:
    - bibliography.bib
    - references/other-sources.bib
```

#### 2.2.4 toc（目录结构）

`toc` 定义文档的层级结构，用于生成网站导航和侧边栏：

```yaml
project:
  toc:
    - file: index.md
      title: 首页
    - title: 第一章 入门
      children:
        - file: chapter1/intro.md
          title: 简介
        - file: chapter1/install.md
          title: 安装指南
    - file: chapter2.md
      title: 第二章 语法
```

> **提示**：可以使用 `myst init --write-toc` 命令自动扫描文件生成 TOC。

#### 2.2.5 exports（导出配置）

定义需要导出的格式和输出文件：

```yaml
project:
  exports:
    - format: pdf
      template: arxiv_two_column
      output: exports/paper.pdf
    - format: docx
      output: exports/document.docx
    - format: tex
      output: exports/latex-source.zip
    - format: md
      output: exports/markdown.md
```

支持的导出格式包括：`pdf`、`docx`、`tex`、`md`、`jats`、`typst` 等。

### 2.3 site 块（网站配置）

`site` 块配置静态网站的主题、导航、外观等。

#### 2.3.1 基础网站字段

| 字段 | 类型 | 说明 |
|---|---|---|
| `template` | string | 网站主题模板，如 `book-theme` |
| `title` | string | 网站标题（可与 project.title 不同） |
| `options` | object | 模板选项（logo、favicon 等） |
| `nav` | list[] | 顶部导航栏配置 |
| `actions` | list[] | 导航栏操作按钮 |
| `domains` | string[] | 自定义域名列表 |

#### 2.3.2 template（主题模板）

MyST 提供多种官方主题模板：

```yaml
site:
  template: book-theme  # 书籍主题（默认）
  # template: article-theme  # 文章主题
  # template: slide-theme    # 幻灯片主题
```

#### 2.3.3 options（模板选项）

配置 logo、favicon 等主题选项：

```yaml
site:
  options:
    logo: images/logo.png
    logo_text: "MyST 指南"
    favicon: images/favicon.ico
    twitter: "@mystmd"
    analytics_google: "G-XXXXXXXXXX"
```

#### 2.3.4 nav（导航栏）

定义顶部导航栏链接：

```yaml
site:
  nav:
    - title: 文档
      url: /
    - title: API 参考
      url: /api
    - title: GitHub
      url: https://github.com/example/repo
      external: true
```

#### 2.3.5 actions（操作按钮）

在导航栏添加突出显示的操作按钮：

```yaml
site:
  actions:
    - title: 开始使用
      url: /getting-started
      style: primary
    - title: 下载 PDF
      url: /exports/paper.pdf
```

### 2.4 完整 myst.yml 示例（带注释）

```yaml
# MyST 配置文件版本，当前固定为 1
version: 1

# 项目元数据配置
project:
  # 项目标题
  title: "MyST 学习指南"
  
  # 项目描述（用于 SEO）
  description: "一份全面的 MyST Markdown 学习资料，涵盖语法、配置和最佳实践"
  
  # 关键词列表
  keywords:
    - MyST
    - Markdown
    - 科学写作
    - Jupyter
    - 可复现研究
  
  # 作者信息
  authors:
    - name: "文档作者"
      email: "author@example.com"
      affiliations:
        - "开源社区"
  
  # GitHub 仓库链接
  github: "https://github.com/example/myst-guide"
  
  # 参考文献文件
  bibliography:
    - bibliography.bib
  
  # 许可证
  license:
    code: MIT
    content: CC-BY-4.0
  
  # 目录结构（TOC）
  toc:
    - file: index.md
      title: 首页
    - file: 01-syntax.md
      title: 核心语法
    - file: 02-project-structure.md
      title: 项目结构
    - title: 进阶主题
      children:
        - file: advanced/citations.md
          title: 引用与参考文献
        - file: advanced/math.md
          title: 数学公式
  
  # 导出配置
  exports:
    - format: pdf
      template: arxiv_two_column
      output: _build/exports/myst-guide.pdf
    - format: docx
      output: _build/exports/myst-guide.docx

# 网站配置
site:
  # 使用书籍主题模板
  template: book-theme
  
  # 网站标题（显示在浏览器标签页）
  title: "MyST 学习指南"
  
  # 模板选项
  options:
    logo: images/logo.png
    logo_text: "MyST Guide"
    favicon: images/favicon.ico
  
  # 顶部导航栏
  nav:
    - title: 首页
      url: /
    - title: GitHub
      url: https://github.com/example/myst-guide
      external: true
  
  # 操作按钮
  actions:
    - title: 阅读指南
      url: /01-syntax
      style: primary
  
  # 站点域名配置（部署时使用）
  domains:
    - myst-guide.example.com
```

---

## 3. 常用命令

mystmd 提供了一组命令行工具，用于项目初始化、开发预览、构建导出等操作。

### 3.1 myst init（初始化项目）

在空目录中初始化 MyST 项目，自动创建 `myst.yml` 配置文件：

```shell
# 在当前目录初始化项目（创建 myst.yml）
myst init

# 或直接使用 myst 命令（等同于 myst init）
myst
```

初始化后会在当前目录生成基础的 `myst.yml` 文件。

### 3.2 myst init --write-toc（自动生成 TOC）

自动扫描当前目录下的 Markdown 和 Notebook 文件，生成目录结构并写入 `myst.yml`：

```shell
myst init --write-toc
```

这对于已有大量内容文件的项目特别有用，可以快速生成 TOC 框架。

### 3.3 myst start（启动本地开发服务器）

启动本地开发预览服务器，支持热重载，修改文件后浏览器自动刷新：

```shell
myst start

# 指定端口启动
myst start --port 3000

# 不自动打开浏览器
myst start --no-open
```

默认访问地址：`http://localhost:3000`

### 3.4 myst build（构建静态网站）

将项目构建为静态 HTML 网站，产物输出到 `_build/site/` 目录：

```shell
# 构建静态网站
myst build

# 构建时同时执行所有导出（PDF/Word 等）
myst build --all

# 构建并指定输出目录
myst build --output ./dist
```

### 3.5 myst clean（清理构建产物）

清理构建输出目录 `_build/`：

```shell
# 仅清理构建产物（_build/site/ 和 _build/exports/）
myst clean

# 清理所有缓存和模板（包括 _build/templates/）
myst clean --all
```

### 3.6 myst -v（查看版本）

查看当前安装的 mystmd 版本：

```shell
myst -v
# 或
myst --version
```

### 3.7 其他常用命令

| 命令 | 说明 |
|---|---|
| `myst --help` | 查看帮助信息 |
| `myst <command> --help` | 查看具体命令的帮助 |
| `myst check` | 检查项目配置和链接有效性 |
| `myst upgrade` | 升级 mystmd 到最新版本 |

---

## 4. 项目初始化完整流程示例

下面是从零开始创建一个 MyST 项目的完整步骤：

### 步骤 1：创建项目文件夹

```shell
# 创建并进入项目目录
mkdir my-myst-book
cd my-myst-book
```

### 步骤 2：添加内容文件

创建首页和章节内容文件：

```shell
# 创建首页
# index.md
# # 我的第一本 MyST 书籍
# 欢迎来到我的书籍！
```

```shell
# 创建第一章
# chapter1.md
# # 第一章 简介
# 这是第一章的内容。
```

### 步骤 3：运行 myst 初始化

```shell
# 初始化项目并自动生成 TOC
myst init --write-toc
```

执行后会自动生成 `myst.yml`，并包含扫描到的文件作为 TOC 条目。

### 步骤 4：配置 myst.yml

编辑生成的 `myst.yml`，完善项目元数据、作者信息、网站配置等（参考本文档第 2 节的配置示例）。

### 步骤 5：启动本地预览

```shell
# 启动开发服务器
myst start
```

打开浏览器访问 `http://localhost:3000`，查看实时预览效果。修改 Markdown 文件后页面会自动刷新。

### 步骤 6：构建导出

当内容准备好后，构建静态网站和导出文件：

```shell
# 构建静态网站
myst build

# 构建并导出 PDF/Word 等格式
myst build --all
```

构建产物位于 `_build/site/`（网站）和 `_build/exports/`（导出文件）。

---

## 5. _build 目录说明

`_build/` 是 MyST 的构建输出目录，由工具自动生成和管理，不应手动修改其中的文件。

### 5.1 子目录结构

```
_build/
├── site/         # 静态网站构建产物
├── exports/      # 导出的 PDF/Word/LaTeX 等文件
├── templates/    # 下载的网站/导出模板缓存
└── temp/         # 构建过程中的临时文件
```

### 5.2 各子目录说明

| 目录 | 说明 |
|---|---|
| `_build/site/` | 静态网站的最终产物，包含 HTML、CSS、JS 和资源文件。部署时只需上传此目录即可。 |
| `_build/exports/` | 导出的文档文件，如 PDF、Word (.docx)、LaTeX (.tex)、Markdown 等。文件名由 `myst.yml` 中 `exports` 配置决定。 |
| `_build/templates/` | 从远程下载的网站主题模板和导出模板缓存。首次使用某模板时会自动下载到此目录。 |
| `_build/temp/` | 构建过程中产生的临时文件，如执行缓存、中间转换文件等。 |

### 5.3 Git 忽略配置

由于 `_build/` 目录包含自动生成的构建产物和缓存文件，**强烈建议**将其加入 `.gitignore`：

```gitignore
# .gitignore 文件内容
_build/
node_modules/
.DS_Store
*.log
```

这样可以避免将大量生成文件提交到 Git 仓库，保持仓库整洁。

---

## 参考资料

- MyST Quickstart 快速入门：https://mystmd.org/guide/quickstart
- MyST Configuration 配置文档：https://mystmd.org/guide/configuration
- MyST 命令行参考：https://mystmd.org/guide/command-line
