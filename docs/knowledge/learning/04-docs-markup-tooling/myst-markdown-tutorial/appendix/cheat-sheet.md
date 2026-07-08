---
id: "myst-appendix-cheat-sheet"
title: "附录A：MyST Markdown 速查表"
x-toml-ref: "../../../../../../.meta/toml/docs/knowledge/learning/04-docs-markup-tooling/myst-markdown-tutorial/appendix/cheat-sheet.toml"
---
# 附录A：MyST Markdown 速查表

本速查表按类别整理最常用的 MyST 语法，方便快速查阅。所有示例均可直接复制使用。

---

## A.1 基础语法速查

| 语法 | 效果 | 说明 |
|------|------|------|
| `# 标题1`<br>`## 标题2`<br>`### 标题3`<br>`#### 标题4`<br>`##### 标题5`<br>`###### 标题6` | **标题1**<br>标题2<br>标题3 | 6级标题，对应 HTML h1-h6 |
| `**粗体**` | **粗体** | 加粗强调 |
| `*斜体*` | *斜体* | 斜体强调 |
| `~~删除线~~` | ~~删除线~~ | 删除线 |
| `` `行内代码` `` | `行内代码` | 行内代码标记 |
| `==高亮==` | <mark>高亮</mark> | 文本高亮（需扩展支持） |
| `- 无序项1`<br>`- 无序项2` | • 无序项1<br>• 无序项2 | 无序列表，可用 `-`/`*`/`+` |
| `1. 有序项1`<br>`2. 有序项2` | 1. 有序项1<br>2. 有序项2 | 有序列表，数字自动编号 |
| `- [ ] 待办`<br>`- [x] 完成` | ☐ 待办<br>☑ 完成 | 任务列表 |
| `术语`<br>`: 定义内容` | **术语**<br>&nbsp;&nbsp;&nbsp;定义内容 | 定义列表 |
| `[文字](https://url)` | [文字](https://url) | 外部链接 |
| `[文字](./other.md)` | [文字](#) | 内部文档链接 |
| `[文字](#锚点)` | [文字](#锚点) | 锚点链接 |
| `<mail@example.com>` | <mail@example.com> | 邮箱链接自动识别 |
| `![alt](img.png)` | ![图片](#) | 基础图片语法 |

---

## A.2 Directives 速查

| 指令名 | 语法示例 | 用途 |
|--------|----------|------|
| `note` | ````{note} 这是备注信息 ```` | 备注提示框 |
| `tip` | ````{tip} 这是技巧提示 ```` | 技巧/建议提示框 |
| `warning` | ````{warning} 注意警告内容 ```` | 警告提示框 |
| `important` | ````{important} 重要事项 ```` | 重要信息提示框 |
| `seealso` | ````{seealso} 参考相关内容 ```` | 参见/相关内容 |
| `danger` | ````{danger} 危险操作警告 ```` | 危险/严重警告 |
| `code-block` | ` ```{code-block} python`<br>`:linenos:`<br>`:caption: 示例代码.py`<br><br>`print("hello")`<br>` ``` ` | 代码块（支持行号、标题、强调行） |
| `math` | ````{math}`<br>`:label: eq-pythagoras`<br><br>`a^2 + b^2 = c^2`<br>```` | 块级数学公式，支持标签引用 |
| `image` | ````{image} img.png`<br>`:width: 80%`<br>`:align: center`<br>```` | 图片插入（宽度/对齐等选项） |
| `figure` | ````{figure} img.png`<br>`:label: fig-example`<br>`:width: 60%`<br><br>图注说明文字<br>```` | 带标题/编号的图片，支持引用 |
| `table` | ````{table} 表格标题`<br>`:label: tbl-data`<br><br>`| 列1 | 列2 |`<br>`|-----|-----|`<br>`| A   | B   |`<br>```` | 带标题/编号的表格 |
| `list-table` | ````{list-table} 标题`<br>`:header-rows: 1`<br><br>`* - 列1`<br>`  - 列2`<br>`* - A`<br>`  - B`<br>```` | 列表式表格（复杂内容友好） |
| `csv-table` | ````{csv-table} 标题`<br>`:header-rows: 1`<br><br>`列1,列2`<br>`A,B`<br>```` | CSV 格式表格 |
| `card` | ````{card} 卡片标题`<br>`:img-top: cover.png`<br><br>卡片正文内容<br>```` | 卡片组件（UI） |
| `dropdown` | ````{dropdown} 点击展开`<br>折叠/展开的内容<br>```` | 折叠面板组件 |
| `tab-set` | ` ```{tab-set}`<br>````{tab-item} 标签1<br>内容1<br>```<br>````{tab-item} 标签2<br>内容2<br>```<br>` ``` ` | 标签页组件 |
| `bibliography` | ` ```{bibliography} refs.bib` ``` | 参考文献列表 |

---

## A.3 Roles 速查

| Role名 | 语法示例 | 用途 |
|--------|----------|------|
| `abbr` | <code>{abbr}`HTML (HyperText Markup Language)`</code> | 缩写（鼠标悬停显示全称） |
| `sub` | <code>H{sub}`2`O</code> | 下标（如 H₂O） |
| `sup` | <code>E=mc{sup}`2`</code> | 上标（如 mc²） |
| `literal` | <code>{literal}`print()`</code> | 行内字面量（等同于反引号） |
| `math` | <code>{math}`E=mc^2`</code> | 行内数学公式 |
| `ref` | <code>{ref}`label-name`</code> | 交叉引用（显示标题文本） |
| `numref` | <code>{numref}`fig-example`</code> | 交叉引用（显示编号，如图 1） |
| `eq` | <code>{eq}`eq-pythagoras`</code> | 公式引用（显示公式编号） |
| `doc` | <code>{doc}`./other.md`</code> | 文档引用（显示文档标题） |
| `cite` | <code>{cite}`author2024`</code> | 学术引用（需 bibliography） |

---

## A.4 配置速查

### mystmd（`myst.yml`）

```yaml
version: 1
project:
  title: 项目标题
  toc:
    - file: intro.md
    - file: chapter1.md
  exports:
    - format: pdf
      pdf: {engine: xelatex}
site:
  template: book-theme
```

### Jupyter Book（`_config.yml` + `_toc.yml`）

```yaml
# _config.yml
title: 书籍标题
execute:
  execute_notebooks: cache
sphinx:
  config:
    html_theme: sphinx_book_theme
```
```yaml
# _toc.yml
format: jb-book
root: intro
chapters:
  - file: chapter1
  - file: chapter2
```

### Sphinx（`conf.py`）

```python
project = '项目名称'
extensions = ['myst_parser', 'sphinxcontrib.bibtex']
source_suffix = {'.md': 'myst-parser'}
html_theme = 'sphinx_rtd_theme'
myst_enable_extensions = [
    'amsmath', 'colon_fence', 'deflist',
    'dollarmath', 'html_image', 'tasklist'
]
```

---

## A.5 常用命令速查

| 命令 | 工具链 | 用途 |
|------|--------|------|
| `myst start` | mystmd | 启动本地预览服务器（热更新） |
| `myst build` | mystmd | 构建静态网站（默认 HTML） |
| `myst build --pdf` | mystmd | 构建 PDF 输出 |
| `myst deploy` | mystmd | 部署到托管平台 |
| `myst clean` | mystmd | 清理构建产物 |
| `jupyter-book create mybook` | Jupyter Book | 创建新书项目 |
| `jupyter-book build .` | Jupyter Book | 构建书籍 |
| `jupyter-book clean .` | Jupyter Book | 清理构建产物 |
| `make html` | Sphinx | 构建 HTML 文档 |
| `sphinx-autobuild . _build/html` | Sphinx | 自动构建+热更新预览 |

---

## A.6 标签与引用速查

### 标签定义方式

| 方式 | 语法示例 | 适用场景 |
|------|----------|----------|
| 块级标签 | `(my-section)=`<br>`## 章节标题` | 标题、章节、独立元素 |
| 指令选项 | ` ```{figure} img.png`<br>`:label: fig-chart`<br><br>`图注...`<br>` ``` ` | 指令内元素（图/表/公式等） |

### 引用方式对比

| 引用语法 | 显示效果 | 适用对象 |
|----------|----------|----------|
| <code>{ref}`label`</code> | 标题文本（如"研究方法"） | 章节、一般元素 |
| <code>{numref}`label`</code> | 编号（如"图 2"、"表 3"） | 图、表等自动编号元素 |
| <code>{eq}`label`</code> | 公式编号（如"(1)"） | 数学公式 |
| <code>{doc}`./file.md`</code> | 文档标题 | 跨文档引用 |
| `[文字](#label)` | 自定义文字链接 | 简单锚点跳转 |

---

> 💡 **提示**：本速查表仅包含最常用语法。完整语法说明、示例和高级用法请参阅教程正文中的对应章节，或查阅 [MyST 官方文档](https://mystmd.org/guide)。

---

## 导航

[« 返回目录](../README.md) | [上一章：常见问题解答](../16-faq.md) | [下一章：资源推荐 »](resources.md)
