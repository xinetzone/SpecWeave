---
id: "lib-api-quality_report"
title: "lib.quality_report — 质量报告聚合与输出"
source: "lib/api_docs.py#quality_report"
x-toml-ref: "../../../../.meta/toml/.agents/scripts/lib/docs/13-quality-report.toml"
---

# lib.quality_report — 质量报告聚合与输出

提供检查报告的分组统计、JSON 构建、彩色打印与汇总输出能力，供质量检查脚本共享。

| 函数/类 | 签名 | 说明 |
|---------|------|------|
| `ResultGroupMixin` | `class` | 为报告对象提供 `errors/warnings/passes` 三类结果视图 |
| `score_to_ansi` | `(score: int) -> str` | 根据分数返回 ANSI 颜色码 |
| `print_result_lines` | `(results, *, verbose, print_pass, print_warn, print_error) -> None` | 打印单条检查结果列表 |
| `issue_list` | `(items: Iterable) -> list[dict]` | 将结果对象转为 JSON 友好的 `{name,message}` 列表 |
| `safe_relative_to` | `(path: Path, root_dir: Path) -> Path` | 安全计算相对路径，失败时回退原路径 |
| `aggregate_stats` | `(reports: list) -> dict` | 聚合总错误/警告/通过数与平均分 |
| `build_json_output` | `(reports, root_dir, *, base_dir_key, base_dir_value, count_key, items_key, item_builder) -> dict` | 构建统一 JSON 输出骨架 |
| `common_report_fields` | `(report) -> dict` | 提取通用报告字段（score/errors/warnings/pass_count） |
| `print_scored_report` | `(*, score, header, extra_lines, results, verbose, print_pass, print_warn, print_error) -> None` | 打印带分数标题的报告块 |
| `print_scored_report_cli` | `(*, score, header, extra_lines, results, verbose) -> None` | 使用 CLI 预设样式打印报告块 |
| `print_aggregate_summary` | `(reports: list) -> dict` | 打印平均分与通过/警告/错误摘要，并返回统计值 |

**示例**：

```python
from lib.quality_report import build_json_output, common_report_fields

payload = build_json_output(
    reports,
    root_dir,
    base_dir_key='skills_dir',
    base_dir_value=skills_dir,
    count_key='skill_count',
    items_key='skills',
    item_builder=lambda r: {'name': r.skill_name, **common_report_fields(r)},
)
```

---

## 相关模式

- [共享库引力定律](../../../docs/retrospective/patterns/methodology-patterns/tools-automation/shared-lib-gravity.md)
- [临时sys.path修改](../../../docs/retrospective/patterns/code-patterns/temporary-syspath-modification.md)

---

← 上一章: [← 质量规则复用函数](12-quality-rules.md) | **[返回索引](../README.md)** | 下一章 → [全局常量（scripts/ 根目录） →](14-constants.md)
