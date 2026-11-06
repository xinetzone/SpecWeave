---
id: "lib-api-docs_as_product"
title: "lib.docs_as_product — 文档即产品校验"
source: "../api_docs.py"
x-toml-ref: "../../../../.meta/toml/.agents/scripts/lib/docs/10-docs-as-product.toml"
---

# lib.docs_as_product — 文档即产品校验

把《文档即产品经营法》模式固化为可执行校验：Diátaxis 四型分区、G1–G4 + V 门、元数据漂移（F-021）、读者契约与 M1–M5 指标脚手架。入口脚本为 `.agents/scripts/docs-as-product.py`。

| 函数 | 签名 | 说明 |
|------|------|------|
| `scan_docs` | `(root: str \| Path, config=None) -> DocsTree` | 扫描文档目录，解析 frontmatter/head/toctree/orphan/标题/首段 |
| `check_structure` | `(tree: DocsTree) -> Report` | 校验 Diátaxis 四型分区与 toctree/orphan 一致性 |
| `check_quality_gates` | `(root, *, run_external=True, config=None) -> Report` | 执行 G1–G4 与 V 门；外部工具缺失降级 WARN |
| `check_metadata_drift` | `(tree: DocsTree, config=None) -> Report` | head 仅允许跨版本稳定字段；canonical 与基准核对（F-021） |
| `check_reader_contract` | `(docs_root: str \| Path) -> Report` | 校验四类读者各有可执行验收任务 |
| `scaffold_metrics` | `(root, out_dir: str \| Path) -> list[Path]` | 生成 M1–M5 面板脚手架（metrics.json + metrics.md） |

**示例**：

```python
from lib.docs_as_product import scan_docs, check_structure

tree = scan_docs('docs')
report = check_structure(tree)
print(report.passed)  # 无 error 级发现时为 True
```

---

## 相关模式

- [共享库引力定律](../../../../docs/retrospective/patterns/methodology-patterns/tools-automation/shared-lib-gravity.md)
- [临时sys.path修改](../../../../docs/retrospective/patterns/code-patterns/temporary-syspath-modification.md)

---

← 上一章: [← 误报过滤规则引擎](09-rules.md) | **[返回索引](../README.md)** | 下一章 → [进程探测与安全终止 →](11-process.md)
