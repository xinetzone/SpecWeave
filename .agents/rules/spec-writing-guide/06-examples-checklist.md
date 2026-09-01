---
id: "spec-writing-06"
title: "06 正反示例与检查清单"
source: "rules/spec-writing-guide.md#06"
x-toml-ref: "../../../.meta/toml/.agents/rules/spec-writing-guide/06-examples-checklist.toml"
---

# 06 正反示例与检查清单


### 7.1 Requirement 完整性

**✅ 良好示例**：

```
### Requirement: 订单超时自动取消

系统 SHALL 对支付后 30 分钟内未发货的订单自动取消，并释放预留库存。

#### Scenario: 超时订单自动取消

- **WHEN** 订单状态为「已支付待发货」且持续超过 30 分钟
- **THEN** 系统 SHALL 将订单状态更新为「已取消」
- **THEN** 系统 SHALL 释放该订单预留的库存
- **THEN** 用户 SHALL 收到订单取消通知和退款指引
```

**❌ 不良示例**：

```
### Requirement: 订单超时处理

系统应该处理订单超时的情况。（缺少描述细节）
（没有 Scenario）
```

---

### 7.2 Scenario 结构完整性

**✅ 良好示例**：

```
#### Scenario: 新用户首次下单优惠

- **WHEN** 用户完成注册且尚未产生任何订单
- **AND** 用户提交第一个订单（金额 ≥ 100 元）
- **THEN** 系统 SHALL 减免订单金额的 10%
- **THEN** 优惠金额 SHALL NOT 超过 50 元
- **THEN** 用户 SHALL 在订单确认页看到优惠后金额
```

**❌ 不良示例**：

```
#### Scenario: 新用户优惠

- **WHEN** 用户注册后下单
- **THEN** 系统给予一定优惠（未说明优惠的具体形式和触发条件）
```

---

### 7.3 验收标准具体性

**✅ 良好示例**：

```
- **THEN** API 响应时间 SHALL ≤ 200ms（P99）
- **THEN** 成功率 SHALL ≥ 99.9%
- **THEN** 返回字段 `code` 的值 SHALL 为 0 表示成功，非 0 表示失败
```

**❌ 不良示例**：

```
- **THEN** 系统返回正确结果（未说明「正确」的定义）
- **THEN** 响应速度令人满意（未定义「满意」的量化标准）
- **THEN** 基本上成功（使用「基本上」使结果模糊）
```

---

完成 Spec 文档编写后，请逐项检查：

### 8.1 结构完整性

- [ ] 文件头部包含 TOML frontmatter 版本号声明（`---\nversion: X.Y\n---`）
- [ ] 包含成对的 `<!-- changelog -->` 标记包裹的 Changelog 章节
- [ ] 包含 Why 章节，动机说明清晰
- [ ] 包含 What Changes 章节，变更要点已列出
- [ ] 包含 Impact 章节，影响范围已评估
- [ ] 包含 ADDED Requirements 章节（若无新增则注明「无」）
- [ ] 包含 MODIFIED Requirements 章节（若无修改则注明「无」）
- [ ] 包含 REMOVED Requirements 章节（若无移除则注明「无」）

### 8.2 Requirement 质量

- [ ] 每个 Requirement 名称以「### Requirement:」开头
- [ ] ADDED/MODIFIED 下的每个 Requirement 包含「系统 SHALL」或「系统 SHALL NOT」描述
- [ ] 每个 Requirement 至少包含一个 Scenario（以「#### Scenario:」开头）
- [ ] Scenario 命名清晰、描述测试目的

### 8.3 Scenario 质量

- [ ] 每个 Scenario 包含 WHEN 部分（使用 `- **WHEN**` 列表项加粗格式）
- [ ] 每个 Scenario 包含 THEN 部分（使用 `- **THEN**` 列表项加粗格式）
- [ ] AND 部分（若有）描述必要的前置条件（使用 `- **AND**`）
- [ ] THEN 部分结果具体可测量

### 8.4 格式规范

- [ ] 无空章节（无内容章节请注明「无」）
- [ ] 章节标题使用纯英文（如 `## Why`，中文括号注释可选）
- [ ] 验收标准无模糊词汇（可能、也许、较好等）
- [ ] 章节标题层级正确（## 用于主章节，### 用于 Requirement，#### 用于 Scenario）
- [ ] 命名简洁清晰，符合第 5 节规范
- [ ] Changelog 条目按时间倒序排列，格式为 `- YYYY-MM-DD | type | description`

### 8.5 可执行性

- [ ] Scenario 可转化为验收测试用例
- [ ] 预期结果可通过自动化测试验证
- [ ] 技术指标包含可测量的目标值

---

## 附录：模板参考

```markdown
---
version: 1.0
---

# [功能名称] Spec

<!-- changelog -->
## Changelog
- YYYY-MM-DD | added | 初始版本
<!-- changelog -->

## Why

[说明问题背景或机会，1-2 段。建议用"系统 SHALL..."总结核心目标]

## What Changes

- [变更点 1]
- [变更点 2]
- [变更点 3]

## Impact

- Affected specs: [受影响的 spec，无则写「无」]
- Affected code: [受影响的代码/文件]
- [其他影响说明]

## ADDED Requirements

### Requirement: [需求名称]

[主体描述，系统 SHALL...]

#### Scenario: [场景名称]

- **WHEN** [触发条件]
- **AND** [前置条件，可选]
- **THEN** [预期结果 1]
- **THEN** [预期结果 2]

## MODIFIED Requirements

### Requirement: [需求名称]

系统 SHALL [修改后的行为描述]。

**修改原因**：[修改的业务或技术原因]

**变更后行为**：[修改后的行为描述]

#### Scenario: [场景名称]

- **WHEN** [触发条件]
- **THEN** [预期结果]

## REMOVED Requirements

（若无移除内容请写「无」）

### Requirement: [被移除需求名称]

**移除原因**：[移除的业务或技术原因]

**迁移方案**：[用户或开发者需要采取的迁移步骤]

#### Scenario: [场景名称]

- **WHEN** [触发条件]
- **THEN** [预期结果]
```

---

## 相关模式

- [Spec九段叙事法](../../../docs/retrospective/patterns/methodology-patterns/product-growth/spec-nine-section-narrative.md)
- [规范三同步原则](../../../docs/retrospective/patterns/methodology-patterns/governance-strategy/spec-triple-sync.md)
- [双向导航链接](../../../docs/retrospective/patterns/methodology-patterns/document-architecture/bidirectional-navigation-links.md)
---

← 上一章: [05 命名规范与格式化要求](05-naming-formatting.md) | **[返回索引](../spec-writing-guide.md)** | 下一章: [07 完整Spec模板](07-template-reference.md) →

