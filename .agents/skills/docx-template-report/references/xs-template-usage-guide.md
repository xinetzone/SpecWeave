---
id: xs-template-usage-guide
date: 2026-08-29
type: usage-guide
source: "templates/xs-sdk-guide-template.docx"
---

# 脱敏高保真技术文档模板使用说明（xs-sdk-guide-template）

> 本指南面向**使用模板生成文档**的使用者：从零跑通渲染、组织数据、注入 logo、
> 处理目录与交付自检。模板格式规范、构建机制与反模式清单（维护者视角）见
> [xs-sdk-guide-template.md](xs-sdk-guide-template.md)；渲染异常排查见
> [troubleshooting.md](troubleshooting.md)。

## 1. 这份模板能做什么

`templates/xs-sdk-guide-template.docx` 是以一份真实企业 SDK 使用指南为基底、
经副本基底法高保真复刻并**品牌脱敏**后的技术手册模板。渲染时只需传入一个
Python dict，即可生成包含以下结构的 Word 文档：

- **封面**：大标题 + 文件状态/版本/作者/完成日期/审核字段 + 公司名与版权句
- **更新记录页**：5 列深色修订表（版本/修改人/修改日期/修改说明/核定人），行数任意
- **目录页**：TOC 域，Word 打开时一键更新（或按 F9）
- **正文**：按顺序渲染的内容块流——四级标题（自动多级编号）、正文段落、
  列表项、代码块、Shell 命令行（蓝色）、警告行（红色）、2/3/4/5 列参数表、分页符
- **页眉**：公司名 + 页码域，首页页眉独立；logo 位置为占位符，可按需注入

模板本体**零媒体、零水印、零品牌信息、零作者元数据**（19 个部件，约 30 KB），
样式体系（字体、编号链、主题、表格底纹、代码块边框）完整继承自源文档。

> **与 tech-guide-template.docx 如何选择？**
> 本模板是真实企业文档的高保真复刻（公文风格：黑体标题、仿宋正文、深色修订表），
> 适合要求与既有企业文档视觉一致的场景；`tech-guide-template.docx` 是重新设计的
> 科技蓝美化版，适合无历史包袱的新文档。两者数据契约不同，不可混用 context。

## 2. 环境准备

```powershell
# 必须使用 Python 3.14（项目锁定 py314 环境）
py -3.14 -m pip install docxtpl==0.20.2 python-docx==1.2.0
```

模板文件自包含（样式/编号/主题/页眉骨架均在包内），**渲染时不需要源文档**，
也不需要任何图片素材——除非你要注入自己的 logo。

## 3. 五分钟快速开始

新建 `render.py`：

```python
# -*- coding: utf-8 -*-
# 运行：py -3.14 render.py
from docxtpl import DocxTemplate

TPL = r"d:\AI\.agents\skills\docx-template-report\templates\xs-sdk-guide-template.docx"
OUT = r"my-guide.docx"

context = {
    # —— 封面字段 ——
    "doc_title":        "XX SDK 用户使用指南",
    "doc_status":       "正式发布",
    "doc_version":      "1.0.0",
    "doc_author":       "研发部",
    "doc_date":         "2026-08-29",
    "doc_reviewer":     "张三",
    # —— 公司与版权（公司名同时用于封面与页眉）——
    "company":          "XX 科技有限公司",
    "copyright_notice": "（版本所有，翻版必究）",
    # —— 更新记录（任意行数）——
    "revisions": [
        {"version": "1.0.0", "author": "李四", "date": "2026-08-29",
         "description": "初始版本", "reviewer": "张三"},
    ],
    # —— 正文块（按列表顺序渲染）——
    "blocks": [
        {"type": "h1", "text": "开发环境准备"},
        {"type": "p",  "text": "本工具链支持在 Linux 环境下运行。"},
        {"type": "h2", "text": "Conda 环境配置"},
        {"type": "code", "lines": [
            "conda env create --file=env.yaml",
            "conda activate myenv",
        ]},
        {"type": "shell", "text": "$ conda activate myenv"},
        {"type": "warn",  "text": "注意：模型文件必须使用 torch.jit.save 保存。"},
        {"type": "list", "text": "支持 Ubuntu 20.04 及以上版本"},
        {"type": "table", "cols": 4,
         "header": ["参数名", "类型", "默认值", "说明"],
         "rows": [
             ["batch_size", "int", "1", "批大小"],
             ["device", "str", "npu", "运行设备"],
         ]},
        {"type": "pagebreak"},
        {"type": "h1", "text": "量化原理"},
        {"type": "p",  "text": "量化通过降低权重与激活位宽提升推理效率。"},
    ],
}

doc = DocxTemplate(TPL)
doc.render(context)
doc.save(OUT)
print(f"[OK] 已生成: {OUT}")
```

运行后用 Word 打开 `my-guide.docx`，弹出"是否更新域"时选**是**，目录即生成。

> 完整可运行示例（覆盖全部块类型与 2/3/4/5 列表格）见
> [examples/xs-render-example.py](../examples/xs-render-example.py)，
> 运行方式：`py -3.14 examples/xs-render-example.py`，产物在
> `examples/output/xs-template-example.docx`。

## 4. 数据上下文（context）完整参考

### 4.1 封面与公司字段

| 字段 | 含义 | 出现位置 | 是否必填 |
|------|------|---------|---------|
| `doc_title` | 文档大标题（22pt 居中） | 封面 | 是 |
| `doc_status` | 文件状态（如"正式发布"/"草稿"） | 封面 | 是 |
| `doc_version` | 当前版本号 | 封面 | 是 |
| `doc_author` | 作者 | 封面 | 是 |
| `doc_date` | 完成日期 | 封面 | 是 |
| `doc_reviewer` | 审核人 | 封面 | 是 |
| `company` | 公司名 | 封面隐形表 + **页眉每页** | 是 |
| `copyright_notice` | 版权声明句 | 封面 | 是 |
| `header_logo` | 页眉 logo（InlineImage 对象） | 页眉表格左侧 | 否，不传则留空 |
| `cover_logo` | 封面 logo（InlineImage 对象） | 封面标题上方 | 否，不传则留空 |

> 未传入的变量按空字符串渲染，不会残留 `{{ }}` 标签；但文本字段建议全部显式
> 传值，避免封面出现空白栏。

### 4.2 更新记录 `revisions`

列表，每个元素一个 dict，5 个键对应修订表 5 列：

```python
"revisions": [
    {"version": "1.0.0",      # 版本
     "author": "李四",        # 修改人
     "date": "2026-08-29",    # 修改日期
     "description": "初始版本",  # 修改说明（可较长）
     "reviewer": "张三"},      # 核定人
    # ……任意多行，表格按行循环自动扩展
]
```

### 4.3 正文块 `blocks`

列表，元素为 dict，按顺序渲染。`type` 决定块类型：

| type | 必填字段 | 渲染效果 |
|------|---------|---------|
| `h1` | `text` | 一级标题，**自动编号**（1. 2. 3. …） |
| `h2` | `text` | 二级标题，自动编号（1.1 …） |
| `h3` | `text` | 三级标题，自动编号（1.1.1 …） |
| `h4` | `text` | 四级标题 |
| `p` | `text` | 正文段落（仿宋 10.5pt，1.25 倍行距，首行缩进） |
| `list` | `text` | 列表项 |
| `shell` | `text` | 命令行，代码块样式 + 蓝色斜体（建议文本以 `$ ` 开头） |
| `warn` | `text` | 警告行，正文样式 + 红色加粗 |
| `code` | `lines`（字符串列表） | 代码块，**每行一个**带边框段落 |
| `table` | `cols` / `header` / `rows` | 参数表，黑底白字表头（见 4.4） |
| `pagebreak` | 无 | 分页符（此后内容另起一页） |

编号说明：标题编号由模板内置的多级列表链自动维护，**不要**在 `text` 里手写
"1."、"1.1" 等编号；"更新记录"页标题已内置编号抑制，不参与章节计数。

### 4.4 表格块约束

```python
{"type": "table",
 "cols": 4,                                  # 只能是 2、3、4、5
 "header": ["参数名", "类型", "默认值", "说明"],  # 长度必须 == cols
 "rows": [                                    # 每行是列表（不是 dict），长度必须 == cols
     ["batch_size", "int", "1", "批大小"],
     ["device", "str", "npu", "运行设备"],
 ]}
```

- `cols` 仅支持 **2/3/4/5** 四种取值，其他值该表格静默不渲染；
- `len(header) == cols`，且 `rows` 中**每一行**长度都必须等于 `cols`，
  否则渲染出的表格会错位；
- 行数据必须用**列表**（按列序），不能用字典（模板按 `row[i]` 索引取值）；
- 需要 1 列或 6 列以上表格时，在生成的 Word 文档中手工复制邻近表格后增删列。

## 5. 常见任务

### 5.1 注入自己的 logo（可选）

模板已将源文档 logo 位置替换为占位符。传入 docxtpl 的 `InlineImage` 对象即可
注入自己的品牌图片；**不传则位置留空**，不影响排版：

```python
from docxtpl import DocxTemplate, InlineImage
from docx.shared import Mm

doc = DocxTemplate(TPL)
context = {
    # ... 其他字段同上
    "header_logo": InlineImage(doc, r"assets\my-logo.png", width=Mm(20)),  # 页眉，建议小尺寸
    "cover_logo":  InlineImage(doc, r"assets\my-logo.png", width=Mm(40)),  # 封面，可大一些
}
doc.render(context)
doc.save(OUT)
```

- `InlineImage(模板对象, 图片路径, width=..., height=...)`，只设宽度时高度等比缩放；
- 支持 PNG/JPEG 等 Word 兼容格式；图片路径也可以传文件对象；
- 两个字段相互独立，可只注其中一个。

### 5.2 代码块与命令行

- 多行代码/配置用 `code` 块，`lines` 列表中**每个元素一行**，不要自行含换行符；
- 单行 Shell 命令用 `shell` 块（蓝色斜体），与代码块视觉区分；
- 需要警示的内容用 `warn` 块（红色加粗）。

### 5.3 段落内混排（局部加粗/变色）

普通块的 `text` 是纯文本。需要段内局部加粗、变色等富文本效果时，使用 docxtpl
的 `RichText` 并在模板中对应位置使用 `{{r 字段名}}` 标签——本模板未预置富文本
字段，可参考 [template-guide.md](template-guide.md) 的 RichText 用法在 Word 中
自行加标签扩展。

### 5.4 分页与章节组织

- 在 `blocks` 中放入 `{"type": "pagebreak"}` 即强制分页；
- 每个 `h1` 建议开启新的一章（可在其前加 pagebreak）；
- 正文内嵌截图：模板未内置图片块类型，建议渲染后在 Word 中手工插入，
  或参照 [xs-sdk-guide-template.md](xs-sdk-guide-template.md) 第 6 节扩展新块类型。

## 6. 渲染之后：更新目录

模板目录页是 TOC 域，渲染脚本不生成目录条目：

- **Word**：打开文档时若弹出"此文档包含可能引用其他文件的域，是否更新？"选**是**；
  未弹出则点目录区域后按 **F9**（或右键 → 更新域 → 更新整个目录）；
- **WPS**：点击目录区域的"更新目录"按钮；
- 标题增减、页码变化后都需要重新更新域。

模板已设置 `updateFields` 标志，正常情况下打开即会提示更新。

## 7. 品牌中立与交付自检

模板本体经过三脱敏（图形元素 / 敏感部件关系 / 文档元数据），**不含任何源企业的
水印、logo、图片、作者信息**。但请注意：

- 你传入的 `company`、`doc_author`、`revisions` 中的人员名等**数据**会如实渲染
  进产物——品牌中立的责任在数据侧；对外交付前请确认 context 中没有不该出现的
  内部名称、人员真名；
- 模板不含水印，渲染产物也不会出现水印；如需水印请在 Word 中自行添加；
- 交付前可运行全包自检脚本，确认产物零媒体残留、无悬空引用（Word 打开不修复）：

```powershell
py -3.14 examples\scan-brand-residue.py
```

该脚本检查关键词残留、`word/media/` 媒体、VML 水印元素（`w:pict`）、
关系悬空引用，覆盖两个内置模板与示例产物。输出"悬空关系引用: 无"即表示
包结构完整。

## 8. 常见问题（FAQ）

**Q1：不传 logo 会不会留下 `{{ header_logo }}` 字样？**
不会。未传变量按空字符串渲染，占位位置为空白，页眉表格与封面排版不受影响。

**Q2：打开生成的文档目录是空的？**
目录是 TOC 域，需在 Word/WPS 中更新域（打开时选"是"，或 F9）。见第 6 节。

**Q3：标题为什么自动出现了编号？我能关掉吗？**
多级编号是模板样式系统的一部分（H1-H4 绑定 numbering 链），正文标题无需手写
编号。个别标题不需要编号时，在 Word 中选中该段将编号清除即可。

**Q4：表格传了 6 列为什么没渲染出来？**
`cols` 只支持 2/3/4/5，其他值条件块不命中、静默跳过。请检查 context 中
`cols` 与 `header`/`rows` 长度是否一致。

**Q5：渲染报 `TemplateSyntaxError: unknown tag 'endfor'` 或表格列数变多？**
这是手工改动模板表格行循环标签导致的（三行分离机制被破坏）。请直接使用未改动的
模板文件；机制说明与修复见 [troubleshooting.md](troubleshooting.md) 第 7 节。

**Q6：Word 打开提示"文档已损坏/需要修复"？**
通常是包内存在悬空关系引用（手工改包或扩展脚本误删部件所致）。运行
`scan-brand-residue.py` 查看"悬空关系引用"项；使用本技能自带脚本渲染的产物
保证无此问题。

**Q7：能改模板的字体/配色吗？**
可以在 Word 中直接修改样式（开始 → 样式 → 修改），改完另存为新模板使用；
请勿删除含 Jinja 标签的段落/表格行。需要从另一份企业 DOCX 重新萃取时，
使用 [examples/build-xs-template.py](../examples/build-xs-template.py)
重建（重建后须重新执行脱敏扫描，见契约文档 6.1 节）。

**Q8：生成的文档里公司名/人员名是示例数据怎么办？**
渲染示例脚本中的公司名/人员名均为虚构中立演示数据（如「示例科技有限公司」
「张三/李四」），不含任何真实品牌信息。实际使用时替换为你自己的
context 即可；模板本身不含这些内容。

## 9. 工具与延伸阅读

| 用途 | 资源 |
|------|------|
| 复制即用的完整渲染脚本（37 项断言） | [examples/xs-render-example.py](../examples/xs-render-example.py) |
| 交付前品牌残留/包完整性自检 | [examples/scan-brand-residue.py](../examples/scan-brand-residue.py) |
| 模板格式规范、块类型契约、脱敏细节（维护者视角） | [xs-sdk-guide-template.md](xs-sdk-guide-template.md) |
| 渲染异常/乱码/行循环排查 | [troubleshooting.md](troubleshooting.md) |
| Jinja2 语法、RichText 富文本、InlineImage 高级用法 | [template-guide.md](template-guide.md) |
| docxtpl 官方文档 | <https://docxtpl.readthedocs.io/> |
| 技能总说明与五步工作流 | [../SKILL.md](../SKILL.md) |
