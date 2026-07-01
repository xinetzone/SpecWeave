---
id: "tuyaopen-insight-3-routing-table-discoverability"
source: "docs/knowledge/learning/tuya-open-learning-report.md"
x-toml-ref: "../../../../../../.meta/toml/docs/retrospective/reports/competitive-analysis/retrospective-tuyaopen-learning-report-optimization-20260630/insights/insight-3-routing-table-is-key-to-discoverability.toml"
---
# 洞察3：路由表是规范可发现性的关键

**来源**：TuyaOpen 学习报告优化任务

## 发现

文件命名规范虽然存在，但由于未在上下文路由表中列出，智能体在创建文件时无法自动路由到该规范文档。

## 深层含义

- 规范文档的价值不仅在于内容本身，更在于可发现性
- 路由表是智能体查找规范的入口，必须覆盖所有常用任务场景
- 创建文件是高频任务，必须在路由表中占一席之地

## 验证证据

- 修复前：上下文路由表中有"技术知识库查阅"条目，但无"文件命名规范"条目
- 修复后：在路由表中新增"文件命名规范（创建任何新文件前必读）"条目
- 位置：与"技术知识库查阅"条目相邻，创建文件时可被同时读取

## 关联资源

- [智能体全局契约](../../../../../../AGENTS.md)
- [规范可发现性保障模式](../../../../patterns/methodology-patterns/governance-strategy/spec-discoverability-guarantee.md)
- [文件创建前置检查模式](../../../../patterns/methodology-patterns/governance-strategy/file-creation-precheck-pattern.md)