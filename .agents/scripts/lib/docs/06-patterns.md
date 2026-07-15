---
id: "lib-api-patterns"
title: "lib.patterns — 模式成熟度分析"
source: "lib/api_docs.py#patterns"
x-toml-ref: "../../../../.meta/toml/.agents/scripts/lib/docs/06-patterns.toml"
---

# lib.patterns — 模式成熟度分析

提供模式文件扫描、frontmatter 解析、成熟度分类、分布统计、README 统计表解析与更新能力。

| 常量 | 说明 |
|------|------|
| `REQUIRED_FIELDS` | 模式文件必填字段列表（id/domain/layer/maturity/validation_count/reuse_count/documentation_level/source） |
| `MATURITY_LEVELS` | 成熟度等级：['L1', 'L2', 'L3', 'L4'] |
| `PATTERN_DOMAINS` | 模式子域：['methodology-patterns', 'code-patterns', 'architecture-patterns'] |
| `EXCLUDED_FILENAMES` | 排除文件名：{'README.md', 'CATEGORIES.md'} |

| 函数 | 签名 | 说明 |
|------|------|------|
| `parse_pattern_frontmatter` | `(filepath) -> dict \| None` | 解析模式文件 frontmatter，返回结构化字典（含 int 类型转换） |
| `scan_patterns` | `(base_dir) -> tuple[list, list]` | 递归扫描所有模式文件，返回 (patterns, issues) |
| `classify_pattern` | `(pattern) -> str` | 分类模式状态：'upgrade'/'anomaly'/'ok' |
| `analyze_distribution` | `(patterns) -> tuple[dict, dict]` | 分析成熟度分布与各子域分布 |
| `find_upgrade_candidates` | `(patterns) -> dict` | 找出待升级模式：{'L1_to_L2': [...], 'L2_to_L3': [...]} |
| `count_patterns` | `(dir_path) -> int` | 统计目录中模式文件数（递归，排除README/CATEGORIES） |
| `grep_maturity_per_directory` | `(patterns_root) -> dict` | 按目录统计成熟度分布 |
| `parse_readme_stats_table` | `(readme_path) -> dict` | 解析 patterns/README.md 统计表 |
| `parse_readme_index_table` | `(readme_path) -> OrderedDict` | 解析 patterns/README.md 索引表 |
| `check_stats_consistency` | `(patterns_root, readme_path) -> list` | 比对 grep 统计与 README 声明的差异 |
| `update_readme_index_table` | `(readme_path, declared_stats, actual_counts) -> str` | 更新 README 索引表中的统计数字，返回新内容 |
| `build_report_data` | `(patterns, issues) -> dict` | 构建统一报告数据（供 stats 子命令使用） |

---

## 相关模式

- [共享库引力定律](../../../docs/retrospective/patterns/methodology-patterns/tools-automation/shared-lib-gravity.md)
- [临时sys.path修改](../../../docs/retrospective/patterns/code-patterns/temporary-syspath-modification.md)

---

← 上一章: [← 链接修复](05-link-fixer.md) | **[返回索引](../README.md)** | 下一章 → [Spec 文档处理 →](07-spec.md)
