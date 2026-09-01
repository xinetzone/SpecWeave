---
id: "spec-writing-05"
title: "05 命名规范与格式化要求"
source: "rules/spec-writing-guide.md#05"
x-toml-ref: "../../../.meta/toml/.agents/rules/spec-writing-guide/05-naming-formatting.toml"
---

# 05 命名规范与格式化要求


### 5.1 Requirement 命名

- 清晰：名称应直接表达该需求的意图
- 简洁：控制在 20 个中文字符以内
- 聚焦：一个 Requirement 只描述一个功能点

**良好示例**：
- Requirement: 订单支付结果异步回调处理
- Requirement: 用户登录失败锁定机制
- Requirement: 商品库存不足时的下单拦截

**不良示例**：
- Requirement: 订单相关功能（过于笼统）
- Requirement: 处理和验证用户输入的各种情况（过长且不清晰）

---

### 5.2 Scenario 命名

- 描述性：说明该场景的测试目的
- 独立性：每个 Scenario 有明确的测试焦点
- 可执行：场景名应能指导测试用例的编写

**良好示例**：
- Scenario: 预售商品订单自动识别为高优先级
- Scenario: 用户连续 5 次输入错误密码后账户被锁定
- Scenario: 商品库存为零时下单按钮禁用

---

### 5.3 章节标题

- 使用 `###` 二级标题，用于主要章节
- 使用 `####` 三级标题，用于 Scenario
- 避免过度嵌套，层级不宜超过 4 级

---

### 6.1 章节完整性

- **禁止空章节**：所有标记的章节必须有实质内容
- **禁止仅有标题**：每个 Requirement 必须包含描述和至少一个 Scenario
- **禁止仅有 Scenario 标题**：每个 Scenario 必须包含 WHEN 和 THEN 部分

### 6.2 验收标准

- **必须具体可测量**：使用明确的数值或状态描述
- **禁止模糊词汇**：包括但不限于「可能」「也许」「较好」「较快」「适量」
- **禁止主观描述**：使用「系统 SHALL」而非「系统应该」

**良好示例**：

```
- **THEN** 系统 SHALL 在 500ms 内返回查询结果
- **THEN** 错误率 SHALL NOT 超过 0.1%
- **THEN** 响应数据 SHALL 包含订单号、状态、时间戳三个字段
```

**不良示例**：

```
- **THEN** 系统反应较快（未定义「较快」的具体含义）
- **THEN** 返回合适的结果（未说明「合适」的判定标准）
- **THEN** 可能发送通知（使用「可能」使结果不确定）
```

---

---

## 相关模式

- [Spec九段叙事法](../../../docs/retrospective/patterns/methodology-patterns/product-growth/spec-nine-section-narrative.md)
- [规范三同步原则](../../../docs/retrospective/patterns/methodology-patterns/governance-strategy/spec-triple-sync.md)
- [双向导航链接](../../../docs/retrospective/patterns/methodology-patterns/document-architecture/bidirectional-navigation-links.md)
---

← 上一章: [04 可选元素](04-optional-elements.md) | **[返回索引](../spec-writing-guide.md)** | 下一章: [06 正反示例与检查清单](06-examples-checklist.md) →

