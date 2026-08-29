---
id: xs-sdk-guide-template-contract
date: 2026-08-29
type: template-contract
source: "脱敏前源 DOCX（企业 SDK 使用指南，位于本地 .chaos 临时工作区，不入库）"
---

# XS SDK 指南模板契约（xs-sdk-guide-template）

> 配套 [docx-template-report SKILL.md](../SKILL.md)，定义 `templates/xs-sdk-guide-template.docx`
> 的数据上下文契约、格式规范、块类型清单、边界与反模式。
>
> 模板萃取来源：脱敏前的企业 SDK 用户使用指南 DOCX（536 段落 / 26 表格 /
> 86 样式 / 12 媒体；位于本地 `.chaos` 临时工作区，不入库）。采用**副本基底法**
> 构建——以源 DOCX 为基底保留全部样式定义、编号链、主题、页眉、媒体，仅重建
> body 并注入标签，因此视觉保真度为 100%（样式系统不是仿造，是源文档原件）。

## 1. 模板定位

与 `tech-guide-template.docx`（手工重构的科技蓝美化版，样式由脚本生成）互补：
本模板是**真实企业文档的高保真复刻**，适合需要与原文档视觉完全一致、或直接
继承源文档复杂样式体系（多级标题自动编号、深色修订表、代码块边框、页眉 logo）
的批量生成场景。

| 结构块 | 载体 | 说明 |
|--------|------|------|
| 封面 | sdt 内容块 deepcopy | logo + 22pt 黑体居中标题 + 文件状态/版本/作者/日期/审核字段 |
| 封面隐形表 | 3×1 无边框表 deepcopy | 公司名（黑体 16pt 居中）+ 版权句 |
| 更新记录 | H1（numId=0 抑制编号）+ 深色修订表 | 5 列行循环：版本/修改人/修改日期/修改说明/核定人 |
| 目录 | 样式 80 标题 + TOC 域 | Word 打开时经 updateFields 提示更新（或 F9） |
| 正文 | `{% for blk in blocks %}` 块循环 | h1-h4/p/list/shell/warn/code/table/pagebreak 九类块 |
| 页眉 | header1.xml 1×2 表 | logo 图片 + 公司名（9pt）+ PAGE 域，首页页眉独立 |

## 2. 格式规范（源文档实测）

### 2.1 页面与节

- A4：210.01 × 297.0 mm；页边距 上/下 25.4 mm、左/右 31.75 mm；页眉/页脚距边界 12.7 mm
- 首页页眉独立（`different_first_page`）；页脚为空
- 正文可用宽度约 8306 twips（块表等宽列据此计算）

### 2.2 样式体系（styleId）

| styleId | 名称 | 规格 | 用途 |
|---------|------|------|------|
| 1 | Normal | 华文仿宋 10.5pt，两端对齐，首行缩进 2 字符 | 正文基底 |
| 2 | H1 | 黑体 18pt，绑定多级列表 numId=1 | 一级标题（自动编号 `1.`） |
| 3 | H2 | 16pt，ilvl=1 | 二级标题（`1.1`） |
| 4 | H3 | 15pt，ilvl=2 | 三级标题（`1.1.1`） |
| 5 | H4 | 14pt，ilvl=3 | 四级标题 |
| 64 | code | 华文楷体 9pt，color=333333，左右缩进，四边框 + 底纹 | 代码块/命令行（源文档 217 段） |
| 63 | 表格文本 | 宋体，无首行缩进 | 表格单元格段落 |
| 80 | TOC 标题2 | color=104862，居中 | “目录”标题 |
| 46 | List Paragraph | left=720 | 列表项 |
| 58 | OP_ExcelTableContent-911 | 表头 shd=191919 白字 bold，数据行 shd=B8B0B0 | 修订记录深色表 |
| 26 | Table Grid | 标准网格 | 块表（表头改造为 shd=000000 白字 bold 居中） |

- docDefaults：ascii/hAnsi/cs = Times New Roman，eastAsia = 宋体
- 正文段落直接格式：行距 1.25 倍（`w:line=300 lineRule=auto`）、首行缩进 420 twips
- shell 命令行：code 样式 + color=215F9A 蓝色斜体 run
- 警告行：Normal 样式 + color=EE0000 红色加粗 run

### 2.3 标题自动编号链

numbering.xml 中 numId=1 → abstractNumId=2，L0-L4 通过 pStyle 绑定
styleId 2/3/4/5/6，decimal 格式 `%1.` / `%1.%2.`。
“更新记录”H1 通过显式 `numId=0` 抑制编号（不参与章节计数）。

### 2.4 代码块

每行一个 code(64) 段落、单 run；模板内为段落级循环
`{% for line in blk.lines %}`（纯标签独占段落）。源文档共 65 个连续代码块，
最长 35 行。

## 3. 数据上下文契约

```python
# 以下示例数据均为虚构中立数据，不含任何真实品牌/人员信息
context = {
    # 封面 sdt 字段
    "doc_title":       "XS SDK 用户使用指南",
    "doc_status":      "正式发布",          # 文件状态
    "doc_version":     "1.1.0",             # 当前版本
    "doc_author":      "张三",              # 作者
    "doc_date":        "2025-10-15",        # 完成日期
    "doc_reviewer":    "李四",              # 审核
    # 封面隐形表
    "company":         "示例科技有限公司",   # 同时用于页眉
    "copyright_notice": "（版本所有，翻版必究）",
    # 品牌 logo（可选，不传则位置留空；模板本体零媒体，见 6.1 脱敏说明）
    # "header_logo":  InlineImage(tpl, "logo.png", width=Mm(20)),   # 页眉表格左侧
    # "cover_logo":   InlineImage(tpl, "logo.png", width=Mm(40)),   # 封面 sdt 内
    # 修订记录（5 列深色表，行循环）
    "revisions": [
        {"version": "1.0.0", "author": "王五", "date": "2025-07-02",
         "description": "初始版本", "reviewer": "李四"},
        # ... 任意行数
    ],
    # 正文块（顺序渲染）
    "blocks": [
        {"type": "h1", "text": "开发环境准备"},
        {"type": "h2", "text": "Conda 环境配置"},
        {"type": "h3", "text": "构建 xsenv 环境"},
        {"type": "h4", "text": "环境变量说明"},
        {"type": "p",    "text": "正文段落……"},
        {"type": "list", "text": "列表项……"},
        {"type": "shell", "text": "$ conda activate xsenv"},
        {"type": "warn",  "text": "注意：……"},
        {"type": "code",  "lines": ["cd release", "conda env create --file=xs.yaml"]},
        {"type": "table", "cols": 4,
         "header": ["参数名", "类型", "默认值", "说明"],
         "rows": [["batch_size", "int", "1", "批大小"], ...]},
        {"type": "pagebreak"},
        # ...
    ],
}
```

### 3.1 blocks 块类型清单

| type | 必填字段 | 渲染样式 |
|------|---------|---------|
| `h1` / `h2` / `h3` / `h4` | `text` | 样式 2/3/4/5，自动编号 |
| `p` | `text` | Normal + 1.25 倍行距 + 首行缩进 |
| `list` | `text` | List Paragraph(46) |
| `shell` | `text` | code(64) + 215F9A 蓝斜体 |
| `warn` | `text` | Normal + EE0000 红加粗 |
| `code` | `lines`（字符串列表） | 每行一个 code(64) 段落 |
| `table` | `cols`(2/3/4/5)、`header`（长度=cols）、`rows`（每行长度=cols） | Table Grid + 黑底白字表头 |
| `pagebreak` | 无 | 插入分页符 |

> **表格约束**：`cols` 只能是 2/3/4/5；`header` 长度与 `rows` 每行长度必须等于 `cols`。
> 不支持的列数静默不渲染（条件块不命中）。

## 4. 表格行循环机制（三行分离，核心）

docxtpl 0.20.2 的表格行循环**必须**使用三行分离结构（经
`examples/debug-rowloop-patterns.py` A-J 十变体实证）：

```
模板物理行：
  <w:tr>表头</w:tr>
  <w:tr><w:tc>{%tr for x in items %}</w:tc> ...</w:tr>   ← for 标记行（渲染时整行移除）
  <w:tr><w:tc>{{ x.a }}</w:tc><w:tc>{{ x.b }}</w:tc></w:tr>  ← 数据行（只放变量）
  <w:tr><w:tc>{%tr endfor %}</w:tc> ...</w:tr>           ← endfor 标记行（渲染时整行移除）
渲染结果：表头行 + N 份数据行
```

机制要点：

- docxtpl 的 patch_xml 对含 `{%tr ... %}` 标记的整行解包：标记裸留在行位置，
  该行渲染时移除；数据行随之按 Jinja 循环复制。
- **块级段落循环/条件**（包裹段落或表格的 `{% for %}`/`{% if %}`）用纯标签
  **独占段落**即可，不需要 `{%p %}` 显式标记。
- 两种致命反模式（详见 troubleshooting.md）：
  1. 数据行单元格内放纯标签 `{% for %}` → Jinja 在格内重复内容，**单元格横向增生**
     （2 列 ×3 数据渲染成 2 行 ×4 列）；
  2. 同一行内出现两个 `{%tr %}` 标记（for 在首格、endfor 在末格）→ patch_xml
     正则回溯吞掉 for 标记 → `TemplateSyntaxError: Encountered unknown tag 'endfor'`。
- 官方规则原文：*Do not use `{%p`, `{%tr`, `{%tc` or `{%r` twice in the same
  paragraph, row, column or run.*

## 5. 适用场景

- 需要与源企业文档（企业 SDK 指南）视觉完全一致的批量文档生成
- 依赖标题自动编号、深色修订表、代码块边框等源文档样式资产（logo/水印已脱敏，按需注入）
- 内容可抽象为顺序块流（标题/段落/列表/代码/命令/警告/表格/分页）的技术手册
- 修订记录行数、正文块数量、表格行数均为运行期数据，模板物理结构固定

## 6. 边界与扩展

| 需求 | 处置方式 |
|------|---------|
| 1 列或 ≥6 列表格 | Word 中复制最近列数表格后增删列 |
| 目录内容 | TOC 域 + updateFields，Word 打开时更新（F9），脚本不生成目录条目 |
| 页眉/封面 logo | 模板内置 `{{ header_logo }}`/`{{ cover_logo }}` 占位；传 `InlineImage` 注入，不传留空 |
| 正文内嵌图片（源文档正文 11 处） | blocks 不含 image 块；可用 docxtpl `InlineImage` 扩展新块类型，或渲染后 Word 手工插入 |
| 富文本混排（段内加粗/变色） | `{{r richtext}}` + RichText（见 template-guide.md） |
| 合并单元格 | Word 手工，docxtpl 不支持动态合并 |
| 斑马纹交替行底色 | 行循环为单物理行复制，无法逐行交替；需后处理 |
| 更换品牌/样式 | 修改源基底 DOCX 后重跑 `examples/build-xs-template.py`（水印/元数据随源文件变化需复核脱敏） |
| 新增块类型 | 在 build 脚本 blocks 段加 `{% if blk.type == "xxx" %}` 分支并重建模板 |

### 6.1 品牌资产脱敏（模板品牌中立）

模板以源文档为基底构建，但**品牌资产属于数据而非骨架**，构建时执行三脱敏
（build 脚本步骤 8），模板本体保持品牌中立：

| 脱敏对象 | 源文档内容 | 处置 |
|----------|-----------|------|
| VML 水印 | 三个页眉部件的 `PowerPlusWaterMarkObject`（原品牌英文标识水印文字，斜向居中）+ `mc:AlternateContent` 装饰图形（椭圆） | 删除 `w:pict`/`mc:AlternateContent`，清理水印独立空段落 |
| logo 图片 | image1.png（页眉表格 + 封面 sdt，共 3 处引用） | drawing run 替换为 `{{ header_logo }}`/`{{ cover_logo }}` 占位 |
| 媒体文件 | 12 个媒体（logo + 正文截图 11 张，约 1.26MB） | 删除全部 image 部件关系，孤儿媒体随序列化排除（模板 1.25MB→43KB） |
| WPS 自定义 XML | customXml/item1-3（校对缓存含源文术语、水印形状扩展） | 删除 customXml 部件关系 |
| WPS 自定义属性 | docProps/custom.xml（base64 内含 WPS 用户 ID） | 删除 custom-properties 关系 |
| 核心元数据 | docProps/core.xml（作者真名、修改者、标题、打印时间） | 字段清空 |

> **重建依赖说明**：模板文件自包含（styles/numbering/theme/header 骨架已继承，
> 零媒体），渲染时不需要源文档。仅当需要**重建模板**时才依赖源基底 DOCX
> （企业 SDK 使用指南，位于 `.chaos/tests/old/work/doc/` 临时工作区，
> 若被清理需先恢复源文件），路径可通过构建脚本位置参数覆盖。

## 7. 反模式

| 反模式 | 后果 | 对策 |
|--------|------|------|
| 数据行格内放纯标签 `{% for %}` | 单元格横向增生 | 三行分离 `{%tr %}` 标记行 |
| 同一行放两个 `{%tr %}` 标记 | unknown tag 'endfor' | for/endfor 各占独立标记行 |
| `cols` 与 header/rows 长度不一致 | 索引越界、空值 | cols == len(header) == len(rows[i]) |
| `cols` 取 2/3/4/5 以外值 | 表格静默不渲染 | 校验取值 |
| 表格行数据用字典 `{{ r.key }}` | 与模板 `{{ row[i] }}` 索引不兼容 | 行数据用列表 |
| 用 `doc.paragraphs` 断言封面/表格 | sdt 与表格内段落漏检 | body 全树 `iter(qn("w:t"))` + tables 双维度 |
| 只断言文本不断言物理结构 | 横向增生坏结构误判 PASS | 断言 `len(tbl.rows)/len(tbl.columns)` |
| 副本基底法只清正文不查包部件 | 孤儿媒体、水印、customXml、WPS 用户 ID 残留 | 三脱敏（图形/敏感关系/元数据）+ 全包关键词扫描 |
| 脱敏只查 document.xml | 水印在 header*.xml、userId 在 docProps/custom.xml | 遍历包内全部 .xml/.rels 部件扫描 |
| 直接改 .docx 后不更新本契约 | 字段与模板不同步 | 模板变更同步更新本文档 |

## 8. 构建与验证

- 模板构建（副本基底法）：[examples/build-xs-template.py](../examples/build-xs-template.py)

  ```
  py -3.14 examples/build-xs-template.py [源docx] [输出模板docx]
  ```

- 渲染验证（37 项断言，含 H 组脱敏专项 6 项）：[examples/xs-render-example.py](../examples/xs-render-example.py)

  ```
  py -3.14 examples/xs-render-example.py
  ```

- 品牌残留与 OPC 完整性扫描：[examples/scan-brand-residue.py](../examples/scan-brand-residue.py)
  （关键词/media/w:pict/悬空关系引用，覆盖模板与渲染产物）

  ```
  py -3.14 examples/scan-brand-residue.py
  ```

- 行循环机制实验：[examples/debug-rowloop-patterns.py](../examples/debug-rowloop-patterns.py)
  （A-J 十变体，A-F 为反模式复现，G-J 为三行分离正确模式）

## 9. 验证记录

- **v1.0.0**（2026-08-29）：
  - 渲染引擎：docxtpl 0.20.2 + python-docx 1.2.0，py314 环境
  - 31 项断言全部 PASS：封面 6 项（标题/版本/状态/作者/日期/审核 + 无残留标签 +
    变量化检查）、页眉 3 项（公司名 ×2、logo drawing）、更新记录 5 项（标题/
    修订表 4 行物理结构/循环数据/numId=0/191919 表头底纹）、目录 3 项（标题/
    TOC 域/updateFields）、正文块 6 项（H1×3/H2×1/code 6 段/shell 215F9A/
    warn EE0000/列表 2）、表格 4 项（总数 6/块表维度 3×2·3×3·3×4·3×5/
    数据文本/000000 表头）、部件保真 4 项（code 样式/numbering 绑定/
    theme1.xml/media）
  - 样式/编号/主题/页眉/媒体 100% 继承源文档（副本基底法）

- **v1.1.0**（2026-08-29）：品牌资产脱敏
  - 背景：v1.0.0 副本基底法将源文档品牌资产一并继承（V 阶段对抗审查发现）
  - 脱敏内容：三个页眉 `PowerPlusWaterMarkObject` 水印（原品牌英文标识文字）+
    椭圆装饰图形删除；logo 图片 3 处（页眉 ×2/封面 sdt ×1）替换为
    `{{ header_logo }}`/`{{ cover_logo }}` 占位；12 个媒体文件（约 1.26MB）
    随 image 关系删除全部排除；customXml/item1-3（WPS 校对缓存含水印形状扩展）
    与 docProps/custom.xml（base64 含 WPS 用户 ID）关系删除；core.xml 作者/
    修改者/标题/打印时间清空；模板体积 1,252,794 → 43,102 字节，部件 29 → 19
  - 验证：37 项断言全部 PASS（新增 H1-H6 脱敏专项：模板/产物零水印文字与元素、
    零媒体、logo 占位标签存在、元数据脱敏、页眉无残留标签；B3 由"logo 保留"
    反转为"零水印零图形"；G4 反转为"零媒体"）
  - 扫描工具：examples/scan-brand-residue.py（关键词/media/pict/悬空关系四查），
    模板本体零残留、零悬空引用；渲染产物中的公司名/人员名原为 context 演示数据
    （预期行为，数据由使用者传入）

- **v1.2.0**（2026-08-30）：品牌中立化更名
  - 模板文件名由原产品代号更名为 `xs-sdk-guide-template.docx`（模板二进制内容
    不变，仅文件更名；构建脚本/渲染示例/文档引用同步更名）
  - 渲染示例演示数据全部替换为虚构中立数据（公司「示例科技有限公司」、
    作者/审核「张三/李四」、示例命令 xs.yaml/xsenv/xs:latest），断言同步更新
  - 验证：37 项断言全部 PASS；scan-brand-residue.py 扫描模板与渲染产物
    品牌关键词均 0 命中；检测词表原样保留（扫描器职责）
