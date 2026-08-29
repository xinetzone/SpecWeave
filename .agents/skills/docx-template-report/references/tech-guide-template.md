# 技术文档模板契约（tech-guide-template）

> 配套 [docx-template-report SKILL.md](../SKILL.md)，定义 `templates/tech-guide-template.docx` 的
> 数据上下文契约、适用场景、边界与反模式。
>
> 模板萃取来源：`XMNN_SDK_使用指南v1.1.0.docx`（芯劢微 XMNPU 工具链使用指南）。

## 1. 模板定位

从真实技术文档（SDK 使用指南）萃取的通用结构模板，覆盖技术手册的高频骨架：

| 结构块 | Word 样式 | 说明 |
|--------|-----------|------|
| 封面 | Table Grid（3×1） | 公司名 / 文档标题 / 版本元信息 |
| 更新记录 | Table Grid（5 列） | 版本/修改人/修改日期/修改说明/核定人，行循环 |
| 章节 | Heading 1 | `{% for ch in chapters %}` 循环 |
| 小节 | Heading 2 | `{% for sec in ch.sections %}` 循环 |
| 正文段落 | Normal | 逐段循环 |
| 代码块 | Normal + Consolas + 浅灰底纹 | `sec.code` 逐行循环 |
| 参数表 | Table Grid（4 列） | 表头 + 数据行循环 |

## 2. 数据上下文契约

```python
context = {
    "company":   "公司名",
    "doc_title": "文档标题",
    "doc_meta":  "版本信息 / 日期",
    "revisions": [
        {"version": "1.0.0", "author": "张三", "date": "2025-07-02",
         "desc": "初始版本", "approver": "李四"},
    ],
    "chapters": [
        {
            "title": "章标题",
            "intro": ["章引言段落", "..."],          # 可选，可为空列表
            "sections": [
                {
                    "title": "节标题",
                    "paragraphs": ["正文段落", "..."],
                    "code": ["代码行1", "代码行2"],     # 可选，可为空列表
                    "table": {                         # 可选，省略则不渲染表格
                        "headers": ["参数名", "类型", "可选项", "说明"],
                        "rows": [["name", "str", "", "说明"], ...],
                    },
                },
            ],
        },
    ],
}
```

> 命名约定：键名英文小写下划线，与 `template-guide.md` 一致。

## 3. 适用场景

- 技术使用指南、SDK 手册、工具链文档、API 参考手册
- 需要封面 + 更新记录 + 多级章节 + 代码示例 + 参数表的标准技术文档
- 批量生成多份结构一致、仅内容不同的技术手册

## 4. 边界与扩展（对抗审查结论）

以下能力不在本模板覆盖范围内，需在 Word 中手工调整：

| 需求 | 处置方式 |
|------|---------|
| 2 列说明表 / 3 列属性表 / 5 列命令参数表 | 复制 4 列参数表后增删列数，同步调整占位符 `headers[n]` / `r[n]` 索引 |
| 自动目录（TOC） | 交给 Word 域字段，本 Skill 不处理 |
| 修订追踪 | Word 完成，python-docx 不支持 |
| 富文本混排（加粗/变色） | 用 `{{r richtext}}` + `RichText`（见 template-guide.md） |

**根本原因**：docxtpl 的表格列数在模板中物理固定，无法在渲染期动态增删列。模板聚焦覆盖技术文档最高频的 4 列参数表，牺牲覆盖率换取模板简洁性。

## 5. 反模式

| 反模式 | 后果 | 对策 |
|--------|------|------|
| 用列表索引越界（`headers[4]` 但表只有 4 列） | 渲染报错或空值 | 表头/数据行列数与索引严格对齐 |
| 在 `table` 中放变长列 | 渲染期列数无法匹配 | 列数固定为 4，多列表格手工调整 |
| 代码块与正文混用同一样式 | 代码失去等宽与底纹区分 | 代码走 `sec.code`，等宽 Consolas + 灰底 |
| 遗漏 `intro`/`code`/`table` 字段 | Jinja2 未定义变量报错 | context 中三字段要么给值要么给空列表 |

## 6. 验证记录

- 渲染引擎：docxtpl 0.20.2 + python-docx 1.2.0，py314 环境
- 验证方式：`render_verify.py` 用样例数据渲染，8 项断言（封面/更新记录×2/章节/小节/代码/表格×2）全部 PASS
- 列表索引 `headers[0]`、`r[0]` 语法经 docxtpl 渲染验证支持