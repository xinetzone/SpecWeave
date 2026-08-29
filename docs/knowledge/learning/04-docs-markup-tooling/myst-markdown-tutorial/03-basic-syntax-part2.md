---
id: "myst-tutorial-basic-syntax-2"
title: "第3章：基础语法（下）- 列表、链接与图片"
x-toml-ref: "../../../../../.meta/toml/docs/knowledge/learning/04-docs-markup-tooling/myst-markdown-tutorial/03-basic-syntax-part2.toml"
---
# 第3章：基础语法（下）- 列表、链接与图片

本章讲解 MyST Markdown 的列表、链接与图片语法。

---

## 3.1 列表

### 3.1.1 无序列表

使用 `-`、`*` 或 `+` 作为标记，标记后加空格。

```markdown
- 使用连字符
- 第二项
* 星号列表项
+ 加号列表项
```

:::{tip}
同一文档内建议统一使用 `-` 作为列表标记。
:::

**使用场景**：功能清单、并列要点、注意事项。

:::{warning}
标记与文本之间必须有一个空格，`-item` 不会被识别为列表。
:::

---

### 3.1.2 有序列表

数字加 `.`，数字顺序不影响最终渲染，MyST 自动重新编号。

```markdown
1. 第一步
2. 第二步
1. 即使数字顺序不对
1. 也会自动编号为 1、2、3
```

:::{warning}
第一个列表项的数字决定起始编号：`3.` 开头会从 3 开始编号。
:::

**使用场景**：操作步骤、教程流程、变更记录。

---

### 3.1.3 嵌套列表

使用 **4个空格** 或 **1个Tab** 缩进创建子列表。

```markdown
- 一级项
    - 二级项（缩进4空格）
        - 三级项
1. 有序一级
    1. 有序二级
        - 无序子列表
```

:::{warning}
缩进必须对齐，混合空格和Tab会导致解析错误；子列表与父项之间不要有空行。
:::

**使用场景**：多级目录、分类层级、步骤分解。建议最多嵌套3层。

---

### 3.1.4 任务列表

MyST 原生支持 GFM 任务列表，渲染为复选框。

```markdown
- [x] 已完成任务
- [ ] 未完成任务
- [x] 编写文档
```

:::{tip}
在 mystmd 预览环境中，复选框可以点击切换状态。
:::

**使用场景**：TODO清单、待办跟踪、检查清单。

:::{warning}
`[` 和 `]` 与 `x`/空格之间必须有空格，`-[x]` 不会被识别。
:::

---

### 3.1.5 定义列表（MyST增强）

用于术语定义，术语独占一行，下一行以 `:` 开头写定义。

```markdown
MyST
: Markedly Structured Text，Markdown 超集

Directive
: MyST 扩展机制，用于插入复杂组件
```

:::{warning}
术语行后不要有空行；`:` 必须在行首；一个术语可对应多个定义。
:::

**使用场景**：术语表、API参数说明、配置项解释、名词解释。

---

## 3.2 链接

### 3.2.1 外部链接

```markdown
[MyST 官方文档](https://mystmd.org/guide)
[带标题链接](https://github.com "鼠标悬停显示")
直接写URL也可自动识别：https://example.com
```

:::{tip}
MyST 自动识别文本中的 URL 和 DOI，无需手动标记：`DOI: 10.1145/xxx`
:::

**使用场景**：引用外部资源、参考资料、开源项目地址。

---

### 3.2.2 内部文档链接

使用相对路径链接到项目内其他 `.md` 文件。

```markdown
[返回目录](README.md)
[上一章](02-basic-syntax-part1.md)
```

:::{tip}
**{doc} 角色增强**：`` {doc}`02-basic-syntax-part1` `` 自动提取目标文档标题作为链接文本。
:::

:::{warning}
使用相对路径，不要用本地绝对路径；路径区分大小写；移动文档后记得更新路径。
:::

**使用场景**：章节导航、相关文档引用。

---

### 3.2.3 锚点链接

链接到文档内特定标题位置。

```markdown
[跳转到列表章节](#31-列表)
[跨文档锚点](02-basic-syntax-part1.md#21-标题headings)
```

锚点规则：中文保留原样，英文小写、空格替换为 `-`。

:::{warning}
修改标题会导致锚点变化，建议对长期引用位置添加显式标签：
```markdown
(my-label)=
## 需要稳定引用的章节
```
:::

**使用场景**：目录跳转、"回到顶部"、长文档内导航。

### 3.2.4 邮箱链接

用尖括号包裹邮箱地址，自动生成 `mailto:` 链接。

```markdown
<support@example.com>
联系我们：<contact@mystmd.org>
```

也可使用标准语法：`[联系团队](mailto:support@example.com)`

**使用场景**：联系方式、支持邮箱、反馈渠道。

### 3.2.5 引用式链接

将URL集中放在文档末尾，保持正文整洁。

```markdown
正文中引用 [myst-docs][] 或 [自定义文本][ref]。

[ref]: https://example.com "可选标题"
[myst-docs]: https://mystmd.org/guide
```

隐式写法（文本即标签）：
```markdown
访问 [MyST 官网] 了解更多。
[MyST 官网]: https://mystmd.org
```

**使用场景**：同一链接多次使用、长URL、集中管理链接地址。

---

## 3.3 图片

### 3.3.1 基础语法

与链接类似，前面加 `!`。

```markdown
![替代文本](images/screenshot.png)
![远程图片](https://example.com/image.jpg)
```

- `[]` 内是替代文本（Alt Text）：图片加载失败时显示，用于无障碍访问
- `()` 内是图片路径（本地相对路径或远程URL）

:::{warning}
必须填写有意义的Alt Text，不要留空 `![](path)`。
:::

**使用场景**：快速插入简单图片、行内小图标。

---

### 3.3.2 图片标题

路径后加空格，用双引号包裹悬停标题。

```markdown
![安装界面](images/install.png "MyST安装向导第一步")
```

:::{note}
标题（悬停显示）与图注（始终显示在下方）不同，图注需使用 `{figure}` 指令。
:::

**使用场景**：图片补充说明、版权声明、简短注释。

---

### 3.3.3 尺寸与对齐（image指令预览）

基础语法不支持尺寸设置，使用 `image` 指令：

~~~markdown
```{image} images/diagram.png
:alt: 架构图
:width: 600px
:align: center
```
~~~

常用选项：`:width:`、`:height:`、`:align:`（left/center/right）、`:class:`。

:::{tip}
需要图注、自动编号、交叉引用时，使用更强大的 `{figure}` 指令（第10章详解）。
:::

**使用场景**：控制图片大小、居中对齐、响应式图片。

---

### 3.3.4 路径最佳实践

**推荐目录结构**：
```
docs/
├── index.md
└── images/
    ├── screenshot.png
    └── diagram.svg
```

**最佳实践**：
1. 始终使用相对路径，不用绝对路径或 `file://`
2. 图片集中放在 `images/` 目录，规范命名
3. 格式选择：截图用PNG/WebP，矢量图用SVG
4. 控制图片大小，单张建议 < 500KB
5. Windows路径反斜杠 `\` 改为正斜杠 `/`

:::{warning}
提交文档时一起提交图片文件；移动md文件后更新图片路径；路径大小写敏感。
:::

---

## 导航

[« 上一章：基础语法（上）](02-basic-syntax-part1.md) | [返回目录](README.md) | [下一章：高级功能：Directives 和 Roles »](04-advanced-directives-roles.md)
