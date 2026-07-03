---
id: "lib-api-rules"
title: "lib.rules — 误报过滤规则引擎"
source: "lib/api_docs.py#rules"
x-toml-ref: "../../../../.meta/toml/.agents/scripts/lib/docs/09-rules.toml"
---

# lib.rules — 误报过滤规则引擎

从 `config/false-positive-rules.toml` 加载通用误报过滤规则，提供四层过滤能力（路径排除/文件标记/块过滤/行过滤），供所有 linter/checker 复用。

| 函数/类 | 签名 | 说明 |
|---------|------|------|
| `load_rules` | `(rules_file: Path \| str \| None = None) -> FalsePositiveRules` | 加载误报过滤规则（默认加载 config/false-positive-rules.toml） |
| `FalsePositiveRules` | `dataclass` | 规则集合，提供各类过滤判断方法 |
| `FalsePositiveRules.should_exclude_dir` | `(dir_name: str) -> bool` | 判断目录名是否应排除 |
| `FalsePositiveRules.should_exclude_file` | `(file_name: str) -> bool` | 判断文件名是否应排除 |
| `FalsePositiveRules.should_exclude_path` | `(rel_path) -> bool` | 判断路径是否命中正则排除 |
| `FalsePositiveRules.is_marked_file` | `(file_path: Path) -> tuple[bool, str]` | 判断文件是否有排除标记（兼容包装/自动生成/第三方） |
| `FalsePositiveRules.is_excluded_line` | `(normalized_line: str) -> bool` | 判断归一化行是否应过滤 |
| `FalsePositiveRules.is_excluded_block` | `(normalized_lines: list[str]) -> tuple[bool, str]` | 判断代码块是否为样板误报 |
| `FalsePositiveRules.filter_lines` | `(lines: list[tuple[int,str]]) -> list[tuple[int,str]]` | 过滤归一化行列表中的排除行 |
| `FalsePositiveRules.should_skip_file` | `(file_path, root_dir=None) -> tuple[bool, str]` | 综合判断文件是否应跳过（路径+文件名+标记三检查） |

**规则文件位置**：`config/false-positive-rules.toml`（TOML格式，四层过滤规则）

**示例**：

```python
from lib.rules import load_rules

rules = load_rules()  # 加载默认规则

# 文件扫描时跳过排除项
for py_file in scripts_dir.rglob('*.py'):
    should_skip, reason = rules.should_skip_file(py_file, root_dir=scripts_dir)
    if should_skip:
        continue
    # ... 处理文件

# 归一化时过滤样板行
norm_lines = rules.filter_lines(norm_lines)

# 块级别过滤（如 import 样板块）
is_bp, reason = rules.is_excluded_block(block_normalized_lines)
if is_bp:
    continue  # 跳过样板误报
```

---

## 相关模式

- [共享库引力定律](../../../../docs/retrospective/patterns/methodology-patterns/tools-automation/shared-lib-gravity.md)
- [临时sys.path修改](../../../../docs/retrospective/patterns/code-patterns/temporary-syspath-modification.md)

---

← 上一章: [← 检查器框架](08-checks.md) | **[返回索引](../README.md)** | 下一章 → [PowerShell脚本编码工具 →](10-powershell.md)
