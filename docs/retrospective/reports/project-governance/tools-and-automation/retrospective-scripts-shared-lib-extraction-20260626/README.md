---
id: "retrospective-scripts-shared-lib-extraction-20260626"
x-toml-ref: "../../../../../../.meta/toml/docs/retrospective/reports/project-governance/tools-and-automation/retrospective-scripts-shared-lib-extraction-20260626/README.toml"
---
# 脚本共享代码库提取与重复模式消除复盘

> **报告类型**：任务复盘（Task Retrospective）
> **复盘日期**：2026-06-26
> **任务范围**：`.agents/scripts/` 下 24 个 Python 脚本的共享代码库提取与 12 类重复模式消除
> **触发方式**：用户请求 `/spec` 对 `.agents/scripts/` 目录进行代码重构，提取重复代码片段建立可复用代码库

## 问题概述

`.agents/scripts/` 目录下约 30 个脚本中存在大量重复代码（约 280 行），多个脚本绕过已有的 `lib/` 共享模块自建实现相同逻辑，导致维护成本高、目录结构调整时多处失效的风险。

| 问题类别 | 重复次数 | 典型表现 |
|---------|---------|---------|
| 硬编码项目根路径 | 9 处 | `Path(__file__).parent.parent.parent` |
| 自建 frontmatter 正则 | 5 处 | `FRONTMATTER_RE`、`TOML_ID_RE` 等 |
| 重定义链接正则 | 3 处 | `INLINE_LINK_RE` |
| 手写 CLI 标题 | 10+ 处 | `print("=" * 60)` |
| 手写通用参数 | 4 处 | `--json`、`--path` |
| 本地重定义排除目录 | 2 处 | `EXCLUDED_DIRS` |
| 自建 spec 目录发现 | 2 处 | `discover_spec_dirs` |
| 自建标记区替换 | 3 处 | `update_readme`、`update_file` |
| 自建标题/描述提取 | 3 处 | `extract_title`、`extract_description` |
| 内部逻辑重复 | 1 处 | check-spec-consistency 批量 vs 单个 |

## 核心成果

1. **新增 `lib/markdown.py` 共享模块**（145 行）：提供 `find_markdown_files`、`extract_title`、`extract_description`、`parse_inline_links`、`update_marker_region` 5 个跨脚本复用函数
2. **提取 `discover_spec_dirs` 到 `lib/spec/`**：统一 check-spec-consistency 与 generate-tests 中完全相同的实现
3. **批量迁移 24 个脚本**：覆盖 9 脚本路径解析、5 脚本 frontmatter、3 脚本链接正则、10+ 脚本 CLI 输出
4. **重构 check-spec-consistency.py 内部重复**：提取 `run_spec_checks()` 共享函数，消除 main() JSON 批量分支与 `check_single_spec()` 的 80% 重复
5. **发现并修复隐藏 bug**：`resolve_project_root` 迁移使 check-spec-consistency 检查结果从 19 通过提升至 25 通过（原硬编码路径 `spec_dir.parent.parent.parent` 在部分场景下解析错误）
6. **全量验证通过**：24 个脚本 `--help` 输出正常，ci-check.ps1 综合检查无新增回归

## 变更统计

| 指标 | 数值 |
|------|------|
| 变更文件数 | 27 个 |
| 新增代码行数 | 653 行 |
| 删除代码行数 | 406 行 |
| 净增行数 | +247 行 |
| 新增共享模块 | 1 个（`lib/markdown.py`） |
| 新增共享函数 | 6 个（5 个 markdown + 1 个 discover_spec_dirs） |
| 消除重复模式 | 12 类 |
| 消除重复代码 | ~280 行 |
| 并行子代理数 | 4 个 |
| Spec 检查点 | 29 项（全部通过） |

## 交付物

| 文件 | 内容 |
|------|------|
| [execution-retrospective.md](execution-retrospective.md) | 事实回顾、时间线、重复模式分析、重构过程、验证结果 |
| [insight-extraction.md](insight-extraction.md) | 洞察萃取、可复用模式提炼、成熟度更新 |
| [export-suggestions.md](export-suggestions.md) | 改进建议、行动计划、后续优化方向 |
| [spec.md](../../../../../../.trae/specs/standards-tools/refactor-scripts-shared-lib/spec.md) | Spec 规格文档（ADDED + MODIFIED Requirements） |
| [tasks.md](../../../../../../.trae/specs/standards-tools/refactor-scripts-shared-lib/tasks.md) | 10 项任务清单（全部完成） |
| [checklist.md](../../../../../../.trae/specs/standards-tools/refactor-scripts-shared-lib/checklist.md) | 29 项检查点（全部通过） |
