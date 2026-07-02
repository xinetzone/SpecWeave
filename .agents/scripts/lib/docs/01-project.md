---
id: "lib-api-project"
title: "lib.project — 项目路径解析"
source: "lib/__init__.py#project"
x-toml-ref: "../../../../.meta/toml/.agents/scripts/lib/docs/01-project.toml"
---

# lib.project — 项目路径解析

| 函数 | 签名 | 说明 |
|------|------|------|
| `resolve_project_root` | `(anchor: str \| Path) -> Path` | 从锚点位置向上查找工程根目录（含 AGENTS.md） |
| `resolve_agents_dir` | `(anchor: str \| Path) -> Path` | 解析 `.agents/` 目录路径 |
| `resolve_scripts_dir` | `(anchor: str \| Path) -> Path` | 解析 `.agents/scripts/` 目录路径 |

**示例**：

```python
from lib.project import resolve_project_root
root = resolve_project_root(__file__)  # 返回项目根目录 Path
```

---

## 相关模式

- [共享库引力定律](../../../../docs/retrospective/patterns/methodology-patterns/tools-automation/shared-lib-gravity.md)
- [临时sys.path修改](../../../../docs/retrospective/patterns/code-patterns/temporary-syspath-modification.md)

---

**[返回索引](../README.md)** | 下一章 → [CLI 输出格式化 →](02-cli.md)
