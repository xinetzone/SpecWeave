---
id: "lib-api-spec"
title: "lib.spec — Spec 文档处理"
source: "lib/api_docs.py#spec"
x-toml-ref: "../../../../.meta/toml/.agents/scripts/lib/docs/07-spec.toml"
---

# lib.spec — Spec 文档处理

提供 Spec 文件（spec.md / tasks.md / checklist.md）的解析、一致性检查与报告生成能力。

| 子模块 | 说明 |
|--------|------|
| `lib.spec.parsers` | Spec 文档解析器：`parse_spec()`、`parse_tasks()`、`parse_checklist()` |
| `lib.spec.models` | Spec 数据模型：`SpecDoc`、`TaskItem`、`CheckItem` 等 |
| `lib.spec.consistency_checkers` | 一致性检查器 |
| `lib.spec.format_checkers` | 格式检查器 |
| `lib.spec.reporters` | 检查报告生成器 |
| `lib.spec.utils` | 工具函数：`discover_spec_dirs()` 等 |

**主要入口函数**：

```python
from lib.spec.utils import discover_spec_dirs
from lib.spec.parsers import parse_spec, parse_tasks, parse_checklist
spec_dirs = discover_spec_dirs(root)  # 发现所有 .trae/specs/ 下的 spec 目录
```

---

## 相关模式

- [共享库引力定律](../../../docs/retrospective/patterns/methodology-patterns/tools-automation/shared-lib-gravity.md)
- [临时sys.path修改](../../../docs/retrospective/patterns/code-patterns/temporary-syspath-modification.md)

---

← 上一章: [← 模式成熟度分析](06-patterns.md) | **[返回索引](../README.md)** | 下一章 → [检查器框架 →](08-checks.md)
