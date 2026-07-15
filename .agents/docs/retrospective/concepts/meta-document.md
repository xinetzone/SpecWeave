> **来源**：从 `docs/retrospective/knowledge-extraction.md` 六、可复用知识概念 拆分

# 元文档（Meta-Document）

## 定义
主要目的是描述、分析或评估另一个文档/项目，而非描述自身的文档。

## 特征
- 引用外部数据（数据引用与自身统计显著不一致）
- 描述他者而非自身
- 自身规模通常较小

## 处理规则
数据引用不一致 → 警告（非错误）

## 示例
复盘报告、审计报告、技术评审报告、迁移方案、对比分析、评估报告。

> **关联模块**：
> - `frameworks/meta-document-processing-matrix.md`
> - `patterns/code-patterns/meta-document-detection.md`