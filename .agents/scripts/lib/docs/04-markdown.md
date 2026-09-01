---
id: "lib-api-markdown"
title: "lib.markdown — Markdown 文件处理"
source: "lib/api_docs.py#markdown"
x-toml-ref: "../../../../.meta/toml/.agents/scripts/lib/docs/04-markdown.toml"
---

# lib.markdown — Markdown 文件处理

| 函数 | 签名 | 说明 |
|------|------|------|
| `find_markdown_files` | `(root: Path, exclude_dirs=None) -> list[Path]` | 递归查找 Markdown 文件，默认排除系统目录 |
| `extract_title` | `(path: Path \| str) -> str` | 提取首个一级标题（# Title）文本 |
| `extract_description` | `(path: Path \| str) -> str` | 提取标题下首行描述文本 |
| `parse_inline_links` | `(content: str) -> list[tuple[str, str]]` | 提取所有内联链接，返回 [(text, url), ...] |
| `update_marker_region` | `(file_path, marker_start, marker_end, new_content) -> None` | 替换 HTML 注释标记之间的内容 |

**常量**：

- `TITLE_RE` — 一级标题正则
- `DESC_RE` — 描述段落正则

**示例**：

```python
from lib.markdown import find_markdown_files, extract_title, update_marker_region
md_files = find_markdown_files(root_dir)
for f in md_files:
    title = extract_title(f)
# 更新自动生成区域
update_marker_region('README.md', '<!-- AUTO-START -->', '<!-- AUTO-END -->', new_content)
```

---

## 相关模式

- [共享库引力定律](../../../../docs/retrospective/patterns/methodology-patterns/tools-automation/shared-lib-gravity.md)
- [临时sys.path修改](../../../../docs/retrospective/patterns/code-patterns/temporary-syspath-modification.md)

---

← 上一章: [← Frontmatter 解析](03-frontmatter.md) | **[返回索引](../README.md)** | 下一章 → [链接修复 →](05-link-fixer.md)
