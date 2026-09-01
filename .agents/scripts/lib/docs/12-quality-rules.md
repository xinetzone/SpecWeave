---
id: "lib-api-quality_rules"
title: "lib.quality_rules — 质量规则复用函数"
source: "lib/api_docs.py#quality_rules"
x-toml-ref: "../../../../.meta/toml/.agents/scripts/lib/docs/12-quality-rules.toml"
---

# lib.quality_rules — 质量规则复用函数

提供质量检查脚本共享的轻量规则函数，避免在多个 checker 中重复实现同一条规则。

| 函数/常量 | 签名 | 说明 |
|-----------|------|------|
| `FILE_URL_PATTERN` | `Pattern` | 匹配 Markdown 中的 `file:///` 绝对路径链接 |
| `count_file_urls` | `(content: str) -> int` | 统计文本中的 `file:///` 绝对路径数量 |
| `check_no_file_url` | `(content: str, make_result) -> list` | 生成「禁止 file:/// 绝对路径」检查结果，供不同 Result 类型复用 |

**示例**：

```python
from lib.quality_rules import check_no_file_url

results = check_no_file_url(content, lambda **kw: CheckResult(**kw))
```

---

## 相关模式

- [共享库引力定律](../../../../docs/retrospective/patterns/methodology-patterns/tools-automation/shared-lib-gravity.md)
- [临时sys.path修改](../../../../docs/retrospective/patterns/code-patterns/temporary-syspath-modification.md)

---

← 上一章: [← 进程探测与安全终止](11-process.md) | **[返回索引](../README.md)** | 下一章 → [质量报告聚合与输出 →](13-quality-report.md)
