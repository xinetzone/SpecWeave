+++
title = "基础语法示例"
source = "https://mystmd.org/guide/syntax-overview"
category = "learning"
tags = ["myst", "examples", "syntax", "admonitions", "code-block", "basic"]
date = "2026-07-02"
+++

# MyST Markdown 基础语法示例

本示例演示 MyST Markdown 常用的 Directives 用法，以及与标准 Markdown 的兼容性。

## Admonitions（提示框）

Admonitions 用于突出显示重要信息，MyST 支持多种内置样式。

### note（普通提示）

用于提供一般性的说明信息。

渲染效果：

:::{note}
这是一个普通提示框，用于展示一般性的说明信息。
:::

对应代码：

````
:::{note}
这是一个普通提示框，用于展示一般性的说明信息。
:::
````

### warning（警告）

用于警告用户需要注意的事项。

渲染效果：

:::{warning}
这是一个警告提示框，请仔细阅读其中的注意事项。
:::

对应代码：

````
:::{warning}
这是一个警告提示框，请仔细阅读其中的注意事项。
:::
````

### tip（小技巧）

用于提供实用的小技巧或建议。

渲染效果：

:::{tip}
这是一个小技巧提示，帮助你更高效地完成任务。
:::

对应代码：

````
:::{tip}
这是一个小技巧提示，帮助你更高效地完成任务。
:::
````

### important（重要信息）

用于强调非常重要的内容。

渲染效果：

:::{important}
这是重要信息，必须认真阅读并遵守。
:::

对应代码：

````
:::{important}
这是重要信息，必须认真阅读并遵守。
:::
````

### caution（谨慎操作）

用于提醒用户谨慎执行某些操作。

渲染效果：

:::{caution}
执行此操作前请确保已备份数据，谨慎操作。
:::

对应代码：

````
:::{caution}
执行此操作前请确保已备份数据，谨慎操作。
:::
````

### seealso（另请参阅）

用于引导用户查看相关资料。

渲染效果：

:::{seealso}
更多详细信息请参考官方文档。
:::

对应代码：

````
:::{seealso}
更多详细信息请参考官方文档。
:::
````

## Code Block（代码块）

MyST 支持增强的代码块功能，包括行号显示、代码高亮等。

### 带行号的 Python 代码块

渲染效果：

:::{code-block} python
:linenos:
:emphasize-lines: 2, 4
def greet(name):
    """打招呼函数"""
    message = f"Hello, {name}!"
    print(message)
    return message

greet("World")
:::

对应代码：

````
:::{code-block} python
:linenos:
:emphasize-lines: 2, 4
def greet(name):
    """打招呼函数"""
    message = f"Hello, {name}!"
    print(message)
    return message

greet("World")
:::
````

参数说明：
- `python`：指定语言为 Python，用于语法高亮
- `:linenos:`：显示行号
- `:emphasize-lines: 2, 4`：高亮第 2 行和第 4 行

## 普通 Markdown 语法

MyST 完全兼容标准 Markdown 语法，以下是常用示例。

### 标题

使用 `#` 表示各级标题：

```
# 一级标题
## 二级标题
### 三级标题
#### 四级标题
```

渲染效果：

# 一级标题示例
## 二级标题示例
### 三级标题示例

### 列表

支持无序列表和有序列表：

**无序列表：**

```
- 项目一
- 项目二
  - 子项目 A
  - 子项目 B
- 项目三
```

渲染效果：

- 项目一
- 项目二
  - 子项目 A
  - 子项目 B
- 项目三

**有序列表：**

```
1. 第一步
2. 第二步
3. 第三步
```

渲染效果：

1. 第一步
2. 第二步
3. 第三步

### 文本格式

支持粗体、斜体等文本格式：

```
**这是粗体文本**
*这是斜体文本*
`这是行内代码`
~~这是删除线文本~~
```

渲染效果：

**这是粗体文本**
*这是斜体文本*
`这是行内代码`
~~这是删除线文本~~

### 链接

```
[外部链接](https://mystmd.org)
[相对链接](./00-overview.md)
```

渲染效果：

[外部链接](https://mystmd.org)
[相对链接](../00-overview.md)

### 图片

```
![替代文字](图片地址)
```

### 引用块

```
> 这是一段引用文本
> 可以跨越多行
```

渲染效果：

> 这是一段引用文本
> 可以跨越多行
