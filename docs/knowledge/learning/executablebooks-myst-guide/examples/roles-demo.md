---
source: "https://mystmd.org/guide/roles"
x-toml-ref: "../../../../../.meta/toml/docs/knowledge/learning/executablebooks-myst-guide/examples/roles-demo.toml"
---

# MyST Roles（行内扩展）示例

Roles 用于在行内插入特殊内容，是 MyST 区别于普通 Markdown 的核心特性之一。与 Directives（块级扩展）不同，Roles 不会产生新的块级元素，而是嵌入在文本行内。

## abbr（缩写）

`{abbr}` role 用于创建缩写，鼠标悬停时会显示全称。

渲染效果：

{abbr}`MyST (Markedly Structured Text)` 是一种专为科学出版设计的 Markdown 扩展格式。

对应代码：

```
{abbr}`MyST (Markedly Structured Text)` 是一种专为科学出版设计的 Markdown 扩展格式。
```

语法说明：在括号中填写缩写和全称，格式为 `缩写 (全称)`。

## sub（下标）

`{sub}` role 用于创建下标文本，常用于化学式、数学公式等场景。

渲染效果：

水的化学式是 H{sub}`2`O，二氧化碳是 CO{sub}`2`。

对应代码：

```
水的化学式是 H{sub}`2`O，二氧化碳是 CO{sub}`2`。
```

## sup（上标）

`{sup}` role 用于创建上标文本，常用于指数、脚注引用等场景。

渲染效果：

爱因斯坦质能方程：E=mc{sup}`2`

对应代码：

```
爱因斯坦质能方程：E=mc{sup}`2`
```

## math（行内数学公式）

`{math}` role 用于在行内插入 LaTeX 语法的数学公式。

渲染效果：

欧拉恒等式：{math}`e^{i\pi} + 1 = 0`，被称为"数学中最优美的公式"。

对应代码：

```
欧拉恒等式：{math}`e^{i\pi} + 1 = 0`，被称为"数学中最优美的公式"。
```

更多数学公式示例：

渲染效果：

- 勾股定理：{math}`a^2 + b^2 = c^2`
- 二次方程求根公式：{math}`x = \frac{-b \pm \sqrt{b^2-4ac}}{2a}`
- 求和符号：{math}`\sum_{i=1}^{n} i = \frac{n(n+1)}{2}`

对应代码：

```
- 勾股定理：{math}`a^2 + b^2 = c^2`
- 二次方程求根公式：{math}`x = \frac{-b \pm \sqrt{b^2-4ac}}{2a}`
- 求和符号：{math}`\sum_{i=1}^{n} i = \frac{n(n+1)}{2}`
```

## 强调类 Roles

MyST 还提供了一些用于语义化强调的 roles。

### strong（加粗强调）

语义化的加粗强调，与 `**text**` 效果类似，但具有明确的语义。

渲染效果：

这是{strong}`非常重要`的内容，请务必注意。

对应代码：

```
这是{strong}`非常重要`的内容，请务必注意。
```

### emphasis（斜体强调）

语义化的斜体强调，与 `*text*` 效果类似。

渲染效果：

这是一个{emphasis}`需要特别说明`的概念。

对应代码：

```
这是一个{emphasis}`需要特别说明`的概念。
```

### literal（行内代码）

语义化的行内代码标记，与 `` `code` `` 效果类似。

渲染效果：

使用 {literal}`print()` 函数输出内容。

对应代码：

```
使用 {literal}`print()` 函数输出内容。
```

## 其他常用 Roles

### kbd（键盘按键）

`{kbd}` role 用于表示键盘按键，通常会渲染为按键样式。

渲染效果：

按 {kbd}`Ctrl` + {kbd}`C` 复制选中内容，按 {kbd}`Ctrl` + {kbd}`V` 粘贴。

对应代码：

```
按 {kbd}`Ctrl` + {kbd}`C` 复制选中内容，按 {kbd}`Ctrl` + {kbd}`V` 粘贴。
```

### file（文件路径）

`{file}` role 用于标记文件或目录路径。

渲染效果：

配置文件位于 {file}`config/myst.yml`，文档源码在 {file}`src/` 目录下。

对应代码：

```
配置文件位于 {file}`config/myst.yml`，文档源码在 {file}`src/` 目录下。
```

### menuselection（菜单选择）

`{menuselection}` role 用于表示 GUI 菜单的选择路径。

渲染效果：

点击 {menuselection}`File --> Open --> Folder...` 打开项目目录。

对应代码：

```
点击 {menuselection}`File --> Open --> Folder...` 打开项目目录。
```

## Roles 语法总结

MyST Roles 的基本语法格式为：

```
{role_name}`content`
```

- `role_name`：role 的名称，如 `abbr`、`sub`、`math` 等
- `content`：role 的内容，放在反引号内
- role 可以嵌入在普通文本行内使用，不会打断段落流
