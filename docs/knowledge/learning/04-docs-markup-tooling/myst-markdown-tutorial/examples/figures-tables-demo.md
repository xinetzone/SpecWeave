---
id: "myst-example-figures-tables-demo"
title: "示例：图片与表格"
---

# 示例：图片与表格组件

本文件展示图片（Image）、图（Figure）和各类表格的实际渲染效果。

配套教程：[../10-components-figures.md](../10-components-figures.md)

---

## 1. 基础图片与 {image} 指令

### {image} 指令（尺寸/对齐控制）

````markdown
```{image} https://via.placeholder.com/800x300/4f46e5/ffffff?text=居中+80%25宽度
:alt: 示例图片 - 居中对齐
:width: 80%
:align: center
```
````

```{image} https://via.placeholder.com/800x300/4f46e5/ffffff?text=居中+80%25宽度
:alt: 示例图片 - 居中对齐
:width: 80%
:align: center
```

````markdown
```{image} https://via.placeholder.com/300x200/10b981/ffffff?text=左对齐+300px
:alt: 示例图片 - 左对齐
:width: 300px
:align: left
```
````

```{image} https://via.placeholder.com/300x200/10b981/ffffff?text=左对齐+300px
:alt: 示例图片 - 左对齐
:width: 300px
:align: left
```

左对齐图片会让文字环绕，适合图文混排。

<div style="clear: both;"></div>

:::{note}
本地图片请使用相对路径，例如：`![架构图](./images/architecture.png)`，建议在文档同级创建 `images/` 文件夹。
:::

---

## 2. {figure} 组件（带标题 + 自动编号引用）

### 带标签的 Figure 示例

````markdown
```{figure} https://via.placeholder.com/900x400/f97316/ffffff?text=MyST+发布流程图
:label: fig-myst-workflow
:alt: MyST 文档发布流程图
:width: 90%
:align: center

图：MyST Markdown 文档发布工作流程。
```
````

```{figure} https://via.placeholder.com/900x400/f97316/ffffff?text=MyST+发布流程图
:label: fig-myst-workflow
:alt: MyST 文档发布流程图
:width: 90%
:align: center

图：MyST Markdown 文档发布工作流程。
```

### {numref} 引用示例

- 自动编号：如 {numref}`fig-myst-workflow` 所示，发布流程清晰明了。
- 自定义格式：{numref}`图 %s <fig-myst-workflow>` 展示了完整工作流。

### 第二个 Figure

````markdown
```{figure} https://via.placeholder.com/700x350/8b5cf6/ffffff?text=表格+对比
:label: fig-table-comparison
:alt: 表格类型对比
:width: 70%
:align: center

图：五种表格格式适用场景对比。
```
````

```{figure} https://via.placeholder.com/700x350/8b5cf6/ffffff?text=表格+对比
:label: fig-table-comparison
:alt: 表格类型对比
:width: 70%
:align: center

图：五种表格格式适用场景对比。
```

引用：{numref}`fig-table-comparison` 展示了不同表格格式的适用场景。

---

## 3. 各类表格示例

### 3.1 标准管道表格

| 组件 | 语法 | 难度 | 支持合并 | 可引用 |
|------|------|:----:|:--------:|:------:|
| 管道表格 | `|` 分隔 | ⭐ | ❌ | ❌ |
| 网格表格 | `+-|` 绘制 | ⭐⭐⭐ | ✅ | ❌ |
| list-table | 列表定义 | ⭐⭐ | ❌ | ❌ |
| {table} | 包裹表格 | ⭐⭐ | 取决于内部 | ✅ |
| csv-table | CSV 数据 | ⭐ | ❌ | ✅ |

### 3.2 带对齐的管道表格

| 功能点 | 描述 | 状态 | 版本 |
|:-------|:----:|-----:|-----:|
| 图片尺寸控制 | 像素/百分比/比例 | 已发布 | v1.0 |
| Figure 编号 | 配合 {numref} 引用 | 已发布 | v1.2 |
| CSV 导入 | 内联/外部文件 | 已发布 | v1.5 |

### 3.3 网格表格（支持合并）

```markdown
+------------------------+----------------+------------------+
| 功能 \ 版本             | 社区版         | 企业版           |
+============+===========+                |                  |
| 基础功能    | 文档编辑  > 全功能支持    > 全功能支持       |
|            +-----------+                |                  |
|            | 图片表格  |                |                  |
+------------+-----------+----------------+------------------+
| 高级功能    | 协作编辑  | ❌             | ✅               |
+------------+-----------+----------------+------------------+
| 技术支持               | 社区论坛       | 专属客户经理     |
+------------------------+----------------+------------------+
```

+------------------------+----------------+------------------+
| 功能 \ 版本             | 社区版         | 企业版           |
+============+===========+                |                  |
| 基础功能    | 文档编辑  > 全功能支持    > 全功能支持       |
|            +-----------+                |                  |
|            | 图片表格  |                |                  |
+------------+-----------+----------------+------------------+
| 高级功能    | 协作编辑  | ❌             | ✅               |
+------------+-----------+----------------+------------------+
| 技术支持               | 社区论坛       | 专属客户经理     |
+------------------------+----------------+------------------+

### 3.4 list-table 指令

````markdown
```{list-table} 表格选型决策表
:header-rows: 1
:widths: 25 20 55

* - 场景
  - 推荐格式
  - 理由
* - 简单数据快速罗列
  - 管道表格
  - 语法最简洁，编辑最快
* - 内容很长需要换行
  - list-table
  - 无需手动对齐，自动换行
* - 需要合并单元格
  - 网格表格
  - 唯一支持跨行跨列合并
* - 需要正文引用
  - {table} 指令
  - 支持 label 和 numref
* - 从 Excel/CSV 导出
  - csv-table
  - 直接复制粘贴数据
```
````

```{list-table} 表格选型决策表
:header-rows: 1
:widths: 25 20 55

* - 场景
  - 推荐格式
  - 理由
* - 简单数据快速罗列
  - 管道表格
  - 语法最简洁，编辑最快
* - 内容很长需要换行
  - list-table
  - 无需手动对齐，自动换行
* - 需要合并单元格
  - 网格表格
  - 唯一支持跨行跨列合并
* - 需要正文引用
  - {table} 指令
  - 支持 label 和 numref
* - 从 Excel/CSV 导出
  - csv-table
  - 直接复制粘贴数据
```

### 3.5 {table} 指令（带标题 + 可引用）

````markdown
```{table} 各版本功能差异对比
:label: table-edition-compare
:align: center

| 功能模块 | 社区版 | 专业版 | 企业版 |
|----------|:------:|:------:|:------:|
| 基础编辑 | ✅ | ✅ | ✅ |
| 图片表格 | ✅ | ✅ | ✅ |
| 交叉引用 | ✅ | ✅ | ✅ |
| 协作编辑 | ❌ | ✅ | ✅ |
| 审计日志 | ❌ | ❌ | ✅ |
```
````

```{table} 各版本功能差异对比
:label: table-edition-compare
:align: center

| 功能模块 | 社区版 | 专业版 | 企业版 |
|----------|:------:|:------:|:------:|
| 基础编辑 | ✅ | ✅ | ✅ |
| 图片表格 | ✅ | ✅ | ✅ |
| 交叉引用 | ✅ | ✅ | ✅ |
| 协作编辑 | ❌ | ✅ | ✅ |
| 审计日志 | ❌ | ❌ | ✅ |
```

引用：详细功能对比请见 {numref}`table-edition-compare`。

### 3.6 csv-table 指令

````markdown
```{csv-table} 配置项参数说明
:header: "参数名,类型,默认值,说明"
:widths: 15 10 15 60

host,string,0.0.0.0,服务监听地址
port,integer,3000,服务端口号
debug,boolean,false,是否开启调试模式
workers,integer,4,工作进程数
log_level,string,info,日志级别
```
````

```{csv-table} 配置项参数说明
:header: "参数名,类型,默认值,说明"
:widths: 15 10 15 60

host,string,0.0.0.0,服务监听地址
port,integer,3000,服务端口号
debug,boolean,false,是否开启调试模式
workers,integer,4,工作进程数
log_level,string,info,日志级别
```

---

## 4. 交叉引用综合示例

1. 如 {numref}`fig-myst-workflow` 所示，MyST 提供完整发布流程
2. 功能差异详见 {numref}`table-edition-compare`
3. 表格选型参考 {numref}`fig-table-comparison`

---

## 5. 本地图片路径说明

推荐目录结构：

```
your-document.md
images/
  ├── architecture.png
  └── workflow-diagram.svg
```

引用方式：
```markdown
![系统架构](./images/architecture.png)
```

或带标签的 figure：
````markdown
```{figure} ./images/architecture.png
:label: fig-local-arch
:width: 100%

图：本地图片示例
```
````

:::{tip}
SVG 矢量图缩放不失真，适合图表/架构图；PNG 适合截图。
:::
