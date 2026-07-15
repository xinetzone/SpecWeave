---
id: "myst-tutorial-ui-components"
title: "第9章：扩展组件 - 卡片、下拉与标签页"
x-toml-ref: "../../../../../../.meta/toml/docs/knowledge/learning/04-docs-markup-tooling/myst-markdown-tutorial/09-components-ui.toml"
---
# 第9章：扩展组件 - 卡片、下拉与标签页

除了提示框之外，MyST 还提供了丰富的 UI 交互组件，让技术文档具备类似网页应用的交互体验。本章介绍三种最常用的组件：卡片（Card）、下拉/折叠面板（Dropdown）和标签页（Tab/TabSet）。

:::{note}
本章配套示例文件：[examples/ui-components-demo.md](examples/ui-components-demo.md)。
:::

## 9.1 卡片（Card）组件

卡片组件用于将相关内容组织在独立的视觉容器中，常用于功能介绍、产品展示、导航入口等场景。

### 9.1.1 基本语法

使用 `:::{card}` 指令创建卡片，第一行是标题，后续是内容：

````markdown
:::{card} 卡片标题
这是卡片的正文内容，可以包含 **Markdown** 格式的文本、
列表、链接甚至代码片段。
:::
````

:::{card} 卡片标题
这是卡片的正文内容，可以包含 **Markdown** 格式的文本、
列表、链接甚至代码片段。
:::

### 9.1.2 常用选项

| 选项 | 作用 | 示例值 |
|------|------|--------|
| `:link:` | 点击卡片跳转的 URL | `https://mystmd.org/guide` |
| `:width:` | 卡片宽度 | `50%`、`300px` |
| `:shadow:` | 阴影效果 | `none`/`sm`/`md`/`lg` |
| `:footer:` | 卡片底部内容 | 与 `+++` 分隔符配合使用 |

**示例 - 带链接和阴影的卡片：**

````markdown
:::{card} 前往官方文档
:link: https://mystmd.org/guide
:shadow: md
点击此卡片可跳转到 MyST 官方文档站点。
+++
:footer: 了解更多 →
:::
````

:::{card} 前往官方文档
:link: https://mystmd.org/guide
:shadow: md
点击此卡片可跳转到 MyST 官方文档站点。
+++
:footer: 了解更多 →
:::

### 9.1.3 卡片网格布局

配合 `::::{grid}` 指令实现多列响应式网格，`{grid}` 后数字 `1 2 2 3` 表示 xs/sm/md/lg 屏幕尺寸下的列数：

`````markdown
::::{grid} 1 2 2 3
:gutter: 3

:::{grid-item-card} 🚀 快速上手
5分钟完成安装与初始化。
:::

:::{grid-item-card} 📦 组件丰富
内置 20+ 种出版级组件。
:::

:::{grid-item-card} 🔌 生态完善
支持多种工具链。
:::
::::
`````

渲染效果：

::::{grid} 1 2 2 3
:gutter: 3

:::{grid-item-card} 🚀 快速上手
5分钟完成安装与初始化。
:::

:::{grid-item-card} 📦 组件丰富
内置 20+ 种出版级组件。
:::

:::{grid-item-card} 🔌 生态完善
支持多种工具链。
:::
::::

:::{tip}
`grid-item-card` 是 `grid-item` + `card` 的便捷组合，专门用于网格卡片布局。
:::

**使用场景**：功能介绍、产品展示、导航入口、团队成员名片。

## 9.2 下拉/折叠面板（Dropdown）组件

下拉/折叠面板允许用户点击标题来展开或收起内容，适合组织补充信息、FAQ 问答等。

### 9.2.1 基本语法

使用 `:::{dropdown}` 指令，第一行是可点击标题，内部是可折叠内容：

````markdown
:::{dropdown} 点击展开查看详细信息
这部分内容默认折叠，可以包含任意 Markdown：
- 列表项
- **粗体文本**
- `代码片段`
:::
````

:::{dropdown} 点击展开查看详细信息
这部分内容默认折叠，可以包含任意 Markdown：
- 列表项
- **粗体文本**
- `代码片段`
:::

### 9.2.2 默认展开与嵌套

使用 `:open:` 选项让面板默认展开：

````markdown
:::{dropdown} 默认展开的面板
:open:
这部分内容默认展开，适合展示大多数用户都需要的信息。
:::
````

:::{dropdown} 默认展开的面板
:open:
这部分内容默认展开，适合展示大多数用户都需要的信息。
:::

下拉面板支持嵌套其他组件（提示框、代码块，甚至嵌套下拉）：

`````markdown
:::{dropdown} 🔧 高级配置选项
:::{warning}
修改高级配置可能影响系统稳定性。
:::

```python
config = {"timeout": 30, "retry": 3}
```
:::
`````

**使用场景**：FAQ 常见问题、补充信息/技术细节、高级用户选项、习题答案折叠。

## 9.3 标签页（Tab/TabSet）组件

标签页允许在同一空间切换显示多个内容面板，是组织平行内容的理想选择。

### 9.3.1 基本语法

两层指令配合：外层 `::::{tab-set}`（4冒号），内层多个 `:::{tab-item}`（3冒号）：

`````markdown
::::{tab-set}

:::{tab-item} Python
```python
print("Hello, MyST!")
```
:::

:::{tab-item} JavaScript
```javascript
console.log("Hello, MyST!");
```
:::

::::
`````

渲染效果：

::::{tab-set}

:::{tab-item} Python
```python
print("Hello, MyST!")
```
:::

:::{tab-item} JavaScript
```javascript
console.log("Hello, MyST!");
```
:::

::::

### 9.3.2 默认选中与同步切换

- `:selected:` 指定默认选中标签（默认第一个）
- `:sync:` mystmd 独有功能，让多个标签组同步切换（如全局切换代码语言）

`````markdown
::::{tab-set}

:::{tab-item} 方案A
实现简单，性能一般。
:::

:::{tab-item} 方案B
:selected:
推荐方案，性能优秀。
:::

::::
`````

:::{tip}
`:sync:` 对多语言教程非常实用——用户选择一次语言后，页面所有代码示例自动切换到对应语言。
:::

**使用场景**：多语言代码示例、多平台安装步骤、多版本 API 对比、多种方案优缺点对比。

## 9.4 工具链兼容性

| 组件 | mystmd | Jupyter Book | Sphinx |
|------|--------|-------------|--------|
| card/dropdown/grid | ✅ 原生支持 | ✅ 自动包含 sphinx-design | ⚠️ 需安装 sphinx-design |
| tab-set | ✅ 原生支持（含 sync） | ✅ 自动包含 sphinx-tabs | ⚠️ 需安装 sphinx-tabs |

- **mystmd**：所有组件原生支持，`:sync:` 为独有特性
- **Jupyter Book**：自动包含所需扩展，开箱即用
- **Sphinx**：需在 `conf.py` 中启用：
  ```python
  extensions = ["myst_parser", "sphinx_design", "sphinx_tabs"]
  ```

:::{warning}
Sphinx 的 sphinx-design 部分选项名称可能与 mystmd 略有差异，跨工具链时请查阅对应文档。
:::

## 9.5 使用建议

1. **适度使用**：一页卡片网格不超过 2 行（6-8张），避免视觉混乱
2. **信息层级**：核心内容直接展示，补充信息用 dropdown，平行选项用 tab-set
3. **移动端适配**：使用响应式列数（如 `1 2 2 3`）
4. **保持一致**：同类内容始终使用同一种组件
5. **可发现性**：重要信息不要只放在折叠面板里

## 9.6 小结

- **卡片**：`:::{card}` 创建独立容器，配合 `grid` 实现网格布局，用于功能展示/导航
- **下拉**：`:::{dropdown}` 创建可折叠内容，`:open:` 控制默认展开，用于 FAQ/补充信息
- **标签页**：`::::{tab-set}` + `:::{tab-item}` 实现多标签切换，`:selected:` 指定默认，`:sync:` 跨组同步
- **兼容性**：mystmd 原生支持最佳，Jupyter Book 开箱即用，Sphinx 需手动安装扩展

## 导航

[« 上一章：提示框](08-components-admonitions.md) | [返回目录](README.md) | [下一章：图片与表格 »](10-components-figures.md)
