---
id: "spec-writing-02"
title: "02 标准章节结构"
source: "rules/spec-writing-guide.md#02"
x-toml-ref: "../../../.meta/toml/.agents/rules/spec-writing-guide/02-standard-structure.toml"
---

# 02 标准章节结构


Spec 文档必须按照以下顺序包含六大核心章节。**推荐使用纯英文标题**（项目中已普遍采用），允许附加中文括号注释增强可读性（如 `## Why（动机）`），两种格式均被格式检查脚本认可。

### 2.1 Why（动机）

解释问题背景或机会，说明为什么需要进行这项变更。

**写作要求**：
- 1-2 段文字，简洁明了
- 说明当前存在的问题或痛点
- 或说明识别到的发展机会
- 如有相关数据或案例支撑，应予提供
- 建议使用"系统 SHALL"句式总结核心目标（可选但推荐）

**示例**：

```
## Why

当前订单处理流程依赖人工审核，平均处理时长为 4.2 小时，高峰期积压订单常超过 200 单。
用户反馈显示，42% 的投诉源于订单状态更新延迟。为降低运营成本并提升用户体验，
系统 SHALL 将人工审核环节改造为自动化流程。
```

---

### 2.2 What Changes（变更摘要）

列出本次变更的核心要点，使用无序列表形式。

**写作要求**：
- 使用简洁的 bullet list
- 每条变更点应独立、可理解
- 区分新增、修改、移除三类变更

**示例**：

```
## What Changes

- 新增订单自动分类引擎，基于商品类型和用户等级进行优先级排序
- 修改订单状态机，新增「自动审核中」状态及状态转换规则
- 移除人工审核环节的短信通知依赖，改为系统内消息通知
- 新增订单处理异常的人工介入触发条件
```

---

### 2.3 Impact（影响范围）

说明本变更对其他 Specs、模块和代码的影响。

**写作要求**：
- 明确列出受影响的组件或模块
- 说明影响的性质（接口变更、数据模型变更、行为变更等）
- 标注需要同步更新的相关文档

**示例**：

```
## Impact

- Affected specs: 无（修改工具脚本，不修改现有 specs）
- Affected code: `.agents/scripts/check-spec-format.py`
- 与现有 `.agents/scripts/check-spec-consistency.py` 的关系：同属自动化验证脚本系列
```

---

### 2.4 ADDED Requirements（新增需求）

详细描述新增的功能需求，每个 Requirement 独立成段。

详见本文档第 3 节「必需元素清单」。

---

### 2.5 MODIFIED Requirements（修改需求）

描述对现有需求的修改，包括修改原因和预期影响。

**写作要求**：
- 引用原 Requirement 编号和名称
- 说明修改的具体内容
- 明确修改前后的行为差异

**示例**：

```
## MODIFIED Requirements

### Requirement: 订单状态查询接口

系统 SHALL 扩展原接口返回完整状态流转历史（原接口仅返回订单基本信息）。

**修改原因**：前端需要展示订单的完整处理轨迹，便于用户理解当前所处阶段。

**变更后行为**：响应体新增 `statusHistory` 字段，包含各状态的进入时间和操作者。

#### Scenario: 查询包含历史记录

- **WHEN** 客户端请求订单详情接口
- **THEN** 响应 SHALL 包含 `statusHistory` 字段
- **AND** 字段中 SHALL 包含至少一条状态记录
```

---

### 2.6 REMOVED Requirements（移除需求）

描述移除的需求、移除原因及迁移方案。

**写作要求**：
- 说明移除的需求编号和名称
- 解释移除的业务或技术原因
- 提供迁移路径或替代方案
- REMOVED 章节下的 Requirement 不强制使用"系统 SHALL"句式（描述被移除功能即可）

**示例**：

```
## REMOVED Requirements

### Requirement: 人工审核确认短信通知

**移除原因**：自动化审核流程不再依赖人工确认，短信通知失去必要性。

**影响范围**：审核人员将改为通过系统内消息接收审核任务通知。

**迁移方案**：
- 现有审核人员账号自动开通站内消息通知权限
- 旧版短信通知接口（`/api/v1/notify/sms`）标记为 `@Deprecated`，保留 3 个月过渡期

#### Scenario: 旧接口已标记弃用

- **WHEN** 客户端调用旧版短信通知接口
- **THEN** 响应 SHALL 返回 deprecation 警告头
- **AND** 日志 SHALL 记录弃用调用
```

---

---

## 相关模式

- [Spec九段叙事法](../../../docs/retrospective/patterns/methodology-patterns/product-growth/spec-nine-section-narrative.md)
- [规范三同步原则](../../../docs/retrospective/patterns/methodology-patterns/governance-strategy/spec-triple-sync.md)
- [双向导航链接](../../../docs/retrospective/patterns/methodology-patterns/document-architecture/bidirectional-navigation-links.md)
---

← 上一章: [01 概述](01-overview.md) | **[返回索引](../spec-writing-guide.md)** | 下一章: [03 必需元素清单](03-required-elements.md) →

