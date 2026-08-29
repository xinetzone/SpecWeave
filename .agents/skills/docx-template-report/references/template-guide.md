# Jinja2 模板编写指南（template-guide）

> 配套 [docx-template-report SKILL.md](../SKILL.md)，供编写 `.docx` 模板占位符时查阅。
> 渲染引擎：`docxtpl`（Jinja2 语法 + `python-docx`），运行环境 py314。

## 1. 占位符语法速查

| 需求 | 语法 | 说明 |
|------|------|------|
| 单变量 | `{{ title }}` | 直接取值 |
| 嵌套字段 | `{{ user.name }}` | 字典/对象属性访问 |
| 列表循环 | `{% for item in items %}...{% endfor %}` | 遍历列表 |
| 字典循环 | `{% for k, v in info.items() %}...{% endfor %}` | 遍历键值对 |
| 条件 | `{% if score > 90 %}...{% elif %}...{% else %}...{% endif %}` | 分支渲染 |
| 富文本 | `{{r richtext}}` | RichText 对象，可混排样式 |
| 段内换行 | `{%p for line in lines %}{{ line }}...{%p endfor %}` | 控制段落边界 |

## 2. 数据上下文契约

渲染时的 `context` 是普通 Python dict，键名必须与模板占位符一一对应：

```python
context = {
    "title": "季度总结",              # 对应 {{ title }}
    "author": "张三",                # 对应 {{ author }}
    "items": [                       # 对应 {% for item in items %}
        {"name": "A", "status": "完成"},
        {"name": "B", "status": "进行中"},
    ],
}
```

> **命名约定**：键名用英文小写/下划线，语义清晰，避免与 Jinja2 保留字冲突。

## 3. 表格循环（高频场景）

表格循环需将 `{% for %}` 与 `{% endfor %}` 分别放在**首行和数据行**（或首列），示例：

```
| 列1            | 列2            |
|----------------|----------------|
| {% for r in rows %}{{ r.col1 }} | {{ r.col2 }} |
| {% endfor %}   |                |
```

> **⚠️ 注意**：表格占位符若横跨多个 run（在 Word 中反复修改格式导致），docxtpl 会识别失败。对策：在 Word 中一次性完整输入占位符，或直接用 `python-docx` 构造模板（见 SKILL.md 示例）。

## 4. 富文本（可选进阶）

需要同一段落内混排加粗/变色/变体时，使用 `RichText`：

```python
from docxtpl import RichText

rt = RichText()
rt.add("加粗重点", bold=True)
rt.add("正常文字")
context = {"richtext": rt}
```

模板侧使用 `{{r richtext}}`（注意 `r` 前缀）。

## 5. 模板编写规范

1. **只用 Word 内置样式**：标题用 Heading 1/2/3，正文用 Normal，表格用 Table Grid
2. **不在模板里硬编码数据**：可变内容一律占位符
3. **中文**：模板与数据统一 UTF-8，避免 PowerShell 管道传中文
4. **边界明确**：本 Skill 不处理修订追踪（`w:ins`/`w:del`）、TOC 域字段自动更新，这些交给 Word 完成