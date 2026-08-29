***

name: docx-template-report
version: 1.2.1
description: "当用户提到'模板驱动报告'、'生成报告'、'批量报告'、'报告生成'、'模板填充'、'生成docx'、'导出Word报告'、'周报'、'月报'、'报告模板'、'docxtpl'时，必须使用此技能。提供模板驱动报告生成能力：输入校验→模板/数据准备→渲染→产物校验→交付。基于 docxtpl + python-docx，必须使用 py314 环境。不要硬编码 Word 排版——模板是唯一事实来源，代码只填数据。"
argument-hint: "<模板.docx路径> <数据(JSON/YAML/dict)> <输出.docx路径>"
user-invocable: true
title: "Docx-Template-Report 模板驱动报告生成 Skill"
--------------------------------------------

# Docx-Template-Report 模板驱动报告生成 Skill

> 本 Skill 从「Word 模板 + 结构化数据」确定性生成统一格式的 .docx 报告。
> 设计依据见 [docx-template-report-skill-design.md](../../docs/knowledge/learning/docx-template-report-skill-design.md)（v1.1.0）。

## 1. Skill ID

`docx-template-report`

## 2. 功能描述

提供模板驱动报告生成能力，完成「输入校验 → 模板/数据准备 → 渲染 → 产物校验 → 交付」流程：

| 要素   | 载体                          | 说明                   |
| ---- | --------------------------- | -------------------- |
| 模板   | `.docx` + Jinja2 占位符        | **唯一事实来源**，Word 内置样式 |
| 数据   | 结构化 JSON/YAML/dict          | 承载可变内容               |
| 渲染引擎 | `docxtpl`（依赖 `python-docx`） | 执行填充                 |
| 产物校验 | 文件存在性 + 非空 + 结构检测           | 闭环保证                 |

> **为什么用本 Skill 而非手动生成？** 手动生成容易硬编码 Word 排版（样式不一致、维护成本高）、遗漏产物校验（生成损坏文件不自知）。本 Skill 封装了「模板唯一事实来源、零排版代码、闭环校验」三条原则，确保报告样式标准化、可复用、可验证。

## 3. 何时使用本技能

当用户提到以下任何内容时触发：

* 「模板驱动报告」「生成报告」「批量报告」「报告生成」

* 「模板填充」「生成 docx」「导出 Word 报告」

* 「周报」「月报」「季度报告」「复盘报告」「评审报告」等需要格式统一的批量报告

* 已有 Word 模板需要填充数据生成成品

* 需要从结构化数据批量产出统一格式文档

> **关于触发**：本 Skill 只做「模板填充生成报告」这一件事。文档分析、格式互转（docx↔Markdown/PDF）、RAG 加载、在线协作不属于本 Skill 职责。**与系统内置** **`docx`、`consulting-analysis`** **互斥，不可同轮共存**（历史格式冲突教训）。

## 4. 运行环境（强制）

**必须使用 py314（Python 3.14.7）**，所有 Python 命令统一 `py -3.14` 前缀。

> **为什么锁定 py314？** 本机 `python` 命令指向 TRAE 内置 Python 3.10.11，而 `py` 启动器默认版本才是 3.14.7。若不用 `py -3.14` 前缀，依赖会误装入 3.10 环境。

依赖安装（一次成功，无编译报错，均已 dry-run 验证 cp314 兼容）：

```
py -3.14 -m pip install docxtpl==0.20.2 python-docx==1.2.0 lxml==6.1.2
```

| 依赖          | 版本     | py314 兼容性                              |
| ----------- | ------ | -------------------------------------- |
| python-docx | 1.2.0  | `requires_python >=3.9`，纯 Python wheel |
| lxml        | 6.1.2  | 提供 cp314-cp314-win\_amd64 官方 wheel     |
| docxtpl     | 0.20.2 | 纯 Python，依赖均满足                         |

## 5. 核心工作流（五步）

```
步骤1：输入校验 → 步骤2：模板/数据准备 → 步骤3：渲染 → 步骤4：产物校验 → 步骤5：交付
```

### 步骤1：输入校验（数据标准化前置）

* 确认模板路径存在且为 `.docx`

* 确认数据为标准结构（JSON/YAML/dict），非标准格式先收敛

* 校验失败立即报错，不进入渲染

### 步骤2：模板/数据准备

* 有现成模板 → 直接使用

* 无模板 → 用 `pandoc` 从 Markdown 生成基础模板，或在 Word 中新建并加 Jinja2 占位符

* 数据整理为渲染上下文（dict）

> **内置模板**（`templates/`）：
> - `sample-report.docx`：通用报告，三段式示例
> - `tech-guide-template.docx`：**v2 美化版**技术文档模板，科技蓝配色体系 + 三段式封面 + 深蓝表头表格 + 灰底代码块 + 标题分隔线，含封面/更新记录/多级章节/代码块/2-5列多类型表格（契约见 [references/tech-guide-template.md](references/tech-guide-template.md)，渲染示例见 [examples/tech-guide-render-example.py](examples/tech-guide-render-example.py)）

### 步骤3：渲染

```python
# 运行方式：py -3.14 report.py
from docxtpl import DocxTemplate

doc = DocxTemplate("template.docx")
context = {
    "title": "项目周报",
    "items": [
        {"name": "任务1", "status": "完成"},
        {"name": "任务2", "status": "进行中"},
    ],
}
doc.render(context)
doc.save("output.docx")
```

### 步骤4：产物校验（错误分类）

| 错误类别                    | 指向   | 处置           |
| ----------------------- | ---- | ------------ |
| 渲染异常（Jinja2 语法错误/未定义变量） | 模板   | 报告精确占位符问题    |
| 产物校验失败（文件不存在/空/损坏）      | 生成逻辑 | 检查渲染链路       |
| 样式丢失                    | 模板样式 | 改用 Word 内置样式 |

> **⚠️ 校验必须区分两个维度**：`doc.paragraphs` 仅返回正文段落，**不包含表格单元格文本**。若只用 `paragraphs` 收集文本，会出现「报告生成了、表格数据却没进去」却误判成功的情况。须同时遍历 `doc.tables` 的单元格：

```python
from docx import Document

doc = Document("output.docx")
body_text = "\n".join(p.text for p in doc.paragraphs)          # 正文段落
table_text = "\n".join(                                         # 表格单元格
    cell.text for tbl in doc.tables for row in tbl.rows for cell in row.cells
)
# 分别断言正文与表格内容，确保两者均已正确渲染
assert "标题内容" in body_text
assert "表格单元格内容" in table_text
```

### 步骤5：交付

* 返回产物绝对路径 + `computer://` 链接

* 报告意外情况（中文编码、特殊字符）

## 6. 三段式最小示例（新人上手路径）

### 示例 A：简单字段

模板占位符：`{{ title }}`、`{{ author }}`

```python
context = {"title": "季度总结", "author": "张三"}
```

### 示例 B：列表循环

模板占位符：`{% for item in items %} {{ item.name }} {% endfor %}`

```python
context = {"items": [{"name": "A"}, {"name": "B"}]}
```

### 示例 C：表格循环

模板占位符：表格首行 `{% for row in rows %}` ... `{% endfor %}`

```python
context = {"rows": [{"col1": "x", "col2": "y"}]}
```

## 7. 反模式与陷阱对策

| 反模式                             | 后果                   | 对策                       |
| ------------------------------- | -------------------- | ------------------------ |
| 使用系统默认 `python` 而非 `py -3.14`   | 依赖装进 3.10 环境，违反约束    | 所有命令统一 `py -3.14` 前缀     |
| 在代码中硬编码 Word 排版                 | 样式不一致、维护成本高          | 模板唯一事实来源                 |
| 与 consulting-analysis/docx 同时加载 | 输出格式偏离 DOCX/Markdown | 互斥元数据 + 单一职责             |
| 用非 UTF-8 编码或 PowerShell 管道传中文   | 中文乱码                 | 统一 UTF-8，临时文件读写          |
| 忽略产物校验                          | 生成损坏文件不自知            | 闭环校验                     |
| 尝试处理修订追踪/TOC 自动更新               | 超出 python-docx 能力边界  | 交给 Word 模板域字段，本 Skill 不做 |

## 8. 安全检查清单（生成质量门）

* [ ] 全程使用 `py -3.14` 解释器执行，未落到系统默认 3.10 环境

* [ ] 模板已存在且为 `.docx`，数据为标准结构

* [ ] 未与系统 docx/consulting-analysis 同轮共存

* [ ] 模板使用 Word 内置样式（Heading/Normal/Table Grid），未硬编码排版

* [ ] 产物通过存在性 + 非空 + 结构完整性校验

* [ ] 中文内容无乱码

## 9. 关键参考

| 参考               | 层级 | 路径                                                                                                         | 何时查阅                    |
| ---------------- | -- | ---------------------------------------------------------------------------------------------------------- | ----------------------- |
| 方案设计文档           | 设计 | [docx-template-report-skill-design.md](../../docs/knowledge/learning/docx-template-report-skill-design.md) | 理解设计背景与第一性原理推导          |
| Jinja2 模板编写指南    | L2 | [references/template-guide.md](references/template-guide.md)                                               | 编写模板占位符时（A-2 行动项）       |
| 技术文档模板契约        | L2 | [references/tech-guide-template.md](references/tech-guide-template.md)                                     | 使用 `tech-guide-template.docx` 时（数据契约/边界/反模式） |
| 技术文档渲染示例        | L2 | [examples/tech-guide-render-example.py](examples/tech-guide-render-example.py)                             | 复制即用的完整渲染脚本，覆盖 2/3/4/5 列全部表格类型 |
| 错误分类与排查          | L2 | [references/troubleshooting.md](references/troubleshooting.md)                                             | 渲染异常/产物失败/乱码排查（A-3 行动项） |
| docxtpl 官方文档     | 外部 | <https://docxtpl.readthedocs.io/>                                                                          | 高级语法（条件/循环/图片）          |
| python-docx 官方文档 | 外部 | <https://python-docx.readthedocs.io/>                                                                      | 底层 API 细节               |

## 10. Changelog

* **v1.2.1** (2026-08-29): 封面布局调整——品牌栏左公司名、右版本号（版本号移至右上角醒目位置）；字号体系统一优化：正文/表格 11pt、H1 16pt、H2 13pt、封面标题 24pt、代码块 10pt，层级比例更协调。
* **v1.2.0** (2026-08-29): **tech-guide-template v2 美化版**——科技蓝配色体系重构（深蓝 #1F4E79 / 中蓝 #2E75B6 / 浅蓝 #D6E4F0）；封面升级为三段式（品牌栏+大标题+信息表），带分隔线与标签列配色；表格升级深蓝表头白字 + 灰网格边框；代码块升级浅灰底纹 + Consolas 等宽字体；一级标题增加蓝色下分隔线；新增封面信息表字段（doc_status/doc_version/doc_date/doc_author）；示例脚本同步升级为 12 项断言校验；契约文档新增设计规范章节（配色/字体/页面布局）。
* **v1.1.0** (2026-08-29): tech-guide-template 扩展：单 4 列表格升级为 2/3/4/5 列四种预置表格（按 `tbl.cols` 条件切换），`sec.table` 改为 `sec.tables` 列表支持多表格；新增 `examples/tech-guide-render-example.py` 渲染示例脚本（覆盖全部列数类型 + 产物校验）；更新契约文档 v1.1.0。
* **v1.0.1** (2026-08-29): 新增 `templates/tech-guide-template.docx` 技术文档模板（从真实 SDK 使用指南萃取，含封面/更新记录/多级章节/代码块/4列参数表），配套契约文档 `references/tech-guide-template.md`。
* **v1.0.0** (2026-08-29): 初始版本，封装模板驱动报告生成能力（输入校验→渲染→产物校验五步工作流 + 三段式示例 + 6 条反模式），运行环境锁定 py314。

