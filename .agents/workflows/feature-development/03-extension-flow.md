---
id: "feat-dev-03"
title: "03 功能扩展轻量流程（6步）"
source: "workflows/feature-development.md#03"
x-toml-ref: "../../../.meta/toml/.agents/workflows/feature-development/03-extension-flow.toml"
---

# 03 功能扩展轻量流程（6步）


适用于在已有功能上新增能力、不破坏现有结构和接口的场景（如"给评论加点赞"、"增加导出Excel功能"）。

### E1：影响分析

- **负责角色**：developer
- **📋 前置文档**：原始需求、待扩展功能的需求文档和技术方案、待扩展功能的现有代码
- **执行要点**：
  1. 分析新增能力对已有代码的影响范围。
  2. 列出需修改/新增的文件清单。
  3. 评估对已有接口和数据模型的影响（应无破坏性变更）。
- **输出**：影响分析报告（文件清单+影响范围）

### E2：增量方案确认

- **负责角色**：architect
- **📋 前置文档**：影响分析报告、待扩展功能的技术方案
- **执行要点**：
  1. 确认影响分析的完整性。
  2. 给出增量实现方案（不重新设计整体架构）。
  3. 明确回归测试范围（哪些已有功能必须验证）。
- **输出**：增量方案（含回归测试范围）

### E3：增量实现

- **负责角色**：developer
- **📋 前置文档**：增量方案、待扩展功能现有代码、开发规范
- **执行要点**：
  1. 按增量方案编码，保持已有代码不变。
  2. 为新增功能编写单元测试。
  3. 不修改已有功能的接口和行为。
  4. 提交PR。
- **输出**：增量代码实现
- **注意**：跳过"任务分配"阶段，由orchestrator直接指派developer执行。

### E4：回归测试

- **负责角色**：tester
- **📋 前置文档**：增量方案、代码实现、回归测试范围
- **执行要点**：
  1. 执行新增功能的测试。
  2. 按architect指定的范围执行已有功能的回归测试。
  3. 发现缺陷反馈至developer。
- **输出**：测试报告（含回归测试结果）

### E5：增量审查

- **负责角色**：reviewer
- **📋 前置文档**：增量方案、增量代码、回归测试报告
- **执行要点**：
  1. 审查增量代码的质量和规范符合性。
  2. 确认回归测试已通过。
  3. 审查通过则批准合并，否则退回developer。
- **输出**：审查报告

### E6：合并

- **负责角色**：orchestrator
- **执行要点**：
  1. 确认增量审查通过、回归测试通过。
  2. 执行合并。
- **完成标志**：代码已合并至主干。

---

---

## 相关模式

- [学习-验证-采用](../../../docs/retrospective/patterns/methodology-patterns/governance-strategy/learn-validate-adopt.md)
- [两阶段处理](../../../docs/retrospective/patterns/methodology-patterns/document-architecture/two-phase-processing.md)
---

← 上一章: [02 新功能完整流程（8步）](02-new-feature-flow.md) | **[返回索引](../feature-development.md)** | 下一章: [04 功能重构重量流程（7步）](04-refactoring-flow.md) →
