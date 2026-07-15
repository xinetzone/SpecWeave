---
id: "spec-writing-03"
title: "03 必需元素清单"
source: "rules/spec-writing-guide.md#03"
x-toml-ref: "../../../.meta/toml/.agents/rules/spec-writing-guide/03-required-elements.toml"
---

# 03 必需元素清单


### 3.1 Requirement 结构

每个 Requirement 必须包含以下要素：

#### 3.1.1 名称

- 以 "**Requirement:**" 开头
- 使用清晰、简洁的中文描述
- 名称应表达该需求的核心功能目标

#### 3.1.2 主体描述

- 使用 "系统 SHALL" 或 "系统 SHALL NOT" 句式
- 明确说明系统必须提供什么功能
- 避免模糊词汇和主观描述

#### 3.1.3 Scenario（场景）

- 以 "**#### Scenario:**" 开头
- 每个 Requirement 至少包含一个 Scenario
- Scenario 是验收测试的基础

**完整示例**：

```
### Requirement: 订单自动分类

系统 SHALL 根据商品类型和用户等级对订单进行优先级分类，确保高优先级订单优先处理。

#### Scenario: 普通商品订单

##### WHEN
- 用户提交一个包含普通商品（非预售、非限量）的订单

##### AND
- 用户等级为普通会员（Lv.0-Lv.2）

##### THEN
- 系统 SHALL 将该订单分类为「标准优先级」
- 订单处理队列位置由提交时间决定
- 预计处理时长显示为 30 分钟以内
```

---

### 3.2 Scenario 结构

每个 Scenario 必须包含 WHEN 和 THEN 部分（AND 为可选）。**推荐使用列表项加粗格式**（项目中普遍采用），五级标题格式（`##### WHEN`）同样兼容。

#### 3.2.1 WHEN 部分

- 描述触发条件
- 说明在什么情况下该场景被激活
- 只描述用户或外部系统的初始动作

**推荐格式（列表项加粗）**：

```
#### Scenario: 普通商品订单

- **WHEN** 用户提交一个包含普通商品（非预售、非限量）的订单
- **AND** 用户等级为普通会员（Lv.0-Lv.2）
- **THEN** 系统 SHALL 将该订单分类为「标准优先级」
```

**兼容格式（五级标题）**：

```
#### Scenario: 普通商品订单

##### WHEN
- 用户提交一个包含普通商品（非预售、非限量）的订单

##### AND
- 用户等级为普通会员（Lv.0-Lv.2）

##### THEN
- 系统 SHALL 将该订单分类为「标准优先级」
```

**不良示例**：

```
#### Scenario: 错误示例

- **WHEN** 系统接收到订单处理请求，然后进行库存校验，
  然后检查用户等级，然后分配优先级（错误：混淆了触发条件和处理逻辑）
```

#### 3.2.2 AND 部分（可选，可多个）

- 描述前置条件
- 说明 WHEN 触发时必须满足的额外状态
- 用于构建完整的测试前置环境

**推荐格式（列表项加粗）**：

```
- **AND** 用户账户余额充足
- **AND** 配送地址已在系统中存档
- **AND** 商品库存大于等于订单数量
```

#### 3.2.3 THEN 部分

- 描述可观察的预期结果
- 说明系统必须返回什么或发生什么变化
- 结果必须是可测试、可验证的

**推荐格式（列表项加粗）**：

```
- **THEN** 系统 SHALL 生成订单编号并返回给用户
- **THEN** 订单状态 SHALL 更新为「已支付待发货」
- **THEN** 用户 SHALL 收到订单确认邮件
```

**禁止表述**：
- 禁止使用「可能」「也许」「大约」等模糊词汇
- 禁止使用「较好」「更快」等无法量化的比较级
- 禁止描述系统内部实现细节

---

---

## 相关模式

- [Spec九段叙事法](../../docs/retrospective/patterns/methodology-patterns/product-growth/spec-nine-section-narrative.md)
- [规范三同步原则](../../docs/retrospective/patterns/methodology-patterns/governance-strategy/spec-triple-sync.md)
- [双向导航链接](../../docs/retrospective/patterns/methodology-patterns/document-architecture/bidirectional-navigation-links.md)
---

← 上一章: [02 标准章节结构](02-standard-structure.md) | **[返回索引](../spec-writing-guide.md)** | 下一章: [04 可选元素](04-optional-elements.md) →

