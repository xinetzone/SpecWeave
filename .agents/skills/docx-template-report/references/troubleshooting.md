# 错误分类与排查指南（troubleshooting）

> 配套 [docx-template-report SKILL.md](../SKILL.md)，供渲染异常/产物失败/乱码排查时查阅。

## 1. 错误分类总览

| 类别 | 典型症状 | 指向 | 首要处置 |
|------|---------|------|---------|
| 渲染异常 | Jinja2 语法错误、未定义变量 | 模板 | 检查占位符语法与 context 键名 |
| 产物失败 | 文件不存在/空/损坏 | 生成逻辑 | 检查渲染链路与保存路径 |
| 样式丢失 | 标题/表格样式异常 | 模板样式 | 改用 Word 内置样式 |
| 中文乱码 | 中文显示为问号/方框 | 编码 | 统一 UTF-8 |

## 2. 渲染异常排查

### 2.1 Jinja2 语法错误

**症状**：抛出 `TemplateSyntaxError` / `TemplateError`。

**排查**：
- 检查 `{% for %}` 与 `{% endfor %}`、`{% if %}` 与 `{% endif %}` 是否成对
- 检查花括号是否完整（`{{` `}}`、`{%` `%}`）

### 2.2 未定义变量

**症状**：抛出 `UndefinedError`，或字段渲染为空。

**排查**：
- 核对 `context` 的键名与模板占位符是否完全一致（含嵌套层级）
- 用 `context.get("key", "默认值")` 兜底，或模板侧用 `{{ var|default("") }}`

### 2.3 占位符不被识别

**症状**：模板中的 `{{ x }}` 原样出现在产物中。

**根因**：占位符被 Word 拆分到多个 run，docxtpl 无法跨 run 识别。

**排查**：
- 在 Word 中删除占位符后一次性重新完整输入
- 或改用 `python-docx` 构造模板（`add_paragraph("{{ x }}")` 整段写入）

## 3. 产物失败排查

| 症状 | 根因 | 处置 |
|------|------|------|
| 文件不存在 | 保存路径错误 / 目录不存在 | 检查输出路径，必要时先 `os.makedirs` |
| 空文件（0 字节） | 渲染未执行 / 异常被吞 | 检查是否调用了 `render` 与 `save` |
| 打开报损坏 | 非标准 docx 写入 | 确认用 `DocxTemplate.save()` 而非手写 zip |

## 4. 中文乱码排查

- **统一 UTF-8**：脚本首行 `# -*- coding: utf-8 -*-`，文件以 UTF-8 保存
- **避免 PowerShell 管道传中文**：长时间运行的中文经管道可能转码丢失，改用临时文件读写
- **字体缺失**：目标机器缺中文字体导致显示异常，模板内嵌字体或指定通用中文字体（宋体/微软雅黑）

## 5. py314 环境问题排查

| 症状 | 根因 | 处置 |
|------|------|------|
| `ModuleNotFoundError: docxtpl` | 依赖装进系统默认 3.10 | 统一 `py -3.14` 前缀重装 |
| lxml 安装报编译错误 | 未命中 cp314 wheel | 确认安装 `lxml==6.1.2`（提供 cp314 win wheel） |
| 解释器版本不对 | 用了内置 3.10 | 检查 `sys.executable` 指向 Python314 |

标准安装命令：

```
py -3.14 -m pip install docxtpl==0.20.2 python-docx==1.2.0 lxml==6.1.2
```

## 6. 产物校验提醒（重要）

产物校验必须**区分正文与表格两个维度**：

- `doc.paragraphs` 只返回正文段落，**不包含表格单元格文本**
- 只校验 `paragraphs` 会漏检「表格数据没渲染进去」的情况

正确做法是分别遍历 `doc.paragraphs`（正文）与 `doc.tables`（表格单元格）并分别断言，详见 SKILL.md 步骤4。

**补充盲区：`w:sdt` 内容块（封面）内段落**。`doc.paragraphs` 只返回 body 直接子段落，
不含 `w:sdt` 块内段落。封面等 sdt 内容须用全树迭代提取：

```python
from docx.oxml.ns import qn
body_text = "\n".join(t.text or "" for t in doc.element.body.iter(qn("w:t")))
```

**结构断言优先于文本断言**：表格行循环出错时文本可能全部存在但物理结构损坏
（单元格横向增生），只查文本会误判 PASS。必须断言物理维度：

```python
assert (len(tbl.rows), len(tbl.columns)) == (预期行数, 预期列数)
```

## 7. 表格行循环专项排查（docxtpl 0.20.2）

### 7.1 症状：单元格横向增生

**症状**：2 列 ×3 行数据，渲染后表格变成 2 行 ×4 列（列数 = 1 + 数据行数）；
5 列修订表 3 行数据变成 2 行 ×13 单元格。文本都在，但结构完全错误。

**根因**：把纯标签 `{% for %}`/`{% endfor %}` 放在**数据行单元格内**
（如首格 `{% for r in rows %}{{ r.a }}`、末格 `{{ r.b }}{% endfor %}`）。
Jinja 在单元格内部循环重复内容，导致单元格横向增生，行不复制。

**对策（三行分离模式）**：for/endfor 各占一个**独立表格行**（标记行），数据行
只放变量：

```
<w:tr>表头行</w:tr>
<w:tr><w:tc>{%tr for r in rows %}</w:tc><w:tc></w:tc></w:tr>   ← 标记行，渲染移除
<w:tr><w:tc>{{ r.a }}</w:tc><w:tc>{{ r.b }}</w:tc></w:tr>      ← 数据行，仅变量
<w:tr><w:tc>{%tr endfor %}</w:tc><w:tc></w:tc></w:tr>          ← 标记行，渲染移除
```

标记行渲染时整行移除（含行内其他静态内容，实证无泄漏），产物为表头 + N 份数据行。

### 7.2 症状：TemplateSyntaxError: Encountered unknown tag 'endfor'

**根因**：同一表格行内出现两个 `{%tr %}` 标记（for 在首格、endfor 在末格）。
docxtpl patch_xml 的行解包正则因回溯绑定到该行**最后一个**标记，整行被替换为
孤立的 `{% endfor %}`，for 标记被吞。

**对策**：同一行/段/列/run 内禁止两次同类显式标记（官方明文规则：*Do not use
`{%p`, `{%tr`, `{%tc` or `{%r` twice in the same paragraph, row, column or run*）。
for 与 endfor 必须分属两个独立标记行。

### 7.3 对照实验脚本

`examples/debug-rowloop-patterns.py` 提供 A-J 十变体隔离实验：A-F 复现上述两类
反模式（语法错误 / 横向增生），G-J 验证三行分离正确模式（标记在首列/末列、
带表头、标记行含静态文本无泄漏）。排查行循环问题时先运行该脚本对照。

> **注意**：块级（段落级）循环/条件不受此限——纯标签 `{% for %}` 独占段落、
> 包裹段落或表格的写法是正确的。三行分离仅针对**表格行复制**场景。

## 8. 品牌资产残留排查（副本基底模板必查）

以真实企业 DOCX 为基底构建模板时，品牌/敏感资产会随包部件继承，且**不在
document.xml 正文里**，只查正文必然漏检：

| 残留类型 | 典型藏匿位置 | 排查/处置 |
|----------|-------------|-----------|
| VML 文字水印（`PowerPlusWaterMarkObject`） | `word/header1-3.xml` 的 `w:pict`/`v:textpath` | 删除 `w:pict` 与 `mc:AlternateContent` 装饰图形，清理水印独立空段落 |
| logo/截图等媒体 | `word/media/`（正文引用删除后仍为孤儿文件残留） | 删除 image 部件关系，孤儿媒体随 OPC 序列化自动排除 |
| WPS 校对缓存/形状扩展 | `customXml/item*.xml`（含源文术语、水印 spid） | 删除 customXml 部件关系 |
| WPS 用户 ID 等私有属性 | `docProps/custom.xml`（base64 编码，肉眼不可见） | 删除 custom-properties 部件关系 |
| 作者真名/标题 | `docProps/core.xml`（creator/lastModifiedBy/title） | core_properties 清空 |

**排查工具**：`examples/scan-brand-residue.py`（全包关键词/media/w:pict/
悬空关系引用四查）与 `examples/analyze-media-watermark.py`（媒体引用与水印
定位盘点）。交付副本基底模板前必跑。

**logo 占位化**：品牌 logo 属于数据而非骨架——drawing run 替换为
`{{ header_logo }}` 等占位标签，渲染时传 `docxtpl.InlineImage` 注入、不传留空。