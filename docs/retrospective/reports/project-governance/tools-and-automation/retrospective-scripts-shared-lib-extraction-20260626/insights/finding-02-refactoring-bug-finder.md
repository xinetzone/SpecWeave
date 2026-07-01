---
id: "finding-refactoring-bug-finder"
source: "../insight-extraction.md#发现-2重构即-bug-发现器"
x-toml-ref: "../../../../../../../.meta/toml/docs/retrospective/reports/project-governance/tools-and-automation/retrospective-scripts-shared-lib-extraction-20260626/insights/finding-02-refactoring-bug-finder.toml"
---
# 发现2：重构即 Bug 发现器

→ 正式模式：[diff-driven-refactoring.md](../../../../../patterns/methodology-patterns/tools-automation/diff-driven-refactoring.md)（重构价值公式 L2）

## 事件发现

迁移 `resolve_project_root` 时发现 check-spec-consistency.py 原硬编码 `spec_dir.parent.parent.parent` 在部分场景下解析错误，导致 6 个 spec 目录未被正确检查。

后续执行复盘建议时又发现 `ci-check.ps1` 因编码问题（UTF-8无BOM+LF换行）在Windows PowerShell下无法解析——这也是之前重构时引入的隐藏bug。

## 规律

重复代码是隐藏 bug 的温床——当同一逻辑被复制到多个位置时，每个副本都可能独立演化出微妙差异，部分副本正确、部分副本错误，但因为是"复制粘贴"的产物，错误副本不会被及时发现。重构时统一到单一实现，迫使所有调用方面对同一逻辑，差异会自然暴露。

## 价值公式验证

```
重构价值 = 消除的重复代码量 + 发现的隐藏问题 + 建立的结构基础
        = 280 行 + 1 个路径解析 bug（影响 6 个 spec 检查） + lib/markdown.py
```

仅计算"消除重复"会低估 ROI 约 50%。发现的 bug 使 check-spec-consistency 通过数从 19 提升至 25，验证了 diff-driven-refactoring 中"重构价值公式"的预言。

## 关联洞察

- [meta-01-three-layer-value.md](meta-01-three-layer-value.md) — 重构三层价值模型
- [finding-01-duplication-threshold.md](finding-01-duplication-threshold.md) — 3次阈值规律

---
*来源：[脚本共享库提取复盘](../README.md)*
