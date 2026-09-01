---
id: "spec-writing-04"
title: "04 可选元素"
source: "rules/spec-writing-guide.md#04"
x-toml-ref: "../../../.meta/toml/.agents/rules/spec-writing-guide/04-optional-elements.toml"
---

# 04 可选元素


以下元素为可选项，根据实际需要选用：

### 4.1 技术指标表格

用于定义性能、容量、可用性等非功能性需求。

```
### 技术指标

| 指标名称 | 目标值 | 测量方法 |
|---|---|---|
| 订单处理成功率 | ≥ 99.5% | 自动化监控统计 |
| 单笔订单处理时长 | P99 ≤ 5s | APM 性能追踪 |
| 系统可用性 | ≥ 99.9% | 月度 SLA 报告 |
| 最大并发订单数 | 1,000 QPS | 压力测试验证 |
```

### 4.2 依赖关系说明

用于说明本系统对外部组件或服务的依赖。

```
### 依赖关系

| 依赖组件 | 依赖类型 | 说明 |
|---|---|---|
| Redis Cluster | 数据存储 | 订单缓存和队列 |
| Kafka | 消息队列 | 订单状态变更事件 |
| User Service | 同步调用 | 用户等级查询 |
```

### 4.3 实施优先级

用于说明功能实现的阶段划分。

```
### 实施优先级

| 阶段 | 优先级 | 内容 |
|---|---|---|
| Phase 1 | P0 | 核心自动分类引擎 |
| Phase 2 | P1 | 异常处理和人工介入 |
| Phase 3 | P2 | 历史数据迁移和报表 |
```

---

---

## 相关模式

- [Spec九段叙事法](../../../docs/retrospective/patterns/methodology-patterns/product-growth/spec-nine-section-narrative.md)
- [规范三同步原则](../../../docs/retrospective/patterns/methodology-patterns/governance-strategy/spec-triple-sync.md)
- [双向导航链接](../../../docs/retrospective/patterns/methodology-patterns/document-architecture/bidirectional-navigation-links.md)
---

← 上一章: [03 必需元素清单](03-required-elements.md) | **[返回索引](../spec-writing-guide.md)** | 下一章: [05 命名规范与格式化要求](05-naming-formatting.md) →

