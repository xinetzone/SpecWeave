---
id: "lib-api-frontmatter"
title: "lib.frontmatter — Frontmatter 解析"
source: "lib/api_docs.py#frontmatter"
x-toml-ref: "../../../../.meta/toml/.agents/scripts/lib/docs/03-frontmatter.toml"
---

# lib.frontmatter — Frontmatter 解析

解析 Markdown 文件头部的 frontmatter 元数据块，支持 TOML（`+++ ... +++`）和 YAML（`--- ... ---`）两种格式。

| 函数 | 签名 | 说明 |
|------|------|------|
| `parse_toml_frontmatter` | `(file_path: str \| Path) -> str \| None` | 读取文件并返回 TOML frontmatter 纯文本（不含 +++） |
| `extract_frontmatter_field` | `(frontmatter: str, field_name: str) -> str \| None` | 从 frontmatter 文本中提取指定字段值（支持带引号/无引号） |
| `extract_all_fields` | `(frontmatter: str) -> dict[str, str]` | 提取 frontmatter 中所有字段为字典 |
| `parse_toml_frontmatter_as_dict` | `(file_path: str \| Path) -> dict[str, str] \| None` | 一步读取文件并解析所有 frontmatter 字段为字典（便捷函数，等价于 parse + extract_all_fields） |
| `parse_yaml_frontmatter` | `(file_path: str \| Path) -> str \| None` | 读取文件并返回 YAML frontmatter 纯文本（不含 ---） |
| `extract_yaml_field` | `(frontmatter: str, field_name: str) -> str \| None` | 从 YAML frontmatter 文本中提取指定标量字段值（支持双引号/单引号/无引号） |
| `extract_frontmatter_field_from_file` | `(file_path: str \| Path, field_name: str) -> str \| None` | 从文件提取 frontmatter 字段值，自动识别 TOML/YAML 格式 |

**示例**：

```python
from lib.frontmatter import parse_toml_frontmatter, extract_frontmatter_field, parse_yaml_frontmatter, extract_yaml_field, extract_frontmatter_field_from_file
# TOML frontmatter（.agents/ 文档常用）
fm = parse_toml_frontmatter('docs/retrospective/patterns/mypattern.md')
if fm:
    maturity = extract_frontmatter_field(fm, 'maturity')  # 'L2'
# YAML frontmatter（docs/knowledge/ 文档常用）
yaml_fm = parse_yaml_frontmatter('docs/knowledge/three-layer-routing.md')
if yaml_fm:
    source = extract_yaml_field(yaml_fm, 'source')  # 'vendor/AGENTS.md#三层路由流程图'
# 统一入口：自动识别 TOML/YAML 格式（推荐用于扫描混合文档库）
source = extract_frontmatter_field_from_file('path/to/file.md', 'source')
```

---

## 相关模式

- [共享库引力定律](../../../docs/retrospective/patterns/methodology-patterns/tools-automation/shared-lib-gravity.md)
- [临时sys.path修改](../../../docs/retrospective/patterns/code-patterns/temporary-syspath-modification.md)

---

← 上一章: [← CLI 输出格式化](02-cli.md) | **[返回索引](../README.md)** | 下一章 → [Markdown 文件处理 →](04-markdown.md)
