---
source: "{facts.md, verification.md, spec.md}"
created_at: 2026-09-24
task: "Task 3（examples 可复现性判定）"
status: completed
---

# Examples 决策

## 可复现性两问

1. 是否有明确输入、步骤、输出和可重复环境？**否**。文章是关系建议与观点表达，没有可复现的实验输入输出。
2. 是否能由执行者独立复测结果并记录成功/失败？**否**。关系结果依赖双方意愿与情境，不能当作确定性验证。

## 结论

- 本篇不创建 `examples/`。
- 可迁移步骤放在 `knowledge-map.md` 和后续 `concepts/`，并标记为沟通实践建议，不宣称结果保证。
- 不创建空的 `examples/` 目录或占位示例文件；若未来出现具备输入、过程、输出和结果记录的授权案例，应重新执行两问判定。
