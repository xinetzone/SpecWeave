---
id: "regex-markdown-parsing"
source: "external: 不存在-docs/retrospective/knowledge-extraction.md"
x-toml-ref: "../../../../.meta/toml/docs/retrospective/patterns/code-patterns/regex-markdown-parsing.toml"
---
> **来源**：从 `docs/retrospective/knowledge-extraction.md` 一、可复用代码模式 拆分

# 正则驱动的 Markdown 解析

## 来源
`check-spec-consistency.py` — `parse_spec()`、`parse_tasks()`、`parse_checklist()`

## 通用 Markdown 章节解析器
```python
def parse_markdown_sections(filepath: Path, heading_pattern: str) -> list[dict]:
    """通用 Markdown 章节解析器。
    
    Args:
        filepath: Markdown 文件路径
        heading_pattern: 章节标题的正则模式，如 r"^###\s+Requirement:\s+(.+)"
    
    Returns:
        [{"name": str, "line": int}, ...]
    """
    items = []
    text = filepath.read_text(encoding="utf-8")
    for i, line in enumerate(text.splitlines(), 1):
        match = re.match(heading_pattern, line.strip())
        if match:
            items.append({"name": match.group(1).strip(), "line": i})
    return items
```

## 通用 Markdown 任务列表解析器
```python
def parse_task_list_items(filepath: Path, item_pattern: str) -> list[dict]:
    """通用 Markdown 任务列表解析器。
    
    Args:
        filepath: Markdown 文件路径
        item_pattern: 列表项的正则模式，如 r"^-\s+\[([ xX])\]\s+(.+)"
    
    Returns:
        [{"text": str, "completed": bool, "line": int}, ...]
    """
    items = []
    text = filepath.read_text(encoding="utf-8")
    for i, line in enumerate(text.splitlines(), 1):
        match = re.match(item_pattern, line.strip())
        if match:
            items.append({
                "text": match.group(2).strip(),
                "completed": match.group(1).lower() == "x",
                "line": i,
            })
    return items
```

## 复用场景
任何需要解析结构化 Markdown 文档的工具。替换正则模式即可适配不同格式。

> **关联模块**：
> - `patterns/code-patterns/three-tier-check-tool.md`