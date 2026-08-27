---
id: "myst-example-ui-components-demo"
title: "示例：卡片、下拉与标签页"
x-toml-ref: "../../../../../../.meta/toml/docs/knowledge/learning/04-docs-markup-tooling/myst-markdown-tutorial/examples/ui-components-demo.toml"
---
# 示例：卡片、下拉与标签页组件

本文件展示卡片（Card）、下拉（Dropdown）、标签页（TabSet）三类组件的实际渲染效果，可直接复制使用。

配套教程：[../09-components-ui.md](../09-components-ui.md)

---

## 1. 基础卡片示例

:::{card} 📚 学习 MyST Markdown
MyST 是专为技术文档设计的 Markdown 超集，支持指令、角色、交叉引用、UI 组件等强大功能。
:::

:::{card} 🔗 访问 MyST 官方文档
:link: https://mystmd.org/guide
:shadow: md
点击此卡片跳转到 MyST 官方指南，获取最新权威语法参考。
+++
:footer: 开始探索 →
:::

---

## 2. 卡片网格布局

::::{grid} 1 2 2 3
:gutter: 3

:::{grid-item-card} 🚀 快速开始
:shadow: sm
3 步搭建第一个 MyST 文档项目。
+++ [开始学习 →](../00-quick-start.md)
:::

:::{grid-item-card} 📦 组件库
:shadow: sm
内置提示框、卡片、标签页等 20+ 种组件。
+++ [查看组件 →](../08-components-admonitions.md)
:::

:::{grid-item-card} 🔧 工具链
:shadow: sm
支持 mystmd、Jupyter Book、Sphinx。
+++ [工具链指南 →](../13-tooling-mystmd.md)
:::

::::

---

## 3. 下拉/折叠面板示例

:::{dropdown} ❓ MyST 和 CommonMark 有什么区别？
MyST 是 CommonMark 的超集，额外提供：
- `:::{directive}` 指令系统
- `` {role}`text` `` 内联角色
- 自动编号交叉引用
- 卡片/标签页/提示框等 UI 组件
- 数学公式、BibTeX 引用等学术功能
:::

:::{dropdown} 💡 学习 MyST 的推荐路径
:open:
建议按顺序学习：
1. 基础部分（00-03章）：快速上手 + 基础语法
2. 高级语法（04-07章）：指令、交叉引用、数学、引用
3. 组件系统（08-10章）：提示框、卡片、图表
4. 工具链与实战（11-15章）
:::

**FAQ 常见问题：**

:::{dropdown} Q: 文档构建后图片不显示？
请检查：1) 是否使用相对路径；2) 文件名是否含特殊字符；3) 图片是否已提交版本控制；4) static 路径配置是否正确。
:::

:::{dropdown} Q: 如何自定义主题颜色？
在 mystmd 项目中创建 `custom.css`，在 `myst.yml` 配置 `site: css: custom.css`，覆盖 CSS 变量即可。
:::

---

## 4. 标签页示例

### 多语言安装命令

::::{tab-set}
:sync: install-lang

:::{tab-item} npm
```bash
npm install -g mystmd
```
:::

:::{tab-item} pip
```bash
pip install mystmd
```
:::

:::{tab-item} brew
```bash
brew install mystmd
```
:::

::::

### 方案对比

::::{tab-set}

:::{tab-item} 方案 A：纯静态
**优点**：部署简单、速度快、安全性高
**缺点**：无动态交互、无法登录
**适用**：开源文档、产品手册、博客
:::

:::{tab-item} 方案 B：服务端渲染
:selected:
**优点**：支持动态内容、SEO 友好、可个性化
**缺点**：需服务器维护、架构复杂
**适用**：企业知识库、付费文档平台
:::

:::{tab-item} 方案 C：SPA
**优点**：体验流畅、交互最强、开发效率高
**缺点**：SEO 较差、首屏加载慢
**适用**：交互式文档、应用内帮助中心
:::

::::

---

## 5. 组件组合使用

卡片 + 下拉面板的组合示例：

::::{grid} 1 1 2 2
:gutter: 2

:::{grid-item-card} 📖 基础入门
适合零基础用户

:::{dropdown} 章节列表
- [00 快速开始](../00-quick-start.md)
- [01 MyST 简介](../01-introduction.md)
- [02-03 基础语法](../02-basic-syntax-part1.md)
:::
:::

:::{grid-item-card} ⚡ 高级特性
适合有基础的用户

:::{dropdown} 章节列表
- [04 指令与角色](../04-advanced-directives-roles.md)
- [05 交叉引用](../05-advanced-cross-references.md)
- [06-07 数学与引用](../06-advanced-math-code.md)
:::
:::

::::

---

> 💡 提示：本文件本身就是用 MyST 编写的，直接用 `myst start` 即可预览所有组件的实际渲染效果。
