> **来源**：从 `docs/retrospective/knowledge-extraction.md` 六、可复用知识概念 拆分

# 上下文感知（Context Awareness）

## 定义
检查逻辑在执行前先感知当前上下文的属性（文档类型、路径语义、语义粒度），据此调整检查行为。

## v1.0 vs v1.1 对比
- v1.0：无上下文感知 → 固定阈值、统一路径基准、不区分数据来源 → 大量误报
- v1.1：有上下文感知 → 可配置阈值、语义前缀解析、区分元文档 → 误报大幅减少

## 推广
任何自动化工具都应在"执行检查"前先"感知上下文"。

> **关联模块**：
> - `patterns/architecture-patterns/perception-check-report-model.md`
> - `patterns/code-patterns/context-aware-path-resolution.md`