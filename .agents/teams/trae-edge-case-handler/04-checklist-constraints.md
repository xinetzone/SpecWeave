---
id: "edge-case-checklist-constraints"
title: "验证清单与使用约束"
source: "trae-edge-case-handler.md#04-checklist-constraints"
x-toml-ref: "../../../.meta/toml/.agents/teams/trae-edge-case-handler/04-checklist-constraints.toml"
---
# 验证清单与使用约束

## 边界情况验证清单

本模块为纯规范文档，以结构化验证清单替代单元测试，确保规范的有效性与一致性。

### 规范完整性验证

| 验证项 | 验证方法 | 通过标准 |
|---|---|---|
| 四大边界场景均有判断标准 | 检查每个场景章节含边界条件表 | IDE/论坛/工具链/Trae Work 四节均存在且含表格 |
| 每个边界条件有检测信号 | 检查边界条件表的"检测信号"列 | 每行检测信号非空且可观测 |
| 每个边界条件有判断方法 | 检查边界条件表的"判断方法"列 | 每行判断方法非空且含具体阈值或匹配规则 |
| 每个异常处理流程有完整链路 | 检查三级处理流程的 Mermaid 图 | 致命/警告/提示三级均有流程图且覆盖检测到恢复 |
| 每个特殊场景有预定义策略 | 检查特殊场景适配策略章节 | 沙箱/PowerShell/登录过期/DOM 变化四节均有优先级表 |
| 接口规范定义清晰 | 检查模块接口规范章节 | 输入/输出/日志/验证四接口均有定义 |
| Mermaid 流程图 ≥ 2 个 | 统计文档中 Mermaid 代码块 | 至少含分级决策图与异常处理流程图 |

### 规范一致性验证

| 验证项 | 验证方法 | 通过标准 |
|---|---|---|
| 引用模式存在且成熟度达标 | 核对 [multi-signal-detection](../../../docs/retrospective/patterns/methodology-patterns/tools-automation/multi-signal-detection.md)、[dry-run-first](../../../docs/retrospective/patterns/methodology-patterns/tools-automation/dry-run-first.md)、[check-and-restore](../../../docs/retrospective/patterns/code-patterns/check-and-restore.md) | 三模式文件均存在，成熟度均 ≥ L2 |
| 与 teams/README.md 模块职责矩阵一致 | 核对 [.agents/teams/README.md](.././README.md) | 职责矩阵含 trae-edge-case-handler 条目 |
| 与 AGENTS.md 团队管理索引一致 | 核对 [AGENTS.md](../../../AGENTS.md) 团队管理路由 | 索引含本模块引用 |
| 格式风格与现有 teams/ 文档一致 | 对比 team-admin.md、permission-system.md 等 | 标题层级、表格风格、Mermaid 用法一致 |
| 相对路径链接有效 | 运行 `python .agents/scripts/check-links.py` | 无断链 |
| 规范一致性校验通过 | 运行 `python .agents/scripts/check-spec-consistency.py` | 校验通过 |


## 使用约束

1. **多信号强制**：边界条件判断必须使用多信号组合检测，禁止依赖单一信号下结论。
2. **分级强制**：所有边界条件须明确分级，处理流程须与分级匹配，禁止跳级处理。
3. **dry-run 优先**：警告级降级操作涉及状态变更时，须遵循 dry-run-first 原则先预览后执行。
4. **检查不污染**：边界检查函数须遵循 check-and-restore 模式，检查不改变调用方状态。
5. **替代优先于退出**：致命级边界须先尝试替代方案，无可行替代方可退出。
6. **日志留痕**：所有级别的边界判断与处理须写入结构化日志，致命级须归档。
7. **反复出现须优化**：同一提示级或警告级边界情况在多次任务中反复出现，须提请优化根因（如更新选择器常量、调整登录持久化策略）。
8. **索引同步**：本规范变更后须同步更新 [.agents/teams/README.md](.././README.md) 的目录结构、职责矩阵与核心概念关系图。


---

## 相关模式

- - [forum-posting Skill](../../skills/forum-posting/SKILL.md)
- - [trae_edge_case_handler/包](../../scripts/trae_edge_case_handler/)
- - [任务交接协议](../../protocols/handoff.md)

← 上一章: [特殊场景适配策略与模块接口规范](03-adaptation-interface.md) | **[返回索引](../trae-edge-case-handler.md)**
