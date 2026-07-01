---
id: "law-shared-lib-gravity"
source: "../insight-extraction.md#规律-2共享库的引力效应"
x-toml-ref: "../../../../../../../.meta/toml/docs/retrospective/reports/project-governance/tools-and-automation/retrospective-scripts-shared-lib-extraction-20260626/insights/law-02-shared-lib-gravity.toml"
---
# 规律2：共享库的"引力效应"

## 观察

本次重构后，`lib/` 共享库从 5 个模块扩展到 6 个，函数从 ~20 个扩展到 ~26 个。新脚本开发时引用共享库的概率提升。执行复盘建议后又新增 `lib/rules.py` 和 `lib/checks/` 模块，覆盖面进一步扩大。

## 规律

共享库的吸引力随其覆盖面扩大而增强——覆盖的概念域越多，新脚本"先查共享库"的预期收益越高，形成**正反馈循环**：

```
共享库覆盖域 ↑ → "先查"收益 ↑ → 复用率 ↑ → 新函数提取↑ → 覆盖域进一步↑
```

反之，共享库覆盖面小时，"自建"的边际成本更低，导致重复持续积累（负反馈）。

## 临界点

当共享库覆盖 **≥ 5 个概念域**时，引力效应开始显著（本项目从 5 模块到 6 模块时触发）。

## 验证

- docgen.py 重构后使用新的 `parse_toml_frontmatter_as_dict` 便捷函数，从3行简化为1行
- check-links/check-source-traceability 改用共享 `find_markdown_files`
- 后续新增 check-duplication.py 时开发者主动查阅 lib/ 复用了 cli.py 和 project.py

## 对策

- 在共享库达到临界点后，"先查共享库"约定从建议变为强制（已在 development-standards.md 中实现）
- 为共享库生成 API 文档降低发现成本（已通过 `generate_api_docs()` 实现）

## 关联洞察

- [finding-03-concept-domain-separation.md](finding-03-concept-domain-separation.md) — 概念域分离是引力效应的前提
- [law-01-duplication-entropy.md](law-01-duplication-entropy.md) — 引力效应是对抗熵增的机制

---
*来源：[脚本共享库提取复盘](../README.md)*
