---
type: Reference

id: "knowledge-review-log"
title: "知识库复核日志"
x-toml-ref: "../../../.meta/toml/docs/knowledge/operations/knowledge-review-log.toml"
category: "operations"
tags: ["knowledge-management", "review", "audit-log", "知识治理", "复核日志"]
date: "2026-09-11"
last_verified: "2026-09-11"
status: "stable"
author: "SpecWeave"
summary: "docs/knowledge 条目定期复核的集中登记日志：日期、条目、复核结论（保持/修订/置待更新/退役）、复核人与关联复盘，配合 git 历史构成双轨可追溯证据。"
source: "../../retrospective/reports/concepts/milestone/retrospective-intelligent-doc-system-milestone-20260910.md#4-原子行动项a-阶段"
---
# 知识库复核日志

> 本日志是[知识库定期复核机制](knowledge-review-mechanism.md)的可追溯台账：**一行一条复核记录**，与条目文件的 git 历史构成双轨证据。条目修订与日志追加必须在同一提交内。
>
> 复核结论取值：**保持**（内容仍成立，仅更新 `last_verified`）、**修订**（内容有改动并重新验证）、**置待更新**（置 `status: needs-update`）、**退役**（置 `status: deprecated`）、**建基线**（存量条目首次补录 `last_verified`）。

## 登记表

| 日期 | 条目 | 复核结论 | 复核人 | 关联复盘/提交 |
|---|---|---|---|---|
| 2026-09-11 | [knowledge-review-mechanism.md](knowledge-review-mechanism.md) | 保持（机制建立当日首验） | SpecWeave | [里程碑复盘 A4](../../retrospective/reports/concepts/milestone/retrospective-intelligent-doc-system-milestone-20260910.md) |
| 2026-09-11 | [knowledge-review-log.md](knowledge-review-log.md) | 保持（日志建立当日首验） | SpecWeave | [里程碑复盘 A4](../../retrospective/reports/concepts/milestone/retrospective-intelligent-doc-system-milestone-20260910.md) |
| 2026-09-11 | [knowledge-retrospective-cross-reference-spec.md](knowledge-retrospective-cross-reference-spec.md) | 保持（入库当日首验） | SpecWeave | [里程碑复盘 A3](../../retrospective/reports/concepts/milestone/retrospective-intelligent-doc-system-milestone-20260910.md) |
| 2026-09-11 | [doc-automation-toolchain.md](doc-automation-toolchain.md) | 修订（同步 staleness 脚本新接口） | SpecWeave | [里程碑复盘 A2/A4](../../retrospective/reports/concepts/milestone/retrospective-intelligent-doc-system-milestone-20260910.md) |

## 登记规则

1. 新记录追加在表格末尾，不插序、不删历史行；结论被推翻时追加新行并在"关联"列引用原行日期。
2. 单次巡检批量复核多条时逐条登记，不用"等 N 条"合并行。
3. "关联复盘/提交"列优先放复盘报告相对链接；无复盘的例行巡检可填提交短 hash。
4. 存量条目首次补录 `last_verified` 记为"建基线"，基线日期必须等于实际复核当日，禁止回填。

## 相关资源

- [知识库定期复核机制](knowledge-review-mechanism.md)：周期、状态机、季度巡检 SOP 与阶段门禁
- [知识库与复盘体系双向引用规范](knowledge-retrospective-cross-reference-spec.md)：验证回路与"修正三必做"
- [check-wiki-staleness.py](../../../.agents/scripts/check-wiki-staleness.py)：新鲜度检查脚本
