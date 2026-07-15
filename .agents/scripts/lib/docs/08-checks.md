---
id: "lib-api-checks"
title: "lib.checks — 检查器框架"
source: "lib/api_docs.py#checks"
x-toml-ref: "../../../../.meta/toml/.agents/scripts/lib/docs/08-checks.toml"
---

# lib.checks — 检查器框架

提供统一的检查器基类和内置检查器实现。

| 子模块 | 说明 |
|--------|------|
| `lib.checks.base` | 检查器基类 `BaseChecker` |
| `lib.checks.filename` | 文件名规范检查 |
| `lib.checks.gitignore` | .gitignore 规则检查 |
| `lib.checks.mermaid` | Mermaid 语法检查 |
| `lib.checks.roles` | 角色权限检查 |
| `lib.checks.vendor` | vendor 目录合规性检查 |

---

## 相关模式

- [共享库引力定律](../../../docs/retrospective/patterns/methodology-patterns/tools-automation/shared-lib-gravity.md)
- [临时sys.path修改](../../../docs/retrospective/patterns/code-patterns/temporary-syspath-modification.md)

---

← 上一章: [← Spec 文档处理](07-spec.md) | **[返回索引](../README.md)** | 下一章 → [误报过滤规则引擎 →](09-rules.md)
