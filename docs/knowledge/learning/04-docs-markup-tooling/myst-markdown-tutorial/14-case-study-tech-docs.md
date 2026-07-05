---
id: "myst-tutorial-case-tech-docs"
title: "第14章：实战案例 - 技术文档写作"
---

# 第14章：实战案例 - 技术文档写作

本章通过 Python 开源库文档案例，带你走完技术文档从规划到部署的完整流程。配套模板见 [examples/tech-doc-template.md](examples/tech-doc-template.md)。

:::{tip}
**学习目标**：完成本章后能够独立设计文档结构、编写 API 参考、管理版本信息、构建部署专业文档站点。
:::

## 14.1 案例背景

以 Python 数据处理工具库 `pydata-utils` 为例，文档需要包含：快速开始、安装指南、API 参考、分步教程、FAQ。

## 14.2 项目结构设计

推荐目录结构（兼容 mystmd 和 Jupyter Book）：

```
your-project/
├── docs/
│   ├── index.md              # 文档首页
│   ├── getting-started.md    # 快速开始
│   ├── installation.md       # 安装指南
│   ├── tutorials/            # 教程目录
│   │   ├── index.md
│   │   ├── basic-usage.md
│   │   └── advanced.md
│   ├── api/                  # API 参考
│   │   ├── index.md
│   │   ├── cleaning.md
│   │   ├── stats.md
│   │   └── io.md
│   ├── faq.md                # 常见问题
│   ├── examples/             # 示例代码
│   └── myst.yml              # mystmd 配置
├── src/pydata_utils/
├── pyproject.toml
└── README.md
```

## 14.3 YAML Frontmatter 规范

统一 Frontmatter 确保元数据一致性：

```yaml
---
id: "pydata-utils-install"
title: "安装指南"
description: "pydata-utils 库在多平台下的安装方法"
author: "文档团队"
date: "2024-01-15"
---
```

| 字段 | 必填 | 说明 |
|------|------|------|
| `id` | ✅ | 全局唯一标识符，用于交叉引用 |
| `title` | ✅ | 页面标题 |
| `description` | ⚠️ | 页面简介，用于 SEO 和导航 |
| `author` | ⚠️ | 作者/维护者 |
| `date` | ⚠️ | 最后更新日期 |

## 14.4 API 文档编写实战

以 `clean_data()` 函数为例：

````markdown
(clean-data)=
### clean_data(data, drop_na=True, fill_value=None)

清洗输入数据，处理缺失值和异常值。

**参数**：

```{list-table}
:header-rows: 1
:widths: 15 10 20 40

* - 参数名
  - 类型
  - 默认值
  - 说明
* - `data`
  - `pd.DataFrame`
  - **必填**
  - 输入的 DataFrame 数据
* - `drop_na`
  - `bool`
  - `True`
  - 是否删除包含缺失值的行
* - `fill_value`
  - `Any`
  - `None`
  - 缺失值填充值，为 `None` 时不填充
```

**返回值**：`pd.DataFrame` — 清洗后的 DataFrame

**示例**：

```python
import pandas as pd
from pydata_utils import clean_data

df = pd.DataFrame({"a": [1, None, 3], "b": [4, 5, None]})
result = clean_data(df, drop_na=False, fill_value=0)
```
````

:::{warning}
**注意事项**：
- 输入 `data` 不能是空 DataFrame，否则抛出 `ValueError`
- `fill_value` 与 `drop_na=True` 同时使用时，`drop_na` 优先级更高
:::

版本标注指令：

```markdown
:::{versionadded} 1.1.0
新增 `fill_value` 参数支持自定义填充值
:::

:::{versionchanged} 1.2.0
修复了整数列填充后变为浮点数的问题
:::

:::{deprecated} 1.3.0
`inplace` 参数已弃用，请使用返回值赋值方式
:::
```

## 14.5 交叉引用实战

```markdown
详细安装步骤见 [](installation.md)。
进阶用法请参考 [高级教程](tutorials/advanced.md)。
```

定义锚点与引用：

```markdown
(my-anchor)=
### 某节标题

参见 [](#my-anchor) 的说明。
```

代码与图表引用：

```markdown
见 [示例代码](examples/basic-usage.py) 中的完整实现。
数据流程如 [](#data-pipeline) 所示。
```

## 14.6 版本信息管理：Substitution

在 `myst.yml` 中配置全局替换变量：

```yaml
myst:
  substitutions:
    version: "1.2.0"
    min_python: "3.9"
    repo_url: "https://github.com/yourname/pydata-utils"
```

在文档中使用：

````markdown
当前版本：{{ version }}
需要 Python {{ min_python }} 或更高版本。

安装命令：
```bash
pip install pydata-utils=={{ version }}
```
````

:::{tip}
版本号只在 `myst.yml` 中改一次，所有文档自动更新。
:::

## 14.7 代码示例组织

```
docs/examples/
├── basic/
│   ├── 01-quickstart.py
│   └── 02-cleaning.py
└── advanced/
    └── custom-pipeline.py
```

| 场景 | 推荐方式 | 指令 |
|------|---------|------|
| 需要展示运行结果 | 可执行代码块 | `{code-cell} python3` |
| 仅展示代码片段 | 静态代码块 | 普通 ` ```python ` |
| 大型示例文件 | 引用外部文件 | `{literalinclude}` |

引用外部代码：

````markdown
```{literalinclude} examples/basic/cleaning-demo.py
:language: python
:linenos:
:emphasize-lines: 5,10
```
````

## 14.8 常见技术文档模式

### 多平台安装标签页

````markdown
::::{tab-set}
:::{tab-item} pip（推荐）
:sync: pip

```bash
pip install pydata-utils=={{ version }}
```
:::

:::{tab-item} conda
:sync: conda

```bash
conda install -c conda-forge pydata-utils
```
:::

:::{tab-item} 源码安装
:sync: source

```bash
git clone {{ repo_url }}.git
cd pydata-utils
pip install -e .
```
:::
::::
````

### 5分钟快速开始（3W1H结构）

- **What**：这是什么？（1句话）
- **Why**：为什么用？（2-3个核心卖点）
- **Install**：怎么装？（1行命令）
- **Hello World**：最小可运行示例

### 各类提示框场景

```markdown
:::{note} 补充信息、背景知识 :::
:::{tip} 小技巧、最佳实践 :::
:::{important} 必须阅读的关键信息 :::
:::{warning} 可能导致错误的操作 :::
:::{danger} 破坏性操作、安全风险 :::
```

## 14.9 构建与部署

```bash
myst start              # 本地预览
myst build --html       # 构建静态站点
myst build --pdf        # 导出 PDF
```

部署选项：GitHub Pages、Read the Docs、Vercel/Netlify 一键部署。

## 14.10 写作 Checklist

- [ ] 统一 Frontmatter、API 五要素（签名/参数/返回/示例/注意）
- [ ] 交叉引用、substitution 版本管理、多平台标签页
- [ ] 5分钟快速开始、warning 提示、版本标注、无断链

:::{important}
**黄金法则**：用户第一次接触你的项目是看文档，不是看源码。
:::

## 14.11 小结

- 标准结构：首页/快速开始/安装/教程/API/FAQ
- substitution 统一版本号，`{tab-set}` 多平台，`{versionadded}` 标注
- mystmd 构建，部署到 GitHub Pages 或 Read the Docs

配套模板：[examples/tech-doc-template.md](examples/tech-doc-template.md)

## 导航
[« 上一章：mystmd 工具链](13-tooling-mystmd.md) | [返回目录](README.md) | [下一章：实战案例 - 学术论文与书籍 »](15-case-study-academic.md)
